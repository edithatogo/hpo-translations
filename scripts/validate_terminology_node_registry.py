"""Validate exact terminology registry coverage and fail-closed variant identity."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_terminology_node_registry import OUTPUT, ROOT, build_registry, canonical_bytes, load

SCHEMA = ROOT / "research_validation" / "terminology_node_registry.schema.json"
UNSAFE_PARENT_VALUES = {"ICD10CM", "ICD-10-CM", "ICD10CA", "ICD-10-CA", "SCTID-CA", "SNOMED CT CA"}


def validation_errors(registry: dict[str, Any]) -> list[str]:
    errors = [
        error.message
        for error in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(registry)
    ]
    nodes = registry.get("nodes", [])
    ids = [item.get("node_id") for item in nodes]
    if len(ids) != len(set(ids)):
        errors.append("node IDs must be unique")
    known = set(ids)
    for item in nodes:
        if item.get("parent_node_id") not in known and item.get("parent_node_id") is not None:
            errors.append(f"{item.get('node_id')} references an unknown parent")
    expected = build_registry()
    expected_namespaces = {item["node_id"] for item in expected["nodes"] if item["node_kind"] == "identifier_namespace"}
    actual_namespaces = {item["node_id"] for item in nodes if item.get("node_kind") == "identifier_namespace"}
    if actual_namespaces != expected_namespaces:
        errors.append("identifier namespace coverage must exactly match mapping artifacts and source coverage")
    expected_editions = {item["node_id"] for item in expected["nodes"] if item["node_kind"] == "edition"}
    actual_editions = {item["node_id"] for item in nodes if item.get("node_kind") == "edition"}
    if actual_editions != expected_editions:
        errors.append("edition coverage must exactly match ICD-10 and SNOMED inventories")
    renditions = registry.get("language_renditions", [])
    rendition_ids = [item.get("rendition_id") for item in renditions]
    if len(rendition_ids) != len(set(rendition_ids)):
        errors.append("language rendition IDs must be unique")
    rendition_rows = {
        (item.get("rendition_id"), item.get("parent_node_id"), item.get("bcp47"), item.get("status"))
        for item in renditions
    }
    expected_rows = {
        (item["rendition_id"], item["parent_node_id"], item["bcp47"], item["status"])
        for item in expected["language_renditions"]
    }
    if rendition_rows != expected_rows:
        errors.append("language rendition coverage must exactly match governed inventories")
    for item in renditions:
        if item.get("parent_node_id") not in known:
            errors.append(f"{item.get('rendition_id')} references an unknown parent")
    for family in ("family-icd10", "family-snomed-ct"):
        record = next((item for item in nodes if item.get("node_id") == family), {})
        values = {item.get("value") for item in record.get("aliases", [])}
        if values & UNSAFE_PARENT_VALUES:
            errors.append(f"{family} contains an unsafe edition alias")
    alias_owners: dict[tuple[str, str], set[str]] = {}
    for item in nodes:
        for entry in item.get("aliases", []):
            if entry.get("alias_type") in {"canonical_prefix", "edition_uri", "profile_id", "product_id"}:
                key = (entry.get("alias_type", ""), entry.get("value", "").casefold())
                alias_owners.setdefault(key, set()).add(item["node_id"])
    if any(len(owners) > 1 for owners in alias_owners.values()):
        errors.append("resolving typed aliases must be unique")
    boundary = registry.get("admission_boundary", {})
    if any(
        boundary.get(key) is not False
        for key in (
            "payloads_included",
            "parent_relations_create_mappings",
            "language_variants_are_interchangeable",
            "edition_inheritance_allowed",
        )
    ):
        errors.append("variant admission boundary must remain fail-closed")
    return sorted(set(errors))


def main() -> int:
    registry = load(OUTPUT)
    errors = validation_errors(registry)
    if OUTPUT.read_bytes().replace(b"\r\n", b"\n") != canonical_bytes(build_registry()):
        errors.append("committed terminology node registry does not match deterministic generation")
    if errors:
        for error in sorted(set(errors)):
            print(f"ERROR: {error}")
        return 1
    counts: dict[str, int] = {}
    for item in registry["nodes"]:
        counts[item["node_kind"]] = counts.get(item["node_kind"], 0) + 1
    rendition_count = len(registry["language_renditions"])
    print(f"Terminology node registry validation passed: {counts}; {rendition_count} language renditions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
