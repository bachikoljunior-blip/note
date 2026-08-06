#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "distribution.json"
OUT_MD = ROOT / "dist" / "distribution_pack.md"
OUT_JSON = ROOT / "dist" / "distribution_pack.json"
REPORT = ROOT / "reports" / "distribution_pack.json"


def tracked_url(base: str, source: str, medium: str, campaign: str, content: str) -> str:
    parsed = urllib.parse.urlsplit(base)
    query = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    query.update({
        "utm_source": source,
        "utm_medium": medium,
        "utm_campaign": campaign,
        "utm_content": content,
    })
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), parsed.fragment))


def fill(template: str, *, title: str, text: str, url: str) -> str:
    values = {
        "title": urllib.parse.quote(title, safe=""),
        "text": urllib.parse.quote(text, safe=""),
        "url": urllib.parse.quote(url, safe=""),
        "text_with_url": urllib.parse.quote(f"{text}\n{url}", safe=""),
    }
    return template.format(**values)


def main() -> int:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    product = cfg["product"]
    campaign = cfg["tracking"]["utm_campaign"]
    rows: list[dict[str, str | None]] = []

    for target in cfg["targets"]:
        for variant in cfg["variants"]:
            url = tracked_url(
                product["url"],
                target["utm_source"],
                target["utm_medium"],
                campaign,
                variant["id"],
            )
            prefill = target.get("prefill")
            rows.append({
                "target_id": target["id"],
                "target_label": target["label"],
                "variant_id": variant["id"],
                "variant_label": variant["label"],
                "text": variant["text"],
                "tracked_url": url,
                "prefilled_url": fill(prefill, title=product["title"], text=variant["text"], url=url) if prefill else None,
            })

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"generated_at_utc": datetime.now(timezone.utc).isoformat(), "items": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = ["# 配布パック", "", "各リンクは媒体・訴求別のUTM付きです。最終投稿は各アカウント本人が確定します。", ""]
    for row in rows:
        lines += [
            f"## {row['target_label']} / {row['variant_label']}",
            "",
            str(row["text"]),
            "",
            f"商品URL: {row['tracked_url']}",
        ]
        if row["prefilled_url"]:
            lines.append(f"事前入力リンク: {row['prefilled_url']}")
        lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    errors: list[str] = []
    expected = len(cfg["targets"]) * len(cfg["variants"])
    if len(rows) != expected:
        errors.append("combination_count_mismatch")
    for row in rows:
        if "utm_source=" not in str(row["tracked_url"]) or "utm_content=" not in str(row["tracked_url"]):
            errors.append(f"tracking_missing:{row['target_id']}:{row['variant_id']}")

    report = {
        "ok": not errors,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "targets": len(cfg["targets"]),
        "variants": len(cfg["variants"]),
        "combinations": len(rows),
        "cost_yen": 0,
        "credentials_used": False,
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
