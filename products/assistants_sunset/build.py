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
    if title != "Assistants API Sunset Migration Kit" or summary != "Audit legacy Assistants API usage, preview conservative code changes, and migrate toward Responses + Conversations before the 2026-08-26 shutdown.":
        raise SystemExit("assistants_sunset_one_session_copy_contract")
    html = "<!doctype html>\n<html lang=\"ja\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Gumroad非労働収益化 iPhone一括パック</title><style>\nbody{font-family:-apple-system,BlinkMacSystemFont,\"Hiragino Sans\",sans-serif;max-width:760px;margin:auto;padding:18px;line-height:1.65;color:#172033;background:#f3f6fa}section{background:#fff;border:1px solid #d8e1ed;border-radius:16px;padding:16px;margin:14px 0}a.button{display:block;background:#0f766e;color:#fff;text-decoration:none;padding:13px 15px;border-radius:10px;margin:10px 0;font-weight:700}.warn{background:#fff0d5;color:#763b00;padding:11px;border-radius:9px}.ok{background:#e8f7f2;color:#075c50;padding:11px;border-radius:9px}code{word-break:break-all}table{border-collapse:collapse;width:100%}th,td{border:1px solid #d8e1ed;padding:8px;text-align:left;vertical-align:top}small{color:#55657a}</style></head><body>\n<h1>Gumroad非労働収益化<br>iPhone一括パック</h1><p>外側のこのZIPだけを1回展開し、<code>START_HERE.html</code>をSafariで開きます。1回の認証済みGumroadセッションで、既存商品の高単価ライセンス追加と新商品の公開準備を続けて行います。</p>\n<section><h2>A. 既存商品に高単価版を追加</h2><a class=\"button\" href=\"https://app.gumroad.com/products\">Gumroadの商品一覧を開く</a><p>公開済みの「放置クリッカー制作キット」を選び、Productタブの<strong>Versions</strong>に次の2枠を追加します。既存の購入者向けZIPは削除・差し替えしません。</p>\n<table><tr><th>Version</th><th>追加額</th><th>購入総額</th></tr><tr><td>通常ライセンス / Standard (1 site)</td><td>US$0</td><td>US$25</td></tr><tr><td>拡張ライセンス / Extended (unlimited client work)</td><td>US$324</td><td><strong>US$349</strong></td></tr></table>\n<p>個別コピー: <a href=\"brandable/standard_version.txt\">通常版</a> ／ <a href=\"brandable/extended_version.txt\">拡張版</a> ／ <a href=\"brandable/unit_economics.txt\">単価計算</a></p><p class=\"warn\">拡張版は、購入者が複数の自社サイトおよび件数無制限のクライアント案件へ組み込めるライセンスです。キット自体の再販・再配布は禁止。個別の制作、設置、カスタマイズ、コンサルティングは商品に含めません。</p>\n<p>保存後、creator Test Purchaseで<strong>拡張版</strong>を選べることと、購入者向けZIPを取得できることを確認します。可能ならGumroad Affiliatesをオプトインしますが、手動で他人を追加したりアカウント権限を渡したりしません。</p></section>\n<section><h2>B. Assistants API移行キット</h2><p><strong>Name</strong><br>Assistants API Sunset Migration Kit</p><p><strong>Type</strong>: Digital product<br><strong>Price</strong>: US$9<br><strong>Custom permalink</strong>: assistants-api-sunset-migration-kit<br><strong>Refund period</strong>: 7 days</p><p><strong>Summary</strong><br>Audit legacy Assistants API usage, preview conservative code changes, and migrate toward Responses + Conversations before the 2026-08-26 shutdown.</p><p>個別コピー: <a href=\"copy/title.txt\">商品名</a> ／ <a href=\"copy/summary.txt\">短文</a> ／ <a href=\"copy/description.md\">説明</a> ／ <a href=\"copy/tags.txt\">タグ</a> ／ <a href=\"copy/refund_fine_print.txt\">返金条件</a></p>\n<a class=\"button\" href=\"Assistants_API_Sunset_Migration_Kit_v1.zip\" download>購入者向けZIPを選ぶ／保存する</a><p class=\"warn\">この内側の商品ZIPは展開せず、そのままGumroadのContentへアップロードします。外側のiPhone一括パックは購入者向けファイルにしません。</p><a class=\"button\" href=\"cover/cover.svg\">検証済みカバーを開く</a><a class=\"button\" href=\"https://gumroad.com/products/new\">Gumroad新規商品画面を開く</a><p>別商品として作成し、ZIPのアップロード完了後にcreator Test Purchaseを実行します。</p></section>\n<section><h2>C. 完了条件</h2><ol><li>既存商品で通常版US$25と拡張版US$349を選べる。</li><li>拡張版のcreator Test PurchaseでZIPを取得できる。</li><li>Assistants商品でもcreator Test Purchaseで内側ZIPを取得できる。</li><li>内容と規約を確認し、公開する商品だけ本人が最終公開する。</li></ol><p class=\"ok\">完了後は、公開した商品の公開URLだけをチャットへ返します。</p><p>パスワード、確認コード、Cookie、本人確認・税務・銀行情報はGumroad以外へ送信しません。</p></section>\n<section><h2>根拠</h2><p><small>Gumroad公式: <a href=\"https://gumroad.com/help/article/126-setting-up-versions-on-a-digital-product.html\">Versions設定</a> ／ <a href=\"https://gumroad.com/help/article/66-gumroads-fees.html\">手数料</a> ／ <a href=\"https://gumroad.com/help/article/333-affiliates-on-gumroad.html\">Affiliates</a>。為替は計画時点の1米ドル=159.29円、ストレス計算は145円を使用しています。税・為替・振込費用は実測値で後から再計算します。</small></p></section>\n</body></html>\n"
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
    if title != "Assistants API Sunset Migration Kit" or price != "$9 launch price":
        raise SystemExit("assistants_sunset_listing_contract")
    for required in ("2026-08-26", "Responses + Conversations", "independent developer utility", "not an official OpenAI product"):
        if required not in listing:
            raise SystemExit(f"assistants_sunset_listing_missing:{required}")

    entries = {
        "Assistants_API_Sunset_Migration_Kit_v1.zip": product,
        "README_iPhone.txt": "Gumroad non-labor income - one-session iPhone pack\n\n1. Open START_HERE.html in Safari.\n2. On the existing idle-clicker product, add Standard ($0 extra, $25 total) and Extended ($324 extra, $349 total) versions without replacing the buyer ZIP.\n3. Creator Test Purchase the Extended version and verify the buyer ZIP.\n4. Create the separate US$9 Assistants API Sunset Migration Kit, upload the inner ZIP, and run creator Test Purchase.\n5. Make the final publication decisions on Gumroad. Enter credentials, identity, tax, payout and banking information only on Gumroad.\n".encode("utf-8"),
        "START_HERE.html": start_here(title, summary),
        "brandable/standard_version.txt": "Version name:\n通常ライセンス / Standard (1 site)\n\nAdditional amount above the existing US$25 base price:\nUS$0\n\nDescription:\nUse for one site owned or operated by the purchaser. Commercial use and modification are allowed. Client delivery, resale, and redistribution of the kit are not allowed.\n".encode("utf-8"),
        "brandable/extended_version.txt": "Version name:\n拡張ライセンス / Extended (unlimited client work)\n\nAdditional amount above the existing US$25 base price:\nUS$324\n\nTotal customer price:\nUS$349\n\nDescription:\nUse on multiple sites owned or operated by the purchaser and in unlimited client projects. Modified deliverables may be handed to clients. Resale or redistribution of the kit itself is prohibited. Self-service download only; bespoke development, installation, customization, consulting, and ongoing support are not included.\n".encode("utf-8"),
        "brandable/unit_economics.txt": "Extended version unit economics (planning assumptions, 2026-08-12)\n\nCustomer price: US$349\nCurrent planning FX: 159.29 JPY/USD\nStress FX: 145 JPY/USD\n\nDirect sale after 10% + US$0.50 platform fee:\nUS$313.60 = about JPY49,953 at 159.29, or JPY45,472 at 145.\n\nDiscover-style 30% platform fee:\nUS$244.30 = about JPY38,915 at 159.29, or JPY35,424 at 145.\n\nOperational target: 7 Extended sales per month.\nAt the stress FX and 30% fee, 7 sales are about JPY247,965 before taxes, currency-conversion, payout, refund, and other costs. Use verified platform net revenue for the final JPY200,000 decision.\n".encode("utf-8"),
        "copy/title.txt": (title + "\n").encode("utf-8"),
        "copy/summary.txt": (summary + "\n").encode("utf-8"),
        "copy/description.md": (description + "\n").encode("utf-8"),
        "copy/tags.txt": (TAGS + "\n").encode("utf-8"),
        "copy/refund_fine_print.txt": (REFUND_FINE_PRINT + "\n").encode("utf-8"),
        "cover/cover.svg": cover_svg(),
    }
    manifest = {
        "schema_version": "2.0",
        "classification": "private_repository_authenticated_user_handoff",
        "purpose": "one_authenticated_gumroad_session_for_two_non_labor_income_changes",
        "one_authenticated_session": True,
        "assistants_product": {
            "product": title,
            "price_usd": 9,
            "permalink": PERMALINK,
            "refund_period_days": 7,
            "sunset_date": "2026-08-26",
            "product_zip_must_remain_unextracted": True,
        },
        "brandable_product_upgrade": {
            "existing_base_price_usd": 25,
            "standard_additional_usd": 0,
            "extended_additional_usd": 324,
            "extended_total_usd": 349,
            "monthly_extended_sales_target": 7,
            "current_planning_usd_jpy": 159.29,
            "stress_usd_jpy": 145,
            "buyer_zip_must_not_be_replaced": True,
        },
        "creator_test_purchase_required_for_both_products": True,
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
        "brandable/standard_version.txt", "brandable/extended_version.txt", "brandable/unit_economics.txt",
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
        if (
            manifest["assistants_product"]["price_usd"] != 9
            or manifest["brandable_product_upgrade"]["extended_total_usd"] != 349
            or manifest["brandable_product_upgrade"]["monthly_extended_sales_target"] != 7
            or manifest["final_publication"] != "human_only"
            or not manifest["creator_test_purchase_required_for_both_products"]
        ):
            raise SystemExit("assistants_sunset_iphone_listing_contract")
        for name in expected - {"manifest.json"}:
            data = archive.read(name)
            if manifest["files"].get(name) != {"bytes": len(data), "sha256": sha256(data)}:
                raise SystemExit(f"assistants_sunset_iphone_manifest:{name}")
        if archive.read("Assistants_API_Sunset_Migration_Kit_v1.zip") != product:
            raise SystemExit("assistants_sunset_iphone_nested_product")
        start = archive.read("START_HERE.html").decode("utf-8")
        for fragment in ("Assistants API Sunset Migration Kit", "US$9", "2026-08-26", "US$349", "US$324", "https://app.gumroad.com/products", "https://gumroad.com/products/new", "creator Test Purchase", "最終公開"):
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
        "iphone_zip_members": 13,
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
