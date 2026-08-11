import copy
import unittest

from scripts.validate_language_readiness import (
    CATALOG_PATH,
    ICD10_PATH,
    ROOT,
    SCHEMA_PATH,
    SNOMED_PATH,
    SUPPLEMENTARY_PATH,
    UMLS_PATH,
    load_json,
    validation_errors,
)


class LanguageReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = load_json(CATALOG_PATH)
        self.schema = load_json(SCHEMA_PATH)
        self.supplementary = load_json(SUPPLEMENTARY_PATH)
        self.umls = load_json(UMLS_PATH)
        self.snomed = load_json(SNOMED_PATH)
        self.icd10 = load_json(ICD10_PATH)

    def errors(self, catalog: dict) -> list[str]:
        return validation_errors(
            catalog,
            self.schema,
            self.supplementary,
            self.umls,
            self.snomed,
            self.icd10,
            ROOT / "babelon",
        )

    def test_committed_catalog_passes(self) -> None:
        self.assertEqual(self.errors(self.catalog), [])

    def test_translation_rows_fail_closed(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["translation_rows_added"] = 1
        self.assertTrue(self.errors(mutated))

    def test_candidate_set_drift_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["hpo_candidate_languages"].pop()
        self.assertIn(
            "HPO metadata candidate languages must be exactly ko, pl, ru, sv, and uk",
            self.errors(mutated),
        )

    def test_unverified_regional_context_cannot_claim_confirmation(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["pro_ctcae"]["validated_translations"] = [
            item for item in mutated["pro_ctcae"]["validated_translations"] if item["language_tag"] != "pt-PT"
        ]
        self.assertIn(
            "confirmed regional context is absent from validated inventories: pt-PT",
            self.errors(mutated),
        )

    def test_decs_permission_cannot_be_opened(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["decs"]["payload_retrieval_allowed"] = True
        self.assertTrue(self.errors(mutated))

    def test_pro_ctcae_authority_table_drift_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["pro_ctcae"]["validated_translations"][0]["authority_name"] = "Invented"
        self.assertIn(
            "PRO-CTCAE validated translation names must exactly match the 2026-08-11 authority table",
            self.errors(mutated),
        )

    def test_twi_cannot_resolve_repository_profile(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        twi = next(item for item in mutated["pro_ctcae"]["validated_translations"] if item["authority_name"] == "Twi")
        twi["repository_profile_linkage"] = "resolved"
        self.assertIn(
            "PRO-CTCAE Twi must remain unlinked from the unresolved repository tw profile",
            self.errors(mutated),
        )

    def test_development_modules_cannot_be_combined(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        development = mutated["pro_ctcae"]["in_development"]
        development["pro_ctcae"].append(development["ped_pro_ctcae_separate_module"].pop())
        errors = self.errors(mutated)
        self.assertIn(
            "PRO-CTCAE in-development metadata must exactly match the 2026-08-11 authority list",
            errors,
        )
        self.assertIn("Ped-PRO-CTCAE in-development metadata must remain exact and separate", errors)


if __name__ == "__main__":
    unittest.main()
