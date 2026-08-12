import copy
import unittest

from scripts.validate_stage1_preflight import PREFLIGHT, SCHEMA, load, validation_errors


class Stage1PreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preflight = load(PREFLIGHT)
        self.schema = load(SCHEMA)

    def errors(self, value: dict) -> list[str]:
        return validation_errors(value, self.schema)

    def test_committed_preflight_passes(self) -> None:
        self.assertEqual(self.errors(self.preflight), [])

    def test_sample_cannot_drift(self) -> None:
        value = copy.deepcopy(self.preflight)
        value["stage_1_hpo_ids"].pop()
        self.assertIn("preflight HPO IDs must match the frozen Stage 1 sample", self.errors(value))

    def test_candidate_count_cannot_drift(self) -> None:
        value = copy.deepcopy(self.preflight)
        value["candidate_row_count"] = 47
        self.assertIn("preflight candidate counts must match the frozen conditions", self.errors(value))

    def test_panel_cannot_drift(self) -> None:
        value = copy.deepcopy(self.preflight)
        value["specialist_roles"].pop()
        self.assertIn("preflight panel must match the frozen agent instrument", self.errors(value))

    def test_execution_cannot_be_claimed(self) -> None:
        value = copy.deepcopy(self.preflight)
        value["execution_started"] = True
        self.assertTrue(self.errors(value))


if __name__ == "__main__":
    unittest.main()
