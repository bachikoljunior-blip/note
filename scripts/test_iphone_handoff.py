#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import stat
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "handoff/note_iPhone_handoff.zip"
README = ROOT / "handoff/README.md"
EXPECTED_BYTES = 137187
EXPECTED_SHA256 = "82b8177bdd9ad40c3ec940d7cfe592693d73ab5c817f91e9ceed601fdf899d68"
EXPECTED_MEMBERS = {
    "AI_trivia_shorts_creator_kit_v1.1.zip",
    "README_iPhone.txt",
    "START_HERE.html",
    "booth_listing_launcher.html",
    "booth_visuals/booth_cover_contents.png",
    "booth_visuals/booth_cover_main.png",
    "booth_visuals/booth_cover_workflow.png",
    "copy/booth_description.md",
    "copy/booth_tags.txt",
    "copy/booth_title.txt",
    "copy/note_body.md",
    "copy/note_title.txt",
    "funnel_article_launcher.html",
    "manifest.json",
    "share_launcher.html",
    "tracked_launch_links.json",
}


def fail(message: str) -> None:
    raise SystemExit(message)


data = OUTPUT.read_bytes()
actual_sha = hashlib.sha256(data).hexdigest()
if len(data) != EXPECTED_BYTES:
    fail(f"handoff_release_bytes:{len(data)}")
if actual_sha != EXPECTED_SHA256:
    fail(f"handoff_release_sha256:{actual_sha}")

with zipfile.ZipFile(OUTPUT) as archive:
    infos = archive.infolist()
    names = [info.filename for info in infos]
    if names != sorted(EXPECTED_MEMBERS) or set(names) != EXPECTED_MEMBERS:
        fail(f"handoff_members:{names}")
    if archive.testzip() is not None:
        fail("handoff_zip_crc")
    for info in infos:
        path = PurePosixPath(info.filename)
        if path.is_absolute() or ".." in path.parts or "\\" in info.filename:
            fail(f"unsafe_handoff_path:{info.filename}")
        if info.flag_bits & 0x1:
            fail(f"encrypted_handoff_member:{info.filename}")
        if info.compress_type != zipfile.ZIP_STORED:
            fail(f"nondeterministic_handoff_compression:{info.filename}")
        if info.date_time != (2026, 8, 7, 0, 0, 0):
            fail(f"handoff_timestamp:{info.filename}:{info.date_time}")
        mode = info.external_attr >> 16
        if not stat.S_ISREG(mode) or stat.S_IMODE(mode) != 0o644:
            fail(f"handoff_mode:{info.filename}:{oct(mode)}")

    manifest = json.loads(archive.read("manifest.json"))
    if manifest["repository_visibility_required"] != "private":
        fail("handoff_private_repository_contract")
    recorded = manifest["files"]
    for name in EXPECTED_MEMBERS - {"manifest.json"}:
        member = archive.read(name)
        expected = recorded.get(name)
        if not expected:
            fail(f"handoff_manifest_missing:{name}")
        if expected != {
            "bytes": len(member),
            "sha256": hashlib.sha256(member).hexdigest(),
        }:
            fail(f"handoff_manifest_mismatch:{name}")

    start = archive.read("START_HERE.html").decode("utf-8")
    required_start_links = (
        'href="share_launcher.html"',
        'href="funnel_article_launcher.html"',
        'href="booth_listing_launcher.html"',
        'href="AI_trivia_shorts_creator_kit_v1.1.zip"',
        "https://note.com/new",
        "https://manage.booth.pm/",
        "Gumroad認証開始",
        'href="copy/note_title.txt"',
        'href="copy/note_body.md"',
        'href="copy/booth_title.txt"',
        'href="copy/booth_description.md"',
        'href="copy/booth_tags.txt"',
    )
    for fragment in required_start_links:
        if start.count(fragment) != 1:
            fail(f"handoff_start_contract:{fragment}:{start.count(fragment)}")
    if "は展開せず、そのままBOOTHへアップロード" not in start:
        fail("handoff_inner_zip_warning")
    distribution = json.loads(archive.read("tracked_launch_links.json"))
    for target in ("x", "bluesky"):
        item = distribution["targets"].get(target)
        if not item or item["variant_id"] != "launch_a":
            fail(f"handoff_distribution_default:{target}")
        if html.escape(item["prefilled_url"], quote=True) not in start:
            fail(f"handoff_tracked_prefill_missing:{target}")
        for fragment in (
            f"utm_source={target}",
            "utm_medium=social",
            "utm_campaign=note_launch_20260806",
            "utm_content=launch_a",
        ):
            if fragment not in item["tracked_url"]:
                fail(f"handoff_tracking_contract:{target}:{fragment}")
    if "fallback: その他の共有／コピー（媒体別UTMなし）" not in start:
        fail("handoff_untracked_fallback_must_be_labeled")

readme = README.read_text(encoding="utf-8")
for fragment in (
    str(EXPECTED_BYTES),
    EXPECTED_SHA256,
    "リポジトリをprivateのまま維持",
    "./note_iPhone_handoff.zip?raw=1",
):
    if fragment not in readme:
        fail(f"handoff_readme_contract:{fragment}")

gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
if any(line.strip() in {"handoff", "handoff/", "*.zip"} for line in gitignore):
    fail("handoff_must_be_tracked_in_private_repository")

for forbidden in ("GUMROAD_ACCESS_TOKEN", "Authorization: Bearer", "password=", "token="):
    if forbidden.encode() in data:
        fail(f"handoff_secret_marker:{forbidden}")

builder_source = (ROOT / "scripts/build_iphone_handoff.py").read_text(encoding="utf-8")
if "dist/distribution_pack.json" in builder_source:
    fail("handoff_must_not_depend_on_timestamped_distribution_output")
volatile_distribution = ROOT / "dist/distribution_pack.json"
if not volatile_distribution.is_file():
    fail("handoff_timestamp_independence_fixture_missing")
original_distribution = volatile_distribution.read_bytes()
try:
    mutation = json.loads(original_distribution)
    mutation["generated_at_utc"] = "2099-12-31T23:59:59+00:00"
    volatile_distribution.write_text(
        json.dumps(mutation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build_iphone_handoff.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        fail(f"handoff_timestamp_independence_build:{result.stderr.strip()}")
    mutation_sha = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    if mutation_sha != EXPECTED_SHA256:
        fail(f"handoff_timestamp_independence_sha256:{mutation_sha}")
finally:
    volatile_distribution.write_bytes(original_distribution)
    restore = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build_iphone_handoff.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if restore.returncode:
        fail(f"handoff_restore_build:{restore.stderr.strip()}")

print(
    json.dumps(
        {
            "ok": True,
            "bytes": len(data),
            "sha256": actual_sha,
            "zip_members": len(EXPECTED_MEMBERS),
            "repository_visibility_required": "private",
            "source_launchers": 3,
            "tracked_prefill_targets": 2,
            "booth_product_files": 1,
            "booth_visual_files": 3,
        },
        ensure_ascii=False,
    )
)
