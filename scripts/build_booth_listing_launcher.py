#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE_PATH = ROOT / "content" / "booth" / "title.txt"
DESCRIPTION_PATH = ROOT / "content" / "booth" / "description.md"
TAGS_PATH = ROOT / "content" / "booth" / "tags.txt"
ARTIFACT_MANIFEST = ROOT / "artifacts" / "manifest.json"
OUTPUT = ROOT / "dist" / "booth_listing_launcher.html"
REPORT = ROOT / "reports" / "booth_listing.json"

PRICE_YEN = 1480
SERVICE_RATE = 0.056
FIXED_FEE_YEN = 45
MAX_FILE_BYTES = 1_200_000_000
BOOTH_GUIDE_URL = "https://booth.pm/guide"
BOOTH_MANAGER_URL = "https://manage.booth.pm/"
OFFICIAL_SOURCES = [
    "https://booth.pm/guide",
    "https://booth.pm/announcements/832",
    "https://booth.pm/announcements/916",
    "https://booth.pm/announcements/950",
    "https://booth.pm/customer_guide",
]


def load_product() -> dict:
    manifest = json.loads(ARTIFACT_MANIFEST.read_text(encoding="utf-8"))
    for item in manifest.get("artifacts", []):
        if item.get("id") == "product_v1_1":
            return item
    raise ValueError("product_v1_1 is missing from artifact manifest")


def main() -> int:
    title = TITLE_PATH.read_text(encoding="utf-8").strip()
    description = DESCRIPTION_PATH.read_text(encoding="utf-8").strip()
    tags = [line.strip() for line in TAGS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    product = load_product()
    errors: list[str] = []

    if not 20 <= len(title) <= 100:
        errors.append("title_length_out_of_range")
    if len(description) < 1400:
        errors.append("description_too_short")
    if not 5 <= len(tags) <= 10:
        errors.append("tag_count_out_of_range")
    if len(tags) != len(set(tags)):
        errors.append("duplicate_tags")
    if "ダウンロード商品" not in description:
        errors.append("download_product_disclosure_missing")
    if "再生数、収益、YouTube収益化審査を保証しません" not in description:
        errors.append("earnings_disclaimer_missing")
    if "再配布・転売は禁止" not in description:
        errors.append("redistribution_rule_missing")
    if "https://note.com/" in description:
        errors.append("external_note_promotion_found")
    for placeholder in ("TODO", "[要確認]", "ここに"):
        if placeholder in title or placeholder in description:
            errors.append(f"placeholder_found:{placeholder}")

    product_bytes = int(product["bytes"])
    if product_bytes >= MAX_FILE_BYTES:
        errors.append("product_exceeds_booth_file_limit")
    if product.get("zip_members") != 15:
        errors.append("unexpected_zip_member_count")
    product_output = str(product["output"])
    if not product_output.endswith(".zip"):
        errors.append("product_output_is_not_zip")

    variable_fee = math.ceil(PRICE_YEN * SERVICE_RATE)
    service_fee = variable_fee + FIXED_FEE_YEN
    estimated_net = PRICE_YEN - service_fee

    payload = json.dumps(
        {
            "title": title,
            "description": description,
            "tags": tags,
            "price": PRICE_YEN,
            "productPath": product_output,
            "productBytes": product_bytes,
            "serviceFee": service_fee,
            "estimatedNet": estimated_net,
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")

    source_links = "\n".join(
        f'<li><a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(url)}</a></li>'
        for url in OFFICIAL_SOURCES
    )

    document = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="color-scheme" content="light dark">
  <title>BOOTH出品ランチャー</title>
  <style>
    :root {{ font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", sans-serif; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: Canvas; color: CanvasText; }}
    main {{ max-width: 780px; margin: 0 auto; padding: max(20px, env(safe-area-inset-top)) 16px max(28px, env(safe-area-inset-bottom)); }}
    h1 {{ font-size: 1.45rem; line-height: 1.4; margin: 0 0 8px; }}
    .lead, .small {{ line-height: 1.65; opacity: .78; }}
    .small {{ font-size: .88rem; }}
    .card {{ border: 1px solid color-mix(in srgb, CanvasText 18%, transparent); border-radius: 16px; padding: 16px; margin: 14px 0; }}
    label {{ display: block; font-weight: 750; margin: 12px 0 7px; }}
    input, textarea, button, a.button {{ width: 100%; font: inherit; border-radius: 12px; }}
    input, textarea {{ border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); background: Canvas; color: CanvasText; padding: 12px; }}
    textarea {{ min-height: 340px; line-height: 1.65; resize: vertical; }}
    .actions {{ display: grid; gap: 10px; margin-top: 14px; }}
    button, a.button {{ border: 0; padding: 14px 16px; font-weight: 750; text-align: center; text-decoration: none; cursor: pointer; }}
    button.primary {{ background: #111; color: #fff; }}
    button.secondary, a.button {{ background: color-mix(in srgb, CanvasText 10%, Canvas); color: CanvasText; }}
    .status {{ min-height: 1.5em; line-height: 1.5; font-weight: 700; }}
    code {{ overflow-wrap: anywhere; }}
    ul {{ line-height: 1.7; padding-left: 1.25rem; }}
    .summary {{ display: grid; grid-template-columns: 1fr auto; gap: 8px 14px; line-height: 1.5; }}
  </style>
</head>
<body>
<main>
  <h1>BOOTH出品ランチャー</h1>
  <p class="lead">実体のあるZIP商品をBOOTHでも販売するための入力一式です。外部サイトへの誘導だけを目的とせず、BOOTH上で購入・配布が完結する設計です。</p>

  <section class="card">
    <div class="summary">
      <span>価格</span><strong>¥{PRICE_YEN:,}</strong>
      <span>サービス利用料の概算</span><strong>¥{service_fee:,}</strong>
      <span>1販売あたり概算受取額</span><strong>¥{estimated_net:,}</strong>
      <span>アップロードするZIP</span><code>{html.escape(product_output)}</code>
      <span>ZIP容量</span><strong>{product_bytes:,} bytes</strong>
    </div>
    <p class="small">概算受取額は、BOOTH公式の5.6%＋45円、小数点以下切り上げを使った計算です。振込・税務・その他の個別条件は含みません。</p>
  </section>

  <section class="card">
    <label for="title">商品名</label>
    <input id="title">
    <label for="description">商品説明</label>
    <textarea id="description"></textarea>
    <label for="tags">タグ（1行1件）</label>
    <textarea id="tags" style="min-height:180px"></textarea>
    <div class="actions">
      <button class="primary" id="copyAll" type="button">出品情報をまとめてコピー</button>
      <button class="secondary" id="copyTitle" type="button">商品名をコピー</button>
      <button class="secondary" id="copyDescription" type="button">説明をコピー</button>
      <button class="secondary" id="copyTags" type="button">タグをコピー</button>
      <a class="button" href="{BOOTH_MANAGER_URL}" target="_blank" rel="noopener">BOOTHの商品管理を開く</a>
      <a class="button" href="{BOOTH_GUIDE_URL}" target="_blank" rel="noopener">BOOTH公式の出品ガイドを確認</a>
    </div>
    <p class="status" id="status" role="status" aria-live="polite"></p>
  </section>

  <section class="card">
    <strong>本人操作として残るもの</strong>
    <ul>
      <li>BOOTHへログインし、ダウンロード商品を作成する</li>
      <li>生成済みのタイトル・説明・タグ・価格を貼り、ZIPを選択する</li>
      <li>表示と受取先を確認して最終公開する</li>
    </ul>
    <p class="small">ショップ未開設の場合は、受取先としてPayPalまたは日本の銀行口座の設定が必要です。認証情報や決済情報はこのランチャーへ保存しません。</p>
  </section>

  <section class="card">
    <strong>確認済み公式情報</strong>
    <ul>{source_links}</ul>
  </section>
</main>
<script id="listing-data" type="application/json">{payload}</script>
<script>
(() => {{
  'use strict';
  const data = JSON.parse(document.getElementById('listing-data').textContent);
  const title = document.getElementById('title');
  const description = document.getElementById('description');
  const tags = document.getElementById('tags');
  const status = document.getElementById('status');
  title.value = data.title;
  description.value = data.description;
  tags.value = data.tags.join('\\n');

  async function copyText(text) {{
    if (navigator.clipboard && window.isSecureContext) {{
      await navigator.clipboard.writeText(text);
      return;
    }}
    const temp = document.createElement('textarea');
    temp.value = text;
    temp.setAttribute('readonly', '');
    temp.style.position = 'fixed';
    temp.style.opacity = '0';
    document.body.appendChild(temp);
    temp.select();
    const ok = document.execCommand('copy');
    temp.remove();
    if (!ok) throw new Error('copy failed');
  }}

  async function run(text, message) {{
    try {{
      await copyText(text);
      status.textContent = message;
    }} catch {{
      status.textContent = '自動コピーに失敗しました。入力欄を長押ししてコピーしてください。';
    }}
  }}

  document.getElementById('copyAll').addEventListener('click', () => run(
    `商品名\n${{title.value.trim()}}\n\n価格\n¥${{data.price}}\n\n商品説明\n${{description.value.trim()}}\n\nタグ\n${{tags.value.trim()}}\n\n商品ZIP\n${{data.productPath}}`,
    '商品名・価格・説明・タグ・ZIPパスをコピーしました。'
  ));
  document.getElementById('copyTitle').addEventListener('click', () => run(title.value.trim(), '商品名をコピーしました。'));
  document.getElementById('copyDescription').addEventListener('click', () => run(description.value.trim(), '商品説明をコピーしました。'));
  document.getElementById('copyTags').addEventListener('click', () => run(tags.value.trim(), 'タグをコピーしました。'));
}})();
</script>
</body>
</html>
"""

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(document, encoding="utf-8")
    digest = hashlib.sha256(document.encode("utf-8")).hexdigest()
    report = {
        "ok": not errors,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "channel": "BOOTH",
        "title_chars": len(title),
        "description_chars": len(description),
        "tag_count": len(tags),
        "price_yen": PRICE_YEN,
        "service_rate": SERVICE_RATE,
        "fixed_fee_yen": FIXED_FEE_YEN,
        "estimated_service_fee_yen": service_fee,
        "estimated_net_per_sale_yen": estimated_net,
        "product_output": product_output,
        "product_bytes": product_bytes,
        "product_zip_members": product.get("zip_members"),
        "booth_file_limit_bytes": MAX_FILE_BYTES,
        "output": str(OUTPUT.relative_to(ROOT)),
        "sha256": digest,
        "official_sources": OFFICIAL_SOURCES,
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
