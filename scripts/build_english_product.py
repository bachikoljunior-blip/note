#!/usr/bin/env python3
from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS_DIR = ROOT / "artifacts" / "product_en_v1_0"
OUTPUT = ROOT / "dist" / "Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.0.zip"
REPORT = ROOT / "reports" / "english_product.json"
EXPECTED_BYTES = 20577
EXPECTED_SHA256 = "73d1009517456d50578f702c836d4da004e1cee4fe17a410e40df84a1559ffc8"
EXPECTED_MEMBERS = 15
JAPANESE = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")


def main() -> int:
    errors: list[str] = []
    parts = sorted(PARTS_DIR.glob("part-*.b64"))
    if len(parts) != 7:
        errors.append(f"part_count:{len(parts)}!=7")

    try:
        encoded = "".join("".join(path.read_text(encoding="ascii").split()) for path in parts)
        data = base64.b64decode(encoded, validate=True)
    except Exception as exc:  # noqa: BLE001
        data = b""
        errors.append(f"decode:{type(exc).__name__}:{exc}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != EXPECTED_BYTES:
        errors.append(f"bytes:{len(data)}!={EXPECTED_BYTES}")
    if digest != EXPECTED_SHA256:
        errors.append(f"sha256:{digest}!={EXPECTED_SHA256}")

    member_count = 0
    topic_count = 0
    unique_topic_ids = 0
    format_count = 0
    prompt_count = 0
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            bad_member = archive.testzip()
            names = archive.namelist()
            member_count = len(names)
            if bad_member:
                errors.append(f"corrupt_member:{bad_member}")
            if member_count != EXPECTED_MEMBERS:
                errors.append(f"zip_members:{member_count}!={EXPECTED_MEMBERS}")

            topics = list(csv.DictReader(io.StringIO(archive.read("100_topics.csv").decode("utf-8-sig"))))
            topic_count = len(topics)
            unique_topic_ids = len({row.get("id", "") for row in topics})
            if topic_count != 100:
                errors.append(f"topics:{topic_count}!=100")
            if unique_topic_ids != 100:
                errors.append(f"unique_topic_ids:{unique_topic_ids}!=100")

            formats = archive.read("12_formats.md").decode("utf-8")
            prompts = archive.read("prompt_library.md").decode("utf-8")
            format_count = len(re.findall(r"^## F\d{2}\b", formats, flags=re.MULTILINE))
            prompt_count = len(re.findall(r"^## P\d{2}\b", prompts, flags=re.MULTILINE))
            if format_count != 12:
                errors.append(f"formats:{format_count}!=12")
            if prompt_count != 9:
                errors.append(f"prompts:{prompt_count}!=9")

            for name in names:
                if Path(name).suffix.lower() not in {".md", ".txt", ".csv", ".json"}:
                    continue
                text = archive.read(name).decode("utf-8-sig")
                if JAPANESE.search(text):
                    errors.append(f"japanese_character_found:{name}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"zip_validation:{type(exc).__name__}:{exc}")

    payload = {
        "ok": not errors,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "output": str(OUTPUT.relative_to(ROOT)),
        "bytes": len(data),
        "sha256": digest,
        "zip_members": member_count,
        "topics": topic_count,
        "unique_topic_ids": unique_topic_ids,
        "formats": format_count,
        "prompts": prompt_count,
        "japanese_character_scan": "passed" if not any("japanese_character" in e for e in errors) else "failed",
        "cost_yen": 0,
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
