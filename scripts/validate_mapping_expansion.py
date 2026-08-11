import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "research_validation" / "mapping_expansion_catalog.json"
SCHEMA_PATH = ROOT / "research_validation" / "mapping_expansion_catalog.schema.json"
SOURCE_REGISTRY_PATH = ROOT / "ontology_network" / "source_registry.json"


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(catalog: dict[str, Any], schema: dict[str, Any], source_registry: dict[str, Any]) -> list[str]:
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
    for item in coverage:
        if not isinstance(item, dict):
            continue
        unknown = set(item.get("artifact_ids", [])) - known_artifacts
        if unknown:
            errors.append(f"{item.get('source_id')} references unknown artifacts: {sorted(unknown)}")

    if any(item.get("payload_commit_allowed") is not False for item in catalog.get("artifacts", [])):
        errors.append("every mapping artifact must remain payload-commit blocked")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(load_json(CATALOG_PATH), load_json(SCHEMA_PATH), load_json(SOURCE_REGISTRY_PATH))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Mapping expansion catalog validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
