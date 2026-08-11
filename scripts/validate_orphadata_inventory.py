import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "conductor/tracks/orphanet_integration_20260623/product_language_inventory.json"
SCHEMA = ROOT / "conductor/schemas/orphadata_product_language_inventory_v1.schema.json"


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(inventory: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [error.message for error in validator.iter_errors(inventory)]
    products = {row.get("product_id"): row for row in inventory.get("products", [])}
    if len(products) != 3:
        errors.append("product_id values must be unique and cover exactly three scoped products")
    expected = {
        "nomenclature-pack": (9, {"cs", "de", "en", "es", "fr", "it", "nl", "pl", "pt"}),
        "product4-phenotypes-hpo": (7, {"de", "en", "es", "fr", "it", "nl", "pt"}),
    }
    for product_id, (count, languages) in expected.items():
        product = products.get(product_id, {})
        if product.get("language_count") != count or set(product.get("languages", [])) != languages:
            errors.append(f"{product_id}: exact product language set is inconsistent")
    alignments = products.get("product1-alignments", {})
    vintages = alignments.get("language_vintages", [])
    if alignments.get("language_count") != 12 or len(vintages) != 12:
        errors.append("product1-alignments: exactly 12 language vintages are required")
    codes = [row.get("language") for row in vintages]
    if len(codes) != len(set(codes)):
        errors.append("product1-alignments: language values must be unique")
    stale_expected = {"tr", "uk", "zh"}
    stale_actual = {row.get("language") for row in vintages if str(row.get("vintage_status", "")).startswith("stale")}
    if stale_actual != stale_expected:
        errors.append("product1-alignments: Turkish, Ukrainian and Chinese must retain explicit stale status")
    for row in vintages:
        if row.get("language") not in stale_expected and row.get("release_date") != "2026-06-23":
            errors.append(f"product1-alignments: {row.get('language')} current vintage must be 2026-06-23")
    if any(product.get("payload_incorporated") is not False for product in products.values()):
        errors.append("all Orphadata products must remain payload-free")
    phenotype_scope = str(products.get("product4-phenotypes-hpo", {}).get("scope", "")).lower()
    if "not independent hpo lexical translation evidence" not in phenotype_scope:
        errors.append("product4-phenotypes-hpo must not be promoted as independent translation evidence")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(load_json(INVENTORY), load_json(SCHEMA))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Orphadata product-language inventory validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
