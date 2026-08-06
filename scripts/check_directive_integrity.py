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


def expected_text(manifest: dict[str, Any]) -> str:
    instructions = manifest.get("exact_instructions")
    if not isinstance(instructions, list) or not all(
        isinstance(item, str) and item for item in instructions
    ):
        raise ValueError("exact_instructions must be a non-empty list of strings")
    return "\n\n".join(instructions) + "\n"


def inspect(
    manifest: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], list[str], list[str]]:
    expected = expected_text(manifest).encode("utf-8")
    expected_hash = manifest["expected_sha256_utf8"]
    expected_bytes = int(manifest["expected_utf8_bytes"])
    metadata_errors: list[str] = []

    if manifest.get("classification") != "user_permanent_directive_only":
        metadata_errors.append("invalid_classification")
    if len(manifest["exact_instructions"]) != int(
        manifest.get("expected_instruction_count", -1)
    ):
        metadata_errors.append("instruction_count_mismatch")
    if sha256(expected) != expected_hash:
        metadata_errors.append("manifest_hash_does_not_match_exact_instructions")
    if len(expected) != expected_bytes:
        metadata_errors.append("manifest_byte_count_does_not_match_exact_instructions")

    canonical_path = manifest.get("canonical_path")
    mirror_path = manifest.get("mirror_path")
    encoded_path = manifest.get("encoded_backup_path")
    assistant_policy_path = manifest.get("assistant_policy_path")
    boundary_path = manifest.get("boundary_path")
    required_paths = [
        canonical_path,
        mirror_path,
        encoded_path,
        assistant_policy_path,
        boundary_path,
    ]
    if not all(isinstance(path, str) and path for path in required_paths):
        metadata_errors.append("manifest_required_path_missing")

    if len({canonical_path, mirror_path, encoded_path, assistant_policy_path, boundary_path}) != 5:
        metadata_errors.append("directive_and_policy_paths_must_be_distinct")

    specs = {
        "canonical": (ROOT / str(canonical_path), False),
        "mirror": (ROOT / str(mirror_path), False),
        "encoded_backup": (ROOT / str(encoded_path), True),
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
            "matches_expected": data == expected,
            "matches_manifest_hash": (
                data is not None
                and digest == expected_hash
                and len(data) == expected_bytes
            ),
            "error": error,
            "data": data,
        }

    separation_errors: list[str] = []
    canonical_data = copies["canonical"]["data"]
    if canonical_data is not None:
        try:
            canonical_text = canonical_data.decode("utf-8")
        except UnicodeDecodeError as exc:
            separation_errors.append(f"canonical_not_utf8:{exc}")
        else:
            if canonical_text != expected.decode("utf-8"):
                separation_errors.append("canonical_not_exact_user_text")
            for phrase in manifest.get("forbidden_assistant_text_in_canonical", []):
                if phrase in canonical_text:
                    separation_errors.append(f"assistant_text_in_canonical:{phrase}")

    assistant_path = ROOT / str(assistant_policy_path)
    boundary_file = ROOT / str(boundary_path)
    if not assistant_path.is_file():
        separation_errors.append(f"missing_assistant_policy:{assistant_policy_path}")
    else:
        policy = assistant_path.read_text(encoding="utf-8")
        for phrase in [
            "ユーザー恒久指示ではありません",
            "このファイルはAIが考えた可変方針",
            "OPERATIONS/CORE_DIRECTIVE.md",
        ]:
            if phrase not in policy:
                separation_errors.append(
                    f"assistant_policy_boundary_phrase_missing:{phrase}"
                )

    if not boundary_file.is_file():
        separation_errors.append(f"missing_boundary_file:{boundary_path}")
    else:
        boundary = boundary_file.read_text(encoding="utf-8")
        for phrase in [
            "ユーザー恒久指示",
            "AIが考えた補助方針",
            "外部の上位制約",
            "OPERATIONS/CORE_DIRECTIVE.md",
            "OPERATIONS/ASSISTANT_OPERATING_POLICY.md",
        ]:
            if phrase not in boundary:
                separation_errors.append(f"boundary_phrase_missing:{phrase}")

    bootstrap_requirements = {
        "AGENTS.md": [
            "OPERATIONS/CORE_DIRECTIVE.md",
            "OPERATIONS/DIRECTIVE_BOUNDARY.md",
            "OPERATIONS/ASSISTANT_OPERATING_POLICY.md",
            "check_directive_integrity.py",
        ],
        "CLAUDE.md": [
            "OPERATIONS/CORE_DIRECTIVE.md",
            "OPERATIONS/DIRECTIVE_BOUNDARY.md",
            "OPERATIONS/ASSISTANT_OPERATING_POLICY.md",
            "check_directive_integrity.py",
        ],
        ".github/copilot-instructions.md": [
            "OPERATIONS/CORE_DIRECTIVE.md",
            "OPERATIONS/DIRECTIVE_BOUNDARY.md",
            "OPERATIONS/ASSISTANT_OPERATING_POLICY.md",
            "check_directive_integrity.py",
        ],
        "OPERATIONS/BOOTSTRAP.md": [
            "OPERATIONS/DIRECTIVE_MANIFEST.json",
            "OPERATIONS/CORE_DIRECTIVE.md",
            "OPERATIONS/DIRECTIVE_BOUNDARY.md",
            "OPERATIONS/ASSISTANT_OPERATING_POLICY.md",
        ],
    }
    for rel, required in bootstrap_requirements.items():
        path = ROOT / rel
        if not path.is_file():
            separation_errors.append(f"missing_bootstrap:{rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in required:
            if phrase not in text:
                separation_errors.append(
                    f"bootstrap_pointer_missing:{rel}:{phrase}"
                )

    return copies, metadata_errors, separation_errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Repair damaged directive copies only when at least two exact copies remain.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    repaired_paths: list[str] = []
    try:
        manifest = load_manifest()
        expected = expected_text(manifest).encode("utf-8")
    except Exception as exc:  # noqa: BLE001
        payload = {
            "ok": False,
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "errors": [f"manifest_error:{type(exc).__name__}:{exc}"],
            "repaired_paths": [],
            "absolute_permanence_guaranteed": False,
        }
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    copies, metadata_errors, separation_errors = inspect(manifest)
    matching = [name for name, item in copies.items() if item["matches_expected"]]
    damaged = [name for name, item in copies.items() if not item["matches_expected"]]

    if damaged and args.repair and len(matching) >= 2 and not metadata_errors:
        for name in damaged:
            item = copies[name]
            write_copy(
                ROOT / item["path"],
                expected,
                encoded=bool(item["encoded"]),
            )
            repaired_paths.append(item["path"])
        copies, metadata_errors, separation_errors = inspect(manifest)
        matching = [name for name, item in copies.items() if item["matches_expected"]]
        damaged = [name for name, item in copies.items() if not item["matches_expected"]]

    if damaged:
        errors.append(
            "directive_copy_mismatch:"
            + ",".join(damaged)
            + f":matching_copies={len(matching)}"
        )
    errors.extend(metadata_errors)
    errors.extend(separation_errors)

    serializable_copies = {
        name: {key: value for key, value in item.items() if key != "data"}
        for name, item in copies.items()
    }
    payload = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": manifest.get("classification"),
        "directive_version": manifest.get("directive_version"),
        "expected_instruction_count": manifest.get("expected_instruction_count"),
        "expected_sha256_utf8": manifest.get("expected_sha256_utf8"),
        "matching_copy_count": len(matching),
        "separation_ok": not separation_errors,
        "copies": serializable_copies,
        "repaired_paths": repaired_paths,
        "errors": errors,
        "absolute_permanence_guaranteed": False,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
