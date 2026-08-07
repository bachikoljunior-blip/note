#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_continuation_gate import validate_data  # noqa: E402


def load(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def expect_error(
    name: str,
    config: dict[str, object],
    control: dict[str, object],
    current: dict[str, object],
    policy: str,
    agents: str,
    expected: str,
) -> dict[str, object]:
    errors = validate_data(config, control, current, policy, agents)
    return {"name": name, "ok": expected in errors, "errors": errors}


def main() -> int:
    config = load("config/continuation_gate.json")
    control = load("state/continuation_control.json")
    current = load("state/current.json")
    policy = (ROOT / "OPERATIONS/ASSISTANT_OPERATING_POLICY.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    tests: list[dict[str, object]] = []

    baseline = validate_data(config, control, current, policy, agents)
    tests.append({"name": "canonical_configuration_passes", "ok": not baseline, "errors": baseline})

    candidate = copy.deepcopy(control)
    candidate["project_status"] = "stopped"
    tests.append(expect_error(
        "stopping_without_explicit_user_end_is_rejected",
        config, candidate, current, policy, agents,
        "project_stopped_without_explicit_user_end",
    ))

    candidate = copy.deepcopy(control)
    candidate["search_horizon_evaluation"].pop("new_product_pricing_and_channel_expansion")
    tests.append(expect_error(
        "missing_search_horizon_is_rejected",
        config, candidate, current, policy, agents,
        "search_horizon_set_mismatch",
    ))

    candidate = copy.deepcopy(control)
    candidate["user_authentication_pending_is_global_stop"] = True
    tests.append(expect_error(
        "authentication_wait_cannot_stop_project",
        config, candidate, current, policy, agents,
        "authentication_wait_must_not_be_global_stop",
    ))

    candidate = copy.deepcopy(control)
    candidate["authentication_handoff"]["status"] = "not_presented"
    tests.append(expect_error(
        "active_user_authentication_handoff_is_required",
        config, candidate, current, policy, agents,
        "active_user_authentication_handoff_not_presented",
    ))

    candidate = copy.deepcopy(control)
    candidate["user_presence"]["observed_active_in_current_turn"] = False
    candidate["authentication_handoff"]["expiring_code_issued"] = True
    tests.append(expect_error(
        "expiring_code_without_active_user_is_rejected",
        config, candidate, current, policy, agents,
        "expiring_auth_code_issued_without_active_user",
    ))

    candidate_config = copy.deepcopy(config)
    candidate_config["authentication_handoff_gate"]["resume_same_workstream_after_completion_signal"] = False
    tests.append(expect_error(
        "authentication_workstream_resume_is_required",
        candidate_config, control, current, policy, agents,
        "authentication_workstream_must_resume_after_completion",
    ))

    candidate = copy.deepcopy(control)
    candidate["capacity"]["strategy"] = "ignore"
    tests.append(expect_error(
        "available_capacity_cannot_be_ignored",
        config, candidate, current, policy, agents,
        "available_capacity_strategy_invalid",
    ))

    candidate = copy.deepcopy(control)
    candidate["yield_requested"] = True
    candidate["latest_decision"] = "yield"
    tests.append(expect_error(
        "yield_while_actionable_work_exists_is_rejected",
        config, candidate, current, policy, agents,
        "yield_forbidden_while_actionable_work_exists",
    ))

    candidate = copy.deepcopy(control)
    candidate["yield_requested"] = True
    candidate["next_automation_verified"] = False
    candidate["active_work_units"] = [
        {"id": "future", "status": "future_trigger_verified", "assistant_executable": False, "user_blocked": False}
    ]
    tests.append(expect_error(
        "yield_without_verified_continuation_is_rejected",
        config, candidate, current, policy, agents,
        "yield_requires_verified_next_automation",
    ))

    failures = [item["name"] for item in tests if not item["ok"]]
    payload = {"ok": not failures, "tests": tests, "failures": failures}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
