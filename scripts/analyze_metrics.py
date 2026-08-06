#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "metrics.csv"
REPORT_PATH = ROOT / "reports" / "latest.md"
JSON_PATH = ROOT / "reports" / "latest.json"


def integer(row: dict[str, str], key: str) -> int:
    value = (row.get(key) or "0").strip()
    return int(value) if value else 0


def main() -> int:
    with CSV_PATH.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        text = "# 最新分析\n\n計測値はまだありません。公開48時間後の数値を `data/metrics.csv` に追加してください。\n"
        REPORT_PATH.write_text(text, encoding="utf-8")
        JSON_PATH.write_text(json.dumps({"status": "waiting_for_metrics"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(text)
        return 0

    row = rows[-1]
    views = integer(row, "views")
    likes = integer(row, "likes")
    purchases = integer(row, "purchases")
    gross = integer(row, "gross_revenue_yen")
    refunds = integer(row, "refunds")
    net_gross = max(gross - refunds, 0)
    conversion = purchases / views if views else 0.0
    like_rate = likes / views if views else 0.0
    revenue_per_view = net_gross / views if views else 0.0

    actions: list[str] = []
    if views < 100:
        actions.append("流入不足を優先。無料サンプル記事と既存の発信先から商品ページへ送客する。")
    elif purchases == 0:
        actions.append("閲覧はあるが購入0件。タイトル・冒頭・完成実例・価格の順で1要素ずつテストする。")
    elif purchases < 3:
        actions.append("初期購入が発生。3件または7日までは大幅変更せず、購入理由と離脱点を集める。")
    else:
        actions.append("販売3件以上。価格1,980円への移行候補を、購入率と手取りの両方で比較する。")
    if views >= 100 and like_rate < 0.01:
        actions.append("スキ率が1%未満。無料部分の具体性と信頼材料を強化する。")
    if purchases and conversion >= 0.03:
        actions.append("購入率3%以上。商品ページ改変より流入拡大を優先する。")

    payload = {
        "status": "analyzed",
        "checkpoint": row.get("checkpoint", ""),
        "views": views,
        "likes": likes,
        "purchases": purchases,
        "net_gross_revenue_yen": net_gross,
        "purchase_conversion": conversion,
        "like_rate": like_rate,
        "revenue_per_view_yen": revenue_per_view,
        "actions": actions,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    lines = [
        "# 最新分析",
        "",
        f"- チェックポイント: {payload['checkpoint'] or '未指定'}",
        f"- 閲覧: {views}",
        f"- スキ: {likes}（{like_rate:.2%}）",
        f"- 購入: {purchases}（閲覧→購入 {conversion:.2%}）",
        f"- 返金控除後の総売上入力値: {net_gross:,}円",
        f"- 閲覧1件あたり売上: {revenue_per_view:.2f}円",
        "",
        "## 次の判断",
        "",
    ] + [f"- {action}" for action in actions]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
