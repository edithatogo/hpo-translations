from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "research_validation" / "biomedical_source_preparation_matrix.json"
SCHEMA = ROOT / "research_validation" / "biomedical_source_preparation_matrix.schema.json"
CATALOG = ROOT / "research_validation" / "registry_source_expansion_catalog.json"

EXPECTED = {
    "maxo",
    "hpo-phenotype-hpoa",
    "hpo-genes-to-phenotype",
    "hpo-phenotype-to-genes",
    "maxo-disease-treatment-annotations",
    "cmo",
    "mmo",
    "xco",
    "eco",
    "sepio",
    "phenopackets",
    "phenopacket-store",
    "beacon",
    "duo",
    "wikidata-p3841",
    "disease-ontology-spanish",
    "nci-cancer-dictionary-en",
    "nci-cancer-dictionary-es",
    "elements-of-morphology",
    "geno",
    "oae",
    "hancestro",
}


def load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(matrix: dict[str, Any], schema: dict[str, Any], catalog: dict[str, Any]) -> list[str]:
    errors = [f"schema: {item.message}" for item in Draft202012Validator(schema).iter_errors(matrix)]
    rows = matrix.get("components", [])
    ids = [row.get("id") for row in rows]
    if set(ids) != EXPECTED or len(ids) != len(EXPECTED):
        errors.append("preparation matrix must cover the exact 22-component inventory")
    source_ids = {row["source_id"] for row in catalog["sources"]}
    for row in rows:
        if row.get("source_ref") not in source_ids:
            errors.append(f"unknown registry source reference: {row.get('source_ref')}")
    bound = [item for group in matrix.get("analysis_bindings", []) for item in group.get("components", [])]
    if set(bound) != EXPECTED or len(bound) != len(EXPECTED):
        errors.append("analysis bindings must cover each component exactly once")
    controls = matrix.get("controls", {})
    if any(value is not False for key, value in controls.items() if key != "new_freeze_required"):
        errors.append("preparation controls must remain fail-closed")
    if controls.get("new_freeze_required") is not True:
        errors.append("empirical use must require a new freeze")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(load(MATRIX), load(SCHEMA), load(CATALOG))
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("Biomedical source preparation validation passed: 22 components, 5 analysis groups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
