#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "public_page.json"
RETRYABLE_HTTP_STATUSES = {403, 408, 425, 429, 500, 502, 503, 504}
RETRY_DELAYS_SECONDS = (1, 2)
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1",
    "Accept-Language": "ja,en-US;q=0.8,en;q=0.6",
    "Accept": "text/html,application/xhtml+xml",
}


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


def fetch_public_page(
    url: str,
    *,
    opener: Any = urllib.request.urlopen,
    sleeper: Any = time.sleep,
    delays: tuple[int, ...] = RETRY_DELAYS_SECONDS,
) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    max_attempts = len(delays) + 1
    status: int | None = None
    final_url = url
    body = b""
    terminal_error: str | None = None

    for index in range(max_attempts):
        request = urllib.request.Request(url, headers=REQUEST_HEADERS)
        attempt_error: str | None = None
        try:
            with opener(request, timeout=25) as response:
                status = response.status
                final_url = response.geturl()
                body = response.read(3_000_000)
        except urllib.error.HTTPError as exc:
            status = exc.code
            final_url = exc.geturl() or url
            body = exc.read(200_000)
            attempt_error = f"http_error:{exc.code}"
        except Exception as exc:  # noqa: BLE001
            status = None
            final_url = url
            body = b""
            attempt_error = f"fetch_error:{type(exc).__name__}:{exc}"

        retryable = (
            status in RETRYABLE_HTTP_STATUSES
            if status is not None
            else isinstance(attempt_error, str)
        )
        attempts.append(
            {
                "attempt": index + 1,
                "status": status,
                "final_url": final_url,
                "response_bytes": len(body),
                "error": attempt_error,
                "retryable": retryable,
            }
        )
        if attempt_error is None and status == 200:
            terminal_error = None
            break
        if not retryable or index == max_attempts - 1:
            terminal_error = attempt_error or f"unexpected_status:{status}"
            break
        sleeper(delays[index])

    return {
        "status": status,
        "final_url": final_url,
        "body": body,
        "attempts": attempts,
        "terminal_error": terminal_error,
    }


def main() -> int:
    campaign = json.loads((ROOT / "config/campaign.json").read_text(encoding="utf-8"))
    url = campaign["channels"]["note_product_url"]
    expected_title = campaign["product"]["title"]
    fetched = fetch_public_page(url)
    status = fetched["status"]
    final_url = fetched["final_url"]
    body = fetched["body"]
    attempts = fetched["attempts"]

    errors: list[str] = []
    warnings: list[str] = []
    if fetched["terminal_error"]:
        errors.append(fetched["terminal_error"])
    elif len(attempts) > 1:
        warnings.append(f"transient_fetch_recovered_after:{len(attempts)}_attempts")

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
        "fetch_attempt_count": len(attempts),
        "fetch_attempts": attempts,
        "retry_policy": {
            "max_attempts": len(RETRY_DELAYS_SECONDS) + 1,
            "delays_seconds": list(RETRY_DELAYS_SECONDS),
            "retryable_http_statuses": sorted(RETRYABLE_HTTP_STATUSES),
        },
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
