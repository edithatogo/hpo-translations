"""Generate payload-safe source atoms for the authorized Option B snapshots."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESEARCH_ROOT = ROOT / "research_validation"
MANIFEST_PATH = RESEARCH_ROOT / "pilot_source_payload_manifest.json"
ATOMS_PATH = RESEARCH_ROOT / "pilot_source_atoms.jsonl.gz"
GROUPS_PATH = RESEARCH_ROOT / "pilot_independent_lineage_groups.json"
INDEPENDENT_GROUP = "hpo-translations-repository-snapshots"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value: dict[str, Any] = json.load(handle)
    return value


def generate() -> tuple[int, str]:
    manifest = load_json(MANIFEST_PATH)
    atom_count = 0
    source_counts: dict[str, int] = {}
    output_lines: list[str] = []

    for payload in manifest["payloads"]:
        source_id = str(payload["source_id"])
        language = str(payload["language"])
        source_path = ROOT / str(payload["path"])
        source_bytes = source_path.read_bytes()
        source_digest = sha256_bytes(source_bytes)
        if source_digest != payload["sha256"]:
            raise ValueError(f"authorized payload hash drifted: {payload['path']}")

        with source_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            required = {"subject_id", "predicate_id", "source_value", "translation_value"}
            if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                raise ValueError(f"authorized payload has unexpected columns: {payload['path']}")
            for data_row_number, row in enumerate(reader, start=1):
                canonical_payload_row = "\t".join(str(row.get(field, "")) for field in reader.fieldnames)
                row_digest = sha256_bytes(canonical_payload_row.encode("utf-8"))
                atom_seed = f"{source_id}\0{data_row_number}\0{row_digest}".encode()
                atom = {
                    "schema_version": "pilot-source-atom-v1",
                    "source_atom_id": f"atom-{sha256_bytes(atom_seed)}",
                    "source_id": source_id,
                    "language": language,
                    "subject_id": row["subject_id"],
                    "predicate_id": row["predicate_id"],
                    "designation_role": "preferred" if row["predicate_id"] == "rdfs:label" else "not_applicable",
                    "source_snapshot_sha256": source_digest,
                    "source_data_row_number": data_row_number,
                    "source_row_sha256": row_digest,
                    "derivation_path": [str(payload["path"]), f"data-row-{data_row_number}"],
                    "shared_lineage_cluster": f"{source_id}-content-addressed-snapshot",
                    "independent_evidence_group": INDEPENDENT_GROUP,
                    "payload_text_retained": False,
                    "empirical_use_authorized": False,
                }
                output_lines.append(json.dumps(atom, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
                atom_count += 1
                source_counts[source_id] = source_counts.get(source_id, 0) + 1

    atoms_payload = ("\n".join(output_lines) + "\n").encode("utf-8")
    compressed_atoms = gzip.compress(atoms_payload, compresslevel=9, mtime=0)
    ATOMS_PATH.write_bytes(compressed_atoms)
    atoms_digest = sha256_bytes(compressed_atoms)
    groups = {
        "schema_version": "pilot-independent-lineage-groups-v1",
        "track_id": manifest["track_id"],
        "source_atom_artifact": "research_validation/pilot_source_atoms.jsonl.gz",
        "source_atom_artifact_sha256": atoms_digest,
        "source_atom_count": atom_count,
        "source_atom_counts": source_counts,
        "groups": [
            {
                "independent_evidence_group": INDEPENDENT_GROUP,
                "member_source_ids": sorted(source_counts),
                "independent_vote_count": 1,
                "rationale": (
                    "Both language snapshots share the HPO translations repository provenance boundary; "
                    "no evidence supports treating them as independent votes."
                ),
            }
        ],
        "independent_evidence_group_count": 1,
        "payload_text_retained": False,
        "empirical_use_authorized": False,
        "claims_boundary": (
            "lineage_inventory_only_no_translation_text_independent_language_authority_empirical_or_promotion_claim"
        ),
    }
    GROUPS_PATH.write_text(json.dumps(groups, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return atom_count, atoms_digest


def main() -> int:
    atom_count, digest = generate()
    print(f"Generated {atom_count} payload-safe source atoms; sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
