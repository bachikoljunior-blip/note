#!/usr/bin/env python3
"""有償Issue測定が片側だけの観測や古い値で通らないことを固定時刻で検証する。"""
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from check_options import check_bounty_scan


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


if __name__ == "__main__":
    unittest.main()
