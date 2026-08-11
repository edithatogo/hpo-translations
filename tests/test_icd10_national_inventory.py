import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "conductor/tracks/icd10_integration_20260623/national_variant_inventory.json"


class Icd10NationalInventoryTests(unittest.TestCase):
    def test_variants_and_canadian_bilingual_map_are_explicit_and_payload_free(self) -> None:
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        profiles = {row["profile_id"]: row for row in inventory["variant_profiles"]}
        required = {
            "who_icd10_2019",
            "icd10cm_us_2026",
            "icd10pcs_us_2026",
            "icd10ca_ca_2022",
            "icd10am_au_13",
            "icd10gm_de_2026",
            "cim10fr_fr_2025",
            "cie10es_es_2026",
            "icd10_uk_5e_2025",
        }
        self.assertEqual(set(profiles), required)
        self.assertEqual(profiles["icd10ca_ca_2022"]["languages"], ["en-CA", "fr-CA"])
        canadian_map = next(row for row in inventory["mapping_profiles"] if row["map_id"].startswith("snomedctca"))
        self.assertEqual(canadian_map["languages"], ["en-CA", "fr-CA"])
        self.assertIn("not every", canadian_map["coverage_caveat"])
        self.assertIs(inventory["payload_incorporated"], False)
        self.assertIs(inventory["hpo_mapping_policy"]["direct_official_hpo_icd10_map_found"], False)


if __name__ == "__main__":
    unittest.main()
