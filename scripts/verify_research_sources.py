"""Stream and verify pinned public research source assets without retaining payloads."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "research_validation" / "source_catalog.json"


@dataclass(frozen=True)
class SourcePin:
    source_id: str
    url: str
    size_bytes: int
    sha256: str


def hash_stream(stream: BinaryIO) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
        size += len(chunk)
    return size, digest.hexdigest()


def catalog_pins(catalog: dict[str, Any]) -> list[SourcePin]:
    hpo_release = catalog["hpo_release"]
    primary_asset = hpo_release["primary_asset"]
    pins = [
        SourcePin(
            source_id="hpo-release-hp-json",
            url=str(primary_asset["url"]),
            size_bytes=int(primary_asset["size_bytes"]),
            sha256=str(primary_asset["sha256"]),
        )
    ]
    for mapping in catalog["mappings"]:
        integrity = mapping["integrity"]
        if integrity["algorithm"] == "sha256":
            pins.append(
                SourcePin(
                    source_id=str(mapping["source_id"]),
                    url=str(mapping["versioned_url"]),
                    size_bytes=int(mapping["artifact_size_bytes"]),
                    sha256=str(integrity["value"]),
                )
            )
        for member in mapping["members"]:
            pins.append(
                SourcePin(
                    source_id=f"{mapping['source_id']}:{member['name']}",
                    url=str(member["url"]),
                    size_bytes=int(member["size_bytes"]),
                    sha256=str(member["sha256"]),
                )
            )
    return pins


def verify_pin(pin: SourcePin, timeout: float) -> list[str]:
    if not pin.url.startswith("https://"):
        return [f"{pin.source_id}: source URL must use HTTPS"]
    request = urllib.request.Request(pin.url, headers={"User-Agent": "hpo-translations-source-verifier/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        size, digest = hash_stream(response)
    errors: list[str] = []
    if size != pin.size_bytes:
        errors.append(f"{pin.source_id}: size {size} != expected {pin.size_bytes}")
    if digest != pin.sha256:
        errors.append(f"{pin.source_id}: sha256 {digest} != expected {pin.sha256}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--source-id", action="append", default=[])
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    pins = catalog_pins(catalog)
    requested = set(args.source_id)
    selected = [pin for pin in pins if not requested or pin.source_id in requested]
    missing = requested - {pin.source_id for pin in pins}
    if missing:
        print(f"Unknown source IDs: {sorted(missing)}")
        return 2

    errors: list[str] = []
    for pin in selected:
        try:
            pin_errors = verify_pin(pin, args.timeout)
        except Exception as exception:  # network and TLS errors are reported as verification failures
            pin_errors = [f"{pin.source_id}: {exception}"]
        errors.extend(pin_errors)
        print(f"{'FAIL' if pin_errors else 'PASS'} {pin.source_id}")

    if errors:
        print(f"Source pin verification failed with {len(errors)} issue(s):")
        for message in errors:
            print(f"- {message}")
        return 1
    print(f"Verified {len(selected)} pinned public source asset(s); no payloads were retained.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
