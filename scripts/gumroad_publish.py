#!/usr/bin/env python3
"""Safely configure and publish one existing Gumroad product.

Gumroad's API cannot attach buyer content. Execution therefore works only on an
explicit existing product and fails closed unless the API read-back reports at
least one attached file both before metadata changes and immediately before
enablement. A public URL is never treated as paid-product delivery.

Examples:
    GUMROAD_TOKEN=... python scripts/gumroad_publish.py --check \
        --existing-product-id PRODUCT_ID
    python scripts/gumroad_publish.py --dry-run --tier extended
    GUMROAD_TOKEN=... python scripts/gumroad_publish.py --execute \
        --existing-product-id PRODUCT_ID --tier extended

The token is read only from the environment and is never printed or stored.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


BASE = "https://api.gumroad.com/v2"

PRODUCTS = {
    "standard": {
        "key": "standard",
        "name": "設定1枚で自社ブランドになる放置クリッカー｜ビルド不要・依存ゼロ・スマホ対応",
        "price_jpy": 3800,
        "license": "【通常ライセンス】自分の店・自社・自分のチャンネルのために、公開先1つで使えます。商用可・改変自由。クライアントの案件に納品する場合は拡張ライセンスが必要です。",
    },
    "extended": {
        "key": "extended",
        "name": "設定1枚で自社ブランドになる放置クリッカー｜拡張ライセンス（クライアントワーク納品可）",
        "price_jpy": 38000,
        "license": "【拡張ライセンス】クライアントの案件へ組み込んで納品できます。件数の上限はありません。ご自身が運営する複数のサイトでも使えます。",
    },
}

DESCRIPTION = (
    "<p><strong>設定ファイル1枚を書き換えるだけで、自分の店・商品・チャンネルの放置ゲームになります。</strong>"
    "題名・配色・数えるものの名前・増やすもの8種・強化6種・到達メッセージ・誘導ボタン・フッターまで、"
    "すべて <code>brand.config.json</code> から決まります。</p>"
    "<ul>"
    "<li><strong>ビルド不要。</strong>フォルダを静的ホスティングに置くだけで動きます</li>"
    "<li><strong>外部ライブラリなし・通信なし。</strong>設定したリンク以外へは何も送りません</li>"
    "<li>セーブは端末内。サーバーもデータベースも要りません</li>"
    "<li>スマホ縦画面前提。片手・タップだけで遊べます</li>"
    "<li><code>generator.html</code> で設定ファイルを生成できます</li>"
    "<li>書き換え例3種と実ブラウザ検査スクリプトを同梱</li>"
    "</ul>"
    "<p>効果音・BGM・画像素材は含みません。売上や集客を保証するものではありません。</p>"
)


def call(token: str, method: str, path: str, **fields: str) -> tuple[int, dict[str, Any]]:
    fields["access_token"] = token
    data = urllib.parse.urlencode(fields).encode()
    url = f"{BASE}{path}" + (f"?{data.decode()}" if method == "GET" else "")
    req = urllib.request.Request(url, data=None if method == "GET" else data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()[:400]
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"raw": raw}


def product_from(body: Any) -> dict[str, Any]:
    if not isinstance(body, dict):
        return {}
    product = body.get("product")
    return product if isinstance(product, dict) else {}


def attached_file_count(product: dict[str, Any]) -> int:
    """Return the API-reported buyer-content count; missing/ambiguous data is zero."""
    files = product.get("files")
    if not isinstance(files, list):
        return 0
    return sum(1 for item in files if item)


def receipt(license_text: str) -> str:
    return (
        "お買い上げありがとうございます。購入内容から添付ZIPをダウンロードしてください。\n\n"
        f"{license_text}\n\n"
        "まず README.md を読むか、generator.html を開いてフォームを埋めてください。"
    )


def verify_public(url: str) -> tuple[int | None, bool]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, b"gumroad" in resp.read(4000).lower()
    except urllib.error.HTTPError as exc:
        return exc.code, False
    except Exception:  # noqa: BLE001
        return None, False


def fetch_product(token: str, product_id: str) -> tuple[int, dict[str, Any]]:
    status, body = call(token, "GET", f"/products/{product_id}")
    return status, product_from(body)


def readiness(token: str, product_id: str) -> dict[str, Any]:
    status, product = fetch_product(token, product_id)
    count = attached_file_count(product)
    return {
        "ready": status == 200 and bool(product) and count > 0 and not product.get("published"),
        "http_status": status,
        "product_found": bool(product),
        "attached_file_count": count,
        "published": bool(product.get("published")),
    }


def publish_existing(
    token: str,
    product_id: str,
    spec: dict[str, Any],
    *,
    test_purchase_confirmed: bool,
) -> dict[str, Any]:
    """Publish only after two independent API read-backs confirm attached content."""
    if not test_purchase_confirmed:
        return {"status": "aborted_test_purchase_not_confirmed"}
    before = readiness(token, product_id)
    if not before["ready"]:
        return {"status": "aborted_not_ready", **before}

    updates = (
        {"name": str(spec["name"]), "price": str(spec["price_jpy"])},
        {"description": DESCRIPTION},
        {"custom_receipt": receipt(str(spec["license"]))},
    )
    for fields in updates:
        status, body = call(token, "PUT", f"/products/{product_id}", **fields)
        if status < 200 or status >= 300 or (isinstance(body, dict) and body.get("success") is False):
            return {"status": "aborted_metadata_update_failed", "http_status": status}

    immediately_before_enable = readiness(token, product_id)
    if not immediately_before_enable["ready"]:
        return {"status": "aborted_content_missing_before_enable", **immediately_before_enable}

    status, body = call(token, "PUT", f"/products/{product_id}/enable")
    if status < 200 or status >= 300 or (isinstance(body, dict) and body.get("success") is False):
        return {"status": "enable_failed", "http_status": status}

    fetched_status, product = fetch_product(token, product_id)
    file_count = attached_file_count(product)
    short_url = product.get("short_url", "") if product else ""
    public_http, public_loaded = verify_public(short_url) if short_url else (None, False)
    safe = (
        fetched_status == 200
        and bool(product.get("published"))
        and file_count > 0
        and public_http == 200
        and public_loaded
    )
    if not safe:
        call(token, "PUT", f"/products/{product_id}/disable")
        return {
            "status": "verification_failed_disabled",
            "published_readback": bool(product.get("published")),
            "attached_file_count": file_count,
            "public_http": public_http,
            "public_page_loaded": public_loaded,
        }
    return {
        "status": "published_verified",
        "tier": spec["key"],
        "price_jpy": product.get("price"),
        "formatted_price": product.get("formatted_price"),
        "attached_file_count": file_count,
        "short_url": short_url,
        "public_http": public_http,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--existing-product-id", default="")
    parser.add_argument("--tier", choices=sorted(PRODUCTS), default="extended")
    parser.add_argument(
        "--test-purchase-confirmed",
        action="store_true",
        help="Confirm the creator test purchase downloaded the attached ZIP before enablement",
    )
    args = parser.parse_args()

    spec = PRODUCTS[args.tier]
    if args.dry_run:
        print(json.dumps({"mode": "dry_run", "product": spec}, ensure_ascii=False, indent=2))
        return 0

    token = os.environ.get("GUMROAD_TOKEN", "").strip()
    if not token or not args.existing_product_id:
        print(json.dumps({"aborted": True, "reason": "token_or_existing_product_id_missing"}))
        return 2

    if args.check:
        result = readiness(token, args.existing_product_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["ready"] else 1

    result = publish_existing(
        token,
        args.existing_product_id,
        spec,
        test_purchase_confirmed=args.test_purchase_confirmed,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "published_verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
