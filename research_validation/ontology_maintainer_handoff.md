# Ontology-Maintainer Handoff

## Handoff state

**Hold — no ontology or translation promotion is authorized.**

This handoff communicates the locally frozen research design and its current blocked state. It contains no
translation payload, candidate term, restricted terminology, credential, identifiable clinical text, or
empirical result.

## Materials safe to inspect

- `research_validation/phase_4_freeze/freeze_receipt.json`
- `research_validation/phase_4_freeze/component_manifest.json`
- `research_validation/phase_4_g3_component_inventory.json`
- `research_validation/pilot_source_payload_manifest.json`
- `research_validation/pilot_independent_lineage_groups.json`
- `research_validation/phase_4_payload_safe_report.md`

The two selected repository snapshots are identified by hashes in the payload manifest. Their translation
text is not reproduced in this handoff.

## Maintainer actions now

1. Preserve all existing HPO and Babelon records unchanged.
2. Do not mark any candidate `OFFICIAL`, merge a candidate into HPO, alter preferred labels or synonyms,
   or infer endorsement from the G3 freeze.
3. Treat the Spanish and Japanese snapshots as bounded research inputs only after their separate
   community-use gates close.
4. Treat all excluded external, restricted, mapping-catalog, and archived sources as unavailable to this
   run.
5. Require a new freeze identifier if any model, prompt, agent mandate, source hash, sample, randomization,
   aggregation, exclusion, progression, privacy control, or analysis implementation changes.

## Evidence required before a future promotion handoff

- Recorded Spanish and Japanese language/community-use decisions.
- Recorded ethics/privacy determination.
- Successful Stage 1 execution and frozen go decision.
- Completed pilot with deterministic aggregation and payload-safe analysis.
- Applicable Phase 5 evidence, if required for the proposed claim.
- A candidate-level provenance and safety record with unresolved conflicts closed.
- Explicit ontology-maintainer release authorization for the exact proposed changes.
- Passing local and hosted checks on the exact release commit.

## Current disposition

The appropriate downstream disposition is `hold_no_promotion`. The next authorized technical action is to
verify accountable G2 evidence; agent-panel execution remains prohibited until that evidence is recorded.

