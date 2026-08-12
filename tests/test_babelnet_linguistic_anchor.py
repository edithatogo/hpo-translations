import copy
import unittest

from scripts.validate_babelnet_linguistic_anchor import PLAN_PATH, SCHEMA_PATH, load_json, validation_errors


class BabelNetLinguisticAnchorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = load_json(PLAN_PATH)
        self.schema = load_json(SCHEMA_PATH)

    def test_committed_plan_passes(self) -> None:
        self.assertEqual(validation_errors(self.plan, self.schema), [])

    def test_full_scan_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["trigger_policy"]["run_on_every_term"] = True
        self.assertTrue(validation_errors(plan, self.schema))

    def test_generic_portuguese_cannot_prove_variant(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["regional_language_policy"]["generic_pt_proves_variant"] = True
        self.assertTrue(validation_errors(plan, self.schema))

    def test_empirical_execution_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["controls"]["empirical_execution_authorized"] = True
        self.assertTrue(validation_errors(plan, self.schema))

    def test_health_domain_cannot_be_the_only_gate(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["sense_selection"]["health_domain_is_feature_not_gate"] = False
        self.assertTrue(validation_errors(plan, self.schema))


if __name__ == "__main__":
    unittest.main()
