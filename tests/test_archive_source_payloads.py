import copy
import unittest

from scripts.archive_source_payloads import CATALOG, PLAN, SCHEMA, load_json, validation_errors


class SourcePayloadArchiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = load_json(PLAN)
        self.schema = load_json(SCHEMA)
        self.catalog = load_json(CATALOG)

    def test_committed_plan_passes(self) -> None:
        self.assertEqual(validation_errors(self.plan, self.schema, self.catalog), [])

    def test_plan_covers_complete_mapping_catalog(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["artifacts"].pop()
        self.assertIn(
            "archive plan must cover every mapping catalog artifact exactly once",
            validation_errors(mutated, self.schema, self.catalog),
        )

    def test_metadata_only_cannot_retrieve(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["artifacts"][-1]["payload_retrieval_allowed"] = True
        self.assertTrue(
            any("metadata-only route cannot retrieve" in item for item in validation_errors(mutated, self.schema))
        )

    def test_private_route_cannot_enable_upload_by_default(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["artifacts"][3]["remote_upload_allowed"] = True
        self.assertTrue(
            any(
                "restricted route cannot enable remote upload" in item
                for item in validation_errors(mutated, self.schema)
            )
        )

    def test_public_upload_requires_explicit_target(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["artifacts"][0]["remote_upload_allowed"] = True
        self.assertTrue(
            any(
                "public upload requires an explicit public target" in item
                for item in validation_errors(mutated, self.schema)
            )
        )

    def test_retrieval_requires_checksum(self) -> None:
        mutated = copy.deepcopy(self.plan)
        mutated["artifacts"][0]["expected_sha256"] = None
        self.assertTrue(
            any("retrieval requires an expected SHA-256" in item for item in validation_errors(mutated, self.schema))
        )


if __name__ == "__main__":
    unittest.main()
