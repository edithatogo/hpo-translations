import json
import unittest
from pathlib import Path

from scripts.validate_hpo_language_inventory import validate


class HpoLanguageInventoryTests(unittest.TestCase):
    def test_local_files_and_hashes_match(self) -> None:
        self.assertEqual(validate(), [])

    def test_governance_exclusions_remain_explicit(self) -> None:
        data = json.loads(Path("conductor/hpo_babelon_language_inventory.json").read_text(encoding="utf-8"))
        rows = {row["code"]: row for row in data["profiles"]}
        self.assertEqual(rows["ar"]["babelon_rows"], 0)
        self.assertIn("excluded", rows["tw"]["status"])
        self.assertIn("identity_gate", rows["pt"]["status"])
        self.assertIn("identity_gate", rows["zh"]["status"])
        self.assertEqual({row["code"] for row in data["documentation_only_leads"]}, {"fi", "th"})
        self.assertEqual(data["archaeology_leads"][0]["code"], "hi")


if __name__ == "__main__":
    unittest.main()
