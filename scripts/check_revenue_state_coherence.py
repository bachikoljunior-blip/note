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
        "state/brandable_idle.json",
        "scripts/gumroad_publish.py",
        "scripts/test_gumroad_publish.py",
        "OPERATIONS/GUMROAD_ATTACHED_CONTENT_GATE_VALIDATION_2026-08-08.json",
        "OPERATIONS/GUMROAD_PUBLIC_PRODUCT_READBACK_2026-08-08.json",
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
    brandable_idle = load("state/brandable_idle.json")

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

    high_ticket_product = current.get("high_ticket_pivot", {}).get("product", {})
    if high_ticket_product.get("artifact") != brandable_idle.get("output"):
        errors.append("brandable_idle_artifact_path_drift")
    if high_ticket_product.get("sha256") != brandable_idle.get("sha256"):
        errors.append("brandable_idle_artifact_sha_drift")
    if high_ticket_product.get("bytes") != brandable_idle.get("bytes"):
        errors.append("brandable_idle_artifact_bytes_drift")

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

    public_product = current.get("sales_channels", {}).get("gumroad", {}).get(
        "brandable_idle_public_product", {}
    )
    expected_public_product = {
        "status": "published_public_attached_content_observed",
        "product_id": "rMqZDCfZHOiaDJO5Iv0aHQ==",
        "url": "https://bachiko4.gumroad.com/l/fbozt",
        "currency_code": "usd",
        "price_cents": 2500,
        "public_size_display": "31.2 KB",
        "canonical_artifact_bytes": 31941,
        "canonical_artifact_sha256": "cdb71a22a1d454fcea89cfef50cee71a84cd19782e47db843e79a36abd4dd93f",
        "content_attachment_observed": True,
        "creator_test_purchase_verified": False,
        "purchaser_download_verified": False,
        "validation_record": "OPERATIONS/GUMROAD_PUBLIC_PRODUCT_READBACK_2026-08-08.json",
    }
    for key, expected in expected_public_product.items():
        if public_product.get(key) != expected:
            errors.append(f"gumroad_public_product_drift:{key}")
    public_record = load("OPERATIONS/GUMROAD_PUBLIC_PRODUCT_READBACK_2026-08-08.json")
    observed = public_record.get("observed_product", {})
    bounded = public_record.get("bounded_conclusions", {})
    if observed.get("id") != public_product.get("product_id"):
        errors.append("gumroad_public_record_product_id_drift")
    if observed.get("price_cents") != public_product.get("price_cents"):
        errors.append("gumroad_public_record_price_drift")
    if observed.get("currency_code") != public_product.get("currency_code"):
        errors.append("gumroad_public_record_currency_drift")
    if observed.get("is_published") is not True:
        errors.append("gumroad_public_record_not_published")
    if bounded.get("creator_test_purchase_verified") is not False:
        errors.append("gumroad_creator_test_must_remain_unverified")
    if bounded.get("revenue_inference") is not False:
        errors.append("gumroad_public_readback_must_not_infer_revenue")

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
        errors.append("legacy_gumroad_listing_gate_must_remain_deferred")
    gumroad_high_request = request_map.get("gumroad_brandable_idle_attachment_v1", {})
    if gumroad_high_request.get("currently_requested") is not False:
        errors.append("resolved_gumroad_attachment_request_must_not_remain_active")
    if "creator_test_optional" not in str(gumroad_high_request.get("status", "")):
        errors.append("gumroad_creator_test_optional_status_missing")
    stale_unimplemented = json.dumps(
        gumroad_high_request.get("not_implemented", []), ensure_ascii=False
    )
    if "Contentへの完成ZIP添付" in stale_unimplemented:
        errors.append("gumroad_attachment_still_marked_unimplemented")
    booth_high_request = request_map.get("booth_brandable_idle_listing_v1", {})
    if booth_high_request.get("currently_requested") is not False:
        errors.append("booth_high_ticket_gate_must_be_deferred")
    forecast_request_id = current.get("income_forecast", {}).get("next_user_operation_id")
    expected_active_request_ids = [forecast_request_id] if forecast_request_id else []
    if current.get("next_actions", {}).get("user_action_request_ids") != expected_active_request_ids:
        errors.append("forecast_single_active_request_drift")
    if expected_active_request_ids:
        selected_request = request_map.get(expected_active_request_ids[0], {})
        if selected_request.get("currently_requested") is not True:
            errors.append("forecast_selected_request_must_be_active")
    active_registry_ids = {
        request_id
        for request_id, request in request_map.items()
        if request.get("currently_requested") is True
    }
    if active_registry_ids != set(expected_active_request_ids):
        errors.append("single_active_request_registry_drift")
    assistants_request = request_map.get("assistants_sunset_gumroad_publication_v1", {})
    if expected_active_request_ids == ["assistants_sunset_gumroad_publication_v1"]:
        if assistants_request.get("residual_step_count") != 1:
            errors.append("assistants_sunset_request_must_remain_one_step")
        if assistants_request.get("evidence", [])[:2] != [
            "state/assistants_sunset_iphone_pack.json",
            "handoff/ASSISTANTS_SUNSET_GUMROAD_IPHONE.md",
        ]:
            errors.append("assistants_sunset_request_evidence_drift")
    elif assistants_request.get("currently_requested") is not False:
        errors.append("assistants_sunset_request_must_be_deferred_when_not_selected")
    assistants_pack = load("state/assistants_sunset_iphone_pack.json")
    if assistants_pack.get("status") not in {
        "remote_ci_validated_private_artifact_ready",
        "local_deterministic_tiered_pack_validated_private_library_replaced",
    }:
        errors.append("assistants_sunset_pack_not_ready")
    if assistants_pack.get("buyer_zip_attached") is not False:
        errors.append("assistants_sunset_buyer_zip_attachment_must_remain_unverified")
    if assistants_pack.get("creator_test_purchase_verified") is not False:
        errors.append("assistants_sunset_creator_test_must_remain_unverified")
    if expected_active_request_ids:
        if owner_request.get("status") != "automation_evaluated_one_session_requested":
            errors.append("selected_owner_request_status_drift")
        if owner_request.get("user_action_request_id") != expected_active_request_ids[0]:
            errors.append("selected_owner_request_id_drift")
    else:
        if owner_request.get("status") != "no_current_user_request_after_external_publication_readback":
            errors.append("zero_owner_request_status_drift")
        if owner_request.get("user_action_request_id") is not None:
            errors.append("zero_owner_request_id_must_be_null")
    owner_text = json.dumps(owner_request, ensure_ascii=False)
    if expected_active_request_ids == ["assistants_sunset_gumroad_publication_v1"]:
        if "Test Purchase" not in owner_text and "test purchase" not in owner_text.lower() and "テスト購入" not in owner_text:
            errors.append("gumroad_owner_gate_creator_test_missing")
    publisher_source = (ROOT / "scripts/gumroad_publish.py").read_text(encoding="utf-8")
    if "--existing-product-id" not in publisher_source:
        errors.append("gumroad_publisher_existing_product_gate_missing")
    if "--test-purchase-confirmed" not in publisher_source:
        errors.append("gumroad_publisher_creator_test_gate_missing")
    if "--delivery-url" in publisher_source:
        errors.append("gumroad_publisher_external_delivery_regression")
    if 'call(token, "POST", "/products"' in publisher_source:
        errors.append("gumroad_publisher_new_product_probe_regression")

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
