#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "artifacts" / "manifest.json"
REPORT = ROOT / "reports" / "artifacts.json"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    results: list[dict[str, object]] = []
    errors: list[str] = []

    for item in manifest["artifacts"]:
        source = ROOT / item["source_base64"]
        output = ROOT / item["output"]
        try:
            encoded = "".join(source.read_text(encoding="ascii").split())
            data = base64.b64decode(encoded, validate=True)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(data)

            digest = hashlib.sha256(data).hexdigest()
            size = len(data)
            with zipfile.ZipFile(output) as archive:
                bad_member = archive.testzip()
                members = archive.namelist()

            artifact_errors: list[str] = []
            if size != item["bytes"]:
                artifact_errors.append(f"size:{size}!={item['bytes']}")
            if digest != item["sha256"]:
                artifact_errors.append(f"sha256:{digest}!={item['sha256']}")
            if len(members) != item["zip_members"]:
                artifact_errors.append(f"zip_members:{len(members)}!={item['zip_members']}")
            if bad_member is not None:
                artifact_errors.append(f"corrupt_member:{bad_member}")

            if artifact_errors:
                errors.extend(f"{item['id']}:{error}" for error in artifact_errors)

            results.append(
                {
                    "id": item["id"],
                    "output": item["output"],
                    "bytes": size,
                    "sha256": digest,
                    "zip_members": len(members),
                    "zip_integrity": "ok" if bad_member is None else "failed",
                    "errors": artifact_errors,
                }
            )
        except Exception as exc:  # noqa: BLE001
            message = f"{item['id']}:{type(exc).__name__}:{exc}"
            errors.append(message)
            results.append({"id": item["id"], "errors": [message]})

    payload = {
        "ok": not errors,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "errors": errors,
        "artifacts": results,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
