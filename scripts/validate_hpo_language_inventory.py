import json
import subprocess
from pathlib import Path
from typing import Any, cast

INVENTORY = Path("conductor/hpo_babelon_language_inventory.json")
EXPECTED = {"ar", "cs", "de", "dtp", "es", "fr", "it", "ja", "nl", "nna", "pt", "tr", "tw", "zh"}


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True, encoding="utf-8", errors="replace"
    ).stdout.strip()


def validate() -> list[str]:
    data = cast(dict[str, Any], json.loads(INVENTORY.read_text(encoding="utf-8")))
    rows = cast(list[dict[str, Any]], data["profiles"])
    errors: list[str] = []
    shallow_repository = git("rev-parse", "--is-shallow-repository") == "true"
    if {str(row["code"]) for row in rows} != EXPECTED:
        errors.append("profile codes must match the 14 tracked Babelon profiles")
    for row in rows:
        code = str(row["code"])
        for kind, header_rows in (("babelon", 1), ("synonyms", 2)):
            path = Path(f"babelon/hp-{code}.{kind}.tsv")
            if not path.exists():
                errors.append(f"missing {path}")
                continue
            count = len(path.read_text(encoding="utf-8-sig").splitlines()) - header_rows
            field = "babelon_rows" if kind == "babelon" else "synonym_rows"
            blob_field = "babelon_blob" if kind == "babelon" else "synonym_blob"
            commit_field = "babelon_commit" if kind == "babelon" else "synonym_commit"
            if count != row[field]:
                errors.append(f"{code} {field} mismatch")
            if git("hash-object", "--", str(path)) != row[blob_field]:
                errors.append(f"{code} {blob_field} mismatch")
            recorded_commit = str(row[commit_field])
            if len(recorded_commit) != 40 or any(character not in "0123456789abcdef" for character in recorded_commit):
                errors.append(f"{code} {commit_field} must be a full hexadecimal commit")
            elif not shallow_repository and git("log", "-1", "--format=%H", "--", str(path)) != recorded_commit:
                errors.append(f"{code} {commit_field} mismatch")
    if any(data["payload_policy"].values()):
        errors.append("inventory must not authorize or add payloads")
    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        raise SystemExit("\n".join(problems))
    print("HPO Babelon language inventory validation passed")
