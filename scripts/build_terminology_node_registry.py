"""Build the payload-free terminology namespace, edition, and language registry."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RV = ROOT / "research_validation"
CONDUCTOR = ROOT / "conductor"
OUTPUT = RV / "terminology_node_registry.json"

INPUTS = {
    "routes": RV / "mapping_route_definitions.json",
    "expansion": RV / "mapping_expansion_catalog.json",
    "icd10": CONDUCTOR / "tracks/icd10_integration_20260623/national_variant_inventory.json",
    "snomed": CONDUCTOR / "tracks/snomed_ct_integration_20260623/national_edition_inventory.json",
    "umls": CONDUCTOR / "tracks/umls_metathesaurus_integration_20260623/release_inventory_2026aa.json",
    "loinc": CONDUCTOR / "tracks/loinc_integration_20260623/regional_language_inventory_2_82.json",
    "meddra": CONDUCTOR / "tracks/meddra_integration_20260623/release_language_inventory_v29_0.json",
    "who": CONDUCTOR / "tracks/icd11_integration_20260623/who_classifications_language_inventory_2026_01.json",
    "orphadata": CONDUCTOR / "tracks/orphanet_integration_20260623/product_language_inventory.json",
    "hpo": CONDUCTOR / "hpo_babelon_language_inventory.json",
}

UNSAFE_FAMILY_ALIASES = {"ICD10CM", "ICD-10-CM", "ICD10CA", "ICD-10-CA", "SCTID-CA", "SNOMED CT CA"}
NAMESPACE_FAMILY = {
    "HP": "hpo",
    "DOID": "do",
    "FMA": "fma",
    "ICD10": "icd10",
    "ICD10CA": "icd10",
    "ICD10CM": "icd10",
    "ICD10WHO": "icd10",
    "ICD11": "icd11",
    "LOINC": "loinc",
    "MedDRA": "meddra",
    "MESH": "mesh",
    "MP": "mp",
    "OMIM": "omim",
    "ONCOTREE": "oncotree",
    "ORPHA": "orphanet",
    "ORPHANET": "orphanet",
    "PATO": "pato",
    "SCTID": "snomed-ct",
    "SCTID-CA": "snomed-ct",
    "UMLS": "umls",
    "UPHENO": "upheno",
    "EFO": "efo",
    "DECIPHER": "decipher",
    "NCIT": "ncit",
    "MONDO": "mondo",
    "NANDO": "nando",
    "CL": "cell-ontology",
    "UBERON": "uberon",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def alias(value: str, alias_type: str, authority_scope: str) -> dict[str, str]:
    return {"value": value, "alias_type": alias_type, "authority_scope": authority_scope}


def build_registry() -> dict[str, Any]:
    data = {key: load(path) for key, path in INPUTS.items()}
    nodes: list[dict[str, Any]] = []
    for family in data["routes"]["nodes"]:
        if any(
            reference["catalog"] == "research_validation/terminology_node_registry.json"
            for reference in family["catalog_references"]
        ):
            continue
        values = [value for value in family["aliases"] if value not in UNSAFE_FAMILY_ALIASES]
        nodes.append(
            {
                "node_id": f"family-{family['node_id']}",
                "node_kind": "source_family",
                "name": family["name"],
                "aliases": [alias(value, "family_alias", family["node_id"]) for value in values],
                "provenance": ["research_validation/mapping_route_definitions.json"],
            }
        )

    namespaces = sorted(
        {ns for artifact in data["expansion"]["artifacts"] for ns in artifact["mapped_namespaces"]}
        | {ns for coverage in data["expansion"]["source_coverage"] for ns in coverage["additional_mapped_namespaces"]}
    )
    for namespace in namespaces:
        parent = NAMESPACE_FAMILY.get(namespace)
        nodes.append(
            {
                "node_id": f"namespace-{slug(namespace)}",
                "node_kind": "identifier_namespace",
                "name": namespace,
                **({"parent_node_id": f"family-{parent}"} if parent else {}),
                "governance_status": "governed_family" if parent else "auxiliary_inventory_only",
                "aliases": [alias(namespace, "canonical_prefix", "mapping-artifact")],
                "provenance": ["research_validation/mapping_expansion_catalog.json"],
            }
        )

    rendition_specs: list[tuple[str, list[dict[str, Any]], str]] = []
    for profile in data["icd10"]["variant_profiles"]:
        node_id = f"edition-{slug(profile['profile_id'])}"
        nodes.append(
            {
                "node_id": node_id,
                "node_kind": "edition",
                "name": profile["classification"],
                "parent_node_id": "family-icd10",
                "jurisdiction": profile["jurisdiction"],
                "version": profile["release"],
                "aliases": [alias(profile["profile_id"], "profile_id", "icd10-inventory")],
                "provenance": ["conductor/tracks/icd10_integration_20260623/national_variant_inventory.json"],
            }
        )
        rendition_specs.append((node_id, [{"bcp47": code} for code in profile["languages"]], "current"))

    snomed_profiles = [
        *data["snomed"]["translation_profiles"],
        *data["snomed"]["edition_examples_without_translation_inference"],
    ]
    for profile in snomed_profiles:
        node_id = f"edition-snomed-{slug(profile.get('jurisdiction', profile.get('name', 'unknown')))}"
        edition_aliases = [
            alias(profile.get("jurisdiction", profile.get("name", "")), "display_name", "snomed-inventory")
        ]
        if profile.get("edition_uri"):
            edition_aliases.append(alias(profile["edition_uri"], "edition_uri", "snomed-international"))
        nodes.append(
            {
                "node_id": node_id,
                "node_kind": "edition",
                "name": f"SNOMED CT {profile.get('jurisdiction', profile.get('name'))}",
                "parent_node_id": "family-snomed-ct",
                "jurisdiction": profile.get("jurisdiction", profile.get("name")),
                "aliases": edition_aliases,
                "provenance": ["conductor/tracks/snomed_ct_integration_20260623/national_edition_inventory.json"],
            }
        )
        rendition_specs.append((node_id, [{"bcp47": code} for code in profile["languages"]], "current"))

    def product(node_id: str, name: str, parent: str, version: str, provenance: str) -> None:
        nodes.append(
            {
                "node_id": node_id,
                "node_kind": "product_release",
                "name": name,
                "parent_node_id": parent,
                "version": version,
                "aliases": [alias(node_id.removeprefix("product-"), "product_id", provenance)],
                "provenance": [provenance],
            }
        )

    product(
        "product-umls-2026aa",
        "UMLS Metathesaurus 2026AA",
        "family-umls",
        data["umls"]["release"],
        "conductor/tracks/umls_metathesaurus_integration_20260623/release_inventory_2026aa.json",
    )
    rendition_specs.append(("product-umls-2026aa", data["umls"]["languages"], "current"))
    product(
        "product-loinc-2-82",
        "LOINC 2.82 linguistic variants",
        "family-loinc",
        data["loinc"]["package_release"],
        "conductor/tracks/loinc_integration_20260623/regional_language_inventory_2_82.json",
    )
    rendition_specs.append(("product-loinc-2-82", data["loinc"]["regional_variants"], "current"))
    product(
        "product-meddra-29-0",
        "MedDRA 29.0",
        "family-meddra",
        data["meddra"]["release"],
        "conductor/tracks/meddra_integration_20260623/release_language_inventory_v29_0.json",
    )
    rendition_specs.append(("product-meddra-29-0", data["meddra"]["languages"], "current"))
    for item in data["who"]["products"]:
        node_id = f"product-who-{slug(item['product_id'])}-2026-01"
        parent = "family-icd11" if item["product_id"] == "icd11-mms" else "family-who-icf"
        product(
            node_id,
            item["product_name"],
            parent,
            data["who"]["release_id"],
            "conductor/tracks/icd11_integration_20260623/who_classifications_language_inventory_2026_01.json",
        )
        rendition_specs.append((node_id, item["languages"], "current"))
    for item in data["orphadata"]["products"]:
        node_id = f"product-orphadata-{slug(item['product_id'])}"
        version = item.get("knowledge_base_release", item.get("release", "unresolved"))
        product(
            node_id,
            item["name"],
            "family-orphanet",
            version,
            "conductor/tracks/orphanet_integration_20260623/product_language_inventory.json",
        )
        language_rows = item.get("language_vintages", [{"language": code} for code in item.get("languages", [])])
        rendition_specs.append((node_id, language_rows, "current"))
    product(
        "product-hpo-babelon",
        "HPO Babelon profiles",
        "family-hpo",
        data["hpo"]["observed_at_commit"],
        "conductor/hpo_babelon_language_inventory.json",
    )
    rendition_specs.append(
        (
            "product-hpo-babelon",
            [{"bcp47": row["code"], "availability_status": row["status"]} for row in data["hpo"]["profiles"]],
            "current",
        )
    )

    renditions: list[dict[str, Any]] = []
    for parent, rows, default_status in rendition_specs:
        for row in rows:
            code = str(row.get("bcp47", row.get("language")))
            status = row.get("availability_status", row.get("vintage_status", default_status))
            renditions.append(
                {
                    "rendition_id": f"rendition-{parent}-{slug(code)}",
                    "parent_node_id": parent,
                    "bcp47": code,
                    "status": status,
                }
            )

    return {
        "schema_version": "terminology-node-registry-v1",
        "generated_at": "2026-08-12T00:00:00Z",
        "scope": "payload-free terminology families, namespaces, editions, products, and language renditions",
        "nodes": sorted(nodes, key=lambda item: item["node_id"]),
        "language_renditions": sorted(renditions, key=lambda item: item["rendition_id"]),
        "admission_boundary": {
            "payloads_included": False,
            "parent_relations_create_mappings": False,
            "language_variants_are_interchangeable": False,
            "edition_inheritance_allowed": False,
        },
    }


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = canonical_bytes(build_registry())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_bytes().replace(b"\r\n", b"\n") != generated:
            print("ERROR: terminology node registry drift detected")
            return 1
        print("Terminology node registry drift check passed")
        return 0
    OUTPUT.write_bytes(generated)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
