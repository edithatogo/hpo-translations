import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "conductor/tracks/snomed_ct_integration_20260623/national_edition_inventory.json"


class SnomedNationalInventoryTests(unittest.TestCase):
    def test_national_translation_inventory_is_variant_specific_and_payload_free(self) -> None:
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        profiles = {row["jurisdiction"]: row for row in inventory["translation_profiles"]}
        canada = profiles["Canada"]
        self.assertEqual(canada["edition_uri"], "http://snomed.info/sct/20611000087101")
        self.assertEqual(canada["language_refsets"]["en-CA"], "19491000087109")
        self.assertEqual(canada["language_refsets"]["fr-CA"], "20581000087109")
        languages = {code for row in profiles.values() for code in row["languages"]}
        self.assertTrue({"fr-BE", "fr-CA", "fr-FR", "lt-LT", "mi-NZ", "nb-NO", "nn-NO"} <= languages)
        self.assertNotIn("no", languages)
        self.assertIs(inventory["payload_incorporated"], False)
        self.assertIn("effectiveTime and RF2 package identity", inventory["admission_requirements"])


if __name__ == "__main__":
    unittest.main()
