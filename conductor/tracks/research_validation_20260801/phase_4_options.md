# Phase 4 Options, Contingencies, and Recommendation

## Decision status

The user accepted the recommended path on 2026-08-02: Option A is the target,
Option D is the immediate route, and the language-selection rule and progression
defaults are accepted for prospective freeze. The payload-free Stage 0 rehearsal
has passed. G0 is complete with a provisional 30-hour Stage 1 release cap and a
120-hour full-pilot ceiling. This closes design capacity planning only; it does
not activate empirical work or authorize reviewer contact or expenditure.

The current source-access review authorizes zero payload retrievals, no reviewer
roster is approved, and external preregistration requires explicit maintainer
approval. No empirical pilot is active.

### Decision receipt

| Decision | State |
| --- | --- |
| Target design | Option A selected |
| Immediate route | Option D completed |
| Language-selection rule | Accepted; named languages remain unselected |
| Progression defaults | Accepted; must be checksummed again at G3 before empirical data |
| Maximum reviewer-time budget | Provisional G0 envelope recorded: 30-hour Stage 1 cap, 120-hour full-pilot ceiling; expansion requires observed Stage 1 reforecast |
| Stage 1 approvals | All pending in `research_validation/approval_manifest.json` |
| External preregistration, publication, push, and PR | Not authorized |

The deterministic receipt at `research_validation/stage_0/receipt.json` records
12 synthetic items, 48 blinded candidate rows, 144 synthetic assignments and
decisions, 24 synthetic adjudications, temporary export hashes, redaction checks,
and all go/revise/stop branches. It establishes operational readiness only.

## What Phase 4 must decide

Phase 4 is a feasibility pilot, not a small confirmatory trial. It must establish
whether the team can lawfully and reproducibly generate candidates, blind and
complete review, measure the prespecified outcomes, estimate reviewer and concept
variance, and size a later confirmatory study. Apparent method superiority is not
a Phase 4 progression criterion.

## Design options

Workload estimates assume four candidate conditions and three independent
reviews for every concept-language unit. They exclude training, adjudication,
governance, and instrument-revision time. A concept-language unit is one HPO
concept evaluated in one language across all candidate conditions.

| Option | Design | Nominal independent judgments | What it can answer | Main limitation |
| --- | --- | ---: | --- | --- |
| **A. Staged three-language pilot (recommended)** | 60 unique HPO concepts: 10 common anchors in all three languages plus 50 additional concept-language assignments, for 80 concept-language units | 960 | Whether the full workflow is feasible across contrasting language situations; preliminary variance, error prevalence, calibration, and workload estimates | Highest reviewer and approval burden; not powered for method superiority |
| **B. Lean two-language pilot** | 50 unique concepts: 10 common anchors in both languages plus 40 additional assignments, for 60 concept-language units | 720 | Cross-language feasibility and preliminary variance with lower coordination cost | Weak evidence about resource-tier, script, and governance heterogeneity |
| **C. Single-language measurement pilot** | 50 concepts in one approved language | 600 | Instrument reliability, reviewer burden, error prevalence, and workflow feasibility in that language | Cannot support multilingual or cross-language claims |
| **D. Governance-only rehearsal** | 12 synthetic items with no source or candidate payloads | Not an empirical sample | Whether schemas, randomization, blinding, export, adjudication, redaction, and failure handling work | Produces no translation-quality or reviewer-variance evidence |

### Language selection rule

For Option A, fill language slots only after approvals and reviewer capacity are
documented:

1. one relatively high-resource language with an approved source path and
   clinical-language reviewers;
2. one language with a contrasting script or typology and qualified reviewers;
3. one lower-resource or community-governed language only where the relevant
   authority approves model use and study participation.

If the third slot cannot be ethically and operationally filled, use Option B or
substitute an approved medium-resource language and narrow the inference. Do not
select a language merely because an accessible mirror or aggregator contains
labels. Exclude the unresolved `tw` profile until its Tiwi/Twi authority and
migration direction are resolved.

## Recommendation

The selected path adopts **Option A as the target** and has completed **Option D
as the immediate, payload-free Stage 0**. After the remaining gates close,
freeze a prospective package and run an authorized 12-concept-language-unit
Stage 1 before committing the remaining review budget. Balance those units
across the approved languages and,
when the design has more than one language, include at least two common anchors.
Continue to the full Option A sample only if the prespecified progression
criteria pass.

This staged design preserves the scientific value of language contrast while
limiting avoidable reviewer burden. The common anchors estimate cross-language
measurement behaviour; the additional assignments broaden phenotype and
linguistic coverage. Option B is the preferred planned fallback, Option C is a
measurement-only fallback, and Option D remains the safe fallback if empirical
permissions do not close.

## Gate sequence

| Gate | Required evidence | If the gate does not close |
| --- | --- | --- |
| **G0 — Design authority** | Maintainer records Option A, B, C, or D; language-slot rule; reviewer-time budget; and default progression thresholds | Remain at Option D |
| **G1 — Source authority** | Selected HPO and terminology versions are pinned; source authority, access, license, permitted use, storage, and reporting decisions are approved | Omit the source or shrink the design; never substitute a mirror as new authority |
| **G2 — Human and community authority** | Reviewer qualifications, consent, privacy, conflicts, adjudication capacity, ethics determination, language-working-group approval, and community model-use authority where applicable | Substitute an approved language or step down A → B → C → D |
| **G3 — Prospective freeze** | Sampling frame, items, conditions, prompts, model/endpoints, versions, seeds, exclusions, instrument, progression criteria, and analysis code are checksummed before empirical data | Do not start empirical review |
| **G4 — Stage 1 feasibility** | The first 12 authorized concept-language units complete without a stop condition and meet the frozen progression rule | Revise once under a logged amendment, or stop |
| **G5 — Pilot completion** | Remaining authorized sample, adjudication, descriptive analysis, deviation log, payload-safe report, and full-study sample-size recommendation are complete | Retain a feasibility-only conclusion |

An internal, checksummed prospective freeze is required. Registration on OSF or
another external service is optional and may occur only after explicit maintainer
approval. Without an immutable external registration, describe the artifact as a
“prospectively frozen protocol,” not a completed preregistration.

## Recommended progression criteria

These are defaults for owner review. G0 must approve or amend them, and G3 must
freeze them before any empirical data are inspected.

### Go

- all required source, license, ethics, language, reviewer, and community
  decisions are approved;
- three independent reviewers per language are available;
- at least 90% of assigned independent reviews and 90% of required adjudications
  are completed within the approved workload window;
- fewer than 10% of Stage 1 concept-language units are technically invalid;
- blinding remains viable; and
- there is no license, privacy, security, consent, or community-authority incident.

### Revise once under a prospective amendment

- only two independent reviewers per language are available but an independent
  adjudicator remains available;
- review or adjudication completion is 70–89%;
- 10–20% of Stage 1 concept-language units are technically invalid; or
- recoverable problems occur in the instrument, blinding, abstention rate, or
  reviewer workload.

A revised run remains feasibility evidence and must not be represented as if it
followed the original protocol without deviation.

### Stop or step down

- a required permission or authority is refused, expires, or is revoked;
- fewer than two independent reviewers are available for an empirical language;
- more than 20% of Stage 1 concept-language units are technically invalid;
- a material license, privacy, security, consent, or community-authority incident
  occurs; or
- the instrument cannot distinguish semantic error, language quality, and
  abstention reliably enough to estimate the planned outcomes.

Do not stop early for apparent candidate-method benefit. Phase 4 analyses should
report feasibility measures and estimates with 95% uncertainty intervals, not
formal effectiveness hypothesis tests or significance-based progression.

## Contingency matrix

| Trigger | Response | Permitted conclusion |
| --- | --- | --- |
| Three approved languages and three reviewers per language | Option A | Multilingual feasibility across the selected language situations |
| Two approved languages | Option B | Two-language feasibility only |
| One approved language | Option C | Measurement and workflow feasibility in that language only |
| No approved payload, language, or reviewer roster | Option D | Operational readiness only |
| Two reviewers plus an independent adjudicator | Use the revise branch; report reduced assurance and do not estimate three-reviewer reliability | Feasibility only |
| One or zero reviewers | Do not run empirical review | No human-validation claim |
| Selected source remains unavailable or unlicensed | Omit its condition or evidence field before the freeze; do not scrape or replace it with a mirror | No claim about that source's incremental value |
| PRO-CTCAE permission does not close | Omit its content and the source-specific patient-facing comparison | Other approved outcomes only |
| WHO credentialed access does not close | Omit the credentialed ICF context | Other approved sources only |
| DeCS version or distribution route remains unresolved | Omit DeCS | No DeCS-based triangulation claim |
| HPO or a source releases during the pilot | Keep the frozen release, record drift, and test the new release later | Validity for the frozen versions only |
| Model endpoint or version changes | Stop the batch; create a new frozen run identifier or omit the condition | No pooled claim across model versions |
| High disagreement or abstention | Inspect only prespecified feasibility summaries, revise definitions or training prospectively, and rerun under an amendment | Measurement feasibility, not method quality |
| Accidental unblinding or payload disclosure | Quarantine affected records, perform the incident process, and rerun only if authorization remains | Unaffected data only, with the deviation disclosed |
| Community approval is unavailable | Substitute an approved language or step down the design | No inference to the unavailable community |
| `tw` remains ambiguous | Exclude it | No Tiwi or Twi claim |

## Decision record and downstream owner gates

G0 records items 1–5 below. They are complete under the provisional budget and
remain subject to the G3 checksum freeze. Items 6–8 are downstream gates and
remain pending:

1. selected option and maximum reviewer-time budget;
2. language-selection rule and any named candidate languages;
3. whether Stage 1 uses 12 concept-language units, balanced across languages with
   at least two common anchors, or a justified alternative;
4. go, revise, and stop thresholds;
5. whether two reviewers plus an adjudicator is an acceptable feasibility-only
   fallback;
6. **Pending G1:** authorized source set and owner for each unresolved permission;
7. **Pending G2:** ethics, privacy, reviewer-consent, and community-approval
   owners; and
8. **Not authorized:** external preregistration after the prospective freeze.

## Rationale and methodological sources

- The CONSORT extension for randomized pilot and feasibility trials centres pilot
  objectives on feasibility, asks protocols to define progression criteria, and
  recommends choosing sample size for feasibility objectives rather than formal
  effectiveness testing: <https://www.bmj.com/content/355/bmj.i5239>.
- OSF registrations provide a time-stamped, read-only version of a study plan;
  this supports the distinction between an internal prospective freeze and an
  externally registered preregistration:
  <https://help.osf.io/article/330-welcome-to-registrations>.
- The PRO-CTCAE translation program documents dual forward translation,
  reconciliation/back translation, bilingual clinical review, proofing, and
  cognitive testing. It supports multi-role human review as a methodological
  triangulation source, but does not grant reuse permission for its payloads:
  <https://healthcaredelivery.cancer.gov/pro-ctcae/language.html>.
- Reporting should be selected against the final design and checked through the
  EQUATOR Network rather than treating a pilot label as sufficient:
  <https://www.equator-network.org/reporting-guidelines-study-design/experimental-studies/>.

## Claims boundary

Phase 4 may establish operational feasibility, reviewer and concept variance,
event prevalence, workload, measurement reliability, and a defensible
confirmatory sample size. It may not establish official HPO translations,
clinical safety, source independence beyond documented lineage, broad
cross-language generalizability, or candidate-method superiority. Those claims
require the authorized confirmatory and downstream studies in Phase 5.
