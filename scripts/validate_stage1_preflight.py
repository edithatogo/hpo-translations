from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research_validation"
PREFLIGHT = RESEARCH / "stage_1_execution_preflight.json"
SCHEMA = RESEARCH / "stage_1_execution_preflight.schema.json"
FREEZE = RESEARCH / "phase_4_freeze"


def load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validation_errors(preflight: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = [f"schema: {item.message}" for item in Draft202012Validator(schema).iter_errors(preflight)]
    manifest = load(FREEZE / "component_manifest.json")
    sampling = load(FREEZE / "sampling_frame.json")
    conditions = load(FREEZE / "candidate_conditions.json")
    panel = load(FREEZE / "agent_panel_instrument.json")
    for name, expected in manifest.get("component_hashes", {}).items():
        path = FREEZE / name
        if not path.is_file() or digest(path) != expected:
            errors.append(f"frozen component hash drift: {name}")
    if preflight.get("stage_1_hpo_ids") != sampling.get("stage_1_hpo_ids"):
        errors.append("preflight HPO IDs must match the frozen Stage 1 sample")
    units = sum(
        2 if item["hpo_id"] in sampling["stage_1_hpo_ids"] and len(item["languages"]) == 2 else 1
        for item in sampling["assignments"]
        if item["hpo_id"] in sampling["stage_1_hpo_ids"]
    )
    if preflight.get("concept_language_unit_count") != units:
        errors.append("preflight unit count must match the frozen Stage 1 sample")
    condition_count = len(conditions.get("conditions", []))
    if (
        preflight.get("candidate_condition_count") != condition_count
        or preflight.get("candidate_row_count") != units * condition_count
    ):
        errors.append("preflight candidate counts must match the frozen conditions")
    if (
        preflight.get("specialist_roles") != panel.get("roles")
        or preflight.get("adjudicator") != panel.get("adjudicator")
        or preflight.get("auditor") != panel.get("auditor")
    ):
        errors.append("preflight panel must match the frozen agent instrument")
    for relative in preflight.get("gate_receipts", []):
        if not (ROOT / relative).is_file():
            errors.append(f"missing gate receipt: {relative}")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(load(PREFLIGHT), load(SCHEMA))
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(
        "Stage 1 preflight passed: 13 frozen components, 12 units, 48 candidate rows, "
        "5 specialists + adjudicator + auditor; execution not started."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
