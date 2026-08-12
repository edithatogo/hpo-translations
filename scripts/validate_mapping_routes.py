"""Validate mapping-route definitions and their deterministic all-pairs catalog."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from scripts.build_mapping_routes import DEFINITIONS, OUTPUT, build_catalog, canonical_bytes, load_json

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "research_validation" / "mapping_route_definitions.schema.json"
EXPANSION = ROOT / "research_validation" / "mapping_expansion_catalog.json"
SOURCE_CATALOG = ROOT / "research_validation" / "source_catalog.json"
REGISTRY = ROOT / "ontology_network" / "source_registry.json"
SUPPLEMENTARY = ROOT / "research_validation" / "supplementary_source_access_reviews.json"


def validation_errors(definitions: dict[str, Any], catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    schema = load_json(SCHEMA)
    errors.extend(error.message for error in Draft202012Validator(schema).iter_errors(definitions))
    nodes = definitions.get("nodes", [])
    node_ids = [item.get("node_id") for item in nodes]
    if len(node_ids) != len(set(node_ids)):
        errors.append("node IDs must be unique")
    alias_owners: dict[str, set[str]] = {}
    for item in nodes:
        for alias in item.get("aliases", []):
            alias_owners.setdefault(alias.casefold(), set()).add(item["node_id"])
    if any(len(owners) > 1 for owners in alias_owners.values()):
        errors.append("namespace aliases must resolve uniquely across canonical nodes")

    assertion_ids = [item.get("assertion_id") for item in definitions.get("atomic_assertions", [])]
    if len(assertion_ids) != len(set(assertion_ids)):
        errors.append("assertion IDs must be unique")
    known_nodes = set(node_ids)
    known_artifacts = {item["artifact_id"] for item in load_json(EXPANSION)["artifacts"]}
    known_artifacts |= {item["source_id"] for item in load_json(SOURCE_CATALOG)["mappings"]}
    for item in definitions.get("atomic_assertions", []):
        if item.get("subject_node_id") not in known_nodes or item.get("object_node_id") not in known_nodes:
            errors.append(f"{item.get('assertion_id')} references an unknown node")
        if item.get("artifact_id") not in known_artifacts:
            errors.append(f"{item.get('assertion_id')} references an unknown artifact")
        if item.get("route_class") == "compositional" and item.get("status") == "authorized":
            errors.append(f"{item.get('assertion_id')} compositional assertion cannot be authorized")

    registry_ids = {item["source_id"] for item in load_json(REGISTRY)["records"]}
    supplementary_ids = {item["source_id"] for item in load_json(SUPPLEMENTARY)["reviews"]}
    represented = set(node_ids)
    normalized_registry = {"snomed-ct" if item == "snomed_ct" else item for item in registry_ids}
    if not normalized_registry <= represented:
        errors.append("every registered ontology source must have a canonical node")
    if not {"hpo", "mondo", "cell-ontology", "nando"} <= represented:
        errors.append("required anchor and mediator nodes are missing")
    if not ({"pato"} | (supplementary_ids - {"pato"})) <= represented:
        errors.append("every supplementary source family must have one canonical node")

    assertions_structurally_routable = all(
        item.get("subject_node_id") in known_nodes and item.get("object_node_id") in known_nodes
        for item in definitions.get("atomic_assertions", [])
    )
    if assertions_structurally_routable:
        expected = build_catalog(definitions)
        if catalog != expected:
            errors.append("committed mapping route catalog does not match deterministic generation")
    routes = catalog.get("routes", [])
    if len(routes) != len(nodes) ** 2:
        errors.append("catalog must contain exactly N squared ordered routes")
    keys = [(item.get("source_node_id"), item.get("target_node_id")) for item in routes]
    if len(keys) != len(set(keys)):
        errors.append("ordered route pairs must be unique")
    assertions = {item["assertion_id"]: item for item in catalog.get("assertions", [])}
    for route in routes:
        path = route.get("path_node_ids", [])
        edge_ids = route.get("assertion_ids", [])
        if edge_ids:
            if len(path) != len(edge_ids) + 1:
                errors.append(f"{route.get('route_id')} has a malformed path")
                continue
            for index, edge_id in enumerate(edge_ids):
                edge = assertions.get(edge_id)
                if (
                    edge is None
                    or edge.get("subject_node_id") != path[index]
                    or edge.get("object_node_id") != path[index + 1]
                ):
                    errors.append(f"{route.get('route_id')} path is not directionally contiguous")
        if route.get("admissibility") == "authorized":
            errors.append(f"{route.get('route_id')} illegally authorizes a metadata-only route")
        if route.get("status") == "unavailable" and not route.get("reason_code"):
            errors.append(f"{route.get('route_id')} unavailable route lacks a reason")
    if catalog.get("admission_boundary", {}).get("payloads_included") is not False:
        errors.append("mapping routes must remain payload-free")
    return sorted(set(errors))


def main() -> int:
    definitions = load_json(DEFINITIONS)
    catalog = load_json(OUTPUT)
    errors = validation_errors(definitions, catalog)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if OUTPUT.read_bytes() != canonical_bytes(build_catalog(definitions)):
        print("ERROR: mapping route catalog byte drift detected")
        return 1
    print(f"Mapping route validation passed: {len(catalog['nodes'])} nodes, {len(catalog['routes'])} ordered pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
