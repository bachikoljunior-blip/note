#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "OPERATIONS" / "DIRECTIVE_MANIFEST.json"
REPORT_PATH = ROOT / "reports" / "directive_integrity.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def read_copy(path: Path, *, encoded: bool = False) -> tuple[bytes | None, str | None]:
    try:
        raw = path.read_bytes()
        if encoded:
            raw = base64.b64decode(b"".join(raw.split()), validate=True)
        return raw, None
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}:{exc}"


def write_copy(path: Path, data: bytes, *, encoded: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if encoded:
        path.write_text(base64.b64encode(data).decode("ascii") + "\n", encoding="ascii")
    else:
        path.write_bytes(data)


def inspect(manifest: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    expected_hash = manifest["expected_sha256_utf8"]
    expected_bytes = int(manifest["expected_utf8_bytes"])
    specs = {
        "canonical": (ROOT / manifest["canonical_path"], False),
        "mirror": (ROOT / manifest["mirror_path"], False),
        "encoded_backup": (ROOT / manifest["encoded_backup_path"], True),
    }
    copies: dict[str, dict[str, Any]] = {}
    for name, (path, encoded) in specs.items():
        data, error = read_copy(path, encoded=encoded)
        digest = sha256(data) if data is not None else None
        copies[name] = {
            "path": str(path.relative_to(ROOT)),
            "encoded": encoded,
            "exists_and_decodes": data is not None,
            "bytes": len(data) if data is not None else None,
            "sha256": digest,
            "matches_expected": (
                data is not None
                and digest == expected_hash
                and len(data) == expected_bytes
            ),
            "error": error,
            "data": data,
        }

    bootstrap_errors: list[str] = []
    bootstrap_requirements = {
        "AGENTS.md": ["OPERATIONS/CORE_DIRECTIVE.md", "check_directive_integrity.py"],
        "CLAUDE.md": ["OPERATIONS/CORE_DIRECTIVE.md", "check_directive_integrity.py"],
        ".github/copilot-instructions.md": ["OPERATIONS/CORE_DIRECTIVE.md", "check_directive_integrity.py"],
        "OPERATIONS/BOOTSTRAP.md": ["OPERATIONS/DIRECTIVE_MANIFEST.json", "OPERATIONS/CORE_DIRECTIVE.md"],
    }
    for rel, required in bootstrap_requirements.items():
        path = ROOT / rel
        if not path.is_file():
            bootstrap_errors.append(f"missing_bootstrap:{rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in required:
            if phrase not in text:
                bootstrap_errors.append(f"bootstrap_pointer_missing:{rel}:{phrase}")

    canonical_data = copies["canonical"]["data"]
    if canonical_data is not None:
        try:
            canonical_text = canonical_data.decode("utf-8")
        except UnicodeDecodeError as exc:
            bootstrap_errors.append(f"canonical_not_utf8:{exc}")
        else:
            for phrase in manifest.get("minimum_required_phrases", []):
                if phrase not in canonical_text:
                    bootstrap_errors.append(f"required_phrase_missing:{phrase}")

    return copies, bootstrap_errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Repair exactly one damaged copy when the other two match the manifest.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    repaired_paths: list[str] = []
    try:
        manifest = load_manifest()
    except Exception as exc:  # noqa: BLE001
        payload = {
            "ok": False,
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "errors": [f"manifest_error:{type(exc).__name__}:{exc}"],
            "repaired_paths": [],
        }
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    copies, bootstrap_errors = inspect(manifest)
    matching = [name for name, item in copies.items() if item["matches_expected"]]
    damaged = [name for name, item in copies.items() if not item["matches_expected"]]

    if damaged and args.repair and len(matching) >= 2:
        source = copies[matching[0]]["data"]
        assert isinstance(source, bytes)
        for name in damaged:
            item = copies[name]
            write_copy(ROOT / item["path"], source, encoded=bool(item["encoded"]))
            repaired_paths.append(item["path"])
        copies, bootstrap_errors = inspect(manifest)
        matching = [name for name, item in copies.items() if item["matches_expected"]]
        damaged = [name for name, item in copies.items() if not item["matches_expected"]]

    if damaged:
        errors.append(
            "directive_copy_mismatch:"
            + ",".join(damaged)
            + f":matching_copies={len(matching)}"
        )
    errors.extend(bootstrap_errors)

    serializable_copies = {
        name: {key: value for key, value in item.items() if key != "data"}
        for name, item in copies.items()
    }
    payload = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "directive_version": manifest.get("directive_version"),
        "expected_sha256_utf8": manifest.get("expected_sha256_utf8"),
        "matching_copy_count": len(matching),
        "copies": serializable_copies,
        "repaired_paths": repaired_paths,
        "errors": errors,
        "absolute_permanence_guaranteed": False,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
