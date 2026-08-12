import argparse
import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "research_validation" / "source_payload_archive_plan.json"
SCHEMA = ROOT / "research_validation" / "source_payload_archive_plan.schema.json"
CATALOG = ROOT / "research_validation" / "mapping_expansion_catalog.json"
STAGING = ROOT / ".archive-staging"


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
        if route in {"private_hf", "local_only", "metadata_only"} and remote:
            errors.append(f"{item.get('artifact_id')}: restricted route cannot enable remote upload by default")
        if route == "metadata_only" and retrieval:
            errors.append(f"{item.get('artifact_id')}: metadata-only route cannot retrieve payload")
        if retrieval and not item.get("expected_sha256"):
            errors.append(f"{item.get('artifact_id')}: retrieval requires an expected SHA-256")
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
        if item["payload_retrieval_allowed"] is not True:
            receipts.append({"artifact_id": item["artifact_id"], "status": "not_retrieved", "reason": item["reason"]})
            continue
        target = STAGING / cast(str, item["artifact_id"]) / Path(cast(str, item["source_url"])).name
        target.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(cast(str, item["source_url"]), timeout=120) as response:  # noqa: S310
            payload = response.read()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != item["expected_sha256"]:
            raise ValueError(f"{item['artifact_id']}: SHA-256 mismatch; payload not retained")
        target.write_bytes(payload)
        receipts.append(
            {
                "artifact_id": item["artifact_id"],
                "status": "archived_local_content_addressed",
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
    receipts = archive(plan)
    print(json.dumps({"schema_version": "local-source-archive-receipts-v1", "receipts": receipts}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
