# Multilingual HPO Translation Validation Protocol

## Status and scope

This is a draft pilot protocol intended to become preregistrable; it is not a completed preregistration or empirical result. It covers payload-safe evaluation of translation candidates. Source ingestion, candidate generation, community-use decisions, applicable ethics/privacy review, and publication remain blocked until their responsible owners approve them. No people will be recruited for translation review.

The pilot will compare four candidate conditions where licensing and agent capacity permit:

1. machine translation only;
2. language-model generation without ontology evidence;
3. language-model generation with ontology and terminology evidence;
4. an authorized human or upstream reference translation used only as an evaluation comparator.

Approved reference translations must be withheld from candidate generators and must not be used as evidence for themselves.

## Version and approval freeze

Before any empirical run, record the HPO release, every source release, retrieval date, model and endpoint version, prompt version, sampling code commit, random seed, instrument version, and analysis code commit. A run cannot advance beyond a synthetic schema probe while any selected source is unpinned.

The run manifest must also record license, ethics, community, and language-working-group decisions. A pending or rejected required approval is a stop condition. Restricted payloads, model and role identifiers, identifiable clinical text, and unredistributable model context remain local-only.

## Pilot sampling frame

Select 50 to 100 HPO concepts before candidate generation. Stratify the sample across:

- at least three contrasting HPO branches;
- ontology depth and local sibling density;
- short, long, and compositional terms;
- labels, definitions, synonyms, regional variants, and patient-facing renderings;
- source agreement and disagreement;
- changed and unchanged concepts across the frozen HPO releases;
- language resource level, script, region, register, and translation status; and
- plausible clinical consequence, without claiming a clinical-risk ranking before expert review.

For every benchmark item, construct at least one parent, child, or close-sibling hard negative. Exclude obsolete identifiers, items whose identity cannot be frozen, leaked reference translations, and content whose license or community rules prohibit the planned use. Record every exclusion before unblinding.

## Specialist-agent assessment and adjudication

Use randomized presentation order and blind each isolated specialist agent to candidate method and source popularity. Run the five canonical roles for every candidate. Lock their decisions before a separately isolated adjudication agent sees them. A non-voting reproducibility auditor verifies model, prompt, input, isolation, and aggregation receipts. Missing roles fail admission.

Agents record accept without edit, accept with edit, reject, or abstain; clinically significant error; error categories; confidence; and review time. Agent identifiers are pseudonymous in committed artifacts. Conflicts of interest, qualifications, consent, withdrawal, attribution, and culturally restricted-term handling are maintained in approved local governance records.

Disagreements proceed to documented adjudication by an authorized agent who has not generated the candidate. Preserve both independent decisions and the adjudicated result. No score or majority vote promotes a candidate automatically.

## Error taxonomy

Prespecify these non-exclusive categories: polarity or negation; anatomy or body site; laterality; severity or frequency; onset or temporal course; inheritance or causal implication; granularity; omission; addition; ambiguity; misleading cognate; terminology register; regional mismatch; grammar; and other with a mandatory explanation. Clinically significant error is a separate binary outcome and requires the isolated clinical-safety specialist plus independent agent adjudication. This assessment does not constitute clinical validation or promotion authority.

## Outcomes

The primary outcomes are:

- clinically significant error rate;
- acceptance without edit;
- normalized character- and token-level edit burden;
- agent runtime and compute cost;
- discrimination of the intended HPO concept from hard negatives; and
- calibrated confidence against adjudicated acceptance.

Secondary outcomes include overall acceptance, error-category frequencies, inter-agent agreement, abstention, results by translation-object type, regional and register variants, language-resource tier, and downstream HPO extraction or phenotype-ranking performance where public or approved data permit.

## Analysis plan

Estimate effects with language- and concept-aware hierarchical models or mixed-effects models, treating candidate method as the main fixed effect and agent, language, and concept as grouping factors where the data support them. Report effect sizes and 95% uncertainty intervals alongside exact denominators. Do not substitute pooled performance for language-specific results.

Use a prespecified lineage ablation to compare naive source counts with independent-evidence-group aggregation. Evaluate hard-negative discrimination separately from lexical similarity. Assess confidence with calibration curves and Brier score. Adjust confirmatory comparisons for multiplicity; label all other analyses exploratory.

The pilot estimates agent-role and concept variance, event prevalence, intraclass correlation, attrition, and feasible effect size. Use those estimates to calculate the confirmatory sample size. The pilot does not stop early for apparent benefit; it may stop for safety, invalid blinding, prohibited source use, inadequate agent coverage, or unusable measurement reliability.

## Feasibility staging and progression

The Conductor [Phase 4 options and contingencies](../conductor/tracks/research_validation_20260801/phase_4_options.md) are the canonical decision record for pilot scale, progression thresholds, and fallback branches. Their recommended default is a payload-free 12-item synthetic operational rehearsal, followed by an authorized 12-concept-language-unit Stage 1 and then the remainder of the selected design only when the frozen progression criteria pass. Balance Stage 1 across approved languages and include at least two common anchors where the design is multilingual. The recommendation is not active until the maintainer records the G0 design and workload decision.

Stage 0 tests only sampling, randomization, blinding, export, adjudication, redaction, and failure handling; it cannot produce empirical translation or agent-variance evidence. Stage 1 assesses feasibility and may trigger go, one prospective revision, or stop. Report feasibility measures and estimates with 95% uncertainty intervals. Do not use formal effectiveness hypothesis tests, significance thresholds, or apparent candidate-method benefit as progression rules.

An internal checksummed freeze is mandatory before empirical work. External registration remains a maintainer-controlled action. If no immutable external registration has occurred, describe the protocol as prospectively frozen rather than preregistered.

## Downstream and temporal studies

If suitable public or approved corpora exist, compare translated-text HPO extraction and phenotype-driven ranking using the frozen candidates. Keep extraction accuracy and ranking utility separate from translation acceptance. Replay at least two HPO releases to test drift prediction, and use a temporal or held-out-language split where feasible to reduce benchmark leakage.

## Reproducibility and reporting

Publish only payload-safe protocols, schemas, code, aggregate results, permitted identifiers, and provenance. Report missing languages, agent-role execution gaps, approval constraints, source dependence, model changes, exclusions, and all deviations from this protocol. Schema validation is reported as contract validation only; empirical readiness requires nonzero version-pinned records and complete agent-panel receipts and deterministic reproduction.
