from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "research_validation" / "babelnet_linguistic_anchor_plan.json"
SCHEMA_PATH = ROOT / "research_validation" / "babelnet_linguistic_anchor_plan.schema.json"

EXPECTED_TRIGGERS = {
    "snomed_wikidata_material_disagreement",
    "no_eligible_lexical_candidate",
    "descriptive_or_compositional_component",
    "low_calibrated_confidence",
    "unresolved_regional_portuguese",
    "model_tier_material_disagreement",
    "untranslated_structural_component",
}
EXPECTED_CONDITIONS = [
    f"B{i}_{name}"
    for i, name in enumerate(
        (
            "snomed_only",
            "wikidata_only",
            "snomed_plus_wikidata",
            "babelnet_only",
            "baseline_plus_conditional_babelnet",
            "conditional_babelnet_plus_structural_decomposition",
            "lineage_aware_full_system",
        )
    )
]


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(plan: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = [f"schema: {item.message}" for item in Draft202012Validator(schema).iter_errors(plan)]
    if errors:
        return sorted(errors)
    trigger = plan["trigger_policy"]
    if trigger["run_on_every_term"] is not False or set(trigger["triggers"]) != EXPECTED_TRIGGERS:
        errors.append("BabelNet must remain a conditional resolver with the exact governed triggers")
    regional = plan["regional_language_policy"]
    if regional["generic_pt_proves_variant"] is not False or regional["variants_requiring_independent_evidence"] != [
        "pt-BR",
        "pt-PT",
    ]:
        errors.append("generic Portuguese must not establish Brazilian or European Portuguese")
    if plan["prospective_ablation"]["conditions"] != EXPECTED_CONDITIONS:
        errors.append("BabelNet ablation must remain ordered B0 through B6")
    if (
        plan["role"]["independent_vote_by_default"] is not False
        or plan["lineage_policy"]["one_vote_per_independent_evidence_group"] is not True
    ):
        errors.append("BabelNet sources must remain lineage-deduplicated rather than independent by default")
    if (
        plan["sense_selection"]["health_domain_is_feature_not_gate"] is not True
        or plan["sense_selection"]["single_first_result_selection_allowed"] is not False
    ):
        errors.append("sense selection must remain contextual and polysemy-aware")
    if any(value is not False for value in plan["controls"].values()):
        errors.append("BabelNet execution, payload, redistribution, promotion, and freeze controls must remain false")
    return sorted(set(errors))


def main() -> int:
    errors = validation_errors(load_json(PLAN_PATH), load_json(SCHEMA_PATH))
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("BabelNet linguistic-anchor plan validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
