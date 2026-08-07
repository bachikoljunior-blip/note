#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import stat
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist/Gumroad_iPhone_Listing_Pack_v1.1.zip"
REPORT = ROOT / "reports/gumroad_iphone_pack.json"
FIXED_ZIP_TIME = (2026, 8, 7, 7, 0, 0)

SOURCES = {
    "Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.1.zip": ("dist/Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.1.zip", "3adb147dc55b671d99141281cc9849e3530a8865def543d341c326a54bcf0113"),
    "gumroad_listing_launcher.html": ("dist/gumroad_listing_launcher.html", "f12c8f24f7c7a89d90ce8410776853a857e95d53754c63ce12ac02f4ddf5ec43"),
    "gumroad_visual_pack.html": ("dist/gumroad_visual_pack.html", "e805c3362029899d4504872abea99dfe26facfc32a75067d18ebc527b73e75d7"),
    "visuals/gumroad_cover_main.png": ("dist/gumroad_visuals/gumroad_cover_main.png", "7f14aa402d919617ecfe34b4bf310a5bab649d1081e9a481b4bd817a9954de75"),
    "visuals/gumroad_cover_sample.png": ("dist/gumroad_visuals/gumroad_cover_sample.png", "1aaea10932f8d93a9ef278f756f2c7cbdee7492ca41d983a75a43d9e98cac677"),
    "visuals/gumroad_cover_workflow.png": ("dist/gumroad_visuals/gumroad_cover_workflow.png", "b97b8d750855e0cabe94eced0f6ea3a593eca162a49b3698ce5200cb497abc79"),
    "visuals/gumroad_thumbnail.png": ("dist/gumroad_visuals/gumroad_thumbnail.png", "d038c99585fcbb358f648e6201adaa5334fb23115141768951926f914a03f5fb"),
    "copy/title.txt": ("content/gumroad/title.txt", "875b147ef8ae19d870096877ced297c8449f23f98bc3a71318ad163d606c18fb"),
    "copy/description.md": ("content/gumroad/description.md", "52fb7e56fd1a5762ca4386c0b33b0640826014476fd3d511ea56d9d15bcee3c4"),
    "copy/tags.txt": ("content/gumroad/tags.txt", "f29bc7c6f05175dde9c12eb869d54affa039a3f4790fad49467dc596dc531aa0"),
    "copy/refund_fine_print.txt": ("content/gumroad/refund_fine_print.txt", "221ebe24ec7f2019685cec403f63e2871f6cf8d35e25c7ad7f26574a210fec2d"),
}

START_HERE = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gumroad iPhone出品パック</title><style>
body{font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;max-width:720px;margin:auto;padding:18px;line-height:1.6;color:#172033;background:#f6f8fc}section{background:#fff;border:1px solid #dce3ef;border-radius:14px;padding:15px;margin:13px 0}a.button{display:block;background:#155eef;color:#fff;text-decoration:none;padding:13px 15px;border-radius:10px;margin:9px 0;font-weight:700}.warn{background:#fff1dc;color:#7a3100;padding:10px;border-radius:8px}code{word-break:break-all}</style></head><body>
<h1>Gumroad iPhone出品パック</h1>
<p>外側のこのZIPだけを1回展開し、<code>START_HERE.html</code>をSafariで開きます。</p>
<section><h2>1. 商品情報</h2><p><strong>Name</strong><br>Non-Repetitive AI Trivia Shorts Kit: 100 Topic Prompts + 12 Formats</p><p><strong>Type</strong>: Digital product<br><strong>Price</strong>: US$12<br><strong>Custom permalink</strong>: non-repetitive-ai-trivia-shorts-kit<br><strong>Refund period</strong>: 7 days</p><a class="button" href="gumroad_listing_launcher.html">商品文・価格ランチャーを開く</a><p>個別コピー: <a href="copy/title.txt">商品名</a> ／ <a href="copy/description.md">説明</a> ／ <a href="copy/tags.txt">タグ</a> ／ <a href="copy/refund_fine_print.txt">返金条件</a></p></section>
<section><h2>2. 商品ZIP</h2><a class="button" href="Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.1.zip" download>商品ZIPを選ぶ／保存する</a><p class="warn">この英語商品ZIPは展開せず、そのままGumroadの商品ファイルとしてアップロードします。</p></section>
<section><h2>3. 画像4点</h2><a class="button" href="gumroad_visual_pack.html">画像プレビューを開く</a><a class="button" href="visuals/gumroad_cover_main.png" download>メインカバーを保存</a><a class="button" href="visuals/gumroad_cover_sample.png" download>実データ画像を保存</a><a class="button" href="visuals/gumroad_cover_workflow.png" download>工程画像を保存</a><a class="button" href="visuals/gumroad_thumbnail.png" download>正方形サムネイルを保存</a></section>
<section><h2>4. Gumroadへ戻る</h2><a class="button" href="https://gumroad.com/products/new">Gumroad新規商品画面を開く</a><p>パスワード、確認コード、Cookie、本人確認・税務・銀行情報はチャットやGitHubへ送らず、Gumroadだけに入力します。最終公開は、商品名・US$12・ZIP・画像・7日返金条件を確認してから本人が行います。</p></section>
</body></html>
"""

README = """Gumroad iPhone出品パック v1.1

1. 外側の Gumroad_iPhone_Listing_Pack_v1.1.zip をFilesで1回だけ展開します。
2. START_HERE.htmlを長押しし、共有または「このアプリで開く」からSafariを選びます。
3. 商品名、説明、タグ、US$12、7日返金条件、英語商品ZIP、画像4点を同じフォルダから使います。
4. Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.1.zip は展開せずGumroadへアップロードします。
5. 最終公開、本人確認、税務・受取先設定は本人がGumroad上で確認します。

秘密情報はチャットやGitHubへ送らないでください。
"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_verified(relative: str, expected_sha: str) -> bytes:
    path = ROOT / relative
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise SystemExit(f"missing_gumroad_iphone_source:{relative}") from exc
    if not stat.S_ISREG(metadata.st_mode) or path.is_symlink():
        raise SystemExit(f"unsafe_gumroad_iphone_source:{relative}")
    data = path.read_bytes()
    actual = sha256(data)
    if actual != expected_sha:
        raise SystemExit(f"gumroad_iphone_source_mismatch:{relative}:sha256={actual}")
    return data


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    return info


def main() -> int:
    entries = {name: read_verified(relative, expected_sha) for name, (relative, expected_sha) in SOURCES.items()}
    entries["README_iPhone.txt"] = README.encode("utf-8")
    entries["START_HERE.html"] = START_HERE.encode("utf-8")
    manifest = {
        "schema_version": "1.0",
        "classification": "private_repository_authenticated_user_handoff",
        "product_version": "1.1",
        "price_usd": 12,
        "refund_period_days": 7,
        "product_zip_must_remain_unextracted": True,
        "final_publication": "human_only",
        "credentials_used": False,
        "cost_yen": 0,
        "files": {name: {"bytes": len(data), "sha256": sha256(data)} for name, data in sorted(entries.items())},
    }
    entries["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.{os.getpid()}.tmp")
    with zipfile.ZipFile(temporary, "w", allowZip64=False) as archive:
        for name, data in sorted(entries.items()):
            archive.writestr(zip_info(name), data)
    os.replace(temporary, OUTPUT)
    output = OUTPUT.read_bytes()
    report = {"ok": True, "checked_at_utc": datetime.now(timezone.utc).isoformat(), "output": str(OUTPUT.relative_to(ROOT)), "bytes": len(output), "sha256": sha256(output), "zip_members": len(entries), "source_files_verified": len(SOURCES), "credentials_used": False, "cost_yen": 0, "errors": []}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
