#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "state" / "current.json"
REQUESTS_PATH = ROOT / "state" / "user_action_requests.json"
REPORT_PATH = ROOT / "reports" / "user_action_gate.json"

REQUIRED_REVIEW_KEYS = {
    "connected_tools",
    "official_api_or_webhook",
    "github_actions_or_scheduler",
    "browser_share_or_shortcut",
    "batching_and_prefill",
    "verification_and_logging",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not STATE_PATH.is_file():
        errors.append("missing:state/current.json")
    if not REQUESTS_PATH.is_file():
        errors.append("missing:state/user_action_requests.json")

    if errors:
        return write_report(errors, warnings, [])

    state = load(STATE_PATH)
    store = load(REQUESTS_PATH)
    requests = store.get("requests", [])
    by_id = {item.get("id"): item for item in requests if item.get("id")}

    next_actions = state.get("next_actions", {})
    user_actions = next_actions.get("user", [])
    active_ids = next_actions.get("user_action_request_ids", [])

    if user_actions and not active_ids:
        errors.append("user_actions_exist_without_request_ids")
    if len(active_ids) != len(set(active_ids)):
        errors.append("duplicate_user_action_request_ids")

    checked: list[dict[str, object]] = []
    for request_id in active_ids:
        item = by_id.get(request_id)
        if item is None:
            errors.append(f"missing_request:{request_id}")
            continue

        item_errors: list[str] = []
        status = str(item.get("status", ""))
        review = item.get("automation_review", {})
        residual = item.get("residual_user_steps", [])
        declared_count = item.get("residual_step_count")

        if not review.get("completed"):
            item_errors.append("automation_review_not_completed")
        missing_review = sorted(REQUIRED_REVIEW_KEYS - set(review))
        if missing_review:
            item_errors.append("missing_review_sections:" + ",".join(missing_review))
        if "evaluated" not in status:
            item_errors.append("status_does_not_show_evaluation")
        if not isinstance(residual, list):
            item_errors.append("residual_user_steps_not_list")
            residual = []
        if declared_count != len(residual):
            item_errors.append(f"residual_step_count_mismatch:{declared_count}!={len(residual)}")
        if len(residual) > 3 and not item.get("exception_reason"):
            item_errors.append(f"too_many_residual_steps:{len(residual)}")
        if residual and not item.get("user_only_reason"):
            item_errors.append("missing_user_only_reason")
        if not item.get("fallback"):
            item_errors.append("missing_fallback")

        evidence = item.get("evidence", [])
        if not isinstance(evidence, list) or not evidence:
            item_errors.append("missing_evidence")
        else:
            for rel in evidence:
                path = ROOT / str(rel)
                if not path.exists():
                    item_errors.append(f"evidence_not_found:{rel}")

        for section in REQUIRED_REVIEW_KEYS:
            value = review.get(section)
            if not isinstance(value, dict):
                continue
            if not value.get("status") or not value.get("result"):
                item_errors.append(f"incomplete_review_section:{section}")

        if item_errors:
            errors.extend(f"{request_id}:{error}" for error in item_errors)

        checked.append(
            {
                "id": request_id,
                "status": status,
                "residual_step_count": len(residual),
                "errors": item_errors,
            }
        )

    # Draft requests may exist, but any request marked active must have been reviewed.
    for item in requests:
        if item.get("status") == "draft" and item.get("id") in active_ids:
            errors.append(f"active_request_is_draft:{item.get('id')}")

    if not user_actions:
        warnings.append("no_current_user_actions")

    return write_report(errors, warnings, checked)


def write_report(errors: list[str], warnings: list[str], checked: list[dict[str, object]]) -> int:
    payload = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "errors": errors,
        "warnings": warnings,
        "checked_requests": checked,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
