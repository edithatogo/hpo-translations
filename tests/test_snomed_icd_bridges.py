import copy
import unittest

from scripts.validate_snomed_icd_bridges import CATALOG, SCHEMA, load, validation_errors


class SnomedIcdBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load(CATALOG)
        cls.schema = load(SCHEMA)

    def errors(self, value: dict[str, object]) -> list[str]:
        return validation_errors(value, self.schema)

    def test_committed_catalog_passes(self) -> None:
        self.assertEqual([], self.errors(self.catalog))

    def test_orphanet_cannot_be_promoted_to_direct(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        next(row for row in mutated["resources"] if row["resource_id"] == "orphadata-alignments")["connection_type"] = (
            "direct_authority_map"
        )
        self.assertTrue(any("only the authority-published" in error for error in self.errors(mutated)))

    def test_umls_payload_authority_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["resources"][0]["payload_authorized"] = True
        self.assertTrue(any("payload" in error for error in self.errors(mutated)))

    def test_missing_icd_endpoint_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["resources"][1]["icd_endpoint"] = ""
        self.assertTrue(any("terminology endpoints" in error or "schema" in error for error in self.errors(mutated)))

    def test_authenticated_access_cannot_be_inferred(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["controls"]["authenticated_access_authorized"] = True
        self.assertIn("bridge controls must remain fail-closed", self.errors(mutated))


if __name__ == "__main__":
    unittest.main()
