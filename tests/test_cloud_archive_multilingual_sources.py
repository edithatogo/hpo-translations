from scripts.cloud_archive_multilingual_sources import (
    LOINC_282_VARIANTS,
    github_catalog_artifacts,
    mesh_artifacts,
    orphanet_artifacts,
)


def test_orphanet_catalog_has_every_advertised_language_and_format() -> None:
    artifacts = orphanet_artifacts("2026-07")

    assert len(artifacts) == 34
    assert {artifact["language"] for artifact in artifacts} == {
        "cs",
        "de",
        "en",
        "es",
        "fr",
        "it",
        "nl",
        "pl",
        "pt",
        "tr",
        "uk",
        "zh",
    }
    assert sum(artifact["format"] == "xml" for artifact in artifacts) == 12
    assert sum(artifact["format"] == "json-tar-gz" for artifact in artifacts) == 12
    assert sum(artifact["format"] == "diff" for artifact in artifacts) == 10


def test_mp_catalog_includes_japanese_and_international_products() -> None:
    artifacts = github_catalog_artifacts("mp")

    assert any(artifact["path"].endswith("mp-ja.babelon.owl") for artifact in artifacts)
    assert any(artifact["path"].endswith("mp-ja.synonyms.tsv") for artifact in artifacts)
    assert any(artifact["path"].endswith("mp-international.owl") for artifact in artifacts)


def test_do_catalog_includes_spanish_and_international_products() -> None:
    artifacts = github_catalog_artifacts("do")

    assert any(artifact["path"].endswith("doid-es.obo") for artifact in artifacts)
    assert any(artifact["path"].endswith("doid-es.owl") for artifact in artifacts)
    assert any(artifact["path"].endswith("doid-international.owl") for artifact in artifacts)


def test_mesh_catalog_is_the_complete_official_nlm_xml_set() -> None:
    artifacts = mesh_artifacts("2026")

    assert {artifact["path"].rsplit("/", 1)[-1] for artifact in artifacts} == {
        "desc2026.xml",
        "pa2026.xml",
        "qual2026.xml",
        "supp2026.xml",
    }
    assert {artifact["language"] for artifact in artifacts} == {"en"}


def test_loinc_catalog_tracks_all_release_282_linguistic_variants() -> None:
    assert len(LOINC_282_VARIANTS) == 21
    assert {"ar-JO", "de-DE", "es-MX", "uk-UA", "zh-CN"} <= set(LOINC_282_VARIANTS)
