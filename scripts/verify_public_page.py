#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "public_page.json"


class MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.in_title = False
        self.title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "meta":
            key = values.get("property") or values.get("name")
            content = values.get("content")
            if key and content:
                self.meta[key.lower()] = content
        elif tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def normalize(value: str) -> str:
    return re.sub(r"\s+", "", html.unescape(value)).lower()


def main() -> int:
    campaign = json.loads((ROOT / "config/campaign.json").read_text(encoding="utf-8"))
    url = campaign["channels"]["note_product_url"]
    expected_title = campaign["product"]["title"]
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1",
            "Accept-Language": "ja,en-US;q=0.8,en;q=0.6",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    errors: list[str] = []
    warnings: list[str] = []
    status: int | None = None
    final_url = url
    body = b""
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            status = response.status
            final_url = response.geturl()
            body = response.read(3_000_000)
    except urllib.error.HTTPError as exc:
        status = exc.code
        errors.append(f"http_error:{exc.code}")
        body = exc.read(200_000)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"fetch_error:{type(exc).__name__}:{exc}")

    text = body.decode("utf-8", errors="replace")
    parser = MetaParser()
    parser.feed(text)
    page_title = parser.meta.get("og:title") or "".join(parser.title_parts).strip()
    description = parser.meta.get("og:description") or parser.meta.get("description") or ""

    if status != 200:
        errors.append(f"unexpected_status:{status}")
    if expected_title and normalize(expected_title) not in normalize(page_title + text[:500_000]):
        errors.append("expected_title_not_found")
    if "mobile_ai_studio" not in final_url and "mobile_ai_studio" not in text:
        errors.append("publisher_id_not_found")
    if "n779329665155" not in final_url and "n779329665155" not in text:
        errors.append("article_id_not_found")
    if "1,480" not in text and "1480" not in text:
        warnings.append("launch price was not visible in fetched public HTML")

    payload = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "requested_url": url,
        "final_url": final_url,
        "status": status,
        "page_title": page_title,
        "description_excerpt": description[:300],
        "response_bytes": len(body),
        "response_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "errors": errors,
        "warnings": warnings,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
