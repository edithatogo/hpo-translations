import copy
import unittest

from scripts.validate_spanish_japanese_use_approval import PAYLOAD, RECEIPT, SCHEMA, load, validation_errors


class SpanishJapaneseUseApprovalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.receipt = load(RECEIPT)
        self.schema = load(SCHEMA)
        self.payload = load(PAYLOAD)

    def errors(self, receipt: dict) -> list[str]:
        return validation_errors(receipt, self.schema, self.payload)

    def test_committed_receipt_passes(self) -> None:
        self.assertEqual(self.errors(self.receipt), [])

    def test_language_scope_cannot_expand(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["languages"].append("fr")
        self.assertTrue(self.errors(receipt))

    def test_payload_binding_cannot_drift(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["source_snapshots"].pop()
        self.assertIn("approval must bind the exact two frozen payload source IDs", self.errors(receipt))

    def test_ethics_gate_cannot_be_bypassed(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["empirical_execution_authorized"] = True
        self.assertTrue(self.errors(receipt))

    def test_upstream_boundary_is_required(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["study_conditions"].remove("no_upstream_write")
        self.assertIn("approval must preserve upstream-write and validation-claim boundaries", self.errors(receipt))


if __name__ == "__main__":
    unittest.main()
