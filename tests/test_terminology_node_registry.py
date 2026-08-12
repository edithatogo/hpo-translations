import copy
import unittest

from scripts.build_terminology_node_registry import OUTPUT, build_registry, canonical_bytes, load
from scripts.validate_terminology_node_registry import validation_errors


class TerminologyNodeRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = load(OUTPUT)

    def test_committed_registry_passes(self) -> None:
        self.assertEqual(validation_errors(self.registry), [])

    def test_generation_is_byte_stable(self) -> None:
        self.assertEqual(canonical_bytes(build_registry()), OUTPUT.read_bytes().replace(b"\r\n", b"\n"))

    def test_every_artifact_namespace_is_explicit(self) -> None:
        namespaces = [item for item in self.registry["nodes"] if item["node_kind"] == "identifier_namespace"]
        self.assertEqual(len(namespaces), 64)
        namespace_ids = {item["node_id"] for item in namespaces}
        self.assertIn("namespace-bto", namespace_ids)
        self.assertIn("namespace-radlex", namespace_ids)
        self.assertIn("namespace-rxnorm", namespace_ids)

    def test_route_editions_are_not_duplicated_as_source_families(self) -> None:
        families = [item for item in self.registry["nodes"] if item["node_kind"] == "source_family"]
        self.assertEqual(len(families), 28)
        self.assertNotIn("family-edition-snomed-canada", {item["node_id"] for item in families})

    def test_all_national_editions_are_explicit(self) -> None:
        editions = [item for item in self.registry["nodes"] if item["node_kind"] == "edition"]
        self.assertEqual(len(editions), 30)

    def test_language_renditions_remain_separate(self) -> None:
        self.assertEqual(len(self.registry["language_renditions"]), 184)
        tags = {(item["parent_node_id"], item["bcp47"]) for item in self.registry["language_renditions"]}
        self.assertIn(("edition-icd10ca-ca-2022", "fr-CA"), tags)
        self.assertIn(("edition-snomed-canada", "fr-CA"), tags)
        self.assertIn(("product-loinc-2-82", "fr-CA"), tags)

    def test_icd10ca_cannot_resolve_to_parent_family(self) -> None:
        mutated = copy.deepcopy(self.registry)
        family = next(item for item in mutated["nodes"] if item["node_id"] == "family-icd10")
        family["aliases"].append({"value": "ICD10CA", "alias_type": "family_alias", "authority_scope": "icd10"})
        self.assertTrue(any("unsafe edition alias" in error for error in validation_errors(mutated)))

    def test_sctid_ca_cannot_resolve_to_parent_family(self) -> None:
        mutated = copy.deepcopy(self.registry)
        family = next(item for item in mutated["nodes"] if item["node_id"] == "family-snomed-ct")
        family["aliases"].append({"value": "SCTID-CA", "alias_type": "family_alias", "authority_scope": "snomed"})
        self.assertTrue(any("unsafe edition alias" in error for error in validation_errors(mutated)))

    def test_region_specific_language_is_not_collapsed(self) -> None:
        mutated = copy.deepcopy(self.registry)
        rendition = next(item for item in mutated["language_renditions"] if item["bcp47"] == "fr-CA")
        rendition["bcp47"] = "fr"
        self.assertIn("language rendition coverage must exactly match governed inventories", validation_errors(mutated))

    def test_missing_namespace_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.registry)
        mutated["nodes"] = [item for item in mutated["nodes"] if item["node_id"] != "namespace-icd10ca"]
        self.assertIn(
            "identifier namespace coverage must exactly match mapping artifacts and source coverage",
            validation_errors(mutated),
        )

    def test_parent_relations_cannot_create_mappings(self) -> None:
        mutated = copy.deepcopy(self.registry)
        mutated["admission_boundary"]["parent_relations_create_mappings"] = True
        self.assertIn("variant admission boundary must remain fail-closed", validation_errors(mutated))


if __name__ == "__main__":
    unittest.main()
