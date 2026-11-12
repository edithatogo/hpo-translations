import copy
import unittest

from scripts.validate_biomedical_source_preparation import CATALOG, MATRIX, SCHEMA, load, validation_errors


class BiomedicalSourcePreparationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.matrix = load(MATRIX)
        self.schema = load(SCHEMA)
        self.catalog = load(CATALOG)

    def errors(self, matrix: dict) -> list[str]:
        return validation_errors(matrix, self.schema, self.catalog)

    def test_committed_matrix_passes(self) -> None:
        self.assertEqual(self.errors(self.matrix), [])

    def test_component_cannot_disappear(self) -> None:
        mutated = copy.deepcopy(self.matrix)
        mutated["components"].pop()
        self.assertTrue(self.errors(mutated))

    def test_unknown_catalog_source_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.matrix)
        mutated["components"][0]["source_ref"] = "invented"
        self.assertIn("unknown registry source reference: invented", self.errors(mutated))

    def test_component_cannot_be_bound_twice(self) -> None:
        mutated = copy.deepcopy(self.matrix)
        mutated["analysis_bindings"][1]["components"].append("maxo")
        self.assertIn("analysis bindings must cover each component exactly once", self.errors(mutated))

    def test_payload_authority_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.matrix)
        mutated["controls"]["payload_retrieval_authorized"] = True
        self.assertIn("preparation controls must remain fail-closed", self.errors(mutated))


if __name__ == "__main__":
    unittest.main()
