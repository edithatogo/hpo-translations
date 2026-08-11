# Specification - Establish Empirical Validation for Multilingual HPO Translation

## Overview

Establish a preregisterable, version-pinned research programme that evaluates whether ontology and terminology evidence improves multilingual HPO translation quality, safety, agent-panel efficiency, and downstream utility. This track converts the existing payload-free ontology-network scaffold into an empirical benchmark without treating schemas, mirrors, imported labels, or source counts as scientific evidence.

## Objectives

1. Separate governance-scaffold readiness from empirical-artifact and translation-evidence readiness.
2. Define a reproducible multilingual benchmark before candidate generation or source ingestion.
3. Model source lineage and semantic role so dependent or imported sources do not create false consensus.
4. Evaluate labels, definitions, synonyms, regional variants, and patient-facing terms as distinct objects.
5. Measure translation quality through blinded, context-isolated specialist-agent assessment and independent agent adjudication and ontology-discriminative tasks, not string similarity alone.
6. Retain language-working-group, license, privacy, ethics, and community authority as fail-closed gates.

## Primary Research Questions

1. Does ontology-supported evidence reduce clinically significant translation errors and agent evaluation cost compared with machine-translation-only and LLM-only candidates?
2. Does lineage-aware evidence aggregation predict specialist-agent panel acceptance better than naive source voting?
3. Can a translated term still discriminate its intended HPO concept from parents, children, and close siblings?
4. Do improved preferred labels and curated synonyms improve multilingual HPO extraction or phenotype-driven ranking?
5. Can definition-, graph-, and provenance-aware signals predict which translations require re-review after an HPO release change?

## Functional Requirements

### Research protocol

- Freeze HPO, terminology, ontology, model, prompt, and evaluation-instrument versions for every run.
- Predefine hypotheses, primary and secondary outcomes, exclusions, sampling strata, analysis methods, and stopping rules.
- Use a pilot to estimate agent-role and concept variance and calculate the full study sample size.
- Use temporal and held-out-language evaluation where feasible to reduce benchmark leakage.

### Benchmark sampling

- Stratify by language-resource level, HPO branch, ontology depth, term length, compositionality, translation status, source disagreement, release-change status, and plausible clinical consequence.
- Include hard-negative parent, child, and sibling concepts for ontology-discrimination evaluation.
- Keep approved HPO translations unavailable to candidate-generation systems for benchmark items.

### Specialist-agent evaluation

- Use blinded candidate provenance, randomized presentation order, and isolated initial contexts.
- Run all five canonical specialist roles for every candidate, followed by a separately isolated adjudication agent when prespecified conflicts occur.
- Record pinned model and prompt identifiers, protocol attestations, edit burden, runtime, confidence, safety findings, locked initial decisions, agent adjudication, and deterministic reproduction.
- Report language-specific results and uncertainty; do not hide language-specific failure modes in pooled averages.

### Evidence and provenance

- Represent mappings with typed predicates such as exact, broad, narrow, related, and unmapped.
- Record originating authority, source atom, source release, derivation path, shared-lineage cluster, independent-evidence group, designation role, and license class.
- Treat aggregators and mirrors as discovery layers unless independent provenance is demonstrated.
- Keep LLM and terminology outputs candidate-only and require explicit maintainer release authorization for promotion.

### Language and community governance

- Validate language identity using BCP 47 language, script, region, and variant subtags.
- Record terminology register and intended audience separately from language identity.
- Treat the current `tw` Tiwi/Twi identity conflict as blocked until the language authority confirms the intended identity and migration path.
- Require community authority, consent, attribution, culturally restricted-term handling, model-use permission, benefit, and withdrawal rules for community-governed languages.

## Non-Functional Requirements

- No restricted terminology payloads, credentials, identifiable clinical data, or licensed full responses are committed.
- Every empirical artifact identifies source and HPO releases, retrieval date, generator version, validation command, and provenance identifier.
- All schemas reject unknown fields and have passing and expected-failure fixtures.
- Reproduction must be possible from committed code and metadata plus documented local-only inputs.
- Source rights and community-use constraints remain external evidence gates; semantic evaluation is performed by the canonical agent panel, while release remains an explicit maintainer action.

## Acceptance Criteria

- Release readiness distinguishes governance scaffold, empirical artifacts, translation evidence, and restricted-source payloads.
- A versioned benchmark protocol and pilot design are committed.
- Language identity, translation-evaluation item, source-lineage, agent-decision, and run-manifest schemas validate against passing and failing fixtures.
- The pilot includes a prespecified error taxonomy, adjudication procedure, statistical analysis plan, and downstream-task evaluation plan.
- A fail-fast benchmark fixture exercises at least one HPO item, one hard negative, and two independently identified evidence groups without using restricted text.
- Conductor, ontology-network, lint, and relevant unit tests pass locally.
- No empirical completion claim is made until nonzero, version-pinned records and reproducible agent-panel evidence exist.

## Out of Scope

- Automatic promotion of translations to `OFFICIAL`.
- Unapproved ingestion or redistribution of restricted sources.
- Renaming or migrating a community language profile without authority approval.
- Use of identifiable patient records.
- Claims of clinical effectiveness based only on lexical agreement or schema validation.
- Opening a pull request, publishing results, or registering a study without explicit maintainer approval.

## Candidate Source Families

- Existing HPO SSSOM mapping sets and release reports.
- HeTOP and BioPortal as provenance-aware discovery layers.
- DeCS, Mondo, PRO-CTCAE, WHO ICF, NCIt/NCI dictionaries, and RadLex subject to source-specific terms.
- Uberon, Cell Ontology, GO, ChEBI, NBO, PATO, and uPheno for compositional-semantic evidence.
- Properly licensed usage corpora for attestation and downstream evaluation.

