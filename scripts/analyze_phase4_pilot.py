"""Frozen payload-safe descriptive analysis for the Option B feasibility pilot."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ANALYSIS_VERSION = "phase4-option-b-analysis-v1"
ALLOWED_DECISIONS = {"accept_without_edit", "accept_with_edit", "reject", "abstain"}


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return (0.0, 0.0)
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def analyze(records: list[dict[str, Any]]) -> dict[str, Any]:
    strata: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        decision = record.get("decision")
        if decision not in ALLOWED_DECISIONS:
            raise ValueError(f"invalid decision: {decision}")
        language = str(record.get("language"))
        condition = str(record.get("candidate_condition"))
        if language not in {"es", "ja"}:
            raise ValueError(f"language outside frozen design: {language}")
        strata[(language, condition)].append(record)

    summaries: list[dict[str, Any]] = []
    for (language, condition), values in sorted(strata.items()):
        counts = Counter(str(value["decision"]) for value in values)
        accepted = counts["accept_without_edit"] + counts["accept_with_edit"]
        lower, upper = wilson_interval(accepted, len(values))
        summaries.append(
            {
                "language": language,
                "candidate_condition": condition,
                "decision_counts": dict(sorted(counts.items())),
                "denominator": len(values),
                "accepted": accepted,
                "acceptance_rate": accepted / len(values),
                "acceptance_wilson_95": [lower, upper],
                "clinically_significant_error_count": sum(
                    value.get("clinically_significant_error") is True for value in values
                ),
                "abstention_count": counts["abstain"],
            }
        )
    return {
        "analysis_version": ANALYSIS_VERSION,
        "record_count": len(records),
        "strata": summaries,
        "claims_boundary": (
            "descriptive_feasibility_only_no_effectiveness_superiority_human_community_or_clinical_validation_claim"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    records = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line]
    args.output.write_text(json.dumps(analyze(records), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
