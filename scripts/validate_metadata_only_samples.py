"""Validate approved metadata-only ontology samples without reading payloads."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TRACKS = ROOT / "conductor" / "tracks"
APPROVED_STATUS = "approved_bounded_metadata_only_sample"
PHASE2_STATUS = "metadata_only_sample_normalized_payload_free"
PHASE4_SAMPLE_VALIDATION = (
    "metadata_only_normalized_identifier_and_provenance_check_passed_import_dry_run_not_applicable_without_terms"
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


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
    if phase2.get("status") != PHASE2_STATUS:
        errors.append("Phase 2 is not marked payload-free metadata-only normalization")
    sample = phase2.get("sample")
    normalized = phase2.get("normalized_record")
    if not isinstance(sample, dict) or sample.get("allowed") is not True:
        errors.append("Phase 2 sample is not explicitly allowed")
    if not isinstance(sample, dict) or sample.get("payload_retained") is not False:
        errors.append("Phase 2 sample does not prove payload discard")
    if not isinstance(sample, dict) or sample.get("source_terms_included") is not False:
        errors.append("Phase 2 sample does not exclude source terms")
    if not isinstance(normalized, dict) or normalized.get("payload_retained") is not False:
        errors.append("normalized record does not prove payload discard")
    if phase2.get("payload_commit_allowed") is not False:
        errors.append("Phase 2 allows payload commit")
    if phase4.get("sample_validation") != PHASE4_SAMPLE_VALIDATION:
        errors.append("Phase 4 does not record the metadata-only no-op import result")
    excluded = set(phase4.get("excluded_payloads", []))
    if not {"source_labels", "source_synonyms", "source_definitions", "full_responses"}.issubset(excluded):
        errors.append("Phase 4 excluded-payload list is incomplete")
    return errors


def main() -> int:
    track_dirs = []
    skipped = []
    for handoff_path in sorted(TRACKS.glob("*/maintainer_review_handoff.json")):
        handoff = load_json(handoff_path)
        if (
            handoff.get("status") == APPROVED_STATUS
            and isinstance(handoff.get("approval"), dict)
            and isinstance(handoff.get("bounded_sample"), dict)
        ):
            track_dir = handoff_path.parent
            required = [
                track_dir / "phase2_data_access_normalization.json",
                track_dir / "phase4_validation_review.json",
            ]
            if all(path.exists() for path in required):
                track_dirs.append(track_dir)
            else:
                skipped.append(track_dir.name)
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
    suffix = f"; incomplete handoffs skipped: {', '.join(skipped)}" if skipped else ""
    print(
        f"Metadata-only sample validation passed: {len(track_dirs)} complete sample(s); no payload terms read{suffix}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
