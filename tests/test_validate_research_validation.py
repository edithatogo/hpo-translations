import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_research_validation import (
    DEFAULT_RESEARCH_ROOT,
    load_json,
    phase_4_candidate_matrix_errors,
    phase_4_decision_receipt_template_errors,
    phase_4_g1_internal_scope_review_errors,
    phase_4_g1_route_review_errors,
    phase_4_g3_component_inventory_errors,
    phase_4_g3_freeze_readiness_errors,
    phase_4_g3_freeze_receipt_template_errors,
    phase_4_gate_docket_errors,
    phase_4_wave_1_source_decisions_errors,
    phase_4_wave_2_authority_routes_errors,
    pilot_source_readiness_errors,
    private_source_archive_receipts_errors,
    reviewer_workload_budget_errors,
    schema_errors,
    semantic_errors,
    validate_contract,
)


class ValidateResearchValidationTests(unittest.TestCase):
    def test_committed_contract_passes(self) -> None:
        self.assertEqual(validate_contract(), [])

    def test_private_archive_receipts_reject_revision_drift(self) -> None:
        receipts = load_json(DEFAULT_RESEARCH_ROOT / "source_archive_receipts.json")
        inventory = load_json(DEFAULT_RESEARCH_ROOT.parent / "conductor" / "source_hosting_inventory.json")
        receipts["archive_revision"] = "0" * 40
        self.assertIn(
            "private archive target and revision must match the canonical hosting inventory",
            private_source_archive_receipts_errors(receipts, inventory),
        )

    def test_private_archive_receipts_reject_payload_authority(self) -> None:
        receipts = load_json(DEFAULT_RESEARCH_ROOT / "source_archive_receipts.json")
        inventory = load_json(DEFAULT_RESEARCH_ROOT.parent / "conductor" / "source_hosting_inventory.json")
        receipts["authorization_boundary"]["payload_retrieval_authorized"] = True
        self.assertIn(
            "private archive receipts must not authorize source, payload, empirical, or promotion actions",
            private_source_archive_receipts_errors(receipts, inventory),
        )

    def test_private_archive_receipts_reject_false_lineage(self) -> None:
        receipts = load_json(DEFAULT_RESEARCH_ROOT / "source_archive_receipts.json")
        inventory = load_json(DEFAULT_RESEARCH_ROOT.parent / "conductor" / "source_hosting_inventory.json")
        receipts["lineage_state"]["independent_evidence_groups_added"] = 4
        self.assertIn(
            "private archive receipts must not claim source-atom lineage or evidence independence",
            private_source_archive_receipts_errors(receipts, inventory),
        )

    def test_private_archive_receipts_reject_inventory_coverage_drift(self) -> None:
        receipts = load_json(DEFAULT_RESEARCH_ROOT / "source_archive_receipts.json")
        inventory = load_json(DEFAULT_RESEARCH_ROOT.parent / "conductor" / "source_hosting_inventory.json")
        inventory["sources"].append(
            {
                "source_id": "new-source",
                "status": "archived_private",
                "release": "v1",
                "archive_path": "releases/new-source/v1/source.obo",
                "sha256": "0" * 64,
            }
        )
        self.assertIn(
            "private archive receipts must cover the complete canonical archived-source inventory",
            private_source_archive_receipts_errors(receipts, inventory),
        )

    def _pilot_source_inputs(self) -> tuple[dict, dict, dict, dict, dict]:
        return (
            load_json(DEFAULT_RESEARCH_ROOT / "pilot_source_readiness.json"),
            load_json(DEFAULT_RESEARCH_ROOT / "source_catalog.json"),
            load_json(DEFAULT_RESEARCH_ROOT / "supplementary_source_access_reviews.json"),
            load_json(DEFAULT_RESEARCH_ROOT / "source_archive_receipts.json"),
            load_json(DEFAULT_RESEARCH_ROOT / "approval_manifest.json"),
        )

    def test_pilot_source_readiness_rejects_false_selection(self) -> None:
        readiness, catalog, supplementary, receipts, approval = self._pilot_source_inputs()
        readiness["decision_state"]["final_pilot_source_set_selected"] = True
        self.assertIn(
            "pilot source readiness must not select sources or claim payload, lineage, or G1 readiness",
            pilot_source_readiness_errors(readiness, catalog, supplementary, receipts, approval),
        )

    def test_pilot_source_readiness_rejects_archive_double_count(self) -> None:
        readiness, catalog, supplementary, receipts, approval = self._pilot_source_inputs()
        readiness["overlap_controls"].pop()
        self.assertIn(
            "pilot source readiness must preserve PATO, MP, and uPheno overlap controls",
            pilot_source_readiness_errors(readiness, catalog, supplementary, receipts, approval),
        )

    def test_pilot_source_readiness_rejects_count_drift(self) -> None:
        readiness, catalog, supplementary, receipts, approval = self._pilot_source_inputs()
        readiness["evidence_layers"][0]["record_count"] += 1
        self.assertIn(
            "official_hpo_mapping_families readiness count must match its canonical input",
            pilot_source_readiness_errors(readiness, catalog, supplementary, receipts, approval),
        )

    def test_pilot_source_readiness_rejects_overlap_layer_drift(self) -> None:
        readiness, catalog, supplementary, receipts, approval = self._pilot_source_inputs()
        readiness["overlap_controls"][0]["appears_in"] = ["owner_only_archive_receipts"]
        self.assertIn(
            "pato overlap control must name its exact canonical evidence layers",
            pilot_source_readiness_errors(readiness, catalog, supplementary, receipts, approval),
        )

    def test_pilot_source_readiness_rejects_canonical_input_drift(self) -> None:
        readiness, catalog, supplementary, receipts, approval = self._pilot_source_inputs()
        readiness["canonical_inputs"]["approval_manifest"] = "research_validation/alternate.json"
        self.assertIn(
            "pilot source readiness must reference every canonical input by its exact repository path",
            pilot_source_readiness_errors(readiness, catalog, supplementary, receipts, approval),
        )

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

    def test_gate_docket_rejects_authorization(self) -> None:
        docket = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_gate_docket.json")
        supplementary = load_json(DEFAULT_RESEARCH_ROOT / "supplementary_source_access_reviews.json")
        approval = load_json(DEFAULT_RESEARCH_ROOT / "approval_manifest.json")
        docket["authorization_boundary"]["external_contact_authorized"] = True
        self.assertIn(
            "all Phase 4 gate-docket authorization fields must remain false",
            phase_4_gate_docket_errors(docket, supplementary, approval),
        )

    def test_gate_docket_rejects_tw(self) -> None:
        docket = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_gate_docket.json")
        supplementary = load_json(DEFAULT_RESEARCH_ROOT / "supplementary_source_access_reviews.json")
        approval = load_json(DEFAULT_RESEARCH_ROOT / "approval_manifest.json")
        docket["decision_packets"][0]["linked_language_ids"].append("tw")
        self.assertIn(
            "decision packet contains an unresolved or inactive language profile",
            phase_4_gate_docket_errors(docket, supplementary, approval),
        )

    def test_gate_docket_rejects_unrecorded_approval(self) -> None:
        docket = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_gate_docket.json")
        supplementary = load_json(DEFAULT_RESEARCH_ROOT / "supplementary_source_access_reviews.json")
        approval = load_json(DEFAULT_RESEARCH_ROOT / "approval_manifest.json")
        docket["decision_packets"][0]["decision"] = "approved"
        self.assertIn(
            "decision packet state must match the recorded Wave 1 evidence and pending gate set",
            phase_4_gate_docket_errors(docket, supplementary, approval),
        )

    def test_gate_docket_rejects_recommendation_drift(self) -> None:
        docket = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_gate_docket.json")
        supplementary = load_json(DEFAULT_RESEARCH_ROOT / "supplementary_source_access_reviews.json")
        approval = load_json(DEFAULT_RESEARCH_ROOT / "approval_manifest.json")
        docket["blocker_resolution_plan"]["options"].reverse()
        self.assertIn(
            "Phase 4 blocker options must preserve the recommended B-to-A dual-lane order",
            phase_4_gate_docket_errors(docket, supplementary, approval),
        )

    def test_gate_docket_rejects_subagent_approval_authority(self) -> None:
        docket = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_gate_docket.json")
        supplementary = load_json(DEFAULT_RESEARCH_ROOT / "supplementary_source_access_reviews.json")
        approval = load_json(DEFAULT_RESEARCH_ROOT / "approval_manifest.json")
        docket["blocker_resolution_plan"]["accountability_boundary"]["advisory_subagent_panel_must_not"].remove(
            "authorize_payload_retrieval"
        )
        self.assertIn(
            "advisory subagents must not receive accountable approval or payload authority",
            phase_4_gate_docket_errors(docket, supplementary, approval),
        )

    def test_gate_docket_private_archive_does_not_authorize_payload(self) -> None:
        docket = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_gate_docket.json")
        supplementary = load_json(DEFAULT_RESEARCH_ROOT / "supplementary_source_access_reviews.json")
        approval = load_json(DEFAULT_RESEARCH_ROOT / "approval_manifest.json")
        docket["private_storage_readiness"]["payload_upload_authorized"] = True
        self.assertIn(
            "private storage infrastructure must not imply source, payload, human, or freeze authority",
            phase_4_gate_docket_errors(docket, supplementary, approval),
        )

    def test_gate_docket_private_archive_retains_source_permission_gate(self) -> None:
        docket = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_gate_docket.json")
        supplementary = load_json(DEFAULT_RESEARCH_ROOT / "supplementary_source_access_reviews.json")
        approval = load_json(DEFAULT_RESEARCH_ROOT / "approval_manifest.json")
        docket["private_storage_readiness"]["required_before_use"].remove(
            "source_specific_rightsholder_permission_or_licence_scope_for_private_cloud_hosting"
        )
        self.assertIn(
            "private storage readiness must retain permission, custody, and maintainer action gates",
            phase_4_gate_docket_errors(docket, supplementary, approval),
        )

    def test_decision_receipt_template_rejects_approval(self) -> None:
        receipt = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_decision_receipt.template.json")
        receipt["decision"] = "approved"
        self.assertIn(
            "decision receipt must remain an unexecuted pending template",
            phase_4_decision_receipt_template_errors(receipt),
        )

    def test_decision_receipt_template_rejects_identity(self) -> None:
        receipt = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_decision_receipt.template.json")
        receipt["approver_pseudonym"] = "reviewer-001"
        self.assertIn(
            "decision receipt template field approver_pseudonym must remain null",
            phase_4_decision_receipt_template_errors(receipt),
        )

    def test_decision_receipt_template_rejects_downstream_authority(self) -> None:
        receipt = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_decision_receipt.template.json")
        receipt["reviewer_contact_allowed"] = True
        self.assertIn(
            "decision receipt template must not authorize downstream actions",
            phase_4_decision_receipt_template_errors(receipt),
        )

    def test_g1_route_review_rejects_false_dispatch(self) -> None:
        review = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g1_route_review.json")
        review["dispatch_completed_count"] = 1
        self.assertIn(
            "G1 route review must record zero completed dispatches",
            phase_4_g1_route_review_errors(review),
        )

    def test_g1_route_review_rejects_payload_authority(self) -> None:
        review = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g1_route_review.json")
        review["authorization_boundary"]["source_payload_retrieval_authorized"] = True
        self.assertTrue(
            any("prohibited downstream authority" in error for error in phase_4_g1_route_review_errors(review))
        )

    def test_g1_route_review_rejects_missing_source(self) -> None:
        review = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g1_route_review.json")
        review["routes"].pop()
        self.assertIn(
            "G1 route review must cover each authorized source exactly once",
            phase_4_g1_route_review_errors(review),
        )

    def test_internal_scope_review_rejects_payload_authority(self) -> None:
        review = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g1_internal_scope_review.json")
        review["source_reviews"][0]["payload_retrieval_allowed"] = True
        self.assertIn(
            "Wave 1 internal scope decisions must not authorize payload retrieval",
            phase_4_g1_internal_scope_review_errors(review),
        )

    def test_internal_scope_review_rejects_closed_gate(self) -> None:
        review = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g1_internal_scope_review.json")
        review["program_decision"]["source_licence_gate_closed"] = True
        self.assertIn(
            "Wave 1 must be complete while the overall source licence gate remains open",
            phase_4_g1_internal_scope_review_errors(review),
        )

    def test_wave_1_source_decisions_reject_evidence_hash_drift(self) -> None:
        decisions = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_wave_1_source_decisions.json")
        decisions["decisions"][0]["evidence"]["assertion"] += " changed"
        self.assertIn(
            "Wave 1 evidence assertion hash must match its payload-safe assertion",
            phase_4_wave_1_source_decisions_errors(decisions),
        )

    def test_wave_1_source_decisions_reject_payload_authority(self) -> None:
        decisions = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_wave_1_source_decisions.json")
        decisions["decisions"][0]["payload_retrieval_allowed"] = True
        self.assertIn(
            "Wave 1 source decisions must not authorize payload retrieval or promotion",
            phase_4_wave_1_source_decisions_errors(decisions),
        )

    def test_wave_1_source_decisions_preserve_who_no_derivatives(self) -> None:
        decisions = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_wave_1_source_decisions.json")
        who = next(item for item in decisions["decisions"] if item["source_id"] == "who-icf")
        who["prohibited_or_deferred"].remove("mapping_or_transformative_use")
        self.assertIn(
            "WHO ICF Wave 1 scope must prohibit adaptation, mapping, and modified distribution",
            phase_4_wave_1_source_decisions_errors(decisions),
        )

    def test_wave_2_authority_routes_reject_premature_sponsor_selection(self) -> None:
        routes = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_wave_2_authority_routes.json")
        routes["sponsor_route_selection"]["decision"] = "approved"
        routes["sponsor_route_selection"]["selected_route_id"] = "flinders_sponsored"
        self.assertIn(
            "Wave 2 must preserve three unselected sponsor routes pending an accountable choice",
            phase_4_wave_2_authority_routes_errors(routes),
        )

    def test_wave_2_authority_routes_reject_dispatch_authority(self) -> None:
        routes = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_wave_2_authority_routes.json")
        routes["request_packets"][0]["dispatch_authorized"] = True
        self.assertIn(
            "Wave 2 request packets must remain pending, unsent, and without receipts",
            phase_4_wave_2_authority_routes_errors(routes),
        )

    def test_wave_2_authority_routes_reject_identity_leak(self) -> None:
        routes = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_wave_2_authority_routes.json")
        routes["sender_email"] = "person@example.org"
        self.assertIn(
            "Wave 2 Git artifact must not contain email addresses",
            phase_4_wave_2_authority_routes_errors(routes),
        )

    def test_wave_2_authority_routes_preserve_ethics_route_hold(self) -> None:
        routes = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_wave_2_authority_routes.json")
        ethics = next(item for item in routes["request_packets"] if item["packet_id"] == "g2-ethics-privacy")
        ethics["dispatch_route"] = "https://example.org/submit"
        self.assertIn(
            "ethics/privacy dispatch must remain unset until sponsor-route selection",
            phase_4_wave_2_authority_routes_errors(routes),
        )

    def test_internal_scope_review_preserves_who_no_derivatives(self) -> None:
        review = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g1_internal_scope_review.json")
        who = next(item for item in review["source_reviews"] if item["source_id"] == "who-icf")
        who["prohibited_or_deferred_roles"].remove("adaptation_of_codes")
        self.assertIn(
            "WHO ICF review must prohibit code adaptation and modified-material distribution",
            phase_4_g1_internal_scope_review_errors(review),
        )

    def test_g3_readiness_rejects_false_freeze(self) -> None:
        readiness = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g3_freeze_readiness.json")
        readiness["status"] = "frozen"
        readiness["freeze_id"] = "premature"
        self.assertIn(
            "G3 readiness must remain explicitly not frozen with no freeze identifier or timestamp",
            phase_4_g3_freeze_readiness_errors(readiness),
        )

    def test_g3_component_inventory_rejects_hash(self) -> None:
        inventory = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g3_component_inventory.json")
        inventory["components"][0]["version_or_hash"] = "sha256:premature"
        self.assertIn(
            "G3 planning inventory must not contain versions or hashes",
            phase_4_g3_component_inventory_errors(inventory),
        )

    def test_g3_component_inventory_rejects_missing_component(self) -> None:
        inventory = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g3_component_inventory.json")
        inventory["components"].pop()
        self.assertIn(
            "G3 component inventory must cover every required component exactly once",
            phase_4_g3_component_inventory_errors(inventory),
        )

    def test_g3_component_inventory_rejects_false_readiness(self) -> None:
        inventory = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g3_component_inventory.json")
        inventory["components"][0]["readiness"] = "ready"
        self.assertIn(
            "G3 component inventory must not claim component freeze readiness",
            phase_4_g3_component_inventory_errors(inventory),
        )

    def test_g3_freeze_receipt_template_rejects_false_execution(self) -> None:
        receipt = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g3_freeze_receipt.template.json")
        receipt["execution_state"] = "prospective_frozen"
        self.assertIn(
            "G3 freeze receipt must remain an unexecuted not-frozen template",
            phase_4_g3_freeze_receipt_template_errors(receipt),
        )

    def test_g3_freeze_receipt_template_rejects_hash(self) -> None:
        receipt = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g3_freeze_receipt.template.json")
        receipt["aggregate_freeze_manifest_sha256"] = "sha256:premature"
        self.assertIn(
            "G3 freeze receipt template field aggregate_freeze_manifest_sha256 must remain null",
            phase_4_g3_freeze_receipt_template_errors(receipt),
        )

    def test_g3_freeze_receipt_template_rejects_preregistration(self) -> None:
        receipt = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g3_freeze_receipt.template.json")
        receipt["external_registration"]["authorized"] = True
        self.assertIn(
            "G3 freeze receipt template must not record external registration",
            phase_4_g3_freeze_receipt_template_errors(receipt),
        )

    def test_g3_readiness_rejects_premature_checksum(self) -> None:
        readiness = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g3_freeze_readiness.json")
        readiness["checksum_contract"]["recorded_checksum_count"] = 1
        self.assertIn(
            "G3 readiness must not record checksums before the prospective freeze",
            phase_4_g3_freeze_readiness_errors(readiness),
        )

    def test_g3_readiness_rejects_downstream_authority(self) -> None:
        readiness = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g3_freeze_readiness.json")
        readiness["authorization_boundary"]["start_empirical_work"] = True
        self.assertIn(
            "all G3 readiness authorization fields must remain false", phase_4_g3_freeze_readiness_errors(readiness)
        )

    def test_g3_readiness_rejects_candidate_matrix_drift(self) -> None:
        readiness = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g3_freeze_readiness.json")
        matrix = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_candidate_matrix.json")
        matrix["approved_language_count"] = 1
        self.assertIn(
            "G3 readiness approval counts must match the canonical candidate matrix",
            phase_4_g3_freeze_readiness_errors(readiness, matrix),
        )

    def test_g3_readiness_rejects_approval_manifest_drift(self) -> None:
        readiness = load_json(DEFAULT_RESEARCH_ROOT / "phase_4_g3_freeze_readiness.json")
        approval = load_json(DEFAULT_RESEARCH_ROOT / "approval_manifest.json")
        approval["gates"][4]["decision"] = "approved"
        self.assertIn(
            "G3 readiness G1 state must match the canonical source-licence decision",
            phase_4_g3_freeze_readiness_errors(readiness, approval_manifest=approval),
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
