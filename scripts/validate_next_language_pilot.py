import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "research_validation" / "next_language_pilot_plan.json"
SCHEMA_PATH = ROOT / "research_validation" / "next_language_pilot_plan.schema.json"
INVENTORY_PATH = ROOT / "conductor" / "hpo_babelon_language_inventory.json"


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(plan: dict[str, Any], schema: dict[str, Any], inventory: dict[str, Any]) -> list[str]:
    errors = [f"schema: {error.message}" for error in Draft202012Validator(schema).iter_errors(plan)]
    profiles = {row["code"]: row for row in inventory.get("profiles", [])}
    selected = plan.get("primary_next_pilot", {}).get("source_profiles", [])
    optional = plan.get("affordability_contingency", {}).get("source_profiles", [])
    for row in [*selected, *optional]:
        observed = profiles.get(row.get("language"))
        if not observed:
            errors.append(f"missing HPO inventory profile: {row.get('language')}")
            continue
        for field in ("babelon_rows", "synonym_rows", "babelon_blob", "synonym_blob"):
            if row.get(field) != observed.get(field):
                errors.append(f"{row.get('language')}: {field} must match the canonical HPO inventory")
        if row.get("source_status") != observed.get("status"):
            errors.append(f"{row.get('language')}: source_status must match the canonical HPO inventory")
    if [row.get("language") for row in selected] != ["fr", "cs"]:
        errors.append("primary next pilot must be exactly French and Czech")
    if [row.get("language") for row in optional] != ["nl", "tr"]:
        errors.append("affordability expansion must add exactly Dutch and Turkish")
    preparation = plan.get("new_language_governance_preparation", [])
    if [row.get("language") for row in preparation] != ["pl", "uk"]:
        errors.append("new-language governance preparation must be exactly Polish and Ukrainian")
    local_codes = {row.get("code") for row in inventory.get("profiles", [])}
    if any(row.get("language") in local_codes for row in preparation):
        errors.append("Polish and Ukrainian governance preparation cannot claim an existing local HPO payload")
    if plan.get("controls") != {
        "current_g3_changed": False,
        "source_payload_retrieval_authorized": False,
        "translation_rows_added": False,
        "agent_execution_authorized": False,
        "financial_spend_authorized": False,
        "external_contact_authorized": False,
        "remote_upload_authorized": False,
        "automatic_promotion_allowed": False,
        "new_freeze_required": True,
    }:
        errors.append("next-language pilot controls must remain fail-closed")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(load_json(PLAN_PATH), load_json(SCHEMA_PATH), load_json(INVENTORY_PATH))
    if errors:
        print("Next-language pilot validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Next-language pilot validation passed (fr+cs primary; nl+tr contingent; pl+uk governance-only).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
