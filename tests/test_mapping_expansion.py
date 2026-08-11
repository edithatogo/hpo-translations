import copy
import unittest

from scripts.validate_mapping_expansion import (
    CATALOG_PATH,
    SCHEMA_PATH,
    SOURCE_REGISTRY_PATH,
    load_json,
    validation_errors,
)


class MappingExpansionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = load_json(CATALOG_PATH)
        self.schema = load_json(SCHEMA_PATH)
        self.registry = load_json(SOURCE_REGISTRY_PATH)

    def errors(self, catalog: dict) -> list[str]:
        return validation_errors(catalog, self.schema, self.registry)

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


if __name__ == "__main__":
    unittest.main()
