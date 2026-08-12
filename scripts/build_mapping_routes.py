"""Build the deterministic, payload-free ontology mapping route catalogue."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFINITIONS = ROOT / "research_validation" / "mapping_route_definitions.json"
OUTPUT = ROOT / "research_validation" / "mapping_route_catalog.json"
TRAVERSABLE_CLASSES = {"curated-crosswalk", "source-xref", "ontology-bridge", "classification-map"}
ROUTE_CLASS_RANK = {
    "curated-crosswalk": 0,
    "source-xref": 1,
    "classification-map": 2,
    "ontology-bridge": 3,
    "compositional": 4,
    "lexical-candidate": 5,
}
STATUS_RANK = {
    "metadata-only-payload-blocked": 1,
    "metadata-only-rights-review-required": 2,
    "metadata-only-access-required": 3,
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def normalized_file_bytes(path: Path) -> bytes:
    """Normalize Git checkout line endings before deterministic comparison."""
    return path.read_bytes().replace(b"\r\n", b"\n")


def _edges(definitions: dict[str, Any]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for item in definitions["atomic_assertions"]:
        edge = dict(item)
        edges.append(edge)
        if item["direction"] == "bidirectional-candidate":
            reverse = dict(item)
            reverse["assertion_id"] = f"{item['assertion_id']}--reverse-candidate"
            reverse["subject_node_id"], reverse["object_node_id"] = (item["object_node_id"], item["subject_node_id"])
            reverse["derived_from_assertion_id"] = item["assertion_id"]
            edges.append(reverse)
    return sorted(edges, key=lambda item: item["assertion_id"])


def _route_class(edges: list[dict[str, Any]]) -> str:
    classes = {edge["route_class"] for edge in edges}
    if "compositional" in classes:
        return "compositional"
    return "direct" if len(edges) == 1 else "mediated"


def _admissibility(edges: list[dict[str, Any]]) -> str:
    statuses = {edge["status"] for edge in edges}
    if any("access-required" in status or "rights-review-required" in status for status in statuses):
        return "blocked"
    if any(edge["route_class"] in {"lexical-candidate", "compositional"} for edge in edges):
        return "candidate_only"
    return "metadata_only"


def _weakest_rights_status(edges: list[dict[str, Any]]) -> str:
    return max((edge["status"] for edge in edges), key=lambda value: (STATUS_RANK.get(value, 99), value))


def _find_path(
    source: str,
    target: str,
    nodes: dict[str, dict[str, Any]],
    outgoing: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]] | None:
    queue: deque[tuple[str, list[dict[str, Any]]]] = deque([(source, [])])
    best_depth: dict[str, int] = {source: 0}
    while queue:
        current, path = queue.popleft()
        if len(path) >= 3:
            continue
        for edge in outgoing.get(current, []):
            next_id = edge["object_node_id"]
            candidate = [*path, edge]
            if len(candidate) > 1 and (
                edge["route_class"] not in TRAVERSABLE_CLASSES or nodes[next_id]["domain"] != nodes[source]["domain"]
            ):
                continue
            if next_id == target:
                return candidate
            # Composition is allowed only within one declared semantic domain.
            if edge["route_class"] not in TRAVERSABLE_CLASSES or nodes[next_id]["domain"] != nodes[source]["domain"]:
                continue
            depth = len(candidate)
            if best_depth.get(next_id, 99) < depth:
                continue
            best_depth[next_id] = depth
            queue.append((next_id, candidate))
    return None


def build_catalog(definitions: dict[str, Any]) -> dict[str, Any]:
    nodes = {item["node_id"]: item for item in definitions["nodes"]}
    edges = _edges(definitions)
    outgoing: dict[str, list[dict[str, Any]]] = {}
    for edge in edges:
        outgoing.setdefault(edge["subject_node_id"], []).append(edge)
    for value in outgoing.values():
        value.sort(
            key=lambda item: (
                ROUTE_CLASS_RANK.get(item["route_class"], 99),
                STATUS_RANK.get(item["status"], 99),
                item["assertion_id"],
            )
        )

    routes: list[dict[str, Any]] = []
    for source in sorted(nodes):
        for target in sorted(nodes):
            route_id = f"{source}--to--{target}"
            if source == target:
                routes.append(
                    {
                        "route_id": route_id,
                        "source_node_id": source,
                        "target_node_id": target,
                        "status": "identity",
                        "route_class": "identity",
                        "hop_count": 0,
                        "assertion_ids": [],
                        "path_node_ids": [source],
                        "admissibility": "metadata_only",
                    }
                )
                continue
            path = _find_path(source, target, nodes, outgoing)
            if path is None:
                reason = "no_declared_directed_path"
                if nodes[source].get("artifact_status") == "no_artifact":
                    reason = "source_has_no_governed_mapping_artifact"
                routes.append(
                    {
                        "route_id": route_id,
                        "source_node_id": source,
                        "target_node_id": target,
                        "status": "unavailable",
                        "route_class": "unavailable",
                        "hop_count": 0,
                        "assertion_ids": [],
                        "path_node_ids": [],
                        "admissibility": "none",
                        "reason_code": reason,
                    }
                )
                continue
            path_nodes = [source, *[edge["object_node_id"] for edge in path]]
            routes.append(
                {
                    "route_id": route_id,
                    "source_node_id": source,
                    "target_node_id": target,
                    "status": "direct" if len(path) == 1 else "mediated",
                    "route_class": _route_class(path),
                    "hop_count": len(path),
                    "assertion_ids": [edge["assertion_id"] for edge in path],
                    "path_node_ids": path_nodes,
                    "admissibility": _admissibility(path),
                    "weakest_rights_status": _weakest_rights_status(path),
                    "lineage_groups": sorted({edge["lineage_group"] for edge in path}),
                    "artifact_ids": sorted({edge["artifact_id"] for edge in path}),
                }
            )

    counts: dict[str, int] = {}
    for route in routes:
        counts[route["route_class"]] = counts.get(route["route_class"], 0) + 1
    definition_hash = hashlib.sha256(canonical_bytes(definitions)).hexdigest()
    return {
        "schema_version": "mapping-route-catalog-v1",
        "generated_at": definitions["generated_at"],
        "scope": "payload-safe-explicit-assertions-and-domain-safe-routes",
        "definition_sha256": definition_hash,
        "node_count": len(nodes),
        "assertion_count": len(definitions["atomic_assertions"]),
        "ordered_pair_count": len(routes),
        "route_class_counts": dict(sorted(counts.items())),
        "nodes": [nodes[key] for key in sorted(nodes)],
        "assertions": edges,
        "routes": routes,
        "admission_boundary": definitions["admission_boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = canonical_bytes(build_catalog(load_json(DEFINITIONS)))
    if args.check:
        if not OUTPUT.exists() or normalized_file_bytes(OUTPUT) != generated:
            print("ERROR: mapping route catalog drift detected")
            return 1
        print("Mapping route catalog drift check passed")
        return 0
    OUTPUT.write_bytes(generated)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
