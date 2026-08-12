import copy
import tempfile
import unittest
from pathlib import Path

from scripts.build_mapping_routes import (
    DEFINITIONS,
    OUTPUT,
    build_catalog,
    canonical_bytes,
    load_json,
    normalized_file_bytes,
)
from scripts.validate_mapping_routes import validation_errors


class MappingRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.definitions = load_json(DEFINITIONS)
        self.catalog = load_json(OUTPUT)

    def errors(
        self,
        definitions: dict | None = None,
        catalog: dict | None = None,
    ) -> list[str]:
        return validation_errors(definitions or self.definitions, catalog or self.catalog)

    def test_committed_catalog_passes(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_every_ordered_pair_is_present_once(self) -> None:
        node_count = len(self.definitions["nodes"])
        pairs = [(route["source_node_id"], route["target_node_id"]) for route in self.catalog["routes"]]
        self.assertEqual(len(pairs), node_count**2)
        self.assertEqual(len(pairs), len(set(pairs)))

    def test_generation_is_deterministic_and_byte_stable(self) -> None:
        first = build_catalog(copy.deepcopy(self.definitions))
        second = build_catalog(copy.deepcopy(self.definitions))
        self.assertEqual(first, second)
        self.assertEqual(canonical_bytes(first), canonical_bytes(second))
        self.assertEqual(canonical_bytes(first), normalized_file_bytes(OUTPUT))

    def test_windows_checkout_line_endings_are_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_bytes(b'{\r\n  "ok": true\r\n}\r\n')
            self.assertEqual(normalized_file_bytes(path), b'{\n  "ok": true\n}\n')

    def test_curated_or_source_xref_route_precedes_lexical_candidate(self) -> None:
        route = next(item for item in self.catalog["routes"] if item["route_id"] == "mondo--to--hpo")
        self.assertEqual(route["preferred_path"]["assertion_ids"], ["mondo-hpo-xref"])
        self.assertEqual(route["preferred_path"]["use_status"], "catalogue_only")
        self.assertEqual(route["alternative_paths"][0]["assertion_ids"], ["mondo-hpo-lexical"])

    def test_missing_pair_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["routes"].pop()
        self.assertIn("catalog must contain exactly N squared ordered routes", self.errors(catalog=mutated))

    def test_duplicate_pair_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["routes"][-1] = copy.deepcopy(mutated["routes"][0])
        self.assertIn("ordered route pairs must be unique", self.errors(catalog=mutated))

    def test_unknown_assertion_node_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.definitions)
        mutated["atomic_assertions"][0]["object_node_id"] = "invented-ontology"
        self.assertTrue(any("references an unknown node" in error for error in self.errors(definitions=mutated)))

    def test_unknown_artifact_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.definitions)
        mutated["atomic_assertions"][0]["artifact_id"] = "invented-map"
        self.assertTrue(any("references an unknown artifact" in error for error in self.errors(definitions=mutated)))

    def test_alias_collision_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.definitions)
        mutated["nodes"][1]["aliases"].append(mutated["nodes"][0]["aliases"][0].swapcase())
        self.assertIn(
            "namespace aliases must resolve uniquely across canonical nodes",
            self.errors(definitions=mutated),
        )

    def test_broken_path_shape_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        route = next(
            item for item in mutated["routes"] if item["preferred_path"] and item["preferred_path"]["assertion_ids"]
        )
        route["preferred_path"]["path_node_ids"].pop()
        self.assertIn(
            "committed mapping route catalog does not match deterministic generation", self.errors(catalog=mutated)
        )

    def test_broken_path_direction_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        route = next(
            item for item in mutated["routes"] if item["preferred_path"] and item["preferred_path"]["assertion_ids"]
        )
        route["preferred_path"]["path_node_ids"][0] = route["target_node_id"]
        self.assertIn(
            "committed mapping route catalog does not match deterministic generation", self.errors(catalog=mutated)
        )

    def test_metadata_route_cannot_be_escalated_to_authorized(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        route = next(
            item for item in mutated["routes"] if item["preferred_path"] and item["preferred_path"]["assertion_ids"]
        )
        route["preferred_path"]["use_status"] = "authorized"
        self.assertTrue(any("illegally authorizes" in error for error in self.errors(catalog=mutated)))

    def test_compositional_assertion_cannot_be_authorized(self) -> None:
        mutated = copy.deepcopy(self.definitions)
        assertion = next(item for item in mutated["atomic_assertions"] if item["route_class"] == "compositional")
        assertion["status"] = "authorized"
        self.assertTrue(self.errors(definitions=mutated))

    def test_unavailable_route_requires_reason(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        route = next(item for item in mutated["routes"] if item["status"] == "unavailable")
        route.pop("unavailable_reasons")
        self.assertTrue(
            any("unavailable route lacks structured reasons" in error for error in self.errors(catalog=mutated))
        )

    def test_payload_boundary_is_fail_closed(self) -> None:
        mutated = copy.deepcopy(self.catalog)
        mutated["admission_boundary"]["payloads_included"] = True
        self.assertIn("mapping routes must remain payload-free", self.errors(catalog=mutated))

    def test_no_reverse_edge_is_synthesized(self) -> None:
        self.assertFalse(any("reverse" in item["assertion_id"] for item in self.catalog["assertions"]))
        reverse = next(item for item in self.catalog["routes"] if item["route_id"] == "mp--to--hpo")
        self.assertEqual(reverse["status"], "unavailable")

    def test_alternative_routes_are_retained_and_ranked(self) -> None:
        route = next(item for item in self.catalog["routes"] if item["route_id"] == "mondo--to--hpo")
        self.assertEqual(route["preferred_path"]["assertion_ids"], ["mondo-hpo-xref"])
        self.assertTrue(any(path["assertion_ids"] == ["mondo-hpo-lexical"] for path in route["alternative_paths"]))

    def test_artifact_dispositions_are_exact(self) -> None:
        mutated = copy.deepcopy(self.definitions)
        mutated["artifact_dispositions"].pop()
        self.assertIn(
            "artifact dispositions must exactly cover both governed artifact catalogs", self.errors(definitions=mutated)
        )

    def test_unresolved_catalog_reference_is_rejected_without_crashing(self) -> None:
        mutated = copy.deepcopy(self.definitions)
        mutated["atomic_assertions"][0]["evidence_refs"] = ["terminology_node_registry:invented-node"]
        self.assertTrue(any("unresolved catalog reference" in error for error in self.errors(definitions=mutated)))

    def test_invalid_schema_fails_without_calling_generation(self) -> None:
        mutated = copy.deepcopy(self.definitions)
        mutated["atomic_assertions"][0].pop("predicate")
        self.assertTrue(self.errors(definitions=mutated))

    def test_hyperedge_clique_inference_boundary_is_fail_closed(self) -> None:
        mutated = copy.deepcopy(self.definitions)
        mutated["admission_boundary"]["hyperedge_cliques_forbidden"] = False
        self.assertTrue(self.errors(definitions=mutated))


if __name__ == "__main__":
    unittest.main()
