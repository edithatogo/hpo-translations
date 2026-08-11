import json
import re
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "research_validation" / "language_readiness_catalog.json"
SCHEMA_PATH = ROOT / "research_validation" / "language_readiness_catalog.schema.json"
SUPPLEMENTARY_PATH = ROOT / "research_validation" / "supplementary_source_access_reviews.json"
UMLS_PATH = ROOT / "conductor" / "tracks" / "umls_metathesaurus_integration_20260623" / "release_inventory_2026aa.json"
SNOMED_PATH = ROOT / "conductor" / "tracks" / "snomed_ct_integration_20260623" / "national_edition_inventory.json"
ICD10_PATH = ROOT / "conductor" / "tracks" / "icd10_integration_20260623" / "national_variant_inventory.json"
LANGUAGE_TAG = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
EXPECTED_CANDIDATES = {"ko", "pl", "ru", "sv", "uk"}
EXPECTED_REGIONAL_TAGS = {
    "de-AT",
    "de-DE",
    "es-AR",
    "es-ES",
    "es-MX",
    "fr-BE",
    "fr-CA",
    "fr-FR",
    "nl-BE",
    "nl-NL",
    "pt-BR",
    "pt-PT",
    "zh-Hans",
    "zh-Hant",
}
EXPECTED_PRO_TRANSLATION_NAMES = {
    "Afrikaans",
    "Arabic",
    "Assamese",
    "Belarusian",
    "Bengali",
    "Bosnian",
    "Bulgarian",
    "Cebuano",
    "Chinese (Simplified) (Universal)",
    "Chinese (Traditional) (Universal)",
    "Croatian (Universal)",
    "Czech",
    "Danish",
    "Dutch",
    "English (Universal)",
    "Estonian",
    "Finnish",
    "French (for Canada)",
    "French (for France, Belgium, Switzerland)",
    "Georgian",
    "German (Universal)",
    "Greek",
    "Gujarati",
    "Haitian Creole",
    "Hausa",
    "Hebrew",
    "Hiligaynon",
    "Hindi",
    "Hungarian",
    "Icelandic",
    "Igbo",
    "Ilocano",
    "Italian",
    "Japanese",
    "Kannada",
    "Kazakh",
    "Korean",
    "Latvian",
    "Luganda",
    "Macedonian",
    "Malay",
    "Malayalam",
    "Marathi",
    "North Sotho/Sepedi",
    "Norwegian",
    "Odia/Oriya",
    "Persian/Farsi",
    "Polish",
    "Portuguese (for Brazil)",
    "Portuguese (for Portugal)",
    "Punjabi",
    "Romanian",
    "Russian (Universal)",
    "Serbian (for Serbia)",
    "Serbian (for Bosnia and Herzegovina)",
    "Setswana/Tswana",
    "Slovak",
    "Slovenian",
    "Southern Sotho/Sesotho",
    "Spanish (Universal)",
    "Swahili",
    "Swedish",
    "Tagalog",
    "Tamil",
    "Telugu",
    "Thai",
    "Tongan",
    "Turkish",
    "Twi",
    "Ukrainian",
    "Urdu",
    "Vietnamese",
    "Xhosa",
    "Welsh",
    "Yoruba",
    "Zulu",
}
EXPECTED_PRO_DEVELOPMENT = {
    ("Amharic", "am", ("Ethiopia", "United States")),
    ("Arabic", "ar", ("Jordan", "Lebanon", "UAE", "Oman")),
    ("Indonesian/Bahasa Indonesia", "id", ("Indonesia",)),
    ("Lithuanian", "lt", ("Lithuania",)),
    ("Tsonga", "ts", ("South Africa",)),
}
EXPECTED_PED_DEVELOPMENT = {
    ("Greek", "el", ("Greece",)),
    ("Hungarian", "hu", ("Hungary",)),
    ("Malay", "ms", ("Singapore", "Malaysia")),
    ("Polish", "pl", ("Poland",)),
    ("Thai", "th", ("Thailand",)),
    ("Turkish", "tr", ("Turkey",)),
    ("Vietnamese", "vi", ("Vietnam",)),
}


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(
    catalog: dict[str, Any],
    schema: dict[str, Any],
    supplementary: dict[str, Any],
    umls: dict[str, Any],
    snomed: dict[str, Any],
    icd10: dict[str, Any],
    babelon_dir: Path,
) -> list[str]:
    validator = cast(Any, Draft202012Validator(schema, format_checker=FormatChecker()))
    errors = [error.message for error in validator.iter_errors(catalog)]
    candidate_records = cast(list[dict[str, Any]], catalog.get("hpo_candidate_languages", []))
    candidates = {language for item in candidate_records if isinstance(language := item.get("language"), str)}
    if candidates != EXPECTED_CANDIDATES:
        errors.append("HPO metadata candidate languages must be exactly ko, pl, ru, sv, and uk")
    active_assets = {
        path.name.removeprefix("hp-").removesuffix(".babelon.tsv") for path in babelon_dir.glob("hp-*.babelon.tsv")
    }
    overlap = candidates & active_assets
    if overlap:
        errors.append(f"candidate languages already have HPO Babelon assets: {sorted(overlap)}")

    regional_families = cast(list[dict[str, Any]], catalog.get("regional_contexts", []))
    regional_records: list[dict[str, Any]] = [
        tag for family in regional_families for tag in cast(list[dict[str, Any]], family.get("tags", []))
    ]
    regional_tags = {tag for record in regional_records if isinstance(tag := record.get("tag"), str)}
    if regional_tags != EXPECTED_REGIONAL_TAGS or len(regional_records) != len(regional_tags):
        errors.append("regional contexts must contain the exact unique prespecified language tags")
    for tag in candidates | regional_tags:
        if not LANGUAGE_TAG.fullmatch(tag):
            errors.append(f"invalid BCP 47 language tag: {tag!r}")

    pro = cast(dict[str, Any], catalog.get("pro_ctcae", {}))
    validated_translations = cast(list[dict[str, Any]], pro.get("validated_translations", []))
    inventory_tags = set(umls.get("regional_loinc_2_82_editions", []))
    inventory_tags.update(
        language
        for item in snomed.get("translation_profiles", [])
        + snomed.get("edition_examples_without_translation_inference", [])
        for language in item.get("languages", [])
    )
    inventory_tags.update(
        language
        for item in icd10.get("variant_profiles", []) + icd10.get("mapping_profiles", [])
        for language in item.get("languages", [])
    )
    inventory_tags.update(tag for item in validated_translations if isinstance(tag := item.get("language_tag"), str))
    for record in regional_records:
        if record.get("evidence_status") == "confirmed_public_metadata" and record.get("tag") not in inventory_tags:
            errors.append(f"confirmed regional context is absent from validated inventories: {record.get('tag')}")
        if record.get("evidence_status") != "confirmed_public_metadata" and record.get("evidence_sources") == []:
            continue
        if not record.get("evidence_sources"):
            errors.append(f"confirmed regional context lacks evidence sources: {record.get('tag')}")

    decs = catalog.get("decs", {})
    if set(decs.get("languages", [])) != {"en", "es", "fr", "pt"}:
        errors.append("DeCS metadata language set must be exactly en, es, fr, and pt")

    supplementary_records = cast(list[dict[str, Any]], supplementary.get("reviews", []))
    pro_review = next(
        (record for record in supplementary_records if record.get("source_id") == "pro-ctcae"),
        cast(dict[str, Any], {}),
    )
    expected_overlap = set(cast(list[str], pro_review.get("active_translation_profile_overlap", [])))
    validated_tags = {tag for item in validated_translations if isinstance(tag := item.get("language_tag"), str)}
    if not expected_overlap <= {tag.split("-", 1)[0] for tag in validated_tags}:
        errors.append("PRO-CTCAE authority table must cover every locally recorded active-profile overlap")
    names = {name for item in validated_translations if isinstance(name := item.get("authority_name"), str)}
    if names != EXPECTED_PRO_TRANSLATION_NAMES or len(validated_translations) != len(names):
        errors.append("PRO-CTCAE validated translation names must exactly match the 2026-08-11 authority table")
    if len(validated_tags) != len(validated_translations):
        errors.append("PRO-CTCAE validated translation language tags must be unique")
    expected_special_tags = {
        "Chinese (Simplified) (Universal)": "zh-Hans",
        "Chinese (Traditional) (Universal)": "zh-Hant",
        "French (for Canada)": "fr-CA",
        "French (for France, Belgium, Switzerland)": "fr-FR",
        "Portuguese (for Brazil)": "pt-BR",
        "Portuguese (for Portugal)": "pt-PT",
        "Serbian (for Serbia)": "sr-RS",
        "Serbian (for Bosnia and Herzegovina)": "sr-BA",
        "English (Universal)": "en",
        "Spanish (Universal)": "es",
    }
    actual_special_tags = {
        item.get("authority_name"): item.get("language_tag")
        for item in validated_translations
        if item.get("authority_name") in expected_special_tags
    }
    if actual_special_tags != expected_special_tags:
        errors.append("PRO-CTCAE universal and regional variants must retain their exact language tags")
    twi = next(
        (item for item in validated_translations if item.get("authority_name") == "Twi"),
        cast(dict[str, Any], {}),
    )
    if twi.get("language_tag") != "tw" or twi.get("repository_profile_linkage") != "unresolved_do_not_link_to_hp_tw":
        errors.append("PRO-CTCAE Twi must remain unlinked from the unresolved repository tw profile")

    development = cast(dict[str, Any], pro.get("in_development", {}))

    def development_set(key: str) -> set[tuple[str, str, tuple[str, ...]]]:
        records = cast(list[dict[str, Any]], development.get(key, []))
        return {
            (
                str(item.get("authority_name")),
                str(item.get("language_tag")),
                tuple(cast(list[str], item.get("countries", []))),
            )
            for item in records
        }

    if development_set("pro_ctcae") != EXPECTED_PRO_DEVELOPMENT:
        errors.append("PRO-CTCAE in-development metadata must exactly match the 2026-08-11 authority list")
    if development_set("ped_pro_ctcae_separate_module") != EXPECTED_PED_DEVELOPMENT:
        errors.append("Ped-PRO-CTCAE in-development metadata must remain exact and separate")
    if development.get("availability_status") != "in_development_not_validated_or_available":
        errors.append("in-development translations must not be represented as validated or available")

    if catalog.get("translation_rows_added") != 0 or catalog.get("source_payload_rows_added") != 0:
        errors.append("language readiness catalog must remain metadata-only")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(
        load_json(CATALOG_PATH),
        load_json(SCHEMA_PATH),
        load_json(SUPPLEMENTARY_PATH),
        load_json(UMLS_PATH),
        load_json(SNOMED_PATH),
        load_json(ICD10_PATH),
        ROOT / "babelon",
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Language readiness catalog validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
