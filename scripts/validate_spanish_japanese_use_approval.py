from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "research_validation" / "spanish_japanese_use_approval.json"
SCHEMA = ROOT / "research_validation" / "spanish_japanese_use_approval.schema.json"
PAYLOAD = ROOT / "research_validation" / "pilot_source_payload_manifest.json"


def load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(receipt: dict[str, Any], schema: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    errors = [f"schema: {item.message}" for item in Draft202012Validator(schema).iter_errors(receipt)]
    expected_sources = [row["source_id"] for row in payload["payloads"]]
    if receipt.get("source_snapshots") != expected_sources:
        errors.append("approval must bind the exact two frozen payload source IDs")
    urls = receipt.get("license_evidence", {})
    if urls.get("provided_url") != "https://hpo.jax.org/license":
        errors.append("approval must preserve the exact maintainer-provided licence URL")
    if any(receipt.get(key) is not False for key in ("promotion_allowed", "empirical_execution_authorized")):
        errors.append("approval cannot authorize promotion or bypass ethics/privacy")
    conditions = set(receipt.get("study_conditions", []))
    if "no_upstream_write" not in conditions or "no_human_or_community_validation_claim" not in conditions:
        errors.append("approval must preserve upstream-write and validation-claim boundaries")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(load(RECEIPT), load(SCHEMA), load(PAYLOAD))
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    digest = hashlib.sha256(RECEIPT.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    print(f"Spanish/Japanese use approval validation passed: sha256:{digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
