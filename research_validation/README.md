# Empirical Translation Validation

This directory contains canonical, payload-safe research governance inputs for the empirical translation-validation track.

The ontology-network build may read these files to determine scientific readiness, but it must not infer that schema validation, a source count, or a payload-free probe constitutes empirical translation evidence.

## Current gate

`language_identity_registry.json` records language identities that require authority review. An unresolved record fails translation-evidence readiness but does not rename or modify any translation profile.

## Benchmark contract

- `protocol.md` defines the payload-safe pilot design, outcomes, reviewer process, and analysis gates.
- `source_catalog.json` records pinned authoritative mapping metadata and dependence groups without mapping rows.
- `source_verification.md` documents the primary-source search and license boundary.
- `schemas/` contains strict JSON Schemas for every committed research artifact.
- `fixtures/passing/` contains synthetic, non-clinical examples that must validate.
- `fixtures/failing/` contains deliberately invalid examples that must be rejected.

Run `pixi run validate-research-validation` to validate the schemas, canonical language-identity registry, and fixtures. A passing result proves only that the local research contract is executable; it is not evidence that a translation is valid or release-ready.

Run `pixi run verify-research-source-pins` only when network access is available. It streams and hashes the pinned public assets without retaining their payloads. This is a reproducibility check, not permission to commit or reuse the source content.
