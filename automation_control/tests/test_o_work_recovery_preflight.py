"""Regressions drawn from the generation-35 recovery stall."""
import hashlib
import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).parents[1] / "tools" / "o_work_recovery_preflight.py"
SPEC = importlib.util.spec_from_file_location("recovery_preflight", MODULE)
PREFLIGHT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREFLIGHT)


class RecoveryPreflightTests(unittest.TestCase):
    def facts(self):
        return {
            "main_sha": "same-main", "prior_main_sha": "same-main",
            "control_blob_sha": "same-control", "prior_control_blob_sha": "same-control",
            "prior_hold_eligibility_verified": True,
            "hold_fingerprint_complete_and_unchanged": True,
            "consecutive_lightweight_reuses": 0,
            "prior_full_observed_at": "2026-09-12T21:00:00Z",
            "human_monitor": {"observed_at": "2026-09-12T21:45:00Z",
                              "main_sha": "same-main", "result": "no_material_request_change",
                              "source_ref": "exact-human-receipt"},
            "blocked_action_key": "publication-A",
        }

    def emitted(self):
        text = "Publish the reviewed files to the public O repository?"
        return {"action_key": "publication-A", "status": "emitted", "notice_text": text,
                "emission": {"kind": "visible_task_chat_final", "source_ref": "observed-final-message",
                             "text_sha256": hashlib.sha256(text.encode()).hexdigest()}}

    def evaluate(self, facts):
        return PREFLIGHT.assess(facts, "2026-09-12T22:00:00Z")

    def test_prepared_notice_is_not_delivery_even_with_prior_visible_claim(self):
        f = self.facts()
        f["notification"] = {"status": "actionable_notice_prepared_for_current_user_response",
                             "action_key": "publication-A", "delivery_verified": False,
                             "prior_payload_approval_notice_already_visible": True}
        self.assertTrue(self.evaluate(f)["notification_due"])

    def test_emitted_without_source_does_not_suppress(self):
        f = self.facts(); f["notification"] = self.emitted()
        f["notification"]["emission"].pop("source_ref")
        self.assertTrue(self.evaluate(f)["notification_due"])

    def test_visible_exact_notice_deduplicates_without_claiming_delivery(self):
        f = self.facts(); f["notification"] = self.emitted()
        result = self.evaluate(f)
        self.assertFalse(result["notification_due"])
        self.assertFalse(result["delivery_verified"])
        self.assertFalse(result["full_refresh_required"])

    def test_different_payload_notice_does_not_suppress(self):
        f = self.facts(); f["notification"] = self.emitted(); f["blocked_action_key"] = "publication-B"
        self.assertTrue(self.evaluate(f)["notification_due"])

    def test_actual_221457_start_was_already_stale(self):
        f = self.facts(); f["human_monitor"]["observed_at"] = "2026-09-12T20:41:05Z"
        result = PREFLIGHT.assess(f, "2026-09-12T22:14:57Z")
        self.assertEqual(result["human_monitor_age_seconds"], 5632)
        self.assertIn("human_monitor_stale_or_future", result["full_refresh_reasons"])

    def test_monitor_without_exact_main_cannot_enable_lightweight_hold(self):
        f = self.facts(); f["notification"] = self.emitted(); f["human_monitor"].pop("main_sha")
        self.assertTrue(self.evaluate(f)["full_refresh_required"])

    def test_incomplete_fingerprint_cannot_reuse_hold(self):
        f = self.facts(); f["notification"] = self.emitted()
        f.pop("hold_fingerprint_complete_and_unchanged")
        self.assertTrue(self.evaluate(f)["full_refresh_required"])

    def test_unknown_reuse_counter_cannot_reuse_hold(self):
        f = self.facts(); f["notification"] = self.emitted()
        f.pop("consecutive_lightweight_reuses")
        self.assertTrue(self.evaluate(f)["full_refresh_required"])

    def test_missing_commit_preserves_payload_and_selects_local_proposal(self):
        f = self.facts(); f.update(consumed_response_successor_unpublished=True,
                                  frozen_native_objects_verified=True, original_commit_available=False)
        result = self.evaluate(f)
        self.assertEqual(result["next_step"], "prepare_local_proposal_with_honest_new_metadata")
        self.assertFalse(result["native_resume_authorized"])
        self.assertFalse(result["publication_authorized"])

    def test_pending_operation_is_queried_before_another_launch(self):
        f = self.facts(); f.update(accepted_pending_operation=True, consumed_response_successor_unpublished=True)
        self.assertEqual(self.evaluate(f)["next_step"], "query_existing_operation_before_any_relaunch")

    def test_healthy_owner_never_replaced(self):
        f = self.facts(); f["separate_owner_substantive_progress_verified"] = True
        self.assertEqual(self.evaluate(f)["next_step"], "preserve_owner_and_recheck_bound_progress")


if __name__ == "__main__":
    unittest.main()
