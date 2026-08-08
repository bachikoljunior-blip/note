#!/usr/bin/env python3
"""ブランド差し替え型 放置クリッカーを、決定的なZIPへまとめる。

    python scripts/build_brandable_idle.py

同じ入力からは必ず同じ sha256 が出る（時刻・順序・権限を固定する）。
CIは2回ビルドしてハッシュ差分が無いことを確認する。
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "products" / "brandable_idle"
OUT = ROOT / "dist" / "Brandable_Idle_Clicker_Kit_v1.0.zip"
STATE = ROOT / "state" / "brandable_idle.json"
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)

# 同梱するもの。ここに無いものは入らない（テストの生成物やスクリーンショットを
# 誤って商品へ混ぜないため、除外ではなく明示の許可リストにしている）。
MEMBERS = [
    "README.md",
    "LICENSE.txt",
    "index.html",
    "generator.html",
    "brand.config.json",
    "validate_config.py",
    "test_engine.py",
    "assets/engine.js",
    "assets/style.css",
    "examples/cafe.json",
    "examples/salon.json",
    "examples/creator.json",
]


def build() -> dict:
    missing = [name for name in MEMBERS if not (SOURCE / name).is_file()]
    if missing:
        raise SystemExit("同梱するファイルがありません: " + ", ".join(missing))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name in MEMBERS:
            info = zipfile.ZipInfo(f"brandable-idle-clicker/{name}", date_time=FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, (SOURCE / name).read_bytes())

    data = OUT.read_bytes()
    return {
        "output": str(OUT.relative_to(ROOT)),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "members": len(MEMBERS),
    }


def main() -> int:
    result = build()
    config = json.loads((SOURCE / "brand.config.json").read_text(encoding="utf-8"))
    result.update(
        {
            "product": "ブランド差し替え型 放置クリッカー",
            "version": "1.0",
            "source": str(SOURCE.relative_to(ROOT)),
            "generators": len(config["generators"]),
            "upgrades": len(config.get("upgrades", [])),
            "examples": 3,
            "external_dependencies": 0,
            "build_step_required": False,
            "browser_test": "products/brandable_idle/test_engine.py",
            "config_validator": "products/brandable_idle/validate_config.py",
        }
    )
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
