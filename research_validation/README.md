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
- `mapping_route_definitions.json` declares canonical source identities, aliases, domains, and atomic artifact-backed assertions. `mapping_route_catalog.json` deterministically records one directed outcome for all 784 ordered pairs across 28 governed source families. Run `pixi run validate-mapping-routes` and `pixi run check-mapping-route-drift` after editing mapping metadata. The interpretation guide is [the ontology mapping catalogue](../docs/ontology-mapping-catalog.md).
- `source_verification.md` documents the primary-source search and license boundary.
- `supplementary_source_access_reviews.json` records source-specific access, overlap, licence, and human-decision gates without retrieving payloads.
- `supplementary_source_access_review.md` summarizes the supplementary-source decisions and their interpretation boundary.
- `schemas/` contains strict JSON Schemas for every committed research artifact.
- `fixtures/passing/` contains synthetic, non-clinical examples that must validate.
- `fixtures/failing/` contains deliberately invalid examples that must be rejected.

Run `pixi run validate-research-validation` to validate the schemas, canonical language-identity registry, and fixtures. A passing result proves only that the local research contract is executable; it is not evidence that a translation is valid or release-ready.

Run `pixi run verify-research-source-pins` only when network access is available. It streams and hashes the pinned public assets without retaining their payloads. This is a reproducibility check, not permission to commit or reuse the source content.

The supplementary access review is metadata-only. A `metadata_probe_allowed` decision never authorizes payload retrieval, mapping, adaptation, redistribution, or empirical use.
