# /// script
# requires-python = ">=3.11"
# dependencies = ["huggingface-hub>=0.34,<2", "httpx>=0.27,<1"]
# ///
"""Archive governed multilingual source artifacts directly to a private HF dataset.

This program is intended to run as a Hugging Face Job. Source payloads are
downloaded into the Job's ephemeral filesystem, uploaded one at a time, and
then removed. Only provenance receipts and automation live in this repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

ORPHADATA_LANGUAGES = (
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
)
ORPHADATA_DIFF_LANGUAGES = tuple(language for language in ORPHADATA_LANGUAGES if language not in {"tr", "zh"})


def hf_api(token: str) -> Any:
    """Load the upload client only when the archive command actually runs."""
    from huggingface_hub import HfApi  # type: ignore[import-not-found]

    return HfApi(token=token)


GITHUB_MULTILINGUAL_CATALOGS: dict[str, dict[str, Any]] = {
    "do": {
        "source": "Disease Ontology",
        "release": "v2026-07-31",
        "repository": "DiseaseOntology/HumanDiseaseOntology",
        "licence": "CC0-1.0",
        "languages": ["en", "es"],
        "paths": [
            "src/ontology/releases/translations/doid-es.obo",
            "src/ontology/releases/translations/doid-es.owl",
            "src/ontology/releases/translations/doid-international.owl",
            "src/translations/README-translation.md",
            "src/translations/doid-es-all.tsv",
            "src/translations/doid-es-changed.tsv",
            "src/translations/doid-es-deprecated.tsv",
            "src/translations/doid-es-translated.tsv",
            "src/translations/doid-es-untranslated.tsv",
            "src/translations/doid-es.tsv",
        ],
    },
    "mp": {
        "source": "Mammalian Phenotype Ontology",
        "release": "v2026-07-22",
        "repository": "obophenotype/mammalian-phenotype-ontology",
        "licence": "CC0-1.0",
        "languages": ["en", "ja"],
        "paths": [
            "src/translations/README.md",
            "src/translations/mp-all.babelon.tsv",
            "src/translations/mp-ja-changed.babelon.tsv",
            "src/translations/mp-ja-not-translated.babelon.tsv",
            "src/translations/mp-ja.babelon.owl",
            "src/translations/mp-ja.babelon.tsv",
            "src/translations/mp-ja.synonyms.tsv",
        ],
        "release_assets": [
            "mp-international.owl",
            "mp-ja-changed.babelon.tsv",
            "mp-ja-not-translated.babelon.tsv",
            "mp-ja.babelon.tsv",
        ],
    },
}

MESH_2026_ARTIFACTS = (
    "desc2026.xml",
    "pa2026.xml",
    "qual2026.xml",
    "supp2026.xml",
)

LOINC_282_VARIANTS = (
    "ar-JO",
    "cs-CZ",
    "de-AT",
    "de-DE",
    "el-GR",
    "es-AR",
    "es-ES",
    "es-MX",
    "et-EE",
    "fr-BE",
    "fr-CA",
    "fr-FR",
    "it-IT",
    "ko-KR",
    "nl-NL",
    "pl-PL",
    "pt-BR",
    "ru-RU",
    "tr-TR",
    "uk-UA",
    "zh-CN",
)


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def orphanet_artifacts(release: str) -> list[dict[str, str]]:
    artifacts: list[dict[str, str]] = []
    for language in ORPHADATA_LANGUAGES:
        artifacts.extend(
            [
                {
                    "language": language,
                    "format": "xml",
                    "url": f"https://www.orphadata.com/data/xml/{language}_product1.xml",
                    "path": f"releases/orphanet/{release}/xml/{language}_product1.xml",
                },
                {
                    "language": language,
                    "format": "json-tar-gz",
                    "url": (f"https://www.orphadata.com/data/json/{language}_product1.json.tar.gz"),
                    "path": (f"releases/orphanet/{release}/json/{language}_product1.json.tar.gz"),
                },
            ]
        )
    for language in ORPHADATA_DIFF_LANGUAGES:
        artifacts.append(
            {
                "language": language,
                "format": "diff",
                "url": f"https://www.orphadata.com/data/diff/{language}_product1.diff",
                "path": f"releases/orphanet/{release}/diff/{language}_product1.diff",
            }
        )
    return artifacts


def github_catalog_artifacts(source: str) -> list[dict[str, str]]:
    catalog = GITHUB_MULTILINGUAL_CATALOGS[source]
    repository = catalog["repository"]
    release = catalog["release"]
    artifacts = []
    for path in catalog["paths"]:
        language = "ja" if "-ja" in path else "es" if "-es" in path else "mul"
        artifacts.append(
            {
                "language": language,
                "format": Path(path).suffix.lstrip(".") or "text",
                "url": f"https://raw.githubusercontent.com/{repository}/{release}/{path}",
                "path": f"releases/{source}/{release}/source-tree/{path}",
            }
        )
    for filename in catalog.get("release_assets", []):
        language = "ja" if "-ja" in filename else "mul"
        artifacts.append(
            {
                "language": language,
                "format": Path(filename).suffix.lstrip("."),
                "url": f"https://github.com/{repository}/releases/download/{release}/{filename}",
                "path": f"releases/{source}/{release}/release-assets/{filename}",
            }
        )
    return artifacts


def mesh_artifacts(release: str) -> list[dict[str, str]]:
    base_url = "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh"
    return [
        {
            "language": "en",
            "format": "xml",
            "url": f"{base_url}/{filename}",
            "path": f"releases/mesh/{release}/xml/{filename}",
        }
        for filename in MESH_2026_ARTIFACTS
    ]


def download(client: httpx.Client, url: str, destination: Path) -> tuple[str, int]:
    last_error: Exception | None = None
    for attempt in range(1, 5):
        digest = hashlib.sha256()
        size = 0
        try:
            with client.stream("GET", url, follow_redirects=True) as response:
                response.raise_for_status()
                with destination.open("wb") as output:
                    for chunk in response.iter_bytes(1024 * 1024):
                        output.write(chunk)
                        digest.update(chunk)
                        size += len(chunk)
            if size == 0:
                raise RuntimeError(f"empty response from {url}")
            return digest.hexdigest(), size
        except Exception as exc:  # retries are deliberately bounded
            last_error = exc
            destination.unlink(missing_ok=True)
            if attempt < 4:
                time.sleep(2**attempt)
    raise RuntimeError(f"failed to download {url}") from last_error


def upload_receipt(
    api: Any,
    repo_id: str,
    receipt: dict[str, Any],
    receipt_path: str,
) -> None:
    payload = json.dumps(receipt, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    api.upload_file(
        path_or_fileobj=payload,
        path_in_repo=receipt_path,
        repo_id=repo_id,
        repo_type="dataset",
        commit_message="checkpoint governed multilingual archive receipt",
    )


def archive_orphanet(repo_id: str, release: str, token: str) -> None:
    api = hf_api(token)
    info = api.repo_info(repo_id=repo_id, repo_type="dataset")
    if not info.private:
        raise RuntimeError(f"refusing to archive restricted sources to public repo {repo_id}")

    artifacts = orphanet_artifacts(release)
    receipt_path = f"receipts/orphanet-{release}-multilingual.json"
    receipt: dict[str, Any] = {
        "schema_version": "1.0",
        "source": "Orphanet/Orphadata",
        "release": release,
        "source_catalog": "https://sciences.orphadata.com/alignments/",
        "licence": "CC BY 4.0",
        "archive_class": "private-owner-only",
        "downstream_promotion": "blocked",
        "expected_artifact_count": len(artifacts),
        "expected_languages": list(ORPHADATA_LANGUAGES),
        "started_at": utc_now(),
        "completed_at": None,
        "status": "running",
        "artifacts": [],
        "failures": [],
    }
    upload_receipt(api, repo_id, receipt, receipt_path)

    timeout = httpx.Timeout(connect=30, read=300, write=300, pool=30)
    headers = {"User-Agent": "hpo-translations-governed-private-archive/1.0"}
    with (
        httpx.Client(timeout=timeout, headers=headers) as client,
        tempfile.TemporaryDirectory(prefix="ontology-archive-") as temporary,
    ):
        temp_root = Path(temporary)
        for index, artifact in enumerate(artifacts, start=1):
            local_path = temp_root / Path(artifact["path"]).name
            try:
                sha256, size = download(client, artifact["url"], local_path)
                api.upload_file(
                    path_or_fileobj=local_path,
                    path_in_repo=artifact["path"],
                    repo_id=repo_id,
                    repo_type="dataset",
                    commit_message=(f"archive Orphadata {release} {artifact['language']} {artifact['format']}"),
                )
                receipt["artifacts"].append(
                    {
                        **artifact,
                        "sha256": sha256,
                        "size_bytes": size,
                        "archived_at": utc_now(),
                    }
                )
                print(
                    f"archived {index}/{len(artifacts)} {artifact['language']} {artifact['format']} ({size} bytes)",
                    flush=True,
                )
            except Exception as exc:
                receipt["failures"].append({**artifact, "error": type(exc).__name__, "failed_at": utc_now()})
                receipt["status"] = "partial"
                upload_receipt(api, repo_id, receipt, receipt_path)
                raise
            finally:
                local_path.unlink(missing_ok=True)
            upload_receipt(api, repo_id, receipt, receipt_path)

    receipt["completed_at"] = utc_now()
    receipt["status"] = "complete"
    upload_receipt(api, repo_id, receipt, receipt_path)
    print(f"complete: archived {len(receipt['artifacts'])} artifacts", flush=True)


def archive_github_catalog(repo_id: str, source: str, token: str) -> None:
    catalog = GITHUB_MULTILINGUAL_CATALOGS[source]
    release = catalog["release"]
    artifacts = github_catalog_artifacts(source)
    api = hf_api(token)
    info = api.repo_info(repo_id=repo_id, repo_type="dataset")
    if not info.private:
        raise RuntimeError(f"refusing to archive governed sources to public repo {repo_id}")

    receipt_path = f"receipts/{source}-{release}-multilingual.json"
    receipt: dict[str, Any] = {
        "schema_version": "1.0",
        "source": catalog["source"],
        "release": release,
        "source_catalog": f"https://github.com/{catalog['repository']}/tree/{release}",
        "licence": catalog["licence"],
        "archive_class": "private-owner-only",
        "downstream_promotion": "blocked",
        "expected_artifact_count": len(artifacts),
        "expected_languages": catalog["languages"],
        "started_at": utc_now(),
        "completed_at": None,
        "status": "running",
        "artifacts": [],
        "failures": [],
    }
    upload_receipt(api, repo_id, receipt, receipt_path)
    timeout = httpx.Timeout(connect=30, read=300, write=300, pool=30)
    headers = {"User-Agent": "hpo-translations-governed-private-archive/1.0"}
    with (
        httpx.Client(timeout=timeout, headers=headers) as client,
        tempfile.TemporaryDirectory(prefix="ontology-archive-") as temporary,
    ):
        temp_root = Path(temporary)
        for index, artifact in enumerate(artifacts, start=1):
            local_path = temp_root / f"artifact-{index}"
            try:
                sha256, size = download(client, artifact["url"], local_path)
                api.upload_file(
                    path_or_fileobj=local_path,
                    path_in_repo=artifact["path"],
                    repo_id=repo_id,
                    repo_type="dataset",
                    commit_message=(
                        f"archive {catalog['source']} {release} {artifact['language']} {artifact['format']}"
                    ),
                )
                receipt["artifacts"].append(
                    {
                        **artifact,
                        "sha256": sha256,
                        "size_bytes": size,
                        "archived_at": utc_now(),
                    }
                )
                print(
                    f"archived {index}/{len(artifacts)} {artifact['path']} ({size} bytes)",
                    flush=True,
                )
            except Exception as exc:
                receipt["failures"].append({**artifact, "error": type(exc).__name__, "failed_at": utc_now()})
                receipt["status"] = "partial"
                upload_receipt(api, repo_id, receipt, receipt_path)
                raise
            finally:
                local_path.unlink(missing_ok=True)
            upload_receipt(api, repo_id, receipt, receipt_path)

    receipt["completed_at"] = utc_now()
    receipt["status"] = "complete"
    upload_receipt(api, repo_id, receipt, receipt_path)
    print(f"complete: archived {len(receipt['artifacts'])} artifacts", flush=True)


def archive_mesh(repo_id: str, release: str, token: str) -> None:
    artifacts = mesh_artifacts(release)
    api = hf_api(token)
    info = api.repo_info(repo_id=repo_id, repo_type="dataset")
    if not info.private:
        raise RuntimeError(f"refusing to archive governed sources to public repo {repo_id}")
    receipt_path = f"receipts/mesh-{release}.json"
    receipt: dict[str, Any] = {
        "schema_version": "1.0",
        "source": "Medical Subject Headings (MeSH)",
        "release": release,
        "source_catalog": "https://www.nlm.nih.gov/databases/download/mesh.html",
        "licence": "NLM terms and conditions apply",
        "archive_class": "private-owner-only",
        "downstream_promotion": "blocked",
        "expected_artifact_count": len(artifacts),
        "expected_languages": ["en"],
        "language_scope_note": (
            "NLM's official bulk distribution is English. National MeSH translations "
            "are independently stewarded and are not represented as NLM bulk products."
        ),
        "started_at": utc_now(),
        "completed_at": None,
        "status": "running",
        "artifacts": [],
        "failures": [],
    }
    upload_receipt(api, repo_id, receipt, receipt_path)
    timeout = httpx.Timeout(connect=30, read=300, write=300, pool=30)
    with (
        httpx.Client(timeout=timeout, follow_redirects=True) as client,
        tempfile.TemporaryDirectory(prefix="ontology-archive-") as temporary,
    ):
        temp_root = Path(temporary)
        for artifact in artifacts:
            local_path = temp_root / Path(artifact["path"]).name
            try:
                sha256, size = download(client, artifact["url"], local_path)
                api.upload_file(
                    path_or_fileobj=local_path,
                    path_in_repo=artifact["path"],
                    repo_id=repo_id,
                    repo_type="dataset",
                    commit_message=f"archive MeSH {release} {artifact['format']}",
                )
                receipt["artifacts"].append(
                    {**artifact, "sha256": sha256, "size_bytes": size, "archived_at": utc_now()}
                )
            except Exception as exc:
                receipt["failures"].append({**artifact, "error": type(exc).__name__, "failed_at": utc_now()})
                receipt["status"] = "partial"
                upload_receipt(api, repo_id, receipt, receipt_path)
                raise
            finally:
                local_path.unlink(missing_ok=True)
            upload_receipt(api, repo_id, receipt, receipt_path)
    receipt["completed_at"] = utc_now()
    receipt["status"] = "complete"
    upload_receipt(api, repo_id, receipt, receipt_path)


def archive_loinc(repo_id: str, release: str, token: str) -> None:
    username = os.environ.get("LOINC_USERNAME")
    password = os.environ.get("LOINC_PASSWORD")
    if not username or not password:
        raise RuntimeError("LOINC_USERNAME and LOINC_PASSWORD must be supplied as Job secrets")
    api = hf_api(token)
    info = api.repo_info(repo_id=repo_id, repo_type="dataset")
    if not info.private:
        raise RuntimeError(f"refusing to archive licensed LOINC to public repo {repo_id}")

    metadata_url = f"https://loinc.regenstrief.org/api/v1/Loinc?version={release}"
    download_url = f"https://loinc.regenstrief.org/api/v1/Loinc/Download?version={release}"
    timeout = httpx.Timeout(connect=30, read=600, write=300, pool=30)
    receipt_path = f"receipts/loinc-{release}-multilingual.json"
    with (
        httpx.Client(
            timeout=timeout,
            auth=httpx.BasicAuth(username, password),
            follow_redirects=True,
        ) as client,
        tempfile.TemporaryDirectory(prefix="ontology-archive-") as temporary,
    ):
        metadata_response = client.get(metadata_url)
        metadata_response.raise_for_status()
        release_metadata = metadata_response.json()
        if not isinstance(release_metadata, dict):
            raise RuntimeError("release metadata response must be a JSON object")
        local_path = Path(temporary) / f"Loinc_{release}.zip"
        sha256, size = download(client, download_url, local_path)
        with zipfile.ZipFile(local_path) as archive:
            members = archive.namelist()
        missing_variants = [
            variant
            for variant in LOINC_282_VARIANTS
            if not any(variant.replace("-", "") in member for member in members)
        ]
        if missing_variants:
            raise RuntimeError(f"LOINC archive is missing expected variants: {missing_variants}")
        archive_path = f"releases/loinc/{release}/Loinc_{release}.zip"
        api.upload_file(
            path_or_fileobj=local_path,
            path_in_repo=archive_path,
            repo_id=repo_id,
            repo_type="dataset",
            commit_message=f"archive licensed multilingual LOINC {release}",
        )
        receipt = {
            "schema_version": "1.0",
            "source": "LOINC",
            "release": release,
            "source_catalog": "https://loinc.org/downloads/",
            "licence": "LOINC License 5.8",
            "archive_class": "private-owner-only",
            "downstream_promotion": "blocked",
            "status": "complete",
            "completed_at": utc_now(),
            "release_metadata_verified": True,
            "languages": list(LOINC_282_VARIANTS),
            "zip_member_count": len(members),
            "artifact": {
                "path": archive_path,
                "sha256": sha256,
                "size_bytes": size,
            },
        }
        upload_receipt(api, repo_id, receipt, receipt_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=("do", "loinc", "mesh", "mp", "orphanet"), required=True)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--release")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN must be supplied as a Job secret")
    if args.source in {"loinc", "mesh", "orphanet"} and not args.release:
        raise RuntimeError(f"--release is required for {args.source}")
    if args.source == "orphanet":
        archive_orphanet(args.repo_id, args.release, token)
    elif args.source == "mesh":
        archive_mesh(args.repo_id, args.release, token)
    elif args.source == "loinc":
        archive_loinc(args.repo_id, args.release, token)
    else:
        archive_github_catalog(args.repo_id, args.source, token)


if __name__ == "__main__":
    main()
