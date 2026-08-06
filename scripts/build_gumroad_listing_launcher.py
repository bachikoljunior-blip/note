#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import math
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE_PATH = ROOT / "content" / "gumroad" / "title.txt"
DESCRIPTION_PATH = ROOT / "content" / "gumroad" / "description.md"
TAGS_PATH = ROOT / "content" / "gumroad" / "tags.txt"
STATE_PATH = ROOT / "state" / "gumroad_listing.json"
OUTPUT = ROOT / "dist" / "gumroad_listing_launcher.html"
REPORT = ROOT / "reports" / "gumroad_listing.json"
VISUAL_LAUNCHER = ROOT / "dist" / "gumroad_visual_pack.html"
GUMROAD_NEW_PRODUCT = "https://app.gumroad.com/products/new"
PRICE_USD = 12.0
PLATFORM_RATE = 0.10
PLATFORM_FIXED = 0.50
CARD_RATE = 0.029
CARD_FIXED = 0.30
DISCOVER_RATE = 0.30
OFFICIAL_SOURCES = [
    "https://gumroad.com/help/article/66-gumroads-fees.html",
    "https://gumroad.com/help/article/289-file-size-limits-on-gumroad.html",
    "https://gumroad.com/help/article/149-adding-a-product",
    "https://gumroad.com/help/article/60-adding-a-cover-image",
    "https://gumroad.com/terms",
    "https://gumroad.com/prohibited",
]


def main() -> int:
    title = TITLE_PATH.read_text(encoding="utf-8").strip()
    description = DESCRIPTION_PATH.read_text(encoding="utf-8").strip()
    tags = [line.strip() for line in TAGS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    product = state["product"]
    product_path = ROOT / product["output"]
    errors: list[str] = []

    if not 20 <= len(title) <= 100:
        errors.append("title_length_out_of_range")
    if len(description) < 1500:
        errors.append("description_too_short")
    if not 5 <= len(tags) <= 10 or len(tags) != len(set(tags)):
        errors.append("invalid_tags")
    for phrase in ("does not guarantee views", "Redistribution", "digital download", "primary or near-primary sources"):
        if phrase.lower() not in description.lower():
            errors.append(f"required_wording_missing:{phrase}")
    for placeholder in ("TODO", "[confirm]", "insert here"):
        if placeholder.lower() in (title + description).lower():
            errors.append(f"placeholder_found:{placeholder}")

    actual_bytes = product_path.stat().st_size if product_path.is_file() else -1
    actual_sha = hashlib.sha256(product_path.read_bytes()).hexdigest() if product_path.is_file() else ""
    member_count = 0
    if not product_path.is_file():
        errors.append("english_product_missing")
    else:
        with zipfile.ZipFile(product_path) as archive:
            member_count = len(archive.namelist())
            if archive.testzip() is not None:
                errors.append("english_product_corrupt")
    if actual_bytes != product["bytes"]:
        errors.append("product_size_mismatch")
    if actual_sha != product["sha256"]:
        errors.append("product_sha_mismatch")
    if member_count != product["zip_members"]:
        errors.append("product_member_count_mismatch")
    if not VISUAL_LAUNCHER.is_file():
        errors.append("gumroad_visual_launcher_missing")

    direct_fee = PRICE_USD * PLATFORM_RATE + PLATFORM_FIXED + PRICE_USD * CARD_RATE + CARD_FIXED
    direct_net = PRICE_USD - direct_fee
    discover_net = PRICE_USD * (1 - DISCOVER_RATE)
    payload = json.dumps({
        "title": title,
        "description": description,
        "tags": tags,
        "price": PRICE_USD,
        "product": product["output"],
        "directNet": round(direct_net, 3),
        "discoverNet": round(discover_net, 2),
    }, ensure_ascii=False).replace("</", "<\\/")
    source_links = "".join(f'<li><a href="{html.escape(url)}" target="_blank" rel="noopener">Official source</a></li>' for url in OFFICIAL_SOURCES)

    document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>Gumroad listing launcher</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:0}}main{{max-width:760px;margin:auto;padding:20px}}section{{border:1px solid #8885;border-radius:16px;padding:16px;margin:14px 0}}input,textarea,button,a{{box-sizing:border-box;width:100%;padding:13px;margin:6px 0;border-radius:11px;font:inherit}}textarea{{min-height:280px}}button,a{{display:block;text-align:center;font-weight:700;text-decoration:none}}small{{line-height:1.55}}</style></head><body><main>
<h1>Gumroad English listing launcher</h1><p>Listing copy, pricing estimates, ZIP validation, and official-source checks are prepared. Authentication, payout settings, upload, and final publication remain with the seller.</p>
<section><strong>Price: ${PRICE_USD:.2f}</strong><p>Estimated direct-sale remainder: ${direct_net:.3f}<br>Estimated Discover remainder: ${discover_net:.2f}<br>Upload: <code>{html.escape(product["output"])}</code></p><small>Estimates exclude tax, refunds, payout differences, PayPal differences, and currency conversion.</small></section>
<section><strong>Product images</strong><p>Three landscape covers and one square thumbnail are generated and validated for this listing.</p><a href="gumroad_visual_pack.html">Open image preview and download pack</a></section>
<section><label>Title</label><input id="title"><label>Description</label><textarea id="description"></textarea><label>Tags</label><textarea id="tags" style="min-height:160px"></textarea><button id="copy">Copy all listing data</button><a href="{GUMROAD_NEW_PRODUCT}" target="_blank" rel="noopener">Open Gumroad new product</a><p id="status"></p></section>
<section><strong>Official sources checked</strong><ul>{source_links}</ul></section>
<script id="data" type="application/json">{payload}</script><script>(()=>{{const d=JSON.parse(document.getElementById('data').textContent),t=document.getElementById('title'),x=document.getElementById('description'),g=document.getElementById('tags'),s=document.getElementById('status');t.value=d.title;x.value=d.description;g.value=d.tags.join('\\n');document.getElementById('copy').onclick=async()=>{{const v=`Title\n${{t.value}}\n\nPrice\nUSD ${{d.price}}\n\nDescription\n${{x.value}}\n\nTags\n${{g.value}}\n\nZIP\n${{d.product}}`;try{{await navigator.clipboard.writeText(v);s.textContent='Copied.'}}catch{{s.textContent='Copy failed. Long-press the fields.'}}}}}})();</script>
</main></body></html>'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(document, encoding="utf-8")
    report = {
        "ok": not errors,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "channel": "Gumroad",
        "title_chars": len(title),
        "description_chars": len(description),
        "tag_count": len(tags),
        "price_usd": PRICE_USD,
        "estimated_direct_net_usd": round(direct_net, 3),
        "estimated_discover_net_usd": round(discover_net, 2),
        "product_bytes": actual_bytes,
        "product_sha256": actual_sha,
        "product_zip_members": member_count,
        "official_sources": OFFICIAL_SOURCES,
        "output": str(OUTPUT.relative_to(ROOT)),
        "visual_launcher": str(VISUAL_LAUNCHER.relative_to(ROOT)),
        "visual_launcher_present": VISUAL_LAUNCHER.is_file(),
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
