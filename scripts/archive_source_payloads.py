import argparse
import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlparse

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "research_validation" / "source_payload_archive_plan.json"
SCHEMA = ROOT / "research_validation" / "source_payload_archive_plan.schema.json"
CATALOG = ROOT / "research_validation" / "mapping_expansion_catalog.json"
STAGING = ROOT / ".archive-staging"
MAX_DOWNLOAD_BYTES = 250 * 1024 * 1024
ALLOWED_HOSTS = {"data.monarchinitiative.org", "raw.githubusercontent.com", "nanbyodata.jp"}
RESTRICTED_MARKERS = (b"SNOMED CT", b"UMLS CUI", b"LOINC Long Common Name")


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def validation_errors(plan: dict[str, Any], schema: dict[str, Any], catalog: dict[str, Any] | None = None) -> list[str]:
    errors = [f"schema: {item.message}" for item in Draft202012Validator(schema).iter_errors(plan)]
    artifacts = cast(list[dict[str, Any]], plan.get("artifacts", []))
    ids = [item.get("artifact_id") for item in artifacts]
    if len(ids) != len(set(ids)):
        errors.append("archive artifact IDs must be unique")
    if catalog is not None:
        catalog_ids = [item.get("artifact_id") for item in cast(list[dict[str, Any]], catalog.get("artifacts", []))]
        if set(ids) != set(catalog_ids):
            errors.append("archive plan must cover every mapping catalog artifact exactly once")
    public_target = plan.get("targets", {}).get("public")
    for item in artifacts:
        route = item.get("archive_route")
        retrieval = item.get("payload_retrieval_allowed")
        remote = item.get("remote_upload_allowed")
        if route == "public_hf" and not item.get("license"):
            errors.append(f"{item.get('artifact_id')}: public archive requires an exact licence")
        if route == "public_hf" and remote and not public_target:
            errors.append(f"{item.get('artifact_id')}: public upload requires an explicit public target")
        if route == "private_hf" and remote and not item.get("license"):
            errors.append(f"{item.get('artifact_id')}: private upload requires explicit storage permission")
        if route in {"local_only", "metadata_only"} and remote:
            errors.append(f"{item.get('artifact_id')}: non-hosted route cannot enable remote upload")
        if route == "metadata_only" and retrieval:
            errors.append(f"{item.get('artifact_id')}: metadata-only route cannot retrieve payload")
        if retrieval and not item.get("expected_sha256"):
            errors.append(f"{item.get('artifact_id')}: retrieval requires an expected SHA-256")
        components = cast(list[dict[str, Any]], item.get("components", []))
        component_ids = [component.get("component_id") for component in components]
        if len(component_ids) != len(set(component_ids)):
            errors.append(f"{item.get('artifact_id')}: component IDs must be unique")
        for component in components:
            if component.get("payload_retrieval_allowed") is True and not component.get("expected_sha256"):
                errors.append(f"{item.get('artifact_id')}: component retrieval requires an expected SHA-256")
    controls = plan.get("controls", {})
    if controls.get("credentials_committed") or controls.get("restricted_payloads_committed"):
        errors.append("archive controls must prohibit committed credentials and restricted payloads")
    if controls.get("private_means_redistributable") is not False:
        errors.append("private hosting must not be treated as redistribution authority")
    return sorted(set(errors))


def archive(plan: dict[str, Any]) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    STAGING.mkdir(parents=True, exist_ok=True)
    for item in cast(list[dict[str, Any]], plan["artifacts"]):
        components = cast(list[dict[str, Any]], item.get("components", []))
        if components:
            component_receipts: list[dict[str, Any]] = []
            for component in components:
                if component["payload_retrieval_allowed"] is not True:
                    continue
                component_item = {
                    **item,
                    "artifact_id": component["component_id"],
                    "source_url": component["source_url"],
                    "expected_sha256": component["expected_sha256"],
                    "expected_bytes": component["expected_bytes"],
                    "payload_retrieval_allowed": True,
                    "components": [],
                }
                component_receipts.extend(archive({"artifacts": [component_item]}))
            receipts.append(
                {
                    "artifact_id": item["artifact_id"],
                    "status": "components_archived_checksum_verified",
                    "components": component_receipts,
                }
            )
            continue
        if item["payload_retrieval_allowed"] is not True:
            receipts.append({"artifact_id": item["artifact_id"], "status": "not_retrieved", "reason": item["reason"]})
            continue
        target = STAGING / cast(str, item["artifact_id"]) / Path(cast(str, item["source_url"])).name
        parsed = urlparse(cast(str, item["source_url"]))
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError(f"{item['artifact_id']}: source host is not allowlisted")
        target.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(cast(str, item["source_url"]), timeout=120) as response:  # noqa: S310
            payload = response.read(MAX_DOWNLOAD_BYTES + 1)
        if len(payload) > MAX_DOWNLOAD_BYTES:
            raise ValueError(f"{item['artifact_id']}: payload exceeds archive size limit")
        expected_bytes = item.get("expected_bytes")
        if expected_bytes is not None and len(payload) != expected_bytes:
            raise ValueError(f"{item['artifact_id']}: byte-count mismatch; payload not retained")
        digest = hashlib.sha256(payload).hexdigest()
        if digest != item["expected_sha256"]:
            raise ValueError(f"{item['artifact_id']}: SHA-256 mismatch; payload not retained")
        if item["archive_route"] == "public_hf" and any(marker in payload for marker in RESTRICTED_MARKERS):
            raise ValueError(f"{item['artifact_id']}: restricted marker blocks public archival")
        target.write_bytes(payload)
        receipts.append(
            {
                "artifact_id": item["artifact_id"],
                "status": "checksum_verified_local_archive",
                "sha256": digest,
                "bytes": len(payload),
                "relative_path": target.relative_to(ROOT).as_posix(),
                "archive_route": item["archive_route"],
                "remote_upload_allowed": item["remote_upload_allowed"],
            }
        )
    return receipts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="retrieve only allowlisted, checksum-pinned payloads")
    parser.add_argument("--receipt-path", type=Path, help="write a payload-safe local receipt")
    args = parser.parse_args()
    plan = load_json(PLAN)
    errors = validation_errors(plan, load_json(SCHEMA), load_json(CATALOG))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if not args.execute:
        print("Source payload archive plan validation passed; no payload retrieved")
        return 0
    receipt = {
        "schema_version": "local-source-archive-receipts-v1",
        "status": "checksum_verified_permissive_local_archive_remote_upload_blocked",
        "receipts": archive(plan),
        "controls": {
            "payload_embedded": False,
            "credentials_embedded": False,
            "absolute_paths_embedded": False,
            "remote_write_performed": False,
        },
    }
    rendered = json.dumps(receipt, indent=2) + "\n"
    if args.receipt_path:
        resolved = args.receipt_path.resolve()
        if ROOT not in resolved.parents or resolved.suffix != ".json":
            raise ValueError("receipt path must be a JSON file inside the repository")
        resolved.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"Wrote payload-safe archive receipt: {resolved.relative_to(ROOT).as_posix()}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
