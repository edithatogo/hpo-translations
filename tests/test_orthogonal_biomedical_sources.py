import copy
import unittest

from scripts.validate_orthogonal_biomedical_sources import CATALOG_PATH, SCHEMA_PATH, load_json, validation_errors


class OrthogonalBiomedicalSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = load_json(CATALOG_PATH)
        self.schema = load_json(SCHEMA_PATH)

    def errors(self, catalog: dict) -> list[str]:
        return validation_errors(catalog, self.schema)

    def test_committed_catalog_passes(self) -> None:
        self.assertEqual(self.errors(self.catalog), [])

    def test_payload_authorization_fails_closed(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["controls"]["payload_retrieval_authorized"] = True
        self.assertTrue(self.errors(mutated))

    def test_atc_cannot_be_publicly_archived(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        next(row for row in mutated["sources"] if row["source_id"] == "who-atc-ddd")["archive_route"] = (
            "public_after_checksum"
        )
        self.assertIn(
            "WHO ATC/DDD must remain metadata-only with exact documented English and Spanish editions",
            self.errors(mutated),
        )

    def test_source_omission_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["sources"].pop()
        self.assertIn("orthogonal source set must exactly match the governed 17-source inventory", self.errors(mutated))

    def test_twi_boundary_is_preserved(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        next(row for row in mutated["sources"] if row["source_id"] == "pro-ctcae")["notes"] = "Resolved"
        self.assertIn(
            "PRO-CTCAE must remain metadata-only and preserve the unresolved Twi boundary", self.errors(mutated)
        )


if __name__ == "__main__":
    unittest.main()
