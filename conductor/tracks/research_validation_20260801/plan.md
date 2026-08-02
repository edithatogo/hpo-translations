# Plan - Establish Empirical Validation for Multilingual HPO Translation

## Phase 0: Dependency, Blocker, Source, and Automation Gates

- [x] **Task 1:** Populate the blocker registry and assign owners.
- [~] **Task 2:** Pin the HPO release and every source release selected for the pilot; complete source access, license, credential, source-authority, language, and version checks. HPO `v2026-06-23`, the four official mapping families, and public supplementary release candidates are reviewed; the final pilot source set, DeCS version, provider permissions, credentials, and human license decisions remain open. (`3ff429e`, review fix `e410f47`, `f3a9584`)
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

- [x] **Task 1:** Ingest metadata for official HPO SSSOM mappings before generating new crosswalks. (`3ff429e`)
- [x] **Task 2:** Classify each source by semantic role, authority, active-language overlap, license feasibility, update cadence, and expected reviewer burden. Completed for the official HPO mapping source set. (`3ff429e`)
- [~] **Task 3:** Populate derivation paths, shared-lineage clusters, and independent-evidence groups at the originating source-atom level. Metadata-level lineage is complete; source-atom ingestion remains blocked on payload and license approval. (`3ff429e`)
- [x] **Task 4:** Add DeCS, Mondo, PRO-CTCAE, WHO ICF, NCIt/NCI dictionaries, RadLex, and structural ontologies only after source-specific access review. Nine metadata-only decisions now cover these sources; no payload was retrieved or cleared. (`f3a9584`)
- [x] **Task 5:** Demonstrate that mirrors and aggregator-derived labels do not increase independent source counts. Four mapping families resolve to three conservative independent-evidence groups; HP–MeSH and HP–UMLS share a MedGen origin. (`3ff429e`, review fix `e410f47`)
- [x] **Task 6:** Phase Verification & Checkpoint (Refer to workflow.md). Review completed with no blocking implementation findings; 45 tests and the research, ontology-network, Conductor, type, format, lint, and prose gates pass. Payload and authority gates remain open. (`f3a9584`)

## Phase 4: Prospectively Frozen Feasibility Pilot

- [x] **Task 1:** Record the maintainer's G0 decision: Option A is selected as the target, Option D as the immediate route, the language-selection rule and progression defaults are accepted, and the provisional 30-hour Stage 1 / 120-hour full-pilot capacity envelope is recorded. Approval gates remain pending and empirical work stays blocked. (`4bfcb2b`, `2a74f58`)
- [x] **Task 2:** Run the 12-item, payload-free synthetic Stage 0 rehearsal for sampling, randomization, artifact-level blinding, export, adjudication, redaction, and stop-condition handling. The deterministic receipt records 48 blinded candidate rows, 144 synthetic assignments and decisions, 24 adjudications, and calculated go/revise/stop branches; it supports operational-readiness claims only. (`4bfcb2b`, refinement `fdc3068`, review fix `eb8df7b`)
- [~] **Task 3:** Prepare the metadata-only language, reviewer-role, source-pathway, and contingency matrix. Spanish and Japanese are planning preferences, the community-governed slot remains unassigned, and `tw` is excluded. Permitted selection, named roster, payload-authorized source set, and stratified concept freeze remain blocked on G1/G2 approvals. (`da81298`)
- [~] **Task 4:** Close source, license, ethics, privacy, reviewer-consent, language-working-group, and community model-use gates. The G1/G2 docket, action pack, receipt template, and live route review are prepared. Conditional internal-use recommendations now cover Mondo, WHO ICF, Uberon, and PATO, but record no human licence decision or payload authority. PRO-CTCAE and DeCS remain externally blocked on sender identity. All approvals and payload access remain pending. (`5e8ff7f`, `8070f4d`, `176e7e2`, `8d0ca96`)
- [~] **Task 5:** Prepare, then freeze and checksum, candidate conditions, prompts, model endpoints, source versions, randomization, exclusions, instrument, progression criteria, and analysis code. The deterministic G3 readiness contract is prepared but explicitly not frozen; its approval counts, authority state, and G1/G2 decisions are reconciled against canonical inputs and fail closed on drift. A 12-component inventory now records each intended freeze artifact, planning source, readiness state, and blocker with zero hashes or ready components. G1/G2 evidence and explicit maintainer approval remain prerequisites to a separate freeze receipt and any external preregistration. (`12c6ad6`, reconciliation `639b2ce`)
- [ ] **Task 6:** Run blinded independent review and adjudication for the first 12 authorized concept-language units, balanced across approved languages and including at least two common anchors where the design is multilingual, then apply the frozen go, revise, or stop rule without testing candidate-method superiority.
- [ ] **Task 7:** If Stage 1 passes, complete the remaining authorized sample. If it enters the revise branch, amend prospectively once and retain a feasibility-only interpretation; if it stops, preserve the failure evidence and do not replace it with a post hoc design.
- [ ] **Task 8:** Estimate review completeness, technical-invalidity rate, workload, abstention, reviewer and concept variance, clinically significant error prevalence, measurement reliability, and the full-study sample size with 95% uncertainty intervals and no formal effectiveness hypothesis tests.
- [ ] **Task 9:** Produce a payload-safe report with deviations and design-specific claim limits, then obtain the maintainer's go, revise, or stop decision for Phase 5.
- [ ] **Task 10:** Phase Verification & Checkpoint (Refer to workflow.md). Confirm that external preregistration, publication, push, and PR gates remain explicit.

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

## Phase 3 Metadata Review Fixes

- [x] **Task:** Require shared-origin summaries to identify their exact source members and independent-evidence group. (`e410f47`)

## Phase 4 Stage 0 Review Fixes

- [x] **Task:** Calculate progression outcomes from numeric feasibility inputs, test the 90% completion and 20% invalidity boundaries, and limit the blinding claim to the reviewer-facing artifact. (`eb8df7b`)
