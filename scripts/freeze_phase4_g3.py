"""Create the immutable conditional G3 freeze package for Option B."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESEARCH_ROOT = ROOT / "research_validation"
FREEZE_ROOT = RESEARCH_ROOT / "phase_4_freeze"
FREEZE_ID = "g3-option-b-es-ja-20260812-v1"
RUN_ID = "run-phase4-option-b-es-ja-v1"
SEED = "research-validation-option-b-g3-20260812-v1"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8") + b"\n"


def write_component(name: str, value: Any) -> str:
    path = FREEZE_ROOT / name
    data = canonical_json(value)
    path.write_bytes(data)
    return digest(data)


def eligible_ids(path: Path) -> set[str]:
    result: set[str] = set()
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row.get("translation_value") and row.get("translation_status") in {"OFFICIAL", "TRANSLATED"}:
                result.add(str(row["subject_id"]))
    return result


def rank_ids(ids: set[str], lane: str) -> list[str]:
    return sorted(ids, key=lambda value: digest(f"{SEED}\0{lane}\0{value}".encode()))


def main() -> int:
    FREEZE_ROOT.mkdir(parents=True, exist_ok=True)
    es_ids = eligible_ids(ROOT / "babelon" / "hp-es.babelon.tsv")
    ja_ids = eligible_ids(ROOT / "babelon" / "hp-ja.babelon.tsv")
    intersection = es_ids & ja_ids
    anchors = rank_ids(intersection, "anchors")[:10]
    remaining = (es_ids | ja_ids) - set(anchors)
    es_additional = rank_ids(remaining & es_ids, "es-additional")[:20]
    ja_additional = rank_ids(remaining & ja_ids - set(es_additional), "ja-additional")[:20]
    if len(anchors) != 10 or len(es_additional) != 20 or len(ja_additional) != 20:
        raise ValueError("authorized snapshots cannot satisfy the frozen Option B sampling contract")

    assignments = [
        *({"hpo_id": value, "languages": ["es", "ja"], "sampling_role": "common_anchor"} for value in anchors),
        *({"hpo_id": value, "languages": ["es"], "sampling_role": "language_additional"} for value in es_additional),
        *({"hpo_id": value, "languages": ["ja"], "sampling_role": "language_additional"} for value in ja_additional),
    ]
    stage_1 = [*anchors[:2], *es_additional[:4], *ja_additional[:4]]
    components: dict[str, Any] = {
        "sampling_frame.json": {
            "run_id": RUN_ID,
            "design": "option_b_spanish_japanese",
            "unique_concept_count": 50,
            "concept_language_unit_count": 60,
            "assignments": assignments,
            "stage_1_hpo_ids": stage_1,
            "stage_1_concept_language_unit_count": 12,
            "selection_algorithm": "ascending_sha256(seed_nul_lane_nul_hpo_id)",
            "selection_seed": SEED,
            "labels_or_translations_retained": False,
        },
        "candidate_conditions.json": {
            "conditions": [
                {"id": "c1_direct_translation", "generator": "gpt-5.6-terra", "ontology_evidence": False},
                {"id": "c2_language_model", "generator": "gpt-5.6-sol", "ontology_evidence": False},
                {"id": "c3_lineage_aware", "generator": "gpt-5.6-sol", "ontology_evidence": True},
                {"id": "c4_withheld_repository_reference", "generator": None, "withheld_from_generators": True},
            ],
            "candidate_only": True,
            "promotion_allowed": False,
        },
        "model_endpoints.json": {
            "provider_runtime": "Codex native multi-agent runtime",
            "candidate_models": [
                {"model_id": "gpt-5.6-terra", "reasoning_effort": "medium", "temperature": 0},
                {"model_id": "gpt-5.6-sol", "reasoning_effort": "high", "temperature": 0},
            ],
            "panel_model": {"model_id": "gpt-5.6-sol", "reasoning_effort": "high", "temperature": 0},
            "provider_snapshot_hash_available": False,
            "drift_rule": (
                "Any model identifier, provider behaviour, endpoint, or reasoning-setting change invalidates "
                "this freeze."
            ),
        },
        "prompts.manifest.json": {
            "prompt_version": "option-b-agent-panel-v1",
            "candidate_prompts": {
                "c1_direct_translation": (
                    "Translate the supplied English HPO label into the target language. Return one candidate only; "
                    "do not use ontology or reference evidence."
                ),
                "c2_language_model": (
                    "Produce one candidate translation from the supplied English HPO label and permitted linguistic "
                    "context. Do not use ontology lineage or the withheld reference."
                ),
                "c3_lineage_aware": (
                    "Produce one candidate translation using the supplied English HPO label, permitted ontology "
                    "identifiers, hard negatives, and payload-safe lineage atoms. Treat dependent sources as one "
                    "evidence group and do not use the withheld reference."
                ),
            },
            "panel_prompt_contract": (
                "Apply only the assigned specialist mandate. Decide accept_without_edit, accept_with_edit, reject, "
                "or abstain; record confidence and error categories. Do not infer community endorsement, clinical "
                "validation, rights, or promotion authority."
            ),
            "role_mandates_ref": "research_validation/agent_review_panel.json",
            "role_mandates_sha256": digest((RESEARCH_ROOT / "agent_review_panel.json").read_bytes()),
        },
        "randomization.json": {
            "seed": SEED,
            "algorithm": "sha256_counter_order_v1",
            "ordering_rule": "sort by sha256(seed NUL run_id NUL item_id NUL candidate_condition NUL agent_role)",
            "blinding": ["candidate_condition", "source_popularity", "other_agent_decisions_before_lock"],
        },
        "aggregation.json": {
            "specialist_roles_required": 5,
            "acceptance_threshold": 4,
            "abstention_counts_as_non_acceptance": True,
            "unanimous_clinical_safety_clearance_required": True,
            "adjudicate_on": [
                "decision_conflict",
                "material_edit_conflict",
                "clinical_safety_conflict",
                "ontology_identity_conflict",
            ],
            "unresolved_material_conflict_action": "reject_or_hold",
            "automatic_promotion_allowed": False,
        },
        "pre_unblinding_exclusions.json": {
            "excluded_languages": ["tw"],
            "excluded_sources": [
                "decs",
                "pro-ctcae",
                "who-icf",
                "mondo",
                "uberon",
                "pato",
                "cell-ontology",
                "ncit",
                "radlex",
                "restricted_and_archived_ontology_sources",
                "hpo_mapping_catalog_payloads",
            ],
            "item_exclusions": [
                "obsolete_identifier",
                "missing_from_selected_language_snapshot",
                "reference_leakage",
                "licence_or_community_rule_prohibits_use",
                "hash_or_version_mismatch",
            ],
            "late_exclusion_rule": "invalidate_or_amend_with_new_run_id_never_patch_silently",
        },
        "agent_panel_instrument.json": {
            "roles": [
                "target_language_semantics",
                "clinical_safety",
                "ontology_semantics",
                "provenance_and_rights",
                "adversarial_error_finder",
            ],
            "adjudicator": "independent_adjudicator",
            "auditor": "reproducibility_auditor_non_voting",
            "context_isolation": True,
            "initial_decisions_locked_before_adjudication": True,
            "human_roles": 0,
            "canonical_panel_sha256": digest((RESEARCH_ROOT / "agent_review_panel.json").read_bytes()),
        },
        "source_versions.json": {
            "payload_manifest": "research_validation/pilot_source_payload_manifest.json",
            "source_atom_artifact": "research_validation/pilot_source_atoms.jsonl.gz",
            "source_atom_sha256": "2c4651d0918a5a367ef5aa12400fade4b631c54987757bf8fc4285ba93159bb9",
            "independent_evidence_group_count": 1,
            "new_external_payload_retrieval": False,
        },
        "progression_criteria.json": {
            "go": {
                "completion_percent_min": 90,
                "technical_invalidity_percent_below": 10,
                "material_governance_incidents": 0,
            },
            "revise_once": {
                "completion_percent_min": 70,
                "completion_percent_below": 90,
                "technical_invalidity_percent_range_inclusive": [10, 20],
            },
            "stop": {
                "technical_invalidity_percent_above": 20,
                "permission_refused_expired_or_revoked": True,
                "material_governance_incident": True,
            },
            "stop_for_apparent_candidate_benefit": False,
        },
        "analysis_environment.json": {
            "analysis_code": "scripts/analyze_phase4_pilot.py",
            "analysis_code_sha256": digest((ROOT / "scripts" / "analyze_phase4_pilot.py").read_bytes()),
            "runtime": "Python >=3.14.6,<3.15",
            "environment_lock": "pixi.lock",
            "environment_lock_sha256": digest((ROOT / "pixi.lock").read_bytes()),
            "analysis_version": "phase4-option-b-analysis-v1",
            "estimands": ["acceptance_rate", "clinically_significant_error_rate", "abstention_rate"],
            "interval": "Wilson 95 percent for descriptive binary proportions",
            "effectiveness_hypothesis_tests": False,
        },
        "approval_receipts.manifest.json": {
            "approval_manifest": "research_validation/approval_manifest.json",
            "approval_manifest_sha256": digest((RESEARCH_ROOT / "approval_manifest.json").read_bytes()),
            "freeze_authority": "repository_maintainer_user_instruction_2026-08-12",
            "empirical_execution_authorized": False,
            "pending_preconditions": [
                "Spanish language and community-use decision",
                "Japanese language and community-use decision",
                "ethics and privacy decision",
            ],
        },
        "privacy_retention_incident.json": {
            "identifiable_clinical_text_allowed": False,
            "raw_agent_outputs": "local_only",
            "retention": "until aggregate validation and incident window close; deletion receipt required",
            "incident_action": "stop_quarantine_rotate_if_needed_and_invalidate_freeze_if_inputs_or_blinding_affected",
            "authority_status": "pending_external_precondition",
        },
    }

    component_hashes = {name: write_component(name, value) for name, value in components.items()}
    manifest = {
        "schema_version": "phase-4-g3-component-manifest-v1",
        "freeze_id": FREEZE_ID,
        "run_id": RUN_ID,
        "component_hashes": component_hashes,
    }
    manifest_hash = write_component("component_manifest.json", manifest)
    receipt = {
        "schema_version": "phase-4-g3-freeze-receipt-v1",
        "freeze_id": FREEZE_ID,
        "run_id": RUN_ID,
        "freeze_date": "2026-08-12",
        "approver": "repository_maintainer_user_instruction",
        "component_manifest": "research_validation/phase_4_freeze/component_manifest.json",
        "component_manifest_sha256": manifest_hash,
        "component_count": len(component_hashes),
        "freeze_status": "prospectively_frozen_execution_blocked_pending_external_preconditions",
        "empirical_execution_authorized": False,
        "external_preregistration_authorized": False,
        "mutation_rule": "immutable_new_freeze_id_required_for_any_change",
        "claims_boundary": (
            "prospective_protocol_freeze_only_not_preregistration_empirical_authority_or_validation_evidence"
        ),
    }
    receipt_hash = write_component("freeze_receipt.json", receipt)

    component_metadata = {
        "sampling_frame_and_stratified_concepts": ("research_validation/protocol.md", "sampling_frame.json"),
        "candidate_conditions": ("research_validation/protocol.md", "candidate_conditions.json"),
        "prompts": ("research_validation/protocol.md", "prompts.manifest.json"),
        "model_endpoints": ("research_validation/freeze_governance.json", "model_endpoints.json"),
        "source_versions": ("research_validation/pilot_source_payload_manifest.json", "source_versions.json"),
        "randomization_seed_and_algorithm": ("research_validation/stage_0/run_manifest.json", "randomization.json"),
        "aggregation_rule": ("research_validation/protocol.md", "aggregation.json"),
        "exclusions": ("research_validation/protocol.md", "pre_unblinding_exclusions.json"),
        "agent_panel_instrument": ("research_validation/agent_review_panel.json", "agent_panel_instrument.json"),
        "progression_criteria": (
            "conductor/tracks/research_validation_20260801/phase_4_options.md",
            "progression_criteria.json",
        ),
        "analysis_code": ("scripts/analyze_phase4_pilot.py", "analysis_environment.json"),
        "approval_receipts": ("research_validation/approval_manifest.json", "approval_receipts.manifest.json"),
        "privacy_retention_and_incident_plan": (
            "research_validation/phase_4_wave_2_authority_routes.json",
            "privacy_retention_incident.json",
        ),
    }
    inventory = {
        "schema_version": "phase-4-g3-component-inventory-v1",
        "track_id": "research_validation_20260801",
        "status": "prospectively_frozen_execution_blocked_pending_external_preconditions",
        "freeze_id": FREEZE_ID,
        "freeze_package_root": "research_validation/phase_4_freeze",
        "components": [
            {
                "component_id": component_id,
                "planning_source": planning_source,
                "freeze_artifact_path": f"research_validation/phase_4_freeze/{filename}",
                "readiness": "frozen_checksummed_execution_blocked",
                "blocker": "Spanish/Japanese community-use and ethics/privacy decisions remain pending",
                "version_or_hash": f"sha256:{component_hashes[filename]}",
            }
            for component_id, (planning_source, filename) in component_metadata.items()
        ],
        "summary": {
            "component_count": len(component_hashes),
            "frozen_component_count": len(component_hashes),
            "checksummed_component_count": len(component_hashes),
            "ready_for_freeze_count": len(component_hashes),
        },
        "authorization_boundary": {
            "create_freeze_artifacts": True,
            "assign_versions_or_hashes": True,
            "start_empirical_work": False,
            "external_preregistration": False,
        },
        "claims_boundary": "prospective_freeze_only_no_empirical_translation_or_validation_evidence",
    }
    (RESEARCH_ROOT / "phase_4_g3_component_inventory.json").write_bytes(canonical_json(inventory))

    readiness = {
        "schema_version": "phase-4-g3-freeze-readiness-v1",
        "track_id": "research_validation_20260801",
        "status": "prospectively_frozen_execution_blocked_pending_external_preconditions",
        "freeze_id": FREEZE_ID,
        "frozen_at": "2026-08-12",
        "prospective_freeze_claim_allowed": True,
        "external_preregistration_claim_allowed": False,
        "prerequisites": {
            "G1_source_authority": "conditional",
            "G2_language_and_community_use_constraints": "pending",
            "approval_manifest_state": "stage0_synthetic_only",
            "approved_language_count": 0,
            "approved_payload_source_count": 2,
            "empirical_agent_execution_count": 0,
            "explicit_maintainer_freeze_approval": True,
        },
        "required_components": list(component_metadata),
        "component_status": "frozen_checksummed_execution_blocked",
        "checksum_contract": {
            "algorithm": "sha256",
            "canonical_serialization": "UTF-8 bytes; JSON uses sorted keys and compact separators",
            "all_required_components_must_have_hash": True,
            "aggregate_manifest_hash_required": True,
            "mutable_aliases_prohibited": True,
            "recorded_checksum_count": len(component_hashes),
            "aggregate_manifest_hash": f"sha256:{manifest_hash}",
        },
        "planning_inputs": [
            "research_validation/phase_4_g3_component_inventory.json",
            "research_validation/phase_4_g3_freeze_receipt.template.json",
            "research_validation/protocol.md",
            "research_validation/phase_4_candidate_matrix.json",
            "research_validation/agent_compute_budget.json",
            "research_validation/approval_manifest.json",
            "research_validation/phase_4_gate_docket.json",
            "research_validation/phase_4_wave_2_authority_routes.json",
        ],
        "advance_rule": (
            "The prospective design freeze is immutable. Empirical work remains prohibited until Spanish and "
            "Japanese community-use decisions and the ethics/privacy decision are evidenced; any component "
            "change requires a new freeze identifier and complete re-freeze."
        ),
        "authorization_boundary": {
            "create_prospective_freeze_receipt": True,
            "start_empirical_work": False,
            "retrieve_source_payloads": False,
            "contact_language_groups": False,
            "external_preregistration": False,
            "publication": False,
            "push": False,
            "pull_request": False,
        },
        "claims_boundary": "prospective_protocol_freeze_only_no_empirical_translation_or_validation_evidence",
    }
    (RESEARCH_ROOT / "phase_4_g3_freeze_readiness.json").write_bytes(canonical_json(readiness))
    print(f"Created {FREEZE_ID}: components={len(component_hashes)} receipt_sha256={receipt_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
