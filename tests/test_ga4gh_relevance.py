import copy
import unittest

from scripts.validate_ga4gh_relevance import CATALOG, SCHEMA, load, validation_errors


class Ga4ghRelevanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load(CATALOG)
        cls.schema = load(SCHEMA)

    def errors(self, value: dict[str, object]) -> list[str]:
        return validation_errors(value, self.schema)

    def test_committed_catalog_passes(self) -> None:
        self.assertEqual([], self.errors(self.catalog))

    def test_developmental_product_is_retained(self) -> None:
        ids = {row["product_id"] for row in self.catalog["products"]}
        self.assertTrue({"pedigree", "human-exposome", "sequence-annotation"} <= ids)

    def test_missing_mapping_path_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["products"][0]["mapping_paths"] = []
        self.assertTrue(any("mapping" in error for error in self.errors(mutated)))

    def test_payload_authority_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["products"][0]["payload_authorized"] = True
        self.assertTrue(any("payload" in error for error in self.errors(mutated)))

    def test_maturity_exclusion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["controls"]["maturity_exclusion_allowed"] = True
        self.assertIn("GA4GH controls must remain relevance-first and fail-closed", self.errors(mutated))


if __name__ == "__main__":
    unittest.main()
