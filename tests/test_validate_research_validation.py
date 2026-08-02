import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_research_validation import (
    DEFAULT_RESEARCH_ROOT,
    load_json,
    phase_4_candidate_matrix_errors,
    reviewer_workload_budget_errors,
    schema_errors,
    semantic_errors,
    validate_contract,
)


class ValidateResearchValidationTests(unittest.TestCase):
    def test_committed_contract_passes(self) -> None:
        self.assertEqual(validate_contract(), [])

    def test_candidate_matrix_rejects_unresolved_tw(self) -> None:
        matrix = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_candidate_matrix.json")
        supplementary = load_json(DEFAULT_RESEARCH_ROOT / "supplementary_source_access_reviews.json")
        matrix["language_slots"][0]["fallback_languages"].append("tw")
        self.assertIn(
            "unresolved tw must not appear in preferred or fallback language slots",
            phase_4_candidate_matrix_errors(matrix, supplementary),
        )

    def test_candidate_matrix_rejects_approval_without_gate_evidence(self) -> None:
        matrix = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_candidate_matrix.json")
        supplementary = load_json(DEFAULT_RESEARCH_ROOT / "supplementary_source_access_reviews.json")
        matrix["approved_language_count"] = 1
        self.assertIn(
            "Phase 4 planning matrix must record zero approved languages, payloads, and named reviewers",
            phase_4_candidate_matrix_errors(matrix, supplementary),
        )

    def test_candidate_matrix_rejects_named_reviewer_approval(self) -> None:
        matrix = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_candidate_matrix.json")
        supplementary = load_json(DEFAULT_RESEARCH_ROOT / "supplementary_source_access_reviews.json")
        matrix["named_reviewer_count"] = 1
        self.assertTrue(phase_4_candidate_matrix_errors(matrix, supplementary))

    def test_reviewer_budget_must_include_adjudicators(self) -> None:
        budget = load_json(DEFAULT_RESEARCH_ROOT / "reviewer_workload_budget.json")
        budget["design_snapshot"]["planning_reviewer_count"] = 9
        self.assertIn(
            "planning reviewer count must include primary reviewers and independent adjudicators",
            reviewer_workload_budget_errors(budget),
        )

    def test_every_schema_rejects_its_expected_failure(self) -> None:
        schema_dir = DEFAULT_RESEARCH_ROOT / "schemas"
        failing_dir = DEFAULT_RESEARCH_ROOT / "fixtures" / "failing"
        for schema_path in schema_dir.glob("*.schema.json"):
            name = schema_path.name.removesuffix(".schema.json")
            with self.subTest(schema=name):
                schema = load_json(schema_path)
                instance = load_json(failing_dir / f"{name}.json")
                self.assertTrue(schema_errors(schema, instance) + semantic_errors(name, instance))

    def test_target_cannot_be_its_own_hard_negative(self) -> None:
        item = load_json(DEFAULT_RESEARCH_ROOT / "fixtures" / "passing" / "translation_evaluation_item.json")
        item["hard_negative_hpo_ids"] = [item["hpo_id"]]
        self.assertIn(
            "the target HPO identifier cannot also be a hard negative",
            semantic_errors("translation_evaluation_item", item),
        )

    def test_source_text_checksum_must_match(self) -> None:
        item = load_json(DEFAULT_RESEARCH_ROOT / "fixtures" / "passing" / "translation_evaluation_item.json")
        item["source_text"] = "Changed after checksum"
        self.assertIn(
            "source_text_sha256 does not match source_text",
            semantic_errors("translation_evaluation_item", item),
        )

    def test_reviewed_count_cannot_exceed_empirical_count(self) -> None:
        manifest = load_json(DEFAULT_RESEARCH_ROOT / "fixtures" / "passing" / "run_manifest.json")
        manifest["human_reviewed_record_count"] = 1
        self.assertIn(
            "human_reviewed_record_count cannot exceed empirical_record_count",
            semantic_errors("run_manifest", manifest),
        )

    def test_rejected_approval_blocks_empirical_run(self) -> None:
        manifest = load_json(DEFAULT_RESEARCH_ROOT / "fixtures" / "passing" / "run_manifest.json")
        manifest["release_scope"] = "pilot"
        manifest["approvals"]["license"] = "rejected"
        self.assertIn(
            "pilot and confirmatory runs require approved or not-required approval states",
            semantic_errors("run_manifest", manifest),
        )

    def test_run_manifest_source_versions_and_dates_must_align(self) -> None:
        manifest = load_json(DEFAULT_RESEARCH_ROOT / "fixtures" / "passing" / "run_manifest.json")
        manifest["source_retrieval_dates"].pop("synthetic-structural-source")
        self.assertIn(
            "source_versions and source_retrieval_dates must name the same sources",
            semantic_errors("run_manifest", manifest),
        )

    def test_source_catalog_dependence_counts_are_recomputed(self) -> None:
        catalog = load_json(DEFAULT_RESEARCH_ROOT / "source_catalog.json")
        catalog["dependence_summary"]["independent_evidence_group_count"] = 4
        self.assertIn(
            "independent_evidence_group_count must equal the number of unique groups",
            semantic_errors("source_catalog", catalog),
        )

    def test_same_origin_cannot_create_false_independence(self) -> None:
        catalog = load_json(DEFAULT_RESEARCH_ROOT / "fixtures" / "passing" / "source_catalog.json")
        catalog["mappings"][1]["independent_evidence_group"] = "invented-independent-group"
        self.assertIn(
            "records with the same origin_dataset must share one independent evidence group",
            semantic_errors("source_catalog", catalog),
        )

    def test_repeated_origins_must_be_reported(self) -> None:
        catalog = load_json(DEFAULT_RESEARCH_ROOT / "fixtures" / "passing" / "source_catalog.json")
        catalog["dependence_summary"]["shared_origin_groups"] = []
        self.assertIn(
            "shared_origin_groups must enumerate every repeated origin_dataset exactly once",
            semantic_errors("source_catalog", catalog),
        )

    def test_shared_origin_summary_must_name_exact_members_and_group(self) -> None:
        catalog = load_json(DEFAULT_RESEARCH_ROOT / "fixtures" / "passing" / "source_catalog.json")
        summary = catalog["dependence_summary"]["shared_origin_groups"][0]
        summary["members"] = ["fixture-a", "invented-source"]
        summary["independent_evidence_group"] = "invented-independent-group"
        errors = semantic_errors("source_catalog", catalog)
        self.assertIn("shared origin fixture-origin must list its exact source members", errors)
        self.assertIn(
            "shared origin fixture-origin must use its source records' independent evidence group",
            errors,
        )

    def test_versioned_source_cannot_use_latest_alias(self) -> None:
        catalog = load_json(DEFAULT_RESEARCH_ROOT / "fixtures" / "passing" / "source_catalog.json")
        catalog["mappings"][0]["versioned_url"] = "https://example.org/latest/a.tsv"
        self.assertIn(
            "fixture-a versioned_url cannot use a latest alias",
            semantic_errors("source_catalog", catalog),
        )

    def test_supplementary_source_counts_are_recomputed(self) -> None:
        review = load_json(DEFAULT_RESEARCH_ROOT / "supplementary_source_access_reviews.json")
        review["summary"]["metadata_probe_allowed_count"] = 9
        self.assertIn(
            "metadata_probe_allowed_count must equal the recomputed supplementary source count",
            semantic_errors("supplementary_source_access_review", review),
        )

    def test_permission_block_requires_written_provider_gate(self) -> None:
        review = load_json(DEFAULT_RESEARCH_ROOT / "fixtures" / "passing" / "supplementary_source_access_review.json")
        record = review["reviews"][0]
        record["repository_decision"] = "payload_blocked_permission_required"
        self.assertIn(
            "fixture-ontology permission block requires a written-provider gate",
            semantic_errors("supplementary_source_access_review", review),
        )

    def test_unexposed_supplementary_version_cannot_be_claimed(self) -> None:
        review = load_json(DEFAULT_RESEARCH_ROOT / "fixtures" / "passing" / "supplementary_source_access_review.json")
        source_version = review["reviews"][0]["source_version"]
        source_version["status"] = "version_not_exposed_before_access"
        self.assertIn(
            "fixture-ontology cannot claim a version before access",
            semantic_errors("supplementary_source_access_review", review),
        )

    def test_unresolved_language_profile_cannot_be_counted_as_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "research_validation"
            for source in DEFAULT_RESEARCH_ROOT.rglob("*"):
                if source.is_file():
                    destination = root / source.relative_to(DEFAULT_RESEARCH_ROOT)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(source.read_bytes())
            review_path = root / "supplementary_source_access_reviews.json"
            review = load_json(review_path)
            review["reviews"][0]["active_translation_profile_overlap"].append("tw")
            review_path.write_text(json.dumps(review), encoding="utf-8")
            codes = {issue.code for issue in validate_contract(root)}
            self.assertIn("supplementary_source_access_review.language_identity_unresolved", codes)

    def test_canonical_supplementary_source_coverage_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "research_validation"
            for source in DEFAULT_RESEARCH_ROOT.rglob("*"):
                if source.is_file():
                    destination = root / source.relative_to(DEFAULT_RESEARCH_ROOT)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(source.read_bytes())
            review_path = root / "supplementary_source_access_reviews.json"
            review = load_json(review_path)
            review["reviews"].pop()
            review["summary"]["source_count"] -= 1
            review["summary"]["metadata_probe_allowed_count"] -= 1
            review_path.write_text(json.dumps(review), encoding="utf-8")
            codes = {issue.code for issue in validate_contract(root)}
            self.assertIn("supplementary_source_access_review.coverage", codes)

    def test_supplementary_active_profiles_cannot_go_stale(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "research_validation"
            for source in DEFAULT_RESEARCH_ROOT.rglob("*"):
                if source.is_file():
                    destination = root / source.relative_to(DEFAULT_RESEARCH_ROOT)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(source.read_bytes())
            review_path = root / "supplementary_source_access_reviews.json"
            review = load_json(review_path)
            review["active_translation_profiles"].remove("ar")
            review_path.write_text(json.dumps(review), encoding="utf-8")
            codes = {issue.code for issue in validate_contract(root)}
            self.assertIn("supplementary_source_access_review.active_profiles_stale", codes)

    def test_empirical_run_requires_frozen_git_commits(self) -> None:
        manifest = load_json(DEFAULT_RESEARCH_ROOT / "fixtures" / "passing" / "run_manifest.json")
        manifest["release_scope"] = "pilot"
        errors = semantic_errors("run_manifest", manifest)
        self.assertIn("sampling_code_commit must be a Git commit for pilot and confirmatory runs", errors)
        self.assertIn("analysis_code_commit must be a Git commit for pilot and confirmatory runs", errors)

    def test_missing_fixture_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "research_validation"
            for source in DEFAULT_RESEARCH_ROOT.rglob("*"):
                if source.is_file():
                    destination = root / source.relative_to(DEFAULT_RESEARCH_ROOT)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(source.read_bytes())
            (root / "fixtures" / "passing" / "reviewer_decision.json").unlink()
            codes = {issue.code for issue in validate_contract(root)}
            self.assertIn("fixture.passing.missing", codes)

    def test_probe_requires_both_linked_lineage_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "research_validation"
            for source in DEFAULT_RESEARCH_ROOT.rglob("*"):
                if source.is_file():
                    destination = root / source.relative_to(DEFAULT_RESEARCH_ROOT)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(source.read_bytes())
            (root / "fixtures" / "passing" / "source_lineage_record_b.json").unlink()
            codes = {issue.code for issue in validate_contract(root)}
            self.assertIn("probe.source_lineage.missing", codes)
            self.assertIn("probe.source_lineage.unresolved", codes)

    def test_unknown_fields_are_rejected(self) -> None:
        schema = load_json(DEFAULT_RESEARCH_ROOT / "schemas" / "translation_evaluation_item.schema.json")
        item = copy.deepcopy(
            load_json(DEFAULT_RESEARCH_ROOT / "fixtures" / "passing" / "translation_evaluation_item.json")
        )
        item["unreviewed_claim"] = "release ready"
        self.assertTrue(schema_errors(schema, item))

    def test_schema_files_are_json_objects(self) -> None:
        for schema_path in (DEFAULT_RESEARCH_ROOT / "schemas").glob("*.schema.json"):
            with self.subTest(schema=schema_path.name), schema_path.open(encoding="utf-8") as handle:
                self.assertIsInstance(json.load(handle), dict)

    def test_reviewer_workload_budget_arithmetic_passes(self) -> None:
        budget = load_json(DEFAULT_RESEARCH_ROOT / "reviewer_workload_budget.json")
        self.assertEqual(reviewer_workload_budget_errors(budget), [])

    def test_reviewer_workload_budget_rejects_inconsistent_ceiling(self) -> None:
        budget = load_json(DEFAULT_RESEARCH_ROOT / "reviewer_workload_budget.json")
        budget["full_pilot_ceiling"]["ceiling_minutes"] = 7100
        self.assertIn(
            "full-pilot ceiling must equal its workload components",
            reviewer_workload_budget_errors(budget),
        )

    def test_reviewer_workload_budget_rejects_unapproved_ceiling_drift(self) -> None:
        budget = load_json(DEFAULT_RESEARCH_ROOT / "reviewer_workload_budget.json")
        budget["full_pilot_ceiling"]["coordination_and_contingency_minutes"] += 60
        budget["full_pilot_ceiling"]["ceiling_minutes"] += 60
        budget["full_pilot_ceiling"]["ceiling_hours"] = 121
        budget["full_pilot_ceiling"]["remaining_after_stage_1_cap_minutes"] += 60
        budget["full_pilot_ceiling"]["remaining_after_stage_1_cap_hours"] = 91
        self.assertIn(
            "approved Stage 1 and full-pilot workload ceilings cannot drift without amendment",
            reviewer_workload_budget_errors(budget),
        )

    def test_reviewer_workload_budget_cannot_authorize_external_action(self) -> None:
        budget = load_json(DEFAULT_RESEARCH_ROOT / "reviewer_workload_budget.json")
        budget["authorization_boundary"]["reviewer_contact_authorized"] = True
        self.assertIn(
            "capacity planning cannot authorize reviewer, payload, empirical, or external actions",
            reviewer_workload_budget_errors(budget),
        )


if __name__ == "__main__":
    unittest.main()
