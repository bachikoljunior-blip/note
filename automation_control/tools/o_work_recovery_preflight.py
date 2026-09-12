"""Read-only evidence checks for O recovery. This tool never grants authority."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must have a timezone")
    return parsed.astimezone(timezone.utc)


def assess(facts: dict, now: str) -> dict:
    """Require source evidence, not a prior monitor's repeated conclusion.

    facts contains non-secret normalized observations and source references.
    notification.emission is supplied only after an actual final message is
    visible in task-chat context, or a platform delivery acknowledgement exists.
    A prepared receipt is never evidence of emission, even if another receipt
    subsequently labels it 'already visible'.
    """
    at = instant(now)
    reasons = []
    for flag in ("new_user_message", "explicit_recovery_candidate",
                 "unresolved_transport_or_permission_ambiguity",
                 "writer_or_progress_evidence_requires_refresh",
                 "semantic_read_before_refresh"):
        if facts.get(flag):
            reasons.append(flag)
    for field in ("main_sha", "control_blob_sha"):
        if not facts.get(field) or facts[field] != facts.get("prior_" + field):
            reasons.append(field + "_changed_or_unknown")
    for verified in ("prior_hold_eligibility_verified", "hold_fingerprint_complete_and_unchanged"):
        if facts.get(verified) is not True:
            reasons.append(verified + "_missing")
    reuse_count = facts.get("consecutive_lightweight_reuses")
    if not isinstance(reuse_count, int) or isinstance(reuse_count, bool) or reuse_count < 0:
        reasons.append("lightweight_reuse_count_unknown")
    elif reuse_count >= 2:
        reasons.append("lightweight_reuse_limit")
    human = facts.get("human_monitor", {})
    try:
        human_age = (at - instant(human["observed_at"])).total_seconds()
        if not 0 <= human_age <= 5400:
            reasons.append("human_monitor_stale_or_future")
    except (KeyError, TypeError, ValueError):
        human_age = None
        reasons.append("human_monitor_time_unknown")
    if (human.get("main_sha") != facts.get("main_sha")
            or human.get("result") != "no_material_request_change"
            or not human.get("source_ref")):
        reasons.append("human_monitor_exact_main_or_result_unverified")
    try:
        full_age = (at - instant(facts["prior_full_observed_at"])).total_seconds()
        if not 0 <= full_age <= 10800:
            reasons.append("prior_full_hold_stale_or_future")
    except (KeyError, TypeError, ValueError):
        reasons.append("prior_full_hold_time_unknown")

    action_key = facts.get("blocked_action_key")
    notice = facts.get("notification", {})
    emission = notice.get("emission", {})
    text = notice.get("notice_text", "")
    valid_emission = bool(
        action_key and notice.get("action_key") == action_key
        and notice.get("status") in {"emitted", "delivery_confirmed"}
        and emission.get("kind") in {"visible_task_chat_final", "platform_delivery_ack"}
        and emission.get("source_ref") and text
        and emission.get("text_sha256") == hashlib.sha256(text.encode()).hexdigest()
    )
    notice_due = bool(action_key and not valid_emission)
    if notice_due:
        reasons.append("actionable_notification_emission_unverified")

    # These are obligations, never native mutation/lease permission.
    if facts.get("accepted_pending_operation"):
        next_step = "query_existing_operation_before_any_relaunch"
    elif facts.get("separate_owner_substantive_progress_verified"):
        next_step = "preserve_owner_and_recheck_bound_progress"
    elif facts.get("consumed_response_successor_unpublished"):
        if not facts.get("frozen_native_objects_verified"):
            next_step = "restore_exact_objects_without_semantic_replay"
        elif not facts.get("original_commit_available") and not facts.get("replacement_proposal_available"):
            next_step = "prepare_local_proposal_with_honest_new_metadata"
        else:
            next_step = "resolve_exact_publication_hold_then_ci_and_main_readback"
    else:
        next_step = "evaluate_stop_cause_and_existing_fenced_authorization"
    return {
        "full_refresh_required": bool(reasons),
        "full_refresh_reasons": reasons,
        "human_monitor_age_seconds": human_age,
        "notification_due": notice_due,
        "notification_emission_verified": valid_emission,
        "delivery_verified": bool(valid_emission and emission.get("kind") == "platform_delivery_ack"),
        "next_step": next_step,
        "native_resume_authorized": False,
        "publication_authorized": False,
        "recovery_success": False,
        "goal_complete": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("facts", type=Path)
    parser.add_argument("--now", required=True)
    args = parser.parse_args()
    print(json.dumps(assess(json.loads(args.facts.read_text()), args.now), indent=2))


if __name__ == "__main__":
    main()
