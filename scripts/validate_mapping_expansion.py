import json
import re
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "research_validation" / "mapping_expansion_catalog.json"
SCHEMA_PATH = ROOT / "research_validation" / "mapping_expansion_catalog.schema.json"
SOURCE_REGISTRY_PATH = ROOT / "ontology_network" / "source_registry.json"
SOURCE_CATALOG_PATH = ROOT / "research_validation" / "source_catalog.json"
SUPPLEMENTARY_REVIEWS_PATH = ROOT / "research_validation" / "supplementary_source_access_reviews.json"
UMLS_INVENTORY_PATH = (
    ROOT / "conductor" / "tracks" / "umls_metathesaurus_integration_20260623" / "release_inventory_2026aa.json"
)
SNOMED_INVENTORY_PATH = (
    ROOT / "conductor" / "tracks" / "snomed_ct_integration_20260623" / "national_edition_inventory.json"
)
ICD10_INVENTORY_PATH = ROOT / "conductor" / "tracks" / "icd10_integration_20260623" / "national_variant_inventory.json"
LANGUAGE_TAG = re.compile(r"^(?:und|[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*)$")


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(
    catalog: dict[str, Any],
    schema: dict[str, Any],
    source_registry: dict[str, Any],
    source_catalog: dict[str, Any],
    supplementary_reviews: dict[str, Any],
    umls_inventory: dict[str, Any],
    snomed_inventory: dict[str, Any],
    icd10_inventory: dict[str, Any],
) -> list[str]:
    errors = [
        error.message for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(catalog)
    ]
    artifact_ids = [item.get("artifact_id") for item in catalog.get("artifacts", [])]
    if len(artifact_ids) != len(set(artifact_ids)):
        errors.append("artifact_id values must be unique")

    registered_ids = {item.get("source_id") for item in source_registry.get("records", []) if isinstance(item, dict)}
    catalog_ids = set(catalog.get("registered_source_ids", []))
    if catalog_ids != registered_ids:
        errors.append("registered_source_ids must exactly cover the ontology source registry")

    coverage = catalog.get("source_coverage", [])
    coverage_ids = [item.get("source_id") for item in coverage if isinstance(item, dict)]
    if len(coverage_ids) != len(set(coverage_ids)) or set(coverage_ids) != catalog_ids:
        errors.append("source_coverage must contain each registered source exactly once")

    known_artifacts = set(artifact_ids)
    artifact_records = {item.get("artifact_id"): item for item in catalog.get("artifacts", [])}
    for item in coverage:
        if not isinstance(item, dict):
            continue
        unknown = set(item.get("artifact_ids", [])) - known_artifacts
        if unknown:
            errors.append(f"{item.get('source_id')} references unknown artifacts: {sorted(unknown)}")

    if any(item.get("payload_commit_allowed") is not False for item in catalog.get("artifacts", [])):
        errors.append("every mapping artifact must remain payload-commit blocked")

    for artifact in catalog.get("artifacts", []):
        for language in artifact.get("languages", []):
            if not isinstance(language, str) or not LANGUAGE_TAG.fullmatch(language):
                errors.append(f"{artifact.get('artifact_id')} has invalid BCP 47 language tag: {language!r}")

    source_catalog_ids = {item.get("source_id") for item in source_catalog.get("mappings", [])}
    supplementary_ids = {item.get("source_id") for item in supplementary_reviews.get("reviews", [])}
    catalog_ids_by_name = {
        "source_catalog": source_catalog_ids,
        "supplementary_source_access_reviews": supplementary_ids,
    }
    link_keys: list[tuple[Any, Any]] = []
    for link in catalog.get("cross_catalog_links", []):
        artifact_id = link.get("artifact_id")
        catalog_name = link.get("catalog")
        link_keys.append((artifact_id, catalog_name))
        if artifact_id not in known_artifacts:
            errors.append(f"cross-catalog link references unknown artifact: {artifact_id}")
        unknown_records = set(link.get("record_ids", [])) - catalog_ids_by_name.get(catalog_name, set())
        if unknown_records:
            errors.append(f"{artifact_id} references unknown {catalog_name} records: {sorted(unknown_records)}")
    if len(link_keys) != len(set(link_keys)):
        errors.append("cross-catalog artifact and catalog links must be unique")
    required_links = {
        ("medgen-id-mappings", "source_catalog"),
        ("cell-ontology-relations", "supplementary_source_access_reviews"),
        ("hpo-hp-mp-manual", "source_catalog"),
        ("nando-ontology", "supplementary_source_access_reviews"),
    }
    missing_links = required_links - set(link_keys)
    if missing_links:
        errors.append(f"required cross-catalog links are missing: {sorted(missing_links)}")

    required_artifacts = {
        "medgen-id-mappings",
        "cell-ontology-relations",
        "hpo-hp-mp-manual",
        "nando-ontology",
        "snomedctca-icd10ca-map",
    }
    missing_required = required_artifacts - known_artifacts
    if missing_required:
        errors.append(f"required direct or cross-catalog artifacts are missing: {sorted(missing_required)}")

    source_mapping_records = {item.get("source_id"): item for item in source_catalog.get("mappings", [])}
    hp_mp = artifact_records.get("hpo-hp-mp-manual", {})
    hp_mp_source = source_mapping_records.get("hpo-hp-mp-manual-collection", {})
    if hp_mp.get("versioned_url") != hp_mp_source.get("versioned_url"):
        errors.append("HP-MP artifact URL must match the canonical source catalog record")
    if hp_mp.get("integrity") != hp_mp_source.get("integrity"):
        errors.append("HP-MP artifact integrity must match the canonical source catalog record")
    if hp_mp.get("lineage_group") != hp_mp_source.get("shared_lineage_cluster"):
        errors.append("HP-MP artifact lineage must match the canonical source catalog record")

    medgen_link = next(
        (link for link in catalog.get("cross_catalog_links", []) if link.get("artifact_id") == "medgen-id-mappings"),
        {},
    )
    medgen_records = [source_mapping_records.get(record_id, {}) for record_id in medgen_link.get("record_ids", [])]
    if len(medgen_records) != 2 or any(
        record.get("originating_authority") != "MedGen" or record.get("origin_dataset") != "MedGenIDMappings.txt"
        for record in medgen_records
    ):
        errors.append("MedGen direct-source link must cover both canonical MedGen-derived HPO mapping records")

    supplementary_records = {item.get("source_id"): item for item in supplementary_reviews.get("reviews", [])}
    for artifact_id, source_id in (
        ("cell-ontology-relations", "cell-ontology"),
        ("nando-ontology", "nando"),
    ):
        artifact = artifact_records.get(artifact_id, {})
        review = supplementary_records.get(source_id, {})
        version = review.get("source_version", {})
        if artifact.get("release") != version.get("value"):
            errors.append(f"{artifact_id} release must match its supplementary source review")
        commit_sha = version.get("commit_sha")
        if commit_sha is not None and artifact.get("integrity") != {
            "algorithm": "git_commit",
            "value": commit_sha,
        }:
            errors.append(f"{artifact_id} integrity must match its supplementary source review")

    coverage_by_source = {item.get("source_id"): item for item in catalog.get("source_coverage", [])}
    expected_languages = {
        "umls": {item.get("bcp47") for item in umls_inventory.get("languages", [])},
        "snomed_ct": {
            language
            for item in snomed_inventory.get("translation_profiles", [])
            + snomed_inventory.get("edition_examples_without_translation_inference", [])
            for language in item.get("languages", [])
        },
        "icd10": {
            language
            for item in icd10_inventory.get("variant_profiles", []) + icd10_inventory.get("mapping_profiles", [])
            for language in item.get("languages", [])
        },
    }
    for source_id, languages in expected_languages.items():
        actual = set(coverage_by_source.get(source_id, {}).get("additional_languages", []))
        if actual != languages:
            errors.append(f"{source_id} additional_languages must exactly match its validated inventory")

    canadian_map = artifact_records.get("snomedctca-icd10ca-map", {})
    canadian_profile = next(
        (
            item
            for item in icd10_inventory.get("mapping_profiles", [])
            if item.get("map_id") == "snomedctca_to_icd10ca_2026_03_25"
        ),
        {},
    )
    if canadian_map.get("languages") != canadian_profile.get("languages") or canadian_map.get(
        "release"
    ) != canadian_profile.get("release_date"):
        errors.append(
            "Canadian SNOMED CT to ICD-10-CA artifact must match the national inventory release and languages"
        )
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(
        load_json(CATALOG_PATH),
        load_json(SCHEMA_PATH),
        load_json(SOURCE_REGISTRY_PATH),
        load_json(SOURCE_CATALOG_PATH),
        load_json(SUPPLEMENTARY_REVIEWS_PATH),
        load_json(UMLS_INVENTORY_PATH),
        load_json(SNOMED_INVENTORY_PATH),
        load_json(ICD10_INVENTORY_PATH),
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Mapping expansion catalog validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
