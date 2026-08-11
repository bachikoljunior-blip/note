#!/usr/bin/env python3
"""既存のものにとらわれていないかを検査する。

正本は `state/options.json`。

## なぜ要るか

2026-08-08 のオーナーの指摘。

> 既存のものにとらわれてない？既存のものにとらわれない設計にして。

そのとおりだった。**その日に作った仕組みは全部、すでに在るものを守る機械だった。**

  `loops.json`          —— いま回している workstream を列挙する
  `watchdogs.json`      —— いま在る監視対象を列挙する
  `failure_classes.json`—— すでに起きた失敗を列挙する
  `goal.json`           —— **いま持っている収入源だけ**を足し上げる

どれも「在るもの」しか入らない。**私が入れたものしか入らず、私が入れたのは
既存のものだけだった。** だから、この一式をどれだけ丁寧に回しても、
**「この資産の組み合わせが間違っている」には永久に到達できない。**

8か月ぶん作業があって0円、という事実に対して、
仕組みの側が「今の路線を続ける」以外の答えを出せない形になっていた。

## だからこの登録簿は、既存で埋まらないようにする

落とすのは5つ。

  1. 未検証かつ非既存の選択肢が `min_untested_non_incumbent` 件に満たない
     —— **登録簿が「いまやっていることの一覧」に退化するのを防ぐ**
  2. 既存（incumbent）の選択肢に kill_date が無い
     —— 撤退の期限が無いものは、永久に続けられる
  3. kill_date を過ぎているのに判断の記録が無い
  4. 最初の1円までの見込み日数が無い
     —— 比較できない案は、比較されずに温存される
  5. メタが測られていない

## 撤退規則

**既存が続いてよいのは、未検証の最良案より「最初の1円までが速い」と
言えるときだけ。** 言えないなら、既存を閉じるか、資源を移すこと。
「もう作ってあるから」は理由にならない（A14: 昔そう言ったから、は理由にならない）。

    python scripts/check_options.py
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "state" / "options.json"
MAX_FUTURE_SKEW_SECONDS = 3 * 60

REQUIRED = ("id", "what", "incumbent", "days_to_first_yen",
            "owner_actions_required", "tested")

BOUNTY_CANDIDATE_REQUIRED = (
    "id", "title", "reward_usd", "status", "available_rewards",
    "active_solvers", "claims_observed", "estimated_effort_hours",
    "source_url", "issue_url", "source_checked_at_utc", "source_status",
    "source_title", "upstream_checked_at_utc", "upstream_status",
    "upstream_title", "rank_eligible", "execution_ready",
    "external_repository_mutated",
)


def parse_aware_datetime(value: object) -> datetime | None:
    """ISO timestampを読み、aware datetimeだけを返す。"""
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def parse_day(value: str) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return None


def check_demand_scan(scan: object, now: datetime) -> list[str]:
    """需要先行案が期限だけで「需要検証済み」にならないことを検査する。"""
    problems: list[str] = []
    name = "demand_first_micro_product"
    if not isinstance(scan, dict):
        return [f"{name}: latest_demand_scan が辞書ではない"]

    checked = parse_aware_datetime(scan.get("checked_at_utc"))
    if checked is None:
        problems.append(f"{name}: checked_at_utc はタイムゾーン付き日時であること")
    max_age = scan.get("max_age_hours")
    max_age_valid = isinstance(max_age, (int, float)) and max_age > 0
    if not max_age_valid:
        problems.append(f"{name}: max_age_hours は正数であること")
    if checked is not None:
        age_seconds = (now - checked).total_seconds()
        if age_seconds < -MAX_FUTURE_SKEW_SECONDS:
            problems.append(f"{name}: checked_at_utc が現在時刻より3分を超えて未来")
        elif max_age_valid and age_seconds > max_age * 3600:
            problems.append(f"{name}: 需要測定が期限切れ。公開需要を再測定すること")

    integers: dict[str, int] = {}
    for field in (
        "lookback_days", "scope_repository_count", "search_query_count",
        "qualification_threshold", "qualifying_unique_issue_count",
    ):
        value = scan.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            problems.append(f"{name}: {field} は正の整数であること")
        else:
            integers[field] = value

    issues = scan.get("qualifying_issues")
    if not isinstance(issues, list):
        problems.append(f"{name}: qualifying_issues は配列であること")
        issues = []
    count = integers.get("qualifying_unique_issue_count")
    if count is not None and count != len(issues):
        problems.append(f"{name}: qualifying_unique_issue_count がIssue件数と一致しない")

    urls: set[str] = set()
    for index, issue in enumerate(issues):
        label = f"{name}/issue[{index}]"
        if not isinstance(issue, dict):
            problems.append(f"{label}: Issueが辞書ではない")
            continue
        url = str(issue.get("url") or "")
        if not url.startswith("https://github.com/"):
            problems.append(f"{label}: url はGitHubのhttps URLであること")
        if url in urls:
            problems.append(f"{label}: url が重複している")
        urls.add(url)
        if not str(issue.get("title") or "").strip():
            problems.append(f"{label}: title がない")
        if issue.get("state") != "open":
            problems.append(f"{label}: state=open の公開Issueだけを数えること")
        created = parse_aware_datetime(issue.get("created_at_utc"))
        if created is None:
            problems.append(f"{label}: created_at_utc はタイムゾーン付き日時であること")
        elif checked is not None:
            if (created - now).total_seconds() > MAX_FUTURE_SKEW_SECONDS:
                problems.append(f"{label}: created_at_utc が現在時刻より3分を超えて未来")
            lookback = integers.get("lookback_days")
            if lookback is not None and created < checked - timedelta(days=lookback):
                problems.append(f"{label}: 直近lookback_daysの範囲外")

    threshold = integers.get("qualification_threshold")
    observed = integers.get("qualifying_unique_issue_count")
    expected_met = (
        threshold is not None and observed is not None and observed >= threshold
    )
    threshold_met = scan.get("threshold_met")
    if not isinstance(threshold_met, bool):
        problems.append(f"{name}: threshold_met は真偽値であること")
    elif threshold_met is not expected_met:
        problems.append(f"{name}: threshold_met が件数と基準からの再計算に一致しない")

    time_cost = scan.get("manual_time_cost_over_30_minutes_verified")
    validated = scan.get("demand_validated")
    if not isinstance(time_cost, bool):
        problems.append(
            f"{name}: manual_time_cost_over_30_minutes_verified は真偽値であること"
        )
    if not isinstance(validated, bool):
        problems.append(f"{name}: demand_validated は真偽値であること")
    elif isinstance(time_cost, bool):
        expected_validated = expected_met and time_cost
        if validated is not expected_validated:
            problems.append(
                f"{name}: demand_validated は件数基準と30分超作業の両方が必要"
            )
        if not validated and scan.get("product_development_decision") != (
            "freeze_additional_build_until_stronger_signal"
        ):
            problems.append(
                f"{name}: 需要未検証なら追加開発をfreezeすること"
            )

    if scan.get("scope_exhaustive") is not False:
        problems.append(f"{name}: 公開Issue検索を網羅的と断定しないこと")
    if scan.get("external_repository_mutated") is not False:
        problems.append(f"{name}: 需要測定で外部リポジトリを変更しないこと")
    if scan.get("external_cost_yen") != 0:
        problems.append(f"{name}: 実現収益0の間は外部費用0円であること")
    if not str(scan.get("inference_boundary") or "").strip():
        problems.append(f"{name}: inference_boundary がない")
    if not str(scan.get("validation_record") or "").strip():
        problems.append(f"{name}: validation_record がない")
    return problems


def check_one(o: dict, today: date) -> list[str]:
    name = o.get("id", "(id なし)")
    problems: list[str] = []

    for field in REQUIRED:
        if field not in o:
            problems.append(f"{name}: 必須項目がない: {field}")
    if problems:
        return problems

    # 「到達不能」は空欄ではなく、立派な測定結果。区別する。
    # 空欄のまま置くと比較されずに温存されるが、unreachable と書けば
    # 順位の最後に落ちて、収入源として数えられなくなる。
    dtfy = o.get("days_to_first_yen")
    if dtfy in (None, ""):
        problems.append(
            f"{name}: days_to_first_yen が空。**比較できない案は温存される。**"
            "到達不能なら 'unreachable' と書くこと。分からないなら根拠つきの範囲を書くこと")
    elif dtfy == "unreachable" and not str(o.get("days_to_first_yen_note") or "").strip():
        problems.append(
            f"{name}: 到達不能と書くなら、なぜ到達しないのかを "
            "days_to_first_yen_note に書くこと")

    if o.get("incumbent"):
        if not o.get("kill_date"):
            problems.append(
                f"{name}: 既存なのに kill_date が無い。"
                "**撤退期限の無いものは永久に続けられる。** "
                "いつまでに1円入らなければ閉じるのかを書くこと")
        else:
            when = parse_day(o["kill_date"])
            if when is None:
                problems.append(f"{name}: kill_date を日付として読めない: {o['kill_date']!r}")
            elif when < today and not o.get("kill_decision"):
                problems.append(
                    f"{name}: kill_date（{o['kill_date']}）を過ぎているのに判断の記録"
                    "（kill_decision）が無い。閉じるか、未検証の最良案より速い理由を書くこと")

    return problems


def check_bounty_scan(
    scan: object,
    now: datetime,
    *,
    valid_fallback_ids: set[str] | None = None,
) -> list[str]:
    """有償 Issue を金額だけで選ばないための測定値を検査する。"""
    problems: list[str] = []
    if not isinstance(scan, dict):
        return ["paid_github_issue: latest_market_scan が辞書ではない"]

    measured = scan.get("checked_at_utc")
    measured_at = parse_aware_datetime(measured)
    if measured_at is None:
        problems.append(
            "paid_github_issue: checked_at_utc はタイムゾーン付き日時であること"
        )
    max_age = scan.get("max_age_hours")
    max_age_valid = isinstance(max_age, (int, float)) and max_age > 0
    if not max_age_valid:
        problems.append("paid_github_issue: max_age_hours は正数であること")
    if measured_at is not None:
        age_seconds = (now - measured_at).total_seconds()
        if age_seconds < -MAX_FUTURE_SKEW_SECONDS:
            problems.append(
                "paid_github_issue: checked_at_utc が現在時刻より3分を超えて未来"
            )
        elif max_age_valid and age_seconds > max_age * 3600:
            problems.append(
                "paid_github_issue: 候補測定が期限切れ。"
                "報酬・競争人数・公開状態を再測定すること"
            )

    candidates = scan.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        problems.append("paid_github_issue: candidates が空。金額だけの推測で順位を付けないこと")
        return problems

    ids: set[str] = set()
    computed_scores: dict[str, float] = {}
    execution_ready: dict[str, bool] = {}
    for candidate in candidates:
        if not isinstance(candidate, dict):
            problems.append("paid_github_issue: candidate が辞書ではない")
            continue
        cid = str(candidate.get("id") or "(id なし)")
        for field in BOUNTY_CANDIDATE_REQUIRED:
            if field not in candidate:
                problems.append(f"paid_github_issue/{cid}: 必須項目がない: {field}")
        if cid in ids:
            problems.append(f"paid_github_issue: candidate id が重複: {cid}")
        ids.add(cid)
        for field in ("reward_usd", "available_rewards", "active_solvers",
                      "claims_observed", "estimated_effort_hours"):
            value = candidate.get(field)
            if not isinstance(value, (int, float)) or value < 0:
                problems.append(f"paid_github_issue/{cid}: {field} は0以上の数値であること")
        reward = candidate.get("reward_usd")
        available = candidate.get("available_rewards")
        effort = candidate.get("estimated_effort_hours")
        solvers = candidate.get("active_solvers")
        if isinstance(reward, (int, float)) and reward <= 0:
            problems.append(f"paid_github_issue/{cid}: reward_usd は正数であること")
        if isinstance(available, (int, float)) and available <= 0:
            problems.append(f"paid_github_issue/{cid}: available_rewards は正数であること")
        rank_eligible = candidate.get("rank_eligible")
        ready = candidate.get("execution_ready")
        if not isinstance(rank_eligible, bool):
            problems.append(f"paid_github_issue/{cid}: rank_eligible は真偽値であること")
        if not isinstance(ready, bool):
            problems.append(f"paid_github_issue/{cid}: execution_ready は真偽値であること")
        execution_ready[cid] = ready is True

        if (rank_eligible is True
                and isinstance(reward, (int, float)) and reward > 0
                and isinstance(effort, (int, float)) and effort > 0
                and isinstance(solvers, (int, float)) and solvers >= 0):
            score = reward / (effort * (1 + solvers))
            computed_scores[cid] = score
            recorded = candidate.get("planning_score_usd_per_competition_adjusted_hour")
            if not isinstance(recorded, (int, float)) or abs(recorded - score) > 0.001:
                problems.append(
                    f"paid_github_issue/{cid}: 記録スコアが selection_formula と一致しない"
                )
        elif isinstance(effort, (int, float)) and effort <= 0:
            problems.append(f"paid_github_issue/{cid}: estimated_effort_hours は正数であること")
        for field in ("source_url", "issue_url"):
            if not str(candidate.get(field) or "").startswith("https://"):
                problems.append(f"paid_github_issue/{cid}: {field} は https URL であること")
        if candidate.get("external_repository_mutated") is not False:
            problems.append(
                f"paid_github_issue/{cid}: この自動実行では外部リポジトリを変更しないこと"
            )

        for field in ("source_checked_at_utc", "upstream_checked_at_utc"):
            raw = candidate.get(field)
            checked = parse_aware_datetime(raw)
            if checked is None:
                problems.append(
                    f"paid_github_issue/{cid}: "
                    f"{field} はタイムゾーン付き日時であること"
                )
                continue
            age_seconds = (now - checked).total_seconds()
            if age_seconds < -MAX_FUTURE_SKEW_SECONDS:
                problems.append(
                    f"paid_github_issue/{cid}: "
                    f"{field} が現在時刻より3分を超えて未来"
                )
            elif max_age_valid and age_seconds > max_age * 3600:
                problems.append(f"paid_github_issue/{cid}: {field} が期限切れ")

        if candidate.get("source_title") != candidate.get("title"):
            problems.append(f"paid_github_issue/{cid}: Opire と候補の title が一致しない")
        upstream_title = candidate.get("upstream_title")
        if upstream_title is not None and upstream_title != candidate.get("title"):
            problems.append(f"paid_github_issue/{cid}: 上流 Issue と候補の title が一致しない")
        if rank_eligible is True:
            if candidate.get("status") != "open":
                problems.append(
                    f"paid_github_issue/{cid}: rank対象は候補status=openが必要"
                )
            if candidate.get("source_status") != "verified_open":
                problems.append(
                    f"paid_github_issue/{cid}: rank対象はOpireのopen確認が必要"
                )
            if candidate.get("upstream_status") != "verified_open":
                problems.append(
                    f"paid_github_issue/{cid}: rank対象は上流Issueのopen確認が必要"
                )
            if upstream_title is None:
                problems.append(
                    f"paid_github_issue/{cid}: rank対象は上流Issueのtitle確認が必要"
                )
        elif not str(candidate.get("rejection_reason") or "").strip():
            problems.append(
                f"paid_github_issue/{cid}: rank対象外にした根拠 rejection_reason がない"
            )

    selected = scan.get("selected_candidate_id")
    if computed_scores and selected not in ids:
        problems.append("paid_github_issue: selected_candidate_id が candidates に存在しない")
    elif computed_scores and selected != max(computed_scores, key=computed_scores.get):
        problems.append("paid_github_issue: selected_candidate_id が再計算した最高スコア候補ではない")
    elif not computed_scores and selected is not None:
        problems.append("paid_github_issue: rank可能な候補がないのに選定候補がある")
    if selected is None or not execution_ready.get(str(selected), False):
        fallback = str(scan.get("fallback_option_id") or "").strip()
        if not fallback:
            problems.append(
                "paid_github_issue: 即実行できる選定候補がないなら fallback_option_id が必要"
            )
        elif valid_fallback_ids is not None and fallback not in valid_fallback_ids:
            problems.append(
                "paid_github_issue: fallback_option_id は登録済みの非既存案であること"
            )
    if not str(scan.get("selection_formula") or "").strip():
        problems.append("paid_github_issue: selection_formula がない。順位を再現できない")
    if not str(scan.get("execution_decision") or "").strip():
        problems.append("paid_github_issue: execution_decision がない")
    if scan.get("external_repository_mutated") is not False:
        problems.append("paid_github_issue: 外部リポジトリを変更した状態は許可範囲外")
    return problems


def main() -> int:
    if not DATA.is_file():
        print(json.dumps({"ok": False, "errors": [f"{DATA} がない"]},
                         ensure_ascii=False, indent=2))
        return 1

    data = json.loads(DATA.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    today = now.date()
    errors: list[str] = []

    options = data.get("options", [])
    if not options:
        errors.append("選択肢が1つも登録されていない")

    seen: set[str] = set()
    for o in options:
        if o.get("id") in seen:
            errors.append(f"id が重複している: {o.get('id')}")
        seen.add(o.get("id"))
        errors.extend(check_one(o, today))

    demand = next(
        (o for o in options if o.get("id") == "demand_first_micro_product"),
        None,
    )
    if demand:
        errors.extend(check_demand_scan(demand.get("latest_demand_scan"), now))

    paid = next((o for o in options if o.get("id") == "paid_github_issue"), None)
    if paid:
        valid_fallback_ids = {
            str(o.get("id")) for o in options
            if not o.get("incumbent") and o.get("id") != "paid_github_issue"
        }
        errors.extend(check_bounty_scan(
            paid.get("latest_market_scan"),
            now,
            valid_fallback_ids=valid_fallback_ids,
        ))

    # ここがこの検査の存在理由。
    # 未検証かつ非既存の案が一定数ないと、登録簿は「いまやっていること」に退化する。
    quota = int(data.get("min_untested_non_incumbent", 3) or 3)
    fresh = [o for o in options if not o.get("incumbent") and not o.get("tested")]
    if len(fresh) < quota:
        errors.append(
            f"未検証かつ非既存の選択肢が {len(fresh)} 件しかない（下限 {quota}）。"
            "**登録簿が『いまやっていることの一覧』に退化している。** "
            "既存の外側を先に増やすこと"
        )

    meta = data.get("meta")
    if not meta:
        errors.append("meta がない。この登録簿自身が測られない")
    elif not meta.get("revisions"):
        errors.append("meta に revisions がない。増やした理由と、捨てた案が残らない")

    def sort_key(o: dict) -> float:
        v = o.get("days_to_first_yen")
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, dict) and isinstance(v.get("low"), (int, float)):
            return float(v["low"])
        return 1e9

    ranked = sorted(options, key=sort_key)
    best_fresh = next((o for o in ranked if not o.get("incumbent")), None)

    payload = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "option_count": len(options),
        "incumbents": sum(1 for o in options if o.get("incumbent")),
        "untested_non_incumbent": len(fresh),
        "fastest_overall": ranked[0].get("id") if ranked else None,
        "fastest_non_incumbent": best_fresh.get("id") if best_fresh else None,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
