#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "booth_distribution.json"
OUTPUT = ROOT / "handoff" / "BOOTH_SHARE.md"
REPORT = ROOT / "reports" / "booth_public_distribution.json"


class ProductSchemaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.capture = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "script" and values.get("type") == "application/ld+json":
            self.capture = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script":
            self.capture = False

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.parts.append(data)


def tracked_url(base: str, source: str, medium: str, campaign: str, content: str) -> str:
    parsed = urllib.parse.urlsplit(base)
    query = [
        (key, value)
        for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        if not key.startswith("utm_")
    ]
    query.extend(
        (
            ("utm_source", source),
            ("utm_medium", medium),
            ("utm_campaign", campaign),
            ("utm_content", content),
        )
    )
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), parsed.fragment)
    )


def prefilled_url(target: str, text: str, url: str) -> str:
    if target == "x":
        return "https://twitter.com/intent/tweet?" + urllib.parse.urlencode(
            {"text": text, "url": url}
        )
    if target == "bluesky":
        return "https://bsky.app/intent/compose?" + urllib.parse.urlencode(
            {"text": f"{text}\n{url}"}
        )
    raise ValueError(f"unsupported_target:{target}")


def conservative_x_weight(text: str) -> int:
    """Approximate X's weighted length conservatively for the supported copy."""
    return sum(1 if ord(character) < 128 else 2 for character in text) + 1 + 23


def verify_distribution_rows(rows: list[dict[str, str]], campaign: str) -> dict[str, int]:
    errors: list[str] = []
    combinations = {(row["target"], row["variant"]) for row in rows}
    if len(rows) != 6 or len(combinations) != 6:
        errors.append(f"combination_count:{len(rows)}:{len(combinations)}")

    max_x_weight = 0
    max_bluesky_length = 0
    for row in rows:
        parsed = urllib.parse.urlsplit(row["tracked_url"])
        query = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
        expected = {
            "utm_source": row["target"],
            "utm_medium": "social",
            "utm_campaign": campaign,
            "utm_content": row["variant"],
        }
        if parsed.scheme != "https" or parsed.netloc != "mobile-ai-studio.booth.pm":
            errors.append(f"tracked_url_origin:{row['target']}:{row['variant']}")
        if any(query.get(key) != value for key, value in expected.items()):
            errors.append(f"tracking_contract:{row['target']}:{row['variant']}")
        if row["target"] == "x":
            weight = conservative_x_weight(row["text"])
            max_x_weight = max(max_x_weight, weight)
            if weight > 280:
                errors.append(f"x_weight:{row['variant']}:{weight}")
        elif row["target"] == "bluesky":
            length = len(row["text"]) + 1 + len(row["tracked_url"])
            max_bluesky_length = max(max_bluesky_length, length)
            if length > 300:
                errors.append(f"bluesky_length:{row['variant']}:{length}")

    if errors:
        raise ValueError(";".join(errors))
    return {
        "max_x_weight": max_x_weight,
        "max_bluesky_length": max_bluesky_length,
    }


def verify_config(config: dict[str, Any]) -> None:
    if config.get("schema_version") != "1.0":
        raise ValueError("config_schema_version")
    product = config.get("product")
    if not isinstance(product, dict):
        raise ValueError("config_product")
    if product.get("id") != "8691522":
        raise ValueError("product_id")
    if product.get("url") != "https://mobile-ai-studio.booth.pm/items/8691522":
        raise ValueError("product_url")
    if product.get("price_yen") != 1480 or product.get("type") != "download":
        raise ValueError("product_price_or_type")
    target_ids = [item.get("id") for item in config.get("targets", [])]
    if target_ids != ["x", "bluesky"]:
        raise ValueError("target_contract")
    variant_ids = [item.get("id") for item in config.get("variants", [])]
    if variant_ids != ["contents", "smartphone", "non_repetitive"]:
        raise ValueError("variant_contract")
    if config.get("automation") != {
        "cost_yen": 0,
        "credentials_used": False,
        "final_publish": "authenticated_account_holder_confirmation_required",
    }:
        raise ValueError("automation_contract")


def fetch_public_page(url: str) -> tuple[int | None, str, bytes, list[str]]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1",
            "Accept-Language": "ja,en-US;q=0.8,en;q=0.6",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    errors: list[str] = []
    status: int | None = None
    final_url = url
    body = b""
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            status = response.status
            final_url = response.geturl()
            body = response.read(4_000_000)
    except urllib.error.HTTPError as exc:
        status = exc.code
        errors.append(f"http_error:{exc.code}")
        body = exc.read(200_000)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"fetch_error:{type(exc).__name__}:{exc}")
    return status, final_url, body, errors


def verify_public_page(config: dict[str, Any]) -> dict[str, Any]:
    product = config["product"]
    status, final_url, body, errors = fetch_public_page(product["url"])
    text = body.decode("utf-8", errors="replace")
    if status != 200:
        errors.append(f"unexpected_status:{status}")
    if final_url.rstrip("/") != product["url"]:
        errors.append(f"unexpected_final_url:{final_url}")

    parser = ProductSchemaParser()
    parser.feed(text)
    schema: dict[str, Any] = {}
    for part in parser.parts:
        try:
            candidate = json.loads(part)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict) and candidate.get("@type") == "Product":
            schema = candidate
            break
    if not schema:
        errors.append("product_schema_missing")
    else:
        offers = schema.get("offers", {})
        brand = schema.get("brand", {})
        if schema.get("name") != product["title"]:
            errors.append("schema_title")
        if str(offers.get("price")) != "1480" or offers.get("priceCurrency") != "JPY":
            errors.append("schema_price")
        if offers.get("availability") != "https://schema.org/InStock":
            errors.append("schema_availability")
        if brand.get("name") != product["shop"]:
            errors.append("schema_brand")

    required_markers = [
        'data-product-id="8691522"',
        '<span class="type">ダウンロード商品</span>',
        '<div class="variation-price">¥ 1,480</div>',
        'class="btn rounded-oval add-cart full-length"',
        '<div class="state-private" style="display:none">',
    ]
    for marker in required_markers:
        if marker not in text:
            errors.append("page_marker_missing:" + marker[:40])
    image_urls = set(
        re.findall(
            r'data-origin="(https://booth\.pximg\.net/[^"]+/i/8691522/[^"]+\.png)"',
            text,
        )
    )
    if len(image_urls) != 3:
        errors.append(f"image_count:{len(image_urls)}")

    return {
        "ok": not errors,
        "status": status,
        "final_url": final_url,
        "response_bytes": len(body),
        "response_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "download_product": "ダウンロード商品" in text,
        "price_yen": 1480 if "¥ 1,480" in text else None,
        "image_count": len(image_urls),
        "cart_form_present": "add-cart full-length" in text,
        "schema_in_stock": schema.get("offers", {}).get("availability") == "https://schema.org/InStock",
        "errors": errors,
    }


def build_handoff(config: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    product = config["product"]
    campaign = config["tracking"]["utm_campaign"]
    rows: list[dict[str, str]] = []
    for variant in config["variants"]:
        for target in config["targets"]:
            tracked = tracked_url(
                product["url"],
                target["utm_source"],
                target["utm_medium"],
                campaign,
                variant["id"],
            )
            rows.append(
                {
                    "target": target["id"],
                    "target_label": target["label"],
                    "variant": variant["id"],
                    "variant_label": variant["label"],
                    "text": variant["text"],
                    "tracked_url": tracked,
                    "prefilled_url": prefilled_url(target["id"], variant["text"], tracked),
                }
            )

    lines = [
        "# 公開済みBOOTH商品を告知",
        "",
        f"商品: {product['title']}",
        "",
        f"価格: {product['price_yen']:,}円",
        "",
        f"[商品ページを確認]({product['url']})",
        "",
        "下のリンクは本文と媒体別UTMを入力済みです。本人アカウントで内容を確認し、最終公開してください。",
        "",
    ]
    for variant in config["variants"]:
        lines.extend((f"## {variant['label']}", "", variant["text"], ""))
        selected = [row for row in rows if row["variant"] == variant["id"]]
        for row in selected:
            lines.append(f"[{row['target_label']}で告知]({row['prefilled_url']})")
        lines.append("")
    lines.extend(
        (
            "## 計測",
            "",
            "各リンクには utm_source、utm_medium、utm_campaign=booth_launch_20260807、utm_content が入っています。",
            "",
            "費用0円。認証情報・Cookie・投稿権限は保存しません。",
            "",
        )
    )
    return "\n".join(lines), rows


def main() -> int:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    errors: list[str] = []
    try:
        verify_config(config)
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))

    verification = verify_public_page(config) if not errors else {
        "ok": False,
        "errors": ["config_invalid_fetch_skipped"],
    }
    errors.extend(verification.get("errors", []))
    document, rows = build_handoff(config) if not errors else ("", [])
    row_validation: dict[str, int] = {}
    if rows:
        try:
            row_validation = verify_distribution_rows(rows, config["tracking"]["utm_campaign"])
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(str(exc))
            document = ""
    if document:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(document, encoding="utf-8", newline="\n")

    payload = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "assistant_operational_validation_not_permanent_directive",
        "product_id": config.get("product", {}).get("id"),
        "product_url": config.get("product", {}).get("url"),
        "public_page": verification,
        "distribution": {
            "targets": len(config.get("targets", [])),
            "variants": len(config.get("variants", [])),
            "combinations": len(rows),
            "campaign": config.get("tracking", {}).get("utm_campaign"),
            "output": str(OUTPUT.relative_to(ROOT)),
            "output_sha256": hashlib.sha256(document.encode("utf-8")).hexdigest() if document else None,
            "row_validation": row_validation,
        },
        "cost_yen": 0,
        "credentials_used": False,
        "final_external_post_performed": False,
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
