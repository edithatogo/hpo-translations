import json
import unittest
from pathlib import Path

from scripts.validate_source_governance_docket import main


class SourceGovernanceDocketTests(unittest.TestCase):
    def test_docket_validates_without_granting_approval(self) -> None:
        self.assertEqual(main(), 0)

    def test_docket_contains_options_and_contingencies(self) -> None:
        path = Path(__file__).resolve().parents[1] / "conductor" / "source_governance_decision_docket.json"
        docket = json.loads(path.read_text(encoding="utf-8"))
        self.assertIs(docket["policy"]["no_approval_granted"], True)
        self.assertEqual({item["id"] for item in docket["decision_options"]}, {"A", "B", "C"})
        for track in docket["tracks"]:
            self.assertIn(track["recommended_option"], {"A", "B", "C"})
            self.assertTrue(track["authority"]["status"])
            self.assertTrue(track["licence"]["status"])
            self.assertTrue(track["contingency"])
            self.assertTrue(track["maintainer_gate"])


if __name__ == "__main__":
    unittest.main()
