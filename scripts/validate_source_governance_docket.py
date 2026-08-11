"""Validate the source authority/licence decision docket."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOCKET = ROOT / "conductor" / "source_governance_decision_docket.json"
PACKETS = ROOT / "conductor" / "source_governance_approval_packets.json"
TRACKS = {
    "do_integration_20260623",
    "fma_integration_20260623",
    "icd10_integration_20260623",
    "lddb_integration_20260623",
    "loinc_integration_20260623",
    "mesh_integration_20260623",
    "mp_integration_20260623",
    "orphanet_integration_20260623",
    "pato_integration_20260623",
    "upheno_integration_20260623",
}


def main() -> int:
    try:
        docket: dict[str, Any] = json.loads(DOCKET.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"invalid source governance docket: {error}", file=sys.stderr)
        return 1
    errors: list[str] = []
    policy = docket.get("policy")
    if not isinstance(policy, dict) or policy.get("no_approval_granted") is not True:
        errors.append("docket must remain explicitly non-approving")
    if not isinstance(policy, dict) or policy.get("metadata_only_default") is not True:
        errors.append("metadata-only must remain the default")
    options = docket.get("decision_options")
    option_ids = {item.get("id") for item in options if isinstance(item, dict)} if isinstance(options, list) else set()
    if option_ids != {"A", "B", "C"}:
        errors.append("decision options A, B, and C are required")
    tracks = docket.get("tracks")
    if not isinstance(tracks, list) or {item.get("track_id") for item in tracks if isinstance(item, dict)} != TRACKS:
        errors.append("docket track set does not match pending ontology tracks")
    for item in tracks if isinstance(tracks, list) else []:
        if not isinstance(item, dict):
            errors.append("track decision must be an object")
            continue
        required_keys = (
            "track_id",
            "authority",
            "licence",
            "recommended_option",
            "recommendation",
            "maintainer_gate",
            "contingency",
            "decision_state",
        )
        for key in required_keys:
            if not item.get(key):
                errors.append(f"{item.get('track_id', '<unknown>')}: missing {key}")
        if item.get("recommended_option") not in {"A", "B", "C"}:
            errors.append(f"{item.get('track_id', '<unknown>')}: invalid recommended option")
        for gate in ("authority", "licence"):
            if not isinstance(item.get(gate), dict) or not item[gate].get("status"):
                errors.append(f"{item.get('track_id', '<unknown>')}: incomplete {gate} evidence")
    try:
        packets: dict[str, Any] = json.loads(PACKETS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"invalid approval packet set: {error}")
        packets = {}
    if packets.get("dispatch_status") != "prepared_unsent":
        errors.append("approval packet set must remain prepared and unsent")
    if packets.get("external_contact_authorized") is not False:
        errors.append("approval packet set must not authorize external contact")
    packet_rows = packets.get("packets")
    if not isinstance(packet_rows, list) or {row.get("track_id") for row in packet_rows if isinstance(row, dict)} != {
        "do_integration_20260623",
        "loinc_integration_20260623",
        "mesh_integration_20260623",
        "mp_integration_20260623",
        "orphanet_integration_20260623",
        "pato_integration_20260623",
    }:
        errors.append("approval packet set does not match recommended Option A tracks")
    for row in packet_rows if isinstance(packet_rows, list) else []:
        if not isinstance(row, dict):
            errors.append("approval packet must be an object")
            continue
        for key in ("packet_id", "track_id", "scope", "approval_questions", "blocked_outputs", "contingency"):
            if not row.get(key):
                errors.append(f"{row.get('track_id', '<unknown>')}: approval packet missing {key}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Source governance docket validation passed: {len(tracks)} tracks; no approvals inferred.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
