import copy
import unittest

from scripts.validate_terminology_inventories import INVENTORIES, load_json, validation_errors


class TerminologyInventoryValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.umls = load_json(INVENTORIES["umls"])
        self.snomed = load_json(INVENTORIES["snomed"])
        self.icd10 = load_json(INVENTORIES["icd10"])

    def errors(self, umls: dict | None = None, snomed: dict | None = None, icd10: dict | None = None) -> list[str]:
        return validation_errors(umls or self.umls, snomed or self.snomed, icd10 or self.icd10)

    def test_committed_inventories_pass(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_payload_flags_fail_closed_in_all_shapes(self) -> None:
        umls = copy.deepcopy(self.umls)
        umls["payload_policy"]["payload_incorporated"] = True
        self.assertTrue(self.errors(umls=umls))
        snomed = copy.deepcopy(self.snomed)
        snomed["payload_incorporated"] = True
        self.assertTrue(self.errors(snomed=snomed))
        icd10 = copy.deepcopy(self.icd10)
        icd10["payload_incorporated"] = True
        self.assertTrue(self.errors(icd10=icd10))

    def test_duplicate_ids_and_bad_language_are_rejected(self) -> None:
        umls = copy.deepcopy(self.umls)
        umls["languages"][1]["umls_code"] = umls["languages"][0]["umls_code"]
        self.assertTrue(any("duplicate umls_code" in error for error in self.errors(umls=umls)))
        snomed = copy.deepcopy(self.snomed)
        snomed["translation_profiles"][1]["jurisdiction"] = snomed["translation_profiles"][0]["jurisdiction"]
        self.assertTrue(any("duplicate jurisdiction" in error for error in self.errors(snomed=snomed)))
        icd10 = copy.deepcopy(self.icd10)
        icd10["variant_profiles"][0]["languages"] = ["fr_CA"]
        self.assertTrue(any("invalid BCP-47" in error for error in self.errors(icd10=icd10)))

    def test_unresolved_release_and_edition_require_explicit_status(self) -> None:
        snomed = copy.deepcopy(self.snomed)
        france = next(row for row in snomed["translation_profiles"] if row["jurisdiction"] == "France")
        france.pop("authority_status")
        self.assertTrue(any("null edition_uri" in error for error in self.errors(snomed=snomed)))
        icd10 = copy.deepcopy(self.icd10)
        uk_map = next(row for row in icd10["mapping_profiles"] if row["map_id"] == "uk_snomedct_to_icd10")
        uk_map.pop("release_status")
        self.assertTrue(any("release identity" in error for error in self.errors(icd10=icd10)))

    def test_canadian_cross_inventory_contract_is_enforced(self) -> None:
        umls = copy.deepcopy(self.umls)
        umls["regional_loinc_2_82_editions"].remove("fr-CA")
        self.assertTrue(any("UMLS Canadian French" in error for error in self.errors(umls=umls)))
        snomed = copy.deepcopy(self.snomed)
        canada = next(row for row in snomed["translation_profiles"] if row["jurisdiction"] == "Canada")
        canada["language_refsets"].pop("fr-CA")
        self.assertTrue(any("refset keys" in error for error in self.errors(snomed=snomed)))
        icd10 = copy.deepcopy(self.icd10)
        ca_map = next(row for row in icd10["mapping_profiles"] if row["map_id"].startswith("snomedctca"))
        ca_map["direction"] = "ambiguous mapping"
        self.assertTrue(any("map direction" in error for error in self.errors(icd10=icd10)))

    def test_secret_keys_and_blank_licence_are_rejected(self) -> None:
        umls = copy.deepcopy(self.umls)
        umls["api_key"] = "not-a-real-secret"
        self.assertTrue(any("secret-bearing key" in error for error in self.errors(umls=umls)))
        icd10 = copy.deepcopy(self.icd10)
        icd10["variant_profiles"][0]["licence_gate"] = ""
        self.assertTrue(any("licence_gate" in error for error in self.errors(icd10=icd10)))

    def test_semantic_non_independence_guardrails_are_enforced(self) -> None:
        umls = copy.deepcopy(self.umls)
        umls["mapping_policy"]["cui_co_membership"] = "exact independent mapping"
        self.assertTrue(any("CUI co-membership" in error for error in self.errors(umls=umls)))
        icd10 = copy.deepcopy(self.icd10)
        icd10["hpo_mapping_policy"]["direct_official_hpo_icd10_map_found"] = True
        self.assertTrue(any("direct official" in error for error in self.errors(icd10=icd10)))


if __name__ == "__main__":
    unittest.main()
