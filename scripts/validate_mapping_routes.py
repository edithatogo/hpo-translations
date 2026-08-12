"""Validate route definitions and their generated all-pairs catalogue, fail-closed."""

from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator

from scripts.build_mapping_routes import (
    DEFINITIONS,
    NODE_REGISTRY,
    OUTPUT,
    ROOT,
    build_catalog,
    canonical_bytes,
    load_json,
    normalized_file_bytes,
)

SCHEMA = ROOT / "research_validation" / "mapping_route_definitions.schema.json"
EXPANSION = ROOT / "research_validation" / "mapping_expansion_catalog.json"
SOURCE_CATALOG = ROOT / "research_validation" / "source_catalog.json"
REGISTRY = ROOT / "ontology_network" / "source_registry.json"
SUPPLEMENTARY = ROOT / "research_validation" / "supplementary_source_access_reviews.json"


def validation_errors(
    definitions: dict[str, Any], catalog: dict[str, Any], node_registry: dict[str, Any] | None = None
) -> list[str]:
    errors = [e.message for e in Draft202012Validator(load_json(SCHEMA)).iter_errors(definitions)]
    nodes = definitions.get("nodes", [])
    node_ids = [n.get("node_id") for n in nodes]
    known = set(node_ids)
    if len(node_ids) != len(set(node_ids)):
        errors.append("node IDs must be unique")
    aliases: dict[str, set[str]] = {}
    for n in nodes:
        for a in n.get("aliases", []):
            aliases.setdefault(a.casefold(), set()).add(str(n.get("node_id")))
    if any(len(v) > 1 for v in aliases.values()):
        errors.append("namespace aliases must resolve uniquely across canonical nodes")
    policies = {p.get("policy_id"): p for p in definitions.get("composition_policies", [])}
    aids = []
    expansion = load_json(EXPANSION)
    sources = load_json(SOURCE_CATALOG)
    artifacts = {("mapping_expansion_catalog", a["artifact_id"]): a for a in expansion["artifacts"]} | {
        ("source_catalog", a["source_id"]): a for a in sources["mappings"]
    }
    registry_data = node_registry or load_json(NODE_REGISTRY)
    reference_records = {
        **artifacts,
        **{("terminology_node_registry", n["node_id"]): n for n in registry_data["nodes"]},
    }
    registry_node_ids = {n["node_id"] for n in registry_data["nodes"]}
    for node in nodes:
        for ref in node.get("catalog_references", []):
            if (
                str(ref.get("catalog", "")).endswith("terminology_node_registry.json")
                and ref.get("record_id") not in registry_node_ids
            ):
                errors.append(
                    f"{node.get('node_id')} references an unknown terminology registry node: {ref.get('record_id')}"
                )
    for a in definitions.get("atomic_assertions", []):
        aids.append(a.get("assertion_id"))
        if a.get("subject_node_id") not in known or a.get("object_node_id") not in known:
            errors.append(f"{a.get('assertion_id')} references an unknown node")
        if a.get("direction") != "directed" or a.get("reversal_policy") not in {
            "forbidden",
            "separate-evidence-required",
        }:
            errors.append(f"{a.get('assertion_id')} may not synthesize a reverse assertion")
        if a.get("composition_policy_id") not in policies:
            errors.append(f"{a.get('assertion_id')} references an unknown composition policy")
        prefix = (
            "source_catalog" if ("source_catalog", a.get("artifact_id")) in artifacts else "mapping_expansion_catalog"
        )
        if (prefix, a.get("artifact_id")) not in artifacts:
            errors.append(f"{a.get('assertion_id')} references an unknown artifact")
        for ref in [
            *a.get("evidence_refs", []),
            a.get("artifact_release_ref"),
            a.get("artifact_integrity_ref"),
            a.get("artifact_rights_ref"),
            a.get("payload_policy_ref"),
        ]:
            if not isinstance(ref, str) or ":" not in ref:
                errors.append(f"{a.get('assertion_id')} has an invalid catalog reference")
                continue
            base, _, pointer = ref.partition("#/")
            prefix, record_id = base.split(":", 1)
            record = reference_records.get((prefix, record_id))
            if record is None or (pointer and pointer not in record):
                errors.append(f"{a.get('assertion_id')} has an unresolved catalog reference: {ref}")
    if len(aids) != len(set(aids)):
        errors.append("assertion IDs must be unique")
    dispositions = definitions.get("artifact_dispositions", [])
    dkeys = [(d.get("catalog"), d.get("artifact_id")) for d in dispositions]
    if set(dkeys) != set(artifacts) or len(dkeys) != len(set(dkeys)):
        errors.append("artifact dispositions must exactly cover both governed artifact catalogs")
    for d in dispositions:
        unknown = set(d.get("assertion_ids", [])) - set(aids)
        if unknown:
            errors.append(f"{d.get('artifact_id')} disposition references unknown assertions")
        cited = {
            a.get("assertion_id")
            for a in definitions.get("atomic_assertions", [])
            if a.get("artifact_id") == d.get("artifact_id")
        }
        if d.get("disposition") == "asserted" and set(d.get("assertion_ids", [])) != cited:
            errors.append(f"{d.get('artifact_id')} asserted disposition must exactly list its assertions")
    structurally_safe = not errors
    if structurally_safe:
        try:
            expected = build_catalog(definitions, node_registry or load_json(NODE_REGISTRY))
            if catalog != expected:
                errors.append("committed mapping route catalog does not match deterministic generation")
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"route generation rejected invalid definitions: {type(exc).__name__}")
    routes = catalog.get("routes", [])
    if len(routes) != len(nodes) ** 2:
        errors.append("catalog must contain exactly N squared ordered routes")
    pairs = [(r.get("source_node_id"), r.get("target_node_id")) for r in routes]
    if len(pairs) != len(set(pairs)):
        errors.append("ordered route pairs must be unique")
    for r in routes:
        preferred = r.get("preferred_path")
        if r.get("status") == "unavailable" and not r.get("unavailable_reasons"):
            errors.append(f"{r.get('route_id')} unavailable route lacks structured reasons")
        for path in ([preferred] if preferred else []) + r.get("alternative_paths", []):
            if path.get("hop_count", 0) > 3:
                errors.append(f"{r.get('route_id')} exceeds maximum hops")
            if path.get("use_status") not in {"catalogue_only", "candidate_only", "blocked"}:
                errors.append(f"{r.get('route_id')} illegally authorizes use")
    if catalog.get("admission_boundary", {}).get("payloads_included") is not False:
        errors.append("mapping routes must remain payload-free")
    return sorted(set(errors))


def main() -> int:
    d = load_json(DEFINITIONS)
    c = load_json(OUTPUT)
    r = load_json(NODE_REGISTRY)
    errors = validation_errors(d, c, r)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    if normalized_file_bytes(OUTPUT) != canonical_bytes(build_catalog(d, r)):
        print("ERROR: mapping route catalog byte drift detected")
        return 1
    print(f"Mapping route validation passed: {len(c['nodes'])} nodes, {len(c['routes'])} ordered pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
