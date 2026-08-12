#!/usr/bin/env python3
from __future__ import annotations

import json
import re
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
    if state.get("status") not in {
        "active_two_layer_configuration_verified_runtime_pending",
        "active_two_layer_runtime_verified",
        "merged_main_remote_ci_validated",
    }:
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

    for key, title, minute in (
        ("primary", "月20万円最短実行", "20"),
        ("watchdog", "月20万円継続監視", "35"),
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
        if item.get("destination_mode") != "standalone":
            errors.append(f"{key}_destination_not_standalone")
        if item.get("creation_readback_conversation_id_null") is not True:
            errors.append(f"{key}_standalone_creation_readback_missing")
        if item.get("conversation_id_after_run_is_not_failure_by_itself") is not True:
            errors.append(f"{key}_conversation_id_semantics_missing")
        match = re.search(r"DTSTART:\d{8}T\d{2}(\d{2})00", str(item.get("schedule", "")))
        if not match or match.group(1) != minute:
            errors.append(f"{key}_schedule_minute_invalid")

    live = state.get("live_observation", {})
    if live.get("primary_enabled") is not True or live.get("watchdog_enabled") is not True:
        errors.append("live_enabled_observation_missing")
    if live.get("active_primary_count") != 1 or live.get("active_watchdog_count") != 1:
        errors.append("active_task_count_invalid")
    if live.get("superseded_versions_enabled") != 0:
        errors.append("superseded_continuity_task_still_enabled")
    if live.get("next_run_time_null_is_failure") is not False:
        errors.append("unsupported_next_run_field_must_not_trigger_repair")

    evidence = state.get("runtime_evidence", {})
    if evidence.get("status") not in {"pending_first_new_run", "verified"}:
        errors.append("runtime_evidence_status_invalid")
    if evidence.get("status") == "pending_first_new_run":
        if evidence.get("compliance_pass") is not False:
            errors.append("pending_runtime_evidence_cannot_pass")
        if not evidence.get("unresolved_correctable_issues"):
            errors.append("pending_runtime_gap_must_be_recorded")
    else:
        required_runtime = {
            "run_started_at", "run_ended_at", "completed_units", "end_reason_code",
            "early_stop_violation", "audit_iterations", "issues_found", "issues_fixed",
            "unresolved_correctable_issues", "residual_external_risks", "compliance_pass",
        }
        if not required_runtime.issubset(evidence):
            errors.append("verified_runtime_evidence_fields_missing")
        if evidence.get("compliance_pass") is True and evidence.get("unresolved_correctable_issues"):
            errors.append("runtime_pass_with_unresolved_correctable_issue")

    audit = state.get("fixed_point_audit_contract", {})
    required_audit_fields = {
        "audit_iterations", "issues_found", "issues_fixed",
        "unresolved_correctable_issues", "residual_external_risks", "compliance_pass",
    }
    if set(audit.get("required_fields", [])) != required_audit_fields:
        errors.append("fixed_point_audit_fields_invalid")
    if audit.get("pass_requires_zero_correctable_issues") is not True:
        errors.append("fixed_point_zero_correctable_gate_missing")
    if audit.get("all_residual_risks_require_detection_and_recovery") is not True:
        errors.append("fixed_point_residual_risk_gate_missing")

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
