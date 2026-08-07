#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "gumroad_distribution.json"
CURRENT_STATE = ROOT / "state" / "current.json"
LISTING_DESCRIPTION = ROOT / "content" / "gumroad" / "description.md"
OUT_HTML = ROOT / "dist" / "gumroad_distribution_launcher.html"
OUT_JSON = ROOT / "dist" / "gumroad_distribution_pack.json"
OUT_MD = ROOT / "dist" / "gumroad_distribution_pack.md"
REPORT = ROOT / "reports" / "gumroad_distribution_pack.json"

UTM_KEYS = ("utm_source", "utm_medium", "utm_campaign", "utm_content")
ALLOWED_ACTIONS = {"prefill", "web_share"}
ID_PATTERN = re.compile(r"^[a-z0-9_]+$")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def expand(template: str, facts: dict[str, object]) -> str:
    values = {
        "topics": int(facts["topics"]),
        "formats": int(facts["formats"]),
        "prompts": int(facts["prompts"]),
        "price": f"{float(facts['price_usd']):g}",
    }
    return template.format_map(values)


def tracked_url(base: str, source: str, medium: str, campaign: str, content: str) -> str:
    parsed = urllib.parse.urlsplit(base)
    query = [(key, value) for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True) if key not in UTM_KEYS]
    query.extend([
        ("utm_source", source),
        ("utm_medium", medium),
        ("utm_campaign", campaign),
        ("utm_content", content),
    ])
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), parsed.fragment))


def valid_runtime_url(raw: object, runtime: dict[str, object]) -> bool:
    if not isinstance(raw, str) or re.search(r"\s|TODO|\[|\]", raw, re.IGNORECASE):
        return False
    try:
        parsed = urllib.parse.urlsplit(raw.strip())
        host = (parsed.hostname or "").lower()
        allowed = any(host == suffix or host.endswith(f".{suffix}") for suffix in runtime["allowed_host_suffixes"])
        path_parts = [part for part in parsed.path.split("/") if part]
        valid_product_path = len(path_parts) == 2 and path_parts[0] == "l" and bool(path_parts[1])
        return (
            parsed.scheme == "https"
            and allowed
            and host not in runtime.get("blocked_hosts", [])
            and parsed.username is None
            and parsed.password is None
            and parsed.port is None
            and parsed.path.startswith(str(runtime["required_path_prefix"]))
            and valid_product_path
        )
    except (TypeError, ValueError):
        return False


def build_rows(cfg: dict[str, object]) -> list[dict[str, object]]:
    facts = cfg["product"]["facts"]
    rows: list[dict[str, object]] = []
    for target in cfg["targets"]:
        for variant in cfg["variants"]:
            text_key = "short_text_template" if target["text_mode"] == "short" else "long_text_template"
            rows.append({
                "target_id": target["id"],
                "target_label": target["label"],
                "variant_id": variant["id"],
                "variant_label": variant["label"],
                "text_mode": target["text_mode"],
                "text": expand(variant[text_key], facts),
                "utm_source": target["utm_source"],
                "utm_medium": target["utm_medium"],
                "utm_campaign": cfg["campaign"]["utm_campaign"],
                "utm_content": variant["id"],
                "action": target["action"],
                "prefill_template": target.get("prefill"),
                "runtime_product_url_required": cfg["product"].get("canonical_url") is None,
            })
    return rows


def build_markdown(cfg: dict[str, object], rows: list[dict[str, object]]) -> str:
    url_note = (
        "The public Gumroad product URL is intentionally supplied at runtime. The launcher adds target- and angle-specific UTM parameters after validating and saving the URL on the device."
        if cfg["product"].get("canonical_url") is None
        else "The validated public Gumroad product URL is embedded in the launcher. Target- and angle-specific UTM parameters are added only when sharing."
    )
    lines = [
        "# Gumroad English distribution pack",
        "",
        url_note,
        "",
        "No item below is proof that a post was published. Final publication remains with the authenticated account owner.",
        "",
    ]
    for row in rows:
        lines.extend([
            f"## {row['target_label']} / {row['variant_label']}",
            "",
            str(row["text"]),
            "",
            f"Tracking: utm_source={row['utm_source']}; utm_medium={row['utm_medium']}; utm_campaign={row['utm_campaign']}; utm_content={row['utm_content']}",
            f"Action: {row['action']}",
            "",
        ])
    lines.extend([
        "## Safety boundary",
        "",
        "- Email is only for recipients who reasonably expect the message; no cold or bulk email.",
        "- The share sheet does not claim which app was selected, so its source remains `share_sheet`.",
        "- Reddit is excluded from automatic targets because community promotion rules require context-specific review and repeated unsolicited promotion is prohibited.",
        "- The launcher records attempts only, never publication success.",
        "",
    ])
    return "\n".join(lines)


def build_launcher(cfg: dict[str, object]) -> str:
    facts = cfg["product"]["facts"]
    payload = {
        "title": cfg["product"]["title"],
        "canonicalUrl": cfg["product"].get("canonical_url"),
        "runtimeUrl": cfg["runtime_url"],
        "defaultVariant": cfg["default_variant"],
        "defaultTarget": cfg["default_target"],
        "variants": [
            {
                "id": item["id"],
                "label": item["label"],
                "shortText": expand(item["short_text_template"], facts),
                "longText": expand(item["long_text_template"], facts),
            }
            for item in cfg["variants"]
        ],
        "targets": cfg["targets"],
        "campaign": cfg["campaign"],
        "safeguards": cfg["safeguards"],
    }
    embedded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return rf'''<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="color-scheme" content="light dark">
  <title>Gumroad英語版 配布ランチャー</title>
  <style>
    :root {{ font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Yu Gothic",sans-serif; }}
    * {{ box-sizing:border-box; }} body {{ margin:0;background:Canvas;color:CanvasText; }}
    main {{ max-width:760px;margin:auto;padding:max(20px,env(safe-area-inset-top)) 16px max(30px,env(safe-area-inset-bottom)); }}
    h1 {{ font-size:1.45rem;margin:0 0 8px; }} .lead,.small {{ line-height:1.65;opacity:.78; }}
    .card {{ border:1px solid color-mix(in srgb,CanvasText 18%,transparent);border-radius:17px;padding:16px;margin:14px 0; }}
    label {{ display:block;font-weight:750;margin:10px 0 7px; }} input,select,textarea,button,a.button {{ width:100%;font:inherit;border-radius:12px; }}
    input,select,textarea {{ padding:12px;border:1px solid color-mix(in srgb,CanvasText 24%,transparent);background:Canvas;color:CanvasText; }}
    textarea {{ min-height:260px;line-height:1.55;resize:vertical; }} textarea.share-output {{ min-height:150px; }} .actions {{ display:grid;gap:10px;margin-top:12px; }}
    button,a.button {{ border:0;padding:14px;text-align:center;text-decoration:none;font-weight:760;cursor:pointer; }}
    button.primary {{ background:#111;color:#fff; }} button.secondary,a.button {{ background:color-mix(in srgb,CanvasText 10%,Canvas);color:CanvasText; }}
    button:disabled,a.disabled {{ opacity:.45;pointer-events:none; }} .status {{ min-height:1.5em;line-height:1.5;font-weight:650; }}
    .warning {{ color:#b44b00; }} code {{ overflow-wrap:anywhere; }} ul {{ line-height:1.65;padding-left:1.3rem; }}
  </style>
</head>
<body><main>
  <h1>Gumroad英語版 配布ランチャー</h1>
  <p class="lead">公開後のGumroad URLを最初に1回だけ保存すると、英語告知文、媒体別UTM、事前入力または共有シート、操作記録を生成します。自動投稿はせず、最終公開は本人が確認します。</p>

  <section class="card">
    <label for="productUrl">公開済みGumroad商品URL</label>
    <input id="productUrl" inputmode="url" autocapitalize="none" autocomplete="url" placeholder="https://creator.gumroad.com/l/product">
    <div class="actions">
      <button class="primary" id="saveUrl" type="button">URLを検証して端末に保存</button>
      <button class="secondary" id="copySetupLink" type="button">URL設定済みランチャーリンクをコピー</button>
    </div>
    <p class="small">HTTPSのgumroad.comまたはサブドメイン上にある公開商品URLだけを受け付けます。URLは認証情報ではなく、保存できない環境ではこの画面内だけで保持します。</p>
  </section>

  <section class="card">
    <label for="target">共有経路</label><select id="target"></select>
    <label for="variant">訴求</label><select id="variant"></select>
    <label for="message">英語告知文（編集可）</label><textarea id="message"></textarea>
    <p class="small" id="tracking"></p>
    <label for="shareText">共有用全文（コピー失敗時はここを長押し）</label><textarea class="share-output" id="shareText" readonly></textarea>
    <div class="actions">
      <button class="primary" id="share" type="button">共有先を開く</button>
      <button class="secondary" id="copy" type="button">告知文と計測URLをコピー</button>
      <a class="button disabled" id="openProduct" target="_blank" rel="noopener">商品ページを確認</a>
      <button class="secondary" id="copyLog" type="button">共有試行の記録をコピー</button>
    </div>
    <p class="status" id="status" role="status" aria-live="polite"></p>
    <p class="small" id="lastAttempt"></p>
  </section>

  <section class="card">
    <strong>安全境界</strong>
    <ul>
      <li>メールは受信を合理的に期待する相手だけ。コールドDMや一括メールは行いません。</li>
      <li>共有シートで選んだアプリは取得できないため、計測元は正直に <code>share_sheet</code> とします。</li>
      <li>Redditはコミュニティ規則の個別確認なしに自動化しません。</li>
      <li>共有のキャンセルや試行を公開成功として記録しません。</li>
    </ul>
  </section>
</main>
<script id="distribution-data" type="application/json">{embedded}</script>
<script>
(() => {{
  'use strict';
  const data = JSON.parse(document.getElementById('distribution-data').textContent);
  const productUrl = document.getElementById('productUrl');
  const targetSelect = document.getElementById('target');
  const variantSelect = document.getElementById('variant');
  const message = document.getElementById('message');
  const status = document.getElementById('status');
  const tracking = document.getElementById('tracking');
  const shareText = document.getElementById('shareText');
  const shareButton = document.getElementById('share');
  const copyButton = document.getElementById('copy');
  const openProduct = document.getElementById('openProduct');
  const lastAttempt = document.getElementById('lastAttempt');
  let sessionUrl = '';
  let renderedMessage = '';
  let duplicateOverride = false;
  const memoryStore = {{}};

  function safeGet(key) {{ try {{ return memoryStore[key] || localStorage.getItem(key) || ''; }} catch {{ return memoryStore[key] || ''; }} }}
  function safeSet(key, value) {{ memoryStore[key] = value; try {{ localStorage.setItem(key, value); return true; }} catch {{ return false; }} }}
  function show(text, warning = false) {{ status.textContent = text; status.className = warning ? 'status warning' : 'status'; }}
  function validUrl(raw) {{
    try {{
      const value = new URL(raw.trim());
      const host = value.hostname.toLowerCase();
      const allowed = data.runtimeUrl.allowed_host_suffixes.some(suffix => host === suffix || host.endsWith(`.${{suffix}}`));
      const pathParts = value.pathname.split('/').filter(Boolean);
      const publicProductPath = value.pathname.startsWith(data.runtimeUrl.required_path_prefix) && pathParts.length === 2 && pathParts[0] === 'l' && pathParts[1];
      const blocked = /\s|T(?:O)DO|\[|\]/i.test(raw) || value.username || value.password || value.port || data.runtimeUrl.blocked_hosts.includes(host);
      return value.protocol === 'https:' && allowed && publicProductPath && !blocked ? value.href : '';
    }} catch {{ return ''; }}
  }}
  function resolvedUrl() {{ return validUrl(data.canonicalUrl || '') || validUrl(productUrl.value) || validUrl(sessionUrl); }}
  function selectedTarget() {{ return data.targets.find(item => item.id === targetSelect.value) || data.targets[0]; }}
  function selectedVariant() {{ return data.variants.find(item => item.id === variantSelect.value) || data.variants[0]; }}
  function contentId() {{ return message.value.trim() === renderedMessage ? selectedVariant().id : `${{selectedVariant().id}}_edited`; }}
  function trackedUrl() {{
    const base = resolvedUrl(); if (!base) return '';
    const value = new URL(base);
    for (const key of ['utm_source','utm_medium','utm_campaign','utm_content']) value.searchParams.delete(key);
    value.searchParams.append('utm_source', selectedTarget().utm_source);
    value.searchParams.append('utm_medium', selectedTarget().utm_medium);
    value.searchParams.append('utm_campaign', data.campaign.utm_campaign);
    value.searchParams.append('utm_content', contentId());
    return value.href;
  }}
  function fullText() {{ return `${{message.value.trim()}}\n\n${{trackedUrl()}}`; }}
  function fill(template) {{
    const values = {{
      title: encodeURIComponent(data.title), text: encodeURIComponent(message.value.trim()),
      url: encodeURIComponent(trackedUrl()), text_with_url: encodeURIComponent(fullText())
    }};
    return template.replace(/\{{(title|text|url|text_with_url)\}}/g, (_, key) => values[key]);
  }}
  async function copyText(value) {{
    if (navigator.clipboard && window.isSecureContext) {{ await navigator.clipboard.writeText(value); return; }}
    const temp = document.createElement('textarea'); temp.value = value; temp.setAttribute('readonly','');
    temp.style.position = 'fixed'; temp.style.opacity = '0'; document.body.appendChild(temp); temp.select();
    const copied = document.execCommand('copy'); temp.remove(); if (!copied) throw new Error('copy failed');
  }}
  function attemptHistory() {{
    const raw = safeGet(data.runtimeUrl.attempt_storage_key);
    try {{ const value = JSON.parse(raw); return Array.isArray(value) ? value.filter(item => item && item.at) : value && value.at ? [value] : []; }}
    catch {{ return []; }}
  }}
  function renderAttempt() {{
    const history = attemptHistory(), item = history[history.length - 1];
    lastAttempt.textContent = item ? `直近の共有試行: ${{new Date(item.at).toLocaleString('ja-JP')}} / ${{item.target}} / ${{item.variant}}（公開成功の記録ではありません）` : '共有試行はまだ記録されていません。';
  }}
  function isDuplicate() {{
    return attemptHistory().some(item => {{
      const hours = (Date.now() - Date.parse(item.at)) / 3600000;
      return item.target === selectedTarget().id && item.variant === contentId() && hours >= 0 && hours < data.safeguards.duplicate_warning_hours;
    }});
  }}
  function recordAttempt() {{
    const item = {{ at:new Date().toISOString(),target:selectedTarget().id,variant:contentId(),tracked_url:trackedUrl() }};
    const cutoff = Date.now() - 7 * 86400000;
    const history = attemptHistory().filter(prior => Date.parse(prior.at) >= cutoff).concat(item).slice(-50);
    safeSet(data.runtimeUrl.attempt_storage_key, JSON.stringify(history)); renderAttempt(); return item;
  }}
  function renderMessage() {{
    const variant = selectedVariant(), target = selectedTarget();
    renderedMessage = target.text_mode === 'short' ? variant.shortText : variant.longText;
    message.value = renderedMessage; duplicateOverride = false; render();
  }}
  function render() {{
    const url = resolvedUrl(), target = selectedTarget();
    const composedLength = url ? message.value.trim().length + 2 + trackedUrl().length : 0;
    const blueskyTooLong = target.id === 'bluesky' && composedLength > data.campaign.bluesky_max_graphemes;
    shareButton.disabled = !url || blueskyTooLong; copyButton.disabled = !url;
    openProduct.href = url || '#'; openProduct.className = url ? 'button' : 'button disabled';
    shareText.value = url ? fullText() : `${{message.value.trim()}}\n\n[公開Gumroad商品URLを保存すると計測URLが入ります]`;
    tracking.textContent = !url ? '公開URLを保存するとUTM付きリンクを生成します。' : blueskyTooLong ? `Bluesky上限を超えるため共有を停止しました（本文＋URL: ${{composedLength}} / ${{data.campaign.bluesky_max_graphemes}}）。本文を短くしてください。` : `UTM: ${{target.utm_source}} / ${{target.utm_medium}} / ${{data.campaign.utm_campaign}} / ${{contentId()}}${{target.id === 'bluesky' ? ` / 本文＋URL: ${{composedLength}}` : ''}}`;
  }}
  for (const item of data.targets) {{ const option=document.createElement('option');option.value=item.id;option.textContent=item.label;targetSelect.appendChild(option); }}
  for (const item of data.variants) {{ const option=document.createElement('option');option.value=item.id;option.textContent=item.label;variantSelect.appendChild(option); }}
  targetSelect.value=data.defaultTarget; variantSelect.value=data.defaultVariant;
  const queryValue = new URL(window.location.href).searchParams.get(data.runtimeUrl.query_parameter) || '';
  sessionUrl = validUrl(data.canonicalUrl || '') || validUrl(queryValue) || validUrl(safeGet(data.runtimeUrl.storage_key));
  productUrl.value=sessionUrl; renderMessage(); renderAttempt();
  targetSelect.addEventListener('change',renderMessage); variantSelect.addEventListener('change',renderMessage);
  message.addEventListener('input',render); productUrl.addEventListener('input',render);
  document.getElementById('saveUrl').addEventListener('click',() => {{
    const value=validUrl(productUrl.value); if (!value) {{ show('公開済みGumroad商品URLを確認してください。',true); return; }}
    sessionUrl=value; productUrl.value=value; const persisted=safeSet(data.runtimeUrl.storage_key,value); render();
    show(persisted ? 'URLを検証し、端末に保存しました。' : 'URLは有効です。この画面内で保持します。保存できないため設定済みリンクも利用できます。',!persisted);
  }});
  document.getElementById('copySetupLink').addEventListener('click',async() => {{
    const value=validUrl(productUrl.value); if (!value) {{ show('先に有効な商品URLを入力してください。',true); return; }}
    const link=new URL(window.location.href); link.searchParams.set(data.runtimeUrl.query_parameter,value);
    try {{ await copyText(link.href); show('URL設定済みランチャーリンクをコピーしました。'); }} catch {{ show(link.href,true); }}
  }});
  copyButton.addEventListener('click',async() => {{
    try {{ await copyText(shareText.value); show('英語告知文とUTM付きURLをコピーしました。'); }} catch {{ show('コピーに失敗しました。「共有用全文」欄を長押ししてコピーしてください。',true); }}
  }});
  shareButton.addEventListener('click',async() => {{
    if (!resolvedUrl()) {{ show('先に公開商品URLを保存してください。',true); return; }}
    if (isDuplicate() && !duplicateOverride) {{ duplicateOverride=true; show('同じ経路・訴求を24時間以内に試行済みです。重複が意図的なら、もう一度「共有先を開く」を押してください。',true); return; }}
    const target=selectedTarget(); recordAttempt(); duplicateOverride=false;
    if (target.action === 'prefill') {{ window.location.href=fill(target.prefill); return; }}
    if (navigator.share) {{
      try {{ await navigator.share({{title:data.title,text:message.value.trim(),url:trackedUrl()}}); show('共有シートを閉じました。公開成功は接続権限なしには確認できません。'); return; }}
      catch (error) {{ if (error && error.name === 'AbortError') {{ show('共有をキャンセルしました。試行としてのみ記録しました。',true); return; }} }}
    }}
    try {{ await copyText(shareText.value); show('共有シートを使えないため、告知文とURLをコピーしました。',true); }} catch {{ show('共有とコピーに失敗しました。「共有用全文」欄を長押ししてください。',true); }}
  }});
  document.getElementById('copyLog').addEventListener('click',async() => {{
    const history=attemptHistory(), item=history[history.length - 1];
    if (!item) {{ show('共有試行がまだないため、記録は作成しません。',true); return; }}
    const log=`Share attempt only (not publication proof)\n${{JSON.stringify(item)}}\nTracked URL: ${{item.tracked_url || '[not recorded by legacy version]'}}`;
    try {{ await copyText(log); show('共有試行の記録をコピーしました。'); }} catch {{ show(log,true); }}
  }});
}})();
</script></body></html>'''


def validate(cfg: dict[str, object], rows: list[dict[str, object]], launcher: str, markdown: str) -> list[str]:
    errors: list[str] = []
    variants = cfg.get("variants", [])
    targets = cfg.get("targets", [])
    variant_ids = [item.get("id") for item in variants]
    target_ids = [item.get("id") for item in targets]
    if len(variant_ids) != len(set(variant_ids)) or any(not ID_PATTERN.fullmatch(str(item)) for item in variant_ids):
        errors.append("invalid_or_duplicate_variant_ids")
    if len(target_ids) != len(set(target_ids)) or any(not ID_PATTERN.fullmatch(str(item)) for item in target_ids):
        errors.append("invalid_or_duplicate_target_ids")
    if cfg.get("default_variant") not in variant_ids:
        errors.append("default_variant_missing")
    if cfg.get("default_target") not in target_ids:
        errors.append("default_target_missing")
    if len(rows) != len(variants) * len(targets):
        errors.append("combination_count_mismatch")
    runtime = cfg["runtime_url"]
    canonical_url = cfg["product"].get("canonical_url")
    if canonical_url is None and runtime.get("required_when_canonical_missing") is not True:
        errors.append("missing_runtime_url_requirement")
    if canonical_url is not None and not valid_runtime_url(canonical_url, runtime):
        errors.append("invalid_canonical_product_url")

    short_limit = int(cfg["campaign"]["short_text_max_chars"])
    max_url = int(cfg["campaign"]["max_runtime_url_chars"])
    bluesky_limit = int(cfg["campaign"]["bluesky_max_graphemes"])
    facts = cfg["product"]["facts"]
    all_copy: list[str] = []
    for variant in variants:
        short_text = expand(variant["short_text_template"], facts)
        long_text = expand(variant["long_text_template"], facts)
        all_copy.extend([short_text, long_text])
        if len(short_text) > short_limit:
            errors.append(f"short_copy_too_long:{variant['id']}:{len(short_text)}")
        if len(short_text) + 2 + max_url > bluesky_limit:
            errors.append(f"bluesky_runtime_budget_exceeded:{variant['id']}")
        conversion_markers = (
            f"${float(facts['price_usd']):g}",
            f"{int(facts['topics'])} research prompts",
            f"{int(facts['formats'])} story formats",
            "Explore",
        )
        for marker in conversion_markers:
            if marker not in short_text:
                errors.append(f"short_copy_conversion_marker_missing:{variant['id']}:{marker}")
        if short_text == long_text:
            errors.append(f"duplicate_short_and_long_copy:{variant['id']}")

    joined_copy = "\n".join(all_copy).lower()
    for phrase in cfg["safeguards"]["forbidden_claims"]:
        if str(phrase).lower() in joined_copy:
            errors.append(f"forbidden_claim:{phrase}")
    for marker in (str(facts["topics"]), str(facts["formats"]), "source", "no view or revenue guarantees"):
        if marker.lower() not in joined_copy:
            errors.append(f"required_copy_fact_missing:{marker}")
    if any("http" in str(item["short_text_template"]).lower() or "http" in str(item["long_text_template"]).lower() for item in variants):
        errors.append("hardcoded_url_in_copy")

    sources = {target["utm_source"] for target in targets}
    if len(sources) != len(targets):
        errors.append("duplicate_utm_source")
    for target in targets:
        if target.get("action") not in ALLOWED_ACTIONS:
            errors.append(f"unsupported_action:{target.get('id')}")
        if target.get("text_mode") not in {"short", "long"}:
            errors.append(f"unsupported_text_mode:{target.get('id')}")
        template = target.get("prefill")
        if target.get("action") == "prefill" and not template:
            errors.append(f"missing_prefill:{target.get('id')}")
        if template and set(re.findall(r"\{([^{}]+)\}", template)) - {"title", "text", "url", "text_with_url"}:
            errors.append(f"invalid_prefill_token:{target.get('id')}")

    synthetic = "https://creator.gumroad.com/l/test?ref=ci&utm_source=old&utm_medium=old&utm_campaign=old&utm_content=old#details"
    if not valid_runtime_url(synthetic, runtime):
        errors.append("valid_synthetic_product_url_rejected")
    invalid_urls = [
        "http://creator.gumroad.com/l/test",
        "https://evilgumroad.com/l/test",
        "https://app.gumroad.com/products/test/edit",
        "https://gumroad.com/help/article/149-adding-a-product",
        "https://creator.gumroad.com/",
        "https://user:pass@creator.gumroad.com/l/test",
    ]
    for invalid in invalid_urls:
        if valid_runtime_url(invalid, runtime):
            errors.append(f"invalid_product_url_accepted:{invalid}")
    for row in rows:
        value = tracked_url(synthetic, str(row["utm_source"]), str(row["utm_medium"]), str(row["utm_campaign"]), str(row["utm_content"]))
        parsed = urllib.parse.urlsplit(value)
        query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        if query.get("ref") != ["ci"] or parsed.fragment != "details":
            errors.append(f"non_utm_or_fragment_not_preserved:{row['target_id']}:{row['variant_id']}")
        expected = {"utm_source": row["utm_source"], "utm_medium": row["utm_medium"], "utm_campaign": row["utm_campaign"], "utm_content": row["utm_content"]}
        for key, expected_value in expected.items():
            if query.get(key) != [expected_value]:
                errors.append(f"utm_mismatch:{row['target_id']}:{row['variant_id']}:{key}")

    state = json.loads(CURRENT_STATE.read_text(encoding="utf-8"))
    current_facts = state["product_artifacts"]["english_product"]
    for key in ("topics", "formats", "prompts"):
        if int(facts[key]) != int(current_facts[key]):
            errors.append(f"state_fact_mismatch:{key}")
    if float(facts["price_usd"]) != float(state["sales_channels"]["gumroad"]["price_usd"]):
        errors.append("state_fact_mismatch:price_usd")
    description = LISTING_DESCRIPTION.read_text(encoding="utf-8").lower()
    for phrase in (
        "does not guarantee views",
        "100 research-ready",
        "12 format-specific hook approaches",
        "25 category-specific visual-planning patterns",
        "9 copy-ready",
    ):
        if phrase not in description:
            errors.append(f"listing_fact_missing:{phrase}")

    for name, value in (("launcher", launcher), ("markdown", markdown)):
        if "TODO" in value or "[confirm]" in value.lower():
            errors.append(f"placeholder_found:{name}")
        if "generated_at_utc" in value or "checked_at_utc" in value:
            errors.append(f"nondeterministic_timestamp_in_dist:{name}")
    for marker in ("localStorage", "memoryStore", "utm_source", "duplicate_warning_hours", "navigator.share", "attemptHistory", "recordAttempt", "tracked_url", "shareText", "composedLength", "bluesky_max_graphemes", "required_path_prefix", "rel=\"noopener\""):
        if marker not in launcher:
            errors.append(f"launcher_feature_missing:{marker}")
    if cfg["safeguards"].get("auto_publish") is not False or cfg["automation"].get("credentials_used") is not False:
        errors.append("unsafe_automation_configuration")
    if int(cfg["automation"].get("cost_yen", -1)) != 0 or int(cfg["automation"].get("external_dependencies", -1)) != 0:
        errors.append("nonzero_cost_or_dependency")
    return errors


def main() -> int:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    runtime_required = cfg["product"].get("canonical_url") is None
    rows = build_rows(cfg)
    launcher = build_launcher(cfg)
    markdown = build_markdown(cfg, rows)
    pack = json.dumps({
        "schema_version": "1.0",
        "runtime_product_url_required": runtime_required,
        "product_title": cfg["product"]["title"],
        "targets": len(cfg["targets"]),
        "variants": len(cfg["variants"]),
        "combinations": rows,
    }, ensure_ascii=False, indent=2) + "\n"
    errors = validate(cfg, rows, launcher, markdown)

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(launcher, encoding="utf-8")
    OUT_JSON.write_text(pack, encoding="utf-8")
    OUT_MD.write_text(markdown, encoding="utf-8")
    report = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "targets": len(cfg["targets"]),
        "variants": len(cfg["variants"]),
        "combinations": len(rows),
        "runtime_product_url_required": runtime_required,
        "canonical_url_embedded": not runtime_required,
        "short_text_lengths": {item["id"]: len(expand(item["short_text_template"], cfg["product"]["facts"])) for item in cfg["variants"]},
        "synthetic_tracking_cases": len(rows),
        "outputs": {
            str(OUT_HTML.relative_to(ROOT)): {"bytes": len(launcher.encode("utf-8")), "sha256": sha256_text(launcher)},
            str(OUT_JSON.relative_to(ROOT)): {"bytes": len(pack.encode("utf-8")), "sha256": sha256_text(pack)},
            str(OUT_MD.relative_to(ROOT)): {"bytes": len(markdown.encode("utf-8")), "sha256": sha256_text(markdown)},
        },
        "excluded_automatic_targets": cfg["safeguards"]["excluded_automatic_targets"],
        "external_dependencies": 0,
        "credentials_used": False,
        "cost_yen": 0,
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
