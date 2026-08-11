# Plan - Integrate ICD-10 into terminology and translation support

This plan introduces ICD-10 into the project where it can improve terminology alignment, multilingual review, or validation.

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
  - Mark any LLM-assisted candidate output as candidate-only and agent-panel-assessment-required and maintainer-promotion-decision-required in the handoff pack.

## Phase 1: Source Governance
- [x] **Task 1:** Catalog authoritative public release channels and jurisdiction-specific licence or terms-review requirements as metadata.
- [x] **Task 2:** Record publicly documented national variants, languages, release labels, and mapping products without retrieving payloads.
- [ ] **Task 3:** Authorize the exact release payload, licence, redistribution scope, and immutable checksum for each admitted jurisdiction.
  - WHO and each national variant remain separate gates; cataloged metadata is not payload authority.
- [x] **Task 4:** List relevant GitHub repositories (tooling reference only; ICD-10 authority and terms remain unresolved):
  - https://github.com/ICD-API

## Phase 2: Data Access and Normalization
- [x] **Task 1:** Define jurisdiction-specific retrieval and local-only handling paths without committing source payloads.
- [x] **Task 2:** Define the payload-free normalization contract for variant identifiers, codes, language tags, mapping provenance, and jurisdiction.
- [x] **Task 3:** Publish the payload-free national-variant and mapping inventory for agent-panel assessment.
- [ ] **Task 4:** Normalize an authorized bounded source sample for each selected jurisdiction.
  - Blocked until the exact variant payload, licence or terms, version, checksum, and local-only controls are authorized.

## Phase 3: HPO Translation Use
- [x] **Task 1:** Identify ICD-10 use for disease-classification context, identifier conflict detection, and language-coverage review; terms remain blocked.
- [x] **Task 2:** Add code/URI-preserving matching and candidate conflict-record rules; unresolved conflicts do not promote.
- [x] **Task 3:** Ensure LLM-assisted outputs remain candidate-only and agent-panel-assessment-required and maintainer-promotion-decision-required; no approved source sample exists.

## Phase 4: Validation and Review
- [x] **Task 1:** Validate governance schema, provenance, and licence metadata; WHO and variant terms remain blocked.
- [x] **Task 2:** Record translation-audit and import dry runs as not applicable without authorized source terms.
- [x] **Task 3:** Document limitations, excluded payloads, and review decisions.


## Phase 0 Validation Evidence
- Generated governance record: `ontology_network/source_registry.json` and `ontology_network/source_access_matrix.*` entries for `icd10_integration_20260623`.
- Source authority: WHO ICD-10 release channel and national localized variants are recorded as terms-review-required before payload access; `https://github.com/ICD-API` is a tooling reference, not the authoritative release payload.
- Payload status: no raw, licensed, credentialed, private, full-release, label, synonym, definition, national-variant, or API-response payload is read or committed.
- Downstream status: identifier-network, translation-use, and non-translation outputs remain blocked until source terms review, variant scope selection, and bounded source probe pass.
