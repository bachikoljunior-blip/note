from itertools import product
from collections import Counter

OP = ["split", "merge"]
FAULT = ["none", "crash_after_prepare", "crash_after_one_child"]
CW = ["none", "old_mapping", "new_mapping"]
FLOOR = ["correct", "reset_or_min"]
RESP = ["observed", "applied_response_lost"]
STALE = [False, True]
RATE = ["none", "left", "right"]
INC = ["same", "recreated_aba"]
GC = ["none", "target"]
SCENARIOS = list(product(OP, FAULT, CW, FLOOR, RESP, STALE, RATE, INC, GC))
STRATEGIES = ["hash_remap_no_epoch", "forwarding_tombstone",
              "topology_prepared_committed_inherit", "dual_read_migration", "fail_closed"]

def evaluate(s, name):
    op, fault, cw, floor, resp, stale, rate, inc, gc = s
    out = Counter(stale_old_mapping_write=0, early_new_mapping_write=0,
                  duplicate_reservation=0, live_root_deleted_by_gc=0,
                  orphan_forwarding=0, recoverable_prepared=0, false_blockage=0,
                  transition_committed=0, transition_blocked=0,
                  stale_coordinator_effect=0, response_reconcile=0, recovery_reads=0)
    if name == "fail_closed":
        out["transition_blocked"] = 1; out["false_blockage"] = 1; out["recovery_reads"] = 1
        return out

    if name == "hash_remap_no_epoch":
        out["transition_committed"] = 1; out["recovery_reads"] = 1
        if stale: out["stale_coordinator_effect"] = 1
        if cw == "old_mapping":
            out["stale_old_mapping_write"] = 1; out["duplicate_reservation"] = 1
        elif cw == "new_mapping":
            out["early_new_mapping_write"] = 1; out["duplicate_reservation"] = 1
        if floor == "reset_or_min" and cw != "none": out["stale_old_mapping_write"] = 1
        if inc == "recreated_aba" and cw == "old_mapping": out["stale_old_mapping_write"] = 1
        if gc == "target" and cw != "none": out["live_root_deleted_by_gc"] = 1
        return out

    if name == "forwarding_tombstone":
        out["recovery_reads"] = 2
        if fault != "none" or rate != "none":
            out["orphan_forwarding"] = 1; out["transition_blocked"] = 1; out["false_blockage"] = 1
        else:
            out["transition_committed"] = 1
        if stale and out["transition_committed"]: out["stale_coordinator_effect"] = 1
        if cw == "new_mapping":
            out["early_new_mapping_write"] = 1
            if out["transition_blocked"]: out["duplicate_reservation"] = 1
        if floor == "reset_or_min" and out["transition_committed"]: out["stale_old_mapping_write"] = 1
        if gc == "target" and ((cw == "new_mapping" and out["transition_blocked"]) or
                                (floor == "reset_or_min" and out["transition_committed"])):
            out["live_root_deleted_by_gc"] = 1
        if resp == "applied_response_lost": out["response_reconcile"] = 1; out["recovery_reads"] += 1
        return out

    if name == "topology_prepared_committed_inherit":
        out["recovery_reads"] = 3
        can_commit = fault == "none" and rate == "none" and floor == "correct"
        if not can_commit:
            out["transition_blocked"] = 1; out["recoverable_prepared"] = 1
            if cw == "new_mapping": out["false_blockage"] = 1
            if stale: out["recovery_reads"] += 1
            return out
        out["transition_committed"] = 1
        if resp == "applied_response_lost": out["response_reconcile"] = 1; out["recovery_reads"] += 1
        if stale: out["recovery_reads"] += 1
        return out

    out["recovery_reads"] = 4
    if fault != "none" or rate != "none": out["transition_blocked"] = 1; out["false_blockage"] = 1
    else: out["transition_committed"] = 1
    if stale: out["stale_coordinator_effect"] = 1
    if cw == "old_mapping": out["stale_old_mapping_write"] = 1; out["duplicate_reservation"] = 1
    elif cw == "new_mapping": out["early_new_mapping_write"] = 1; out["duplicate_reservation"] = 1
    if gc == "target" and (rate != "none" or floor == "reset_or_min"): out["live_root_deleted_by_gc"] = 1
    if resp == "applied_response_lost": out["response_reconcile"] = 1; out["recovery_reads"] += 1
    return out

if __name__ == "__main__":
    print("scenarios", len(SCENARIOS), "strategy_evaluations", len(SCENARIOS) * len(STRATEGIES))
    for name in STRATEGIES:
        total = Counter()
        for s in SCENARIOS: total.update(evaluate(s, name))
        print(name, dict(total))
