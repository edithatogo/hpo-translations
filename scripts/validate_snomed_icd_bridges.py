import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "research_validation" / "snomed_icd_crosslingual_bridge_catalog.json"
SCHEMA = ROOT / "research_validation" / "snomed_icd_crosslingual_bridge_catalog.schema.json"
EXPECTED = {"umls-2026aa", "nlm-snomed-map-products", "omop-athena", "orphadata-alignments", "meddra-snomed"}


def load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(catalog: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = [f"schema: {error.message}" for error in Draft202012Validator(schema).iter_errors(catalog)]
    resources = catalog.get("resources", [])
    ids = [row.get("resource_id") for row in resources if isinstance(row, dict)]
    if set(ids) != EXPECTED or len(ids) != len(EXPECTED):
        errors.append("bridge set must exactly cover UMLS, NLM maps, OMOP/Athena, Orphadata and MedDRA")
    direct = [row.get("resource_id") for row in resources if row.get("connection_type") == "direct_authority_map"]
    if direct != ["nlm-snomed-map-products"]:
        errors.append("only the authority-published NLM/SNOMED map family may be classified as direct")
    for row in resources:
        if row.get("payload_authorized") is not False:
            errors.append(f"{row.get('resource_id')}: payload authority must remain false")
        if not row.get("snomed_endpoint") or not row.get("icd_endpoint"):
            errors.append(f"{row.get('resource_id')}: both terminology endpoints are required")
    if not any(row.get("resource_id") == "omop-athena" and "Athena" in row.get("name", "") for row in resources):
        errors.append("Athena must be represented as the OMOP distribution interface, not an independent lineage")
    controls = catalog.get("controls", {})
    if (
        any(
            controls.get(key) is not False
            for key in (
                "payload_retrieval_authorized",
                "authenticated_access_authorized",
                "empirical_execution_authorized",
                "direct_equivalence_inference_allowed",
                "remote_upload_authorized",
            )
        )
        or controls.get("new_freeze_required") is not True
    ):
        errors.append("bridge controls must remain fail-closed")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(load(CATALOG), load(SCHEMA))
    if errors:
        print("SNOMED-ICD bridge validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("SNOMED-ICD bridge validation passed (5 governed resources; direct and mediated paths separated).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
