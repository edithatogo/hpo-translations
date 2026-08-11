import copy
import unittest

from scripts.validate_open_mapping_rights import (
    MATRIX_PATH,
    SCHEMA_PATH,
    SOURCE_CATALOG_PATH,
    load_json,
    validation_errors,
)


class OpenMappingRightsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.matrix = load_json(MATRIX_PATH)
        self.schema = load_json(SCHEMA_PATH)
        self.source_catalog = load_json(SOURCE_CATALOG_PATH)

    def errors(self, matrix: dict) -> list[str]:
        return validation_errors(matrix, self.schema, self.source_catalog)

    def test_committed_matrix_passes(self) -> None:
        self.assertEqual(self.errors(self.matrix), [])

    def test_payload_inclusion_fails_closed(self) -> None:
        mutated = copy.deepcopy(self.matrix)
        mutated["families"][0]["files"][0]["payload_included"] = True
        self.assertIn("mapping and ontology payloads must remain excluded", self.errors(mutated))

    def test_repository_license_cannot_be_inferred(self) -> None:
        mutated = copy.deepcopy(self.matrix)
        uberon = next(family for family in mutated["families"] if family["family_id"] == "uberon-cl-bridge-families")
        uberon["repository_license_spdx"] = "CC-BY-3.0"
        self.assertIn(
            "uberon-cl-bridge-families repository SPDX status does not match verified metadata",
            self.errors(mutated),
        )

    def test_generated_output_requires_duplication_lineage(self) -> None:
        mutated = copy.deepcopy(self.matrix)
        upheno = next(family for family in mutated["families"] if family["family_id"] == "upheno-components")
        generated = next(file for file in upheno["files"] if file["role"] == "generated_output")
        generated["generates_or_duplicates"] = []
        self.assertTrue(any("generated output lacks" in error for error in self.errors(mutated)))

    def test_pato_import_cannot_inherit_repository_license(self) -> None:
        mutated = copy.deepcopy(self.matrix)
        pato = next(family for family in mutated["families"] if family["family_id"] == "pato-qudt-and-imports")
        imported = next(file for file in pato["files"] if file["role"] == "import_snapshot")
        imported["declared_license"] = "BSD-3-Clause"
        self.assertIn(
            "PATO import snapshots must not inherit the repository licence without source-level proof",
            self.errors(mutated),
        )

    def test_mhmi_per_file_license_drift_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.matrix)
        mhmi = next(family for family in mutated["families"] if family["family_id"] == "mhmi-manual-mp-hp")
        mhmi["files"][0]["declared_license"] = "CC-BY-4.0"
        self.assertIn(
            "MHMI per-file licences must exactly match the canonical source catalog",
            self.errors(mutated),
        )


if __name__ == "__main__":
    unittest.main()
