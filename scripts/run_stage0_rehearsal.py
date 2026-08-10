"""Run the deterministic, payload-free Phase 4 Stage 0 rehearsal."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STAGE0_ROOT = ROOT / "research_validation" / "stage_0"
EXPECTED_METHOD_CODES = {
    "synthetic-control-template",
    "synthetic-model-template",
    "synthetic-ontology-template",
    "synthetic-reference-template",
}
EXPECTED_SCENARIO_IDS = {
    "full-feasibility-success",
    "two-reviewers-with-adjudicator",
    "one-reviewer-only",
    "review-completion-80-percent",
    "technical-invalidity-15-percent",
    "technical-invalidity-25-percent",
    "permission-revoked",
    "material-governance-incident",
}
DECISION_PATTERNS = (
    ("accept", "accept", "reject"),
    ("accept", "accept", "accept"),
    ("reject", "reject", "abstain"),
    ("reject", "reject", "reject"),
)
FORBIDDEN_PUBLIC_KEYS = {"method_code", "candidate_method", "source_id", "provenance_id"}
FORBIDDEN_PUBLIC_PATTERNS = (
    re.compile(r"\bHP:[0-9]{7}\b"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"\b(?:DECIPHER|LOINC|MedDRA|OMIM|PRO-CTCAE|SNOMED|UMLS)\b", re.IGNORECASE),
    re.compile(r"\b(?:api[_-]?key|credential|patient[_-]?record|restricted[_-]?payload|token)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class Stage0Issue:
    code: str
    path: str
    message: str


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def json_schema_errors(schema: dict[str, Any], instance: Any) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [error.message for error in sorted(validator.iter_errors(instance), key=lambda error: list(error.path))]


def build_review_packet(plan: dict[str, Any]) -> list[dict[str, Any]]:
    rng = random.Random(int(plan["random_seed"]))
    packet: list[dict[str, Any]] = []
    for item in plan["items"]:
        candidates = list(item["candidates"])
        rng.shuffle(candidates)
        for presentation_order, candidate in enumerate(candidates, start=1):
            packet.append(
                {
                    "item_id": item["item_id"],
                    "candidate_id": f"candidate-{item['item_id']}-{presentation_order:02d}",
                    "presentation_order": presentation_order,
                    "language_tag": item["language_tag"],
                    "object_type": item["object_type"],
                    "source_text": item["source_text"],
                    "source_text_sha256": item["source_text_sha256"],
                    "candidate_text": candidate["candidate_text"],
                    "hard_negative_ids": item["hard_negative_ids"],
                }
            )
    return packet


def build_assignments(plan: dict[str, Any], packet: list[dict[str, Any]]) -> list[dict[str, Any]]:
    assignments = [
        {
            "assignment_id": f"assignment-{candidate['candidate_id']}-{reviewer_slot}",
            "item_id": candidate["item_id"],
            "candidate_id": candidate["candidate_id"],
            "reviewer_slot": reviewer_slot,
        }
        for candidate in packet
        for reviewer_slot in range(1, int(plan["reviewer_slots_per_candidate"]) + 1)
    ]
    random.Random(int(plan["random_seed"]) + 1).shuffle(assignments)
    return assignments


def build_decisions(assignments: list[dict[str, Any]], packet: list[dict[str, Any]]) -> list[dict[str, Any]]:
    presentation_orders = {record["candidate_id"]: int(record["presentation_order"]) for record in packet}
    decisions: list[dict[str, Any]] = []
    for assignment in assignments:
        order = presentation_orders[assignment["candidate_id"]]
        reviewer_slot = int(assignment["reviewer_slot"])
        decision = DECISION_PATTERNS[(order - 1) % len(DECISION_PATTERNS)][reviewer_slot - 1]
        decisions.append(
            {
                "decision_id": f"decision-{assignment['assignment_id']}",
                "assignment_id": assignment["assignment_id"],
                "item_id": assignment["item_id"],
                "candidate_id": assignment["candidate_id"],
                "reviewer_slot": reviewer_slot,
                "decision": decision,
                "synthetic": True,
            }
        )
    return decisions


def build_adjudications(decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    item_by_candidate: dict[str, str] = {}
    for decision in decisions:
        candidate_id = str(decision["candidate_id"])
        grouped[candidate_id].append(str(decision["decision"]))
        item_by_candidate[candidate_id] = str(decision["item_id"])

    adjudications: list[dict[str, Any]] = []
    for candidate_id in sorted(grouped):
        candidate_decisions = grouped[candidate_id]
        counts = Counter(value for value in candidate_decisions if value != "abstain")
        resolution = counts.most_common(1)[0][0]
        status = "agreed" if len(set(candidate_decisions)) == 1 else "adjudicated"
        adjudications.append(
            {
                "candidate_id": candidate_id,
                "item_id": item_by_candidate[candidate_id],
                "status": status,
                "resolution": resolution,
                "synthetic": True,
            }
        )
    return adjudications


def public_packet_is_blinded(packet: list[dict[str, Any]]) -> bool:
    return all(not (set(record) & FORBIDDEN_PUBLIC_KEYS) for record in packet)


def public_packet_is_redacted(packet: list[dict[str, Any]]) -> bool:
    serialized = json.dumps(packet, ensure_ascii=False)
    return not any(pattern.search(serialized) for pattern in FORBIDDEN_PUBLIC_PATTERNS)


def randomization_was_applied(plan: dict[str, Any], packet: list[dict[str, Any]]) -> bool:
    original_orders = {
        item["item_id"]: [candidate["candidate_text"] for candidate in item["candidates"]] for item in plan["items"]
    }
    presented_orders: dict[str, list[str]] = defaultdict(list)
    for record in packet:
        presented_orders[str(record["item_id"])].append(str(record["candidate_text"]))
    return any(presented_orders[item_id] != order for item_id, order in original_orders.items())


def sampling_strata_are_exercised(plan: dict[str, Any]) -> bool:
    required_branches = {"synthetic-branch-a", "synthetic-branch-b", "synthetic-branch-c"}
    required_object_types = {"label", "definition", "synonym", "regional_variant", "patient_facing"}
    recorded_strata = {str(stratum) for item in plan["items"] for stratum in item["stratum_ids"]}
    recorded_object_types = {str(item["object_type"]) for item in plan["items"]}
    return required_branches <= recorded_strata and required_object_types <= recorded_object_types


def progression_action(scenario: dict[str, Any]) -> str:
    if (
        not scenario["permissions_approved"]
        or int(scenario["reviewer_count"]) < 2
        or float(scenario["technical_invalidity_percent"]) > 20
        or not scenario["blinding_viable"]
        or scenario["material_governance_incident"]
        or not scenario["measurement_usable"]
    ):
        return "stop"
    if (
        int(scenario["reviewer_count"]) >= 3
        and float(scenario["review_completion_percent"]) >= 90
        and float(scenario["adjudication_completion_percent"]) >= 90
        and float(scenario["technical_invalidity_percent"]) < 10
    ):
        return "go"
    if (
        int(scenario["reviewer_count"]) >= 2
        and scenario["independent_adjudicator_available"]
        and float(scenario["review_completion_percent"]) >= 70
        and float(scenario["adjudication_completion_percent"]) >= 70
        and float(scenario["technical_invalidity_percent"]) <= 20
    ):
        return "revise"
    return "stop"


def export_round_trip(artifacts: dict[str, Any]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    with TemporaryDirectory(prefix="hpo-stage0-") as directory:
        export_root = Path(directory)
        for name, value in sorted(artifacts.items()):
            payload = canonical_json_bytes(value)
            path = export_root / f"{name}.json"
            path.write_bytes(payload)
            if load_json(path) != value:
                raise ValueError(f"Stage 0 export round trip failed for {name}")
            hashes[name] = sha256_bytes(payload)
    return hashes


def build_receipt(stage0_root: Path = DEFAULT_STAGE0_ROOT) -> dict[str, Any]:
    plan = load_json(stage0_root / "rehearsal.json")
    manifest = load_json(stage0_root / "run_manifest.json")
    if not isinstance(plan, dict) or not isinstance(manifest, dict):
        raise ValueError("Stage 0 plan and manifest must be JSON objects")

    packet = build_review_packet(plan)
    assignments = build_assignments(plan, packet)
    decisions = build_decisions(assignments, packet)
    adjudications = build_adjudications(decisions)
    scenarios = [
        {"scenario_id": scenario["scenario_id"], "action": progression_action(scenario)}
        for scenario in sorted(plan["stop_condition_scenarios"], key=lambda value: value["scenario_id"])
    ]
    artifact_hashes = export_round_trip(
        {
            "adjudications": adjudications,
            "assignments": assignments,
            "decisions": decisions,
            "review_packet": packet,
            "stop_condition_results": scenarios,
        }
    )
    action_counts = Counter(scenario["action"] for scenario in scenarios)
    adjudication_counts = Counter(record["status"] for record in adjudications)
    return {
        "schema_version": "stage-0-receipt-v1",
        "run_id": plan["run_id"],
        "generated_at": manifest["generated_at"],
        "rehearsal_sha256": sha256_bytes(canonical_json_bytes(plan)),
        "manifest_sha256": sha256_bytes(canonical_json_bytes(manifest)),
        "export_sha256": artifact_hashes,
        "counts": {
            "synthetic_items": len(plan["items"]),
            "blinded_candidate_rows": len(packet),
            "synthetic_assignments": len(assignments),
            "synthetic_decisions": len(decisions),
            "agreed_candidates": adjudication_counts["agreed"],
            "adjudicated_candidates": adjudication_counts["adjudicated"],
            "stop_scenarios": action_counts["stop"],
            "revise_scenarios": action_counts["revise"],
            "go_scenarios": action_counts["go"],
        },
        "checks": {
            "sampling_count": len(plan["items"]) == 12,
            "sampling_strata_exercised": sampling_strata_are_exercised(plan),
            "randomization_reproducible": packet == build_review_packet(plan),
            "randomization_applied": randomization_was_applied(plan, packet),
            "artifact_level_blinding": public_packet_is_blinded(packet),
            "export_round_trip": len(artifact_hashes) == 5,
            "adjudication_exercised": adjudication_counts["adjudicated"] > 0,
            "redaction": public_packet_is_redacted(packet),
            "stop_conditions_exercised": set(action_counts) == {"go", "revise", "stop"},
            "restricted_inputs_absent": manifest["restricted_inputs_present"] is False,
            "empirical_records_absent": manifest["empirical_record_count"] == 0,
            "human_review_absent": manifest["human_reviewed_record_count"] == 0,
        },
        "claims_boundary": "operational_readiness_only_no_translation_or_human_validation_evidence",
    }


def validate_plan_semantics(plan: dict[str, Any], path: Path) -> list[Stage0Issue]:
    issues: list[Stage0Issue] = []
    items = plan.get("items", [])
    if not isinstance(items, list):
        return issues

    item_ids = [item.get("item_id") for item in items if isinstance(item, dict)]
    concept_ids = [item.get("synthetic_concept_id") for item in items if isinstance(item, dict)]
    if len(item_ids) != len(set(item_ids)):
        issues.append(Stage0Issue("item_id.duplicate", str(path), "Stage 0 item identifiers must be unique"))
    if len(concept_ids) != len(set(concept_ids)):
        issues.append(Stage0Issue("concept_id.duplicate", str(path), "synthetic concept identifiers must be unique"))

    for item in items:
        if not isinstance(item, dict):
            continue
        serialized = json.dumps(item, ensure_ascii=False)
        if re.search(r"\bHP:[0-9]{7}\b", serialized):
            issues.append(Stage0Issue("real_hpo_id.present", str(path), "Stage 0 cannot contain real HPO identifiers"))
        source_text = item.get("source_text")
        source_hash = item.get("source_text_sha256")
        if (
            isinstance(source_text, str)
            and isinstance(source_hash, str)
            and sha256_bytes(source_text.encode()) != source_hash
        ):
            issues.append(
                Stage0Issue(
                    "source_text.checksum",
                    str(path),
                    f"{item.get('item_id')} source_text_sha256 does not match source_text",
                )
            )
        candidates = item.get("candidates", [])
        method_codes = {candidate.get("method_code") for candidate in candidates if isinstance(candidate, dict)}
        if method_codes != EXPECTED_METHOD_CODES:
            issues.append(
                Stage0Issue(
                    "candidate_methods.coverage",
                    str(path),
                    f"{item.get('item_id')} must contain each synthetic method exactly once",
                )
            )

    recorded_scenarios = {
        str(scenario.get("scenario_id")): scenario
        for scenario in plan.get("stop_condition_scenarios", [])
        if isinstance(scenario, dict)
    }
    scenario_ids_match = set(recorded_scenarios) == EXPECTED_SCENARIO_IDS
    actions_match = scenario_ids_match and all(
        progression_action(scenario) == scenario.get("expected_action") for scenario in recorded_scenarios.values()
    )
    if not actions_match:
        issues.append(
            Stage0Issue(
                "stop_conditions.mismatch",
                str(path),
                "Stage 0 scenarios must calculate the canonical go, revise, and stop decisions",
            )
        )
    return issues


def validate_stage0_artifacts(stage0_root: Path = DEFAULT_STAGE0_ROOT) -> list[Stage0Issue]:
    issues: list[Stage0Issue] = []
    paths = {
        "schema": stage0_root / "schema.json",
        "manifest": stage0_root / "run_manifest.json",
        "plan": stage0_root / "rehearsal.json",
        "receipt": stage0_root / "receipt.json",
    }
    for name, path in paths.items():
        if not path.exists():
            issues.append(Stage0Issue(f"{name}.missing", str(path), f"Stage 0 {name} is required"))
    if issues:
        return issues

    schema = load_json(paths["schema"])
    plan = load_json(paths["plan"])
    manifest_schema = load_json(stage0_root.parent / "schemas" / "run_manifest.schema.json")
    manifest = load_json(paths["manifest"])
    if not isinstance(schema, dict) or not isinstance(manifest_schema, dict):
        return [Stage0Issue("schema.invalid", str(paths["schema"]), "Stage 0 schemas must be JSON objects")]

    try:
        Draft202012Validator.check_schema(schema)
    except Exception as error:  # jsonschema exposes several schema-error subclasses
        issues.append(Stage0Issue("schema.invalid", str(paths["schema"]), str(error)))
        return issues

    plan_schema_messages = json_schema_errors(schema, plan)
    for message in plan_schema_messages:
        issues.append(Stage0Issue("plan.schema", str(paths["plan"]), message))
    for message in json_schema_errors(manifest_schema, manifest):
        issues.append(Stage0Issue("manifest.schema", str(paths["manifest"]), message))
    if isinstance(plan, dict):
        issues.extend(validate_plan_semantics(plan, paths["plan"]))
    if isinstance(plan, dict) and isinstance(manifest, dict):
        if plan.get("run_id") != manifest.get("run_id"):
            issues.append(Stage0Issue("run_id.mismatch", str(paths["manifest"]), "plan and manifest run IDs differ"))
        if plan.get("random_seed") != manifest.get("random_seed"):
            issues.append(Stage0Issue("random_seed.mismatch", str(paths["manifest"]), "plan and manifest seeds differ"))
        if manifest.get("empirical_record_count") != 0 or manifest.get("human_reviewed_record_count") != 0:
            issues.append(
                Stage0Issue("empirical_count.nonzero", str(paths["manifest"]), "Stage 0 record counts must remain zero")
            )
        if manifest.get("restricted_inputs_present") is not False:
            issues.append(
                Stage0Issue("restricted_input.present", str(paths["manifest"]), "Stage 0 cannot use restricted inputs")
            )

    if not issues:
        computed_receipt = build_receipt(stage0_root)
        committed_receipt = load_json(paths["receipt"])
        if computed_receipt != committed_receipt:
            issues.append(
                Stage0Issue(
                    "receipt.mismatch",
                    str(paths["receipt"]),
                    "committed receipt does not match the deterministic Stage 0 export",
                )
            )
        if not all(computed_receipt["checks"].values()):
            issues.append(Stage0Issue("check.failed", str(paths["receipt"]), "one or more Stage 0 checks failed"))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage0-root", type=Path, default=DEFAULT_STAGE0_ROOT)
    parser.add_argument("--print-computed-receipt", action="store_true")
    args = parser.parse_args()

    if args.print_computed_receipt:
        print(json.dumps(build_receipt(args.stage0_root), indent=2, ensure_ascii=False))
        return 0

    issues = validate_stage0_artifacts(args.stage0_root)
    if issues:
        print(f"Stage 0 rehearsal failed with {len(issues)} issue(s):")
        for issue in issues:
            print(f"- [{issue.code}] {issue.path}: {issue.message}")
        return 1

    receipt = build_receipt(args.stage0_root)
    counts = receipt["counts"]
    print(
        "Stage 0 rehearsal passed: "
        f"{counts['synthetic_items']} synthetic items, "
        f"{counts['blinded_candidate_rows']} blinded candidate rows, "
        f"{counts['synthetic_assignments']} assignments, and "
        f"{counts['adjudicated_candidates']} adjudications."
    )
    print("Operational readiness only; no translation, reviewer, safety, or empirical claim is established.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
