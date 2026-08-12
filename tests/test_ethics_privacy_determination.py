import copy
import unittest

from scripts.validate_ethics_privacy_determination import (
    LANGUAGE_APPROVAL,
    PAYLOAD,
    RECEIPT,
    SCHEMA,
    load,
    validation_errors,
)


class EthicsPrivacyDeterminationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.receipt = load(RECEIPT)
        self.schema = load(SCHEMA)
        self.language_approval = load(LANGUAGE_APPROVAL)
        self.payload = load(PAYLOAD)

    def errors(self, receipt: dict) -> list[str]:
        return validation_errors(receipt, self.schema, self.language_approval, self.payload)

    def test_committed_receipt_passes(self) -> None:
        self.assertEqual(self.errors(self.receipt), [])

    def test_language_scope_cannot_expand(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["scope"]["languages"].append("fr")
        self.assertTrue(self.errors(receipt))

    def test_source_scope_cannot_drift(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["scope"]["source_snapshots"].pop()
        self.assertIn("ethics/privacy scope must bind the exact frozen source snapshots", self.errors(receipt))

    def test_privacy_controls_remain_required(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["privacy_controls_required"] = False
        self.assertIn("a not-required application determination cannot remove privacy controls", self.errors(receipt))

    def test_receipt_cannot_claim_execution_started(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["stage_1_execution_started"] = True
        self.assertIn("the receipt may close the gate but cannot claim Stage 1 has started", self.errors(receipt))

    def test_upstream_boundary_is_required(self) -> None:
        receipt = copy.deepcopy(self.receipt)
        receipt["does_not_authorize"].remove("upstream_write")
        self.assertIn(
            "the receipt must preserve participant, data, promotion, and upstream boundaries", self.errors(receipt)
        )


if __name__ == "__main__":
    unittest.main()
