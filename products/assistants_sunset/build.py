#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
PRODUCT_DIR = Path(__file__).resolve().parent
PRODUCT_OUTPUT = ROOT / "dist/assistants-api-sunset-migration-kit-v1.zip"
IPHONE_OUTPUT = ROOT / "dist/Assistants_API_Sunset_Gumroad_iPhone_Pack_v1.zip"
REPORT = ROOT / "reports/assistants_sunset_iphone_pack.json"
PRODUCT_FILES = ["README.md", "MIGRATION.md", "LICENSE.txt", "scan.py", "codemod.py", "test_scan.py"]
PRODUCT_EPOCH = (2020, 1, 1, 0, 0, 0)
PACK_EPOCH = (2026, 8, 9, 0, 0, 0)
PERMALINK = "assistants-api-sunset-migration-kit"
TAGS = "openai, assistants api, responses api, conversations api, developer tools"
REFUND_FINE_PRINT = (
    "7-day refund period. This utility inventories source usage and previews a conservative subset of edits; "
    "it does not guarantee a production-ready migration. Review every change and run your own tests."
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def regular_file(path: Path) -> bytes:
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise SystemExit(f"missing_assistants_sunset_source:{path.relative_to(ROOT)}") from exc
    if not stat.S_ISREG(metadata.st_mode) or path.is_symlink():
        raise SystemExit(f"unsafe_assistants_sunset_source:{path.relative_to(ROOT)}")
    return path.read_bytes()


def section(markdown: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$\n+(.*?)(?=^## |\Z)", markdown, flags=re.MULTILINE | re.DOTALL)
    if not match:
        raise SystemExit(f"missing_listing_section:{heading}")
    return match.group(1).strip()


def build_product() -> bytes:
    PRODUCT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = PRODUCT_OUTPUT.with_name(f".{PRODUCT_OUTPUT.name}.{os.getpid()}.tmp")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in PRODUCT_FILES:
            data = regular_file(PRODUCT_DIR / name)
            info = zipfile.ZipInfo(name, PRODUCT_EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    os.replace(temporary, PRODUCT_OUTPUT)
    return PRODUCT_OUTPUT.read_bytes()


def cover_svg() -> bytes:
    return b'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1200 1200" role="img" aria-labelledby="title desc">
<title id="title">Assistants API Sunset Migration Kit</title><desc id="desc">Developer utility cover</desc>
<rect width="1200" height="1200" fill="#07111f"/><circle cx="1020" cy="180" r="250" fill="#13b8a6" opacity=".22"/><circle cx="150" cy="1080" r="320" fill="#4f46e5" opacity=".24"/>
<rect x="86" y="82" width="310" height="58" rx="29" fill="#13b8a6"/><text x="241" y="121" text-anchor="middle" font-family="Arial,sans-serif" font-size="27" font-weight="700" fill="#04111c">DEVELOPER UTILITY</text>
<text x="86" y="340" font-family="Arial,sans-serif" font-size="92" font-weight="800" fill="#f8fafc">Assistants API</text><text x="86" y="455" font-family="Arial,sans-serif" font-size="108" font-weight="800" fill="#f8fafc">Sunset</text><text x="86" y="570" font-family="Arial,sans-serif" font-size="108" font-weight="800" fill="#f8fafc">Migration Kit</text>
<text x="90" y="680" font-family="Arial,sans-serif" font-size="40" fill="#b9c8dc">Audit legacy usage</text><text x="90" y="742" font-family="Arial,sans-serif" font-size="40" fill="#b9c8dc">Preview conservative edits</text><text x="90" y="804" font-family="Arial,sans-serif" font-size="40" fill="#b9c8dc">Plan Responses + Conversations</text>
<rect x="86" y="920" width="1028" height="150" rx="34" fill="#101f33" stroke="#2f4865" stroke-width="3"/><text x="600" y="982" text-anchor="middle" font-family="Arial,sans-serif" font-size="32" fill="#9fb2c9">OFFLINE SCANNER + DRY-RUN CODEMOD</text><text x="600" y="1032" text-anchor="middle" font-family="Arial,sans-serif" font-size="25" fill="#13b8a6">Independent utility | Review and test every change</text>
</svg>'''


def start_here(title: str, summary: str) -> bytes:
    html = f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Assistants API移行キット iPhone出品パック</title><style>
body{{font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;max-width:760px;margin:auto;padding:18px;line-height:1.65;color:#172033;background:#f3f6fa}}section{{background:#fff;border:1px solid #d8e1ed;border-radius:16px;padding:16px;margin:14px 0}}a.button{{display:block;background:#0f766e;color:#fff;text-decoration:none;padding:13px 15px;border-radius:10px;margin:10px 0;font-weight:700}}.warn{{background:#fff0d5;color:#763b00;padding:11px;border-radius:9px}}code{{word-break:break-all}}</style></head><body>
<h1>Assistants API移行キット<br>iPhone出品パック</h1><p>外側のこのZIPだけを1回展開し、<code>START_HERE.html</code>をSafariで開きます。</p>
<section><h2>1. 商品情報</h2><p><strong>Name</strong><br>{title}</p><p><strong>Type</strong>: Digital product<br><strong>Base price</strong>: US$29<br><strong>Versions</strong>: Solo US$29 / Team US$149 / Organization US$399<br><strong>Custom permalink</strong>: {PERMALINK}<br><strong>Refund period</strong>: 7 days</p><p><strong>Summary</strong><br>{summary}</p><p>個別コピー: <a href="copy/title.txt">商品名</a> ／ <a href="copy/summary.txt">短文</a> ／ <a href="copy/description.md">説明</a> ／ <a href="copy/tags.txt">タグ</a> ／ <a href="copy/refund_fine_print.txt">返金条件</a></p></section>
<section><h2>2. 購入者向けZIP</h2><a class="button" href="Assistants_API_Sunset_Migration_Kit_v1.zip" download>商品ZIPを選ぶ／保存する</a><p class="warn">この内側の商品ZIPは展開せず、そのままGumroadのContentへアップロードします。外側のiPhone出品パックは購入者向けファイルにしません。</p></section>
<section><h2>3. カバー</h2><a class="button" href="cover/cover.svg">検証済みカバーを開く</a><p>GumroadがSVGを受け付けない場合は、Safariで全画面表示してスクリーンショットを撮り、正方形に切り抜いて使います。内容を誇張する文言は追加しません。</p></section>
<section><h2>4. Gumroadへ</h2><a class="button" href="https://gumroad.com/products/new">Gumroad新規商品画面を開く</a><p>別商品として作成し、商品ZIPのアップロード完了を確認してからcreator Test Purchaseを実行します。最終公開は本人だけが行います。パスワード、確認コード、Cookie、本人確認・税務・銀行情報はGumroad以外へ送信しません。</p></section>
</body></html>'''
    return html.encode("utf-8")


def pack_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, PACK_EPOCH)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    return info


def build_iphone_pack(product: bytes) -> bytes:
    listing = regular_file(PRODUCT_DIR / "listing.md").decode("utf-8")
    title = section(listing, "Product name")
    price = section(listing, "Price")
    summary = section(listing, "Short description")
    description = section(listing, "Description")
    if title != "Assistants API Sunset Migration Kit" or price != "Solo $29 / Team $149 / Organization $399":
        raise SystemExit("assistants_sunset_listing_contract")
    for required in ("2026-08-26", "Responses + Conversations", "independent developer utility", "not an official OpenAI product"):
        if required not in listing:
            raise SystemExit(f"assistants_sunset_listing_missing:{required}")

    entries = {
        "Assistants_API_Sunset_Migration_Kit_v1.zip": product,
        "README_iPhone.txt": (
            "Assistants API Sunset Migration Kit - Gumroad iPhone pack\n\n"
            "1. Open START_HERE.html in Safari.\n"
            "2. Create a separate tiered digital product: Solo US$29, Team US$149, Organization US$399.\n"
            "3. Keep Assistants_API_Sunset_Migration_Kit_v1.zip compressed and upload it as the only buyer download.\n"
            "4. Run creator Test Purchase and verify the inner ZIP before final publication.\n"
            "5. Enter credentials, identity, tax, payout and banking information only on Gumroad.\n"
        ).encode("utf-8"),
        "START_HERE.html": start_here(title, summary),
        "copy/title.txt": (title + "\n").encode("utf-8"),
        "copy/summary.txt": (summary + "\n").encode("utf-8"),
        "copy/description.md": (description + "\n").encode("utf-8"),
        "copy/tags.txt": (TAGS + "\n").encode("utf-8"),
        "copy/refund_fine_print.txt": (REFUND_FINE_PRINT + "\n").encode("utf-8"),
        "cover/cover.svg": cover_svg(),
    }
    manifest = {
        "schema_version": "1.0",
        "classification": "private_repository_authenticated_user_handoff",
        "product": title,
        "price_tiers_usd": {"solo": 29, "team": 149, "organization": 399},
        "permalink": PERMALINK,
        "refund_period_days": 7,
        "sunset_date": "2026-08-26",
        "product_zip_must_remain_unextracted": True,
        "creator_test_purchase_required": True,
        "final_publication": "human_only",
        "credentials_used": False,
        "cost_yen": 0,
        "files": {name: {"bytes": len(data), "sha256": sha256(data)} for name, data in sorted(entries.items())},
    }
    entries["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    IPHONE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = IPHONE_OUTPUT.with_name(f".{IPHONE_OUTPUT.name}.{os.getpid()}.tmp")
    with zipfile.ZipFile(temporary, "w", allowZip64=False) as archive:
        for name, data in sorted(entries.items()):
            archive.writestr(pack_info(name), data)
    os.replace(temporary, IPHONE_OUTPUT)
    return IPHONE_OUTPUT.read_bytes()


def verify(product: bytes, pack: bytes) -> None:
    with zipfile.ZipFile(PRODUCT_OUTPUT) as archive:
        if archive.testzip() is not None or [item.filename for item in archive.infolist()] != PRODUCT_FILES:
            raise SystemExit("assistants_sunset_product_zip_contract")
    expected = {
        "Assistants_API_Sunset_Migration_Kit_v1.zip", "README_iPhone.txt", "START_HERE.html", "manifest.json",
        "copy/title.txt", "copy/summary.txt", "copy/description.md", "copy/tags.txt", "copy/refund_fine_print.txt", "cover/cover.svg",
    }
    with zipfile.ZipFile(IPHONE_OUTPUT) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if names != sorted(expected) or set(names) != expected or archive.testzip() is not None:
            raise SystemExit(f"assistants_sunset_iphone_members:{names}")
        for info in infos:
            path = PurePosixPath(info.filename)
            mode = info.external_attr >> 16
            if path.is_absolute() or ".." in path.parts or "\\" in info.filename:
                raise SystemExit(f"assistants_sunset_iphone_unsafe_path:{info.filename}")
            if info.flag_bits & 1 or info.compress_type != zipfile.ZIP_STORED or info.date_time != PACK_EPOCH:
                raise SystemExit(f"assistants_sunset_iphone_zip_contract:{info.filename}")
            if not stat.S_ISREG(mode) or stat.S_IMODE(mode) != 0o644:
                raise SystemExit(f"assistants_sunset_iphone_mode:{info.filename}")
        manifest = json.loads(archive.read("manifest.json"))
        if manifest["price_tiers_usd"] != {"solo": 29, "team": 149, "organization": 399} or manifest["final_publication"] != "human_only" or not manifest["creator_test_purchase_required"]:
            raise SystemExit("assistants_sunset_iphone_listing_contract")
        for name in expected - {"manifest.json"}:
            data = archive.read(name)
            if manifest["files"].get(name) != {"bytes": len(data), "sha256": sha256(data)}:
                raise SystemExit(f"assistants_sunset_iphone_manifest:{name}")
        if archive.read("Assistants_API_Sunset_Migration_Kit_v1.zip") != product:
            raise SystemExit("assistants_sunset_iphone_nested_product")
        start = archive.read("START_HERE.html").decode("utf-8")
        for fragment in ("Assistants API Sunset Migration Kit", "Solo US$29", "Team US$149", "Organization US$399", "2026-08-26", "https://gumroad.com/products/new", "商品ZIPは展開せず", "creator Test Purchase", "最終公開は本人"):
            if fragment not in start:
                raise SystemExit(f"assistants_sunset_iphone_start:{fragment}")
        svg = archive.read("cover/cover.svg")
        if b"<script" in svg.lower() or b"https://" in svg.lower() or b"xlink:href" in svg.lower():
            raise SystemExit("assistants_sunset_iphone_cover_external_content")
    for forbidden in (b"GUMROAD_ACCESS_TOKEN", b"Authorization: Bearer", b"password=", b"token=", b"bachikoljunior-blip"):
        if forbidden in pack:
            raise SystemExit(f"assistants_sunset_iphone_secret_or_identity:{forbidden.decode()}")


def main() -> int:
    first_product = build_product()
    first_pack = build_iphone_pack(first_product)
    second_product = build_product()
    second_pack = build_iphone_pack(second_product)
    if first_product != second_product or first_pack != second_pack:
        raise SystemExit("assistants_sunset_outputs_not_deterministic")
    verify(second_product, second_pack)
    report = {
        "ok": True,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "product_output": str(PRODUCT_OUTPUT.relative_to(ROOT)),
        "product_bytes": len(second_product),
        "product_sha256": sha256(second_product),
        "iphone_output": str(IPHONE_OUTPUT.relative_to(ROOT)),
        "iphone_bytes": len(second_pack),
        "iphone_sha256": sha256(second_pack),
        "iphone_zip_members": 10,
        "deterministic_rebuild_verified": True,
        "credentials_used": False,
        "cost_yen": 0,
        "errors": [],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
