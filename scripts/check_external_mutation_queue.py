#!/usr/bin/env python3
"""Fail closed when queued external mutations drift from safe, cross-linked state."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "state" / "external_mutation_queue.json"
CURRENT_PATH = ROOT / "state" / "current.json"
REQUESTS_PATH = ROOT / "state" / "user_action_requests.json"
CONTINUATION_PATH = ROOT / "state" / "continuation_control.json"
REPORT_PATH = ROOT / "reports" / "external_mutation_queue.json"

REQUIRED_IDS = {
    "stripe_webhook_secret_recovery_v1",
    "stripe_legal_disclosure_gate_v1",
}
SENSITIVE_VALUE_KEYS = {
    "signing_secret",
    "webhook_secret",
    "api_key",
    "password",
    "credential",
    "bearer_token",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def walk(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key, item in value.items():
            yield f"{path}.{key}", key, item
            yield from walk(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, f"{path}[{index}]")


def main() -> int:
    errors: list[str] = []
    for path in (QUEUE_PATH, CURRENT_PATH, REQUESTS_PATH, CONTINUATION_PATH):
        if not path.is_file():
            errors.append(f"missing:{path.relative_to(ROOT)}")
    if errors:
        return finish(errors, [])

    queue = load(QUEUE_PATH)
    current = load(CURRENT_PATH)
    request_store = load(REQUESTS_PATH)
    continuation = load(CONTINUATION_PATH)

    if queue.get("schema_version") not in {"1.0", "1.1"}:
        errors.append("queue_schema_version_invalid")
    if queue.get("policy") != "single_external_mutation_after_preflight":
        errors.append("queue_policy_invalid")

    safe = queue.get("safe_current_state", {})
    expected_safe = {
        "public_primary_checkout": "BOOTH",
        "stripe_direct_checkout_enabled": False,
        "cloudflare_commerce_enabled": False,
        "secrets_committed_to_github": False,
        "paid_artifact_publicly_accessible": False,
        "site_v13_deployed": True,
        "stripe_webhook_signature_ready": True,
        "enabled_stripe_webhook_count": 1,
        "target_payment_link_exists": False,
    }
    for key, expected in expected_safe.items():
        if safe.get(key) != expected:
            errors.append(f"unsafe_or_missing:{key}")

    pending = queue.get("pending_operations", [])
    completed = queue.get("completed_operations", [])
    if not isinstance(pending, list):
        errors.append("pending_operations_not_list")
        pending = []
    if not isinstance(completed, list):
        errors.append("completed_operations_not_list")
        completed = []
    operations = pending + completed
    ids = [item.get("id") for item in operations if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        errors.append("duplicate_operation_ids")
    if not REQUIRED_IDS.issubset(set(ids)):
        errors.append("required_operation_missing")

    requests = {
        item.get("id"): item
        for item in request_store.get("requests", [])
        if isinstance(item, dict) and item.get("id")
    }
    active_request_ids = set(current.get("next_actions", {}).get("user_action_request_ids", []))
    cross_linked_request_ids = set(active_request_ids)
    cross_linked_request_ids.update(current.get("next_actions", {}).get("deferred_user_action_request_ids", []))
    work_units = {
        item.get("id"): item
        for item in continuation.get("active_work_units", [])
        if isinstance(item, dict) and item.get("id")
    }

    checked: list[dict[str, Any]] = []
    pending_ids = {item.get("id") for item in pending if isinstance(item, dict)}
    completed_ids = {item.get("id") for item in completed if isinstance(item, dict)}
    for operation in operations:
        if not isinstance(operation, dict):
            errors.append("operation_not_object")
            continue
        operation_id = operation.get("id")
        is_pending = operation_id in pending_ids
        item_errors: list[str] = []
        if operation.get("priority") not in {"P0", "P1"}:
            item_errors.append("priority_invalid")
        if not operation.get("status"):
            item_errors.append("status_missing")
        if operation.get("user_action_request_id") != operation_id:
            item_errors.append("user_action_cross_link_mismatch")
        if operation.get("continuation_work_unit_id") != operation_id:
            item_errors.append("continuation_cross_link_mismatch")
        validation_record = operation.get("validation_record")
        if not validation_record or not (ROOT / str(validation_record)).is_file():
            item_errors.append("validation_record_missing")

        request = requests.get(operation_id)
        unit = work_units.get(operation_id)
        if request is None:
            item_errors.append("user_action_request_missing")
        if unit is None:
            item_errors.append("continuation_work_unit_missing")

        if is_pending:
            if operation.get("independent_work_continues") is not True:
                item_errors.append("independent_work_must_continue")
            if request is not None:
                if "evaluated" not in str(request.get("status", "")):
                    item_errors.append("user_action_request_not_evaluated")
                if request.get("automation_review", {}).get("completed") is not True:
                    item_errors.append("user_action_automation_review_incomplete")
            if operation_id not in cross_linked_request_ids:
                item_errors.append("current_request_cross_link_missing")
            if unit is not None:
                if unit.get("user_blocked") is not True:
                    item_errors.append("continuation_unit_must_be_user_blocked")
                if unit.get("global_stop") is not False:
                    item_errors.append("continuation_unit_must_not_be_global_stop")
                if unit.get("actionable_now") is not False:
                    item_errors.append("continuation_unit_actionable_now_must_be_false")
        else:
            if not str(operation.get("status", "")).startswith("completed"):
                item_errors.append("completed_operation_status_invalid")
            if request is not None:
                if "completed" not in str(request.get("status", "")):
                    item_errors.append("completed_user_action_status_invalid")
                if request.get("residual_step_count") != 0:
                    item_errors.append("completed_user_action_has_residual_steps")
            if operation_id in active_request_ids:
                item_errors.append("completed_request_still_active")
            if unit is not None:
                if unit.get("user_blocked") is not False:
                    item_errors.append("completed_unit_must_not_be_user_blocked")
                if unit.get("global_stop") is not False:
                    item_errors.append("completed_unit_must_not_be_global_stop")
                if unit.get("actionable_now") is not False:
                    item_errors.append("completed_unit_actionable_now_must_be_false")

        errors.extend(f"{operation_id}:{error}" for error in item_errors)
        checked.append({"id": operation_id, "state": "pending" if is_pending else "completed", "errors": item_errors})

    landing = current.get("sales_channels", {}).get("autonomous_landing_site", {})
    commerce = landing.get("direct_commerce", {})
    if commerce.get("enabled") is not False:
        errors.append("current_direct_commerce_must_remain_disabled")
    if commerce.get("public_purchase_route") != "BOOTH":
        errors.append("current_public_purchase_route_must_be_booth")
    queue_pointer = current.get("external_mutation_queue", {})
    if queue_pointer.get("path") != "state/external_mutation_queue.json":
        errors.append("current_external_mutation_queue_pointer_missing")
    if set(queue_pointer.get("pending_operation_ids", [])) != pending_ids:
        errors.append("current_pending_operation_ids_mismatch")
    if not completed_ids.issubset(set(queue_pointer.get("completed_operation_ids", []))):
        errors.append("current_completed_operation_ids_mismatch")
    if continuation.get("project_status") == "stopped":
        errors.append("external_mutation_blocker_must_not_stop_project")

    for path, key, value in walk(queue):
        if key.lower() in SENSITIVE_VALUE_KEYS and value not in (False, None, ""):
            errors.append(f"sensitive_value_persisted:{path}")

    return finish(errors, checked)


def finish(errors: list[str], checked: list[dict[str, Any]]) -> int:
    payload = {
        "schema_version": "1.1",
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "errors": errors,
        "checked_operations": checked,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
