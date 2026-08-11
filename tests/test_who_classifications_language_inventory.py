import json
import unittest
from pathlib import Path

INVENTORY = Path("conductor/tracks/icd11_integration_20260623/who_classifications_language_inventory_2026_01.json")


class WhoClassificationsLanguageInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        cls.products = {row["product_id"]: row for row in cls.inventory["products"]}

    def test_release_products_and_exact_language_sets(self) -> None:
        self.assertEqual(self.inventory["release_id"], "2026-01")
        self.assertEqual(set(self.products), {"icd11-mms", "icf"})
        expected = {
            "icd11-mms": {"ar", "zh", "cs", "en", "fr", "de", "kk", "la", "pt", "ru", "sk", "es", "sv", "tr", "uz"},
            "icf": {"hy", "zh", "cs", "en", "et", "fi", "fr", "it", "mn", "pt", "ru", "sk", "es", "tr", "uk"},
        }
        for product_id, codes in expected.items():
            rows = self.products[product_id]["languages"]
            self.assertEqual(self.products[product_id]["language_count"], 15)
            self.assertEqual(len(rows), 15)
            self.assertEqual({row["bcp47"] for row in rows}, codes)

    def test_icd11_limitations_are_machine_readable(self) -> None:
        rows = {row["bcp47"]: row for row in self.products["icd11-mms"]["languages"]}
        self.assertEqual(rows["de"]["availability_status"], "prerelease")
        self.assertEqual(rows["la"]["availability_status"], "titles_only")
        self.assertEqual(rows["zh"]["script_status"], "not_distinguished_by_authority_matrix")
        self.assertEqual(rows["pt"]["region_status"], "not_distinguished_by_authority_matrix")
        self.assertEqual(rows["es"]["region_status"], "not_distinguished_by_authority_matrix")

    def test_icf_is_distinct_and_all_listed_languages_are_available(self) -> None:
        rows = self.products["icf"]["languages"]
        self.assertTrue(all(row["availability_status"] == "available" for row in rows))
        self.assertNotEqual(
            {row["bcp47"] for row in rows},
            {row["bcp47"] for row in self.products["icd11-mms"]["languages"]},
        )

    def test_inventory_contains_no_payload_or_implicit_mapping_authority(self) -> None:
        policy = self.inventory["payload_policy"]
        for field in (
            "payload_incorporated",
            "api_payload_retrieved",
            "labels_or_definitions_included",
            "mapping_rows_included",
            "credentials_used",
            "adaptation_or_crosswalk_authorized",
        ):
            self.assertFalse(policy[field])
        self.assertEqual(self.inventory["scope"], "public_metadata_only")


if __name__ == "__main__":
    unittest.main()
