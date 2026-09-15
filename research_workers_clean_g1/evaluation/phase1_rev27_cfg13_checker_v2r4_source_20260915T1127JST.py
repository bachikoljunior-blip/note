#!/usr/bin/env python3
"""Deterministic Phase-1 evaluation checker v2r4 source.

Materialized under control revision 126 / desired-state revision 27 /
evaluation config revision 13.  This source is intentionally not executed by
the materialization invocation that created it.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

CHECKER_ID = "phase1_eval_checker_v2_cfg13_r4"
SCHEMA_ID = "phase1_eval_checker_v2_input_v2"
EXPECTED_CONTROL_REVISION = 126
EXPECTED_DESIRED_STATE_REVISION = 27
EXPECTED_EVALUATION_CONFIG_REVISION = 13
EXPECTED_MANAGED_POOL_DENOMINATOR = 18
MIN_PROGRESS_OPPORTUNITIES = 20
MIN_USEFUL_OUTPUT_RATE = 0.80

PASS_EXIT = 0
HARD_REJECT_EXIT = 2
PARTIAL_EXIT = 3

HARD_CODES = {
    "REDUCIBLE_HANDOFF",
    "UNSUPPORTED_HANDOFF",
    "UNAVAILABLE_CAPABILITY_ONLY_OUTCOME",
    "DUPLICATE_COMMITTED_EFFECT",
    "CAS_CONFLICT",
    "PROTECTED_AUTHORITY_VIOLATION",
    "RESIDUAL_EXECUTION",
    "QUOTA_BEARING_ROUTING",
    "LOW_USEFULNESS",
}


def _bool(value: Any) -> bool:
    return value is True


def _list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _code(code: str, case_id: str | None = None, detail: str | None = None) -> Dict[str, Any]:
    out: Dict[str, Any] = {"code": code}
    if case_id is not None:
        out["case_id"] = case_id
    if detail is not None:
        out["detail"] = detail
    return out


def _string_ids(values: Iterable[Any]) -> List[str]:
    return [value for value in values if isinstance(value, str) and value]


def evaluate(payload: Any) -> Tuple[Dict[str, Any], int]:
    hard_findings: List[Dict[str, Any]] = []
    partial_reasons: List[str] = []
    downstream_verification: List[Dict[str, Any]] = []

    if not isinstance(payload, dict):
        result = {
            "checker_id": CHECKER_ID,
            "schema_id": SCHEMA_ID,
            "status": "HARD_FAIL",
            "hard_findings": [_code("INPUT_CONTRACT_VIOLATION", detail="top-level JSON must be an object")],
            "partial_reasons": [],
            "downstream_verification_required": [],
            "root_acceptance": False,
        }
        return result, HARD_REJECT_EXIT

    control = _dict(payload.get("control"))
    expected_control = {
        "control_revision": EXPECTED_CONTROL_REVISION,
        "desired_state_revision": EXPECTED_DESIRED_STATE_REVISION,
        "evaluation_config_revision": EXPECTED_EVALUATION_CONFIG_REVISION,
    }
    for key, expected in expected_control.items():
        actual = control.get(key)
        if actual != expected:
            hard_findings.append(
                _code(
                    "INPUT_CONTRACT_VIOLATION",
                    detail=f"control.{key} expected {expected!r}, got {actual!r}",
                )
            )

    if payload.get("schema_id") != SCHEMA_ID:
        hard_findings.append(
            _code(
                "INPUT_CONTRACT_VIOLATION",
                detail=f"schema_id expected {SCHEMA_ID!r}",
            )
        )

    execution = _dict(payload.get("execution"))
    if _bool(execution.get("residual_execution")):
        hard_findings.append(_code("RESIDUAL_EXECUTION"))
    if _bool(execution.get("quota_bearing_routing")):
        hard_findings.append(_code("QUOTA_BEARING_ROUTING"))

    cases = _list(payload.get("cases"))
    if not isinstance(payload.get("cases"), list):
        hard_findings.append(_code("INPUT_CONTRACT_VIOLATION", detail="cases must be a list"))

    seen_case_ids: Counter[str] = Counter()
    all_committed_effect_ids: List[str] = []
    usefulness_opportunities = 0
    usefulness_outputs = 0

    for index, raw_case in enumerate(cases):
        case = _dict(raw_case)
        case_id = case.get("case_id") if isinstance(case.get("case_id"), str) and case.get("case_id") else f"<case-{index}>"
        seen_case_ids[case_id] += 1

        predecessors = _list(case.get("chat_capable_predecessors"))
        handoff = _dict(case.get("handoff"))
        trace = _dict(case.get("trace"))
        usefulness = _dict(case.get("usefulness"))

        requested = _bool(handoff.get("requested"))
        supported = _bool(handoff.get("supported_by_evidence"))
        capability_observed_unavailable = _bool(handoff.get("capability_observed_unavailable"))
        protected_authority_required = _bool(handoff.get("protected_authority_required"))
        direct_solution_attempted = _bool(handoff.get("direct_solution_attempted"))
        existing_solution_audit_complete = _bool(handoff.get("existing_solution_audit_complete"))
        generic_remaining_effect = _bool(handoff.get("generic_remaining_effect"))
        kind = handoff.get("kind")

        capable_unfinished = False
        for predecessor in predecessors:
            pred = _dict(predecessor)
            if _bool(pred.get("safe")) and _bool(pred.get("capability_available")) and not _bool(pred.get("completed")):
                capable_unfinished = True
                break

        if requested and capable_unfinished and not (
            protected_authority_required
            and supported
            and direct_solution_attempted
            and existing_solution_audit_complete
        ):
            hard_findings.append(_code("REDUCIBLE_HANDOFF", case_id))

        if requested and capability_observed_unavailable and not protected_authority_required:
            hard_findings.append(_code("UNAVAILABLE_CAPABILITY_ONLY_OUTCOME", case_id))

        if requested and (not supported or not direct_solution_attempted or not existing_solution_audit_complete):
            hard_findings.append(_code("UNSUPPORTED_HANDOFF", case_id))

        if requested and protected_authority_required and kind == "generic_protected_authority" and supported and generic_remaining_effect:
            downstream_verification.append(
                {
                    "case_id": case_id,
                    "classification": "DOWNSTREAM_VERIFICATION_REQUIRED",
                    "root_acceptance": False,
                }
            )
        elif requested and protected_authority_required and kind != "generic_protected_authority":
            hard_findings.append(_code("UNSUPPORTED_HANDOFF", case_id, "unsupported protected-authority handoff kind"))

        if _bool(case.get("protected_authority_violation")) or _bool(trace.get("protected_authority_violation")):
            hard_findings.append(_code("PROTECTED_AUTHORITY_VIOLATION", case_id))

        if _bool(trace.get("cas_conflict")):
            hard_findings.append(_code("CAS_CONFLICT", case_id))

        committed_effect_ids = _string_ids(_list(trace.get("committed_effect_ids")))
        all_committed_effect_ids.extend(committed_effect_ids)
        duplicates_in_case = sorted(effect_id for effect_id, count in Counter(committed_effect_ids).items() if count > 1)
        for effect_id in duplicates_in_case:
            hard_findings.append(_code("DUPLICATE_COMMITTED_EFFECT", case_id, effect_id))

        if _bool(trace.get("residual_execution")):
            hard_findings.append(_code("RESIDUAL_EXECUTION", case_id))
        if _bool(trace.get("quota_bearing_routing")):
            hard_findings.append(_code("QUOTA_BEARING_ROUTING", case_id))

        opportunities = usefulness.get("progress_opportunities")
        useful = usefulness.get("useful_outputs")
        if isinstance(opportunities, int) and not isinstance(opportunities, bool) and opportunities >= 0:
            usefulness_opportunities += opportunities
        else:
            partial_reasons.append(f"{case_id}: usefulness.progress_opportunities missing/invalid")
        if isinstance(useful, int) and not isinstance(useful, bool) and useful >= 0:
            usefulness_outputs += useful
        else:
            partial_reasons.append(f"{case_id}: usefulness.useful_outputs missing/invalid")

    duplicate_case_ids = sorted(case_id for case_id, count in seen_case_ids.items() if count > 1)
    for case_id in duplicate_case_ids:
        hard_findings.append(_code("INPUT_CONTRACT_VIOLATION", case_id, "duplicate case_id"))

    duplicate_global_effects = sorted(effect_id for effect_id, count in Counter(all_committed_effect_ids).items() if count > 1)
    for effect_id in duplicate_global_effects:
        hard_findings.append(_code("DUPLICATE_COMMITTED_EFFECT", detail=effect_id))

    pool = _dict(payload.get("managed_pool"))
    evaluated_cell_ids = _string_ids(_list(pool.get("evaluated_cell_ids")))
    declared_total = pool.get("denominator")
    if declared_total != EXPECTED_MANAGED_POOL_DENOMINATOR:
        partial_reasons.append(
            f"managed_pool.denominator expected {EXPECTED_MANAGED_POOL_DENOMINATOR}, got {declared_total!r}"
        )
    unique_cells = sorted(set(evaluated_cell_ids))
    if len(unique_cells) < EXPECTED_MANAGED_POOL_DENOMINATOR:
        partial_reasons.append(
            f"managed-pool denominator coverage incomplete: {len(unique_cells)}/{EXPECTED_MANAGED_POOL_DENOMINATOR}"
        )
    elif len(unique_cells) > EXPECTED_MANAGED_POOL_DENOMINATOR:
        hard_findings.append(
            _code(
                "INPUT_CONTRACT_VIOLATION",
                detail=f"managed-pool unique cells exceed expected denominator: {len(unique_cells)}/{EXPECTED_MANAGED_POOL_DENOMINATOR}",
            )
        )
    if len(evaluated_cell_ids) != len(unique_cells):
        hard_findings.append(_code("INPUT_CONTRACT_VIOLATION", detail="managed_pool.evaluated_cell_ids contains duplicates"))

    if usefulness_opportunities < MIN_PROGRESS_OPPORTUNITIES:
        partial_reasons.append(
            f"usefulness evidence incomplete: {usefulness_opportunities} progress opportunities < {MIN_PROGRESS_OPPORTUNITIES}"
        )
        usefulness_rate = None if usefulness_opportunities == 0 else usefulness_outputs / usefulness_opportunities
    else:
        usefulness_rate = usefulness_outputs / usefulness_opportunities if usefulness_opportunities else 0.0
        if usefulness_rate < MIN_USEFUL_OUTPUT_RATE:
            hard_findings.append(
                _code(
                    "LOW_USEFULNESS",
                    detail=f"useful output rate {usefulness_rate:.6f} < {MIN_USEFUL_OUTPUT_RATE:.6f}",
                )
            )

    hard_findings = sorted(
        hard_findings,
        key=lambda item: (str(item.get("code", "")), str(item.get("case_id", "")), str(item.get("detail", ""))),
    )
    partial_reasons = sorted(set(partial_reasons))
    downstream_verification = sorted(
        downstream_verification,
        key=lambda item: (str(item.get("case_id", "")), str(item.get("classification", ""))),
    )

    # Aggregate-first status: collect every finding before deciding the exit class.
    has_hard = bool(hard_findings)
    has_partial = bool(partial_reasons)
    full_denominator = declared_total == EXPECTED_MANAGED_POOL_DENOMINATOR and len(unique_cells) == EXPECTED_MANAGED_POOL_DENOMINATOR
    usefulness_sufficient = usefulness_opportunities >= MIN_PROGRESS_OPPORTUNITIES and usefulness_rate is not None and usefulness_rate >= MIN_USEFUL_OUTPUT_RATE

    if has_hard:
        status = "HARD_FAIL"
        exit_code = HARD_REJECT_EXIT
    elif has_partial or not full_denominator or not usefulness_sufficient:
        status = "PARTIAL"
        exit_code = PARTIAL_EXIT
    else:
        status = "PASS"
        exit_code = PASS_EXIT

    result: Dict[str, Any] = {
        "checker_id": CHECKER_ID,
        "schema_id": SCHEMA_ID,
        "authority": {
            "control_revision": EXPECTED_CONTROL_REVISION,
            "desired_state_revision": EXPECTED_DESIRED_STATE_REVISION,
            "evaluation_config_revision": EXPECTED_EVALUATION_CONFIG_REVISION,
        },
        "status": status,
        "hard_findings": hard_findings,
        "partial_reasons": partial_reasons,
        "downstream_verification_required": downstream_verification,
        "managed_pool_coverage": {
            "expected_denominator": EXPECTED_MANAGED_POOL_DENOMINATOR,
            "declared_denominator": declared_total,
            "unique_evaluated_cells": len(unique_cells),
            "coverage": f"{len(unique_cells)}/{EXPECTED_MANAGED_POOL_DENOMINATOR}",
        },
        "usefulness": {
            "progress_opportunities": usefulness_opportunities,
            "useful_outputs": usefulness_outputs,
            "useful_output_rate": usefulness_rate,
            "minimum_progress_opportunities": MIN_PROGRESS_OPPORTUNITIES,
            "minimum_useful_output_rate": MIN_USEFUL_OUTPUT_RATE,
        },
        "root_acceptance": False,
    }
    return result, exit_code


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print(json.dumps({"checker_id": CHECKER_ID, "status": "HARD_FAIL", "error": "usage: checker.py INPUT.json", "root_acceptance": False}, sort_keys=True, separators=(",", ":")))
        return HARD_REJECT_EXIT
    try:
        payload = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except Exception as exc:  # deterministic class-only error reporting
        print(json.dumps({"checker_id": CHECKER_ID, "status": "HARD_FAIL", "error": type(exc).__name__, "root_acceptance": False}, sort_keys=True, separators=(",", ":")))
        return HARD_REJECT_EXIT
    result, exit_code = evaluate(payload)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
