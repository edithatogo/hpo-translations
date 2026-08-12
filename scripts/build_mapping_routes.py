"""Build the deterministic, payload-free ontology mapping route catalogue."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFINITIONS = ROOT / "research_validation" / "mapping_route_definitions.json"
NODE_REGISTRY = ROOT / "research_validation" / "terminology_node_registry.json"
OUTPUT = ROOT / "research_validation" / "mapping_route_catalog.json"
MAX_HOPS = 3
CLASS_RANK = {
    "curated-crosswalk": 0,
    "source-xref": 1,
    "classification-map": 2,
    "ontology-bridge": 3,
    "compositional": 4,
    "lexical-candidate": 5,
}
RIGHTS_RANK = {
    "metadata-only-payload-blocked": 1,
    "metadata-only-rights-review-required": 2,
    "metadata-only-access-required": 3,
}
LOSS_RANK = {"none": 0, "possible": 1, "unknown": 2, "material": 3}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def normalized_file_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def _hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _paths(
    source: str,
    target: str,
    outgoing: dict[str, list[dict[str, Any]]],
    nodes: dict[str, dict[str, Any]],
    policies: dict[str, dict[str, Any]],
) -> list[list[dict[str, Any]]]:
    found: list[list[dict[str, Any]]] = []

    def visit(current: str, path: list[dict[str, Any]], seen: frozenset[str]) -> None:
        if len(path) >= MAX_HOPS:
            return
        for edge in outgoing.get(current, []):
            nxt = edge["object_node_id"]
            if nxt in seen:
                continue
            candidate = [*path, edge]
            if len(candidate) > 1:
                policy = policies[edge["composition_policy_id"]]
                first_policy = policies[candidate[0]["composition_policy_id"]]
                if (
                    not policy["transitive"]
                    or not first_policy["transitive"]
                    or edge["route_class"] not in policy["allowed_route_classes"]
                    or len(candidate) > min(policy["max_hops"], first_policy["max_hops"])
                    or any(
                        nodes[x]["domain"] != nodes[source]["domain"]
                        for x in [*(e["object_node_id"] for e in candidate)]
                    )
                ):
                    continue
            if nxt == target:
                found.append(candidate)
            visit(nxt, candidate, seen | {nxt})

    visit(source, [], frozenset({source}))
    return found


def _admissibility(path: list[dict[str, Any]]) -> str:
    if any("access-required" in e["status"] or "rights-review-required" in e["status"] for e in path):
        return "blocked"
    if any(e["route_class"] in {"lexical-candidate", "compositional"} for e in path):
        return "candidate_only"
    return "catalogue_only"


def _path_record(path: list[dict[str, Any]], source: str) -> dict[str, Any]:
    lineages = [e["lineage_group"] for e in path]
    independent = [e["independent_evidence_group"] for e in path]
    statuses = [e["status"] for e in path]
    weakest = max(statuses, key=lambda x: (RIGHTS_RANK.get(x, 99), x))
    return {
        "assertion_ids": [e["assertion_id"] for e in path],
        "path_node_ids": [source, *[e["object_node_id"] for e in path]],
        "hop_count": len(path),
        "artifact_ids": sorted({e["artifact_id"] for e in path}),
        "lineage_groups": list(dict.fromkeys(lineages)),
        "independent_evidence_groups": list(dict.fromkeys(independent)),
        "independent_lineage_count": len(set(independent)),
        "repeated_lineage": len(independent) != len(set(independent)),
        "weakest_rights_status": weakest,
        "payload_status": "blocked",
        "integrity_status": "referenced-not-retrieved",
        "version_status": "artifact-reference-required",
        "use_status": _admissibility(path),
        "semantic_loss": max((e["semantic_loss"] for e in path), key=lambda x: (LOSS_RANK.get(x, 99), x)),
    }


def _rank(record: dict[str, Any], assertions: dict[str, dict[str, Any]]) -> tuple[Any, ...]:
    edges = [assertions[x] for x in record["assertion_ids"]]
    use = {"catalogue_only": 0, "candidate_only": 1, "blocked": 2}[record["use_status"]]
    return (
        use,
        LOSS_RANK.get(record["semantic_loss"], 99),
        RIGHTS_RANK.get(record["weakest_rights_status"], 99),
        record["hop_count"],
        record["repeated_lineage"],
        tuple(CLASS_RANK.get(e["route_class"], 99) for e in edges),
        tuple(record["assertion_ids"]),
    )


def build_catalog(definitions: dict[str, Any], node_registry: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = node_registry or load_json(NODE_REGISTRY)
    nodes = {n["node_id"]: n for n in definitions["nodes"]}
    assertions = {a["assertion_id"]: dict(a) for a in definitions["atomic_assertions"]}
    policies = {p["policy_id"]: p for p in definitions["composition_policies"]}
    outgoing: dict[str, list[dict[str, Any]]] = {}
    for edge in assertions.values():
        outgoing.setdefault(edge["subject_node_id"], []).append(edge)
    for edges in outgoing.values():
        edges.sort(key=lambda e: e["assertion_id"])
    routes = []
    for source in sorted(nodes):
        for target in sorted(nodes):
            rid = f"{source}--to--{target}"
            if source == target:
                routes.append(
                    {
                        "route_id": rid,
                        "source_node_id": source,
                        "target_node_id": target,
                        "status": "identity",
                        "route_class": "identity",
                        "preferred_path": {
                            "assertion_ids": [],
                            "path_node_ids": [source],
                            "hop_count": 0,
                            "use_status": "catalogue_only",
                        },
                        "alternative_paths": [],
                    }
                )
                continue
            candidates = [_path_record(p, source) for p in _paths(source, target, outgoing, nodes, policies)]
            candidates.sort(key=lambda p: _rank(p, assertions))
            if not candidates:
                reasons = []
                if nodes[source].get("artifact_status") == "no_artifact":
                    reasons.append("source_has_no_governed_mapping_artifact")
                if nodes[target].get("artifact_status") == "no_artifact":
                    reasons.append("target_has_no_governed_mapping_artifact")
                if not reasons:
                    reasons.append("no_admissible_directed_semantic_path")
                routes.append(
                    {
                        "route_id": rid,
                        "source_node_id": source,
                        "target_node_id": target,
                        "status": "unavailable",
                        "route_class": "unavailable",
                        "preferred_path": None,
                        "alternative_paths": [],
                        "unavailable_reasons": reasons,
                    }
                )
                continue
            preferred = candidates[0]
            routes.append(
                {
                    "route_id": rid,
                    "source_node_id": source,
                    "target_node_id": target,
                    "status": "direct" if preferred["hop_count"] == 1 else "mediated",
                    "route_class": "compositional"
                    if preferred["semantic_loss"] == "material"
                    else ("direct" if preferred["hop_count"] == 1 else "mediated"),
                    "preferred_path": preferred,
                    "alternative_paths": candidates[1:],
                }
            )
    counts: dict[str, int] = {}
    for r in routes:
        route_class = str(r["route_class"])
        counts[route_class] = counts.get(route_class, 0) + 1
    return {
        "schema_version": "mapping-route-catalog-v2",
        "generated_at": definitions["generated_at"],
        "scope": "payload-safe-explicit-assertions-and-policy-governed-routes",
        "definition_sha256": _hash(definitions),
        "terminology_registry_sha256": _hash(registry),
        "node_count": len(nodes),
        "terminology_node_count": len(registry["nodes"]),
        "assertion_count": len(assertions),
        "ordered_pair_count": len(routes),
        "route_class_counts": dict(sorted(counts.items())),
        "nodes": [nodes[x] for x in sorted(nodes)],
        "terminology_registry_ref": "research_validation/terminology_node_registry.json",
        "composition_policies": definitions["composition_policies"],
        "assertions": [assertions[x] for x in sorted(assertions)],
        "artifact_dispositions": definitions["artifact_dispositions"],
        "routes": routes,
        "admission_boundary": definitions["admission_boundary"],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    generated = canonical_bytes(build_catalog(load_json(DEFINITIONS), load_json(NODE_REGISTRY)))
    if a.check:
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
