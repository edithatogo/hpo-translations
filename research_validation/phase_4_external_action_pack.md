# Phase 4 External Action Pack

Status: **drafts only — no external action authorized**

This pack converts the Phase 4 gate docket into messages and decision records
that may be used only after the maintainer explicitly authorizes the named
external action. It contains no addresses, reviewer identities, credentials,
source payloads, or evidence that any recipient has agreed.

## Required authorization sequence

1. The maintainer selects the specific docket packet and authorizes contact.
2. The responsible owner verifies the current official contact route and terms.
3. The sender fills only the bracketed fields, performs a privacy review, and
   sends outside this repository.
4. The response is preserved in an approved evidence store. Only a payload-safe
   URI, hash, pseudonymous authority record, scope, conditions, and date may be
   copied into the approval record.
5. A human decision owner records the outcome. No response or silence is
   approval, and no agent may advance the study automatically.

## Draft A — source permission or licence clarification

Subject: Permission clarification for a bounded multilingual HPO feasibility pilot

> Dear [authority role],
>
> We are preparing a small, non-clinical feasibility study concerning
> multilingual Human Phenotype Ontology terminology. We are considering
> [source and version] for the limited role of [semantic role] in [languages].
> Before retrieving or processing any content, we seek written clarification
> on whether the proposed use is permitted.
>
> The proposed scope is [bounded record count and study stage]. We would not
> redistribute source content, expose credentials, promote translations, or
> represent the source as an independent lexical vote where provenance is
> shared. Reporting would be aggregate and payload-safe.
>
> Could you confirm the permitted access method, version, transformation or
> mapping rights, storage and retention conditions, quotation/reporting limits,
> attribution requirements, and any expiry or re-review date? If the use is not
> permitted, we will omit the source.
>
> Kind regards,
> [authorized sender]

Packet-specific additions:

- `g1-pro-ctcae`: ask specifically about NCI permission for the bounded
  patient-facing comparator role in Spanish and Japanese.
- `g1-decs`: attach or reference the approved pre-licence materials only after
  institutional review; request explicit version and adaptation/mapping scope.
- `g1-mondo`: request confirmation of source-atom provenance handling and the
  pinned Japanese pilot scope before any payload probe.
- `g1-who-icf`: describe Spanish functional context only; do not claim Japanese
  overlap or lexical-vote use.
- `g1-structural-sources`: address Uberon and PATO separately and describe only
  structural or hard-negative design, never lexical voting.

## Draft B — language-working-group scope consultation

Subject: Request for a scope decision on a feasibility pilot for [language]

> Dear [language authority role],
>
> We are preparing, but have not started, a bounded feasibility pilot for HPO
> terminology in [language]. We seek your decision on whether the proposed
> language, register, audience, candidate-generation methods, and review model
> are appropriate. No translation will be promoted automatically.
>
> The proposed first stage contains [authorized unit count], uses blinded
> candidate provenance, and requires independent target-language, clinical, and
> ontology review plus independent adjudication. Please specify permitted scope,
> terminology-register requirements, attribution, model-use conditions,
> culturally restricted terms, withdrawal arrangements, and the authority that
> may approve or stop the work.
>
> We will not recruit reviewers or begin candidate generation unless the
> relevant governance gates are separately approved.
>
> Kind regards,
> [authorized sender]

Spanish and Japanese require separate decisions. The community-governed slot
must remain unassigned until the relevant community selects the language and
defines consent, attribution, restriction, benefit, and withdrawal rules.

## Draft C — reviewer expression of interest

Subject: Expression of interest — blinded multilingual HPO feasibility review

> Dear [prospective reviewer],
>
> Subject to ethics, privacy, language-authority, and source approvals, we are
> assessing availability for a blinded feasibility review in [language]. This
> message is an expression-of-interest request, not an appointment or request to
> review material.
>
> The planning estimate is up to [bounded minutes] in Stage 1, including
> training. Roles require target-language terminology, clinical, or
> ontology/phenotype expertise. Independent adjudicators must not generate
> candidates or serve as an initial reviewer for adjudicated items.
>
> Before any participation, the project would provide an approved information
> statement covering consent, privacy, conflicts, retention, withdrawal,
> attribution, workload, and any compensation. Please do not send qualifications
> or personal information until an approved secure collection route is supplied.
>
> Kind regards,
> [authorized sender]

The repository must retain pseudonyms only. Qualifications, identities, contact
details, consent records, and conflict disclosures remain in the approved
local-only evidence store.

## Draft D — ethics and privacy determination cover note

Subject: Determination request — multilingual HPO terminology feasibility pilot

> Dear [ethics or privacy authority role],
>
> We request a determination for a bounded terminology feasibility pilot using
> non-identifiable ontology concepts and blinded human review. The study will not
> use clinical records, make clinical-effectiveness claims, or promote official
> translations. Some terminology sources may be licensed or credentialed and
> will remain local-only if approved.
>
> Please advise the applicable review pathway and requirements for reviewer
> consent, pseudonymisation, conflicts, time data, retention/deletion, incident
> response, withdrawal, cross-border access, reporting, and any community
> governance. No reviewer data collection will begin before a formal
> determination and all other gates are satisfied.
>
> Kind regards,
> [authorized sender]

## Decision recording

Use `phase_4_decision_receipt.template.json` as a blank structure. Do not place
raw correspondence, signatures, names, addresses, credentials, qualification
documents, conflict disclosures, or restricted content in Git. Conditional
decisions require a bounded scope, explicit conditions, and a recheck date.
