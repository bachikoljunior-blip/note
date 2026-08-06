#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "validation.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    required = [
        "README.md",
        "OPERATIONS/CORE_DIRECTIVE.md",
        "state/current.json",
        "config/campaign.json",
        "content/note/title.txt",
        "content/note/free_body.txt",
        "content/note/paid_body.txt",
        "content/launch_posts.md",
        "data/metrics.csv",
    ]
    for rel in required:
        if not (ROOT / rel).is_file():
            errors.append(f"missing:{rel}")

    state = load_json(ROOT / "state/current.json")
    campaign = load_json(ROOT / "config/campaign.json")
    title = (ROOT / "content/note/title.txt").read_text(encoding="utf-8").strip()
    url = campaign["channels"]["note_product_url"]

    if title != campaign["product"]["title"]:
        errors.append("title_mismatch")
    if state["publication"]["article_url"] != url:
        errors.append("note_url_mismatch")
    if state["publication"]["launch_price_yen"] != campaign["product"]["launch_price_yen"]:
        errors.append("launch_price_mismatch")
    if not re.fullmatch(r"https://note\.com/[A-Za-z0-9_]+/n/n[A-Za-z0-9]+", url):
        errors.append("invalid_note_url")
    if campaign["budget"]["upfront_yen"] != 0 or campaign["budget"]["monthly_yen"] != 0:
        errors.append("budget_not_zero")

    with (ROOT / "data/metrics.csv").open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        expected = ["checkpoint", "observed_at_utc", "views", "likes", "comments", "purchases", "gross_revenue_yen", "refunds", "traffic_notes"]
        if reader.fieldnames != expected:
            errors.append("metrics_header_mismatch")
        for index, row in enumerate(reader, start=2):
            for key in ("views", "likes", "comments", "purchases", "gross_revenue_yen", "refunds"):
                value = (row.get(key) or "").strip()
                if value and (not value.isdigit() or int(value) < 0):
                    errors.append(f"metrics_invalid:{index}:{key}")

    secret_patterns = [r"BEGIN [A-Z ]*PRIVATE KEY", r"ghp_[A-Za-z0-9]{20,}", r"github_pat_[A-Za-z0-9_]{20,}"]
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".zip"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in secret_patterns:
            if re.search(pattern, text):
                errors.append(f"possible_secret:{path.relative_to(ROOT)}")

    if state["publication"].get("external_content_verification") != "verified":
        warnings.append("published page content is not externally verified yet")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "errors": errors,
        "warnings": warnings,
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
