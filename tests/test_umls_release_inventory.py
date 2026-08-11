import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "conductor/tracks/umls_metathesaurus_integration_20260623/release_inventory_2026aa.json"


class UmlsReleaseInventoryTests(unittest.TestCase):
    def test_current_public_metadata_inventory_is_complete_and_payload_free(self) -> None:
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        languages = inventory["languages"]
        self.assertEqual(inventory["release"], "2026AA")
        self.assertEqual(inventory["release_date"], "2026-05-04")
        self.assertEqual(inventory["language_count"], 31)
        self.assertEqual(len(languages), 31)
        self.assertEqual(len({row["umls_code"] for row in languages}), 31)
        self.assertEqual(len({row["bcp47"] for row in languages}), 31)
        self.assertIn("fr-CA", inventory["regional_loinc_2_82_editions"])
        self.assertEqual(inventory["canadian_french_source"]["source_version"], "LNC-FR-CA_282")
        self.assertIs(inventory["payload_policy"]["payload_incorporated"], False)
        serialized = json.dumps(inventory)
        for forbidden in ("CUI:", "AUI:", "api_key", "access_token"):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
