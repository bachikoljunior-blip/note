#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("check_checkout_reachability.py")
SPEC = importlib.util.spec_from_file_location("check_checkout_reachability", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
evaluate = MODULE.evaluate


def valid_snapshot():
    return {
        "audit_id": "example",
        "target": {
            "product_active": True,
            "price_active": True,
            "active_payment_link_matches": 1,
            "legal_disclosure_approved": True,
            "fulfillment_end_to_end_verified": True,
        },
        "public_surface": {
            "direct_commerce_enabled": True,
            "cta_provider": "stripe",
            "cta_targets_audited_price": True,
        },
        "fallback_channel": {
            "provider": "booth",
            "public_purchase_route_verified": True,
        },
    }


class CheckoutReachabilityTest(unittest.TestCase):
    def test_complete_direct_checkout_passes(self):
        self.assertTrue(evaluate(valid_snapshot())["direct_stripe_checkout_live"])

    def test_active_product_and_price_are_insufficient(self):
        data = valid_snapshot()
        data["target"]["active_payment_link_matches"] = 0
        result = evaluate(data)
        self.assertFalse(result["direct_stripe_checkout_live"])
        self.assertIn("no_active_payment_link_for_target_price", result["direct_stripe_blockers"])

    def test_unknown_link_count_fails_closed(self):
        data = valid_snapshot()
        del data["target"]["active_payment_link_matches"]
        self.assertIn(
            "target_payment_link_match_count_unknown", evaluate(data)["direct_stripe_blockers"]
        )

    def test_multiple_links_are_ambiguous(self):
        data = valid_snapshot()
        data["target"]["active_payment_link_matches"] = 2
        self.assertIn(
            "multiple_active_payment_links_for_target_price", evaluate(data)["direct_stripe_blockers"]
        )

    def test_legal_gate_fails_closed(self):
        data = valid_snapshot()
        data["target"]["legal_disclosure_approved"] = False
        self.assertFalse(evaluate(data)["direct_stripe_checkout_live"])

    def test_fulfillment_gate_fails_closed(self):
        data = valid_snapshot()
        data["target"]["fulfillment_end_to_end_verified"] = False
        self.assertIn(
            "fulfillment_end_to_end_not_verified", evaluate(data)["direct_stripe_blockers"]
        )

    def test_cta_must_match_target_price(self):
        data = valid_snapshot()
        data["public_surface"]["cta_targets_audited_price"] = False
        self.assertFalse(evaluate(data)["direct_stripe_checkout_live"])

    def test_verified_fallback_is_reported_without_becoming_revenue(self):
        data = valid_snapshot()
        data["target"]["active_payment_link_matches"] = 0
        data["public_surface"]["direct_commerce_enabled"] = False
        data["public_surface"]["cta_provider"] = "booth"
        data["public_surface"]["cta_targets_audited_price"] = False
        result = evaluate(data)
        self.assertTrue(result["fallback_checkout_live"])
        self.assertEqual("booth", result["fallback_provider"])
        self.assertFalse(result["checkout_is_revenue_or_contract"])


if __name__ == "__main__":
    unittest.main()
