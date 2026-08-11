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
            {
                "not_identified",
                "candidate_identified_authorization_pending",
                "authorized_local_only",
                "authorized_private_archive_partial",
            },
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
            "created_private_owner_only",
        )
        self.assertTrue(inventory["candidate_hosting"]["source_archiving_authorization"])
        archived = [source for source in inventory["sources"] if source["status"] == "archived_private"]
        self.assertEqual(
            {source["source_id"] for source in archived},
            {"do", "loinc", "mesh", "mp", "orphanet", "pato", "upheno"},
        )
        self.assertTrue(inventory["candidate_hosting"]["required_before_upload"])

    def test_archive_workflow_requires_manual_dispatch(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow_path = root / ".github" / "workflows" / "governed-multilingual-archive.yml"
        workflow = workflow_path.read_text(encoding="utf-8")
        self.assertIn("\n  workflow_dispatch:", workflow)
        self.assertNotIn("\n  push:", workflow)
        self.assertFalse((workflow_path.parent / "private-multilingual-archive.yml").exists())


if __name__ == "__main__":
    unittest.main()
