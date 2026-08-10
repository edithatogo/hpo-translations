import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_metadata_only_samples import main, validate_track


class MetadataOnlySampleTests(unittest.TestCase):
    def test_approved_samples_are_payload_free(self) -> None:
        self.assertEqual(main(), 0)

    def test_incomplete_contract_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            track_dir = Path(temporary_directory)
            (track_dir / "maintainer_review_handoff.json").write_text(
                json.dumps({"status": "approved_bounded_metadata_only_sample"}),
                encoding="utf-8",
            )
            self.assertEqual(
                validate_track(track_dir),
                ["missing required Phase 2 artifact", "missing required Phase 4 artifact"],
            )

    def test_phase3_translation_use_artifacts_fail_closed(self) -> None:
        track_root = Path(__file__).resolve().parents[1] / "conductor" / "tracks"
        phase3_paths = sorted(track_root.glob("*/phase3_hpo_translation_use.json"))
        self.assertGreater(len(phase3_paths), 0)
        for phase3_path in phase3_paths:
            with self.subTest(track=phase3_path.parent.name):
                phase3 = json.loads(phase3_path.read_text(encoding="utf-8"))
                if "rules" in phase3:
                    rules = set(phase3["rules"])
                    self.assertIs(phase3.get("promotion_allowed"), False)
                    self.assertIn("llm_candidates_require_human_review", rules)
                    if "exact_identifier_only" in rules:
                        self.assertIn("conflicts_unresolved_by_default", rules)
                        self.assertIn("emit_candidate_conflict_records", rules)
                elif "llm_guardrails" in phase3:
                    guardrails = phase3.get("llm_guardrails", {})
                    self.assertIs(guardrails.get("candidate_only"), True)
                    self.assertIs(guardrails.get("human_review_required"), True)
                    self.assertIs(guardrails.get("approved_translation"), False)
                    self.assertEqual(
                        phase3.get("conflict_reporting", {}).get("default_resolution"),
                        "unresolved_until_human_review",
                    )
                else:
                    self.assertTrue(phase3.get("deterministic_matching_rules"))
                    self.assertTrue(phase3.get("conflict_reporting"))
                    self.assertEqual(
                        phase3["conflict_reporting"].get("default_resolution"),
                        "unresolved_until_human_review",
                    )
                    guardrails = phase3.get("llm_guardrails", {})
                    self.assertIs(guardrails.get("candidate_only"), True)
                    self.assertIs(guardrails.get("human_review_required"), True)
                    self.assertIs(guardrails.get("approved_translation"), False)

    def test_completed_phase3_plans_have_contract_artifacts(self) -> None:
        track_root = Path(__file__).resolve().parents[1] / "conductor" / "tracks"
        for plan_path in sorted(track_root.glob("*/plan.md")):
            plan = plan_path.read_text(encoding="utf-8")
            if "## Phase 3: HPO Translation Use" not in plan:
                continue
            phase3 = plan.split("## Phase 3: HPO Translation Use", 1)[1].split("## Phase 4:", 1)[0]
            if phase3.count("- [x]") >= 3:
                with self.subTest(track=plan_path.parent.name):
                    self.assertTrue((plan_path.parent / "phase3_hpo_translation_use.json").is_file())


if __name__ == "__main__":
    unittest.main()
