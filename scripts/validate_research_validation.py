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
