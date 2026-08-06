#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "validation.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    required = [
        "README.md",
        "AGENTS.md",
        "OPERATIONS/CORE_DIRECTIVE.md",
        "OPERATIONS/CORE_DIRECTIVE_MIRROR.md",
        "OPERATIONS/CORE_DIRECTIVE.b64",
        "OPERATIONS/DIRECTIVE_MANIFEST.json",
        "OPERATIONS/DIRECTIVE_BOUNDARY.md",
        "OPERATIONS/ASSISTANT_OPERATING_POLICY.md",
        "state/current.json",
        "state/budget_ledger.json",
        "state/user_action_requests.json",
        "config/campaign.json",
        "content/note/title.txt",
        "content/note/free_body.txt",
        "content/note/paid_body.txt",
        "content/launch_posts.md",
        "data/metrics.csv",
    ]
    for rel in required:
        if not (ROOT / rel).is_file():
            errors.append(f"missing:{rel}")

    state = load_json(ROOT / "state/current.json")
    campaign = load_json(ROOT / "config/campaign.json")
    manifest = load_json(ROOT / "OPERATIONS/DIRECTIVE_MANIFEST.json")
    ledger = load_json(ROOT / "state/budget_ledger.json")
    title = (ROOT / "content/note/title.txt").read_text(encoding="utf-8").strip()
    url = campaign["channels"]["note_product_url"]

    if title != campaign["product"]["title"]:
        errors.append("title_mismatch")
    if state["publication"]["article_url"] != url:
        errors.append("note_url_mismatch")
    if state["publication"]["launch_price_yen"] != campaign["product"]["launch_price_yen"]:
        errors.append("launch_price_mismatch")
    if not re.fullmatch(r"https://note\.com/[A-Za-z0-9_]+/n/n[A-Za-z0-9]+", url):
        errors.append("invalid_note_url")

    directive_state = state.get("directive_system", {}).get("user_permanent_directive", {})
    if directive_state.get("version") != manifest.get("directive_version"):
        errors.append("directive_version_state_mismatch")
    if directive_state.get("sha256_utf8") != manifest.get("expected_sha256_utf8"):
        errors.append("directive_hash_state_mismatch")
    if directive_state.get("instruction_count") != manifest.get("expected_instruction_count"):
        errors.append("directive_instruction_count_state_mismatch")
    if state.get("directive_system", {}).get("assistant_operating_policy", {}).get("classification") != "assistant_created_mutable_not_permanent_directive":
        errors.append("assistant_policy_classification_missing")

    baseline = ledger.get("chatgpt_baseline", {})
    if baseline.get("monthly_yen") != 30000:
        errors.append("chatgpt_baseline_not_30000")
    if baseline.get("paid_by_user_when_revenue_is_zero") is not True:
        errors.append("chatgpt_zero_revenue_payment_flag_missing")

    revenue = ledger.get("revenue", {})
    costs = ledger.get("reserves_and_costs", {})
    computed_spendable = max(
        0,
        int(revenue.get("realized_net_before_baseline_yen", 0))
        - int(costs.get("chatgpt_reserved_from_revenue_yen", 0))
        - int(costs.get("other_committed_costs_yen", 0))
        - int(costs.get("other_paid_costs_yen", 0)),
    )
    if int(ledger.get("spendable_external_budget_yen", -1)) != computed_spendable:
        errors.append("budget_ledger_calculation_mismatch")
    if int(state.get("budget", {}).get("current_spendable_external_budget_yen", -1)) != computed_spendable:
        errors.append("state_budget_mismatch")
    if ledger.get("negative_balance_allowed") is not False:
        errors.append("negative_budget_must_be_disabled")

    campaign_budget = campaign.get("budget", {})
    campaign_upfront = int(campaign_budget.get("upfront_yen", 0))
    campaign_monthly = int(campaign_budget.get("monthly_yen", 0))
    if campaign_upfront < 0 or campaign_monthly < 0:
        errors.append("campaign_budget_negative")
    if campaign_upfront + campaign_monthly > computed_spendable:
        errors.append("campaign_budget_exceeds_spendable_revenue_balance")

    with (ROOT / "data/metrics.csv").open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        expected = [
            "checkpoint",
            "observed_at_utc",
            "views",
            "likes",
            "comments",
            "purchases",
            "gross_revenue_yen",
            "refunds",
            "traffic_notes",
        ]
        if reader.fieldnames != expected:
            errors.append("metrics_header_mismatch")
        for index, row in enumerate(reader, start=2):
            for key in (
                "views",
                "likes",
                "comments",
                "purchases",
                "gross_revenue_yen",
                "refunds",
            ):
                value = (row.get(key) or "").strip()
                if value and (not value.isdigit() or int(value) < 0):
                    errors.append(f"metrics_invalid:{index}:{key}")

    secret_patterns = [
        r"BEGIN [A-Z ]*PRIVATE KEY",
        r"ghp_[A-Za-z0-9]{20,}",
        r"github_pat_[A-Za-z0-9_]{20,}",
    ]
    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or ".git" in path.parts
            or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".zip"}
        ):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in secret_patterns:
            if re.search(pattern, text):
                errors.append(f"possible_secret:{path.relative_to(ROOT)}")

    if state["publication"].get("external_content_verification") != "verified":
        warnings.append("published page content is not externally verified yet")
    if manifest.get("absolute_permanence_guaranteed") is not False:
        warnings.append("absolute permanence must not be claimed")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "computed_spendable_external_budget_yen": computed_spendable,
        "directive_version": manifest.get("directive_version"),
        "errors": errors,
        "warnings": warnings,
    }
    REPORT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
