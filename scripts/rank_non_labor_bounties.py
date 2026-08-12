#!/usr/bin/env python3
"""Fail-closed ranking for AI-completable, non-labor bounty opportunities."""
from __future__ import annotations
import argparse, json
from pathlib import Path

HARD_REJECTIONS = {
    "human_only": "human-only work is outside the non-labor target",
    "secret_exfiltration": "task requests secrets or hidden instructions",
    "ongoing_user_labor": "task requires continuing user work or service delivery",
    "rights_unclear": "copyright or other required rights are not verified",
    "funding_unverified": "reward funding is not independently verified",
    "illegal_or_unsafe": "task is illegal or unsafe",
}

def rank_candidate(candidate: dict, usd_jpy: float) -> dict:
    flags = candidate.get("flags", {})
    rejected = [reason for key, reason in HARD_REJECTIONS.items() if flags.get(key)]
    missing = [label for key, label in (
        ("auth_ready", "required authentication is not ready"),
        ("environment_ready", "required execution environment is not ready"),
        ("submission_ready", "a verified submission is not ready"),
    ) if not flags.get(key, False)]
    reward = float(candidate.get("reward_usd", 0))
    fee = float(candidate.get("platform_fee_pct", 0)) / 100
    probability = float(candidate.get("success_probability", 0))
    elapsed_hours = max(float(candidate.get("estimated_hours_to_cash", 0)), 0.01)
    expected_net_yen = round(reward * (1 - fee) * usd_jpy * probability)
    status = "rejected" if rejected else "conditional" if missing else "eligible"
    return {**candidate, "status": status, "rejection_reasons": rejected,
            "missing_gates": missing, "expected_one_time_net_yen": expected_net_yen,
            "expected_yen_per_elapsed_hour": round(expected_net_yen / elapsed_hours),
            "verified_monthly_run_rate_increment_yen": 0,
            "pipeline_counted_yen": expected_net_yen if status == "eligible" else 0,
            "target_accounting_note": "One-time rewards never count as verified monthly run rate."}

def build_report(source: dict) -> dict:
    ranked = [rank_candidate(item, float(source["assumptions"]["usd_jpy"])) for item in source["candidates"]]
    ranked.sort(key=lambda item: (item["status"] != "eligible", -item["expected_yen_per_elapsed_hour"]))
    return {"schema_version": "1.0", "classification": "assistant_operational_state_not_permanent_directive",
            "observed_at_utc": source["observed_at_utc"], "assumptions": source["assumptions"],
            "ranking_rule": "eligible first, then probability-weighted net JPY divided by elapsed hours",
            "target_scope": "AI-completable rewards that do not require the user to continue working",
            "summary": {"eligible": sum(i["status"] == "eligible" for i in ranked),
                        "conditional": sum(i["status"] == "conditional" for i in ranked),
                        "rejected": sum(i["status"] == "rejected" for i in ranked),
                        "probability_weighted_pipeline_yen": sum(i["pipeline_counted_yen"] for i in ranked),
                        "verified_monthly_run_rate_increment_yen": 0}, "candidates": ranked}

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("input", type=Path); parser.add_argument("output", type=Path)
    args = parser.parse_args(); report = build_report(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__": main()
