# Supplementary Source Access Review

## Decision

Nine supplementary sources were reviewed on 2026-08-01 and NANDO was added on 2026-08-12 using provider or primary project material. Metadata may be committed, but no terminology, translation, instrument, classification, or ontology payload was retrieved for this review. Every future payload request remains subject to the named accountable gate in `supplementary_source_access_reviews.json`.

| Source | Proposed role | Active profile overlap | Repository decision |
| --- | --- | --- | --- |
| DeCS | Multilingual biomedical lexicon | `es`, `fr`, `pt` | Provider agreement required |
| Mondo international | Disease context and Japanese labels | `ja` | Metadata probe allowed; payload review open |
| PRO-CTCAE | Patient-facing and regional register | `ar`, `cs`, `de`, `es`, `fr`, `it`, `ja`, `nl`, `pt`, `tr`, `zh` | Written NCI permission required |
| WHO ICF | Functional and disability context | `cs`, `es`, `fr`, `it`, `pt`, `tr`, `zh` | Maintainer licence decision and credentials required |
| NCI Thesaurus | Oncology and disease context | None established | Metadata probe allowed; source-atom review open |
| RadLex | Radiology context | None established | Maintainer clickthrough decision required |
| Uberon | Anatomy structure | Not lexical | Metadata probe allowed; payload review open |
| Cell Ontology | Cell-type structure | Not lexical | Metadata probe allowed; payload review open |
| NANDO | Japanese rare-disease context | `ja` | Metadata probe allowed; attribution and imported-lineage review open |
| PATO | Quality structure | Not lexical | Metadata probe allowed; payload review open |

The `tw` profile is deliberately excluded from the PRO-CTCAE overlap count. PRO-CTCAE lists Twi, but this repository still has an unresolved authority record for whether `tw` means Twi or Tiwi. The validator fails if any supplementary review counts an unresolved profile as overlap.

## Interpretation boundary

- A source can be useful for structural or contextual checks without supplying independent lexical evidence.
- An identifier cross-reference, mirror, or imported label retains its originating source lineage and cannot create a new vote.
- Public access does not itself authorize adaptation, mapping, translation, or redistribution.
- The licence phrases in the register are source-declared facts for decision support, not legal conclusions.
- A metadata-probe decision does not authorize payload retrieval or a pilot run.

## Primary evidence

- DeCS services and licence: https://decs.bvsalud.org/wp-content/uploads/2024/04/DeCS-services-EN.pdf and https://decs.bvsalud.org/I/DeCS-License-Agreement-20080801.pdf
- Mondo download and release: https://mondo.monarchinitiative.org/pages/download/ and https://github.com/monarch-initiative/mondo/releases/tag/v2026-07-06
- PRO-CTCAE terms, methods, languages, and release notes: https://healthcaredelivery.cancer.gov/pro-ctcae/terms_of_use.html, https://healthcaredelivery.cancer.gov/pro-ctcae/language.html, https://healthcaredelivery.cancer.gov/pro-ctcae/countries-pro.html, and https://healthcaredelivery.cancer.gov/pro-ctcae/notes.html
- WHO ICF releases, authentication, and licence: https://icd.who.int/docs/icd-api/SupportedClassifications/, https://icd.who.int/docs/icd-api/API-Authentication/, and https://icd.who.int/en/docs/icd11-license.pdf
- NCI EVS and NCIt terms: https://www.cancer.gov/about-nci/organization/cbiit/vocabulary, https://api-evsrest.nci.nih.gov/api/v1/metadata/terminologies, and https://evs.nci.nih.gov/ftp1/NCI_Thesaurus/ThesaurusTermsofUse.pdf
- RadLex official browser: https://radlex.org/RID/RID992
- NANDO ontology and pinned release: https://nanbyodata.jp/ontology/ and https://nanbyodata.jp/ontology/2025-08-26/nando.ttl
- Structural ontology registries and releases: https://obofoundry.org/ontology/uberon.html, https://obofoundry.org/ontology/cl.html, https://obofoundry.org/ontology/pato.html, and the release URLs recorded in the JSON register.
