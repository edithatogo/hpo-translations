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

    def test_approval_packets_are_unsent_and_payload_free(self) -> None:
        path = Path(__file__).resolve().parents[1] / "conductor" / "source_governance_approval_packets.json"
        packets = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(packets["dispatch_status"], "prepared_unsent")
        self.assertIs(packets["external_contact_authorized"], False)
        self.assertIs(packets["payload_terms_included"], False)
        self.assertIs(packets["promotion_authorized"], False)
        for packet in packets["packets"]:
            self.assertEqual(packet["recommended_option"], "A")
            self.assertTrue(packet["approval_questions"])

    def test_private_source_inventory_is_fail_closed(self) -> None:
        path = Path(__file__).resolve().parents[1] / "conductor" / "source_hosting_inventory.json"
        inventory = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn(
            inventory["status"],
            {"not_identified", "candidate_identified_authorization_pending", "authorized_local_only"},
        )
        self.assertIs(inventory["payload_access_allowed"], False)
        self.assertIs(inventory["promotion_allowed"], False)
        self.assertEqual(
            inventory["candidate_hosting"]["status"],
            "platform_authorized_source_scope_pending",
        )
        self.assertEqual(
            inventory["candidate_hosting"]["access_model"],
            "owner-only private repository; no collaborators authorized",
        )
        self.assertEqual(
            inventory["candidate_hosting"]["repository_creation_status"],
            "blocked_insufficient_hf_token_scope",
        )
        self.assertTrue(inventory["candidate_hosting"]["source_archiving_authorization"])
        self.assertTrue(inventory["candidate_hosting"]["required_before_upload"])


if __name__ == "__main__":
    unittest.main()
