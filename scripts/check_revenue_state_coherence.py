#!/usr/bin/env python3
"""Catch cross-file revenue state drift that individual contract checks cannot see."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "revenue_state_coherence.json"


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    required = [
        "state/current.json",
        "state/autonomous_revenue_factory.json",
        "state/continuation_control.json",
        "state/external_mutation_queue.json",
        "state/user_action_requests.json",
        "state/funnel_structure_2026.json",
        "state/gumroad_visual_pack.json",
        "state/booth_visual_pack.json",
        "state/funnel_article_policy_2026.json",
        "state/booth_distribution.json",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        errors.extend(f"missing:{path}" for path in missing)
        return finish(errors)

    current = load("state/current.json")
    factory = load("state/autonomous_revenue_factory.json")
    continuation = load("state/continuation_control.json")
    queue = load("state/external_mutation_queue.json")
    requests = load("state/user_action_requests.json")
    structure = load("state/funnel_structure_2026.json")
    gumroad = load("state/gumroad_visual_pack.json")
    booth_visual = load("state/booth_visual_pack.json")
    funnel = load("state/funnel_article_policy_2026.json")
    distribution = load("state/booth_distribution.json")

    asset = factory.get("first_asset", {})
    version = asset.get("optimization_version")
    latest = asset.get(f"latest_v{version}_deployment", {}) if isinstance(version, int) else {}
    source = asset.get("site_source_commit")
    record = asset.get("optimization_record")
    tests = asset.get("qa", {}).get("test_count")
    if not latest:
        errors.append("factory_latest_version_deployment_missing")
    if source != latest.get("source_commit"):
        errors.append("factory_latest_source_commit_drift")
    if record != latest.get("validation_record"):
        errors.append("factory_latest_validation_record_drift")
    if tests != latest.get("test_count"):
        errors.append("factory_latest_test_count_drift")
    if record and not (ROOT / str(record)).is_file():
        errors.append("factory_latest_validation_record_file_missing")
    validation = load(str(record)) if record and (ROOT / str(record)).is_file() else {}
    if validation.get("status") != "public_deployed_verified":
        errors.append("latest_validation_status_drift")
    if validation.get("source_commit") != source:
        errors.append("latest_validation_source_commit_drift")
    verification = validation.get("verification", {})
    if verification.get("site_version") != version:
        errors.append("latest_validation_site_version_drift")
    if verification.get("automated_test_count") != tests:
        errors.append("latest_validation_test_count_drift")
    changes = validation.get("changes", {})
    if changes.get("commerce_enabled") is not False:
        errors.append("latest_validation_commerce_must_remain_disabled")
    if changes.get("public_primary_checkout") != "BOOTH":
        errors.append("latest_validation_primary_checkout_drift")

    landing = current.get("sales_channels", {}).get("autonomous_landing_site", {})
    growth = current.get("latest_growth_asset", {})
    current_factory = current.get("autonomous_revenue_factory", {})
    if landing.get("optimization_version") != version:
        errors.append("current_landing_optimization_version_drift")
    if landing.get("optimization_record") != record:
        errors.append("current_landing_validation_record_drift")
    if growth.get("validation_record") != record:
        errors.append("current_growth_validation_record_drift")
    if current_factory.get("validation_record") != record:
        errors.append("current_factory_validation_record_drift")
    if current_factory.get("first_asset", {}).get("optimization_version") != version:
        errors.append("current_factory_optimization_version_drift")
    for name, value in (
        ("growth_source", growth.get("site_source_commit")),
        ("current_factory_source", current_factory.get("first_asset", {}).get("site_source_commit")),
    ):
        if value != source:
            errors.append(f"{name}_drift")
    if growth.get("test_count") != tests:
        errors.append("current_growth_test_count_drift")
    if current.get("continuation_control", {}).get("latest_site_validation") != record:
        errors.append("current_latest_site_validation_drift")
    remote_site = continuation.get("remote_validation", {}).get(f"site_v{version}", {})
    if remote_site.get("source_commit") != source or remote_site.get("validation_record") != record:
        errors.append("continuation_latest_site_validation_drift")

    safe = queue.get("safe_current_state", {})
    if safe.get(f"site_v{version}_validation_record") != record:
        errors.append("queue_latest_site_validation_record_drift")
    if safe.get(f"site_v{version}_source_commit") != source:
        errors.append("queue_latest_site_source_commit_drift")
    if safe.get(f"site_v{version}_commerce_fail_closed_verified") is not True:
        errors.append("queue_latest_site_fail_closed_evidence_missing")

    completed = {item.get("id") for item in queue.get("completed_operations", []) if isinstance(item, dict)}
    pending = {item.get("id") for item in queue.get("pending_operations", []) if isinstance(item, dict)}
    if "stripe_webhook_secret_recovery_v1" not in completed or "stripe_webhook_secret_recovery_v1" in pending:
        errors.append("stripe_webhook_completion_state_drift")
    blocker_result = continuation.get("search_horizon_evaluation", {}).get(
        "blocker_reduction_and_authentication_automation", {}
    ).get("result", "")
    if "completed" not in blocker_result or "exactly one enabled endpoint" not in blocker_result:
        errors.append("stripe_webhook_search_horizon_wording_stale")

    if "remote_ci_pending" in json.dumps(structure, ensure_ascii=False):
        errors.append("structure_funnel_remote_ci_pending_stale")
    if structure.get("publication_status") != "ready_for_authenticated_final_publication":
        errors.append("structure_funnel_publication_status_drift")

    gumroad_text = " ".join(
        str(value) for value in (
            gumroad.get("status"),
            gumroad.get("automation", {}).get("gumroad_authenticated_upload"),
            gumroad.get("next_assistant_action"),
        )
    ).lower()
    if "authentication_not_started" in gumroad_text or "device oauth" in gumroad_text:
        errors.append("gumroad_obsolete_oauth_or_authentication_state")
    if gumroad.get("latest_remote_integration", {}).get("gumroad_manual_checkpoint") != "new_product_price_entry":
        errors.append("gumroad_price_checkpoint_missing")

    if booth_visual.get("public_url") != "https://mobile-ai-studio.booth.pm/items/8691522":
        errors.append("booth_visual_public_url_missing")
    if "URL取得後" in str(booth_visual.get("next_assistant_action", "")):
        errors.append("booth_visual_next_action_stale")

    if funnel.get("second_article", {}).get("state") != "state/funnel_structure_2026.json":
        errors.append("funnel_second_article_registry_missing")
    if "Evaluate a second" in json.dumps(funnel.get("next_assistant_actions", []), ensure_ascii=False):
        errors.append("funnel_second_article_plan_stale")

    request_ids = {item.get("id") for item in requests.get("requests", []) if isinstance(item, dict)}
    if "funnel_article_structure_2026" not in request_ids:
        errors.append("structure_funnel_user_action_request_missing")
    current_request_ids = set(current.get("next_actions", {}).get("user_action_request_ids", []))
    current_request_ids.update(current.get("next_actions", {}).get("deferred_user_action_request_ids", []))
    if "funnel_article_structure_2026" not in current_request_ids:
        errors.append("structure_funnel_current_cross_link_missing")

    if distribution.get("currently_requesting_user_action") is not False:
        errors.append("booth_distribution_repeat_prompt_guard_missing")
    if distribution.get("user_action_already_presented") is not True:
        errors.append("booth_distribution_presented_state_missing")

    gumroad_capability = current.get("gumroad_api_capability_2026_08_08", {})
    gumroad_delivery = gumroad_capability.get("delivery_constraint", {})
    gumroad_root = gumroad_capability.get("publish_blocker_root_cause", {})
    owner_request = current.get("owner_action_minimization", {}).get("single_highest_leverage_request", {})
    zero_touch_claims = " ".join(
        str(value)
        for value in (
            gumroad_capability.get("consequence"),
            gumroad_root.get("implication"),
            owner_request.get("why"),
        )
    )
    if "公開まで全てAPI" in zero_touch_claims or "以後は0操作" in zero_touch_claims:
        errors.append("gumroad_api_zero_touch_delivery_claim_stale")
    if gumroad_delivery.get("api_content_upload_supported") is not False:
        errors.append("gumroad_api_content_upload_constraint_missing")
    if gumroad_delivery.get("payment_method_alone_completes_delivery") is not False:
        errors.append("gumroad_payment_method_only_gate_incorrect")
    if gumroad_delivery.get("empty_product_external_message_only_publish_allowed") is not False:
        errors.append("gumroad_empty_external_delivery_fail_closed_missing")
    gumroad_record = gumroad_delivery.get("validation_record")
    if gumroad_record != "OPERATIONS/GUMROAD_API_DELIVERY_CORRECTION_2026-08-08.json":
        errors.append("gumroad_delivery_correction_record_drift")
    if gumroad_record and not (ROOT / str(gumroad_record)).is_file():
        errors.append("gumroad_delivery_correction_record_missing")

    request_map = {
        item.get("id"): item
        for item in requests.get("requests", [])
        if isinstance(item, dict) and item.get("id")
    }
    gumroad_request = request_map.get("gumroad_listing_v1", {})
    gumroad_api_review = gumroad_request.get("automation_review", {}).get("official_api_or_webhook", {})
    if "content_upload_unsupported" not in str(gumroad_api_review.get("status", "")):
        errors.append("gumroad_user_gate_api_content_limit_missing")
    if gumroad_request.get("currently_requested") is not False:
        errors.append("gumroad_secondary_gate_must_not_be_the_active_single_request")
    booth_high_request = request_map.get("booth_brandable_idle_listing_v1", {})
    if booth_high_request.get("currently_requested") is not True:
        errors.append("brandable_idle_single_active_request_missing")
    if current.get("next_actions", {}).get("user_action_request_ids") != ["booth_brandable_idle_listing_v1"]:
        errors.append("current_single_high_leverage_request_drift")

    assistant_actions = " ".join(
        str(value) for value in current.get("next_actions", {}).get("assistant", [])
    )
    if current.get("high_ticket_pivot", {}).get("product") and "Design a 30,000-50,000 JPY offer" in assistant_actions:
        errors.append("completed_high_ticket_offer_still_planned")

    direct_commerce_flags = {
        "current_landing": landing.get("direct_commerce", {}).get("enabled"),
        "current_growth": growth.get("direct_commerce_enabled"),
        "current_factory": current_factory.get("first_asset", {}).get("direct_commerce_enabled"),
        "factory_asset": asset.get("direct_commerce", {}).get("enabled"),
        "queue_stripe": safe.get("stripe_direct_checkout_enabled"),
        "queue_cloudflare": safe.get("cloudflare_commerce_enabled"),
    }
    for name, enabled in direct_commerce_flags.items():
        if enabled is not False:
            errors.append(f"direct_commerce_must_remain_fail_closed:{name}")
    return finish(errors)


def finish(errors: list[str]) -> int:
    payload = {
        "schema_version": "1.0",
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
