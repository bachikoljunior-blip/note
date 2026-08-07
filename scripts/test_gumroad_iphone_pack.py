#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import stat
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist/Gumroad_iPhone_Listing_Pack_v1.1.zip"
BUILDER = ROOT / "scripts/build_gumroad_iphone_pack.py"
EXPECTED_MEMBERS = {
    "Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.1.zip", "README_iPhone.txt", "START_HERE.html", "gumroad_listing_launcher.html", "gumroad_visual_pack.html", "manifest.json",
    "copy/title.txt", "copy/description.md", "copy/tags.txt", "copy/refund_fine_print.txt",
    "visuals/gumroad_cover_main.png", "visuals/gumroad_cover_sample.png", "visuals/gumroad_cover_workflow.png", "visuals/gumroad_thumbnail.png",
}


def fail(message: str) -> None:
    raise SystemExit(message)


def build() -> bytes:
    result = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode:
        fail(f"gumroad_iphone_build:{result.stderr.strip()}")
    return OUTPUT.read_bytes()


first = build()
second = build()
if first != second:
    fail("gumroad_iphone_pack_not_deterministic")

with zipfile.ZipFile(OUTPUT) as archive:
    infos = archive.infolist()
    names = [item.filename for item in infos]
    if names != sorted(EXPECTED_MEMBERS) or set(names) != EXPECTED_MEMBERS:
        fail(f"gumroad_iphone_members:{names}")
    if archive.testzip() is not None:
        fail("gumroad_iphone_crc")
    for info in infos:
        path = PurePosixPath(info.filename)
        if path.is_absolute() or ".." in path.parts or "\\" in info.filename:
            fail(f"gumroad_iphone_unsafe_path:{info.filename}")
        if info.flag_bits & 1 or info.compress_type != zipfile.ZIP_STORED:
            fail(f"gumroad_iphone_zip_contract:{info.filename}")
        if info.date_time != (2026, 8, 7, 7, 0, 0):
            fail(f"gumroad_iphone_timestamp:{info.filename}")
        mode = info.external_attr >> 16
        if not stat.S_ISREG(mode) or stat.S_IMODE(mode) != 0o644:
            fail(f"gumroad_iphone_mode:{info.filename}")
    manifest = json.loads(archive.read("manifest.json"))
    if manifest["price_usd"] != 12 or manifest["refund_period_days"] != 7 or manifest["final_publication"] != "human_only":
        fail("gumroad_iphone_listing_contract")
    for name in EXPECTED_MEMBERS - {"manifest.json"}:
        data = archive.read(name)
        if manifest["files"].get(name) != {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}:
            fail(f"gumroad_iphone_manifest:{name}")
    start = archive.read("START_HERE.html").decode("utf-8")
    for fragment in ("Non-Repetitive AI Trivia Shorts Kit", "US$12", "7 days", "https://gumroad.com/products/new", "商品ZIPは展開せず", "最終公開"):
        if fragment not in start:
            fail(f"gumroad_iphone_start:{fragment}")
    with zipfile.ZipFile(archive.open("Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.1.zip")) as product:
        if len(product.infolist()) != 15 or product.testzip() is not None:
            fail("gumroad_iphone_product_zip")

for forbidden in (b"GUMROAD_ACCESS_TOKEN", b"Authorization: Bearer", b"password=", b"token="):
    if forbidden in first:
        fail(f"gumroad_iphone_secret:{forbidden.decode()}")

print(json.dumps({"ok": True, "bytes": len(first), "sha256": hashlib.sha256(first).hexdigest(), "zip_members": len(EXPECTED_MEMBERS), "product_files": 1, "visual_files": 4, "copy_files": 4, "credentials_used": False, "cost_yen": 0}, ensure_ascii=False))
