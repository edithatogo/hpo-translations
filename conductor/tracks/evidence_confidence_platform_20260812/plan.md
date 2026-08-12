# Implementation Plan: Layered Translation Evidence and Confidence Platform

## Phase 0: Dependency, Blocker, Source, and Automation Gates

- [ ] Task: Populate the blocker registry and assign blocker owners and fallback paths.
- [ ] Task: Complete source access and source_access_status, licence, credential, authority, language and immutable-version checks.
- [ ] Task: Define the restricted_payload policy, commit allowlist, denylist and local-only custody manifests.
- [ ] Task: Run the synthetic fail-fast probe before any bulk implementation.
- [ ] Task: Freeze the artifact contract, schemas, validators, downstream consumers and release-safe outputs.
- [ ] Task: Declare priority, write owner, merge owner and parallelization boundaries for disjoint workstreams.
- [ ] Task: Define local validation, commit boundaries and remote_delivery gates for the fork, GitHub Project, Hugging Face Space, arXiv and upstream handoff.
- [ ] Task: Start agent, model, runtime, validation, conflict and blocker telemetry.
- [ ] Task: Record exact upstream remote, commit, release, fork base and byte hashes for every upstream-controlled translation and validation file.
- [ ] Task: Classify every current repository path as upstream core, compatibility infrastructure, research overlay, restricted local artifact, generated public artifact or proposed handoff.
- [ ] Task: Define a clean upstream-replay branch strategy and prove that regeneration does not modify upstream translation payloads.
- [ ] Task: Inventory source, licence, language/community, ethics/privacy, credential, model and publication blockers without resolving them by inference.
- [ ] Task: Write mutation tests that fail on upstream-core writes, payload leakage, provenance loss, unsafe edition inheritance or AI-to-human reclassification.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md).

## Phase 1: Evidence data model and immutable provenance

- [x] Task: Add and validate the registry-derived source expansion catalogue covering MAxO, HPO association products, CMO/MMO/XCO, ECO/SEPIO, GA4GH standards, multilingual/context candidates, deferred sources and registry deduplication. (`current continuation`)
- [x] Task: Replace GA4GH maturity-based deferral with a relevance-first catalogue in which every retained current, draft, developmental or study-group product has a governed mapping or interoperability path. (`current continuation`)
- [ ] Task: Define LinkML/JSON schemas for translation objects, evidence atoms, lineage groups, mapping assertions, contradictions, assessment records, downstream outcomes and confidence records.
- [ ] Task: Add source-kind and evidence-role vocabularies covering human HPO baseline, independent human terminology, structural/context evidence, model candidates and downstream outcomes.
- [ ] Task: Bind HPO, source, mapping, language-rendition, model, prompt and analysis versions to content hashes.
- [ ] Task: Add ECO/SEPIO-compatible evidence and assertion fields without requiring those ontologies as runtime dependencies.
- [ ] Task: Define append-only event and deviation ledgers for process analysis.
- [ ] Task: Add deterministic validators and expected-failure fixtures before ingestion implementation.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md).

## Phase 2: Upstream-preserving ingestion and source normalization

- [ ] Task: Build read-only adapters for upstream Babelon translations, synonyms and release metadata.
- [ ] Task: Preserve source strings and produce separate normalized comparison forms for Unicode, punctuation, morphology, script and regional analysis.
- [ ] Task: Ingest only authorized external terminology atoms, preserving designation, predicate, edition, rights and origin lineage.
- [ ] Task: Add namespace-aware import detection so translated labels from imported ontologies are not attributed to the container ontology.
- [ ] Task: Produce coverage, exclusion and unavailable-source ledgers with exact denominators.
- [ ] Task: Demonstrate byte-identical upstream core after a complete rebuild.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md).

## Phase 3: Layered candidate-generation experiment

- [ ] Task: Freeze tiny, small, medium and large model endpoints and the model-only, translation-assisted and ontology-assisted arms.
- [ ] Task: Withhold same-item HPO reference translations and dependent lineages from generation.
- [ ] Task: Generate repeated candidates with paired seeds, isolated contexts and exact evidence-packet hashes.
- [ ] Task: Run five specialist agents, isolated adjudication and reproducibility audit under the frozen protocol.
- [ ] Task: Retain failures, abstentions, conflicts and prohibited-source exclusions in assigned denominators.
- [ ] Task: Prohibit all automatic writes to upstream-compatible translation files.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md).

## Phase 4: Confidence model and calibration

- [ ] Task: Implement the multidimensional confidence record and deterministic H1/H2/T1/T2/A1/A2/C/U categorization rules.
- [ ] Task: Estimate provenance priors without treating human-mediated status as proof of correctness.
- [ ] Task: Fit lineage-aware calibration models using held-out concept and language splits; prevent candidate-row leakage.
- [ ] Task: Compare confidence categories against continuous probabilities, uncertainty intervals and non-estimability flags.
- [ ] Task: Run calibration, discrimination, source-ablation, model-tier, regional-fit and temporal-replay analyses.
- [ ] Task: Freeze thresholds prospectively before confirmatory evaluation and retain alternate sensitivity thresholds.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md).

## Phase 5: Network, process and quantitative analysis

- [ ] Task: Generate a typed multiplex evidence graph without turning shared artifacts or registries into cliques.
- [ ] Task: Calculate language, branch, source, lineage, mapping, contradiction and confidence coverage metrics.
- [ ] Task: Evaluate whether network features add predictive value beyond provenance and direct evidence, using held-out data.
- [ ] Task: Run process mining on stage events, exclusions, queue time, retries, adjudication and rework.
- [ ] Task: Report compute, cost, latency, stability and evidence marginal value.
- [ ] Task: Generate publication-ready, colorblind-safe figures and machine-readable figure receipts.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md).

## Phase 6: Payload-safe dashboard and Hugging Face package

- [ ] Task: Define public and private data contracts, dataset cards, model cards, Space card and security boundaries.
- [ ] Task: Build a local read-only Gradio prototype from synthetic and payload-safe aggregate fixtures.
- [ ] Task: Add coverage, calibration, network, concept-card, drift, process and Pareto views.
- [ ] Task: Add secret, PHI, restricted-namespace, licence, unsafe-receipt and source-text scans.
- [ ] Task: Add accessibility, small-screen, deterministic-render and download-integrity tests.
- [ ] Task: Prepare deployment manifests with `execution_authorized=false`; do not create or upload the Space.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md).

## Phase 7: GitHub Project and issue synchronization plan

- [ ] Task: Define a versioned mapping from Conductor tracks and phases to GitHub Project items, issues, sub-issues and checklists.
- [ ] Task: Define stable custom fields, issue templates, labels, milestones, dependency links and external-action states.
- [ ] Task: Build a local dry-run exporter that produces proposed issue/project mutations without calling GitHub.
- [ ] Task: Add idempotency, externally-edited-item preservation, conflict reporting and rollback receipts.
- [ ] Task: Review issue granularity to avoid issue spam and preserve upstream maintainer attention.
- [ ] Task: Obtain explicit repository, organization, project, issue and write-action approval before any hosted mutation.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md).

## Phase 8: Preprint and reproducibility package

- [ ] Task: Freeze the paper question, protocol, statistical analysis plan, search strategy, claim-evidence matrix and authorship/disclosure policy.
- [ ] Task: Draft methods and limitations before unblinding confirmatory results.
- [ ] Task: Generate results, figures, tables and supplementary materials only from frozen manifests.
- [ ] Task: Run citation verification, independent editorial review, statistical review, ethics review and adversarial claim audit.
- [ ] Task: Produce arXiv Markdown/LaTeX/PDF sources, data/code availability statement, RAISE-aligned disclosure and reproducibility checklist.
- [ ] Task: Prepare but do not submit the arXiv package until explicit publication approval.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md).

## Phase 9: Curated upstream handoff

- [ ] Task: Generate a minimal methods/preprint PR proposal and a separate minimal translation-change PR proposal.
- [ ] Task: Prove that the translation proposal contains no research-platform bulk diff and no unapproved AI-only record.
- [ ] Task: Attach per-record provenance, confidence category, contradictions, validation and accountable maintainer decision.
- [ ] Task: Draft a concise upstream issue/PR cross-reference map that respects maintainer workload and contribution policy.
- [ ] Task: Run full local admission, exact-head hosted checks in the fork when authorized, and payload-safe security review.
- [ ] Task: Obtain explicit upstream repository and action approval before opening any issue or PR.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md).
