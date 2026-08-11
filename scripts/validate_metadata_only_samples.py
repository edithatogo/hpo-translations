"""Validate approved metadata-only ontology samples without reading payloads."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TRACKS = ROOT / "conductor" / "tracks"
APPROVED_STATUS = "approved_bounded_metadata_only_sample"
PHASE2_STATUS = "metadata_only_sample_normalized_payload_free"
PHASE4_STATUS = "metadata_only_sample_validated_payload_blocked"
PHASE4_SAMPLE_VALIDATION = (
    "metadata_only_normalized_identifier_and_provenance_check_passed_import_dry_run_not_applicable_without_terms"
)
APPROVAL_DECISION_PREFIX = "Approve bounded metadata-only samples"
APPROVAL_DECISION_BLOCK = "keep labels, crosswalks, and downstream promotion blocked"
APPROVAL_SCOPE = "one-record metadata-only sample; no source-term redistribution"


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def validate_approval_contract(handoff: dict[str, Any]) -> list[str]:
    """Validate the bounded metadata-only decision without inferring broader authority."""
    approval = handoff.get("approval")
    if not isinstance(approval, dict) or not approval:
        return ["handoff lacks structured approval evidence"]

    errors: list[str] = []
    decision = approval.get("decision")
    if (
        not isinstance(decision, str)
        or not decision.startswith(APPROVAL_DECISION_PREFIX)
        or APPROVAL_DECISION_BLOCK not in decision
    ):
        errors.append("handoff approval decision does not preserve the bounded metadata-only scope")
    if approval.get("scope") != APPROVAL_SCOPE:
        errors.append("handoff approval scope is not the approved payload-free one-record contract")

    approved_at = approval.get("approved_at")
    prepared_at = handoff.get("prepared_at")
    try:
        approval_date = date.fromisoformat(approved_at) if isinstance(approved_at, str) else None
        prepared_date = date.fromisoformat(prepared_at) if isinstance(prepared_at, str) else None
    except ValueError:
        approval_date = prepared_date = None
    if approval_date is None or prepared_date is None or approval_date < prepared_date:
        errors.append("handoff approval date is missing, invalid, or predates the prepared contract")
    return errors


def validate_track(track_dir: Path) -> list[str]:
    errors: list[str] = []
    required_paths = {
        "handoff": track_dir / "maintainer_review_handoff.json",
        "Phase 2": track_dir / "phase2_data_access_normalization.json",
        "Phase 4": track_dir / "phase4_validation_review.json",
    }
    missing = [name for name, path in required_paths.items() if not path.is_file()]
    if missing:
        return [f"missing required {name} artifact" for name in missing]
    try:
        handoff = load_json(required_paths["handoff"])
        phase2 = load_json(required_paths["Phase 2"])
        phase4 = load_json(required_paths["Phase 4"])
    except (json.JSONDecodeError, OSError, ValueError) as error:
        return [f"invalid contract artifact: {error}"]
    if handoff.get("status") != APPROVED_STATUS:
        errors.append("handoff is not approved for a bounded metadata-only sample")
    bounded_sample = handoff.get("bounded_sample")
    errors.extend(validate_approval_contract(handoff))
    if not isinstance(bounded_sample, dict) or not bounded_sample:
        errors.append("handoff lacks a structured bounded-sample contract")
    if phase2.get("status") != PHASE2_STATUS:
        errors.append("Phase 2 is not marked payload-free metadata-only normalization")
    sample = phase2.get("sample")
    normalized = phase2.get("normalized_record")
    normalization = phase2.get("normalization")
    if not isinstance(sample, dict) or sample.get("allowed") is not True:
        errors.append("Phase 2 sample is not explicitly allowed")
    if not isinstance(sample, dict) or sample.get("payload_retained") is not False:
        errors.append("Phase 2 sample does not prove payload discard")
    if not isinstance(sample, dict) or sample.get("source_terms_included") is not False:
        errors.append("Phase 2 sample does not exclude source terms")
    if not isinstance(normalized, dict) or normalized.get("payload_retained") is not False:
        errors.append("normalized record does not prove payload discard")
    if not isinstance(normalization, dict) or normalization.get("source_terms_included") is not False:
        errors.append("Phase 2 normalization does not exclude source terms")
    if phase2.get("payload_commit_allowed") is not False:
        errors.append("Phase 2 allows payload commit")
    evidence = handoff.get("evidence")
    identifier = bounded_sample.get("identifier") if isinstance(bounded_sample, dict) else None
    if not isinstance(evidence, dict):
        errors.append("handoff lacks structured release evidence")
    if not isinstance(identifier, str) or not identifier:
        errors.append("handoff bounded sample lacks an identifier")
    if not isinstance(sample, dict) or sample.get("identifier") != identifier:
        errors.append("Phase 2 sample identifier does not match the approved bounded sample")
    if not isinstance(normalized, dict) or normalized.get("identifier") != identifier:
        errors.append("normalized identifier does not match the approved bounded sample")
    if not isinstance(sample, dict) or sample.get("authorization_ref") != "maintainer_review_handoff.json#approval":
        errors.append("Phase 2 sample does not reference its approval evidence")
    if (
        not isinstance(normalized, dict)
        or normalized.get("metadata_evidence_ref") != "maintainer_review_handoff.json#bounded_sample"
    ):
        errors.append("normalized record does not reference its bounded-sample evidence")
    if isinstance(evidence, dict) and isinstance(normalized, dict):
        if normalized.get("release") != evidence.get("release"):
            errors.append("normalized release does not match handoff evidence")
        if normalized.get("immutable_commit") != evidence.get("immutable_commit"):
            errors.append("normalized immutable commit does not match handoff evidence")
    if phase4.get("status") != PHASE4_STATUS:
        errors.append("Phase 4 is not marked as a validated metadata-only sample with payload blocked")
    if phase4.get("sample_validation") != PHASE4_SAMPLE_VALIDATION:
        errors.append("Phase 4 does not record the metadata-only no-op import result")
    if phase4.get("promotion_allowed") is not False:
        errors.append("Phase 4 does not explicitly prohibit promotion")
    if phase4.get("review_required") is not True:
        errors.append("Phase 4 does not require human review")
    excluded = set(phase4.get("excluded_payloads", []))
    if not {"source_labels", "source_synonyms", "source_definitions", "full_responses"}.issubset(excluded):
        errors.append("Phase 4 excluded-payload list is incomplete")
    return errors


def main() -> int:
    track_dirs = []
    for handoff_path in sorted(TRACKS.glob("*/maintainer_review_handoff.json")):
        try:
            handoff = load_json(handoff_path)
        except (json.JSONDecodeError, OSError, ValueError) as artifact_error:
            print(f"{handoff_path.parent.name}: invalid handoff artifact: {artifact_error}", file=sys.stderr)
            return 1
        if handoff.get("status") == APPROVED_STATUS:
            track_dirs.append(handoff_path.parent)
    if not track_dirs:
        print("No approved metadata-only samples found.", file=sys.stderr)
        return 1
    failures = {track.name: validate_track(track) for track in track_dirs}
    failures = {track: errors for track, errors in failures.items() if errors}
    if failures:
        for track, errors in failures.items():
            for error in errors:
                print(f"{track}: {error}", file=sys.stderr)
        return 1
    print(f"Metadata-only sample validation passed: {len(track_dirs)} complete sample(s); no payload terms read.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
