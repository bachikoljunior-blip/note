#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE_PATH = ROOT / "content" / "note" / "funnel_policy_2026" / "title.txt"
BODY_PATH = ROOT / "content" / "note" / "funnel_policy_2026" / "body.md"
OUTPUT = ROOT / "dist" / "funnel_article_launcher.html"
REPORT = ROOT / "reports" / "funnel_article.json"
PRODUCT_URL = "https://note.com/mobile_ai_studio/n/n779329665155"
NOTE_EDITOR_URL = "https://note.com/new"
SOURCE_URLS = [
    "https://support.google.com/youtube/answer/1311392?hl=ja",
    "https://support.google.com/youtube/answer/14328491?co=GENIE.Platform%3DDesktop&hl=ja",
    "https://support.google.com/youtube/answer/2490020?hl=ja",
]


def main() -> int:
    title = TITLE_PATH.read_text(encoding="utf-8").strip()
    body = BODY_PATH.read_text(encoding="utf-8").strip()
    errors: list[str] = []

    if not 20 <= len(title) <= 100:
        errors.append("title_length_out_of_range")
    if len(body) < 2500:
        errors.append("body_too_short")
    if PRODUCT_URL not in body:
        errors.append("product_cta_missing")
    for source in SOURCE_URLS:
        if source not in body:
            errors.append(f"source_missing:{source}")
    for placeholder in ("TODO", "[要確認]", "ここに"):
        if placeholder in title or placeholder in body:
            errors.append(f"placeholder_found:{placeholder}")

    payload = json.dumps({"title": title, "body": body}, ensure_ascii=False).replace("</", "<\\/")
    escaped_title = html.escape(title)
    source_links = "\n".join(
        f'<li><a href="{html.escape(url)}" target="_blank" rel="noopener">公式情報を開く</a></li>'
        for url in SOURCE_URLS
    )

    document = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="color-scheme" content="light dark">
  <title>無料導線記事 投稿ランチャー</title>
  <style>
    :root {{ font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", sans-serif; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: Canvas; color: CanvasText; }}
    main {{ max-width: 760px; margin: 0 auto; padding: max(20px, env(safe-area-inset-top)) 16px max(28px, env(safe-area-inset-bottom)); }}
    h1 {{ font-size: 1.4rem; line-height: 1.4; margin: 0 0 10px; }}
    .lead {{ line-height: 1.7; opacity: .8; }}
    .card {{ border: 1px solid color-mix(in srgb, CanvasText 18%, transparent); border-radius: 16px; padding: 16px; margin: 14px 0; }}
    label {{ display: block; font-weight: 750; margin: 12px 0 7px; }}
    input, textarea, button, a.button {{ width: 100%; font: inherit; border-radius: 12px; }}
    input, textarea {{ border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); background: Canvas; color: CanvasText; padding: 12px; }}
    textarea {{ min-height: 360px; line-height: 1.65; resize: vertical; }}
    .actions {{ display: grid; gap: 10px; margin-top: 14px; }}
    button, a.button {{ border: 0; padding: 14px 16px; font-weight: 750; text-align: center; text-decoration: none; cursor: pointer; }}
    button.primary {{ background: #111; color: #fff; }}
    button.secondary, a.button {{ background: color-mix(in srgb, CanvasText 10%, Canvas); color: CanvasText; }}
    .status {{ min-height: 1.5em; line-height: 1.5; font-weight: 700; }}
    ul {{ line-height: 1.7; padding-left: 1.25rem; }}
    .small {{ font-size: .88rem; opacity: .75; line-height: 1.6; }}
  </style>
</head>
<body>
<main>
  <h1>無料導線記事 投稿ランチャー</h1>
  <p class="lead">高関心のYouTube収益化ポリシーを入口にし、公開中の有料制作キットへ自然につなぐ無料記事です。調査、本文、公式出典、商品CTAは作成済みです。</p>

  <section class="card">
    <label for="title">タイトル</label>
    <input id="title" value="{escaped_title}">
    <label for="body">本文</label>
    <textarea id="body"></textarea>
    <div class="actions">
      <button class="primary" id="copyAll" type="button">タイトルと本文をまとめてコピー</button>
      <button class="secondary" id="copyTitle" type="button">タイトルだけコピー</button>
      <button class="secondary" id="copyBody" type="button">本文だけコピー</button>
      <a class="button" href="{NOTE_EDITOR_URL}" target="_blank" rel="noopener">noteの新規投稿画面を開く</a>
      <a class="button" href="{PRODUCT_URL}" target="_blank" rel="noopener">販売ページを確認</a>
    </div>
    <p class="status" id="status" role="status" aria-live="polite"></p>
  </section>

  <section class="card">
    <strong>公開前に確認する公式情報</strong>
    <ul>{source_links}</ul>
    <p class="small">最終公開はnoteアカウント本人の操作です。認証情報、Cookie、決済情報は使用・保存しません。費用は0円です。</p>
  </section>
</main>
<script id="article-data" type="application/json">{payload}</script>
<script>
(() => {{
  'use strict';
  const data = JSON.parse(document.getElementById('article-data').textContent);
  const title = document.getElementById('title');
  const body = document.getElementById('body');
  const status = document.getElementById('status');
  body.value = data.body;

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

  document.getElementById('copyAll').addEventListener('click', () => run(`${{title.value.trim()}}\n\n${{body.value.trim()}}`, 'タイトルと本文をコピーしました。'));
  document.getElementById('copyTitle').addEventListener('click', () => run(title.value.trim(), 'タイトルをコピーしました。'));
  document.getElementById('copyBody').addEventListener('click', () => run(body.value.trim(), '本文をコピーしました。'));
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
        "title": title,
        "title_chars": len(title),
        "body_chars": len(body),
        "sources": len(SOURCE_URLS),
        "product_cta": PRODUCT_URL,
        "output": str(OUTPUT.relative_to(ROOT)),
        "sha256": digest,
        "cost_yen": 0,
        "credentials_used": False,
        "residual_user_action": "paste into note editor and confirm final publication",
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
