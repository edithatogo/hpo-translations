from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "research_validation" / "ethics_privacy_determination.json"
SCHEMA = ROOT / "research_validation" / "ethics_privacy_determination.schema.json"
LANGUAGE_APPROVAL = ROOT / "research_validation" / "spanish_japanese_use_approval.json"
PAYLOAD = ROOT / "research_validation" / "pilot_source_payload_manifest.json"


def load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(
    receipt: dict[str, Any], schema: dict[str, Any], language_approval: dict[str, Any], payload: dict[str, Any]
) -> list[str]:
    errors = [f"schema: {item.message}" for item in Draft202012Validator(schema).iter_errors(receipt)]
    scope = receipt.get("scope", {})
    if scope.get("languages") != language_approval.get("languages"):
        errors.append("ethics/privacy scope must match the approved language scope")
    expected_sources = [row["source_id"] for row in payload.get("payloads", [])]
    if scope.get("source_snapshots") != expected_sources:
        errors.append("ethics/privacy scope must bind the exact frozen source snapshots")
    if receipt.get("privacy_controls_required") is not True:
        errors.append("a not-required application determination cannot remove privacy controls")
    if (
        receipt.get("stage_1_execution_gate_closed") is not True
        or receipt.get("stage_1_execution_started") is not False
    ):
        errors.append("the receipt may close the gate but cannot claim Stage 1 has started")
    prohibited = set(receipt.get("does_not_authorize", []))
    if not {"person_participation", "patient_or_identifiable_data", "translation_promotion", "upstream_write"}.issubset(
        prohibited
    ):
        errors.append("the receipt must preserve participant, data, promotion, and upstream boundaries")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(load(RECEIPT), load(SCHEMA), load(LANGUAGE_APPROVAL), load(PAYLOAD))
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    digest = hashlib.sha256(RECEIPT.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    print(f"Ethics/privacy determination validation passed: sha256:{digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
