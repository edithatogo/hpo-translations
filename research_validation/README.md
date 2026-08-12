# Empirical Translation Validation

This directory contains canonical, payload-safe research governance inputs for the empirical translation-validation track.

The ontology-network build may read these files to determine scientific readiness, but it must not infer that schema validation, a source count, or a payload-free probe constitutes empirical translation evidence.

## Stage 0 rehearsal

`stage_0/` contains the deterministic, payload-free Phase 4 operational rehearsal.
Run it with `pixi run run-stage-0-rehearsal`. Its receipt covers synthetic
sampling, blinding, randomization, export, adjudication, redaction, and
go/revise/stop handling. A passing receipt establishes operational readiness
only; it does not create empirical translation or agent-panel evidence.

`agent_compute_budget.json` records the provisional G0 capacity envelope.
Only the 30-hour Stage 1 cap is initially releasable; the remaining capacity up
to the 120-hour pilot ceiling requires a reforecast from observed Stage 1 timing,
adjudication, completion, attrition, and roster data. It authorizes no contact,
spend, payload retrieval, empirical generation, registration, publication, push,
or pull request.

## Current gate

`language_identity_registry.json` records language identities that require authority review. An unresolved record fails translation-evidence readiness but does not rename or modify any translation profile.

`phase_4_wave_1_source_decisions.json` records bounded conditional licence-scope
decisions for Mondo, WHO ICF, Uberon, and PATO. It authorizes no payload
retrieval, mapping or adaptation, redistribution, empirical work, or promotion.
The overall source gate remains open and the track remains synthetic-only.

## Benchmark contract

- `protocol.md` defines the payload-safe pilot design, outcomes, agent process, and analysis gates.
- `source_catalog.json` records pinned authoritative mapping metadata and dependence groups without mapping rows.
- `mapping_expansion_catalog.json` covers every registered ontology source, records newly discovered authoritative map families and language editions, and preserves a payload-free admission boundary. Run `pixi run validate-mapping-expansion` after editing it.
- `translation_source_utilisation_plan.json` and its [interpretation guide](translation_source_utilisation_plan.md) specify how existing translations may support candidate generation, lineage-aware triangulation, semantic checks, regional-variant analysis, source ablation, drift prioritization, and a candidate-only handoff. The plan does not alter the sealed Spanish/Japanese G3 freeze or authorize any catalogue payload. Run `pixi run validate-translation-source-utilisation` after editing it.
- `orthogonal_biomedical_source_catalog.json` governs 17 adjacent biomedical source families—among them WHO ATC/DDD, RxNorm, ChEBI, GO, ICF, PRO-CTCAE, MedlinePlus, RadLex, and compositional OBO ontologies—and nine prospective analyses. These sources may supply identity, causal, register, structural, hard-negative, or downstream context, but no direct lexical vote. Run `pixi run validate-orthogonal-biomedical-sources` after editing it.
- `next_language_pilot_plan.json` selects French and Czech for the next prospective two-language pilot, permits Dutch and Turkish only under a pre-freeze affordability rule, and opens metadata-only source preparation for Polish and Ukrainian. It preserves the Spanish/Japanese freeze and authorizes no payload, spend, agent execution, external contact, or empirical work. Run `pixi run validate-next-language-pilot` after editing it.
- `registry_source_expansion_catalog.json` governs 21 resources discovered through OBO Foundry, OLS4, Ontobee, BioPortal, FAIRsharing, LOV and the UMich guide. It resolves registry entries to authoritative upstream sources, preserves mapping-method and lineage provenance, and separates archive eligibility from empirical authority. Run `pixi run validate-registry-source-expansion` after editing it.
- `translation_source_assignments.json` binds all 15 metadata and future-authorized source-use cases to exact assertions, languages, roles, gates, lineage rules, and prohibitions. `translation_statistical_analysis_plan.json` fixes populations, outcome denominators, paired models, missingness, multiplicity, integer Stage 1 thresholds, nine Phase 5 analyses, lexical and mapping controls, cost estimands, and non-estimability rules. Both are planning-only and require re-freezing before they change empirical work.
- `translation_model_tier_plan.json` prospectively crosses tiny, small, medium, and large model-capacity tiers with model-only, existing-translation-assisted, and lineage/ontology-assisted evidence arms. The exact existing Spanish/Japanese HPO translations remain a withheld non-generative comparator for every tier. Exact endpoints are intentionally unselected until a new freeze pins all models, prompts, evidence hashes, repetitions, budgets, and permissions.
- `translation_plan_improvement_register.json` requires every source assignment and A1-A10 analysis to be reconsidered against authority, rights, language/edition, mapping semantics, lineage, bias, leakage, estimability, uncertainty, cost, reproducibility, community governance, and claim boundaries. Findings may clarify future planning, require a prospective amendment/new freeze, defer/exclude a source, or stop affected work; negative and non-estimable findings remain visible.
- `source_payload_archive_plan.json` turns the mapping catalogue into a dataset-preservation queue. `pixi run validate-source-payload-archive` is metadata-only; `pixi run archive-source-payloads-local` retrieves only explicitly allowlisted, checksum-pinned artifacts into ignored `.archive-staging/`. Public and private Hugging Face uploads require separate exact targets, verified licence/storage permission, a rotated credential, and explicit external-write approval.
- `terminology_node_registry.json` catalogues every governed source family, observed mapping namespace, national edition, product release, and language rendition without treating parentage or language similarity as mapping equivalence. `mapping_route_definitions.json` declares exact endpoints and semantic, provenance, rights, version, integrity, and composition controls. `mapping_route_catalog.json` deterministically records 900 directed outcomes across the current 30 routed nodes, retains alternative paths, and assigns a disposition to every governed mapping artifact. Run both terminology-registry and mapping-route validation and drift tasks after editing mapping metadata. The interpretation guide is [the ontology mapping catalogue](../docs/ontology-mapping-catalog.md).
- `source_verification.md` documents the primary-source search and license boundary.
- `supplementary_source_access_reviews.json` records source-specific access, overlap, licence, and human-decision gates without retrieving payloads.
- `supplementary_source_access_review.md` summarizes the supplementary-source decisions and their interpretation boundary.
- `schemas/` contains strict JSON Schemas for every committed research artifact.
- `fixtures/passing/` contains synthetic, non-clinical examples that must validate.
- `fixtures/failing/` contains deliberately invalid examples that must be rejected.

Run `pixi run validate-research-validation` to validate the schemas, canonical language-identity registry, and fixtures. A passing result proves only that the local research contract is executable; it is not evidence that a translation is valid or release-ready.

Run `pixi run verify-research-source-pins` only when network access is available. It streams and hashes the pinned public assets without retaining their payloads. This is a reproducibility check, not permission to commit or reuse the source content.

The supplementary access review is metadata-only. A `metadata_probe_allowed` decision never authorizes payload retrieval, mapping, adaptation, redistribution, or empirical use.
