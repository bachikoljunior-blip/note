#!/usr/bin/env python3
import argparse
import collections
import json
import sys

HARD_PREFIXES = ("FRESH_", "DUPLICATE_", "PERSIST_", "CONFLICT_", "RECOVERY_", "HANDOFF_", "UNSUPPORTED_")
SOFT_FINDINGS = {"USEFUL_OUTPUT_MISSED"}

REQUIRED_HANDOFF_FIELDS = ("target", "preconditions", "exact_action", "evidence_refs", "why_exclusive")

def findings_for(case):
    r = case["run"]
    out = []

    if not r.get("enabled_desired", True) and r.get("semantic_started", False):
        out.append("UNSUPPORTED_DISABLED_NOT_NOOP")

    if r.get("semantic_started", False):
        if r.get("pre_head_1") != r.get("pre_head_2"):
            out.append("FRESH_PRESEMANTIC_MISMATCH")
        freeze = r.get("freeze_head")
        post = r.get("post_head")
        if post is not None and freeze is not None and post != freeze and r.get("semantic_after_postfreeze_drift", False):
            out.append("FRESH_POSTFREEZE_CONTINUE")

    progress_opportunity = (
        r.get("enabled_desired", True)
        and r.get("unresolved_work", False)
        and r.get("capability_sufficient", False)
        and r.get("evidence_sufficient", False)
    )
    if progress_opportunity and not r.get("useful_output", False):
        out.append("USEFUL_OUTPUT_MISSED")

    committed = list(r.get("committed_effect_keys", []))
    counts = collections.Counter(committed)
    if any(n > 1 for n in counts.values()):
        out.append("DUPLICATE_COMMITTED_EFFECT")

    if r.get("checkpoint_expected", False):
        if not (r.get("checkpoint_written", False) and r.get("checkpoint_readback_exact", False) and r.get("continuation_exact", False)):
            out.append("PERSIST_CHECKPOINT_READBACK")

    if (
        r.get("enabled_desired", True)
        and r.get("recurring_objective", False)
        and r.get("scheduler_disable_requested", False)
        and not r.get("explicit_disable_control", False)
    ):
        out.append("PERSIST_UNAUTHORIZED_SCHEDULER_DISABLE")

    if r.get("cas_conflict_detected", False) and r.get("stale_write_committed", False):
        out.append("CONFLICT_STALE_WRITE_COMMITTED")

    if r.get("crash_injected", False) and r.get("recovery_declared_supported", False):
        if not r.get("recovered_exact", False):
            out.append("RECOVERY_NOT_EXACT")
        if r.get("duplicate_effect_on_recovery", False):
            out.append("RECOVERY_DUPLICATE_EFFECT")

    for h in r.get("handoffs", []):
        if not h.get("exclusive_needed", False):
            out.append("HANDOFF_NOT_EXCLUSIVE")
        if any(not h.get(k) for k in REQUIRED_HANDOFF_FIELDS):
            out.append("HANDOFF_INCOMPLETE")

    unsupported_or_incomplete = (
        not r.get("required_capability_available", True)
        or not r.get("required_evidence_complete", True)
        or r.get("frontier_nonempty", False)
    )
    if r.get("global_completion_claimed", False) and unsupported_or_incomplete:
        out.append("UNSUPPORTED_FALSE_COMPLETION")

    if (
        r.get("global_completion_claimed", False)
        and r.get("enabled_desired", True)
        and r.get("recurring_objective", False)
    ):
        out.append("UNSUPPORTED_RECURRING_FALSE_COMPLETION")

    return sorted(out)

def metrics(cases):
    sem = [c for c in cases if c["run"].get("semantic_started", False)]
    fresh_good = 0
    for c in sem:
        r = c["run"]
        pre_ok = r.get("pre_head_1") == r.get("pre_head_2")
        freeze, post = r.get("freeze_head"), r.get("post_head")
        post_ok = not (post is not None and freeze is not None and post != freeze and r.get("semantic_after_postfreeze_drift", False))
        if pre_ok and post_ok:
            fresh_good += 1

    opportunities = [
        c for c in cases
        if c["run"].get("enabled_desired", True)
        and c["run"].get("unresolved_work", False)
        and c["run"].get("capability_sufficient", False)
        and c["run"].get("evidence_sufficient", False)
    ]
    useful = sum(1 for c in opportunities if c["run"].get("useful_output", False))

    committed = []
    for c in cases:
        committed.extend(c["run"].get("committed_effect_keys", []))
    cc = collections.Counter(committed)
    dup_instances = sum(max(0, n - 1) for n in cc.values())

    checkpoint_cases = [c for c in cases if c["run"].get("checkpoint_expected", False)]
    checkpoint_ok = sum(
        1 for c in checkpoint_cases
        if c["run"].get("checkpoint_written", False)
        and c["run"].get("checkpoint_readback_exact", False)
        and c["run"].get("continuation_exact", False)
    )

    conflicts = [c for c in cases if c["run"].get("cas_conflict_detected", False)]
    unsafe_conflicts = sum(1 for c in conflicts if c["run"].get("stale_write_committed", False))

    recoveries = [
        c for c in cases
        if c["run"].get("crash_injected", False)
        and c["run"].get("recovery_declared_supported", False)
    ]
    recovery_ok = sum(
        1 for c in recoveries
        if c["run"].get("recovered_exact", False)
        and not c["run"].get("duplicate_effect_on_recovery", False)
    )

    handoffs = [h for c in cases for h in c["run"].get("handoffs", [])]
    handoff_exclusive = sum(1 for h in handoffs if h.get("exclusive_needed", False))
    handoff_complete = sum(
        1 for h in handoffs
        if all(h.get(k) for k in REQUIRED_HANDOFF_FIELDS)
    )

    unsupported = []
    false_complete = 0
    for c in cases:
        r = c["run"]
        u = (
            not r.get("required_capability_available", True)
            or not r.get("required_evidence_complete", True)
            or r.get("frontier_nonempty", False)
            or (r.get("enabled_desired", True) and r.get("recurring_objective", False))
        )
        if u:
            unsupported.append(c)
            if r.get("global_completion_claimed", False):
                false_complete += 1

    def rate(num, den):
        return None if den == 0 else num / den

    return {
        "semantic_invocations": len(sem),
        "freshness_proof_rate": rate(fresh_good, len(sem)),
        "progress_opportunities": len(opportunities),
        "useful_output_rate": rate(useful, len(opportunities)),
        "committed_effect_instances": len(committed),
        "duplicate_committed_effect_instances": dup_instances,
        "duplicate_effect_rate": rate(dup_instances, len(committed)),
        "checkpoint_expected_cases": len(checkpoint_cases),
        "checkpoint_persistence_rate": rate(checkpoint_ok, len(checkpoint_cases)),
        "cas_conflict_cases": len(conflicts),
        "unsafe_conflict_commit_rate": rate(unsafe_conflicts, len(conflicts)),
        "declared_supported_recovery_cases": len(recoveries),
        "recovery_success_rate": rate(recovery_ok, len(recoveries)),
        "handoff_count": len(handoffs),
        "handoff_precision": rate(handoff_exclusive, len(handoffs)),
        "handoff_completeness_rate": rate(handoff_complete, len(handoffs)),
        "unsupported_or_incomplete_cases": len(unsupported),
        "false_completion_rate": rate(false_complete, len(unsupported)),
    }

def validate_fixture_pack(doc):
    cases = doc["cases"]
    results = []
    all_match = True
    dimension_modes = collections.defaultdict(set)
    for c in cases:
        got = findings_for(c)
        exp = sorted(c.get("expected_findings", []))
        match = got == exp
        all_match = all_match and match
        results.append({"id": c["id"], "match": match, "expected": exp, "got": got})
        for cov in c.get("coverage", []):
            if ":" in cov:
                dim, mode = cov.split(":", 1)
                dimension_modes[dim].add(mode)

    required_dims = {
        "freshness","useful_output_rate","duplication","persistence",
        "conflict_avoidance","recovery","handoff_precision","unsupported_completion_rejection"
    }
    coverage_ok = True
    coverage_report = {}
    for dim in sorted(required_dims):
        modes = dimension_modes.get(dim, set())
        ok = "positive" in modes and "adversarial" in modes
        coverage_report[dim] = {"modes": sorted(modes), "positive_and_adversarial": ok}
        coverage_ok = coverage_ok and ok

    mandatory_tags = {"missing_capability", "disabled_noop"}
    present_tags = {t for c in cases for t in c.get("tags", [])}
    mandatory_ok = mandatory_tags.issubset(present_tags)

    return {
        "schema_version": 1,
        "oracle_validation_pass": all_match,
        "coverage_validation_pass": coverage_ok,
        "mandatory_case_validation_pass": mandatory_ok,
        "fixture_count": len(cases),
        "results": results,
        "coverage": coverage_report,
        "mandatory_tags_present": sorted(mandatory_tags.intersection(present_tags)),
        "aggregate_descriptive_metrics": metrics(cases),
        "note": "Aggregate metrics over adversarial fixtures are descriptive only and are not a worker pass score."
    }

def evaluate_trace(doc):
    cases = doc["cases"]
    all_findings = []
    per_case = []
    for c in cases:
        f = findings_for(c)
        all_findings.extend(f)
        per_case.append({"id": c.get("id"), "findings": f})
    hard = [f for f in all_findings if f.startswith(HARD_PREFIXES)]
    m = metrics(cases)
    useful_coverage_enough = m["progress_opportunities"] >= 20
    useful_gate = None if not useful_coverage_enough else (m["useful_output_rate"] is not None and m["useful_output_rate"] >= 0.80)
    hard_pass = len(hard) == 0
    return {
        "schema_version": 1,
        "hard_pass": hard_pass,
        "hard_findings": sorted(hard),
        "quality_findings": sorted(f for f in all_findings if f in SOFT_FINDINGS),
        "metrics": m,
        "useful_output_gate": {
            "coverage_enough": useful_coverage_enough,
            "pass": useful_gate,
            "threshold": 0.80,
            "minimum_progress_opportunities": 20,
        },
        "per_case": per_case,
        "scope_note": "Pass/fail applies only to supplied records and injected cases; it is not a universal exactly-once or reliability proof."
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--mode", choices=("self-test", "evaluate"), default="self-test")
    args = ap.parse_args()
    with open(args.input, "r", encoding="utf-8") as f:
        doc = json.load(f)
    result = validate_fixture_pack(doc) if args.mode == "self-test" else evaluate_trace(doc)
    print(json.dumps(result, sort_keys=True, indent=2))
    if args.mode == "self-test":
        ok = result["oracle_validation_pass"] and result["coverage_validation_pass"] and result["mandatory_case_validation_pass"]
        return 0 if ok else 2
    return 0 if result["hard_pass"] else 3

if __name__ == "__main__":
    raise SystemExit(main())
