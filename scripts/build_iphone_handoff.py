#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import os
import stat
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "handoff/note_iPhone_handoff.zip"
README = ROOT / "handoff/README.md"
REPORT = ROOT / "reports/iphone_handoff.json"
FIXED_ZIP_TIME = (2026, 8, 7, 0, 0, 0)

SOURCE_SPECS = {
    "AI_trivia_shorts_creator_kit_v1.1.zip": (
        "dist/AI_trivia_shorts_creator_kit_v1.1.zip",
        23954,
        "5c626f702ec8f155e12b63aa399802d601de8cdb087cccaddceb141953128caf",
    ),
    "booth_listing_launcher.html": (
        "dist/booth_listing_launcher.html",
        11672,
        "5f7b87489d0c8e1bff117b8501f41e5817a3ced2d72f7198d800de80437bd3da",
    ),
    "booth_visuals/booth_cover_contents.png": (
        "dist/booth_visuals/booth_cover_contents.png",
        17595,
        "db4eaa50147520ee960f838f31c45cd5da9b09df47800aa912317271956c8fa9",
    ),
    "booth_visuals/booth_cover_main.png": (
        "dist/booth_visuals/booth_cover_main.png",
        17305,
        "99bab78f8072baa7c144f6aa2087c6079ec3f752fb9cb6776fdec84c326493fe",
    ),
    "booth_visuals/booth_cover_workflow.png": (
        "dist/booth_visuals/booth_cover_workflow.png",
        17968,
        "4d4a05eb23a1deb9aff862f348dc1a1d4e53b44a82a9d1e7e5b8f70ce28b10bd",
    ),
    "funnel_article_launcher.html": (
        "dist/funnel_article_launcher.html",
        13257,
        "1674438c2dafce9da658b5dde1101dc03b06e3666a43560225734ec3714fed36",
    ),
    "share_launcher.html": (
        "dist/share_launcher.html",
        8639,
        "d438cc5489e7da90846efc6d70ccb5c32bd5d9aacdb88ac952d2cfa13f4d2711",
    ),
    "copy/note_title.txt": (
        "content/note/funnel_policy_2026/title.txt",
        105,
        "5377dfd58e17e95f42bbf9d0e4b8527d6892cdcb3e98c4c7b64003b72317cdfd",
    ),
    "copy/note_body.md": (
        "content/note/funnel_policy_2026/body.md",
        7612,
        "d19ba64429747484c2728e919183188a11d1bdd2bf8a5cfe5d92815a149d37d5",
    ),
    "copy/booth_title.txt": (
        "content/booth/title.txt",
        102,
        "bd1623de56b2b0f8f38f924eff69a8398752ac62793a1ce4370ed1ab27c79e5f",
    ),
    "copy/booth_description.md": (
        "content/booth/description.md",
        4033,
        "5db4c5d0404658f2d39f55854571e46382b38750f50acd880fb6a7855950190b",
    ),
    "copy/booth_tags.txt": (
        "content/booth/tags.txt",
        97,
        "1e4e8b4a3d915b58caed6c837d73e22165c60a0452790e685cdb9edec05458c0",
    ),
}

DISTRIBUTION_CONFIG_SPEC = (
    "config/distribution.json",
    2681,
    "878286afd1829ef7a238bfad032e0cf39fae92efb8caafb855c45661867f03f6",
)

START_HERE_TEMPLATE = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>収益プロジェクト iPhoneハンドオフ</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;max-width:720px;margin:auto;padding:20px;line-height:1.65;color:#172033;background:#f6f8fc}
h1{font-size:1.55rem}section{background:white;border:1px solid #dce3ef;border-radius:14px;padding:16px;margin:14px 0}a.button{display:block;background:#155eef;color:white;text-decoration:none;padding:13px 15px;border-radius:10px;margin:10px 0;font-weight:700}.warn{color:#7a3100;background:#fff1dc;padding:10px;border-radius:8px}code{word-break:break-all}</style>
</head>
<body>
<h1>収益プロジェクト iPhoneハンドオフ</h1>
<p>外側の <code>note_iPhone_handoff.zip</code> だけを展開し、このファイルをSafariで開いてください。</p>
<section><h2>1. 公開済みnoteを告知</h2><a class="button" href="__X_PREFILLED_URL__">Xへ事前入力（媒体別計測あり）</a><a class="button" href="__BLUESKY_PREFILLED_URL__">Blueskyへ事前入力（媒体別計測あり）</a><p>どちらか1媒体で本文とUTM付き計測URLを確認し、本人アカウントで最終公開します。</p><a href="share_launcher.html">fallback: その他の共有／コピー（媒体別UTMなし）</a></section>
<section><h2>2. 無料note導線を公開</h2><a class="button" href="funnel_article_launcher.html">無料記事ランチャーを開く</a><a class="button" href="https://note.com/new">note新規投稿を開く</a><p>HTMLが動かない時: <a href="copy/note_title.txt">題名</a> ／ <a href="copy/note_body.md">本文</a></p></section>
<section><h2>3. BOOTHを公開</h2><a class="button" href="booth_listing_launcher.html">BOOTH出品ランチャーを開く</a><a class="button" href="https://manage.booth.pm/">BOOTH管理を開く</a><p>HTMLが動かない時: <a href="copy/booth_title.txt">商品名</a> ／ <a href="copy/booth_description.md">説明</a> ／ <a href="copy/booth_tags.txt">タグ</a></p><a class="button" href="AI_trivia_shorts_creator_kit_v1.1.zip" download>商品ZIPを選ぶ／保存する</a><a class="button" href="booth_visuals/booth_cover_main.png" download>画像1を保存</a><a class="button" href="booth_visuals/booth_cover_contents.png" download>画像2を保存</a><a class="button" href="booth_visuals/booth_cover_workflow.png" download>画像3を保存</a><p class="warn">商品ZIP <code>AI_trivia_shorts_creator_kit_v1.1.zip</code> は展開せず、そのままBOOTHへアップロードします。</p></section>
<section><h2>4. Gumroad</h2><p>操作できる時に、このチャットへ「Gumroad認証開始」と送ってください。短時間だけ有効な公式device OAuthをその時点で発行し、承認後はassistantが未公開下書きを一括作成します。</p></section>
<p>HTMLがFilesのプレビューで動かない場合は、長押し → 共有 → Safariで開く、または同梱ファイルを個別に開いてください。</p>
</body>
</html>
"""

README_TEXT = """収益プロジェクト iPhoneハンドオフ

1. 外側の note_iPhone_handoff.zip をiPhoneのFilesで1回だけタップして展開します。
2. 展開フォルダの START_HERE.html を長押しし、共有または「このアプリで開く」からSafariで開きます。
3. 公開済みnoteの告知、無料note記事、BOOTHの順に進めます。
4. AI_trivia_shorts_creator_kit_v1.1.zip は展開せず、そのままBOOTHの商品ファイルに選びます。
5. Gumroadは操作できる時だけチャットへ「Gumroad認証開始」と送ります。期限切れを避けるためdevice codeは事前発行しません。

HTMLが動かない場合は、同梱の copy/note_title.txt、copy/note_body.md、copy/booth_title.txt、copy/booth_description.md、copy/booth_tags.txt を個別に開いてコピーします。
"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_verified_source(relative: str, expected_bytes: int, expected_sha: str) -> bytes:
    path = ROOT / relative
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise SystemExit(f"missing_handoff_source:{relative}") from exc
    if not stat.S_ISREG(metadata.st_mode) or path.is_symlink():
        raise SystemExit(f"unsafe_handoff_source:{relative}")
    data = path.read_bytes()
    actual_sha = sha256(data)
    if len(data) != expected_bytes or actual_sha != expected_sha:
        raise SystemExit(
            f"handoff_source_mismatch:{relative}:bytes={len(data)}:sha256={actual_sha}"
        )
    return data


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    return info


def main() -> int:
    entries: dict[str, bytes] = {
        name: read_verified_source(relative, expected_bytes, expected_sha)
        for name, (relative, expected_bytes, expected_sha) in SOURCE_SPECS.items()
    }
    distribution_bytes = read_verified_source(*DISTRIBUTION_CONFIG_SPEC)
    distribution = json.loads(distribution_bytes.decode("utf-8"))
    variant = next(
        (
            item
            for item in distribution.get("variants", [])
            if item.get("id") == distribution.get("default_variant") == "launch_a"
        ),
        None,
    )
    if not variant:
        raise SystemExit("handoff_distribution_default_variant")
    product_url = distribution.get("product", {}).get("url", "")
    split = urlsplit(product_url)
    if split.scheme != "https" or split.netloc != "note.com" or not split.path.startswith("/mobile_ai_studio/n/"):
        raise SystemExit("handoff_distribution_product_url")
    campaign = distribution.get("tracking", {}).get("utm_campaign")
    targets_by_id = {
        target.get("id"): target for target in distribution.get("targets", [])
    }
    selected: dict[str, dict[str, str]] = {}
    for target in ("x", "bluesky"):
        target_config = targets_by_id.get(target)
        if not target_config:
            raise SystemExit(f"handoff_distribution_target:{target}")
        query = [
            (key, value)
            for key, value in parse_qsl(split.query, keep_blank_values=True)
            if not key.startswith("utm_")
        ]
        query.extend(
            (
                ("utm_source", target_config["utm_source"]),
                ("utm_medium", target_config["utm_medium"]),
                ("utm_campaign", campaign),
                ("utm_content", variant["id"]),
            )
        )
        tracked = urlunsplit(
            (split.scheme, split.netloc, split.path, urlencode(query), split.fragment)
        )
        if target == "x":
            expected_template = "https://twitter.com/intent/tweet?text={text}&url={url}"
            if target_config.get("prefill") != expected_template:
                raise SystemExit("handoff_distribution_x_template")
            prefilled = expected_template.replace(
                "{text}", quote(variant["text"], safe="")
            ).replace("{url}", quote(tracked, safe=""))
        else:
            expected_template = "https://bsky.app/intent/compose?text={text_with_url}"
            if target_config.get("prefill") != expected_template:
                raise SystemExit("handoff_distribution_bluesky_template")
            prefilled = expected_template.replace(
                "{text_with_url}", quote(f'{variant["text"]}\n{tracked}', safe="")
            )
        selected[target] = {
            "target_id": target,
            "variant_id": variant["id"],
            "text": variant["text"],
            "tracked_url": tracked,
            "prefilled_url": prefilled,
        }
    entries["tracked_launch_links.json"] = (
        json.dumps(
            {
                "schema_version": "1.0",
                "source_config_sha256": DISTRIBUTION_CONFIG_SPEC[2],
                "variant_id": variant["id"],
                "targets": selected,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    start_here = START_HERE_TEMPLATE.replace(
        "__X_PREFILLED_URL__", html.escape(selected["x"]["prefilled_url"], quote=True)
    ).replace(
        "__BLUESKY_PREFILLED_URL__",
        html.escape(selected["bluesky"]["prefilled_url"], quote=True),
    )
    entries["README_iPhone.txt"] = README_TEXT.encode("utf-8")
    entries["START_HERE.html"] = start_here.encode("utf-8")
    manifest = {
        "schema_version": "1.0",
        "classification": "private_repository_authenticated_user_handoff",
        "repository": "bachikoljunior-blip/note",
        "repository_visibility_required": "private",
        "source_validation": {
            "pull_request": 25,
            "validated_head": "4d73edd52128ab4095e9d4981ce7ee586f254a4d",
            "workflow_run_id": 31137094621,
            "workflow_conclusion": "success",
            "merged_main_commit": "c4d9e5943dc563da8cb6f0cd0c77aa2a11e921d0",
        },
        "instructions": {
            "outer_zip": "extract once",
            "booth_product_zip": "do not extract; upload as the product file",
            "gumroad_device_oauth": "generate only when the user is ready",
        },
        "files": {
            name: {"bytes": len(data), "sha256": sha256(data)}
            for name, data in sorted(entries.items())
        },
    }
    entries["manifest.json"] = (
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.{os.getpid()}.tmp")
    with zipfile.ZipFile(temporary, "w", allowZip64=False) as archive:
        for name, data in sorted(entries.items()):
            archive.writestr(zip_info(name), data)
    os.replace(temporary, OUTPUT)

    output_bytes = OUTPUT.read_bytes()
    output_sha = sha256(output_bytes)
    readme = f"""# iPhone handoff

[iPhone用ハンドオフZIPをダウンロード](./note_iPhone_handoff.zip?raw=1)

- 外側ZIP: 1回だけ展開
- BOOTH商品ZIP: 展開せずアップロード
- ZIP bytes: `{len(output_bytes)}`
- ZIP SHA-256: `{output_sha}`
- 内容: 公開済みnote告知、無料note記事、BOOTH商品ZIP・画像3点・出品ランチャー

このフォルダには販売物が含まれます。リポジトリをprivateのまま維持してください。公開リポジトリへコピーしないでください。
"""
    README.write_text(readme, encoding="utf-8", newline="\n")

    report = {
        "ok": True,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "assistant_operational_validation_not_permanent_directive",
        "output": str(OUTPUT.relative_to(ROOT)),
        "bytes": len(output_bytes),
        "sha256": output_sha,
        "zip_members": len(entries),
        "compression": "ZIP_STORED",
        "repository_visibility_required": "private",
        "source_files_verified": len(SOURCE_SPECS) + 1,
        "credentials_used": False,
        "cost_yen": 0,
        "errors": [],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
