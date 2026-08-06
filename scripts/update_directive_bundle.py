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
        description="Atomically synchronize all permanent-directive copies and integrity metadata."
    )
    parser.add_argument("--version", required=True, help="New directive version, e.g. 2026-08-06.2")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    canonical_path = ROOT / manifest["canonical_path"]
    mirror_path = ROOT / manifest["mirror_path"]
    encoded_path = ROOT / manifest["encoded_backup_path"]

    data = canonical_path.read_bytes()
    data.decode("utf-8")
    digest = hashlib.sha256(data).hexdigest()

    mirror_path.write_bytes(data)
    encoded_path.write_text(base64.b64encode(data).decode("ascii") + "\n", encoding="ascii")
    manifest["directive_version"] = args.version
    manifest["expected_sha256_utf8"] = digest
    manifest["expected_utf8_bytes"] = len(data)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "directive_version": args.version,
                "sha256": digest,
                "bytes": len(data),
                "updated": [
                    str(mirror_path.relative_to(ROOT)),
                    str(encoded_path.relative_to(ROOT)),
                    str(MANIFEST_PATH.relative_to(ROOT)),
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
