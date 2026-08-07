#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "automation_continuity.json"
CURRENT = ROOT / "state" / "current.json"
CONTROL = ROOT / "state" / "continuation_control.json"
POLICY = ROOT / "OPERATIONS" / "ASSISTANT_OPERATING_POLICY.md"
AGENTS = ROOT / "AGENTS.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    state = load(STATE)
    current = load(CURRENT)
    control = load(CONTROL)
    policy = POLICY.read_text(encoding="utf-8")
    agents = AGENTS.read_text(encoding="utf-8")

    if state.get("classification") != "assistant_operational_state_not_permanent_directive":
        errors.append("continuity_state_classification_invalid")
    if state.get("status") not in {"active_two_layer_verified", "merged_main_remote_ci_validated"}:
        errors.append("continuity_state_not_active")
    if state.get("stop_condition") != "explicit_user_instruction_to_stop_or_end_project_only":
        errors.append("explicit_stop_contract_missing")

    required_non_stop = {
        "no_new_user_message",
        "user_does_not_read_a_response",
        "user_only_authentication_or_publication_wait",
        "one_work_unit_completed",
        "one_run_has_no_reportable_change",
        "temporary_external_or_tool_failure",
    }
    if not required_non_stop.issubset(set(state.get("non_stop_conditions", []))):
        errors.append("non_stop_conditions_incomplete")

    for key, title in (
        ("primary", "収益プロジェクト継続"),
        ("watchdog", "収益タスク監視"),
    ):
        item = state.get(key, {})
        if item.get("title") != title:
            errors.append(f"{key}_title_invalid")
        if item.get("observed_enabled") is not True:
            errors.append(f"{key}_not_observed_enabled")
        if "RRULE:FREQ=HOURLY" not in str(item.get("schedule", "")):
            errors.append(f"{key}_not_hourly")
        if item.get("timezone") != "Asia/Tokyo":
            errors.append(f"{key}_timezone_invalid")

    live = state.get("live_observation", {})
    if live.get("primary_enabled") is not True or live.get("watchdog_enabled") is not True:
        errors.append("live_enabled_observation_missing")
    if live.get("paused_count") != 0:
        errors.append("paused_automation_observed")

    automation = current.get("automation", {})
    if automation.get("revenue_continuation") not in {
        "active_two_layer_verified",
        "merged_main_remote_ci_validated",
    }:
        errors.append("current_continuity_status_invalid")
    if automation.get("automation_continuity_state") != "state/automation_continuity.json":
        errors.append("current_continuity_pointer_missing")

    unit = next(
        (item for item in control.get("active_work_units", []) if item.get("id") == "automation_continuity_v1"),
        None,
    )
    if not unit:
        errors.append("continuation_work_unit_missing")
    elif unit.get("assistant_executable") is not True or unit.get("user_blocked") is not False:
        errors.append("continuation_work_unit_boundary_invalid")

    for phrase in (
        "ユーザーの明示停止だけを停止条件",
        "通知だけを省略",
        "独立した監視タスク",
        "自動で再開",
    ):
        if phrase not in policy:
            errors.append(f"policy_phrase_missing:{phrase}")
    for phrase in (
        "state/automation_continuity.json",
        "定期実行の有効状態",
        "明示的な停止指示",
        "再開を試みる",
    ):
        if phrase not in agents:
            errors.append(f"agents_phrase_missing:{phrase}")

    payload = {"ok": not errors, "errors": errors}
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
