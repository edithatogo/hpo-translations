import copy
import json
import shutil
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.run_stage0_rehearsal import (
    DEFAULT_STAGE0_ROOT,
    build_receipt,
    build_review_packet,
    load_json,
    progression_action,
    public_packet_is_blinded,
    public_packet_is_redacted,
    validate_stage0_artifacts,
)


class Stage0RehearsalTests(unittest.TestCase):
    def test_committed_rehearsal_passes(self) -> None:
        self.assertEqual(validate_stage0_artifacts(), [])

    def test_receipt_counts_and_checks_are_deterministic(self) -> None:
        receipt = build_receipt()
        self.assertEqual(receipt, load_json(DEFAULT_STAGE0_ROOT / "receipt.json"))
        self.assertEqual(receipt["counts"]["synthetic_items"], 12)
        self.assertEqual(receipt["counts"]["blinded_candidate_rows"], 48)
        self.assertEqual(receipt["counts"]["synthetic_assignments"], 144)
        self.assertEqual(receipt["counts"]["synthetic_decisions"], 144)
        self.assertEqual(receipt["counts"]["adjudicated_candidates"], 24)
        self.assertTrue(all(receipt["checks"].values()))

    def test_public_packet_is_blinded_and_redacted(self) -> None:
        plan = load_json(DEFAULT_STAGE0_ROOT / "rehearsal.json")
        packet = build_review_packet(plan)
        self.assertTrue(public_packet_is_blinded(packet))
        self.assertTrue(public_packet_is_redacted(packet))
        self.assertNotIn("method_code", json.dumps(packet))

    def test_real_hpo_identifier_is_rejected(self) -> None:
        with self.mutated_research_root() as root:
            path = root / "stage_0" / "rehearsal.json"
            plan = load_json(path)
            plan["items"][0]["synthetic_concept_id"] = "HP:0001250"
            path.write_text(json.dumps(plan), encoding="utf-8")
            codes = {issue.code for issue in validate_stage0_artifacts(root / "stage_0")}
            self.assertIn("plan.schema", codes)
            self.assertIn("real_hpo_id.present", codes)

    def test_external_action_is_rejected(self) -> None:
        with self.mutated_research_root() as root:
            path = root / "stage_0" / "rehearsal.json"
            plan = load_json(path)
            plan["external_actions_performed"] = ["external-registration"]
            path.write_text(json.dumps(plan), encoding="utf-8")
            codes = {issue.code for issue in validate_stage0_artifacts(root / "stage_0")}
            self.assertIn("plan.schema", codes)

    def test_stop_condition_reclassification_is_rejected(self) -> None:
        with self.mutated_research_root() as root:
            path = root / "stage_0" / "rehearsal.json"
            plan = load_json(path)
            plan["stop_condition_scenarios"][0]["expected_action"] = "stop"
            path.write_text(json.dumps(plan), encoding="utf-8")
            codes = {issue.code for issue in validate_stage0_artifacts(root / "stage_0")}
            self.assertIn("stop_conditions.mismatch", codes)

    def test_progression_threshold_boundaries(self) -> None:
        plan = load_json(DEFAULT_STAGE0_ROOT / "rehearsal.json")
        successful = copy.deepcopy(plan["stop_condition_scenarios"][0])
        self.assertEqual(progression_action(successful), "go")
        successful["review_completion_percent"] = 89.9
        self.assertEqual(progression_action(successful), "revise")
        successful["review_completion_percent"] = 95
        successful["technical_invalidity_percent"] = 20
        self.assertEqual(progression_action(successful), "revise")
        successful["technical_invalidity_percent"] = 20.1
        self.assertEqual(progression_action(successful), "stop")

    def test_stale_receipt_is_rejected(self) -> None:
        with self.mutated_research_root() as root:
            path = root / "stage_0" / "receipt.json"
            receipt = load_json(path)
            receipt["counts"]["synthetic_items"] = 11
            path.write_text(json.dumps(receipt), encoding="utf-8")
            codes = {issue.code for issue in validate_stage0_artifacts(root / "stage_0")}
            self.assertIn("receipt.mismatch", codes)

    @staticmethod
    @contextmanager
    def mutated_research_root() -> Iterator[Path]:
        with TemporaryDirectory() as directory:
            source_root = DEFAULT_STAGE0_ROOT.parent
            target_root = Path(directory) / "research_validation"
            shutil.copytree(source_root, target_root)
            yield target_root
