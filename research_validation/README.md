# Empirical Translation Validation

This directory contains canonical, payload-safe research governance inputs for the empirical translation-validation track.

The ontology-network build may read these files to determine scientific readiness, but it must not infer that schema validation, a source count, or a payload-free probe constitutes empirical translation evidence.

## Stage 0 rehearsal

`stage_0/` contains the deterministic, payload-free Phase 4 operational rehearsal.
Run it with `pixi run run-stage-0-rehearsal`. Its receipt covers synthetic
sampling, blinding, randomization, export, adjudication, redaction, and
go/revise/stop handling. A passing receipt establishes operational readiness
only; it does not create empirical translation or human-review evidence.

`reviewer_workload_budget.json` records the provisional G0 capacity envelope.
Only the 30-hour Stage 1 cap is initially releasable; the remaining capacity up
to the 120-hour pilot ceiling requires a reforecast from observed Stage 1 timing,
adjudication, completion, attrition, and roster data. It authorizes no contact,
spend, payload retrieval, empirical generation, registration, publication, push,
or pull request.

## Current gate

`language_identity_registry.json` records language identities that require authority review. An unresolved record fails translation-evidence readiness but does not rename or modify any translation profile.

## Benchmark contract

- `protocol.md` defines the payload-safe pilot design, outcomes, reviewer process, and analysis gates.
- `source_catalog.json` records pinned authoritative mapping metadata and dependence groups without mapping rows.
- `source_verification.md` documents the primary-source search and license boundary.
- `supplementary_source_access_reviews.json` records source-specific access, overlap, licence, and human-decision gates without retrieving payloads.
- `supplementary_source_access_review.md` summarizes the supplementary-source decisions and their interpretation boundary.
- `schemas/` contains strict JSON Schemas for every committed research artifact.
- `fixtures/passing/` contains synthetic, non-clinical examples that must validate.
- `fixtures/failing/` contains deliberately invalid examples that must be rejected.

Run `pixi run validate-research-validation` to validate the schemas, canonical language-identity registry, and fixtures. A passing result proves only that the local research contract is executable; it is not evidence that a translation is valid or release-ready.

Run `pixi run verify-research-source-pins` only when network access is available. It streams and hashes the pinned public assets without retaining their payloads. This is a reproducibility check, not permission to commit or reuse the source content.

The supplementary access review is metadata-only. A `metadata_probe_allowed` decision never authorizes payload retrieval, mapping, adaptation, redistribution, or empirical use.
