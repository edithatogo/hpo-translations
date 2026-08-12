# Using Existing Translations to Improve HPO Translations

This plan connects the source, language, edition, and mapping catalogues to a reproducible analysis. It does not assume that an available translation is authorized, correct, independent, or equivalent to an HPO term.

## Intended uses

Existing translations can help HPO in five distinct ways:

1. Generate candidate preferred labels and synonyms from independently governed multilingual terminologies.
2. Triangulate lexical choices after collapsing copies and aggregators into their originating evidence lineages.
3. Detect ambiguity, false friends, register mismatch, and regional variation.
4. Test semantic fit using explicit mappings, ontology structure, and parent, child, and sibling hard negatives.
5. Prioritize gaps and release-drift risks even when source payloads cannot be used.

These roles are not interchangeable. Disease classifications provide context, not automatic phenotype-label equivalence. Structural ontologies support anatomy-quality decomposition, not lexical votes. UMLS, MedGen, Mondo, mirrors, and imported mappings remain discovery or lineage layers unless a distinct originating authority is demonstrated.

## Workflow

The machine-readable plan is `translation_source_utilisation_plan.json`.

| Stage | Action | Fail-closed boundary |
| --- | --- | --- |
| U0 | Join the catalogues, routes, editions, and language renditions into an eligibility matrix. | Metadata only; no source text is needed. |
| U1 | Pin and authorize the exact source payload, language variant, purpose, version, checksum, and custody rules. | No licence, community, ethics, or privacy decision can be supplied by an agent. |
| U2 | Generate source atoms with exact concepts, routes, derivations, and independent-evidence groups. | No unauthorized payload is retained or committed. |
| U3 | Construct blinded candidate conditions and hard negatives while withholding HPO references. | Mapping reachability and source counts cannot promote evidence. |
| U4 | Run the five isolated specialist agents, isolated adjudicator, and reproducibility auditor. | Agent agreement is an assessment, not rights or release authority. |
| U5 | Estimate candidate yield, lineage-aware agreement, route utility, discrimination, regional fit, source ablations, drift, and downstream utility. | Report languages and variants separately and preserve uncertainty. |
| U6 | Produce a candidate-only handoff and gap queue. | Every promotion still requires an explicit accountable maintainer decision. |

## Current and future studies

The current frozen pilot remains Spanish and Japanese. The existing HPO snapshots may be used only after the recorded language/community-use and ethics/privacy gates close. Adding another source payload, language, edition, regional variant, candidate condition, or analysis input invalidates the current scope and requires a new prospective freeze.

The first comparative analyses ask whether ontology-supported candidates outperform machine-translation-only and LLM-only baselines, and whether independent-lineage aggregation predicts agent-panel acceptance better than raw source counts. Source-role and route ablations then estimate which sources add useful candidates rather than repeated evidence. Regional analysis keeps `fr-CA`, `fr-FR`, and `fr-BE`—and analogous script or region variants—separate. Generic language evidence can be studied as unresolved, but it cannot substantiate an exact regional claim.

The plan also supports later confirmatory work on semantic discrimination, temporal drift, active prioritization, extraction, and phenotype ranking. Downstream utility cannot substitute for translation validity or clinical validation.

## Contingencies

- If a payload or licence is unavailable, retain the metadata feasibility result and exclude its atoms; do not use a mirror.
- If no direct HPO route exists, limit the source to discovery or a prespecified candidate-only mediated role.
- If lineage independence is unclear, count one conservative evidence group.
- If language, script, region, or register is unresolved, exclude exact-variant claims.
- If a release changes, finish the frozen analysis and create a new freeze for the new release.
- If accountable community or ethics gates remain open, follow the frozen step-down rule or remain synthetic-only.

No numerical result, majority vote, source count, route, or agent-panel outcome automatically changes an HPO translation.
