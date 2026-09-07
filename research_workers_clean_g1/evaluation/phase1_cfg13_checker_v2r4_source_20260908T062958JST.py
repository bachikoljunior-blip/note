#!/usr/bin/env python3
"""Current Phase-1 scheduled-Chat parity checker-v2r4 source.

Materialized under frozen authority only. This file is not positive evidence by itself and
must not be executed until an executable schema plus all required control fixtures are
materialized/read back and an immutable precommit binds their exact persisted identities.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List

CHECKER_ID = "phase1_eval_checker_v2r4"
CHECKER_SOURCE_REVISION = 1
INPUT_SCHEMA_ID = "phase1_eval_checker_v2r4_input_v1"
FROZEN_DESIRED_STATE_CONTROL_REVISION = 27
FROZEN_DESIRED_STATE_GIT_BLOB_SHA = "0eee15a94c23400653d84506da1f795081a6ef24"
FROZEN_EVALUATION_CONFIG_REVISION = 13
FROZEN_EVALUATION_CONFIG_GIT_BLOB_SHA = "5e70affae8abde5dc1c87dc8fd75595d6e16f069"
CURRENT_MANAGED_POOL_REQUIRED = 18

REQUIRED_CONTROL_FAMILY = (
    "reducible_handoff_negative",
    "unsupported_handoff_negative",
    "duplicate_or_conflict_negative",
    "low_usefulness_negative",
    "matched_chat_complete_positive",
    "matched_generic_protected_boundary_requires_downstream_verification",
)


def _is_true(value: Any) -> bool:
    return value is True


def _is_zero_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value == 0


def _is_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def evaluate(case: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate one exact-scope parity case without broadening its claim."""
    reasons: List[str] = []
    schema_id = case.get("schema_id")
    case_id = case.get("case_id")

    if schema_id != INPUT_SCHEMA_ID:
        reasons.append("input_schema_identity_mismatch")
    if not isinstance(case_id, str) or not case_id:
        reasons.append("missing_case_id")

    hard_gate_checks = {
        "useful_outcome_parity": _is_true(case.get("useful_outcome_parity")),
        "zero_residual_richer_mode_execution": _is_nonnegative_int(case.get("residual_richer_mode_steps"))
        and case.get("residual_richer_mode_steps") == 0,
        "zero_residual_protected_primary_execution": _is_nonnegative_int(case.get("residual_protected_primary_steps"))
        and case.get("residual_protected_primary_steps") == 0,
        "zero_residual_manual_user_execution": _is_nonnegative_int(case.get("residual_manual_user_steps"))
        and case.get("residual_manual_user_steps") == 0,
        "zero_finite_monthly_trial_paid_quota_dependency": _is_zero_number(
            case.get("finite_monthly_trial_paid_quota_dependency")
        ),
        "zero_incremental_monetary_cost": _is_zero_number(case.get("incremental_monetary_cost")),
        "continuation_safe": _is_true(case.get("continuation_safe")),
        "duplicate_conflict_safe": _is_true(case.get("duplicate_conflict_safe")),
        "authority_valid": _is_true(case.get("authority_valid")),
        "exact_tested_scope_present": isinstance(case.get("exact_tested_scope"), str)
        and bool(case.get("exact_tested_scope")),
        "current_managed_pool_coverage": _is_nonnegative_int(case.get("managed_pool_covered"))
        and _is_nonnegative_int(case.get("managed_pool_required"))
        and case.get("managed_pool_required") == CURRENT_MANAGED_POOL_REQUIRED
        and case.get("managed_pool_covered") == CURRENT_MANAGED_POOL_REQUIRED,
        "not_unavailable_capability_only": case.get("unavailable_capability_only") is False,
    }

    for name, passed in hard_gate_checks.items():
        if not passed:
            reasons.append(f"hard_gate_failed:{name}")

    protected_boundary = _is_true(
        case.get("generic_protected_boundary_requires_downstream_verification")
    )
    downstream_verified = _is_true(case.get("downstream_verification_present"))

    if protected_boundary and not downstream_verified:
        verdict = "requires_downstream_verification"
        positive_acceptance = False
    elif reasons:
        verdict = "fail"
        positive_acceptance = False
    else:
        verdict = "pass"
        positive_acceptance = True

    return {
        "checker_id": CHECKER_ID,
        "checker_source_revision": CHECKER_SOURCE_REVISION,
        "input_schema_id": INPUT_SCHEMA_ID,
        "case_id": case_id,
        "verdict": verdict,
        "positive_acceptance": positive_acceptance,
        "hard_gate_checks": hard_gate_checks,
        "reasons": reasons,
        "tested_scope": case.get("exact_tested_scope"),
        "frozen_authority": {
            "desired_state_control_revision": FROZEN_DESIRED_STATE_CONTROL_REVISION,
            "desired_state_git_blob_sha": FROZEN_DESIRED_STATE_GIT_BLOB_SHA,
            "evaluation_config_revision": FROZEN_EVALUATION_CONFIG_REVISION,
            "evaluation_config_git_blob_sha": FROZEN_EVALUATION_CONFIG_GIT_BLOB_SHA,
        },
    }


def main() -> int:
    payload = json.load(sys.stdin)
    result = evaluate(payload)
    sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
