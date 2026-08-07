#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE_PATH = ROOT / "content/note/funnel_structure_2026/title.txt"
BODY_PATH = ROOT / "content/note/funnel_structure_2026/body.md"
OUTPUT = ROOT / "dist/structure_funnel_launcher.html"
REPORT = ROOT / "reports/structure_funnel.json"
PRODUCT_URL = "https://note.com/mobile_ai_studio/n/n779329665155"
TRACKED_CTA = (
    PRODUCT_URL
    + "?utm_source=note&utm_medium=organic"
    + "&utm_campaign=structure_funnel_20260807&utm_content=article_cta"
)
NOTE_EDITOR_URL = "https://note.com/new"
REQUIRED_HEADINGS = [
    "## 構成1：見えない仕組みを可視化する",
    "## 構成2：「なぜ別案ではない？」から始める",
    "## 構成3：条件を一つだけ変える",
    "## 構成4：二択実験にする",
    "## 公開前の重複チェック",
]


def main() -> int:
    title = TITLE_PATH.read_text(encoding="utf-8").strip()
    body = BODY_PATH.read_text(encoding="utf-8").strip()
    errors: list[str] = []
    if not 20 <= len(title) <= 100:
        errors.append("title_length_out_of_range")
    if len(body) < 3000:
        errors.append("body_too_short")
    if TRACKED_CTA not in body:
        errors.append("tracked_product_cta_missing")
    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            errors.append(f"required_heading_missing:{heading}")
    for placeholder in ("TODO", "[要確認]", "ここにURL"):
        if placeholder in title or placeholder in body:
            errors.append(f"placeholder_found:{placeholder}")
    if "保証するものではありません" not in body:
        errors.append("no_guarantee_disclosure_missing")

    payload = json.dumps({"title": title, "body": body}, ensure_ascii=False).replace("</", "<\\/")
    document = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="color-scheme" content="light dark">
  <title>構成テンプレ無料記事ランチャー</title>
  <style>
    :root{{font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Yu Gothic",sans-serif}}
    *{{box-sizing:border-box}}body{{margin:0;background:Canvas;color:CanvasText}}
    main{{max-width:760px;margin:auto;padding:max(20px,env(safe-area-inset-top)) 16px max(28px,env(safe-area-inset-bottom))}}
    h1{{font-size:1.4rem;line-height:1.4}}.lead,.small{{line-height:1.7;opacity:.78}}
    .card{{border:1px solid color-mix(in srgb,CanvasText 18%,transparent);border-radius:16px;padding:16px;margin:14px 0}}
    label{{display:block;font-weight:750;margin:12px 0 7px}}input,textarea,button,a.button{{width:100%;font:inherit;border-radius:12px}}
    input,textarea{{border:1px solid color-mix(in srgb,CanvasText 22%,transparent);background:Canvas;color:CanvasText;padding:12px}}
    textarea{{min-height:420px;line-height:1.65;resize:vertical}}.actions{{display:grid;gap:10px;margin-top:14px}}
    button,a.button{{border:0;padding:14px 16px;font-weight:750;text-align:center;text-decoration:none;cursor:pointer}}
    button.primary{{background:#111;color:#fff}}button.secondary,a.button{{background:color-mix(in srgb,CanvasText 10%,Canvas);color:CanvasText}}
    .status{{min-height:1.5em;font-weight:700}}
  </style>
</head>
<body><main>
  <h1>構成テンプレ無料記事ランチャー</h1>
  <p class="lead">4つの実用構成を無料公開し、12構成・100企画の制作キットへ送客する検索導線です。タイトル、本文、UTM付きCTAは入力済みです。</p>
  <section class="card">
    <label for="title">タイトル</label><input id="title" value="{html.escape(title, quote=True)}">
    <label for="body">本文</label><textarea id="body"></textarea>
    <div class="actions">
      <button class="primary" id="copyAll" type="button">タイトルと本文をまとめてコピー</button>
      <button class="secondary" id="copyTitle" type="button">タイトルだけコピー</button>
      <button class="secondary" id="copyBody" type="button">本文だけコピー</button>
      <a class="button" href="{NOTE_EDITOR_URL}" target="_blank" rel="noopener">noteの新規投稿画面を開く</a>
      <a class="button" href="{PRODUCT_URL}" target="_blank" rel="noopener">販売ページを確認</a>
    </div>
    <p class="status" id="status" role="status" aria-live="polite"></p>
  </section>
  <section class="card"><strong>公開前の確認</strong><p class="small">本文に4構成、重複チェック、UTM付き商品CTA、非保証表示を含めています。最終公開だけはnoteアカウント本人が確認します。認証情報は保存しません。費用は0円です。</p></section>
</main>
<script id="article-data" type="application/json">{payload}</script>
<script>(()=>{{'use strict';const data=JSON.parse(document.getElementById('article-data').textContent);const title=document.getElementById('title');const body=document.getElementById('body');const status=document.getElementById('status');body.value=data.body;async function copyText(text){{if(navigator.clipboard&&window.isSecureContext){{await navigator.clipboard.writeText(text);return}}const temp=document.createElement('textarea');temp.value=text;temp.setAttribute('readonly','');temp.style.position='fixed';temp.style.opacity='0';document.body.appendChild(temp);temp.select();const ok=document.execCommand('copy');temp.remove();if(!ok)throw new Error('copy failed')}}async function run(text,message){{try{{await copyText(text);status.textContent=message}}catch{{status.textContent='自動コピーに失敗しました。入力欄を長押ししてコピーしてください。'}}}}document.getElementById('copyAll').addEventListener('click',()=>run(`${{title.value.trim()}}\n\n${{body.value.trim()}}`,'タイトルと本文をコピーしました。'));document.getElementById('copyTitle').addEventListener('click',()=>run(title.value.trim(),'タイトルをコピーしました。'));document.getElementById('copyBody').addEventListener('click',()=>run(body.value.trim(),'本文をコピーしました。'));}})();</script>
</body></html>
"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(document, encoding="utf-8")
    report = {
        "ok": not errors,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "title_chars": len(title),
        "body_chars": len(body),
        "free_formats": 4,
        "paid_formats": 12,
        "tracked_campaign": "structure_funnel_20260807",
        "output": str(OUTPUT.relative_to(ROOT)),
        "sha256": hashlib.sha256(document.encode("utf-8")).hexdigest(),
        "credentials_used": False,
        "cost_yen": 0,
        "residual_user_action": "paste into note editor and confirm final publication",
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
