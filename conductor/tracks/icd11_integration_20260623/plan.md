# Plan - Integrate ICD-11 into terminology and translation support

This plan introduces ICD-11 into the project where it can improve terminology alignment, multilingual review, or validation.

## Phase 0: Dependency, Blocker, Source, and Automation Gates
- [x] **Task 1:** Populate the blocker registry in metadata before implementation.
  - Record `known_blockers`, `expected_blockers`, `blocker_owner`, `fallback_path`, and a go/no-go decision for source ingestion.
  - Do not begin batch extraction while license, credential, source authority, or payload-commit status is unresolved.
- [x] **Task 2:** Complete the source access gate.
  - Record `source_access_status`, authoritative endpoint or repository, version-pinning strategy, credential requirements, cache location, and rate-limit or download constraints.
  - Classify the source as open, restricted, API-only, local-only, documentation-only, or investigation-only.
- [x] **Task 3:** Apply the restricted payload policy.
  - Define the commit allowlist and denylist for this source before touching payloads.
  - Add a local-only manifest for any raw, licensed, private, credentialed, or full-release payload.
  - Prove generated review artifacts do not contain prohibited source text, credentials, or redistributable payload fragments.
- [x] **Task 4:** Run a fail-fast probe before bulk work.
  - Process one authoritative source record end to end into a registry row, provenance row, validation result, and comparison or crosswalk sample when applicable.
  - Stop and update the blocker registry if schema, license, source authority, or mapping semantics fail on the probe.
- [x] **Task 5:** Define the track artifact contract.
  - Name each committed artifact, local-only artifact, generated report, validation fixture, and downstream consumer.
  - Include expected schema, owner, validation command, freshness rule, and whether the artifact can appear in an upstream PR.
- [x] **Task 6:** Set priority, write ownership, and parallelization boundaries.
  - Record `priority`, `parallel_group`, `write_owner`, and `merge_owner`.
  - Parallel work is allowed only when agents have disjoint source manifests, plans, generated artifacts, and Babelon profile write scopes.
- [x] **Task 7:** Define task automation and remote delivery gates.
  - For each ready task, run the implementation workflow, validate locally, commit after completion, run conductor-review after each phase, apply authorized fixes, push after each phase, verify GitHub Actions on the pushed commit and PR head, and verify PR merge before marking complete.
- [x] **Task 8:** Start performance, evidence, and model telemetry.
  - Record coding agent, model, task id, source version, runtime, validation result, conflict count, and unresolved blockers.
  - Mark any LLM-assisted candidate output as candidate-only and human-review-required in the handoff pack.

## Phase 1: Source Governance
- [x] **Task 1:** Confirm authoritative release source, license, and redistribution constraints.
  - WHO ICD API is the authoritative API; ICD-11 is CC BY-ND 3.0 IGO and no adaptations or source-payload redistribution are approved.
  - Decision recorded: metadata-only governance is approved; authenticated probing remains gated on credential custody and a later bounded-probe decision.
- [x] **Task 2:** Record supported languages and source-version metadata.
  - Review target is ICD-11 release `2026-01`; supported MMS languages are Arabic, Chinese, Czech, English, French, German (prerelease), Kazakh, Latin (titles only), Portuguese, Russian, Slovak, Spanish, Swedish, Turkish, and Uzbek.
  - API access uses OAuth2 client credentials; no credential or response payload is stored in the repository.
- [x] **Task 3:** List relevant GitHub repositories:
  - https://github.com/ICD-API
  - The bounded authenticated probe remains a roadmap item and is not executed in this phase.

## Phase 2: Data Access and Normalization
- [x] **Task 1:** Define source retrieval path without committing restricted payloads.
  - Implemented in `phase2_data_access_normalization.json`: WHO API v2, OAuth2 client credentials, request-manifest-only retrieval, and local-only credential/response boundaries.
- [x] **Task 2:** Normalize identifiers, preferred labels, synonyms, language tags, and provenance fields.
  - Implemented a metadata-only normalization contract distinguishing foundation URIs from MMS linearization codes and requiring ISO 639-1 language and request-manifest provenance.
- [ ] **Task 3:** Produce a bounded sample artifact for maintainer review.
- [x] **Task 3:** Produce a bounded sample artifact for maintainer review.
  - `phase4_bounded_sample_metadata.json` records the successful one-entity probe without retaining source labels, synonyms, definitions, or the full response.

## Phase 3: HPO Translation Use
- [x] **Task 1:** Identify where ICD-11 helps: crosswalks, synonym review, multilingual label comparison, or domain validation.
  - Defined crosswalk review, multilingual label comparison, and domain-validation use cases in `phase3_hpo_translation_use.json`.
- [x] **Task 2:** Add deterministic matching rules and conflict reporting.
  - Added exact-identifier, curated-crosswalk, language-match, and postcoordination rules with explicit conflict types and unresolved-by-default handling.
- [x] **Task 3:** Ensure LLM-assisted outputs remain candidate-only and human-review-required.
  - Enforced candidate-only, human-review-required, and no-approved-translation guardrails without reading source payloads.

## Phase 4: Validation and Review
- [x] **Task 1:** Validate schema, provenance, and license metadata.
  - Recorded validation results and the CC BY-ND 3.0 IGO payload boundary in `phase4_validation_review.json`.
- [x] **Task 2:** Run translation-audit and import dry-run checks against sample outputs.
  - The one-entity response passed HTTP/JSON/identifier structural checks; translation audit passed against repository fixtures; no source payload was imported or retained.
- [x] **Task 3:** Document limitations, excluded payloads, and review decisions.
  - Recorded fail-closed limitations, excluded payload classes, candidate-only policy, and the next maintainer review gate.

## P1 Implementation Candidate Addendum
This track is a highest-priority P1 open/public ontology implementation candidate. Start with Phase 0 governance, source-authority confirmation, terms review, and one bounded source probe before any bulk extraction.
Until source terms and payload handling are cleared, commit metadata-only scaffolding only: registry records, source-access records, provenance shells, local-only manifest references, schemas, validation summaries, and reviewer handoff skeletons.
Do not commit raw source terms, ontology labels, synonyms, definitions, full API responses, release payload rows, credentials, or redistributable payload fragments unless redistribution permission is explicitly recorded.

## Phase 0 Validation Evidence
- Generated governance record: `ontology_network/p1_source_governance.json` entry for `icd11_integration_20260623`.
- Payload status: no raw, licensed, credentialed, private, full-release, label, synonym, definition, or API-response payload is read or committed.
- Downstream status: identifier-network, translation-use, and non-translation outputs remain blocked until maintainer review of the redacted probe result and any later source-label approval.

## Phase 0 Review Archive
- Review status: `codex_review_completed`.
- Fixes applied: synchronized metadata, telemetry, source-governance review result, and automation index review state.
- Validation archive: `pixi run validate-conductor`, `pixi run validate-ontology-network`, `pixi run validate-ontology-network-artifacts`, `pixi run test-conductor-validation`, and `git diff --check`.
- Residual blocker: source-label extraction and downstream promotion remain blocked pending maintainer review; the bounded structural probe has passed.
