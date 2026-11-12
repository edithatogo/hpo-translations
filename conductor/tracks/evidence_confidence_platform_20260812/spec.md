# Specification: Layered Translation Evidence and Confidence Platform

## Overview

Build a research and reporting layer around the Human Phenotype Ontology Internationalization Effort without disrupting upstream workflows or rewriting upstream translation assets. The platform will preserve authoritative human-mediated translations as immutable reference inputs, generate separately stored AI-supported candidates, triangulate all available evidence with explicit lineage and rights controls, quantify confidence and uncertainty, and produce payload-safe reports, network analyses, process analyses and interactive visualizations.

The platform is an overlay, not a fork of the upstream translation policy. AI output remains candidate evidence. Nothing in this system promotes a label into an upstream translation file or represents it as human validated.

## Architectural invariants

1. **Immutable upstream core.** Pin upstream commits, releases and translation blobs. Never rewrite, normalize or enrich an upstream file in place for research convenience.
2. **One-way ingestion.** Import identifiers, hashes, metadata and permitted payloads into a versioned evidence lake. Research outputs never flow back automatically.
3. **Separated derivative layers.** Keep source snapshots, normalized atoms, mapping assertions, model candidates, assessments, calibrated scores, reports and proposed upstream patches in distinct schemas and storage paths.
4. **Provenance before confidence.** Every evidence atom identifies its authority, release, language/script/region, object type, mapping predicate, derivation, rights state and independent-lineage group.
5. **No registry multiplication.** OLS, BioPortal, Ontobee, FAIRsharing, LOV and upstream mirrors are discovery records, not independent votes.
6. **No rights laundering.** Open mappings do not authorize restricted labels. Private storage is used only where third-party cloud custody is affirmatively permitted.
7. **Candidate-only AI.** Model outputs are never classified as human-mediated and never receive promotion authority from confidence scores, agent agreement or network centrality.
8. **Reproducible freezes.** Every empirical run freezes source blobs, models, prompts, seeds, mappings, sampling, exclusions, analysis code and price schedules.
9. **Payload-safe publication.** Public reports expose identifiers, aggregate metrics and redistributable evidence only.
10. **Maintainer-controlled handoff.** Upstream-facing changes are generated as a minimal, reviewable patch with provenance attachments and an explicit accountable-maintainer decision.
11. **HPOIE contract fidelity.** Local research contracts must preserve the official distinction between professional, manual and automated translation provenance; use ISO 639-1 or, when unavailable, ISO 639-3/IANA language identity; keep Babelon labels and definitions separate from ROBOT-template synonyms; and synchronize source-value confirmation with exact HPO releases.
12. **Pivot inference is candidate retrieval.** UMLS, SNOMED CT, Orphadata and compositional routes may generate ranked evidence sets, but no CUI, SCTID, ORPHA identifier, source preference flag or first returned string is itself an HPO translation decision.
13. **BabelNet is conditional linguistic evidence.** Use BabelNet only when governed triggers identify pivot disagreement, lexical gaps, descriptive components, low confidence or unresolved locale. Preserve the originating resource and collapse Wikidata-derived senses into the Wikidata lineage; a Health domain label and generic `pt` never establish clinical meaning or a national Portuguese variant.

## Evidence layers

### L0: authoritative upstream reference

- Current and historical human-mediated HPO translation records.
- Exact Git blob, release, contributor-method metadata and upstream status.
- Used as baseline, comparator and calibration target after leakage-safe candidate lock.
- Strong provenance prior, but not automatically error-free or maximally current.

### L1: independent human-mediated terminology evidence

- Authorized multilingual labels and synonyms from other ontologies and terminologies.
- Exact language, regional edition, designation role, mapping direction and source lineage required.
- May support lexical triangulation only when the HPO relationship and source rights permit that role.

### L2: structural and contextual ontology evidence

- Anatomy, cell, quality, measurement, disease, symptom, functioning, treatment, exposure and genotype context.
- Used for semantic constraints, contradiction detection, compositional validation and hard negatives.
- Does not count as a lexical vote unless an independently authorized lexical assertion exists.

### L3: model-generated candidate evidence

- Tiny, small, medium and large model tiers.
- Model-only, authorized-translation-assisted and lineage/ontology-assisted arms.
- Repeated, isolated, blinded and reproducibly frozen.
- Always labelled AI-generated candidate evidence.

### L4: independent assessment and reproducibility evidence

- Five specialist agents, isolated adjudication agent and non-voting reproducibility auditor.
- Locked decisions, error taxonomy, abstentions, conflicts and deterministic aggregation.
- Cannot grant rights, language-community authority, clinical validity or promotion.

### L5: downstream empirical evidence

- Ontology discrimination, extraction, phenotype ranking, Phenopacket round trips, release-drift replay and negative controls.
- Supports utility and safety claims, not reclassification as human-mediated translation.

## Confidence model

Confidence is a calibrated vector plus a reporting category, not a single opaque score.

Required dimensions per HPO concept-language-object record:

- `provenance_confidence`: authority, contributor method and immutable source identity.
- `lexical_support`: agreement among independent authorized lexical lineages.
- `semantic_consistency`: consistency with HPO hierarchy, definitions, logical components and hard negatives.
- `mapping_confidence`: predicate, direction, hop count, semantic loss and edition applicability.
- `regional_fit`: language, script, country, register and terminology-edition match.
- `temporal_currency`: alignment with the current HPO and source releases.
- `model_stability`: agreement across seeds, evidence arms, model tiers and family-disjoint sensitivity analyses.
- `assessment_confidence`: specialist agreement, adjudication outcome, abstention and reproducibility.
- `downstream_utility`: extraction, ranking and structured-record fidelity where estimable.
- `rights_and_use_state`: separately reported gate; never blended into scientific confidence.

### Reporting categories

- **H1 — human-mediated, corroborated:** verified human-mediated HPO provenance plus no material contradiction and at least one qualifying independent corroboration or strong semantic validation.
- **H2 — human-mediated, baseline-only:** verified human-mediated HPO provenance but insufficient independent corroboration, material source staleness, or unresolved conflict.
- **T1 — triangulated candidate:** no authoritative HPO human translation; at least two independent authorized human-mediated lexical lineages, admissible mapping, semantic consistency and stable model/assessment support.
- **T2 — single-lineage supported candidate:** one authorized human-mediated lexical lineage plus semantic and assessment support.
- **A1 — AI candidate with structural support:** reproducible model candidate supported by ontology structure/context but lacking qualifying independent lexical evidence.
- **A2 — AI-only or unstable candidate:** model-derived evidence without sufficient independent or stable support.
- **C — conflicted:** material lexical, semantic, regional, temporal, safety or assessment contradiction.
- **U — unavailable/unassessed:** insufficient admissible evidence or a blocked rights/community/ethics gate.

These categories are descriptive research outputs. None authorizes upstream promotion. Category thresholds and any probabilistic calibration must be frozen before confirmatory evaluation and reported with uncertainty.

## HPOIE-aligned contract boundary

The platform must define machine-readable contracts for language-profile identity, contributor attribution, translation method, Babelon label/definition rows, ROBOT synonym rows, source-value drift confirmation, release synchronization, candidate provenance and upstream handoff. The contracts must preserve the official HPOIE source-of-truth profile and its `OFFICIAL`/`CANDIDATE` status semantics without allowing this research overlay to assign upstream status. Submitter identity and the mandatory short description of how a profile was produced and used belong to the handoff package; optional ORCID, contributor, ROR and Wikidata identifiers remain attribution metadata. Crowdin and Babelon are ingestion routes, not scientific evidence lineages.

The pivot candidate contract must return all eligible atoms with source, release, AUI or source identifier, language, script/region, designation, suppression state, mapping predicate, direction, semantic loss, lineage and rights state. It must prohibit arbitrary `fetchone()` selection, CUI equivalence inference, edition inheritance and source-name confidence shortcuts. Compositional candidates must preserve anatomy, quality, laterality, severity and temporal modifiers and remain labelled as recomposed candidates.

## Quantitative and network analyses

The platform must support:

- Coverage proportions and confidence-category distributions by language, HPO branch and translation object.
- Exact uncertainty intervals and denominator accounting for missing, blocked and ineligible records.
- Lineage-aware versus naive source-voting comparisons.
- Calibration curves, Brier score, log loss, reliability diagrams and prediction intervals.
- Hierarchical models by concept, language, source lineage, model tier and assessment agent.
- Leave-one-lineage-out and source-family ablations.
- Temporal replay and source/HPO drift prediction.
- Mapping-hop and semantic-loss degradation analysis.
- Contradiction, abstention, failure and rework process analysis.
- Cost, latency, tokens, retries and compute per usable candidate.
- Multiplex evidence networks with typed nodes and edges for concepts, translations, sources, mappings, models, assessments and releases.
- Community detection, centrality and bridge analysis for discovery only; graph structure must not be interpreted as correctness without outcome validation.
- Confidence propagation only through an allowlisted, predicate-aware probabilistic model with lineage dependence and rights gates preserved.

## Process analysis

Instrument the complete pipeline as an append-only event log:

`ingested → normalized → mapped → eligible → generated → assessed → adjudicated → reproduced → analysed → handed_off → maintainer_decided`

Measure stage duration, queue time, retry rate, exclusion reasons, conflict rate, adjudication burden, source-blocker time, reproducibility failures and rework loops. Use process-mining outputs to improve the workflow prospectively, never to bypass a gate.

## Visualization and Hugging Face Space design

Design a read-only Gradio Space backed only by payload-safe generated artifacts. Deployment is a separate external action.

Recommended views:

- Global coverage and confidence dashboard.
- Language × HPO-branch heatmap.
- Confidence calibration and uncertainty plots.
- Evidence-lineage network explorer with predicate and rights filters.
- Concept evidence card showing source groups, contradictions, model stability and category rationale without restricted labels.
- Release-drift timeline.
- Process funnel and bottleneck dashboard.
- Model-tier cost/safety/utility Pareto frontier.
- Downloadable aggregate tables and machine-readable methodology receipts.

The Space must have no editing, promotion, source-retrieval or upstream-write capability. Private and public variants use separate repositories and data sets; public builds fail closed if restricted namespaces, payload text, secrets or unsafe receipts are detected.

## Repository and upstream strategy

### Fork organization

- Keep upstream-compatible translation files and validation behavior intact.
- Put research code under explicit analysis/evidence modules rather than modifying Babelon semantics.
- Generate all derived data from manifests; do not commit restricted payloads.
- Maintain a continuously replayable upstream-diff report that classifies changes as untouched upstream core, deterministic infrastructure, research-only artifact or proposed translation patch.
- Rebase or merge upstream changes into a clean integration branch and regenerate derived artifacts; never force upstream to absorb the research architecture.

### Eventual upstream handoff

Prepare two distinct PRs only after explicit approval:

1. **Methods/preprint PR:** documentation, paper link, reproducibility package and methodological context, without translation-file changes.
2. **Translation PR:** minimal accepted translation changes only, with per-record provenance and confidence evidence; no research platform bulk diff.

Cross-reference them through a small number of curated issues. Do not create issue spam or one issue per generated artifact.

## GitHub project plan

The fork should eventually use one GitHub Project with stable custom fields:

- Conductor track ID
- Phase
- Status
- Priority
- Source/rights gate
- Language/community gate
- Freeze ID
- Artifact class
- Confidence workstream
- Upstream impact
- External-action status
- PR and release links

Each Conductor track maps to one parent issue. Each plan phase maps to a GitHub sub-issue only when it represents independently actionable work; atomic checklist tasks remain issue checklists unless they need their own owner, discussion or PR. Synchronization is manifest-driven and dry-run by default, with idempotency keys and no automatic closure of externally edited issues.

## Publication architecture

The eventual arXiv package should follow an auditable research-paper pipeline:

- Frozen protocol and statistical analysis plan.
- Primary-source literature and registry search log.
- Dataset and language flow diagram.
- Rights, exclusions and unavailable-source accounting.
- Model cards, prompt hashes and compute disclosure.
- RAISE-aligned AI research disclosure.
- Methods for lineage-aware confidence and calibration.
- Prespecified primary and secondary analyses.
- Negative controls, ablations and sensitivity analyses.
- Payload-safe reproducibility package.
- Limitations addressing model contamination, absence of human validation, source dependence, regional generalizability and upstream policy.
- Independent internal paper review, citation verification and figure regeneration before submission.

The paper must distinguish human-mediated baselines, human-derived cross-ontology evidence, AI candidates and agent assessments throughout. “High confidence” must never be used as a synonym for “human” or “accepted upstream.”

## Acceptance criteria

- Upstream files remain byte-identical unless a separately authorized minimal translation patch is prepared.
- Every evidence record has immutable provenance, lineage, rights and language identity.
- Confidence categories are deterministic from versioned inputs and calibrated against held-out outcomes when probabilistic claims are made.
- Human-mediated baselines are triangulated and contradictions remain visible.
- AI candidates remain separately labelled and cannot be automatically promoted.
- Network, quantitative, process and confidence outputs reproduce from one frozen manifest.
- Public artifacts contain no restricted payload, secret, patient data or unsafe model context.
- The dashboard is read-only and cannot mutate GitHub, Hugging Face data sets or upstream repositories.
- GitHub synchronization is dry-run, idempotent and reversible.
- The preprint claim-evidence matrix links every result to code, data manifest and figure receipt.
- All external writes remain separately approved.

## Out of scope for this planning track

- Contacting upstream maintainers.
- Creating or updating upstream or fork GitHub issues, projects or pull requests.
- Deploying a Hugging Face Space or dataset.
- Running empirical translation models.
- Promoting translation candidates.
- Submitting an arXiv manuscript.
