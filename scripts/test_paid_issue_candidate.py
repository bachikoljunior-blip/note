#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("check_paid_issue_candidate.py")
SPEC = importlib.util.spec_from_file_location("check_paid_issue_candidate", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
evaluate = MODULE.evaluate


def valid_snapshot():
    return {
        "candidate_id": "example",
        "marketplace": {
            "reward": "$500",
            "status": "open",
            "funding_verified": True,
            "claimable": True,
            "payout_terms_verified": True,
        },
        "issue": {
            "state": "open",
            "community_prs_accepted": True,
            "owner_only_action_required": False,
        },
        "repository": {"archived": False, "push_or_pr_path_available": True},
        "competing_prs": [],
    }


class PaidIssueGateTest(unittest.TestCase):
    def test_valid_candidate_passes(self):
        self.assertTrue(evaluate(valid_snapshot())["eligible"])

    def test_closed_upstream_rejected(self):
        data = valid_snapshot()
        data["issue"]["state"] = "closed"
        self.assertIn("upstream_issue_not_open", evaluate(data)["blockers"])

    def test_unverified_funding_rejected(self):
        data = valid_snapshot()
        data["marketplace"]["funding_verified"] = False
        self.assertFalse(evaluate(data)["eligible"])

    def test_verification_pending_rejected(self):
        data = valid_snapshot()
        data["marketplace"]["claimable"] = False
        self.assertIn("not_currently_claimable", evaluate(data)["blockers"])

    def test_unknown_pr_state_rejected(self):
        data = valid_snapshot()
        del data["competing_prs"]
        self.assertIn("competing_prs_not_checked", evaluate(data)["blockers"])

    def test_open_competing_pr_rejected(self):
        data = valid_snapshot()
        data["competing_prs"] = [{"state": "open"}]
        self.assertIn("competing_open_pr_exists", evaluate(data)["blockers"])

    def test_plain_number_reward_is_accepted(self):
        data = valid_snapshot()
        data["marketplace"]["reward"] = 170
        self.assertEqual(170.0, evaluate(data)["reward_usd"])


if __name__ == "__main__":
    unittest.main()
