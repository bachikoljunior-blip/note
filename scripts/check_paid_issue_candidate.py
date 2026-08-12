#!/usr/bin/env python3
"""Fail-closed eligibility gate for paid GitHub issue candidates.

The scanner deliberately consumes already-fetched JSON snapshots.  It never
claims a bounty or mutates an external repository.  Callers must independently
refresh the marketplace, upstream issue, repository and competing-PR snapshots.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


MONEY_RE = re.compile(r"(?:USD|USDC|\$)\s*([0-9]+(?:\.[0-9]{1,2})?)", re.I)


def _money(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value) if value > 0 else None
    if isinstance(value, str):
        match = MONEY_RE.search(value)
        if match:
            amount = float(match.group(1))
            return amount if amount > 0 else None
    return None


def evaluate(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic, fail-closed eligibility result."""
    blockers: list[str] = []
    marketplace = snapshot.get("marketplace") or {}
    issue = snapshot.get("issue") or {}
    repository = snapshot.get("repository") or {}
    competing_prs = snapshot.get("competing_prs")

    reward = _money(marketplace.get("reward"))
    if reward is None:
        blockers.append("reward_not_binding_or_unparseable")
    if marketplace.get("status") != "open":
        blockers.append("marketplace_not_open")
    if marketplace.get("funding_verified") is not True:
        blockers.append("funding_not_verified")
    if marketplace.get("claimable") is not True:
        blockers.append("not_currently_claimable")
    if marketplace.get("payout_terms_verified") is not True:
        blockers.append("payout_terms_not_verified")

    if issue.get("state") != "open":
        blockers.append("upstream_issue_not_open")
    if issue.get("community_prs_accepted") is not True:
        blockers.append("community_pr_acceptance_not_verified")
    if issue.get("owner_only_action_required") is True:
        blockers.append("owner_only_action_before_submission")

    if repository.get("archived") is not False:
        blockers.append("repository_archival_state_not_verified_active")
    if repository.get("push_or_pr_path_available") is not True:
        blockers.append("submission_path_not_verified")

    if not isinstance(competing_prs, list):
        blockers.append("competing_prs_not_checked")
    elif any(pr.get("state") == "open" for pr in competing_prs if isinstance(pr, dict)):
        blockers.append("competing_open_pr_exists")

    blockers = sorted(set(blockers))
    return {
        "candidate_id": snapshot.get("candidate_id"),
        "eligible": not blockers,
        "reward_usd": reward,
        "blockers": blockers,
        "external_mutation_allowed": False,
        "decision": "prepare_or_implement" if not blockers else "reject_or_recheck",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        result = evaluate(snapshot)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"eligible": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0 if result["eligible"] else 1


if __name__ == "__main__":
    sys.exit(main())
