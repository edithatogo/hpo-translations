"""Validate the payload-safe empirical research contract and its fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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
        source_text = instance.get("source_text")
        source_text_sha256 = instance.get("source_text_sha256")
        if isinstance(source_text, str) and isinstance(source_text_sha256, str):
            computed_sha256 = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
            if source_text_sha256 != computed_sha256:
                errors.append("source_text_sha256 does not match source_text")

    if schema_name == "run_manifest":
        empirical_count = instance.get("empirical_record_count")
        reviewed_count = instance.get("human_reviewed_record_count")
        if isinstance(empirical_count, int) and isinstance(reviewed_count, int) and reviewed_count > empirical_count:
            errors.append("human_reviewed_record_count cannot exceed empirical_record_count")

        if instance.get("release_scope") != "schema_probe":
            approvals = instance.get("approvals", {})
            if isinstance(approvals, dict) and any(value in {"pending", "rejected"} for value in approvals.values()):
                errors.append("pilot and confirmatory runs require approved or not-required approval states")
            for field in ("sampling_code_commit", "analysis_code_commit"):
                if not re.fullmatch(r"[0-9a-f]{7,40}", str(instance.get(field, ""))):
                    errors.append(f"{field} must be a Git commit for pilot and confirmatory runs")

        source_versions = instance.get("source_versions", {})
        source_retrieval_dates = instance.get("source_retrieval_dates", {})
        if (
            isinstance(source_versions, dict)
            and isinstance(source_retrieval_dates, dict)
            and source_versions.keys() != source_retrieval_dates.keys()
        ):
            errors.append("source_versions and source_retrieval_dates must name the same sources")

    if schema_name == "reviewer_decision":
        if instance.get("clinically_significant_error") and not instance.get("error_categories"):
            errors.append("a clinically significant error requires at least one error category")
        selected_hpo_id = instance.get("selected_hpo_id")
        discrimination_correct = instance.get("ontology_discrimination_correct")
        if (selected_hpo_id is None) != (discrimination_correct is None):
            errors.append("ontology discrimination identifier and result must be recorded together")
        if instance.get("conflict_status") == "recused" and instance.get("decision") != "abstain":
            errors.append("a recused reviewer must abstain")

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

        lineage_schema = schemas.get("source_lineage_record")
        manifest_path = passing_dir / "run_manifest.json"
        manifest = load_json(manifest_path) if manifest_path.exists() else {}
        probe_run_id = probe.get("run_id")
        if probe_run_id != manifest.get("run_id"):
            issues.append(
                ValidationIssue(
                    "probe.run_id.mismatch", str(probe_path), "benchmark item is not linked to its manifest"
                )
            )
        lineage_paths = [
            passing_dir / "source_lineage_record.json",
            passing_dir / "source_lineage_record_b.json",
        ]
        evidence_groups: dict[str, str] = {}
        for lineage_path in lineage_paths:
            if not lineage_path.exists():
                issues.append(
                    ValidationIssue(
                        "probe.source_lineage.missing", str(lineage_path), "probe lineage record is required"
                    )
                )
                continue
            lineage_record = load_json(lineage_path)
            if lineage_schema is not None:
                for message in schema_errors(lineage_schema, lineage_record):
                    issues.append(ValidationIssue("probe.source_lineage.invalid", str(lineage_path), message))
            if isinstance(lineage_record, dict):
                if lineage_record.get("run_id") != probe_run_id:
                    issues.append(
                        ValidationIssue(
                            "probe.source_lineage.run_id.mismatch",
                            str(lineage_path),
                            "source lineage record is not linked to the probe run",
                        )
                    )
                evidence_id = lineage_record.get("evidence_id")
                evidence_group = lineage_record.get("independent_evidence_group")
                if isinstance(evidence_id, str) and isinstance(evidence_group, str):
                    evidence_groups[evidence_id] = evidence_group
                source_id = lineage_record.get("source_id")
                manifest_source_versions = manifest.get("source_versions", {})
                if isinstance(source_id, str) and source_id not in manifest_source_versions:
                    issues.append(
                        ValidationIssue(
                            "probe.source_lineage.source_version.missing",
                            str(lineage_path),
                            "source lineage record has no pinned version in the run manifest",
                        )
                    )

        probe_evidence_ids = probe.get("evidence_ids", [])
        missing_evidence_ids = set(probe_evidence_ids) - evidence_groups.keys()
        if missing_evidence_ids:
            issues.append(
                ValidationIssue(
                    "probe.source_lineage.unresolved",
                    str(probe_path),
                    f"missing lineage for evidence IDs: {sorted(missing_evidence_ids)}",
                )
            )
        else:
            linked_groups = {evidence_groups[evidence_id] for evidence_id in probe_evidence_ids}
            if linked_groups != set(probe.get("independent_evidence_groups", [])):
                issues.append(
                    ValidationIssue(
                        "probe.independent_evidence_groups.mismatch",
                        str(probe_path),
                        "item groups do not match the linked source-lineage records",
                    )
                )

        reviewer_path = passing_dir / "reviewer_decision.json"
        if reviewer_path.exists():
            reviewer_decision = load_json(reviewer_path)
            reviewer_run_mismatch = reviewer_decision.get("run_id") != probe_run_id
            reviewer_item_mismatch = reviewer_decision.get("item_id") != probe.get("item_id")
            if reviewer_run_mismatch or reviewer_item_mismatch:
                issues.append(
                    ValidationIssue(
                        "probe.reviewer_decision.link.mismatch",
                        str(reviewer_path),
                        "reviewer decision is not linked to the probe run and item",
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

    print("Research validation contract passed: 5 schemas, 6 passing fixtures, and 5 expected failures.")
    print("This result validates the contract only; it does not establish empirical translation readiness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
