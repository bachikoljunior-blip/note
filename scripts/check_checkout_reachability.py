#!/usr/bin/env python3
"""Fail-closed audit for whether a checkout route is actually reachable.

The audit consumes a sanitized, already-fetched snapshot. It does not create
products, prices, payment links, or public pages. Product and price records are
necessary but deliberately insufficient: legal disclosure, fulfillment,
checkout-link, commerce-mode, and public CTA evidence must all agree.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def evaluate(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return deterministic reachability results without leaking identifiers."""
    target = snapshot.get("target") or {}
    public_surface = snapshot.get("public_surface") or {}
    fallback = snapshot.get("fallback_channel") or {}

    blockers: list[str] = []
    if target.get("product_active") is not True:
        blockers.append("target_product_not_verified_active")
    if target.get("price_active") is not True:
        blockers.append("target_price_not_verified_active")

    matching_links = target.get("active_payment_link_matches")
    if not isinstance(matching_links, int) or isinstance(matching_links, bool):
        blockers.append("target_payment_link_match_count_unknown")
    elif matching_links == 0:
        blockers.append("no_active_payment_link_for_target_price")
    elif matching_links > 1:
        blockers.append("multiple_active_payment_links_for_target_price")

    if target.get("legal_disclosure_approved") is not True:
        blockers.append("legal_disclosure_not_approved")
    if target.get("fulfillment_end_to_end_verified") is not True:
        blockers.append("fulfillment_end_to_end_not_verified")
    if public_surface.get("direct_commerce_enabled") is not True:
        blockers.append("direct_commerce_not_enabled")
    if public_surface.get("cta_provider") != "stripe":
        blockers.append("public_cta_does_not_target_stripe")
    if public_surface.get("cta_targets_audited_price") is not True:
        blockers.append("public_cta_target_price_not_verified")

    fallback_live = (
        isinstance(fallback.get("provider"), str)
        and bool(fallback.get("provider"))
        and fallback.get("public_purchase_route_verified") is True
        and public_surface.get("cta_provider") == fallback.get("provider")
    )
    blockers = sorted(set(blockers))
    direct_live = not blockers
    return {
        "audit_id": snapshot.get("audit_id"),
        "direct_stripe_checkout_live": direct_live,
        "direct_stripe_blockers": blockers,
        "fallback_checkout_live": fallback_live,
        "fallback_provider": fallback.get("provider") if fallback_live else None,
        "checkout_is_revenue_or_contract": False,
        "external_mutation_allowed": False,
        "decision": (
            "direct_checkout_reachable"
            if direct_live
            else "keep_direct_checkout_fail_closed"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        result = evaluate(snapshot)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"direct_stripe_checkout_live": False, "error": str(exc)}))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0 if result["direct_stripe_checkout_live"] else 1


if __name__ == "__main__":
    sys.exit(main())
