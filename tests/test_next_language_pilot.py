import copy
import unittest

from scripts.validate_next_language_pilot import (
    INVENTORY_PATH,
    PLAN_PATH,
    SCHEMA_PATH,
    load_json,
    validation_errors,
)


class NextLanguagePilotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = load_json(PLAN_PATH)
        self.schema = load_json(SCHEMA_PATH)
        self.inventory = load_json(INVENTORY_PATH)

    def errors(self, plan: dict) -> list[str]:
        return validation_errors(plan, self.schema, self.inventory)

    def test_committed_plan_passes(self) -> None:
        self.assertEqual(self.errors(self.plan), [])

    def test_primary_language_drift_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["primary_next_pilot"]["source_profiles"].reverse()
        self.assertIn("primary next pilot must be exactly French and Czech", self.errors(mutated))

    def test_inventory_hash_drift_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["primary_next_pilot"]["source_profiles"][0]["babelon_blob"] = "0" * 40
        self.assertIn("fr: babelon_blob must match the canonical HPO inventory", self.errors(mutated))

    def test_optional_languages_cannot_be_silently_changed(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["affordability_contingency"]["source_profiles"].reverse()
        self.assertIn("affordability expansion must add exactly Dutch and Turkish", self.errors(mutated))

    def test_new_language_payload_cannot_be_authorized(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["new_language_governance_preparation"][0]["payload_retrieval_authorized"] = True
        self.assertTrue(self.errors(mutated))

    def test_current_freeze_cannot_be_changed(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["controls"]["current_g3_changed"] = True
        self.assertIn("next-language pilot controls must remain fail-closed", self.errors(mutated))


if __name__ == "__main__":
    unittest.main()
