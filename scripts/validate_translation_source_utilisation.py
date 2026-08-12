import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "research_validation" / "translation_source_utilisation_plan.json"
SCHEMA_PATH = ROOT / "research_validation" / "translation_source_utilisation_plan.schema.json"
ROUTES_PATH = ROOT / "research_validation" / "mapping_route_definitions.json"
ASSIGNMENTS_PATH = ROOT / "research_validation" / "translation_source_assignments.json"
SAP_PATH = ROOT / "research_validation" / "translation_statistical_analysis_plan.json"
ASSIGNMENTS_SCHEMA_PATH = ROOT / "research_validation" / "translation_source_assignments.schema.json"
SAP_SCHEMA_PATH = ROOT / "research_validation" / "translation_statistical_analysis_plan.schema.json"
MODEL_TIER_PATH = ROOT / "research_validation" / "translation_model_tier_plan.json"
MODEL_TIER_SCHEMA_PATH = ROOT / "research_validation" / "translation_model_tier_plan.schema.json"
LEARNING_LOOP_PATH = ROOT / "research_validation" / "translation_plan_learning_loop.json"
LEARNING_LOOP_SCHEMA_PATH = ROOT / "research_validation" / "translation_plan_learning_loop.schema.json"

EXPECTED_ROLES = {
    "withheld_hpo_reference",
    "independent_multilingual_lexical_source",
    "mapped_clinical_or_disease_context",
    "structural_compositional_source",
    "aggregator_or_derived_hub",
}
EXPECTED_ANALYSES = {f"A{i}" for i in range(1, 9)}


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(
    plan: dict[str, Any],
    schema: dict[str, Any],
    routes: dict[str, Any],
    assignments: dict[str, Any] | None = None,
    sap: dict[str, Any] | None = None,
    model_tiers: dict[str, Any] | None = None,
    learning_loop: dict[str, Any] | None = None,
    root: Path = ROOT,
) -> list[str]:
    validator: Any = Draft202012Validator(schema)
    errors = [f"schema: {error.message}" for error in validator.iter_errors(plan)]
    if errors:
        return sorted(errors)

    inputs = cast(list[str], plan["canonical_inputs"])
    for relative_path in inputs:
        if not (root / relative_path).is_file():
            errors.append(f"canonical input does not exist: {relative_path}")

    roles = cast(list[dict[str, Any]], plan["source_role_classes"])
    role_ids = [cast(str, role["role_id"]) for role in roles]
    if len(role_ids) != len(set(role_ids)):
        errors.append("source role IDs must be unique")
    if set(role_ids) != EXPECTED_ROLES:
        errors.append("source role set must remain the five governed evidence roles")

    stages = cast(list[dict[str, Any]], plan["stages"])
    if [stage["stage_id"] for stage in stages] != [f"U{i}" for i in range(7)]:
        errors.append("utilisation stages must remain ordered U0 through U6")

    analyses = cast(list[dict[str, Any]], plan["analyses"])
    analysis_prefixes = {cast(str, item["analysis_id"]).split("_", 1)[0] for item in analyses}
    if analysis_prefixes != EXPECTED_ANALYSES:
        errors.append("analysis set must remain A1 through A8")

    scope = cast(dict[str, Any], plan["current_study_scope"])
    if scope["freeze_id"] != "g3-option-b-es-ja-20260812-v1" or scope["languages"] != ["es", "ja"]:
        errors.append("current empirical scope must remain the sealed Spanish/Japanese G3 freeze")
    if scope["excluded_profile"] != "tw":
        errors.append("the unresolved tw profile must remain excluded")

    controls = cast(dict[str, Any], plan["controls"])
    false_controls = (
        "payload_rows_committed",
        "restricted_terms_committed",
        "credentials_committed",
        "automatic_promotion_allowed",
        "agent_panel_can_grant_rights_or_community_or_ethics_authority",
    )
    if any(controls[key] is not False for key in false_controls):
        errors.append("payload, credential, authority, and automatic-promotion controls must fail closed")
    if controls["maintainer_promotion_decision_required"] is not True:
        errors.append("an explicit maintainer promotion decision must remain required")

    assertions = cast(list[dict[str, Any]], routes.get("atomic_assertions", []))
    if not assertions:
        assertions = cast(list[dict[str, Any]], routes.get("mapping_assertions", []))
    if len(assertions) != 42:
        errors.append("utilisation plan expects the current 42 metadata-only mapping assertions")
    admitted_markers = {"authorized", "payload-admitted", "payload_allowed", "empirical"}
    for assertion in assertions:
        serialized = json.dumps(assertion, sort_keys=True).lower()
        if any(f'"{marker}"' in serialized for marker in admitted_markers):
            errors.append("mapping assertions must not be treated as payload-admitted evidence")
            break

    promotion_rule = cast(dict[str, Any], plan["decision_rules"])["promotion"]
    if "No score" not in promotion_rule or "maintainer" not in promotion_rule:
        errors.append("promotion rule must reject score-based promotion and retain maintainer authority")
    if assignments is not None:
        errors.extend(
            f"assignments schema: {error.message}"
            for error in validator.evolve(schema=load_json(ASSIGNMENTS_SCHEMA_PATH)).iter_errors(assignments)
        )
        rows = cast(list[dict[str, Any]], assignments.get("assignments", []))
        if assignments.get("assignment_count") != 15 or len(rows) != 15:
            errors.append("source assignment matrix must contain exactly 15 governed assignments")
        ids = [row.get("id") for row in rows]
        if len(ids) != len(set(ids)):
            errors.append("source assignment IDs must be unique")
        known_assertions = {item["assertion_id"] for item in assertions}
        for row in rows:
            for assertion_id in row.get("assertions", []):
                if assertion_id != "*" and assertion_id not in known_assertions:
                    errors.append(f"unknown source-assignment assertion: {assertion_id}")
        if any(assignments.get("controls", {}).values()):
            errors.append("source assignment payload, candidate, route, and promotion controls must remain false")
    if sap is not None:
        errors.extend(
            f"statistical plan schema: {error.message}"
            for error in validator.evolve(schema=load_json(SAP_SCHEMA_PATH)).iter_errors(sap)
        )
        specs = cast(list[dict[str, Any]], sap.get("analyses", []))
        if [item.get("id") for item in specs] != [f"A{i}" for i in range(1, 11)]:
            errors.append("statistical analysis plan must bind A1 through A10 in order")
        if sap.get("freeze_binding", {}).get("current_freeze_id") != "g3-option-b-es-ja-20260812-v1":
            errors.append("statistical plan must preserve the sealed G3 freeze reference")
        if sap.get("promotion_allowed") is not False:
            errors.append("statistical analysis can never authorize promotion")
    if model_tiers is not None:
        errors.extend(
            f"model tier schema: {error.message}"
            for error in validator.evolve(schema=load_json(MODEL_TIER_SCHEMA_PATH)).iter_errors(model_tiers)
        )
        tier_ids = [item.get("id") for item in model_tiers.get("tier_definition", {}).get("tiers", [])]
        if tier_ids != ["tiny", "small", "medium", "large"]:
            errors.append("model tiers must remain ordered tiny, small, medium, large")
        expected_cells = [f"{tier}_{arm}" for tier in tier_ids for arm in ("E0", "E1", "E2")]
        if model_tiers.get("cell_manifest") != expected_cells:
            errors.append("model tier plan must contain the complete ordered 12-cell factorial")
        arms = cast(list[dict[str, Any]], model_tiers.get("evidence_arms", []))
        if [item.get("id") for item in arms] != [
            "E0_model_only",
            "E1_translation_assisted",
            "E2_lineage_ontology_assisted",
            "R0_withheld_existing_hpo_translation",
        ]:
            errors.append("model evidence arms must remain E0, E1, E2, and R0")
        reference: dict[str, Any] = arms[-1] if arms else {}
        if (
            reference.get("generation_allowed") is not False
            or reference.get("reference_reveal") != "after_candidate_lock"
        ):
            errors.append("existing HPO translations must remain non-generative and withheld until candidate lock")
        if model_tiers.get("current_freeze", {}).get("freeze_id") != "g3-option-b-es-ja-20260812-v1":
            errors.append("model tier plan must preserve the current G3 reference")
        controls_tier = model_tiers.get("controls", {})
        for key in (
            "payload_use_authorized",
            "empirical_execution_authorized",
            "automatic_promotion",
            "agents_grant_rights_community_ethics_or_promotion",
        ):
            if controls_tier.get(key) is not False:
                errors.append("model tier payload, execution, authority, and promotion controls must remain false")
                break
        if controls_tier.get("new_freeze_required") is not True:
            errors.append("model tier execution must require a new prospective freeze")
    if learning_loop is not None:
        errors.extend(
            f"learning loop schema: {error.message}"
            for error in validator.evolve(schema=load_json(LEARNING_LOOP_SCHEMA_PATH)).iter_errors(learning_loop)
        )
        learning_controls = learning_loop.get("controls", {})
        if any(
            learning_controls.get(key) is not False
            for key in (
                "current_g3_changed",
                "empirical_execution_authorized",
                "payload_authorized_by_learning",
                "automatic_promotion",
            )
        ):
            errors.append("learning-loop G3, execution, payload, and promotion controls must remain false")
        if learning_controls.get("negative_results_retained") is not True:
            errors.append("learning loop must retain negative and non-estimable results")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(
        load_json(PLAN_PATH),
        load_json(SCHEMA_PATH),
        load_json(ROUTES_PATH),
        load_json(ASSIGNMENTS_PATH),
        load_json(SAP_PATH),
        load_json(MODEL_TIER_PATH),
        load_json(LEARNING_LOOP_PATH),
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Translation source utilisation plan validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
