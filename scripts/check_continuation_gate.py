#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "continuation_gate.json"
DEFAULT_CONTROL = ROOT / "state" / "continuation_control.json"
DEFAULT_CURRENT = ROOT / "state" / "current.json"
DEFAULT_POLICY = ROOT / "OPERATIONS" / "ASSISTANT_OPERATING_POLICY.md"
DEFAULT_AGENTS = ROOT / "AGENTS.md"
REPORT = ROOT / "reports" / "continuation_gate.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_data(
    config: dict[str, Any],
    control: dict[str, Any],
    current: dict[str, Any],
    policy_text: str,
    agents_text: str,
) -> list[str]:
    errors: list[str] = []

    if config.get("classification") != "assistant_created_mutable_policy_not_permanent_directive":
        errors.append("config_classification_invalid")
    if control.get("classification") != "assistant_operational_state_not_permanent_directive":
        errors.append("control_classification_invalid")

    target = config.get("mission_target_monthly_yen")
    if target != 200000:
        errors.append("mission_target_must_be_200000")
    if control.get("mission_target_monthly_yen") != target:
        errors.append("control_target_mismatch")
    if current.get("revenue_target", {}).get("target_monthly_yen") != target:
        errors.append("current_target_mismatch")
    if control.get("mission_status") != current.get("mission_status"):
        errors.append("mission_status_mismatch")
    if control.get("verified_monthly_revenue_yen") != current.get("revenue_target", {}).get(
        "current_verified_monthly_yen"
    ):
        errors.append("verified_revenue_mismatch")

    termination = config.get("project_termination_conditions")
    if termination != ["explicit_user_instruction_to_end_project"]:
        errors.append("project_termination_must_require_explicit_user_end")
    explicit_end = control.get("explicit_user_end_received") is True
    if control.get("project_status") == "stopped" and not explicit_end:
        errors.append("project_stopped_without_explicit_user_end")
    if not explicit_end and control.get("project_status") not in {"continue", "blocked_monitoring"}:
        errors.append("project_status_must_remain_continuing")

    required_horizons = config.get("required_search_horizons")
    evaluations = control.get("search_horizon_evaluation")
    if not isinstance(required_horizons, list) or len(required_horizons) < 5:
        errors.append("at_least_five_search_horizons_required")
        required_horizons = []
    if not isinstance(evaluations, dict):
        errors.append("search_horizon_evaluation_missing")
        evaluations = {}
    if set(evaluations) != set(required_horizons):
        errors.append("search_horizon_set_mismatch")
    for horizon in required_horizons:
        item = evaluations.get(horizon)
        if not isinstance(item, dict) or item.get("evaluated") is not True or not item.get("result"):
            errors.append(f"search_horizon_not_evaluated:{horizon}")

    yield_gate = config.get("yield_gate", {})
    if yield_gate.get("user_only_blocker_is_global_stop") is not False:
        errors.append("user_only_blocker_must_not_be_global_stop")
    if yield_gate.get("independent_work_continues_while_user_blocked") is not True:
        errors.append("independent_work_continuation_required")
    if control.get("user_authentication_pending_is_global_stop") is not False:
        errors.append("authentication_wait_must_not_be_global_stop")

    auth_gate = config.get("authentication_handoff_gate", {})
    if auth_gate.get("silent_indefinite_deferral_forbidden") is not True:
        errors.append("silent_authentication_deferral_must_be_forbidden")
    if auth_gate.get("resume_same_workstream_after_completion_signal") is not True:
        errors.append("authentication_workstream_must_resume_after_completion")
    if auth_gate.get("expiring_code_may_be_issued_only_when_user_present") is not True:
        errors.append("expiring_auth_code_presence_guard_required")
    required_handoff_fields = set(auth_gate.get("required_fields", []))
    if required_handoff_fields != {
        "target_site", "exact_user_action", "secret_handling", "completion_signal"
    }:
        errors.append("authentication_handoff_required_fields_invalid")

    user_present = control.get("user_presence", {}).get("observed_active_in_current_turn") is True
    auth_blocked = any(
        isinstance(item, dict)
        and item.get("user_blocked") is True
        and "authentication" in str(item.get("status", ""))
        for item in control.get("active_work_units", [])
    )
    handoff = control.get("authentication_handoff", {})
    if user_present and auth_blocked:
        if handoff.get("status") not in {
            "website_login_steps_presented_awaiting_user_completion",
            "device_authorization_presented_awaiting_user_completion",
            "user_completion_reported_resuming",
            "completed",
        }:
            errors.append("active_user_authentication_handoff_not_presented")
        for field in required_handoff_fields:
            if not handoff.get(field):
                errors.append(f"authentication_handoff_field_missing:{field}")
    if handoff.get("expiring_code_issued") is True and not user_present:
        errors.append("expiring_auth_code_issued_without_active_user")

    capacity = control.get("capacity", {})
    current_capacity = current.get("operating_context", {}).get("chatgpt_work_capacity", {})
    if capacity.get("remaining_percent") != current_capacity.get("remaining_percent"):
        errors.append("capacity_remaining_percent_mismatch")
    if capacity.get("resets_at") != current_capacity.get("resets_at"):
        errors.append("capacity_reset_mismatch")
    threshold = config.get("capacity_policy", {}).get("remaining_percent_at_or_above")
    if isinstance(capacity.get("remaining_percent"), (int, float)) and isinstance(threshold, (int, float)):
        if capacity["remaining_percent"] >= threshold and capacity.get("strategy") != config.get(
            "capacity_policy", {}
        ).get("mode"):
            errors.append("available_capacity_strategy_invalid")

    work_units = control.get("active_work_units")
    if not isinstance(work_units, list) or not work_units:
        errors.append("active_work_units_required")
        work_units = []
    for item in work_units:
        if not isinstance(item, dict) or not isinstance(item.get("actionable_now"), bool):
            errors.append("work_unit_actionable_now_required")
    actionable = [
        item
        for item in work_units
        if isinstance(item, dict)
        and item.get("actionable_now") is True
        and item.get("assistant_executable") is True
        and item.get("user_blocked") is not True
    ]
    if actionable and control.get("latest_decision") != "continue":
        errors.append("actionable_work_requires_continue_decision")
    if actionable and control.get("yield_requested") is True:
        errors.append("yield_forbidden_while_actionable_work_exists")
    if control.get("yield_requested") is True and control.get("next_automation_verified") is not True:
        errors.append("yield_requires_verified_next_automation")

    required_non_termination = {
        "assistant_turn_or_response_completed",
        "user_absent_or_may_not_read",
        "user_authentication_or_final_publish_pending",
        "temporary_tool_or_external_service_failure",
        "mission_target_reached_switches_to_maintenance",
    }
    if not required_non_termination.issubset(set(config.get("non_termination_conditions", []))):
        errors.append("non_termination_conditions_incomplete")

    for phrase in (
        "プロジェクト全体の停止と誤認しない",
        "本人操作待ちは対象作業だけのブロッカー",
        "5経路をすべて評価",
        "残量を無意味に消費すること自体は目標にしない",
        "認証依頼を無期限に先送りしない",
    ):
        if phrase not in policy_text:
            errors.append(f"assistant_policy_continuation_phrase_missing:{phrase}")
    for phrase in (
        "OPERATIONS/CONTINUATION_GATE.md",
        "scripts/check_continuation_gate.py",
        "state/continuation_control.json",
        "Do not silently defer it",
    ):
        if phrase not in agents_text:
            errors.append(f"agents_continuation_pointer_missing:{phrase}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--control", type=Path, default=DEFAULT_CONTROL)
    parser.add_argument("--current", type=Path, default=DEFAULT_CURRENT)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--agents", type=Path, default=DEFAULT_AGENTS)
    args = parser.parse_args()

    errors: list[str] = []
    try:
        config = load_json(args.config)
        control = load_json(args.control)
        current = load_json(args.current)
        policy_text = args.policy.read_text(encoding="utf-8")
        agents_text = args.agents.read_text(encoding="utf-8")
        errors = validate_data(config, control, current, policy_text, agents_text)
    except Exception as exc:  # noqa: BLE001
        errors = [f"continuation_gate_exception:{type(exc).__name__}:{exc}"]

    payload = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": str(args.config.relative_to(ROOT)) if args.config.is_relative_to(ROOT) else str(args.config),
        "control": str(args.control.relative_to(ROOT)) if args.control.is_relative_to(ROOT) else str(args.control),
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
