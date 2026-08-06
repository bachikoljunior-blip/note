#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "distribution.json"
OUTPUT = ROOT / "dist" / "share_launcher.html"
REPORT = ROOT / "reports" / "share_launcher.json"


def main() -> int:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    product = config["product"]
    variants = config["variants"]
    default_id = config["default_variant"]

    if not variants:
        raise ValueError("distribution variants are empty")
    if default_id not in {item["id"] for item in variants}:
        raise ValueError("default_variant does not exist")
    if not str(product["url"]).startswith("https://note.com/"):
        raise ValueError("product URL is not a note URL")

    payload = {
        "title": product["title"],
        "url": product["url"],
        "defaultVariant": default_id,
        "variants": variants,
    }
    embedded = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    title = html.escape(product["title"])

    document = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="color-scheme" content="light dark">
  <title>note告知ランチャー</title>
  <style>
    :root {{ font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", sans-serif; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: Canvas; color: CanvasText; }}
    main {{ max-width: 680px; margin: 0 auto; padding: max(20px, env(safe-area-inset-top)) 18px max(28px, env(safe-area-inset-bottom)); }}
    h1 {{ font-size: 1.45rem; line-height: 1.35; margin: 0 0 8px; }}
    .lead {{ margin: 0 0 18px; opacity: .78; line-height: 1.65; }}
    .card {{ border: 1px solid color-mix(in srgb, CanvasText 18%, transparent); border-radius: 16px; padding: 16px; margin: 14px 0; background: color-mix(in srgb, Canvas 96%, CanvasText 4%); }}
    label {{ display: block; font-weight: 700; margin-bottom: 8px; }}
    select, textarea, button, a.button {{ width: 100%; font: inherit; border-radius: 12px; }}
    select, textarea {{ border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); background: Canvas; color: CanvasText; padding: 12px; }}
    textarea {{ min-height: 250px; line-height: 1.6; resize: vertical; margin-top: 12px; }}
    .actions {{ display: grid; gap: 10px; margin-top: 14px; }}
    button, a.button {{ border: 0; padding: 14px 16px; text-align: center; text-decoration: none; font-weight: 750; cursor: pointer; }}
    button.primary {{ background: #111; color: #fff; }}
    button.secondary, a.button {{ background: color-mix(in srgb, CanvasText 10%, Canvas); color: CanvasText; }}
    .status {{ min-height: 1.5em; margin: 12px 0 0; font-size: .95rem; line-height: 1.5; }}
    .done {{ font-weight: 700; }}
    .small {{ font-size: .88rem; line-height: 1.55; opacity: .72; }}
    ul {{ padding-left: 1.25rem; line-height: 1.65; }}
    code {{ overflow-wrap: anywhere; }}
  </style>
</head>
<body>
<main>
  <h1>note告知ランチャー</h1>
  <p class="lead">告知文の作成、商品URLの挿入、URL確認、共有試行時刻の記録は自動化済みです。残る本人操作は「共有先の選択」と「最終公開」だけです。</p>

  <section class="card">
    <label for="variant">告知文を選ぶ</label>
    <select id="variant"></select>
    <textarea id="message" aria-label="共有する告知文"></textarea>
    <div class="actions">
      <button class="primary" id="share" type="button">共有シートを開く</button>
      <button class="secondary" id="copy" type="button">告知文とURLをコピー</button>
      <a class="button" id="openProduct" target="_blank" rel="noopener">商品ページを確認</a>
      <button class="secondary" id="copyLog" type="button">公開記録テンプレをコピー</button>
    </div>
    <p class="status" id="status" role="status" aria-live="polite"></p>
  </section>

  <section class="card">
    <strong>自動化済み</strong>
    <ul>
      <li>3種類の告知文生成</li>
      <li>商品URLの自動挿入</li>
      <li>公開商品ページの自動検証</li>
      <li>共有シート非対応時のコピー切替</li>
      <li>共有試行時刻の端末内保存</li>
    </ul>
    <p class="small">共有先のアプリは、このページからは取得・保存しません。パスワード、Cookie、投稿権限も使用しません。費用は0円です。</p>
    <p class="small" id="lastAttempt"></p>
  </section>
</main>
<script id="share-data" type="application/json">{embedded}</script>
<script>
(() => {{
  'use strict';
  const data = JSON.parse(document.getElementById('share-data').textContent);
  const variant = document.getElementById('variant');
  const message = document.getElementById('message');
  const status = document.getElementById('status');
  const lastAttempt = document.getElementById('lastAttempt');
  const openProduct = document.getElementById('openProduct');

  function selected() {{
    return data.variants.find(item => item.id === variant.value) || data.variants[0];
  }}

  function fullText() {{
    return `${{message.value.trim()}}\n${{data.url}}`;
  }}

  function show(text, ok = false) {{
    status.textContent = text;
    status.className = ok ? 'status done' : 'status';
  }}

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
    const copied = document.execCommand('copy');
    temp.remove();
    if (!copied) throw new Error('copy failed');
  }}

  function recordAttempt() {{
    const value = new Date().toISOString();
    localStorage.setItem('noteShareAttemptAt', value);
    renderAttempt();
    return value;
  }}

  function renderAttempt() {{
    const value = localStorage.getItem('noteShareAttemptAt');
    lastAttempt.textContent = value ? `直近の共有操作: ${{new Date(value).toLocaleString('ja-JP')}}` : '共有操作はまだ記録されていません。';
  }}

  for (const item of data.variants) {{
    const option = document.createElement('option');
    option.value = item.id;
    option.textContent = item.label;
    variant.appendChild(option);
  }}
  variant.value = data.defaultVariant;
  message.value = selected().text;
  variant.addEventListener('change', () => {{ message.value = selected().text; show(''); }});
  openProduct.href = data.url;
  renderAttempt();

  document.getElementById('share').addEventListener('click', async () => {{
    const attemptedAt = recordAttempt();
    const shareData = {{ title: data.title, text: message.value.trim(), url: data.url }};
    if (navigator.share) {{
      try {{
        await navigator.share(shareData);
        show(`共有シートを完了しました。操作時刻: ${{new Date(attemptedAt).toLocaleString('ja-JP')}}`, true);
        return;
      }} catch (error) {{
        if (error && error.name === 'AbortError') {{
          show('共有はキャンセルされました。本文は保持されています。');
          return;
        }}
      }}
    }}
    try {{
      await copyText(fullText());
      show('共有シートを使えなかったため、告知文とURLをコピーしました。', true);
    }} catch {{
      show('自動コピーに失敗しました。本文欄を長押ししてコピーしてください。');
    }}
  }});

  document.getElementById('copy').addEventListener('click', async () => {{
    try {{
      await copyText(fullText());
      show('告知文と商品URLをコピーしました。', true);
    }} catch {{
      show('コピーに失敗しました。本文欄を長押ししてコピーしてください。');
    }}
  }});

  document.getElementById('copyLog').addEventListener('click', async () => {{
    const attemptedAt = localStorage.getItem('noteShareAttemptAt') || new Date().toISOString();
    const log = `公開先: [共有先を入力]\n公開または共有操作時刻: ${{attemptedAt}}\n商品URL: ${{data.url}}`;
    try {{
      await copyText(log);
      show('公開記録テンプレをコピーしました。', true);
    }} catch {{
      show(log);
    }}
  }});
}})();
</script>
</body>
</html>
"""

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(document, encoding="utf-8")
    digest = hashlib.sha256(document.encode("utf-8")).hexdigest()
    report = {
        "ok": True,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "output": str(OUTPUT.relative_to(ROOT)),
        "bytes": OUTPUT.stat().st_size,
        "sha256": digest,
        "variants": len(variants),
        "product_url": product["url"],
        "external_dependencies": 0,
        "cost_yen": 0,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
