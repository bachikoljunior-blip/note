#!/usr/bin/env python3
"""BOOTH出品を「開けば1タップで終わる」形にして handoff/ へ置く。

チャットに書いた依頼は、いつ読まれるか分からない。だから依頼を会話に残さず、
GitHub 上で開けば完結する固定の場所に置く。iPhone の GitHub では
コードブロックにコピーボタンが付くので、貼る内容は必ずコードブロックにする。

    python scripts/build_booth_idle_handoff.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LISTING = ROOT / "content" / "booth_idle" / "listing.md"
STATE = ROOT / "state" / "brandable_idle.json"
OUTPUT = ROOT / "handoff" / "BOOTH_IDLE_KIT.md"
BUNDLED_ZIP = ROOT / "handoff" / "Brandable_Idle_Clicker_Kit_v1.0.zip"

NEW_ITEM_URL = "https://manage.booth.pm/items/new"
MANAGER_URL = "https://manage.booth.pm/"

TITLE = "設定1枚で自社ブランドになる放置クリッカー｜ビルド不要・依存ゼロ・スマホ対応"

TAGS = [
    "ゲーム素材", "HTML5", "ブラウザゲーム", "放置ゲーム", "クリッカー",
    "テンプレート", "商用利用可", "Web制作", "販促", "ノーコード",
]

TIERS = [
    ("通常ライセンス（自分の公開先1つ・商用可・改変可）", 3800),
    ("拡張ライセンス（クライアントワーク納品可・件数無制限）", 38000),
]


def net_yen(price: int) -> tuple[int, int]:
    """BOOTH の手数料 5.6% + 45円。表示は円未満切り上げの控えめ側で出す。"""
    fee = int(price * 0.056) + 45
    return fee, price - fee


def description() -> str:
    text = LISTING.read_text(encoding="utf-8")
    start = text.index("## 説明文")
    end = text.index("## 出品時のチェック")
    body = text[start:end].split("\n", 1)[1].strip()
    return body.replace("\n---\n", "\n")


def main() -> int:
    if not LISTING.is_file():
        raise SystemExit(f"出品文がありません: {LISTING}")
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.is_file() else {}

    built = ROOT / (state.get("output") or "dist/Brandable_Idle_Clicker_Kit_v1.0.zip")
    if built.is_file():
        BUNDLED_ZIP.parent.mkdir(parents=True, exist_ok=True)
        BUNDLED_ZIP.write_bytes(built.read_bytes())

    lines: list[str] = []
    add = lines.append

    add("# BOOTH出品（ブランド差し替え型 放置クリッカー）")
    add("")
    add("**これはオーナーへの依頼ではありません。** オーナーはリポジトリを開かないので、")
    add("ここに依頼を置いても読まれない。依頼はチャットにだけ書くこと。")
    add("")
    add("このページは、出品する機会が来たときに使う**素材**（文面・価格・ZIP）の置き場です。")
    add("")
    add(f"[① BOOTHで新規商品を作る]({NEW_ITEM_URL})")
    add("")
    add("---")
    add("")
    add("## ② 商品名（コピーして貼る）")
    add("")
    add("```")
    add(TITLE)
    add("```")
    add("")
    add("## ③ 説明文（コピーして貼る）")
    add("")
    add("```")
    add(description())
    add("```")
    add("")
    add("## ④ タグ（10個・1つずつ貼る）")
    add("")
    add("```")
    add("\n".join(TAGS))
    add("```")
    add("")
    add("## ⑤ 価格とダウンロード枠（2つ作る）")
    add("")
    add("| 枠の名前 | 価格 | 手数料 | 手取り |")
    add("| --- | --- | --- | --- |")
    for label, price in TIERS:
        fee, net = net_yen(price)
        add(f"| {label} | {price:,}円 | {fee:,}円 | {net:,}円 |")
    add("")
    add("どちらの枠にも、同じZIPを添付します。ライセンスの違いは商品説明とZIP内の")
    add("`LICENSE.txt` に書いてあります。")
    add("")
    add("## ⑥ 添付するファイル")
    add("")
    add(f"[{BUNDLED_ZIP.name} をダウンロード]({BUNDLED_ZIP.name})")
    add("")
    add("スマホの GitHub から、このリンクでそのまま落とせます。")
    add("中身は `products/brandable_idle/` と同じで、CIが作り直すたびに更新されます。")
    if state.get("sha256"):
        add("")
        add(f"- sha256: `{state['sha256']}`")
        add(f"- サイズ: {state.get('bytes', 0):,} バイト / {state.get('members', 0)} ファイル")
    add("")
    add("## ⑦ 商品画像")
    add("")
    add("リポジトリの次の2枚をそのまま使えます。")
    add("")
    add("```")
    add("products/brandable_idle/screenshot-default.png")
    add("products/brandable_idle/screenshot-cafe.png")
    add("```")
    add("")
    add("同じゲームが、設定を変えるだけで別ブランドになることが1枚で伝わります。")
    add("")
    add("---")
    add("")
    add("## ⑧ 公開したあと")
    add("")
    add(f"[BOOTHの商品管理を開く]({MANAGER_URL})")
    add("")
    add("公開後のURLを、このリポジトリの `state/brandable_idle.json` の `booth_url` に")
    add("入れてください。入れると、告知文の生成と公開ページの自動監視がそこから動きます。")
    add("URLを貼るだけで構いません。")
    add("")
    add("## 迷ったとき")
    add("")
    add("- **価格を下げたくなったら**: 通常枠だけ下げてください。拡張枠を下げると、")
    add("  月20万円に必要な件数が跳ね上がります（38,000円なら月6件、3,800円なら月57件）。")
    add("- **説明文が長いと感じたら**: 上から削ってください。")
    add("  ただし「ライセンス（2種類）」の表だけは残してください。ここが価格の根拠です。")
    add("- **1枠しか作れなかったら**: 拡張ライセンス（38,000円）を優先してください。")
    add("")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT.relative_to(ROOT)),
        "bytes": OUTPUT.stat().st_size,
        "tiers": len(TIERS),
        "tags": len(TAGS),
        "user_taps": "open the page, copy 4 blocks, attach 1 zip, set 2 prices",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
