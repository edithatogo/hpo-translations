import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "research_validation" / "open_mapping_rights_matrix.json"
SCHEMA_PATH = ROOT / "research_validation" / "open_mapping_rights_matrix.schema.json"
SOURCE_CATALOG_PATH = ROOT / "research_validation" / "source_catalog.json"

EXPECTED_FAMILY_LICENSES = {
    "upheno-components": "CC0-1.0",
    "pato-qudt-and-imports": "BSD-3-Clause",
    "mp-hp-mapping-files": "CC-BY-4.0",
    "mhmi-manual-mp-hp": None,
    "uberon-cl-bridge-families": None,
    "cell-ontology-uberon-bridge": "CC-BY-4.0",
}
EXPECTED_REQUIRED_PATHS = {
    "src/mapping/upheno-cross-species.sssom.tsv",
    "src/mapping/upheno-species-independent-manual.sssom.tsv",
    "src/mappings/pato-to-qudt-quantitykind.sssom.tsv",
    "mappings/MP_HP_upper_level_SSSOM.tsv",
    "mappings/MGI_COVIDSymptom_MP_HPO_3way.tsv",
    "src/ontology/bridge/uberon-bridge-to-ncit.owl",
    "src/ontology/bridge/uberon-bridge-to-sctid.owl",
    "src/ontology/bridge/cl-bridge-to-ncit.owl",
    "src/ontology/bridge/cl-bridge-to-sctid.owl",
    "src/ontology/bridge/cl-bridge-to-uberon.owl",
}


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(matrix: dict[str, Any], schema: dict[str, Any], source_catalog: dict[str, Any]) -> list[str]:
    validator = cast(Any, Draft202012Validator(schema, format_checker=FormatChecker()))
    errors = [error.message for error in validator.iter_errors(matrix)]
    families = cast(list[dict[str, Any]], matrix.get("families", []))
    family_ids = [family.get("family_id") for family in families]
    if set(family_ids) != set(EXPECTED_FAMILY_LICENSES) or len(family_ids) != len(set(family_ids)):
        errors.append("rights matrix must contain each prespecified mapping family exactly once")

    all_files: list[dict[str, Any]] = []
    all_paths: list[str] = []
    for family in families:
        family_id = str(family.get("family_id"))
        if family.get("repository_license_spdx") != EXPECTED_FAMILY_LICENSES.get(family_id):
            errors.append(f"{family_id} repository SPDX status does not match verified metadata")
        files = cast(list[dict[str, Any]], family.get("files", []))
        paths = [str(file.get("path")) for file in files]
        if len(paths) != len(set(paths)):
            errors.append(f"{family_id} contains duplicate file paths")
        all_files.extend(files)
        all_paths.extend(paths)
    missing_paths = EXPECTED_REQUIRED_PATHS - set(all_paths)
    if missing_paths:
        errors.append(f"required mapping or bridge files are missing: {sorted(missing_paths)}")

    if any(file.get("payload_included") is not False for file in all_files):
        errors.append("mapping and ontology payloads must remain excluded")
    if any(file.get("restricted_target_included") is not False for file in all_files):
        errors.append("restricted target content must remain excluded")
    if any(file.get("target_source_review_required") is not True for file in all_files):
        errors.append("every mapping file must retain target-source rights review")
    for file in all_files:
        if file.get("role") == "generated_output" and not file.get("generates_or_duplicates"):
            errors.append(f"generated output lacks source or duplication lineage: {file.get('path')}")
        namespaces = set(cast(list[str], file.get("target_namespaces", [])))
        if namespaces & {"NCIT", "SCTID"} and file.get("restricted_target_included") is not False:
            errors.append(f"restricted target bridge is not payload-safe: {file.get('path')}")

    pato = next(
        (family for family in families if family.get("family_id") == "pato-qudt-and-imports"),
        cast(dict[str, Any], {}),
    )
    pato_files = cast(list[dict[str, Any]], pato.get("files", []))
    pato_map = next(
        (file for file in pato_files if file.get("path") == "src/mappings/pato-to-qudt-quantitykind.sssom.tsv"),
        cast(dict[str, Any], {}),
    )
    if (
        "QUDTQK" not in pato_map.get("target_namespaces", [])
        or pato_map.get("target_source_review_required") is not True
    ):
        errors.append("PATO-QUDT mapping must retain separate QUDT target-source review")
    if any(file.get("role") == "import_snapshot" and file.get("declared_license") is not None for file in pato_files):
        errors.append("PATO import snapshots must not inherit the repository licence without source-level proof")

    source_records = cast(list[dict[str, Any]], source_catalog.get("mappings", []))
    source_mappings = {
        source_id: item for item in source_records if isinstance(source_id := item.get("source_id"), str)
    }
    canonical = source_mappings.get("hpo-hp-mp-manual-collection", cast(dict[str, Any], {}))
    canonical_member_records = cast(list[dict[str, Any]], canonical.get("members", []))
    canonical_members: dict[str, Any] = {
        f"mappings/{member.get('name')}": member.get("declared_license") for member in canonical_member_records
    }
    mhmi = next(
        (family for family in families if family.get("family_id") == "mhmi-manual-mp-hp"),
        cast(dict[str, Any], {}),
    )
    mhmi_files = cast(list[dict[str, Any]], mhmi.get("files", []))
    matrix_members: dict[Any, Any] = {file.get("path"): file.get("declared_license") for file in mhmi_files}
    if matrix_members != canonical_members:
        errors.append("MHMI per-file licences must exactly match the canonical source catalog")

    if matrix.get("payload_files_retrieved") != 0 or matrix.get("mapping_rows_committed") != 0:
        errors.append("rights matrix must remain metadata-only")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(load_json(MATRIX_PATH), load_json(SCHEMA_PATH), load_json(SOURCE_CATALOG_PATH))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Open mapping rights matrix validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
