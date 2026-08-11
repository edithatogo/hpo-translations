import json
import re
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "conductor" / "schemas"
INVENTORIES = {
    "umls": ROOT / "conductor/tracks/umls_metathesaurus_integration_20260623/release_inventory_2026aa.json",
    "snomed": ROOT / "conductor/tracks/snomed_ct_integration_20260623/national_edition_inventory.json",
    "icd10": ROOT / "conductor/tracks/icd10_integration_20260623/national_variant_inventory.json",
}
SCHEMAS = {
    "umls": SCHEMA_DIR / "umls_public_metadata_inventory_v1.schema.json",
    "snomed": SCHEMA_DIR / "snomed_national_edition_inventory_v1.schema.json",
    "icd10": SCHEMA_DIR / "icd10_national_variant_inventory_v1.schema.json",
}
BCP47 = re.compile(r"^[a-z]{2,3}(?:-[A-Z][a-z]{3})?(?:-(?:[A-Z]{2}|[0-9]{3}))?$")
SECRET_KEYS = {"api_key", "access_token", "authorization", "password", "client_secret"}


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _duplicates(values: list[str]) -> list[str]:
    return sorted({value for value in values if values.count(value) > 1})


def _walk(value: object, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key.lower() in SECRET_KEYS:
                errors.append(f"{child_path}: secret-bearing key is prohibited")
            errors.extend(_walk(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_walk(child, f"{path}[{index}]"))
    elif isinstance(value, str) and (
        re.search(r"(?:CUI|AUI):[A-Za-z0-9]+", value) or re.search(r"(?:sct2|der2)_[A-Za-z0-9_]", value)
    ):
        errors.append(f"{path}: terminology payload identifier or RF2 filename is prohibited")
    return errors


def _languages(rows: list[dict[str, Any]], id_key: str, list_key: str = "languages") -> list[str]:
    errors: list[str] = []
    ids = [str(row.get(id_key, "")) for row in rows]
    if "" in ids:
        errors.append(f"{id_key} values must be nonblank")
    if duplicates := _duplicates(ids):
        errors.append(f"duplicate {id_key} values: {duplicates}")
    for identifier, row in zip(ids, rows, strict=True):
        codes = cast(list[str], row.get(list_key, []))
        if not codes:
            errors.append(f"{identifier}: languages must be nonempty")
        if duplicates := _duplicates(codes):
            errors.append(f"{identifier}: duplicate language codes: {duplicates}")
        for code in codes:
            if not BCP47.fullmatch(code):
                errors.append(f"{identifier}: invalid BCP-47 language code {code!r}")
    return errors


def validation_errors(umls: dict[str, Any], snomed: dict[str, Any], icd10: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    documents = {"umls": umls, "snomed": snomed, "icd10": icd10}
    for name, document in documents.items():
        schema = load_json(SCHEMAS[name])
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors.extend(f"{name}: {error.message}" for error in validator.iter_errors(document))
        errors.extend(f"{name}: {error}" for error in _walk(document))

    if umls.get("payload_policy", {}).get("payload_incorporated") is not False:
        errors.append("umls: payload_incorporated must be false")
    umls_rows = cast(list[dict[str, Any]], umls.get("languages", []))
    codes = [str(row.get("umls_code", "")) for row in umls_rows]
    tags = [str(row.get("bcp47", "")) for row in umls_rows]
    if duplicates := _duplicates(codes):
        errors.append(f"umls: duplicate umls_code values: {duplicates}")
    if duplicates := _duplicates(tags):
        errors.append(f"umls: duplicate bcp47 values: {duplicates}")
    if umls.get("language_count") != len(umls_rows):
        errors.append("umls: language_count must equal languages length")
    for tag in tags:
        if not BCP47.fullmatch(tag):
            errors.append(f"umls: invalid BCP-47 language code {tag!r}")

    if snomed.get("payload_incorporated") is not False:
        errors.append("snomed: payload_incorporated must be false")
    snomed_rows = cast(list[dict[str, Any]], snomed.get("translation_profiles", []))
    errors.extend(f"snomed: {error}" for error in _languages(snomed_rows, "jurisdiction"))
    uris = [str(row["edition_uri"]) for row in snomed_rows if row.get("edition_uri")]
    if duplicates := _duplicates(uris):
        errors.append(f"snomed: duplicate edition_uri values: {duplicates}")
    for row in snomed_rows:
        uri = row.get("edition_uri")
        if uri is None and "unresolved" not in str(row.get("authority_status", "")):
            errors.append(f"snomed: {row.get('jurisdiction')}: null edition_uri requires unresolved authority_status")
        if uri and not re.fullmatch(r"http://snomed\.info/sct/[0-9]+", str(uri)):
            errors.append(f"snomed: invalid edition_uri {uri!r}")
    requirements = " ".join(cast(list[str], snomed.get("admission_requirements", []))).lower()
    for term in ("licence", "effectivetime", "rf2", "redistribution"):
        if term not in requirements:
            errors.append(f"snomed: admission requirements must include {term}")

    if icd10.get("payload_incorporated") is not False:
        errors.append("icd10: payload_incorporated must be false")
    variants = cast(list[dict[str, Any]], icd10.get("variant_profiles", []))
    maps = cast(list[dict[str, Any]], icd10.get("mapping_profiles", []))
    errors.extend(f"icd10: {error}" for error in _languages(variants, "profile_id"))
    errors.extend(f"icd10: {error}" for error in _languages(maps, "map_id"))
    for row in [*variants, *maps]:
        identifier = row.get("profile_id", row.get("map_id"))
        if not str(row.get("licence_gate", "")).strip():
            errors.append(f"icd10: {identifier}: licence_gate must be nonblank")
        missing_release = not row.get("release") and not row.get("release_date")
        if missing_release and "unresolved" not in str(row.get("release_status", "")):
            errors.append(f"icd10: {identifier}: release identity or explicit unresolved status required")

    regional = cast(list[str], umls.get("regional_loinc_2_82_editions", []))
    canada_umls = cast(dict[str, Any], umls.get("canadian_french_source", {}))
    if canada_umls.get("language") != "fr-CA" or "fr-CA" not in regional:
        errors.append("cross: UMLS Canadian French must identify fr-CA regional LOINC")
    if not re.fullmatch(r"LNC-FR-CA_[0-9]+", str(canada_umls.get("source_version", ""))):
        errors.append("cross: invalid UMLS Canadian French source version")
    if "not general" not in str(canada_umls.get("scope", "")).lower():
        errors.append("cross: UMLS Canadian French scope must reject general terminology inference")
    snomed_canada = next((row for row in snomed_rows if row.get("jurisdiction") == "Canada"), {})
    canada_languages = {"en-CA", "fr-CA"}
    if set(snomed_canada.get("languages", [])) != canada_languages:
        errors.append("cross: SNOMED Canada languages must be exactly en-CA and fr-CA")
    if set(snomed_canada.get("language_refsets", {})) != canada_languages:
        errors.append("cross: SNOMED Canada refset keys must match its languages")
    ca_variant = next((row for row in variants if row.get("profile_id") == "icd10ca_ca_2022"), {})
    ca_map = next((row for row in maps if str(row.get("map_id", "")).startswith("snomedctca")), {})
    if set(ca_variant.get("languages", [])) != canada_languages or set(ca_map.get("languages", [])) != canada_languages:
        errors.append("cross: ICD Canada variant and map must be bilingual en-CA/fr-CA")
    direction = str(ca_map.get("direction", ""))
    if "SNOMED CT Canadian Edition" not in direction or "ICD-10-CA" not in direction:
        errors.append("cross: Canadian map direction must name both governed products")
    umls_cui_policy = str(umls.get("mapping_policy", {}).get("cui_co_membership", "")).lower()
    if "candidate" not in umls_cui_policy or "not" not in umls_cui_policy:
        errors.append("umls: CUI co-membership must remain candidate, non-independent evidence")
    french_policy = str(snomed.get("french_lineage", {}).get("policy", "")).lower()
    if "not independent" not in french_policy or "redistribution authority" not in french_policy:
        errors.append("snomed: French lineage must reject independence and redistribution inference")
    pcs = next((row for row in variants if row.get("profile_id") == "icd10pcs_us_2026"), {})
    if "not phenotype" not in str(pcs.get("role", "")).lower():
        errors.append("icd10: ICD-10-PCS must be excluded as phenotype evidence")
    spain = next((row for row in variants if row.get("profile_id") == "cie10es_es_2026"), {})
    if "not an independent lineage" not in str(spain.get("derivation", "")).lower():
        errors.append("icd10: CIE-10-ES derivation must remain non-independent")
    if icd10.get("hpo_mapping_policy", {}).get("direct_official_hpo_icd10_map_found") is not False:
        errors.append("icd10: direct official HPO-ICD10 map claim must remain false")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(*(load_json(INVENTORIES[name]) for name in ("umls", "snomed", "icd10")))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Terminology inventory validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
