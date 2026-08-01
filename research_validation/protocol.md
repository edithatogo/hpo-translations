# Multilingual HPO Translation Validation Protocol

## Status and scope

This is a draft pilot protocol intended to become preregistrable; it is not a completed preregistration or empirical result. It covers payload-safe evaluation of translation candidates. Source ingestion, candidate generation, reviewer recruitment, community engagement, ethics review, and publication remain blocked until their responsible owners approve them.

The pilot will compare four candidate conditions where licensing and reviewer capacity permit:

1. machine translation only;
2. language-model generation without ontology evidence;
3. language-model generation with ontology and terminology evidence;
4. an authorized human or upstream reference translation used only as an evaluation comparator.

Approved reference translations must be withheld from candidate generators and must not be used as evidence for themselves.

## Version and approval freeze

Before any empirical run, record the HPO release, every source release, retrieval date, model and endpoint version, prompt version, sampling code commit, random seed, instrument version, and analysis code commit. A run cannot advance beyond a synthetic schema probe while any selected source is unpinned.

The run manifest must also record license, ethics, community, and language-working-group decisions. A pending or rejected required approval is a stop condition. Restricted payloads, reviewer identities, identifiable clinical text, and unredistributable model context remain local-only.

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

## Human review and adjudication

Use randomized presentation order and blind reviewers to candidate method and source popularity. Seek three independent reviewers per language where feasible, collectively covering target-language, clinical, ontology, and relevant community expertise. When that is infeasible, report the achieved roles and reviewer count rather than implying equivalent assurance.

Reviewers record accept without edit, accept with edit, reject, or abstain; clinically significant error; error categories; confidence; and review time. Reviewer identifiers are pseudonymous in committed artifacts. Conflicts of interest, qualifications, consent, withdrawal, attribution, and culturally restricted-term handling are maintained in approved local governance records.

Disagreements proceed to documented adjudication by an authorized reviewer who has not generated the candidate. Preserve both independent decisions and the adjudicated result. No score or majority vote promotes a candidate automatically.

## Error taxonomy

Prespecify these non-exclusive categories: polarity or negation; anatomy or body site; laterality; severity or frequency; onset or temporal course; inheritance or causal implication; granularity; omission; addition; ambiguity; misleading cognate; terminology register; regional mismatch; grammar; and other with a mandatory explanation. Clinically significant error is a separate binary outcome and requires clinical adjudication.

## Outcomes

The primary outcomes are:

- clinically significant error rate;
- acceptance without edit;
- normalized character- and token-level edit burden;
- reviewer time;
- discrimination of the intended HPO concept from hard negatives; and
- calibrated confidence against adjudicated acceptance.

Secondary outcomes include overall acceptance, error-category frequencies, inter-reviewer agreement, abstention, results by translation-object type, regional and register variants, language-resource tier, and downstream HPO extraction or phenotype-ranking performance where public or approved data permit.

## Analysis plan

Estimate effects with language- and concept-aware hierarchical models or mixed-effects models, treating candidate method as the main fixed effect and reviewer, language, and concept as grouping factors where the data support them. Report effect sizes and 95% uncertainty intervals alongside exact denominators. Do not substitute pooled performance for language-specific results.

Use a prespecified lineage ablation to compare naive source counts with independent-evidence-group aggregation. Evaluate hard-negative discrimination separately from lexical similarity. Assess confidence with calibration curves and Brier score. Adjust confirmatory comparisons for multiplicity; label all other analyses exploratory.

The pilot estimates reviewer variance, event prevalence, intraclass correlation, attrition, and feasible effect size. Use those estimates to calculate the confirmatory sample size. The pilot does not stop early for apparent benefit; it may stop for safety, invalid blinding, prohibited source use, inadequate reviewer coverage, or unusable measurement reliability.

## Downstream and temporal studies

If suitable public or approved corpora exist, compare translated-text HPO extraction and phenotype-driven ranking using the frozen candidates. Keep extraction accuracy and ranking utility separate from translation acceptance. Replay at least two HPO releases to test drift prediction, and use a temporal or held-out-language split where feasible to reduce benchmark leakage.

## Reproducibility and reporting

Publish only payload-safe protocols, schemas, code, aggregate results, permitted identifiers, and provenance. Report missing languages, reviewer gaps, approval constraints, source dependence, model changes, exclusions, and all deviations from this protocol. Schema validation is reported as contract validation only; empirical readiness requires nonzero version-pinned records and completed authorized human review.
