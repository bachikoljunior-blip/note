#!/usr/bin/env python3
"""改善効果窓を判断時刻の前後でfail-closedに検査する。"""
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from check_loops import check_loop


NOW = datetime(2026, 8, 11, 5, 0, tzinfo=timezone.utc)


def loop_fixture() -> dict:
    return {
        "id": "effect_window_fixture",
        "metric": "fixture",
        "how_to_measure": "fixed-clock fixture",
        "current": 0,
        "measured_at": "2026-08-11T04:30:00Z",
        "max_age_hours": 24,
        "target": 1,
        "consecutive_no_move": 0,
        "owner_actions_required": 0,
        "consumer": "test",
        "latest_observation": {
            "decision_not_before_utc": "2026-08-11T04:00:00Z",
            "observed_at_utc": "2026-08-11T04:30:00Z",
            "effect_window_elapsed": True,
            "performance_conclusion_allowed": True,
        },
    }


class EffectWindowTest(unittest.TestCase):
    def assert_rejected(self, data: dict, fragment: str) -> None:
        errors = check_loop(data, NOW)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_due_window_with_current_observation_passes(self) -> None:
        self.assertEqual(check_loop(loop_fixture(), NOW), [])

    def test_due_window_cannot_remain_pre_effect(self) -> None:
        data = loop_fixture()
        data["latest_observation"]["effect_window_elapsed"] = False
        self.assert_rejected(data, "decision_not_before_utc を過ぎた")

    def test_future_window_can_remain_pre_effect(self) -> None:
        data = loop_fixture()
        data["latest_observation"]["decision_not_before_utc"] = (
            "2026-08-11T06:00:00Z"
        )
        data["latest_observation"]["effect_window_elapsed"] = False
        data["latest_observation"]["performance_conclusion_allowed"] = False
        self.assertEqual(check_loop(data, NOW), [])

    def test_future_window_cannot_be_claimed_elapsed(self) -> None:
        data = loop_fixture()
        data["latest_observation"]["decision_not_before_utc"] = (
            "2026-08-11T06:00:00Z"
        )
        self.assert_rejected(data, "効果窓を先取り")

    def test_decision_timestamp_requires_timezone(self) -> None:
        data = loop_fixture()
        data["latest_observation"]["decision_not_before_utc"] = (
            "2026-08-11T04:00:00"
        )
        self.assert_rejected(data, "タイムゾーン付き日時")


    def test_elapsed_window_requires_post_deadline_observation(self) -> None:
        data = loop_fixture()
        data["latest_observation"]["observed_at_utc"] = "2026-08-11T03:59:59Z"
        self.assert_rejected(data, "latest_observation.observed_at_utc が decision_not_before_utc より前")

    def test_elapsed_window_requires_post_deadline_loop_measurement(self) -> None:
        data = loop_fixture()
        data["measured_at"] = "2026-08-11T03:59:59Z"
        self.assert_rejected(data, "loop.measured_at が decision_not_before_utc より前")

    def test_conclusion_cannot_precede_effect_window(self) -> None:
        data = loop_fixture()
        data["latest_observation"]["decision_not_before_utc"] = (
            "2026-08-11T06:00:00Z"
        )
        data["latest_observation"]["effect_window_elapsed"] = False
        data["latest_observation"]["performance_conclusion_allowed"] = True
        self.assert_rejected(
            data,
            "performance_conclusion_allowed=true",
        )


    def test_conclusion_flag_requires_boolean(self) -> None:
        data = loop_fixture()
        data["latest_observation"]["performance_conclusion_allowed"] = "yes"
        self.assert_rejected(data, "performance_conclusion_allowed は真偽値")


if __name__ == "__main__":
    unittest.main()
