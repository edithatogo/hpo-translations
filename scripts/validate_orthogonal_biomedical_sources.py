import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "research_validation" / "orthogonal_biomedical_source_catalog.json"
SCHEMA_PATH = ROOT / "research_validation" / "orthogonal_biomedical_source_catalog.schema.json"
EXPECTED_IDS = {
    "who-atc-ddd",
    "who-atcvet",
    "rxnorm-atcprod",
    "chebi",
    "go",
    "uberon-cl",
    "oba-pato-ro",
    "nbo-symp",
    "envo-ecto-exo",
    "pro-uo-ncbitaxon",
    "who-icf",
    "pro-ctcae",
    "medlineplus",
    "radlex",
    "edqm-standard-terms",
    "ema-spor-pms",
    "icnp-icpc3-ichi",
}


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(catalog: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = [
        f"schema: {error.message}"
        for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(catalog)
    ]
    sources = catalog.get("sources", [])
    ids = [row.get("source_id") for row in sources if isinstance(row, dict)]
    if set(ids) != EXPECTED_IDS or len(ids) != len(EXPECTED_IDS):
        errors.append("orthogonal source set must exactly match the governed 17-source inventory")
    analysis_ids = [row.get("analysis_id") for row in catalog.get("analyses", []) if isinstance(row, dict)]
    if analysis_ids != [f"O{i}" for i in range(1, 10)]:
        errors.append("orthogonal analyses must be uniquely ordered O1 through O9")
    for row in sources:
        if not isinstance(row, dict):
            continue
        text = json.dumps(row, sort_keys=True).lower()
        if "phenotype equivalence" in text and "not" not in text and "never" not in text:
            errors.append(f"{row.get('source_id')}: must not claim phenotype equivalence")
        if row.get("archive_route") != "metadata_only" and (
            "current_release_unpinned" in str(row.get("release")) or "mixed_unpinned" in str(row.get("release"))
        ):
            errors.append(f"{row.get('source_id')}: public archive route requires an exact release")
    atc = next((row for row in sources if isinstance(row, dict) and row.get("source_id") == "who-atc-ddd"), {})
    if atc.get("archive_route") != "metadata_only" or atc.get("languages") != ["en", "es"]:
        errors.append("WHO ATC/DDD must remain metadata-only with exact documented English and Spanish editions")
    pro = next((row for row in sources if isinstance(row, dict) and row.get("source_id") == "pro-ctcae"), {})
    if pro.get("archive_route") != "metadata_only" or "Twi" not in str(pro.get("notes")):
        errors.append("PRO-CTCAE must remain metadata-only and preserve the unresolved Twi boundary")
    if catalog.get("controls") != {
        "payload_retrieval_authorized": False,
        "remote_upload_authorized": False,
        "empirical_execution_authorized": False,
        "direct_lexical_vote_allowed": False,
        "automatic_promotion_allowed": False,
        "new_freeze_required": True,
    }:
        errors.append("orthogonal source controls must remain fail-closed")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(load_json(CATALOG_PATH), load_json(SCHEMA_PATH))
    if errors:
        print("Orthogonal biomedical source validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Orthogonal biomedical source validation passed (17 sources; 9 analyses; zero payload authorization).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
