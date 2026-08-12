#!/usr/bin/env python3
import unittest
from rank_non_labor_bounties import build_report

class TestRanker(unittest.TestCase):
    def item(self, **overrides):
        base = {"id":"x","title":"test","reward_usd":100,"platform_fee_pct":10,
                "success_probability":0.5,"estimated_hours_to_cash":10,
                "flags":{"auth_ready":True,"environment_ready":True,"submission_ready":True}}
        base.update(overrides); return base
    def ranked(self, item):
        return build_report({"observed_at_utc":"2026-08-12T08:31:05Z","assumptions":{"usd_jpy":150},"candidates":[item]})["candidates"][0]
    def test_eligible_not_monthly(self):
        item=self.ranked(self.item()); self.assertEqual(item["pipeline_counted_yen"],6750); self.assertEqual(item["verified_monthly_run_rate_increment_yen"],0)
    def test_missing_auth_excluded(self):
        item=self.ranked(self.item(flags={"auth_ready":False,"environment_ready":True,"submission_ready":True})); self.assertEqual(item["status"],"conditional"); self.assertEqual(item["pipeline_counted_yen"],0)
    def test_human_and_secret_rejected(self):
        item=self.ranked(self.item(flags={"auth_ready":True,"environment_ready":True,"submission_ready":True,"human_only":True,"secret_exfiltration":True})); self.assertEqual(item["status"],"rejected"); self.assertEqual(len(item["rejection_reasons"]),2)
    def test_unverified_funding_rejected(self):
        item=self.ranked(self.item(flags={"auth_ready":True,"environment_ready":True,"submission_ready":True,"funding_unverified":True})); self.assertEqual(item["status"],"rejected")
if __name__ == "__main__": unittest.main()
