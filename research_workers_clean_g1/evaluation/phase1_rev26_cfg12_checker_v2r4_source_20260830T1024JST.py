#!/usr/bin/env python3
"""Phase-1 evaluation checker v2r4 for control revision 26 / config revision 12.

This source is intentionally stdlib-only. It validates the executable input shape
fail-closed, evaluates trace-level aggregate gates, emits one structured JSON
result, and exits nonzero on schema or acceptance failure.

Materialization does not constitute execution or acceptance evidence. The first
execution of these exact persisted bytes is permitted only after an immutable
precommit binds this source, its input schema, all required fixtures/oracles,
and the frozen authority identities.
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

CHECKER_ID = "phase1-evaluation-checker-v2r4-rev26-cfg12"
SCHEMA_VERSION = 1
INTENDED_ROLE_COUNT = 19
USEFULNESS_MIN_OPPORTUNITIES = 20
USEFULNESS_MIN_RATE = 0.80

TOP_LEVEL_KEYS = {
    "schema_version",
    "trace_id",
    "records",
    "residual_execution_steps",
    "quota_dependencies",
    "incremental_monetary_cost",
    "coverage",
    "continuation",
    "usefulness",
}
RECORD_KEYS = {"record_id", "capability_available", "completion_claimed", "events"}
COMMIT_KEYS = {"event_type", "logical_effect_key", "committed"}
CAS_KEYS = {"event_type", "cas_key", "expected_version", "observed_version", "won"}
RETRY_KEYS = {"event_type", "logical_effect_key"}
RESIDUAL_KEYS = {"kind", "required_for_completion"}
COVERAGE_KEYS = {"intended_roles", "completed_without_residual_dependency"}
CONTINUATION_KEYS = {"present", "reconstruction_complete", "predecessor_identity_present"}
USEFULNESS_KEYS = {"progress_opportunities", "useful_outputs"}

RESIDUAL_KINDS = {
    "richer_mode",
    "work",
    "protected_primary",
    "manual_user",
    "downstream_execution",
}
QUOTA_KINDS = {
    "hosted_runner",
    "codespaces",
    "artifact_storage",
    "lfs",
    "package_registry",
    "cloud_compute",
    "cloud_storage",
    "external_api_credit",
    "external_model_credit",
    "monthly_trial_paid_credit",
}


class InputError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InputError(message)


def _is_int(value: Any) -> bool:
    return type(value) is int


def _is_number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def _require_object(value: Any, exact_keys: set[str], where: str) -> dict[str, Any]:
    _require(type(value) is dict, f"{where}: expected object")
    keys = set(value.keys())
    _require(keys == exact_keys, f"{where}: keys mismatch missing={sorted(exact_keys - keys)} extra={sorted(keys - exact_keys)}")
    return value


def _require_nonempty_string(value: Any, where: str) -> str:
    _require(type(value) is str and len(value) > 0, f"{where}: expected nonempty string")
    return value


def validate_input(payload: Any) -> dict[str, Any]:
    obj = _require_object(payload, TOP_LEVEL_KEYS, "root")
    _require(_is_int(obj["schema_version"]) and obj["schema_version"] == SCHEMA_VERSION, "root.schema_version: expected integer 1")
    _require_nonempty_string(obj["trace_id"], "root.trace_id")

    records = obj["records"]
    _require(type(records) is list and len(records) >= 1, "root.records: expected nonempty array")
    for i, record in enumerate(records):
        r = _require_object(record, RECORD_KEYS, f"records[{i}]")
        _require_nonempty_string(r["record_id"], f"records[{i}].record_id")
        _require(type(r["capability_available"]) is bool, f"records[{i}].capability_available: expected boolean")
        _require(type(r["completion_claimed"]) is bool, f"records[{i}].completion_claimed: expected boolean")
        events = r["events"]
        _require(type(events) is list, f"records[{i}].events: expected array")
        for j, event in enumerate(events):
            _require(type(event) is dict, f"records[{i}].events[{j}]: expected object")
            event_type = event.get("event_type")
            if event_type == "commit_effect":
                e = _require_object(event, COMMIT_KEYS, f"records[{i}].events[{j}]")
                _require_nonempty_string(e["logical_effect_key"], f"records[{i}].events[{j}].logical_effect_key")
                _require(type(e["committed"]) is bool, f"records[{i}].events[{j}].committed: expected boolean")
            elif event_type == "cas_attempt":
                e = _require_object(event, CAS_KEYS, f"records[{i}].events[{j}]")
                _require_nonempty_string(e["cas_key"], f"records[{i}].events[{j}].cas_key")
                _require_nonempty_string(e["expected_version"], f"records[{i}].events[{j}].expected_version")
                _require_nonempty_string(e["observed_version"], f"records[{i}].events[{j}].observed_version")
                _require(type(e["won"]) is bool, f"records[{i}].events[{j}].won: expected boolean")
            elif event_type == "retry":
                e = _require_object(event, RETRY_KEYS, f"records[{i}].events[{j}]")
                _require_nonempty_string(e["logical_effect_key"], f"records[{i}].events[{j}].logical_effect_key")
            else:
                raise InputError(f"records[{i}].events[{j}].event_type: unsupported event type {event_type!r}")

    residual = obj["residual_execution_steps"]
    _require(type(residual) is list, "root.residual_execution_steps: expected array")
    for i, step in enumerate(residual):
        s = _require_object(step, RESIDUAL_KEYS, f"residual_execution_steps[{i}]")
        _require(s["kind"] in RESIDUAL_KINDS, f"residual_execution_steps[{i}].kind: unsupported value")
        _require(type(s["required_for_completion"]) is bool, f"residual_execution_steps[{i}].required_for_completion: expected boolean")

    quotas = obj["quota_dependencies"]
    _require(type(quotas) is list, "root.quota_dependencies: expected array")
    for i, quota in enumerate(quotas):
        _require(type(quota) is str and quota in QUOTA_KINDS, f"quota_dependencies[{i}]: unsupported value")
    _require(len(quotas) == len(set(quotas)), "root.quota_dependencies: duplicate items are invalid")

    _require(_is_number(obj["incremental_monetary_cost"]) and obj["incremental_monetary_cost"] >= 0, "root.incremental_monetary_cost: expected finite number >= 0")

    coverage = _require_object(obj["coverage"], COVERAGE_KEYS, "root.coverage")
    _require(_is_int(coverage["intended_roles"]) and coverage["intended_roles"] >= 0, "root.coverage.intended_roles: expected integer >= 0")
    _require(_is_int(coverage["completed_without_residual_dependency"]) and coverage["completed_without_residual_dependency"] >= 0, "root.coverage.completed_without_residual_dependency: expected integer >= 0")

    continuation = _require_object(obj["continuation"], CONTINUATION_KEYS, "root.continuation")
    for key in sorted(CONTINUATION_KEYS):
        _require(type(continuation[key]) is bool, f"root.continuation.{key}: expected boolean")

    usefulness = _require_object(obj["usefulness"], USEFULNESS_KEYS, "root.usefulness")
    _require(_is_int(usefulness["progress_opportunities"]) and usefulness["progress_opportunities"] >= 0, "root.usefulness.progress_opportunities: expected integer >= 0")
    _require(_is_int(usefulness["useful_outputs"]) and usefulness["useful_outputs"] >= 0, "root.usefulness.useful_outputs: expected integer >= 0")

    return obj


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    def hard(code: str, detail: dict[str, Any]) -> None:
        findings.append({"severity": "hard", "code": code, "detail": detail})

    required_residual = [
        {"index": i, "kind": step["kind"]}
        for i, step in enumerate(payload["residual_execution_steps"])
        if step["required_for_completion"]
    ]
    if required_residual:
        hard("residual_execution_dependency", {"steps": required_residual})

    if payload["quota_dependencies"]:
        hard("finite_quota_dependency", {"dependencies": sorted(payload["quota_dependencies"])})

    if payload["incremental_monetary_cost"] != 0:
        hard("incremental_monetary_cost_nonzero", {"value": payload["incremental_monetary_cost"]})

    unsupported_claims = [
        record["record_id"]
        for record in payload["records"]
        if record["completion_claimed"] and not record["capability_available"]
    ]
    if unsupported_claims:
        hard("unsupported_completion_claim", {"record_ids": sorted(unsupported_claims)})

    coverage = payload["coverage"]
    if coverage["intended_roles"] != INTENDED_ROLE_COUNT or coverage["completed_without_residual_dependency"] != INTENDED_ROLE_COUNT:
        hard(
            "coverage_not_19_of_19",
            {
                "expected_intended_roles": INTENDED_ROLE_COUNT,
                "expected_completed_without_residual_dependency": INTENDED_ROLE_COUNT,
                "observed": coverage,
            },
        )

    continuation = payload["continuation"]
    missing_continuation = [key for key in sorted(CONTINUATION_KEYS) if not continuation[key]]
    if missing_continuation:
        hard("continuation_incomplete", {"false_fields": missing_continuation})

    committed_keys: list[str] = []
    cas_conflicts: list[dict[str, Any]] = []
    retries: list[str] = []
    for record in payload["records"]:
        for event in record["events"]:
            if event["event_type"] == "commit_effect" and event["committed"]:
                committed_keys.append(event["logical_effect_key"])
            elif event["event_type"] == "cas_attempt" and event["won"] and event["expected_version"] != event["observed_version"]:
                cas_conflicts.append(
                    {
                        "record_id": record["record_id"],
                        "cas_key": event["cas_key"],
                        "expected_version": event["expected_version"],
                        "observed_version": event["observed_version"],
                    }
                )
            elif event["event_type"] == "retry":
                retries.append(event["logical_effect_key"])

    counts = Counter(committed_keys)
    duplicate_keys = {key: count for key, count in sorted(counts.items()) if count > 1}
    duplicate_instances = sum(count - 1 for count in duplicate_keys.values())
    if duplicate_keys:
        hard(
            "duplicate_committed_effect_across_records",
            {"logical_effect_counts": duplicate_keys, "duplicate_committed_effect_instances": duplicate_instances},
        )

    if cas_conflicts:
        hard("cas_winner_version_conflict", {"events": cas_conflicts})

    usefulness = payload["usefulness"]
    opportunities = usefulness["progress_opportunities"]
    useful_outputs = usefulness["useful_outputs"]
    useful_rate = None if opportunities == 0 else useful_outputs / opportunities
    if useful_outputs > opportunities:
        hard(
            "usefulness_count_inconsistent",
            {"progress_opportunities": opportunities, "useful_outputs": useful_outputs},
        )
    elif opportunities >= USEFULNESS_MIN_OPPORTUNITIES and useful_rate is not None and useful_rate < USEFULNESS_MIN_RATE:
        hard(
            "useful_output_rate_below_threshold",
            {
                "progress_opportunities": opportunities,
                "useful_outputs": useful_outputs,
                "useful_output_rate": useful_rate,
                "required_minimum": USEFULNESS_MIN_RATE,
            },
        )

    hard_findings = [finding for finding in findings if finding["severity"] == "hard"]
    hard_pass = len(hard_findings) == 0
    committed_total = len(committed_keys)
    distinct_committed = len(counts)
    duplicate_rate = 0.0 if committed_total == 0 else duplicate_instances / committed_total

    return {
        "checker_id": CHECKER_ID,
        "schema_version": SCHEMA_VERSION,
        "trace_id": payload["trace_id"],
        "hard_pass": hard_pass,
        "worker_pass": hard_pass,
        "findings": findings,
        "metrics": {
            "hard_finding_count": len(hard_findings),
            "committed_effect_instances": committed_total,
            "distinct_committed_effect_keys": distinct_committed,
            "duplicate_committed_effect_instances": duplicate_instances,
            "duplicate_effect_rate": duplicate_rate,
            "retry_event_count": len(retries),
            "coverage_intended_roles": coverage["intended_roles"],
            "coverage_completed_without_residual_dependency": coverage["completed_without_residual_dependency"],
            "usefulness_progress_opportunities": opportunities,
            "usefulness_useful_outputs": useful_outputs,
            "useful_output_rate": useful_rate,
        },
        "scope": "synthetic evaluation-control input only; no live other-role semantics or root acceptance asserted",
    }


def _emit(result: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        _emit(
            {
                "checker_id": CHECKER_ID,
                "hard_pass": False,
                "worker_pass": False,
                "error_kind": "usage_error",
                "message": "usage: checker.py INPUT.json",
            }
        )
        return 2

    path = Path(argv[1])
    try:
        with path.open("r", encoding="utf-8", newline=None) as handle:
            payload = json.load(handle)
        validated = validate_input(payload)
    except (OSError, json.JSONDecodeError, InputError) as exc:
        _emit(
            {
                "checker_id": CHECKER_ID,
                "hard_pass": False,
                "worker_pass": False,
                "error_kind": "input_invalid",
                "message": str(exc),
            }
        )
        return 2

    result = evaluate(validated)
    _emit(result)
    return 0 if result["hard_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
