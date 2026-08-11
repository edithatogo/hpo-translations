import json
import unittest
from pathlib import Path

INVENTORY = Path("conductor/tracks/loinc_integration_20260623/regional_language_inventory_2_82.json")


class LoincRegionalInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))

    def test_exact_21_regional_variants(self) -> None:
        rows = self.inventory["regional_variants"]
        expected = {
            "ar-JO",
            "cs-CZ",
            "de-AT",
            "de-DE",
            "el-GR",
            "es-AR",
            "es-ES",
            "es-MX",
            "et-EE",
            "fr-BE",
            "fr-CA",
            "fr-FR",
            "it-IT",
            "ko-KR",
            "nl-NL",
            "pl-PL",
            "pt-BR",
            "ru-RU",
            "tr-TR",
            "uk-UA",
            "zh-CN",
        }
        self.assertEqual(self.inventory["regional_variant_count"], 21)
        self.assertEqual(len(rows), 21)
        self.assertEqual({row["bcp47"] for row in rows}, expected)

    def test_translation_vintage_is_not_package_release(self) -> None:
        rows = {row["bcp47"]: row for row in self.inventory["regional_variants"]}
        self.assertEqual(self.inventory["package_release"], "2.82")
        self.assertEqual(rows["fr-CA"]["last_updated_in_loinc_version"], "2.82")
        self.assertEqual(rows["es-AR"]["last_updated_in_loinc_version"], "2.15")
        self.assertEqual(rows["et-EE"]["last_updated_in_loinc_version"], "2.23")
        self.assertEqual(self.inventory["interpretation"], "package_release_is_not_translation_vintage")

    def test_payload_and_account_actions_are_excluded(self) -> None:
        self.assertTrue(all(value is False for value in self.inventory["payload_policy"].values()))


if __name__ == "__main__":
    unittest.main()
