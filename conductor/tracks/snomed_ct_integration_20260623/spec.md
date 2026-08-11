# Specification - Integrate SNOMED CT into terminology and translation support

## Objective
Introduce SNOMED CT as a governed terminology source for the HPO translation workflow where it improves concept alignment, multilingual review, or domain-specific validation.

## Source Profile
- Languages: Australian English, Canadian English, UK English, US English, Austrian German, German German, Belgian Dutch, Netherlands Dutch, Belgian French, Canadian French, French French, European Spanish, Spanish, Danish, Estonian, Finnish, Finnish Swedish, Lithuanian, Māori, Norwegian Bokmål, Norwegian Nynorsk, and Swedish Swedish.
- GitHub repositories:
- https://github.com/IHTSDO
- https://github.com/IHTSDO/snowstorm
- https://github.com/IHTSDO/snomed-owl-toolkit
- Source note: Use licensed SNOMED CT releases; GitHub repositories are tooling, not a substitute for release distribution rights.

## Usefulness
Clinical terminology crosswalks, post-coordination review, and clinical synonym support.

## Requirements
- Verify licensing, access constraints, and authoritative release channels before ingesting any source content.
- Capture source version, source URL, retrieval date, and any access constraints in generated artifacts.
- Keep external terminology labels separate from HPO translation candidates unless reviewed and explicitly imported.
- Prefer deterministic crosswalks and exact identifiers over free-text matching.
- Mark any LLM-assisted normalization or translation as candidate-only and agent-panel-assessment-required and maintainer-promotion-decision-required.

## Non-Goals
- Do not redistribute restricted terminology payloads in this repository.
- Do not treat external labels as approved HPO translations without agent-panel assessment and an accountable maintainer promotion decision.
