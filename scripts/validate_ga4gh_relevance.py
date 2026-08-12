import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "research_validation" / "ga4gh_relevance_catalog.json"
SCHEMA = ROOT / "research_validation" / "ga4gh_relevance_catalog.schema.json"
EXPECTED = {
    "phenopackets",
    "pedigree",
    "human-exposome",
    "vrs",
    "cat-vrs",
    "va-spec",
    "sequence-annotation",
    "pharmacogenomics",
    "expmeta",
    "wgs-qc",
    "duo",
    "data-passports",
    "beacon",
    "phenopacket-store",
}


def load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(catalog: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = [f"schema: {error.message}" for error in Draft202012Validator(schema).iter_errors(catalog)]
    products = catalog.get("products", [])
    ids = [row.get("product_id") for row in products if isinstance(row, dict)]
    if set(ids) != EXPECTED or len(ids) != len(EXPECTED):
        errors.append("GA4GH relevance set must exactly match the governed 14-product inventory")
    for row in products:
        if not isinstance(row, dict):
            continue
        product_id = row.get("product_id")
        if not row.get("mapping_paths"):
            errors.append(f"{product_id}: at least one mapping path is required")
        if row.get("direct_lexical_vote") is not False or row.get("payload_authorized") is not False:
            errors.append(f"{product_id}: lexical and payload authority must remain false")
        if "developmental" in str(row.get("lifecycle")) and row.get("mapping_evidence") is None:
            errors.append(f"{product_id}: developmental products still require mapping evidence")
    controls = catalog.get("controls", {})
    if controls != {
        "maturity_exclusion_allowed": False,
        "mapping_path_required": True,
        "empirical_execution_authorized": False,
        "payload_retrieval_authorized": False,
        "new_freeze_required": True,
        "automatic_promotion_allowed": False,
    }:
        errors.append("GA4GH controls must remain relevance-first and fail-closed")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(load(CATALOG), load(SCHEMA))
    if errors:
        print("GA4GH relevance validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("GA4GH relevance validation passed (14 mapped products; maturity is not an exclusion gate).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
