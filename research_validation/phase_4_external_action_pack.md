# Phase 4 External Action Pack

Status: **drafts only — no external action authorized**

This pack converts the Phase 4 gate docket into messages and decision records
that may be used only after the maintainer explicitly authorizes the named
external action. It contains no addresses, model and role identifiers, credentials,
source payloads, or evidence that any recipient has agreed.

## Required authorization sequence

1. The maintainer selects the specific docket packet and authorizes contact.
2. The responsible owner verifies the current official contact route and terms.
3. The sender fills only the bracketed fields, performs a privacy review, and
   sends outside this repository.
4. The response is preserved in an approved evidence store. Only a payload-safe
   URI, hash, pseudonymous authority record, scope, conditions, and date may be
   copied into the approval record.
5. An accountable decision owner records the outcome. No response or silence is
   approval, and no agent may advance the study automatically.

## Wave 2 verified routes and dispatch hold

The canonical, machine-checkable route package is
`research_validation/phase_4_wave_2_authority_routes.json`. The Spanish HPO
working group is still being formed, so its official project issue route is a
request for an authority decision, not evidence of one. The Japanese HPO page
identifies a working-group and external repository route; it likewise supplies
no approval until a bounded response is recorded.

The ethics/privacy request cannot be bound to an institution from repository
location or local Git identity. Use Flinders ResearchNow when Flinders is the
accountable sponsor and no NSW Health site, data, staff, or resources are in
scope. Use ISLHD pathway advice and REGIS when NSW Health or ISLHD sponsorship,
sites, data, staff, or resources are in scope. For cross-institutional work,
identify the lead HREC and obtain each required site or institutional governance
authorization. Until the maintainer selects one route and supplies an authorized
sender reference outside Git, all three requests remain unsent.

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
> We will not execute agents or begin candidate generation unless the
> relevant governance gates are separately approved.
>
> Kind regards,
> [authorized sender]

Spanish and Japanese require separate decisions. The community-governed slot
must remain unassigned until the relevant community selects the language and
defines consent, attribution, restriction, benefit, and withdrawal rules.

## Withdrawn Draft C — no people-based review

The former expression-of-interest draft is withdrawn and must not be sent.
Translation assessment uses the canonical specialist-agent panel. No people are
recruited, no evaluation roster is collected, and no consent, qualification,
conflict, workload, compensation, or personal-contact records are required for
translation review.

## Draft D — ethics and privacy determination cover note

Subject: Determination request — multilingual HPO terminology feasibility pilot

> Dear [ethics or privacy authority role],
>
> We request a determination for a bounded terminology feasibility pilot using
> non-identifiable ontology concepts and an isolated specialist-agent panel. The study will not
> use clinical records, make clinical-effectiveness claims, or promote official
> translations. Some terminology sources may be licensed or credentialed and
> will remain local-only if approved.
>
> Please advise whether any privacy or governance pathway applies to restricted
> source contexts, raw agent outputs, retention/deletion, incident response,
> cross-border compute, reporting, or community-governed model use.
> No restricted context processing will begin before any required formal
> determination and all other gates are satisfied.
>
> Kind regards,
> [authorized sender]

## Decision recording

Use `phase_4_decision_receipt.template.json` as a blank structure. Do not place
raw correspondence, signatures, names, addresses, credentials, qualification
documents, conflict disclosures, or restricted content in Git. Conditional
decisions require a bounded scope, explicit conditions, and a recheck date.
