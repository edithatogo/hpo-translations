# Plan - Establish Empirical Validation for Multilingual HPO Translation

## Phase 0: Dependency, Blocker, Source, and Automation Gates

- [x] **Task 1:** Populate the blocker registry and assign owners.
- [~] **Task 2:** Pin the HPO release and every source release selected for the pilot; complete source access, licence, source-authority, language, and version checks. The exact minimum payload set is now selected and content-addressed as the existing Spanish and Japanese Babelon snapshots in `research_validation/pilot_source_payload_manifest.json`. Local read and ephemeral processing are authorized only after each language/community-use gate closes. DeCS and every supplementary, mapping-catalog, credentialed, click-through, or restricted source payload are omitted; their unresolved permission/version evidence is no longer on the Option B critical path. Source-atom lineage for any future external source and current-release alignment claims remain blocked. (`3ff429e`, review fix `e410f47`, `f3a9584`, current continuation)
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

- [x] **Task 1:** Define schemas for benchmark items, source lineage, agent decisions, language identity, and run manifests. (`57f8816`, review fix `9412ef3`)
- [x] **Task 2:** Add passing and expected-failure fixtures for every schema. (`57f8816`, review fix `9412ef3`)
- [x] **Task 3:** Define the sampling frame, hard-negative construction, error taxonomy, blinding, agent qualifications, adjudication, and statistical analysis. (`57f8816`)
- [x] **Task 4:** Define primary outcomes: clinically significant error rate, no-edit acceptance, edit burden, agent time, ontology-discrimination accuracy, and calibration. (`57f8816`, review fix `9412ef3`)
- [x] **Task 5:** Define secondary outcomes for labels, definitions, synonyms, regional variants, patient-facing terms, and downstream tasks. (`57f8816`)
- [x] **Task 6:** Run schema, fixture, lint, and documentation validation. (`9412ef3`)
- [x] **Task 7:** Phase Verification & Checkpoint (Refer to workflow.md). Review completed with linked lineage, checksum, outcome, and frozen-run fixes applied. (`9412ef3`)

## Phase 3: Source Provenance and Dependence

- [x] **Task 1:** Ingest metadata for official HPO SSSOM mappings before generating new crosswalks. (`3ff429e`)
- [x] **Task 2:** Classify each source by semantic role, authority, active-language overlap, license feasibility, update cadence, and expected agent burden. Completed for the official HPO mapping source set. (`3ff429e`)
- [x] **Task 3:** Populate derivation paths, shared-lineage clusters, and independent-evidence groups at the originating source-atom level for the selected payload set. Generated 37,800 payload-safe atoms from the two authorized repository snapshots: 19,932 Spanish and 17,868 Japanese. No source or translation text is retained. Both snapshots conservatively share one independent-evidence group because repository/HPO provenance does not establish independent votes. External and restricted sources remain omitted. (`3ff429e`, current continuation)
- [x] **Task 4:** Add DeCS, Mondo, PRO-CTCAE, WHO ICF, NCIt/NCI dictionaries, RadLex, and structural ontologies only after source-specific access review. Nine metadata-only decisions now cover these sources; no payload was retrieved or cleared. (`f3a9584`)
- [x] **Task 5:** Demonstrate that mirrors and aggregator-derived labels do not increase independent source counts. Four mapping families resolve to three conservative independent-evidence groups; HP–MeSH and HP–UMLS share a MedGen origin. (`3ff429e`, review fix `e410f47`)
- [x] **Task 6:** Phase Verification & Checkpoint (Refer to workflow.md). Review completed with no blocking implementation findings; 45 tests and the research, ontology-network, Conductor, type, format, lint, and prose gates pass. Payload and authority gates remain open. (`f3a9584`)

## Phase 4: Prospectively Frozen Feasibility Pilot

- [x] **Task 1:** Record the maintainer's revised G0 decision: Option B is the selected minimum viable pilot with Spanish and Japanese, Option D remains the immediate permitted route, the language-selection rule and progression defaults are accepted, and the provisional 30-hour Stage 1 / 120-hour full-pilot capacity envelope is retained. Source, language/community-use, privacy, and freeze gates remain pending and empirical work stays blocked. (`4bfcb2b`, `2a74f58`, current continuation)
- [x] **Task 2:** Run the 12-item, payload-free synthetic Stage 0 rehearsal for sampling, randomization, artifact-level blinding, export, adjudication, redaction, and stop-condition handling. The deterministic receipt records 48 blinded candidate rows, 144 synthetic assignments and decisions, 24 adjudications, and calculated go/revise/stop branches; it supports operational-readiness claims only. (`4bfcb2b`, refinement `fdc3068`, review fix `eb8df7b`)
- [x] **Task 3:** Prepare the metadata-only language, agent-role, source-pathway, and contingency matrix. Spanish and Japanese are selected for Option B but remain unapproved for empirical use; the third community-governed slot is removed. The unresolved `tw` profile is canonically excluded from every study stage, source match, fallback, analysis, and claim without renaming or inferring its identity. Stratified concept freeze remains blocked on the applicable G2 approvals. (`da81298`, current continuation)
- [~] **Task 4:** Close source, licence, ethics, privacy, agent-execution, language-working-group, and community model-use gates. The bounded pilot payload-set decision is complete for the two existing content-addressed Spanish/Japanese repository snapshots; it authorizes no external retrieval and excludes DeCS and all other external/restricted payloads. Spanish, Japanese, and ethics/privacy decisions remain pending and unsent, so agent execution, empirical work, and promotion remain blocked. (`5e8ff7f`, `8070f4d`, `176e7e2`, `8d0ca96`, blocker plan `b4f31f7`, Wave 1 `7881787`, Wave 2 `9953018`, routing receipt `68be472`, current continuation)
- [x] **Task 5:** Freeze and checksum candidate conditions, prompts, model endpoints, source versions, sampling, randomization, aggregation, exclusions, the specialist-agent instrument, progression criteria, approval/privacy controls, and analysis code. Freeze `g3-option-b-es-ja-20260812-v1` binds 13 immutable components for the 50-concept/60-unit Spanish–Japanese Option B design. The prospective design is frozen, but empirical execution and external preregistration remain prohibited pending Spanish/Japanese community-use and ethics/privacy decisions; any component drift requires a new freeze identifier.
- [ ] **Task 6:** Run five context-isolated specialist agent assessments and independent agent adjudication for the first 12 authorized concept-language units, balanced across approved languages and including at least two common anchors where the design is multilingual, then reproduce the deterministic aggregation and apply the frozen go, revise, or stop rule without testing candidate-method superiority. Do not recruit people or describe the result as human, community, or clinical validation.
- [ ] **Task 7:** If Stage 1 passes, complete the remaining authorized sample. If it enters the revise branch, amend prospectively once and retain a feasibility-only interpretation; if it stops, preserve the failure evidence and do not replace it with a post hoc design.
- [ ] **Task 8:** Estimate review completeness, technical-invalidity rate, workload, abstention, agent and concept variance, clinically significant error prevalence, measurement reliability, and the full-study sample size with 95% uncertainty intervals and no formal effectiveness hypothesis tests.
- [~] **Task 9:** Produce a payload-safe report with deviations and design-specific claim limits, then obtain the maintainer's go, revise, or stop decision for Phase 5. An interim blocked-state report now records the G3 evidence, zero empirical records, unresolved G2 gates, non-evaluable progression decision, and prohibited claims; the empirical report and Phase 5 decision remain pending.
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

- [x] **Task 1:** Run `conductor-review` for the full track and treat findings as blocking work. Review found incomplete archive-inventory coverage enforcement, weak overlap-layer binding, stale lifecycle evidence, and repository-wide formatting/type failures; fixes were applied without changing any accountable gate. (`30cc5a2`)
- [x] **Task 2:** Rerun validation and record review, telemetry, unresolved blockers, and local-only artifact changes. At exact reviewed head `913cbda`, research, Conductor, ontology-network, 122-test, Ruff, and the then-current typing gate passed, and all 14 translation profiles passed when run in bounded parallel batches. Sequential `pixi run qc` exceeded 30 minutes because individual profiles took approximately 68–311 seconds; this is a runtime limitation, not a profile failure. At the later reviewed local head, 123 tests and all non-translation gates pass. No restricted local-only artifact was read or committed. (`30cc5a2`, review receipts `913cbda`, `8c572c0`)
- [ ] **Task 3:** Obtain explicit maintainer approval before push, PR creation, preregistration, publication, or release.
- [x] **Task 4:** Verify required GitHub checks and merge state before marking the track complete. Clean PR #4 head `ae022d0` passed both QC events and Docs validation, was squash-merged as `91271dc`, and the exact merged `main` commit passed QC run `31508681793` and Docs run `31508681654`. This infrastructure gate does not complete or archive the track while accountable and empirical tasks remain open.
- [~] **Task 5:** Record downstream handoff to language working groups and ontology maintainers. A payload-safe ontology-maintainer handoff now records `hold_no_promotion`, safe artifacts, mutation rules, and evidence required before any future release. Language-working-group handoff remains blocked until an authorized G2 route and sender exist.
- [ ] **Task 6:** Phase Verification & Checkpoint (Refer to workflow.md).

## Phase 1-2 Review Fixes

- [x] **Task:** Apply review suggestions for fixture integrity, linked source lineage, frozen run metadata, agent conflicts, edit burden, and ontology-discrimination outcomes. (`9412ef3`)

## Phase 3 Metadata Review Fixes

- [x] **Task:** Require shared-origin summaries to identify their exact source members and independent-evidence group. (`e410f47`)

## Phase 4 Stage 0 Review Fixes

- [x] **Task:** Calculate progression outcomes from numeric feasibility inputs, test the 90% completion and 20% invalidity boundaries, and limit the blinding claim to the agent-facing artifact. (`eb8df7b`)

## Local Closeout Review Fixes

- [x] **Task:** Authorize the PR audit workflow to post its translation-diff receipt and ignore local Entire session metadata. (`b6d5332`)

## Current Continuation Review Fixes

- [x] **Task:** Define and validate how existing HPO translations, multilingual terminology editions, disease/context mappings, structural ontologies, and lineage-preserving aggregators may support candidate generation, triangulation, conflict detection, semantic discrimination, regional-variant analysis, source ablation, drift prioritization, and downstream evaluation. The plan is prospective and metadata-only; all 42 mapping assertions remain payload-blocked, the Spanish/Japanese G3 freeze is unchanged, and new empirical inputs require a new freeze. (current continuation)
- [x] **Task:** Operationalize the utilisation plan with 15 source-specific assignments and a prespecified statistical contract covering exact denominators, paired small-sample models, missingness, multiplicity, integer Stage 1 thresholds, end-to-end lineage ablations, temporal validation, active-learning comparison, cost, lexical normalization, mapping ambiguity, selection bias, and explicit non-estimability. These contracts do not amend G3 or authorize payload use. (current continuation)

- [x] **Task:** Apply track-review fixes for complete archive-receipt coverage, exact overlap-layer reconciliation, canonical-input binding, and current lifecycle evidence. (`30cc5a2`)
- [x] **Task:** Remove the credentialed archive workflow's automatic push trigger, restore per-source release pins, prevent complete authenticated metadata responses from entering future uploaded receipts, and enforce manual dispatch with regression validation. A concurrent hosted push run had already executed before this fix; no new external action was authorized or performed during this review. (`8c572c0`)
- [x] **Task:** Supersede the planned people-based evaluation and adjudication pathway with the canonical isolated specialist-agent panel in `research_validation/agent_review_panel.json`. Preserve source rights, community-use constraints, prospective freeze, and maintainer release authority as non-review gates; prohibit human-validation claims. (current continuation)
- [x] **Task:** Reconcile schemas, fixtures, G2 packets, compute budgets, Stage 0 artifacts, prose, and validators to the canonical seven-agent panel; withdraw the obsolete expression-of-interest pathway and preserve zero people-based translation review. (current continuation)
- [x] **Task:** Rebuild the locked Pixi environment and pass exact `pixi run qc` across all 14 translation profiles in 38 minutes 31 seconds. Audit hosted run `31471912686`: only the LOINC receipt has a complete authenticated-response sink in the pre-fix helper; private content verification is blocked by dataset read scope and remote remediation remains unauthorized. (current continuation)
- [x] **Task:** Rebase the research continuation onto the squash-merged governance baseline without restoring the deleted credentialed archive workflow or receipt artifact. Replace archive-receipt coupling with the fail-closed source-hosting inventory, canonicalize payload hashing across Windows line endings, enforce LF for the immutable G3 JSON package, regenerate its complete checksum chain, and pass focused admission. (clean-branch merge-blocker repair)

### Review outcome

The governance and validation continuation is locally admitted, but the track is not complete or archive-eligible. Applicable language/community-use and ethics/privacy constraints, Stage 1 agent-panel evaluation, the full pilot, confirmatory studies, downstream delivery, explicit publication approval, current-head CI, and merge verification remain outstanding. People-based translation review is not part of the revised design, and the study must not make human-, community-, or clinical-validation claims. The archive audit isolated the presumed affected remote object to `receipts/loinc-2.82-multilingual.json`; content verification and any remote remediation remain blocked pending explicit authority and usable private-dataset scope. Archival must not convert these empirical and accountable gates into completed work.
