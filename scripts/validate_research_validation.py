"""Validate the payload-safe empirical research contract and its fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker  # type: ignore[import-untyped]

from scripts.run_stage0_rehearsal import validate_stage0_artifacts

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESEARCH_ROOT = ROOT / "research_validation"
EXPECTED_SCHEMA_NAMES = {
    "language_identity_registry",
    "reviewer_decision",
    "run_manifest",
    "source_catalog",
    "source_lineage_record",
    "supplementary_source_access_review",
    "translation_evaluation_item",
}
EXPECTED_SUPPLEMENTARY_SOURCE_IDS = {
    "cell-ontology",
    "decs",
    "mondo",
    "ncit",
    "pato",
    "pro-ctcae",
    "radlex",
    "uberon",
    "who-icf",
}
EXPECTED_REFORECAST_INPUTS = {
    "median_minutes_per_independent_judgment",
    "observed_adjudication_fraction",
    "observed_training_and_coordination_minutes",
    "confirmed_reviewer_count",
    "observed_completion_and_attrition",
}
EXPECTED_BUDGET_AUTHORIZATION_FIELDS = {
    "reviewer_contact_authorized",
    "financial_spend_authorized",
    "source_payload_retrieval_authorized",
    "empirical_candidate_generation_authorized",
    "external_preregistration_authorized",
    "publication_authorized",
    "push_authorized",
    "pull_request_authorized",
}
EXPECTED_PHASE_4_GATE_PACKET_IDS = {
    "g1-pro-ctcae",
    "g1-decs",
    "g1-mondo",
    "g1-who-icf",
    "g1-structural-sources",
    "g2-spanish-language",
    "g2-japanese-language",
    "g2-community-slot",
    "g2-reviewer-roster",
    "g2-ethics-privacy",
}
EXPECTED_PHASE_4_G1_ROUTE_SOURCE_IDS = {"pro-ctcae", "decs", "mondo", "who-icf", "uberon", "pato"}
EXPECTED_PHASE_4_INTERNAL_SCOPE_SOURCE_IDS = {"mondo", "who-icf", "uberon", "pato"}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def schema_errors(schema: dict[str, Any], instance: Any) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [error.message for error in sorted(validator.iter_errors(instance), key=lambda error: list(error.path))]


def semantic_errors(schema_name: str, instance: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(instance, dict):
        return errors

    if schema_name == "translation_evaluation_item":
        hard_negatives = instance.get("hard_negative_hpo_ids", [])
        if instance.get("hpo_id") in hard_negatives:
            errors.append("the target HPO identifier cannot also be a hard negative")
        source_text = instance.get("source_text")
        source_text_sha256 = instance.get("source_text_sha256")
        if isinstance(source_text, str) and isinstance(source_text_sha256, str):
            computed_sha256 = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
            if source_text_sha256 != computed_sha256:
                errors.append("source_text_sha256 does not match source_text")

    if schema_name == "run_manifest":
        empirical_count = instance.get("empirical_record_count")
        reviewed_count = instance.get("human_reviewed_record_count")
        if isinstance(empirical_count, int) and isinstance(reviewed_count, int) and reviewed_count > empirical_count:
            errors.append("human_reviewed_record_count cannot exceed empirical_record_count")

        if instance.get("release_scope") != "schema_probe":
            approvals = instance.get("approvals", {})
            if isinstance(approvals, dict) and any(value in {"pending", "rejected"} for value in approvals.values()):
                errors.append("pilot and confirmatory runs require approved or not-required approval states")
            for field in ("sampling_code_commit", "analysis_code_commit"):
                if not re.fullmatch(r"[0-9a-f]{7,40}", str(instance.get(field, ""))):
                    errors.append(f"{field} must be a Git commit for pilot and confirmatory runs")

        source_versions = instance.get("source_versions", {})
        source_retrieval_dates = instance.get("source_retrieval_dates", {})
        if (
            isinstance(source_versions, dict)
            and isinstance(source_retrieval_dates, dict)
            and source_versions.keys() != source_retrieval_dates.keys()
        ):
            errors.append("source_versions and source_retrieval_dates must name the same sources")

    if schema_name == "reviewer_decision":
        if instance.get("clinically_significant_error") and not instance.get("error_categories"):
            errors.append("a clinically significant error requires at least one error category")
        selected_hpo_id = instance.get("selected_hpo_id")
        discrimination_correct = instance.get("ontology_discrimination_correct")
        if (selected_hpo_id is None) != (discrimination_correct is None):
            errors.append("ontology discrimination identifier and result must be recorded together")
        if instance.get("conflict_status") == "recused" and instance.get("decision") != "abstain":
            errors.append("a recused reviewer must abstain")

    if schema_name == "source_catalog":
        mappings = instance.get("mappings", [])
        if not isinstance(mappings, list):
            return errors
        source_ids = [record.get("source_id") for record in mappings if isinstance(record, dict)]
        if len(source_ids) != len(set(source_ids)):
            errors.append("source catalog source_id values must be unique")

        dependence_summary = instance.get("dependence_summary", {})
        if isinstance(dependence_summary, dict):
            if dependence_summary.get("naive_mapping_family_count") != len(mappings):
                errors.append("naive_mapping_family_count must equal the number of mapping families")
            independent_groups = {
                record.get("independent_evidence_group") for record in mappings if isinstance(record, dict)
            }
            if dependence_summary.get("independent_evidence_group_count") != len(independent_groups):
                errors.append("independent_evidence_group_count must equal the number of unique groups")

        groups_by_origin: dict[str, set[str]] = {}
        for record in mappings:
            if not isinstance(record, dict):
                continue
            origin = record.get("origin_dataset")
            group = record.get("independent_evidence_group")
            if isinstance(origin, str) and isinstance(group, str):
                groups_by_origin.setdefault(origin, set()).add(group)
            versioned_url = record.get("versioned_url")
            mutable_alias_url = record.get("mutable_alias_url")
            if isinstance(versioned_url, str) and "/latest/" in versioned_url:
                errors.append(f"{record.get('source_id')} versioned_url cannot use a latest alias")
            if versioned_url == mutable_alias_url:
                errors.append(f"{record.get('source_id')} versioned and mutable URLs must differ")
            members = record.get("members", [])
            artifact_size = record.get("artifact_size_bytes")
            if isinstance(members, list) and members and isinstance(artifact_size, int):
                member_size = sum(member.get("size_bytes", 0) for member in members if isinstance(member, dict))
                if member_size != artifact_size:
                    errors.append(f"{record.get('source_id')} member sizes must sum to artifact_size_bytes")
        if any(len(groups) > 1 for groups in groups_by_origin.values()):
            errors.append("records with the same origin_dataset must share one independent evidence group")
        if isinstance(dependence_summary, dict):
            origin_counts: dict[str, int] = {}
            members_by_origin: dict[str, set[str]] = {}
            for record in mappings:
                if (
                    isinstance(record, dict)
                    and isinstance(record.get("origin_dataset"), str)
                    and isinstance(record.get("source_id"), str)
                ):
                    origin = str(record["origin_dataset"])
                    origin_counts[origin] = origin_counts.get(origin, 0) + 1
                    members_by_origin.setdefault(origin, set()).add(str(record["source_id"]))
            expected_shared_origins = {origin for origin, count in origin_counts.items() if count > 1}
            shared_origin_groups = dependence_summary.get("shared_origin_groups", [])
            reported_shared_origins = {
                group.get("origin_dataset") for group in shared_origin_groups if isinstance(group, dict)
            }
            if reported_shared_origins != expected_shared_origins or len(reported_shared_origins) != len(
                shared_origin_groups
            ):
                errors.append("shared_origin_groups must enumerate every repeated origin_dataset exactly once")
            for group in shared_origin_groups:
                if not isinstance(group, dict):
                    continue
                origin = group.get("origin_dataset")
                if not isinstance(origin, str) or origin not in expected_shared_origins:
                    continue
                if set(group.get("members", [])) != members_by_origin[origin]:
                    errors.append(f"shared origin {origin} must list its exact source members")
                expected_groups = groups_by_origin.get(origin, set())
                if len(expected_groups) == 1 and group.get("independent_evidence_group") not in expected_groups:
                    errors.append(f"shared origin {origin} must use its source records' independent evidence group")

    if schema_name == "supplementary_source_access_review":
        reviews = instance.get("reviews", [])
        if not isinstance(reviews, list):
            return errors
        source_ids = [
            source_id
            for record in reviews
            if isinstance(record, dict) and isinstance(source_id := record.get("source_id"), str)
        ]
        if len(source_ids) != len(set(source_ids)):
            errors.append("supplementary source_id values must be unique")

        raw_active_profiles = instance.get("active_translation_profiles", [])
        active_profiles = (
            {profile for profile in raw_active_profiles if isinstance(profile, str)}
            if isinstance(raw_active_profiles, list)
            else set()
        )
        for record in reviews:
            if not isinstance(record, dict):
                continue
            raw_overlap = record.get("active_translation_profile_overlap", [])
            overlap = (
                {profile for profile in raw_overlap if isinstance(profile, str)}
                if isinstance(raw_overlap, list)
                else set()
            )
            if not overlap <= active_profiles:
                errors.append(f"{record.get('source_id')} overlap must be a subset of active translation profiles")
            source_version = record.get("source_version", {})
            if isinstance(source_version, dict):
                version_status = source_version.get("status")
                version_value = source_version.get("value")
                commit_sha = source_version.get("commit_sha")
                if version_status == "version_not_exposed_before_access" and (
                    version_value is not None or commit_sha is not None
                ):
                    errors.append(f"{record.get('source_id')} cannot claim a version before access")
                if version_status != "version_not_exposed_before_access" and not isinstance(version_value, str):
                    errors.append(f"{record.get('source_id')} reviewed release requires a version value")
            if record.get("repository_decision") == "payload_blocked_permission_required" and (
                "written_provider_permission" not in record.get("open_gates", [])
            ):
                errors.append(f"{record.get('source_id')} permission block requires a written-provider gate")
            if record.get("credential_requirement") == "oauth2_client_credentials" and (
                "credential_provisioning" not in record.get("open_gates", [])
            ):
                errors.append(f"{record.get('source_id')} OAuth2 access requires a credential-provisioning gate")

        summary = instance.get("summary", {})
        if isinstance(summary, dict):
            expected_counts = {
                "source_count": len(reviews),
                "metadata_probe_allowed_count": sum(
                    record.get("repository_decision") == "metadata_probe_allowed"
                    for record in reviews
                    if isinstance(record, dict)
                ),
                "permission_required_count": sum(
                    record.get("repository_decision") == "payload_blocked_permission_required"
                    for record in reviews
                    if isinstance(record, dict)
                ),
                "human_review_required_count": sum(
                    record.get("repository_decision") == "payload_blocked_human_review_required"
                    for record in reviews
                    if isinstance(record, dict)
                ),
                "payload_allowed_count": sum(
                    bool(record.get("payload_retrieval_allowed")) for record in reviews if isinstance(record, dict)
                ),
            }
            for field, expected in expected_counts.items():
                if summary.get(field) != expected:
                    errors.append(f"{field} must equal the recomputed supplementary source count")

    return errors


def reviewer_workload_budget_errors(instance: Any) -> list[str]:
    if not isinstance(instance, dict):
        return ["reviewer workload budget must be a JSON object"]

    errors: list[str] = []
    design = instance.get("design_snapshot", {})
    assumptions = instance.get("planning_assumptions", {})
    stage_1 = instance.get("stage_1_release", {})
    full = instance.get("full_pilot_ceiling", {})
    release_rule = instance.get("release_rule", {})
    authorization = instance.get("authorization_boundary", {})
    if not all(isinstance(value, dict) for value in (design, assumptions, stage_1, full, release_rule, authorization)):
        return ["reviewer workload budget sections must be JSON objects"]

    numeric_requirements = {
        "design_snapshot": (
            design,
            (
                "concept_language_units",
                "candidate_conditions",
                "reviews_per_candidate",
                "independent_judgments",
                "primary_reviewer_count",
                "independent_adjudicator_count",
                "planning_reviewer_count",
            ),
        ),
        "planning_assumptions": (
            assumptions,
            (
                "minutes_per_independent_judgment",
                "training_minutes_per_reviewer",
                "anticipated_adjudication_fraction",
                "minutes_per_adjudication",
            ),
        ),
        "stage_1_release": (
            stage_1,
            (
                "concept_language_units",
                "candidate_rows",
                "independent_judgments",
                "anticipated_adjudications",
                "independent_review_minutes",
                "training_minutes",
                "adjudication_minutes",
                "coordination_and_contingency_minutes",
                "release_cap_minutes",
                "release_cap_hours",
            ),
        ),
        "full_pilot_ceiling": (
            full,
            (
                "candidate_rows",
                "independent_judgments",
                "anticipated_adjudications",
                "independent_review_minutes",
                "training_minutes",
                "adjudication_minutes",
                "coordination_and_contingency_minutes",
                "ceiling_minutes",
                "ceiling_hours",
                "remaining_after_stage_1_cap_minutes",
                "remaining_after_stage_1_cap_hours",
            ),
        ),
    }
    for section_name, (section, fields) in numeric_requirements.items():
        for field in fields:
            value = section.get(field)
            if isinstance(value, bool) or not isinstance(value, int | float):
                errors.append(f"{section_name}.{field} must be numeric")
    if errors:
        return errors

    design_candidate_rows = design.get("concept_language_units", 0) * design.get("candidate_conditions", 0)
    design_judgments = design_candidate_rows * design.get("reviews_per_candidate", 0)
    if full.get("candidate_rows") != design_candidate_rows:
        errors.append("full-pilot candidate rows must match the design snapshot")
    if design.get("planning_reviewer_count") != (
        design.get("primary_reviewer_count", 0) + design.get("independent_adjudicator_count", 0)
    ):
        errors.append("planning reviewer count must include primary reviewers and independent adjudicators")
    if design.get("independent_judgments") != design_judgments or full.get("independent_judgments") != design_judgments:
        errors.append("full-pilot independent judgments must match the design snapshot")

    stage_1_candidate_rows = stage_1.get("concept_language_units", 0) * design.get("candidate_conditions", 0)
    stage_1_judgments = stage_1_candidate_rows * design.get("reviews_per_candidate", 0)
    if stage_1.get("candidate_rows") != stage_1_candidate_rows:
        errors.append("Stage 1 candidate rows must match its concept-language units")
    if stage_1.get("independent_judgments") != stage_1_judgments:
        errors.append("Stage 1 independent judgments must match its candidate rows")

    minutes_per_judgment = assumptions.get("minutes_per_independent_judgment", 0)
    training_minutes = assumptions.get("training_minutes_per_reviewer", 0) * design.get("planning_reviewer_count", 0)
    minutes_per_adjudication = assumptions.get("minutes_per_adjudication", 0)
    if stage_1.get("independent_review_minutes") != stage_1_judgments * minutes_per_judgment:
        errors.append("Stage 1 independent-review minutes do not match the planning assumption")
    if full.get("independent_review_minutes") != design_judgments * minutes_per_judgment:
        errors.append("full-pilot independent-review minutes do not match the planning assumption")
    if stage_1.get("training_minutes") != training_minutes or full.get("training_minutes") != training_minutes:
        errors.append("training minutes must match reviewer count and the per-reviewer assumption")
    if stage_1.get("adjudication_minutes") != stage_1.get("anticipated_adjudications", 0) * minutes_per_adjudication:
        errors.append("Stage 1 adjudication minutes do not match the planning assumption")
    if full.get("adjudication_minutes") != full.get("anticipated_adjudications", 0) * minutes_per_adjudication:
        errors.append("full-pilot adjudication minutes do not match the planning assumption")

    stage_1_components = sum(
        stage_1.get(field, 0)
        for field in (
            "independent_review_minutes",
            "training_minutes",
            "adjudication_minutes",
            "coordination_and_contingency_minutes",
        )
    )
    full_components = sum(
        full.get(field, 0)
        for field in (
            "independent_review_minutes",
            "training_minutes",
            "adjudication_minutes",
            "coordination_and_contingency_minutes",
        )
    )
    if stage_1.get("release_cap_minutes") != stage_1_components:
        errors.append("Stage 1 release cap must equal its workload components")
    if full.get("ceiling_minutes") != full_components:
        errors.append("full-pilot ceiling must equal its workload components")
    if stage_1.get("release_cap_hours") * 60 != stage_1.get("release_cap_minutes"):
        errors.append("Stage 1 hour and minute caps must agree")
    if full.get("ceiling_hours") * 60 != full.get("ceiling_minutes"):
        errors.append("full-pilot hour and minute ceilings must agree")

    remaining_minutes = full.get("ceiling_minutes", 0) - stage_1.get("release_cap_minutes", 0)
    if full.get("remaining_after_stage_1_cap_minutes") != remaining_minutes:
        errors.append("remaining budget minutes must equal the ceiling less the Stage 1 cap")
    if full.get("remaining_after_stage_1_cap_hours") * 60 != remaining_minutes:
        errors.append("remaining budget hours and minutes must agree")

    adjudication_fraction = assumptions["anticipated_adjudication_fraction"]
    if stage_1.get("anticipated_adjudications") != round(stage_1_candidate_rows * adjudication_fraction):
        errors.append("Stage 1 anticipated adjudications must match the planning fraction")
    if full.get("anticipated_adjudications") != round(design_candidate_rows * adjudication_fraction):
        errors.append("full-pilot anticipated adjudications must match the planning fraction")

    if instance.get("status") != "provisional_g0_budget_approved":
        errors.append("reviewer workload budget must retain its provisional G0 status")
    if instance.get("target_option") != "A":
        errors.append("reviewer workload budget must remain scoped to selected Option A")
    if stage_1.get("release_cap_minutes") != 1800 or full.get("ceiling_minutes") != 7200:
        errors.append("approved Stage 1 and full-pilot workload ceilings cannot drift without amendment")
    if not release_rule.get("stage_1_only_initially") or not release_rule.get(
        "remaining_budget_requires_observed_stage_1_data"
    ):
        errors.append("remaining budget must stay gated on observed Stage 1 data")
    if set(release_rule.get("required_reforecast_inputs", [])) != EXPECTED_REFORECAST_INPUTS:
        errors.append("remaining budget reforecast inputs must remain complete")
    if set(authorization) != EXPECTED_BUDGET_AUTHORIZATION_FIELDS or any(
        value is not False for value in authorization.values()
    ):
        errors.append("capacity planning cannot authorize reviewer, payload, empirical, or external actions")
    return errors


def phase_4_candidate_matrix_errors(instance: Any, supplementary: Any) -> list[str]:
    if not isinstance(instance, dict) or not isinstance(supplementary, dict):
        return ["Phase 4 candidate matrix and supplementary review must be JSON objects"]

    errors: list[str] = []
    slots = instance.get("language_slots", [])
    if not isinstance(slots, list) or len(slots) != 3:
        return ["Phase 4 candidate matrix must define exactly three language slots"]

    expected_slots = {
        "high_resource_latin": "es",
        "script_typology_contrast": "ja",
        "community_governed_or_lower_resource": None,
    }
    observed_slots = {slot.get("slot_id"): slot.get("preferred_language") for slot in slots if isinstance(slot, dict)}
    if observed_slots != expected_slots:
        errors.append("Phase 4 preferred language slots must remain es, ja, and an unassigned community slot")

    language_values: list[str] = []
    pathway_ids: set[str] = set()
    for slot in slots:
        if not isinstance(slot, dict):
            errors.append("each Phase 4 language slot must be an object")
            continue
        preferred = slot.get("preferred_language")
        if isinstance(preferred, str):
            language_values.append(preferred)
        language_values.extend(value for value in slot.get("fallback_languages", []) if isinstance(value, str))
        for pathway in slot.get("source_pathways", []):
            if isinstance(pathway, dict) and isinstance(pathway.get("source_id"), str):
                pathway_ids.add(pathway["source_id"])

    if "tw" in language_values:
        errors.append("unresolved tw must not appear in preferred or fallback language slots")
    exclusions = instance.get("explicit_exclusions", [])
    if not any(isinstance(item, dict) and item.get("language") == "tw" for item in exclusions):
        errors.append("Phase 4 candidate matrix must explicitly exclude unresolved tw")

    reviews = supplementary.get("reviews", [])
    source_ids = {
        review.get("source_id")
        for review in reviews
        if isinstance(review, dict) and isinstance(review.get("source_id"), str)
    }
    unknown_pathways = pathway_ids - source_ids
    if unknown_pathways:
        errors.append(f"Phase 4 source pathways are absent from the canonical review: {sorted(unknown_pathways)}")
    if any(isinstance(review, dict) and review.get("payload_retrieval_allowed") for review in reviews):
        errors.append("candidate matrix cannot proceed while the canonical review reports an allowed payload")

    if any(
        instance.get(field) != 0
        for field in ("approved_language_count", "approved_source_payload_count", "named_reviewer_count")
    ):
        errors.append("Phase 4 planning matrix must record zero approved languages, payloads, and named reviewers")

    reviewer_model = instance.get("reviewer_model", {})
    if not isinstance(reviewer_model, dict):
        errors.append("reviewer model must be an object")
    else:
        planned_total = reviewer_model.get("planned_primary_reviewer_count", 0) + reviewer_model.get(
            "planned_independent_adjudicator_count", 0
        )
        if reviewer_model.get("planned_human_role_count") != planned_total or planned_total != 12:
            errors.append("reviewer model must budget nine primary reviewers and three independent adjudicators")
        if reviewer_model.get("identities_or_contact_details_permitted_in_repository") is not False:
            errors.append("reviewer identities and contact details must remain excluded")
        expected_roles = {
            "target_language_terminology_reviewer",
            "target_language_clinical_reviewer",
            "target_language_ontology_phenotype_reviewer",
        }
        if set(reviewer_model.get("primary_roles", [])) != expected_roles:
            errors.append("primary reviewer roles must cover terminology, clinical, and ontology expertise")
        adjudicator_requirements = set(reviewer_model.get("adjudicator_requirements", []))
        if not {
            "independent_of_candidate_generation",
            "not_one_of_the_three_initial_reviewers_for_the_adjudicated_item",
            "conflict_of_interest_declaration",
        }.issubset(adjudicator_requirements):
            errors.append("adjudicator requirements must preserve independence and conflict review")

    expected_actions = [
        "step_down_to_option_b_with_es_and_ja",
        "consider_option_b_with_es_and_zh_subject_to_all_gates",
        "consider_option_b_with_fr_or_pt_and_ja_subject_to_all_gates",
        "step_down_to_option_c",
        "remain_at_option_d_synthetic_only",
    ]
    contingencies = instance.get("step_down_contingencies", [])
    actions = [item.get("action") for item in contingencies if isinstance(item, dict)]
    if actions != expected_actions:
        errors.append("Phase 4 step-down contingencies must preserve the approved A-to-B-to-C-to-D order")

    authorization = instance.get("authorization_boundary", {})
    if not isinstance(authorization, dict) or any(value is not False for value in authorization.values()):
        errors.append("all Phase 4 candidate-matrix authorization fields must remain false")
    return errors


def phase_4_gate_docket_errors(instance: Any, supplementary: Any, approval_manifest: Any) -> list[str]:
    if not all(isinstance(value, dict) for value in (instance, supplementary, approval_manifest)):
        return ["Phase 4 gate docket inputs must be JSON objects"]

    errors: list[str] = []
    packets = instance.get("decision_packets", [])
    if not isinstance(packets, list):
        return ["Phase 4 decision packets must be a list"]
    packet_ids = {
        packet.get("packet_id")
        for packet in packets
        if isinstance(packet, dict) and isinstance(packet.get("packet_id"), str)
    }
    if packet_ids != EXPECTED_PHASE_4_GATE_PACKET_IDS or len(packets) != len(packet_ids):
        errors.append("Phase 4 gate docket must contain each canonical decision packet exactly once")

    source_ids = {
        review.get("source_id")
        for review in supplementary.get("reviews", [])
        if isinstance(review, dict) and isinstance(review.get("source_id"), str)
    }
    active_profiles = set(supplementary.get("active_translation_profiles", []))
    for packet in packets:
        if not isinstance(packet, dict):
            errors.append("each Phase 4 decision packet must be an object")
            continue
        if packet.get("decision") != "pending":
            errors.append("decision packets must remain pending until evidence is recorded in the approval manifest")
        linked_sources = set(packet.get("linked_source_ids", []))
        if not linked_sources.issubset(source_ids):
            errors.append(f"decision packet references unknown sources: {sorted(linked_sources - source_ids)}")
        linked_languages = set(packet.get("linked_language_ids", []))
        if "tw" in linked_languages or not linked_languages.issubset(active_profiles):
            errors.append("decision packet contains an unresolved or inactive language profile")
        if (
            not packet.get("decision_owner_role")
            or not packet.get("required_evidence")
            or not packet.get("if_not_approved")
        ):
            errors.append("each decision packet requires an owner role, evidence list, and failure action")

    manifest_decisions = {gate.get("decision") for gate in approval_manifest.get("gates", []) if isinstance(gate, dict)}
    if manifest_decisions != {"pending"} or approval_manifest.get("promotion_allowed") is not False:
        errors.append("gate docket is valid only while the canonical approval manifest remains pending and fail-closed")

    authorization = instance.get("authorization_boundary", {})
    if (
        not isinstance(authorization, dict)
        or not authorization
        or any(value is not False for value in authorization.values())
    ):
        errors.append("all Phase 4 gate-docket authorization fields must remain false")
    if instance.get("advance_rule", {}).get("automatic_advancement_allowed") is not False:
        errors.append("Phase 4 gate decisions must never advance automatically")
    return errors


def phase_4_decision_receipt_template_errors(instance: Any) -> list[str]:
    if not isinstance(instance, dict):
        return ["Phase 4 decision receipt template must be a JSON object"]
    errors: list[str] = []
    if instance.get("template_only") is not True or instance.get("decision") != "pending":
        errors.append("decision receipt must remain an unexecuted pending template")
    for field in (
        "packet_id",
        "approval_manifest_gate",
        "authority_role",
        "approver_pseudonym",
        "decision_date",
        "scope",
        "recheck_date",
        "withdrawal_or_incident_contact_reference",
    ):
        if instance.get(field) is not None:
            errors.append(f"decision receipt template field {field} must remain null")
    for field in ("conditions", "linked_language_ids", "linked_source_ids", "evidence_uris", "evidence_sha256"):
        if instance.get(field) != []:
            errors.append(f"decision receipt template field {field} must remain empty")
    authorization_fields = (
        "payload_retrieval_allowed",
        "reviewer_contact_allowed",
        "reviewer_data_collection_allowed",
        "empirical_work_allowed",
        "promotion_allowed",
    )
    if any(instance.get(field) is not False for field in authorization_fields):
        errors.append("decision receipt template must not authorize downstream actions")
    return errors


def phase_4_g1_route_review_errors(instance: Any) -> list[str]:
    if not isinstance(instance, dict):
        return ["Phase 4 G1 route review must be a JSON object"]
    errors: list[str] = []
    routes = instance.get("routes", [])
    if not isinstance(routes, list):
        return ["Phase 4 G1 routes must be a list"]
    route_ids = {
        route.get("source_id")
        for route in routes
        if isinstance(route, dict) and isinstance(route.get("source_id"), str)
    }
    if route_ids != EXPECTED_PHASE_4_G1_ROUTE_SOURCE_IDS or len(routes) != len(route_ids):
        errors.append("G1 route review must cover each authorized source exactly once")
    for route in routes:
        if not isinstance(route, dict):
            errors.append("each G1 source route must be an object")
            continue
        if (
            not route.get("official_evidence_urls")
            or not route.get("license_finding")
            or not route.get("dispatch_status")
        ):
            errors.append("each G1 source route requires official evidence, a licence finding, and dispatch status")
        if not str(route.get("dispatch_status", "")).startswith(("blocked_", "not_sent_")):
            errors.append("G1 route review cannot claim a dispatch without a send receipt")
    if instance.get("dispatch_completed_count") != 0:
        errors.append("G1 route review must record zero completed dispatches")
    authorization = instance.get("authorization_boundary", {})
    if not isinstance(authorization, dict) or authorization.get("g1_external_enquiry_scope_authorized") is not True:
        errors.append("G1 enquiry scope authorization must be recorded")
    prohibited_true = {
        field
        for field, value in authorization.items()
        if field != "g1_external_enquiry_scope_authorized" and value is not False
    }
    if prohibited_true:
        errors.append(f"G1 route review grants prohibited downstream authority: {sorted(prohibited_true)}")
    return errors


def phase_4_g1_internal_scope_review_errors(instance: Any) -> list[str]:
    if not isinstance(instance, dict):
        return ["Phase 4 G1 internal scope review must be a JSON object"]
    errors: list[str] = []
    reviews = instance.get("source_reviews", [])
    if not isinstance(reviews, list):
        return ["Phase 4 G1 internal source reviews must be a list"]
    source_ids = {
        review.get("source_id")
        for review in reviews
        if isinstance(review, dict) and isinstance(review.get("source_id"), str)
    }
    if source_ids != EXPECTED_PHASE_4_INTERNAL_SCOPE_SOURCE_IDS or len(reviews) != len(source_ids):
        errors.append("internal scope review must cover Mondo, WHO ICF, Uberon, and PATO exactly once")
    for review in reviews:
        if not isinstance(review, dict):
            errors.append("each internal source review must be an object")
            continue
        if (
            review.get("payload_retrieval_allowed") is not False
            or review.get("human_license_decision_recorded") is not False
        ):
            errors.append(
                "internal scope recommendations must not record payload authority or a human licence decision"
            )
        if not review.get("required_controls") or not review.get("prohibited_or_deferred_roles"):
            errors.append("each internal source review requires controls and prohibited or deferred roles")
        if review.get("source_id") == "who-icf":
            prohibited = set(review.get("prohibited_or_deferred_roles", []))
            if not {"adaptation_of_codes", "distribution_of_modified_material"}.issubset(prohibited):
                errors.append("WHO ICF review must prohibit code adaptation and modified-material distribution")
    program_decision = instance.get("program_decision", {})
    if not isinstance(program_decision, dict) or program_decision.get("source_licence_gate_closed") is not False:
        errors.append("internal recommendations must leave the source licence gate open")
    authorization = instance.get("authorization_boundary", {})
    if (
        not isinstance(authorization, dict)
        or not authorization
        or any(value is not False for value in authorization.values())
    ):
        errors.append("all internal scope authorization fields must remain false")
    return errors


def validate_contract(research_root: Path = DEFAULT_RESEARCH_ROOT) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    schema_dir = research_root / "schemas"
    passing_dir = research_root / "fixtures" / "passing"
    failing_dir = research_root / "fixtures" / "failing"

    schemas = {path.name.removesuffix(".schema.json"): load_json(path) for path in schema_dir.glob("*.schema.json")}
    missing_schemas = EXPECTED_SCHEMA_NAMES - schemas.keys()
    extra_schemas = schemas.keys() - EXPECTED_SCHEMA_NAMES
    for name in sorted(missing_schemas):
        issues.append(ValidationIssue("schema.missing", str(schema_dir), f"missing schema: {name}"))
    for name in sorted(extra_schemas):
        issues.append(ValidationIssue("schema.unexpected", str(schema_dir), f"unexpected schema: {name}"))

    for name, schema in sorted(schemas.items()):
        schema_path = schema_dir / f"{name}.schema.json"
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as error:  # jsonschema exposes several schema-error subclasses
            issues.append(ValidationIssue("schema.invalid", str(schema_path), str(error)))
            continue

        passing_path = passing_dir / f"{name}.json"
        failing_path = failing_dir / f"{name}.json"
        if not passing_path.exists():
            issues.append(ValidationIssue("fixture.passing.missing", str(passing_path), "passing fixture is required"))
        else:
            passing_instance = load_json(passing_path)
            errors = schema_errors(schema, passing_instance) + semantic_errors(name, passing_instance)
            for message in errors:
                issues.append(ValidationIssue("fixture.passing.rejected", str(passing_path), message))

        if not failing_path.exists():
            issues.append(
                ValidationIssue("fixture.failing.missing", str(failing_path), "expected-failure fixture is required")
            )
        else:
            failing_instance = load_json(failing_path)
            errors = schema_errors(schema, failing_instance) + semantic_errors(name, failing_instance)
            if not errors:
                issues.append(
                    ValidationIssue("fixture.failing.accepted", str(failing_path), "expected-failure fixture passed")
                )

    registry_path = research_root / "language_identity_registry.json"
    registry_schema = schemas.get("language_identity_registry")
    if registry_schema is not None:
        if not registry_path.exists():
            issues.append(ValidationIssue("registry.missing", str(registry_path), "canonical registry is required"))
        else:
            registry = load_json(registry_path)
            for message in schema_errors(registry_schema, registry):
                issues.append(ValidationIssue("registry.invalid", str(registry_path), message))

    catalog_path = research_root / "source_catalog.json"
    catalog_schema = schemas.get("source_catalog")
    if catalog_schema is not None:
        if not catalog_path.exists():
            issues.append(ValidationIssue("source_catalog.missing", str(catalog_path), "canonical catalog is required"))
        else:
            catalog = load_json(catalog_path)
            errors = schema_errors(catalog_schema, catalog) + semantic_errors("source_catalog", catalog)
            for message in errors:
                issues.append(ValidationIssue("source_catalog.invalid", str(catalog_path), message))

    supplementary_path = research_root / "supplementary_source_access_reviews.json"
    supplementary_schema = schemas.get("supplementary_source_access_review")
    if supplementary_schema is not None:
        if not supplementary_path.exists():
            issues.append(
                ValidationIssue(
                    "supplementary_source_access_review.missing",
                    str(supplementary_path),
                    "canonical supplementary source access review is required",
                )
            )
        else:
            supplementary = load_json(supplementary_path)
            errors = schema_errors(supplementary_schema, supplementary) + semantic_errors(
                "supplementary_source_access_review", supplementary
            )
            for message in errors:
                issues.append(
                    ValidationIssue("supplementary_source_access_review.invalid", str(supplementary_path), message)
                )
            if isinstance(supplementary, dict):
                reviews = supplementary.get("reviews", [])
                source_ids = {
                    source_id
                    for record in reviews
                    if isinstance(record, dict) and isinstance(source_id := record.get("source_id"), str)
                }
                if source_ids != EXPECTED_SUPPLEMENTARY_SOURCE_IDS:
                    issues.append(
                        ValidationIssue(
                            "supplementary_source_access_review.coverage",
                            str(supplementary_path),
                            "canonical review must cover the complete planned supplementary source set",
                        )
                    )
                recorded_active_profiles = supplementary.get("active_translation_profiles", [])
                actual_active_profiles = {
                    path.name.removeprefix("hp-").removesuffix(".babelon.tsv")
                    for path in (ROOT / "babelon").glob("hp-*.babelon.tsv")
                }
                if set(recorded_active_profiles) != actual_active_profiles:
                    issues.append(
                        ValidationIssue(
                            "supplementary_source_access_review.active_profiles_stale",
                            str(supplementary_path),
                            "active translation profiles must match the committed Babelon translation assets",
                        )
                    )
                unresolved_suffixes: set[str] = set()
                if registry_path.exists():
                    registry = load_json(registry_path)
                    for record in registry.get("records", []):
                        if not isinstance(record, dict) or record.get("status") != "authority_review_required":
                            continue
                        suffix = record.get("current_asset_suffix")
                        if isinstance(suffix, str):
                            unresolved_suffixes.add(suffix)
                for record in reviews:
                    if not isinstance(record, dict):
                        continue
                    raw_overlap = record.get("active_translation_profile_overlap", [])
                    overlap = (
                        {profile for profile in raw_overlap if isinstance(profile, str)}
                        if isinstance(raw_overlap, list)
                        else set()
                    )
                    blocked_overlap = overlap & unresolved_suffixes
                    if blocked_overlap:
                        issues.append(
                            ValidationIssue(
                                "supplementary_source_access_review.language_identity_unresolved",
                                str(supplementary_path),
                                (
                                    f"{record.get('source_id')} counts unresolved language profiles: "
                                    f"{sorted(blocked_overlap)}"
                                ),
                            )
                        )

    budget_path = research_root / "reviewer_workload_budget.json"
    if not budget_path.exists():
        issues.append(
            ValidationIssue("reviewer_budget.missing", str(budget_path), "reviewer workload budget is required")
        )
    else:
        budget = load_json(budget_path)
        for message in reviewer_workload_budget_errors(budget):
            issues.append(ValidationIssue("reviewer_budget.invalid", str(budget_path), message))

    candidate_matrix_path = research_root / "phase_4_candidate_matrix.json"
    if not candidate_matrix_path.exists():
        issues.append(
            ValidationIssue(
                "phase_4_candidate_matrix.missing", str(candidate_matrix_path), "candidate matrix is required"
            )
        )
    elif not supplementary_path.exists():
        issues.append(
            ValidationIssue(
                "phase_4_candidate_matrix.canonical_review_missing",
                str(candidate_matrix_path),
                "candidate matrix requires the canonical supplementary source review",
            )
        )
    else:
        candidate_matrix = load_json(candidate_matrix_path)
        supplementary = load_json(supplementary_path)
        for message in phase_4_candidate_matrix_errors(candidate_matrix, supplementary):
            issues.append(ValidationIssue("phase_4_candidate_matrix.invalid", str(candidate_matrix_path), message))

    gate_docket_path = research_root / "phase_4_gate_docket.json"
    approval_manifest_path = research_root / "approval_manifest.json"
    if not gate_docket_path.exists():
        issues.append(ValidationIssue("phase_4_gate_docket.missing", str(gate_docket_path), "gate docket is required"))
    elif not supplementary_path.exists() or not approval_manifest_path.exists():
        issues.append(
            ValidationIssue(
                "phase_4_gate_docket.canonical_input_missing",
                str(gate_docket_path),
                "gate docket requires supplementary reviews and the approval manifest",
            )
        )
    else:
        gate_docket = load_json(gate_docket_path)
        supplementary = load_json(supplementary_path)
        approval_manifest = load_json(approval_manifest_path)
        for message in phase_4_gate_docket_errors(gate_docket, supplementary, approval_manifest):
            issues.append(ValidationIssue("phase_4_gate_docket.invalid", str(gate_docket_path), message))

    action_pack_path = research_root / "phase_4_external_action_pack.md"
    if not action_pack_path.exists():
        issues.append(ValidationIssue("phase_4_action_pack.missing", str(action_pack_path), "action pack is required"))
    else:
        action_pack = action_pack_path.read_text(encoding="utf-8")
        required_boundaries = (
            "drafts only — no external action authorized",
            "no agent may advance the study automatically",
            "Please do not send qualifications",
            "No reviewer data collection will begin",
        )
        for boundary in required_boundaries:
            if boundary not in action_pack:
                issues.append(
                    ValidationIssue(
                        "phase_4_action_pack.boundary_missing",
                        str(action_pack_path),
                        f"required fail-closed boundary is missing: {boundary}",
                    )
                )

    receipt_template_path = research_root / "phase_4_decision_receipt.template.json"
    if not receipt_template_path.exists():
        issues.append(
            ValidationIssue(
                "phase_4_decision_receipt.missing", str(receipt_template_path), "receipt template is required"
            )
        )
    else:
        receipt_template = load_json(receipt_template_path)
        for message in phase_4_decision_receipt_template_errors(receipt_template):
            issues.append(ValidationIssue("phase_4_decision_receipt.invalid", str(receipt_template_path), message))

    g1_route_review_path = research_root / "phase_4_g1_route_review.json"
    if not g1_route_review_path.exists():
        issues.append(
            ValidationIssue("phase_4_g1_route_review.missing", str(g1_route_review_path), "G1 route review is required")
        )
    else:
        g1_route_review = load_json(g1_route_review_path)
        for message in phase_4_g1_route_review_errors(g1_route_review):
            issues.append(ValidationIssue("phase_4_g1_route_review.invalid", str(g1_route_review_path), message))

    internal_scope_path = research_root / "phase_4_g1_internal_scope_review.json"
    if not internal_scope_path.exists():
        issues.append(
            ValidationIssue(
                "phase_4_g1_internal_scope_review.missing",
                str(internal_scope_path),
                "G1 internal scope review is required",
            )
        )
    else:
        internal_scope = load_json(internal_scope_path)
        for message in phase_4_g1_internal_scope_review_errors(internal_scope):
            issues.append(
                ValidationIssue("phase_4_g1_internal_scope_review.invalid", str(internal_scope_path), message)
            )

    probe_path = passing_dir / "translation_evaluation_item.json"
    if probe_path.exists():
        probe = load_json(probe_path)
        if len(probe.get("hard_negative_hpo_ids", [])) < 1:
            issues.append(
                ValidationIssue("probe.hard_negative.missing", str(probe_path), "one hard negative is required")
            )
        if len(probe.get("independent_evidence_groups", [])) < 2:
            issues.append(
                ValidationIssue(
                    "probe.independent_evidence_groups.insufficient", str(probe_path), "two groups are required"
                )
            )

        lineage_schema = schemas.get("source_lineage_record")
        manifest_path = passing_dir / "run_manifest.json"
        manifest = load_json(manifest_path) if manifest_path.exists() else {}
        probe_run_id = probe.get("run_id")
        if probe_run_id != manifest.get("run_id"):
            issues.append(
                ValidationIssue(
                    "probe.run_id.mismatch", str(probe_path), "benchmark item is not linked to its manifest"
                )
            )
        lineage_paths = [
            passing_dir / "source_lineage_record.json",
            passing_dir / "source_lineage_record_b.json",
        ]
        evidence_groups: dict[str, str] = {}
        for lineage_path in lineage_paths:
            if not lineage_path.exists():
                issues.append(
                    ValidationIssue(
                        "probe.source_lineage.missing", str(lineage_path), "probe lineage record is required"
                    )
                )
                continue
            lineage_record = load_json(lineage_path)
            if lineage_schema is not None:
                for message in schema_errors(lineage_schema, lineage_record):
                    issues.append(ValidationIssue("probe.source_lineage.invalid", str(lineage_path), message))
            if isinstance(lineage_record, dict):
                if lineage_record.get("run_id") != probe_run_id:
                    issues.append(
                        ValidationIssue(
                            "probe.source_lineage.run_id.mismatch",
                            str(lineage_path),
                            "source lineage record is not linked to the probe run",
                        )
                    )
                evidence_id = lineage_record.get("evidence_id")
                evidence_group = lineage_record.get("independent_evidence_group")
                if isinstance(evidence_id, str) and isinstance(evidence_group, str):
                    evidence_groups[evidence_id] = evidence_group
                source_id = lineage_record.get("source_id")
                manifest_source_versions = manifest.get("source_versions", {})
                if isinstance(source_id, str) and source_id not in manifest_source_versions:
                    issues.append(
                        ValidationIssue(
                            "probe.source_lineage.source_version.missing",
                            str(lineage_path),
                            "source lineage record has no pinned version in the run manifest",
                        )
                    )

        probe_evidence_ids = probe.get("evidence_ids", [])
        missing_evidence_ids = set(probe_evidence_ids) - evidence_groups.keys()
        if missing_evidence_ids:
            issues.append(
                ValidationIssue(
                    "probe.source_lineage.unresolved",
                    str(probe_path),
                    f"missing lineage for evidence IDs: {sorted(missing_evidence_ids)}",
                )
            )
        else:
            linked_groups = {evidence_groups[evidence_id] for evidence_id in probe_evidence_ids}
            if linked_groups != set(probe.get("independent_evidence_groups", [])):
                issues.append(
                    ValidationIssue(
                        "probe.independent_evidence_groups.mismatch",
                        str(probe_path),
                        "item groups do not match the linked source-lineage records",
                    )
                )

        reviewer_path = passing_dir / "reviewer_decision.json"
        if reviewer_path.exists():
            reviewer_decision = load_json(reviewer_path)
            reviewer_run_mismatch = reviewer_decision.get("run_id") != probe_run_id
            reviewer_item_mismatch = reviewer_decision.get("item_id") != probe.get("item_id")
            if reviewer_run_mismatch or reviewer_item_mismatch:
                issues.append(
                    ValidationIssue(
                        "probe.reviewer_decision.link.mismatch",
                        str(reviewer_path),
                        "reviewer decision is not linked to the probe run and item",
                    )
                )

    for stage0_issue in validate_stage0_artifacts(research_root / "stage_0"):
        issues.append(
            ValidationIssue(
                f"stage0.{stage0_issue.code}",
                stage0_issue.path,
                stage0_issue.message,
            )
        )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-root", type=Path, default=DEFAULT_RESEARCH_ROOT)
    args = parser.parse_args()

    issues = validate_contract(args.research_root)
    if issues:
        print(f"Research validation contract failed with {len(issues)} issue(s):")
        for issue in issues:
            print(f"- [{issue.code}] {issue.path}: {issue.message}")
        return 1

    schema_count = len(EXPECTED_SCHEMA_NAMES)
    passing_count = len(list((args.research_root / "fixtures" / "passing").glob("*.json")))
    failing_count = len(list((args.research_root / "fixtures" / "failing").glob("*.json")))
    print(
        f"Research validation contract passed: {schema_count} schemas, "
        f"{passing_count} passing fixtures, and {failing_count} expected failures."
    )
    print("This result validates the contract only; it does not establish empirical translation readiness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
