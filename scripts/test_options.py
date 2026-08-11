#!/usr/bin/env python3
"""有償Issue測定が片側だけの観測や古い値で通らないことを固定時刻で検証する。"""
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from check_options import check_bounty_scan, check_demand_scan


NOW = datetime(2026, 8, 11, 4, 40, tzinfo=timezone.utc)


def candidate(cid: str, reward: float, effort: float, solvers: int) -> dict:
    title = f"Verified issue {cid}"
    return {
        "id": cid,
        "title": title,
        "reward_usd": reward,
        "status": "open",
        "available_rewards": 1,
        "active_solvers": solvers,
        "claims_observed": solvers,
        "estimated_effort_hours": effort,
        "planning_score_usd_per_competition_adjusted_hour": (
            reward / (effort * (1 + solvers))
        ),
        "source_url": f"https://example.invalid/opire/{cid}",
        "issue_url": f"https://example.invalid/upstream/{cid}",
        "source_checked_at_utc": "2026-08-11T04:30:00Z",
        "source_status": "verified_open",
        "source_title": title,
        "upstream_checked_at_utc": "2026-08-11T04:31:00Z",
        "upstream_status": "verified_open",
        "upstream_title": title,
        "rank_eligible": True,
        "execution_ready": True,
        "external_repository_mutated": False,
    }


def scan() -> dict:
    winner = candidate("winner", 100, 2, 1)
    other = candidate("other", 60, 3, 1)
    return {
        "checked_at_utc": "2026-08-11T04:32:00Z",
        "max_age_hours": 24,
        "selection_formula": (
            "reward_usd / (estimated_effort_hours * (1 + active_solvers))"
        ),
        "candidates": [winner, other],
        "selected_candidate_id": "winner",
        "execution_decision": "verified fixture",
        "external_repository_mutated": False,
    }


def demand_scan() -> dict:
    return {
        "checked_at_utc": "2026-08-11T04:32:00Z",
        "max_age_hours": 168,
        "lookback_days": 14,
        "scope_repository_count": 17,
        "search_query_count": 9,
        "qualification_threshold": 5,
        "qualifying_unique_issue_count": 1,
        "threshold_met": False,
        "manual_time_cost_over_30_minutes_verified": False,
        "demand_validated": False,
        "scope_exhaustive": False,
        "qualifying_issues": [
            {
                "url": "https://github.com/example/project/issues/1",
                "title": "Migration work before shutdown",
                "state": "open",
                "created_at_utc": "2026-08-10T17:19:16Z",
            }
        ],
        "inference_boundary": "selected public repositories only",
        "product_development_decision": (
            "freeze_additional_build_until_stronger_signal"
        ),
        "validation_record": "OPERATIONS/fixture.json",
        "external_repository_mutated": False,
        "external_cost_yen": 0,
    }


class DemandScanTest(unittest.TestCase):
    def assert_rejected(self, data: dict, fragment: str) -> None:
        errors = check_demand_scan(data, NOW)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_below_threshold_scan_passes_without_claiming_demand(self) -> None:
        self.assertEqual(check_demand_scan(demand_scan(), NOW), [])

    def test_count_must_match_unique_issue_list(self) -> None:
        data = demand_scan()
        data["qualifying_unique_issue_count"] = 2
        self.assert_rejected(data, "Issue件数と一致しない")

    def test_threshold_cannot_be_claimed_early(self) -> None:
        data = demand_scan()
        data["threshold_met"] = True
        self.assert_rejected(data, "再計算に一致しない")

    def test_deadline_alone_cannot_validate_demand(self) -> None:
        data = demand_scan()
        data["demand_validated"] = True
        self.assert_rejected(data, "件数基準と30分超作業の両方")

    def test_old_issue_cannot_count_in_recent_window(self) -> None:
        data = demand_scan()
        data["qualifying_issues"][0]["created_at_utc"] = "2026-07-20T00:00:00Z"
        self.assert_rejected(data, "直近lookback_daysの範囲外")

    def test_unvalidated_demand_freezes_additional_build(self) -> None:
        data = demand_scan()
        data["product_development_decision"] = "keep_building"
        self.assert_rejected(data, "追加開発をfreeze")

    def test_external_mutation_is_rejected_for_demand_scan(self) -> None:
        data = demand_scan()
        data["external_repository_mutated"] = True
        self.assert_rejected(data, "外部リポジトリを変更")


class BountyScanTest(unittest.TestCase):
    def assert_rejected(self, data: dict, fragment: str) -> None:
        errors = check_bounty_scan(data, NOW)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_verified_scan_passes(self) -> None:
        self.assertEqual(check_bounty_scan(scan(), NOW), [])

    def test_stale_scan_is_rejected(self) -> None:
        data = scan()
        data["checked_at_utc"] = "2026-08-09T04:32:00Z"
        self.assert_rejected(data, "候補測定が期限切れ")

    def test_wrong_score_is_rejected(self) -> None:
        data = scan()
        data["candidates"][0]["planning_score_usd_per_competition_adjusted_hour"] = 999
        self.assert_rejected(data, "記録スコア")

    def test_wrong_winner_is_rejected(self) -> None:
        data = scan()
        data["selected_candidate_id"] = "other"
        self.assert_rejected(data, "最高スコア候補")

    def test_external_mutation_is_rejected(self) -> None:
        data = scan()
        data["external_repository_mutated"] = True
        self.assert_rejected(data, "外部リポジトリを変更")

    def test_unverified_source_cannot_be_ranked(self) -> None:
        data = scan()
        data["candidates"][0]["source_status"] = "unverified"
        self.assert_rejected(data, "Opireのopen確認")

    def test_title_mismatch_is_rejected(self) -> None:
        data = scan()
        data["candidates"][0]["upstream_title"] = "Different title"
        self.assert_rejected(data, "上流 Issue と候補の title")

    def test_maintainer_rejection_cannot_be_ranked(self) -> None:
        data = scan()
        data["candidates"][0]["upstream_status"] = (
            "verified_open_but_community_prs_rejected"
        )
        self.assert_rejected(data, "上流Issueのopen確認")

    def test_stale_per_source_measurement_is_rejected(self) -> None:
        data = scan()
        data["candidates"][0]["upstream_checked_at_utc"] = "2026-08-09T04:31:00Z"
        self.assert_rejected(data, "upstream_checked_at_utc が期限切れ")

    def test_non_ready_selection_requires_fallback(self) -> None:
        data = scan()
        data["candidates"][0]["execution_ready"] = False
        self.assert_rejected(data, "fallback_option_id")

    def test_no_rankable_candidate_requires_and_accepts_fallback(self) -> None:
        data = scan()
        for item in data["candidates"]:
            item["rank_eligible"] = False
            item["execution_ready"] = False
            item["upstream_status"] = "unverified"
            item["upstream_title"] = None
            item["rejection_reason"] = "upstream could not be independently verified"
        data["selected_candidate_id"] = None
        data["fallback_option_id"] = "demand_first_micro_product"
        self.assertEqual(check_bounty_scan(
            data,
            NOW,
            valid_fallback_ids={"demand_first_micro_product"},
        ), [])

    def test_unknown_fallback_is_rejected(self) -> None:
        data = scan()
        for item in data["candidates"]:
            item["rank_eligible"] = False
            item["execution_ready"] = False
            item["upstream_status"] = "unverified"
            item["upstream_title"] = None
            item["rejection_reason"] = "upstream could not be independently verified"
        data["selected_candidate_id"] = None
        data["fallback_option_id"] = "invented_option"
        errors = check_bounty_scan(
            data,
            NOW,
            valid_fallback_ids={"demand_first_micro_product"},
        )
        self.assertTrue(any("登録済みの非既存案" in error for error in errors), errors)


    def test_naive_top_level_timestamp_is_rejected_without_exception(self) -> None:
        data = scan()
        data["checked_at_utc"] = "2026-08-11T04:32:00"
        self.assert_rejected(data, "checked_at_utc はタイムゾーン付き日時")

    def test_naive_candidate_timestamps_are_rejected_without_exception(self) -> None:
        for field in ("source_checked_at_utc", "upstream_checked_at_utc"):
            with self.subTest(field=field):
                data = scan()
                data["candidates"][0][field] = "2026-08-11T04:32:00"
                self.assert_rejected(
                    data,
                    f"{field} はタイムゾーン付き日時",
                )

    def test_future_top_level_timestamp_is_rejected(self) -> None:
        data = scan()
        data["checked_at_utc"] = "2026-08-11T04:43:01Z"
        self.assert_rejected(data, "checked_at_utc が現在時刻より3分を超えて未来")

    def test_future_candidate_timestamps_are_rejected(self) -> None:
        for field in ("source_checked_at_utc", "upstream_checked_at_utc"):
            with self.subTest(field=field):
                data = scan()
                data["candidates"][0][field] = "2026-08-11T04:43:01Z"
                self.assert_rejected(
                    data,
                    f"{field} が現在時刻より3分を超えて未来",
                )

    def test_exact_three_minute_clock_skew_is_allowed(self) -> None:
        data = scan()
        data["checked_at_utc"] = "2026-08-11T04:43:00Z"
        for item in data["candidates"]:
            item["source_checked_at_utc"] = "2026-08-11T04:43:00Z"
            item["upstream_checked_at_utc"] = "2026-08-11T04:43:00Z"
        self.assertEqual(check_bounty_scan(data, NOW), [])


if __name__ == "__main__":
    unittest.main()
