#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "state" / "gumroad_manual_checkpoint.json"
LISTING = ROOT / "state" / "gumroad_listing.json"
CURRENT = ROOT / "state" / "current.json"
CONTROL = ROOT / "state" / "continuation_control.json"
HANDOFF = ROOT / "handoff" / "GUMROAD_SAFARI_MANUAL.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    checkpoint = load(CHECKPOINT)
    listing = load(LISTING)
    current = load(CURRENT)
    control = load(CONTROL)
    handoff = HANDOFF.read_text(encoding="utf-8")

    if checkpoint.get("classification") != "assistant_operational_state_not_permanent_directive":
        errors.append("checkpoint_classification_invalid")
    if checkpoint.get("status") not in {
        "price_entry_observed_remote_ci_pending",
        "remote_ci_validated_pending_merge",
        "merged_main_remote_ci_validated",
        "end_to_end_handoff_remote_ci_pending",
        "end_to_end_handoff_remote_ci_validated",
        "end_to_end_handoff_merged_main",
    }:
        errors.append("checkpoint_status_invalid")

    observed = checkpoint.get("observed_progress", {})
    if observed.get("screen") != "new_product_price_entry":
        errors.append("latest_screen_not_preserved")
    if observed.get("product_name_visible") is not True or observed.get("product_type") != "digital":
        errors.append("completed_inputs_not_preserved")
    if observed.get("price_currency") != "USD" or observed.get("price_field_state") != "empty_required":
        errors.append("price_checkpoint_invalid")
    if observed.get("secret_or_identity_data_present") is not False:
        errors.append("secret_screen_not_fail_closed")

    values = checkpoint.get("canonical_values", {})
    if values.get("price_usd") != 12:
        errors.append("price_value_invalid")
    if values.get("product_zip_sha256") != "3adb147dc55b671d99141281cc9849e3530a8865def543d341c326a54bcf0113":
        errors.append("product_sha_invalid")
    if values.get("outer_iphone_pack_sha256") != "c61595a1d167209dd357930242a3cdf0d439a872b5bad8246b05c2ae10d137ec":
        errors.append("outer_pack_sha_invalid")

    resume = checkpoint.get("resume", {})
    if resume.get("completed_inputs") != ["product_name", "digital_product_type"]:
        errors.append("completed_input_order_invalid")
    if "12" not in str(resume.get("exact_next_action", "")) or "Next: Customize" not in str(resume.get("exact_next_action", "")):
        errors.append("exact_next_action_incomplete")
    if resume.get("final_publication") != "human_only":
        errors.append("final_publication_boundary_invalid")
    continuous = resume.get("end_to_end_handoff", {})
    if continuous.get("interaction_model") != "continue_through_ordinary_listing_screens_without_waiting_for_chat":
        errors.append("continuous_handoff_missing")
    if continuous.get("final_completion_signal") != "public Gumroad product URL only":
        errors.append("continuous_completion_signal_invalid")

    manual = listing.get("manual_fallback", {})
    if manual.get("observed_screen") != "new_product_price_entry" or manual.get("next_price_usd") != 12:
        errors.append("listing_checkpoint_mismatch")
    if current.get("sales_channels", {}).get("gumroad", {}).get("manual_checkpoint") != "state/gumroad_manual_checkpoint.json":
        errors.append("current_checkpoint_pointer_missing")
    if control.get("authentication_handoff", {}).get("checkpoint") != "state/gumroad_manual_checkpoint.json":
        errors.append("control_checkpoint_pointer_missing")

    for fragment in (
        "Current Price screen",
        "Enter `12`",
        "Next: Customize",
        "Do not re-enter the name",
        "Final publication remains a user-only action",
        "Finish without waiting for another chat reply",
        "Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.1.zip",
        "Gumroad_iPhone_Listing_Pack_v1.1.zip",
        "Content screen",
        "7-day refund period",
        "Test purchase",
        "Copy URL",
    ):
        if fragment not in handoff:
            errors.append(f"handoff_fragment_missing:{fragment}")

    serialized = json.dumps(checkpoint, ensure_ascii=False).lower()
    for forbidden in ("password", "one_time_code", "access_token", "cookie_value", "bank_account"):
        if forbidden in serialized:
            errors.append(f"forbidden_sensitive_field:{forbidden}")

    payload = {"ok": not errors, "errors": errors}
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
