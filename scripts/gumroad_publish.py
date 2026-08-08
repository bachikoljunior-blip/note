#!/usr/bin/env python3
"""Gumroad へ商品を作り、値段と文面を入れ、公開し、公開面を読み直して確認する。

受取方法が未接続だと公開は必ず弾かれる（2026-08-08 実測）。
    PUT /v2/products/:id/enable
    -> "You must connect at least one payment method before you can publish this product for sale."
接続後は、このスクリプト1本で作成から公開・検証まで通る。オーナー操作は要らない。

    GUMROAD_TOKEN=... python scripts/gumroad_publish.py --check     # 公開できる状態かだけ測る
    GUMROAD_TOKEN=... python scripts/gumroad_publish.py --dry-run   # 作る内容を出すだけ
    GUMROAD_TOKEN=... python scripts/gumroad_publish.py --execute --delivery-url https://...

価格は **円をそのまま** 渡す。JPY は小数の無い通貨で、`price=38000` が `¥38,000` になることを
2026-08-08 に実測した（USD アカウント時代のセント換算とは違う）。所在地を日本にした時点で
アカウント通貨が usd から jpy へ切り替わっているので、ここを取り違えると桁が2つずれる。

トークンは環境変数からだけ読む。ファイルにもリポジトリにも書かない。

APIで **できないこと**（実測）:
  - 納品ファイルの添付。`url` は受理されるが無視され `files` は空のまま。
    そのため納品は `custom_receipt`（購入後メッセージ）に置いた配信URLで行う。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.gumroad.com/v2"
PAYOUT_BLOCKER = "connect at least one payment method"

# 価格の単位は通貨で変わる。USD は最小単位（セント）だが、JPY は小数の無い通貨なので
# 円をそのまま渡す。2026-08-08 実測: price=38000 -> formatted_price "¥38,000"。
# アカウント通貨は所在地を日本にした時点で usd から jpy へ切り替わった。
PRODUCTS = [
    {
        "key": "standard",
        "name": "設定1枚で自社ブランドになる放置クリッカー｜ビルド不要・依存ゼロ・スマホ対応",
        "price_jpy": 3800,
        "license": "【通常ライセンス】自分の店・自社・自分のチャンネルのために、公開先1つで使えます。商用可・改変自由。クライアントの案件に納品する場合は拡張ライセンスが必要です。",
    },
    {
        "key": "extended",
        "name": "設定1枚で自社ブランドになる放置クリッカー｜拡張ライセンス（クライアントワーク納品可）",
        "price_jpy": 38000,
        "license": "【拡張ライセンス】クライアントの案件へ組み込んで納品できます。件数の上限はありません。ご自身が運営する複数のサイトでも使えます。",
    },
]

DESCRIPTION = (
    "<p><strong>設定ファイル1枚を書き換えるだけで、自分の店・商品・チャンネルの放置ゲームになります。</strong>"
    "題名・配色・数えるものの名前・増やすもの8種・強化6種・到達メッセージ・誘導ボタン・フッターまで、"
    "すべて <code>brand.config.json</code> から決まります。</p>"
    "<ul>"
    "<li><strong>ビルド不要。</strong>フォルダを静的ホスティングに置くだけで動きます</li>"
    "<li><strong>外部ライブラリなし・通信なし。</strong>あなたが設定したリンク以外へは何も送りません</li>"
    "<li>セーブは端末内。サーバーもデータベースも要りません</li>"
    "<li>スマホ縦画面前提。片手・タップだけで遊べます</li>"
    "<li><code>generator.html</code> — フォームを埋めると設定ファイルが出てきます</li>"
    "<li>書き換え例3種（珈琲店・サロン・配信者）を同梱</li>"
    "<li>実ブラウザで20項目を自動検査。検査スクリプトも同梱</li>"
    "</ul>"
    "<p>遊びの速さ（値段と毎秒の量）は釣り合いを取った既定値が入っているので、"
    "名前を変えるだけで成立します。</p>"
    "<p>効果音・BGM・画像素材は入っていません。表示は絵文字とCSSだけで作っています。"
    "売上や集客を保証するものではありません。</p>"
)


def call(token: str, method: str, path: str, **fields):
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


def receipt(delivery_url: str, license_text: str) -> str:
    return (
        "お買い上げありがとうございます。こちらからダウンロードしてください。\n"
        f"{delivery_url}\n\n"
        f"{license_text}\n\n"
        "まず README.md を読むか、generator.html を開いてフォームを埋めてください。"
    )


def can_publish(token: str) -> tuple[bool, str]:
    """使い捨ての商品で公開を試し、通るかどうかだけを返す。商品は必ず消す。"""
    status, body = call(token, "POST", "/products", name="payout state probe", price="100")
    product = body.get("product") if isinstance(body, dict) else None
    if not product:
        return False, f"probe_create_failed: {str(body)[:150]}"
    pid = product["id"]
    try:
        _, enabled = call(token, "PUT", f"/products/{pid}/enable")
        message = enabled.get("message", "") if isinstance(enabled, dict) else ""
        _, fetched = call(token, "GET", f"/products/{pid}")
        published = fetched.get("product", {}).get("published") if isinstance(fetched, dict) else None
        if published:
            return True, "publishable"
        if PAYOUT_BLOCKER in message:
            return False, "payout_method_not_connected"
        return False, f"not_published: {message or 'no message'}"
    finally:
        call(token, "DELETE", f"/products/{pid}")


def verify_public(url: str) -> tuple[int | None, bool]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, b"gumroad" in resp.read(4000).lower()
    except urllib.error.HTTPError as exc:
        return exc.code, False
    except Exception:  # noqa: BLE001
        return None, False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="公開できる状態かだけ測る")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--delivery-url", default="")
    args = parser.parse_args()

    token = os.environ.get("GUMROAD_TOKEN", "").strip()
    if not token:
        print("GUMROAD_TOKEN が環境変数にありません。")
        return 2

    ok, reason = can_publish(token)
    if args.check or not args.execute:
        print(json.dumps({"publishable": ok, "reason": reason,
                          "products_that_would_be_created":
                              [{"name": p["name"], "jpy": p["price_jpy"]} for p in PRODUCTS]},
                         ensure_ascii=False, indent=2))
        return 0 if ok else 1

    if not ok:
        print(json.dumps({"aborted": True, "reason": reason}, ensure_ascii=False, indent=2))
        return 1
    if not args.delivery_url.startswith("https://"):
        # 納品先が無いまま公開すると、払って何も届かない商品になる。
        # 公開リポジトリを配信先にする案は 2026-08-08 に取り下げた:
        # kit は公開なので、パスをランダムにしてもディレクトリ一覧にファイル名が出る。
        # 「推測できないURL」は成立せず、有料商品が誰でも取れてしまう。
        # 現状の正しい納品は、Gumroad の管理画面で1回だけファイルを添付すること。
        print("--delivery-url が無いか https:// で始まっていません。")
        print("納品先の無い商品は公開しません。Gumroad へファイルを添付済みなら、")
        print("--delivery-url にその商品ページURLを渡すか、購入後メッセージを空のまま使ってください。")
        return 2

    results = []
    for spec in PRODUCTS:
        _, body = call(token, "POST", "/products", name=spec["name"], price=str(spec["price_jpy"]))
        product = body.get("product") if isinstance(body, dict) else None
        if not product:
            results.append({"key": spec["key"], "status": "create_failed", "detail": str(body)[:200]})
            continue
        pid = product["id"]
        call(token, "PUT", f"/products/{pid}", description=DESCRIPTION)
        call(token, "PUT", f"/products/{pid}",
             custom_receipt=receipt(args.delivery_url, spec["license"]))
        call(token, "PUT", f"/products/{pid}/enable")

        # 応答を信じず、読み直す
        _, fetched = call(token, "GET", f"/products/{pid}")
        p = fetched.get("product", {})
        short = p.get("short_url", "")
        http_status, looks_live = verify_public(short) if short else (None, False)
        results.append({
            "key": spec["key"], "id": pid, "name": p.get("name"),
            "price_jpy": p.get("price"), "formatted_price": p.get("formatted_price"),
            "published": p.get("published"),
            "short_url": short, "public_http": http_status, "public_page_loaded": looks_live,
            "receipt_set": bool(p.get("custom_receipt")),
            "description_set": bool(p.get("description")),
        })

    all_live = all(r.get("published") and r.get("public_http") == 200 for r in results)
    print(json.dumps({"all_live": all_live, "results": results}, ensure_ascii=False, indent=2))
    return 0 if all_live else 1


if __name__ == "__main__":
    sys.exit(main())
