import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

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

    def test_main_rejects_incomplete_approved_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            tracks = Path(temporary_directory)
            track_dir = tracks / "approved_incomplete"
            track_dir.mkdir()
            (track_dir / "maintainer_review_handoff.json").write_text(
                json.dumps(
                    {
                        "status": "approved_bounded_metadata_only_sample",
                        "approval": {},
                        "bounded_sample": {},
                    }
                ),
                encoding="utf-8",
            )
            errors = io.StringIO()
            with patch("scripts.validate_metadata_only_samples.TRACKS", tracks), redirect_stderr(errors):
                self.assertEqual(main(), 1)
            self.assertIn("approved_incomplete: missing required Phase 2 artifact", errors.getvalue())

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

    def test_completed_phase4_plans_have_fail_closed_review_artifacts(self) -> None:
        track_root = Path(__file__).resolve().parents[1] / "conductor" / "tracks"
        for plan_path in sorted(track_root.glob("*/plan.md")):
            plan = plan_path.read_text(encoding="utf-8")
            if "## Phase 4: Validation and Review" not in plan:
                continue
            phase4 = plan.split("## Phase 4: Validation and Review", 1)[1].split("## ", 1)[0]
            if phase4.count("- [x]") < 3:
                continue
            with self.subTest(track=plan_path.parent.name):
                artifact_path = plan_path.parent / "phase4_validation_review.json"
                self.assertTrue(artifact_path.is_file())
                artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
                if artifact.get("status") == "metadata_only_sample_validated_payload_blocked":
                    self.assertEqual(
                        artifact.get("sample_validation"),
                        "metadata_only_normalized_identifier_and_provenance_check_passed_import_dry_run_not_applicable_without_terms",
                    )
                    self.assertIs(artifact.get("review_required"), True)
                if artifact.get("status") == "governance_only_validated_payload_blocked":
                    self.assertEqual(artifact.get("validation_result"), "pass_governance_only")
                    self.assertEqual(artifact.get("payload_validation"), "not_run_no_authorized_payload")
                    self.assertIs(artifact.get("promotion_allowed"), False)
                    self.assertIs(artifact.get("review_required"), True)


if __name__ == "__main__":
    unittest.main()
