import copy
import unittest

from scripts.validate_orphadata_inventory import INVENTORY, SCHEMA, load_json, validation_errors


class OrphadataProductLanguageInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inventory = load_json(INVENTORY)
        self.schema = load_json(SCHEMA)

    def errors(self, inventory: dict) -> list[str]:
        return validation_errors(inventory, self.schema)

    def test_committed_inventory_passes(self) -> None:
        self.assertEqual(self.errors(self.inventory), [])

    def test_payload_promotion_fails_closed(self) -> None:
        mutated = copy.deepcopy(self.inventory)
        mutated["products"][0]["payload_incorporated"] = True
        self.assertTrue(self.errors(mutated))

    def test_product_language_sets_cannot_be_collapsed(self) -> None:
        mutated = copy.deepcopy(self.inventory)
        phenotype = next(row for row in mutated["products"] if row["product_id"] == "product4-phenotypes-hpo")
        phenotype["languages"].append("pl")
        self.assertTrue(any("exact product language set" in error for error in self.errors(mutated)))

    def test_stale_alignment_vintages_cannot_be_promoted(self) -> None:
        mutated = copy.deepcopy(self.inventory)
        alignments = next(row for row in mutated["products"] if row["product_id"] == "product1-alignments")
        turkish = next(row for row in alignments["language_vintages"] if row["language"] == "tr")
        turkish["vintage_status"] = "current"
        self.assertTrue(any("stale status" in error for error in self.errors(mutated)))


if __name__ == "__main__":
    unittest.main()
