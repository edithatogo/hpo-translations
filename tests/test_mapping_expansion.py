import copy
import unittest

from scripts.validate_mapping_expansion import (
    CATALOG_PATH,
    ICD10_INVENTORY_PATH,
    SCHEMA_PATH,
    SNOMED_INVENTORY_PATH,
    SOURCE_CATALOG_PATH,
    SOURCE_REGISTRY_PATH,
    SUPPLEMENTARY_REVIEWS_PATH,
    UMLS_INVENTORY_PATH,
    load_json,
    validation_errors,
)


class MappingExpansionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = load_json(CATALOG_PATH)
        self.schema = load_json(SCHEMA_PATH)
        self.registry = load_json(SOURCE_REGISTRY_PATH)
        self.source_catalog = load_json(SOURCE_CATALOG_PATH)
        self.supplementary = load_json(SUPPLEMENTARY_REVIEWS_PATH)
        self.umls_inventory = load_json(UMLS_INVENTORY_PATH)
        self.snomed_inventory = load_json(SNOMED_INVENTORY_PATH)
        self.icd10_inventory = load_json(ICD10_INVENTORY_PATH)

    def errors(self, catalog: dict) -> list[str]:
        return validation_errors(
            catalog,
            self.schema,
            self.registry,
            self.source_catalog,
            self.supplementary,
            self.umls_inventory,
            self.snomed_inventory,
            self.icd10_inventory,
        )

    def test_committed_catalog_passes(self) -> None:
        self.assertEqual(self.errors(self.catalog), [])

    def test_payload_admission_fails_closed(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["artifacts"][0]["payload_commit_allowed"] = True
        self.assertTrue(self.errors(mutated))

    def test_missing_registered_source_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["source_coverage"].pop()
        self.assertIn(
            "source_coverage must contain each registered source exactly once",
            self.errors(mutated),
        )

    def test_unknown_artifact_reference_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["source_coverage"][0]["artifact_ids"] = ["invented-map"]
        self.assertTrue(any("unknown artifacts" in error for error in self.errors(mutated)))

    def test_regional_language_inventory_drift_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        snomed = next(item for item in mutated["source_coverage"] if item["source_id"] == "snomed_ct")
        snomed["additional_languages"].remove("fr-CA")
        snomed["additional_languages"].append("fr")
        self.assertIn(
            "snomed_ct additional_languages must exactly match its validated inventory",
            self.errors(mutated),
        )

    def test_hp_mp_cross_catalog_integrity_drift_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        artifact = next(item for item in mutated["artifacts"] if item["artifact_id"] == "hpo-hp-mp-manual")
        artifact["integrity"]["value"] = "0" * 40
        self.assertIn(
            "HP-MP artifact integrity must match the canonical source catalog record",
            self.errors(mutated),
        )

    def test_unknown_cross_catalog_record_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["cross_catalog_links"][0]["record_ids"] = ["invented-source"]
        self.assertTrue(any("unknown source_catalog records" in error for error in self.errors(mutated)))

    def test_required_cross_catalog_link_is_rejected_when_missing(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["cross_catalog_links"] = [
            link for link in mutated["cross_catalog_links"] if link["artifact_id"] != "hpo-hp-mp-manual"
        ]
        self.assertTrue(any("required cross-catalog links are missing" in error for error in self.errors(mutated)))

    def test_canadian_bilingual_map_release_drift_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        artifact = next(item for item in mutated["artifacts"] if item["artifact_id"] == "snomedctca-icd10ca-map")
        artifact["release"] = "unverified"
        self.assertIn(
            "Canadian SNOMED CT to ICD-10-CA artifact must match the national inventory release and languages",
            self.errors(mutated),
        )

    def test_null_integrity_requires_explicit_gate_metadata(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        artifact = next(item for item in mutated["artifacts"] if item["artifact_id"] == "medgen-id-mappings")
        artifact.pop("retrieval_gate")
        self.assertIn("medgen-id-mappings null integrity requires retrieval_gate", self.errors(mutated))

    def test_null_integrity_cannot_claim_verification(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        artifact = next(item for item in mutated["artifacts"] if item["artifact_id"] == "nando-ontology")
        artifact["integrity_status"] = "verified_sha256"
        self.assertIn("nando-ontology null integrity requires explicit unresolved status", self.errors(mutated))

    def test_integrity_algorithm_and_status_must_agree(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        artifact = next(item for item in mutated["artifacts"] if item["artifact_id"] == "mondo-disease-spine")
        artifact["integrity_status"] = "verified_sha256"
        self.assertIn("mondo-disease-spine integrity status does not match its algorithm", self.errors(mutated))


if __name__ == "__main__":
    unittest.main()
