import copy
import unittest

from scripts.validate_translation_source_utilisation import (
    ASSIGNMENTS_PATH,
    LEARNING_LOOP_PATH,
    MODEL_TIER_PATH,
    PLAN_PATH,
    ROOT,
    ROUTES_PATH,
    SAP_PATH,
    SCHEMA_PATH,
    load_json,
    validation_errors,
)


class TranslationSourceUtilisationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = load_json(PLAN_PATH)
        self.schema = load_json(SCHEMA_PATH)
        self.routes = load_json(ROUTES_PATH)
        self.assignments = load_json(ASSIGNMENTS_PATH)
        self.sap = load_json(SAP_PATH)
        self.model_tiers = load_json(MODEL_TIER_PATH)
        self.learning_loop = load_json(LEARNING_LOOP_PATH)

    def errors(self, plan: dict) -> list[str]:
        return validation_errors(
            plan, self.schema, self.routes, self.assignments, self.sap, self.model_tiers, self.learning_loop, ROOT
        )

    def test_source_assignments_cover_exact_matrix(self) -> None:
        mutated = copy.deepcopy(self.assignments)
        mutated["assignments"].pop()
        self.assertIn(
            "source assignment matrix must contain exactly 15 governed assignments",
            validation_errors(
                self.plan, self.schema, self.routes, mutated, self.sap, self.model_tiers, self.learning_loop, ROOT
            ),
        )

    def test_unknown_assignment_assertion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.assignments)
        mutated["assignments"][4]["assertions"].append("invented")
        self.assertIn(
            "unknown source-assignment assertion: invented",
            validation_errors(
                self.plan, self.schema, self.routes, mutated, self.sap, self.model_tiers, self.learning_loop, ROOT
            ),
        )

    def test_statistical_plan_requires_active_learning_analysis(self) -> None:
        mutated = copy.deepcopy(self.sap)
        mutated["analyses"].pop()
        self.assertIn(
            "statistical analysis plan must bind A1 through A10 in order",
            validation_errors(
                self.plan,
                self.schema,
                self.routes,
                self.assignments,
                mutated,
                self.model_tiers,
                self.learning_loop,
                ROOT,
            ),
        )

    def test_all_four_model_tiers_are_required(self) -> None:
        mutated = copy.deepcopy(self.model_tiers)
        mutated["tier_definition"]["tiers"].pop()
        self.assertIn(
            "model tiers must remain ordered tiny, small, medium, large",
            validation_errors(
                self.plan, self.schema, self.routes, self.assignments, self.sap, mutated, self.learning_loop, ROOT
            ),
        )

    def test_existing_translation_reference_cannot_generate(self) -> None:
        mutated = copy.deepcopy(self.model_tiers)
        mutated["evidence_arms"][-1]["generation_allowed"] = True
        self.assertIn(
            "existing HPO translations must remain non-generative and withheld until candidate lock",
            validation_errors(
                self.plan, self.schema, self.routes, self.assignments, self.sap, mutated, self.learning_loop, ROOT
            ),
        )

    def test_model_tier_plan_requires_new_freeze(self) -> None:
        mutated = copy.deepcopy(self.model_tiers)
        mutated["controls"]["new_freeze_required"] = False
        self.assertIn(
            "model tier execution must require a new prospective freeze",
            validation_errors(
                self.plan, self.schema, self.routes, self.assignments, self.sap, mutated, self.learning_loop, ROOT
            ),
        )

    def test_complete_tier_by_evidence_factorial_is_required(self) -> None:
        mutated = copy.deepcopy(self.model_tiers)
        mutated["cell_manifest"].pop()
        self.assertIn(
            "model tier plan must contain the complete ordered 12-cell factorial",
            validation_errors(
                self.plan, self.schema, self.routes, self.assignments, self.sap, mutated, self.learning_loop, ROOT
            ),
        )

    def test_committed_plan_passes(self) -> None:
        self.assertEqual(self.errors(self.plan), [])

    def test_empirical_scope_cannot_change_without_new_contract(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["current_study_scope"]["languages"].append("fr")
        self.assertTrue(self.errors(mutated))

    def test_tw_cannot_be_admitted(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["current_study_scope"]["excluded_profile"] = "none"
        self.assertTrue(self.errors(mutated))

    def test_automatic_promotion_fails_closed(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["controls"]["automatic_promotion_allowed"] = True
        self.assertTrue(self.errors(mutated))

    def test_agent_panel_cannot_grant_accountable_authority(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["controls"]["agent_panel_can_grant_rights_or_community_or_ethics_authority"] = True
        self.assertTrue(self.errors(mutated))

    def test_source_roles_cannot_silently_disappear(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["source_role_classes"].pop()
        self.assertTrue(self.errors(mutated))

    def test_analysis_set_cannot_silently_drift(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["analyses"].pop()
        self.assertTrue(self.errors(mutated))

    def test_canonical_input_must_exist(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["canonical_inputs"].append("research_validation/invented.json")
        self.assertIn(
            "canonical input does not exist: research_validation/invented.json",
            self.errors(mutated),
        )


if __name__ == "__main__":
    unittest.main()
