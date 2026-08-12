import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "research_validation" / "registry_source_expansion_catalog.json"
SCHEMA_PATH = ROOT / "research_validation" / "registry_source_expansion_catalog.schema.json"
EXPECTED_REGISTRIES = {"obo-foundry", "ols4", "ontobee", "bioportal", "fairsharing", "lov", "umich-guide"}
EXPECTED_SOURCES = {
    "maxo",
    "hpo-associations",
    "maxo-annotations",
    "rgd-measurement-stack",
    "eco-sepio",
    "ga4gh-phenopackets",
    "phenopacket-store",
    "ga4gh-beacon",
    "ga4gh-duo",
    "geno",
    "oae",
    "hancestro",
    "wikidata-hpo",
    "do-spanish",
    "nci-cancer-dictionaries",
    "elements-of-morphology",
    "ga4gh-vrs-va",
    "obi-obcs-ogms-labo",
    "ichpt",
    "ga4gh-deferred",
    "icpc3-discovery",
}


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(catalog: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = [f"schema: {error.message}" for error in Draft202012Validator(schema).iter_errors(catalog)]
    registries = catalog.get("registry_policy", {}).get("discovery_registries", [])
    registry_ids = [row.get("registry_id") for row in registries if isinstance(row, dict)]
    if set(registry_ids) != EXPECTED_REGISTRIES or len(registry_ids) != len(EXPECTED_REGISTRIES):
        errors.append("discovery registry set must exactly match the governed seven-registry inventory")
    sources = catalog.get("sources", [])
    source_ids = [row.get("source_id") for row in sources if isinstance(row, dict)]
    if set(source_ids) != EXPECTED_SOURCES or len(source_ids) != len(EXPECTED_SOURCES):
        errors.append("registry expansion source set must exactly match the governed 21-source inventory")
    for row in sources:
        if not isinstance(row, dict):
            continue
        if row.get("direct_lexical_vote") is not False:
            errors.append(f"{row.get('source_id')}: direct lexical vote must remain false")
        if row.get("source_kind") in {
            "schema",
            "discovery_api_schema",
            "genomic_representation_schema_family",
        } and row.get("languages"):
            errors.append(f"{row.get('source_id')}: language-neutral schema cannot claim language coverage")
        if row.get("archive_status", "").startswith("eligible") and any(
            term in str(row.get("release")) for term in ("pending", "unresolved", "unpinned")
        ):
            errors.append(f"{row.get('source_id')}: archive eligibility requires an exact release")
    refs = {ref for study in catalog.get("planned_studies", []) for ref in study.get("sources", [])}
    if not refs <= EXPECTED_SOURCES:
        errors.append("planned study references unknown sources")
    controls = catalog.get("controls", {})
    if (
        any(
            controls.get(key) is not False
            for key in (
                "payload_retrieval_authorized",
                "translation_rows_added",
                "empirical_execution_authorized",
                "remote_upload_authorized",
                "github_mutation_authorized",
                "upstream_mutation_authorized",
                "automatic_promotion_allowed",
            )
        )
        or controls.get("new_freeze_required") is not True
    ):
        errors.append("registry expansion controls must remain fail-closed")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(load_json(CATALOG_PATH), load_json(SCHEMA_PATH))
    if errors:
        print("Registry source expansion validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Registry source expansion validation passed (21 sources; 7 registries; zero payload authority).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
