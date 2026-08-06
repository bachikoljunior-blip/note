#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "OPERATIONS" / "DIRECTIVE_MANIFEST.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Synchronize the exact user permanent directive copies and integrity metadata. "
            "Use only after the user explicitly redefines the permanent directive."
        )
    )
    parser.add_argument(
        "--version",
        required=True,
        help="New directive version, e.g. 2026-08-06.user-verbatim.2",
    )
    parser.add_argument(
        "--confirm-user-explicit-change",
        action="store_true",
        help="Required acknowledgement that the user explicitly changed permanent instructions.",
    )
    args = parser.parse_args()

    if not args.confirm_user_explicit_change:
        raise SystemExit(
            "Refusing to change the permanent directive without "
            "--confirm-user-explicit-change"
        )

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("classification") != "user_permanent_directive_only":
        raise SystemExit("Manifest classification is not user_permanent_directive_only")

    canonical_path = ROOT / manifest["canonical_path"]
    mirror_path = ROOT / manifest["mirror_path"]
    encoded_path = ROOT / manifest["encoded_backup_path"]

    text = canonical_path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
        canonical_path.write_text(text, encoding="utf-8")

    instructions = text.rstrip("\n").split("\n\n")
    if not instructions or any(not item.strip() for item in instructions):
        raise SystemExit("Permanent directive must be non-empty paragraphs separated by one blank line")

    for phrase in manifest.get("forbidden_assistant_text_in_canonical", []):
        if phrase in text:
            raise SystemExit(f"Assistant-created text detected in permanent directive: {phrase}")

    data = text.encode("utf-8")
    digest = hashlib.sha256(data).hexdigest()

    mirror_path.write_bytes(data)
    encoded_path.write_text(
        base64.b64encode(data).decode("ascii") + "\n",
        encoding="ascii",
    )
    manifest["directive_version"] = args.version
    manifest["expected_sha256_utf8"] = digest
    manifest["expected_utf8_bytes"] = len(data)
    manifest["expected_instruction_count"] = len(instructions)
    manifest["exact_instructions"] = instructions
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "directive_version": args.version,
                "instruction_count": len(instructions),
                "sha256": digest,
                "bytes": len(data),
                "updated": [
                    str(canonical_path.relative_to(ROOT)),
                    str(mirror_path.relative_to(ROOT)),
                    str(encoded_path.relative_to(ROOT)),
                    str(MANIFEST_PATH.relative_to(ROOT)),
                ],
                "next_required_command": "python scripts/check_directive_integrity.py",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
