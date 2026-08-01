# Plan - Establish Empirical Validation for Multilingual HPO Translation

## Phase 0: Dependency, Blocker, Source, and Automation Gates

- [x] **Task 1:** Populate the blocker registry and assign owners.
- [ ] **Task 2:** Pin the HPO release and every source release selected for the pilot; complete source access, license, credential, source-authority, language, and version checks.
- [x] **Task 3:** Define restricted-payload policy, local-only manifest requirements, and the commit allowlist and denylist.
- [x] **Task 4:** Run a fail-fast benchmark fixture containing one HPO concept, one hard negative, and two independently identified evidence groups. (`57f8816`, review fix `9412ef3`)
- [x] **Task 5:** Define the research artifact contract and downstream consumers.
- [x] **Task 6:** Declare priority, write owner, merge owner, and parallelization boundaries.
- [x] **Task 7:** Define local validation commands, commit boundaries, branch, remote, PR target, CI gate, and merge gate; retain push and PR as explicit maintainer gates.
- [x] **Task 8:** Start telemetry for agent, model, runtime, validation, conflicts, and unresolved blockers. (`9412ef3`)
- [x] **Task 9:** Phase Verification & Checkpoint (Refer to workflow.md). Governance and contract work may proceed; empirical ingress remains blocked on Task 2. (`9412ef3`)

## Phase 1: Scientific Readiness Corrections

- [x] **Task 1:** Replace ambiguous overall release readiness with separate governance-scaffold, empirical-artifact, translation-evidence, and source-payload readiness fields. (`dc8c359`)
- [x] **Task 2:** Reframe the archived ontology-network plan as completed scaffolding and hand empirical work to this track. (`dc8c359`)
- [x] **Task 3:** Add a fail-closed language-identity registry and record the unresolved `tw` Tiwi/Twi authority conflict without renaming translation assets. (`dc8c359`)
- [x] **Task 4:** Add tests proving zero empirical records, unpinned inputs, or unresolved language identity cannot be reported as translation-evidence ready. (`dc8c359`)
- [x] **Task 5:** Run local ontology-network and Conductor validation. (`dc8c359`, rerun after `9412ef3`)
- [x] **Task 6:** Phase Verification & Checkpoint (Refer to workflow.md). Review completed with fixes applied; no high or critical findings remain. (`9412ef3`)

## Phase 2: Benchmark and Evaluation Contract

- [x] **Task 1:** Define schemas for benchmark items, source lineage, reviewer decisions, language identity, and run manifests. (`57f8816`, review fix `9412ef3`)
- [x] **Task 2:** Add passing and expected-failure fixtures for every schema. (`57f8816`, review fix `9412ef3`)
- [x] **Task 3:** Define the sampling frame, hard-negative construction, error taxonomy, blinding, reviewer qualifications, adjudication, and statistical analysis. (`57f8816`)
- [x] **Task 4:** Define primary outcomes: clinically significant error rate, no-edit acceptance, edit burden, reviewer time, ontology-discrimination accuracy, and calibration. (`57f8816`, review fix `9412ef3`)
- [x] **Task 5:** Define secondary outcomes for labels, definitions, synonyms, regional variants, patient-facing terms, and downstream tasks. (`57f8816`)
- [x] **Task 6:** Run schema, fixture, lint, and documentation validation. (`9412ef3`)
- [x] **Task 7:** Phase Verification & Checkpoint (Refer to workflow.md). Review completed with linked lineage, checksum, outcome, and frozen-run fixes applied. (`9412ef3`)

## Phase 3: Source Provenance and Dependence

- [ ] **Task 1:** Ingest metadata for official HPO SSSOM mappings before generating new crosswalks.
- [ ] **Task 2:** Classify each source by semantic role, authority, active-language overlap, license feasibility, update cadence, and expected reviewer burden.
- [ ] **Task 3:** Populate derivation paths, shared-lineage clusters, and independent-evidence groups at the originating source-atom level.
- [ ] **Task 4:** Add DeCS, Mondo, PRO-CTCAE, WHO ICF, NCIt/NCI dictionaries, RadLex, and structural ontologies only after source-specific access review.
- [ ] **Task 5:** Demonstrate that mirrors and aggregator-derived labels do not increase independent source counts.
- [ ] **Task 6:** Phase Verification & Checkpoint (Refer to workflow.md).

## Phase 4: Preregistered Pilot

- [ ] **Task 1:** Select 50 to 100 stratified terms across contrasting HPO branches and language situations.
- [ ] **Task 2:** Obtain language-working-group, reviewer, license, ethics, and community approvals required for the selected pilot.
- [ ] **Task 3:** Freeze candidate generators, prompts, source versions, randomization, exclusions, and analysis code.
- [ ] **Task 4:** Run blinded independent review and adjudication.
- [ ] **Task 5:** Estimate reviewer variance, clinically significant error prevalence, effect sizes, and the full-study sample size.
- [ ] **Task 6:** Publish a payload-safe pilot report and decide go, revise, or stop for the full benchmark.
- [ ] **Task 7:** Phase Verification & Checkpoint (Refer to workflow.md).

## Phase 5: Confirmatory and Novel Studies

- [ ] **Task 1:** Run the multilingual candidate-method comparison with prespecified ablations.
- [ ] **Task 2:** Compare naive source voting with lineage-aware evidence aggregation.
- [ ] **Task 3:** Run the ontology-discrimination benchmark with parent, child, and sibling hard negatives.
- [ ] **Task 4:** Evaluate downstream HPO extraction and phenotype-driven ranking where suitable public or approved data exist.
- [ ] **Task 5:** Replay HPO releases for drift prediction and temporal generalization.
- [ ] **Task 6:** Evaluate active-learning queues against random or FIFO review.
- [ ] **Task 7:** Report language, region, script, register, and resource-tier results separately with exact uncertainty intervals.
- [ ] **Task 8:** Phase Verification & Checkpoint (Refer to workflow.md).

## Phase 6: Review, Delivery, and Completion Gates

- [ ] **Task 1:** Run `conductor-review` for the full track and treat findings as blocking work.
- [ ] **Task 2:** Rerun validation and record review, telemetry, unresolved blockers, and local-only artifact changes.
- [ ] **Task 3:** Obtain explicit maintainer approval before push, PR creation, preregistration, publication, or release.
- [ ] **Task 4:** Verify required GitHub checks and merge state before marking the track complete.
- [ ] **Task 5:** Record downstream handoff to language working groups and ontology maintainers.
- [ ] **Task 6:** Phase Verification & Checkpoint (Refer to workflow.md).

## Phase 1-2 Review Fixes

- [x] **Task:** Apply review suggestions for fixture integrity, linked source lineage, frozen run metadata, reviewer conflicts, edit burden, and ontology-discrimination outcomes. (`9412ef3`)
