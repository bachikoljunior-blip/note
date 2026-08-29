from itertools import product
from collections import Counter
import json

AXES = {
    "handoff": ["none", "same_role_recovery", "reassign_role"],
    "root_change_timing": ["before_check", "after_check_before_write", "after_write"],
    "old_late": [False, True],
    "unrelated_advance": [False, True],
    "response_lost": [False, True],
}
STRATEGIES = [
    "local_root_precheck",
    "local_double_precheck",
    "global_ref_from_root_head",
    "canonical_target_capability_epoch",
    "immutable_owner_same_role_only",
]

def evaluate(strategy, s):
    o = Counter()
    reassign = s["handoff"] == "reassign_role"
    changed_before_write = reassign and s["root_change_timing"] in ("before_check", "after_check_before_write")
    changed_after_check = reassign and s["root_change_timing"] == "after_check_before_write"

    if strategy == "local_root_precheck":
        if reassign and s["root_change_timing"] == "before_check":
            o["blocked_old_owner"] += 1
        else:
            o["terminal_old_path"] += 1
            if changed_after_check and s["old_late"]:
                o["unsafe_old_owner"] += 1
            if s["response_lost"]:
                o["duplicate_retry_risk"] += 1

    elif strategy == "local_double_precheck":
        # Two reads reduce exposure time but do not remove the final read->write race.
        if reassign and s["root_change_timing"] == "before_check":
            o["blocked_old_owner"] += 1
        else:
            o["terminal_old_path"] += 1
            if changed_after_check and s["old_late"]:
                o["unsafe_old_owner"] += 1
            if s["response_lost"]:
                o["reconciled"] += 1

    elif strategy == "global_ref_from_root_head":
        # Proposal commit is based on the root-current branch head. Any root change or
        # unrelated branch advance before ref publication makes force=false fail.
        if changed_before_write or s["unrelated_advance"]:
            o["ref_conflict_pending"] += 1
            if s["unrelated_advance"] and not changed_before_write:
                o["extra_conflict"] += 1
        else:
            o["terminal_old_path"] += 1
            if s["response_lost"]:
                o["reconciled"] += 1

    elif strategy == "canonical_target_capability_epoch":
        # Reassignment also changes the same canonical target manifest/epoch that the
        # effect publication CASes. Mechanically safe if such a shared target is writable.
        if changed_before_write:
            o["target_cas_conflict_pending"] += 1
        else:
            o["terminal_old_path"] += 1
            if s["response_lost"]:
                o["reconciled"] += 1

    elif strategy == "immutable_owner_same_role_only":
        if reassign:
            o["false_block_reassign"] += 1
        else:
            o["terminal_old_path"] += 1
            if s["response_lost"]:
                o["reconciled"] += 1
    return o

def run():
    scenarios = [dict(zip(AXES, values)) for values in product(*AXES.values())]
    aggregate = {}
    for strategy in STRATEGIES:
        c = Counter()
        for scenario in scenarios:
            c.update(evaluate(strategy, scenario))
        aggregate[strategy] = dict(c)
    return {
        "scenario_count": len(scenarios),
        "strategy_evaluations": len(scenarios) * len(STRATEGIES),
        "axes": AXES,
        "aggregate": aggregate,
        "key_slice": {
            "reassign_after_final_check_late_old_owner": {
                "scenarios": 4,
                "local_precheck_unsafe": 4,
                "local_double_precheck_unsafe": 4,
                "global_ref_unsafe": 0,
                "canonical_target_epoch_unsafe": 0,
            }
        },
        "deployment_boundary": {
            "global_ref": "Mechanically available repository primitive, but coarse because unrelated branch advances conflict.",
            "canonical_target_epoch": "Mechanically strong but requires both old and new owners to mutate the same canonical target authority object; current per-role CLEAN write boundaries do not expose such a shared target.",
            "immutable_owner": "Compatible with current no-shared-state CLEAN shape; role-to-role reassignment is deliberately unsupported, while same-role crash/takeover remains handled by the role slot epoch."
        }
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
