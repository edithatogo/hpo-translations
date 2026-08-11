import json
import unittest
from pathlib import Path

INVENTORY = Path("conductor/tracks/meddra_integration_20260623/release_language_inventory_v29_0.json")


class MeddraReleaseInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))

    def test_exact_v29_language_set(self) -> None:
        rows = self.inventory["languages"]
        expected = {
            "ar",
            "pt-BR",
            "zh",
            "hr",
            "cs",
            "da",
            "nl",
            "en",
            "et",
            "fi",
            "fr",
            "de",
            "el",
            "hu",
            "is",
            "it",
            "ja",
            "ko",
            "lv",
            "lt",
            "no",
            "pl",
            "pt",
            "ru",
            "sk",
            "sl",
            "es",
            "sv",
        }
        self.assertEqual(self.inventory["available_language_count"], 28)
        self.assertEqual(len(rows), 28)
        self.assertEqual({row["bcp47"] for row in rows}, expected)

    def test_variants_and_turkish_exclusion(self) -> None:
        rows = {row["bcp47"]: row for row in self.inventory["languages"]}
        self.assertEqual(rows["pt-BR"]["name"], "Brazilian Portuguese")
        self.assertEqual(rows["pt"]["region_status"], "not_distinguished_by_public_evidence")
        self.assertNotIn("tr", rows)
        self.assertEqual(self.inventory["non_current_observations"][0]["bcp47"], "tr")

    def test_payload_is_excluded(self) -> None:
        self.assertTrue(all(value is False for value in self.inventory["payload_policy"].values()))


if __name__ == "__main__":
    unittest.main()
