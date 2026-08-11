# Project Tracks

This file tracks all major tracks for the project. Each track has its own detailed plan in its respective folder.

<!-- conductor-automation-index:start -->
## Automation Index

| Track | Status | Priority | Source Access | Depends On | Blocks | Parallel Group | CI | Review | Merge |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `migrate_to_pixi_20260622` | `legacy_complete` | `legacy` | `not_applicable` | `-` | `translation_agents_20260622` | `foundation` | `not_started` | `codex_legacy_review_completed` | `legacy_unverified` |
| `translation_agents_20260622` | `legacy_complete` | `legacy` | `not_applicable` | `migrate_to_pixi_20260622` | `ontology_network_20260623, language_candidate_tracks` | `foundation` | `not_started` | `codex_legacy_review_completed` | `legacy_unverified` |
| `research_validation_20260801` | `in_progress` | `P0` | `mixed_public_and_restricted_metadata_only` | `conductor_validation_20260623, translation_agents_20260622, ontology_network_20260623:phase_1_registry_contract` | `language_candidate_tracks` | `research-validation` | `local_passing_unpublished_continuation` | `prior_batch_reviewed_current_continuation_unreviewed` | `prior_batch_merged_current_continuation_unpublished` |
| `conductor_validation_20260623` | `archived` | `P0` | `not_applicable` | `migrate_to_pixi_20260622, translation_agents_20260622` | `ontology_network_20260623, all_future_conductor_tracks` | `conductor-validation` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `ontology_network_20260623` | `archived` | `P0` | `mixed_network_sources` | `conductor_validation_20260623:phase_1_metadata_schema, translation_agents_20260622` | `umls_metathesaurus_integration_20260623, snomed_ct_integration_20260623, meddra_integration_20260623, icd10_integration_20260623, icd11_integration_20260623, loinc_integration_20260623, mesh_integration_20260623, orphanet_integration_20260623, omim_integration_20260623, decipher_integration_20260623, fma_integration_20260623, pato_integration_20260623, mp_integration_20260623, upheno_integration_20260623, efo_integration_20260623, do_integration_20260623, oncotree_integration_20260623, lddb_integration_20260623` | `ontology-network` | `not_applicable` | `archive_review_completed` | `blocked` |
| `umls_metathesaurus_integration_20260623` | `archived` | `P2` | `license_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `snomed_ct_integration_20260623` | `archived` | `P2` | `license_or_affiliate_release_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `meddra_integration_20260623` | `archived` | `P2` | `subscription_or_license_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `icd10_integration_20260623` | `archived` | `P2` | `public_or_national_variant_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `icd11_integration_20260623` | `archived` | `P1` | `public_api_metadata_only_terms_recorded` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `loinc_integration_20260623` | `archived` | `P2` | `free_account_license_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `mesh_integration_20260623` | `archived` | `P1` | `public_download_terms_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `orphanet_integration_20260623` | `archived` | `P1` | `public_download_terms_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `omim_integration_20260623` | `archived` | `P2` | `api_key_or_license_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `decipher_integration_20260623` | `archived` | `P2` | `permission_or_api_terms_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `fma_integration_20260623` | `archived` | `P3` | `public_ontology_terms_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `pato_integration_20260623` | `archived` | `P1` | `open_ontology_download_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `mp_integration_20260623` | `archived` | `P1` | `open_ontology_download_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `upheno_integration_20260623` | `archived` | `P1` | `open_ontology_download_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `efo_integration_20260623` | `archived` | `P1` | `open_ontology_download_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `do_integration_20260623` | `archived` | `P1` | `open_ontology_download_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `oncotree_integration_20260623` | `archived` | `P1` | `open_api_terms_review_required` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
| `lddb_integration_20260623` | `archived` | `P3` | `source_authority_and_access_unknown` | `translation_agents_20260622, ontology_network_20260623:phase_1_registry_schema` | `ontology_network_20260623:phase_3_identifier_network, ontology_network_20260623:phase_4_non_translation_outputs` | `ontology-source-governance` | `not_applicable` | `archive_review_completed` | `not_applicable` |
<!-- conductor-automation-index:end -->

---

## [x] Track: Migrate project environment and automation workflows from uv/Makefile to pixi and configure code quality tools (ruff and vale)
*Link: [./tracks/migrate_to_pixi_20260622/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/migrate_to_pixi_20260622/)*

---

## [x] Track: Implement translation completeness audits and automated translation using LLM coding agents
*Link: [./tracks/translation_agents_20260622/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/translation_agents_20260622/)*


---

## [x] Track: Implement automated Conductor validation and lifecycle gates
*Link: [./tracks/conductor_validation_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/conductor_validation_20260623/)*

---

## [x] Track: Integrate UMLS Metathesaurus into terminology and translation support (archived — blocked on license_required)
*Link: [./tracks/umls_metathesaurus_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/umls_metathesaurus_integration_20260623/)*

---

## [x] Track: Integrate SNOMED CT into terminology and translation support (archived — blocked on license_or_affiliate_release_required)
*Link: [./tracks/snomed_ct_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/snomed_ct_integration_20260623/)*

---

## [x] Track: Integrate MedDRA into terminology and translation support (archived — blocked on subscription_or_license_required)
*Link: [./tracks/meddra_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/meddra_integration_20260623/)*

---

## [x] Track: Integrate ICD-10 into terminology and translation support (archived — blocked on public_or_national_variant_review_required)
*Link: [./tracks/icd10_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/icd10_integration_20260623/)*

---

## [x] Track: Integrate ICD-11 into terminology and translation support (archived — blocked on source_label_and_payload_review_required)
*Link: [./tracks/icd11_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/icd11_integration_20260623/)*

---

## [x] Track: Integrate LOINC into terminology and translation support (archived — blocked on free_account_license_review_required)
*Link: [./tracks/loinc_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/loinc_integration_20260623/)*

---

## [x] Track: Integrate MeSH into terminology and translation support (archived — blocked on public_download_terms_review_required)
*Link: [./tracks/mesh_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/mesh_integration_20260623/)*

---

## [x] Track: Integrate Orphanet into terminology and translation support (archived — blocked on public_download_terms_review_required)
*Link: [./tracks/orphanet_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/orphanet_integration_20260623/)*

---

## [x] Track: Integrate OMIM into terminology and translation support (archived — blocked on api_key_or_license_required)
*Link: [./tracks/omim_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/omim_integration_20260623/)*

---

## [x] Track: Integrate DECIPHER into terminology and translation support (archived — blocked on permission_or_api_terms_required)
*Link: [./tracks/decipher_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/decipher_integration_20260623/)*

---

## [x] Track: Integrate FMA into terminology and translation support (archived — blocked on public_ontology_terms_review_required)
*Link: [./tracks/fma_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/fma_integration_20260623/)*

---

## [x] Track: Integrate PATO into terminology and translation support (archived — blocked on open_ontology_download_review_required)
*Link: [./tracks/pato_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/pato_integration_20260623/)*

---

## [x] Track: Integrate Mammalian Phenotype Ontology into terminology and translation support (archived — blocked on open_ontology_download_review_required)
*Link: [./tracks/mp_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/mp_integration_20260623/)*

---

## [x] Track: Integrate uPheno into terminology and translation support (archived — blocked on open_ontology_download_review_required)
*Link: [./tracks/upheno_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/upheno_integration_20260623/)*

---

## [x] Track: Integrate EFO into terminology and translation support (archived — blocked on open_ontology_download_review_required)
*Link: [./tracks/efo_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/efo_integration_20260623/)*

---

## [x] Track: Integrate Disease Ontology into terminology and translation support (archived — blocked on open_ontology_download_review_required)
*Link: [./tracks/do_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/do_integration_20260623/)*

---

## [x] Track: Integrate OncoTree into terminology and translation support (archived — blocked on open_api_terms_review_required)
*Link: [./tracks/oncotree_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/oncotree_integration_20260623/)*

---

## [x] Track: Integrate LDDB into terminology and translation support (archived — blocked on source_authority_and_access_unknown)
*Link: [./tracks/lddb_integration_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/lddb_integration_20260623/)*

---

## [x] Track: Define ontology network outputs for terminology triangulation, validation, and downstream artifacts
*Link: [./tracks/ontology_network_20260623/](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/biomedical/hpo-translations/conductor/tracks/ontology_network_20260623/)*

---

## [~] Track: Establish empirical validation for multilingual HPO translation and ontology evidence
*Link: [./tracks/research_validation_20260801/index.md](./tracks/research_validation_20260801/index.md)*
