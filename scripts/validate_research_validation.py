"""Validate the payload-safe empirical research contract and its fixtures."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESEARCH_ROOT = ROOT / "research_validation"
EXPECTED_SCHEMA_NAMES = {
    "language_identity_registry",
    "reviewer_decision",
    "run_manifest",
    "source_lineage_record",
    "translation_evaluation_item",
}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def schema_errors(schema: dict[str, Any], instance: Any) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [error.message for error in sorted(validator.iter_errors(instance), key=lambda error: list(error.path))]


def semantic_errors(schema_name: str, instance: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(instance, dict):
        return errors

    if schema_name == "translation_evaluation_item":
        hard_negatives = instance.get("hard_negative_hpo_ids", [])
        if instance.get("hpo_id") in hard_negatives:
            errors.append("the target HPO identifier cannot also be a hard negative")

    if schema_name == "run_manifest":
        empirical_count = instance.get("empirical_record_count")
        reviewed_count = instance.get("human_reviewed_record_count")
        if isinstance(empirical_count, int) and isinstance(reviewed_count, int) and reviewed_count > empirical_count:
            errors.append("human_reviewed_record_count cannot exceed empirical_record_count")

        if instance.get("release_scope") != "schema_probe":
            approvals = instance.get("approvals", {})
            if isinstance(approvals, dict) and any(value in {"pending", "rejected"} for value in approvals.values()):
                errors.append("pilot and confirmatory runs require approved or not-required approval states")

    return errors


def validate_contract(research_root: Path = DEFAULT_RESEARCH_ROOT) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    schema_dir = research_root / "schemas"
    passing_dir = research_root / "fixtures" / "passing"
    failing_dir = research_root / "fixtures" / "failing"

    schemas = {path.name.removesuffix(".schema.json"): load_json(path) for path in schema_dir.glob("*.schema.json")}
    missing_schemas = EXPECTED_SCHEMA_NAMES - schemas.keys()
    extra_schemas = schemas.keys() - EXPECTED_SCHEMA_NAMES
    for name in sorted(missing_schemas):
        issues.append(ValidationIssue("schema.missing", str(schema_dir), f"missing schema: {name}"))
    for name in sorted(extra_schemas):
        issues.append(ValidationIssue("schema.unexpected", str(schema_dir), f"unexpected schema: {name}"))

    for name, schema in sorted(schemas.items()):
        schema_path = schema_dir / f"{name}.schema.json"
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as error:  # jsonschema exposes several schema-error subclasses
            issues.append(ValidationIssue("schema.invalid", str(schema_path), str(error)))
            continue

        passing_path = passing_dir / f"{name}.json"
        failing_path = failing_dir / f"{name}.json"
        if not passing_path.exists():
            issues.append(ValidationIssue("fixture.passing.missing", str(passing_path), "passing fixture is required"))
        else:
            passing_instance = load_json(passing_path)
            errors = schema_errors(schema, passing_instance) + semantic_errors(name, passing_instance)
            for message in errors:
                issues.append(ValidationIssue("fixture.passing.rejected", str(passing_path), message))

        if not failing_path.exists():
            issues.append(
                ValidationIssue("fixture.failing.missing", str(failing_path), "expected-failure fixture is required")
            )
        else:
            failing_instance = load_json(failing_path)
            errors = schema_errors(schema, failing_instance) + semantic_errors(name, failing_instance)
            if not errors:
                issues.append(
                    ValidationIssue("fixture.failing.accepted", str(failing_path), "expected-failure fixture passed")
                )

    registry_path = research_root / "language_identity_registry.json"
    registry_schema = schemas.get("language_identity_registry")
    if registry_schema is not None:
        if not registry_path.exists():
            issues.append(ValidationIssue("registry.missing", str(registry_path), "canonical registry is required"))
        else:
            registry = load_json(registry_path)
            for message in schema_errors(registry_schema, registry):
                issues.append(ValidationIssue("registry.invalid", str(registry_path), message))

    probe_path = passing_dir / "translation_evaluation_item.json"
    if probe_path.exists():
        probe = load_json(probe_path)
        if len(probe.get("hard_negative_hpo_ids", [])) < 1:
            issues.append(
                ValidationIssue("probe.hard_negative.missing", str(probe_path), "one hard negative is required")
            )
        if len(probe.get("independent_evidence_groups", [])) < 2:
            issues.append(
                ValidationIssue(
                    "probe.independent_evidence_groups.insufficient", str(probe_path), "two groups are required"
                )
            )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-root", type=Path, default=DEFAULT_RESEARCH_ROOT)
    args = parser.parse_args()

    issues = validate_contract(args.research_root)
    if issues:
        print(f"Research validation contract failed with {len(issues)} issue(s):")
        for issue in issues:
            print(f"- [{issue.code}] {issue.path}: {issue.message}")
        return 1

    print("Research validation contract passed: 5 schemas, 5 passing fixtures, and 5 expected failures.")
    print("This result validates the contract only; it does not establish empirical translation readiness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
