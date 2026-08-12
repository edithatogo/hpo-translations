import copy
import unittest

from scripts.validate_registry_source_expansion import CATALOG_PATH, SCHEMA_PATH, load_json, validation_errors


class RegistrySourceExpansionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = load_json(CATALOG_PATH)
        self.schema = load_json(SCHEMA_PATH)

    def errors(self, catalog: dict) -> list[str]:
        return validation_errors(catalog, self.schema)

    def test_committed_catalog_passes(self) -> None:
        self.assertEqual(self.errors(self.catalog), [])

    def test_registry_duplication_cannot_expand_inventory(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["registry_policy"]["discovery_registries"].append(
            copy.deepcopy(mutated["registry_policy"]["discovery_registries"][0])
        )
        self.assertIn(
            "discovery registry set must exactly match the governed seven-registry inventory", self.errors(mutated)
        )

    def test_direct_lexical_vote_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["sources"][0]["direct_lexical_vote"] = True
        self.assertIn("maxo: direct lexical vote must remain false", self.errors(mutated))

    def test_language_neutral_schema_cannot_claim_language(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        next(row for row in mutated["sources"] if row["source_id"] == "ga4gh-phenopackets")["languages"] = ["en"]
        self.assertIn(
            "ga4gh-phenopackets: language-neutral schema cannot claim language coverage", self.errors(mutated)
        )

    def test_remote_or_payload_authority_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["controls"]["upstream_mutation_authorized"] = True
        self.assertIn("registry expansion controls must remain fail-closed", self.errors(mutated))

    def test_unknown_study_source_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["planned_studies"][0]["sources"].append("invented")
        self.assertIn("planned study references unknown sources", self.errors(mutated))


if __name__ == "__main__":
    unittest.main()
