# Specification - Integrate UMLS Metathesaurus into terminology and translation support

## Objective
Introduce UMLS Metathesaurus as a governed terminology source for the HPO translation workflow where it improves concept alignment, multilingual review, or domain-specific validation.

## Source Profile
- Languages: 31 languages including Arabic, Basque, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, German, Greek, Hebrew, Hungarian, Icelandic, Italian, Japanese, Korean, Latvian, Lithuanian, Norwegian, Polish, Portuguese, Russian, Slovak, Slovenian, Spanish, Swedish, Turkish, and Ukrainian.
- GitHub repositories:
- https://github.com/HHS/uts-rest-api
- Source note: Archived UTS REST API samples; use official UMLS licensing and current NLM documentation as the authority.

## Usefulness
Cross-terminology concept anchoring across UMLS CUIs and source vocabularies.

## Requirements
- Verify licensing, access constraints, and authoritative release channels before ingesting any source content.
- Capture source version, source URL, retrieval date, and any access constraints in generated artifacts.
- Keep external terminology labels separate from HPO translation candidates unless reviewed and explicitly imported.
- Prefer deterministic crosswalks and exact identifiers over free-text matching.
- Mark any LLM-assisted normalization or translation as candidate-only and agent-panel-assessment-required and maintainer-promotion-decision-required.

## Non-Goals
- Do not redistribute restricted terminology payloads in this repository.
- Do not treat external labels as approved HPO translations without agent-panel assessment and an accountable maintainer promotion decision.
