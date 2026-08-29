from itertools import product
from collections import Counter

FAULT = ["none", "after_first_shard", "after_both_shards"]
GCPOINT = ["none", "before_first_shard", "between_shards", "after_both_before_commit"]
GCTARGET = ["A", "B"]
RATE = ["none", "A", "B"]
RESP = ["none", "first_shard", "second_shard", "commit"]
TAKEOVER = ["current", "stale"]
OVERLAP = ["none", "same_id", "new_id"]
ABORT = ["no", "before_commit"]
SCENARIOS = list(product(FAULT, GCPOINT, GCTARGET, RATE, RESP, TAKEOVER, OVERLAP, ABORT))
STRATEGIES = ["global_publish_before_bridges", "sequential_bridges_no_intent",
              "durable_intent_bridges_commit", "global_single_ref_atomic", "fail_closed"]

def evaluate(s, name):
    fault, gcp, gct, rate, resp, takeover, overlap, abort = s
    out = Counter(partial_authoritative_promotion=0, live_root_deleted_by_gc=0,
                  orphan_prepared=0, duplicate_promotion=0, false_blockage=0,
                  stale_authority_commit=0, promotion_committed=0, promotion_blocked=0,
                  dead_copy_deleted_by_gc=0, response_reconcile=0, recovery_reads=0)
    copy = {"A": True, "B": True}
    fenced, global_live = set(), set()
    blocked_gc_precommit = 0
    stopped = False
    durable_intent = name == "durable_intent_bridges_commit"

    def gc():
        nonlocal blocked_gc_precommit
        if gcp == "none": return
        t = gct
        if name == "global_single_ref_atomic":
            if t in global_live: return
            if copy[t]: copy[t] = False; out["dead_copy_deleted_by_gc"] = 1
            return
        if name == "fail_closed": return
        if t in fenced:
            if t not in global_live: blocked_gc_precommit = 1
            return
        if t in global_live:
            if copy[t]: copy[t] = False; out["live_root_deleted_by_gc"] = 1
        elif copy[t]:
            copy[t] = False; out["dead_copy_deleted_by_gc"] = 1

    def bridge(t, response_name):
        nonlocal stopped
        if stopped: return False
        if rate == t or not copy[t]: stopped = True; return False
        if takeover == "stale" and durable_intent: out["recovery_reads"] += 1
        fenced.add(t)
        if resp == response_name:
            out["response_reconcile"] = 1; out["recovery_reads"] += 1
        return True

    if name == "fail_closed":
        out["promotion_blocked"] = 1; out["recovery_reads"] = 1; return out

    if name == "global_single_ref_atomic":
        out["recovery_reads"] = 1
        if gcp == "before_first_shard": gc()
        if not all(copy.values()) or abort == "before_commit":
            out["promotion_blocked"] = 1; return out
        global_live = {"A", "B"}; out["promotion_committed"] = 1
        if resp == "commit": out["response_reconcile"] = 1; out["recovery_reads"] += 1
        if overlap == "new_id": out["recovery_reads"] += 1
        if gcp in ("between_shards", "after_both_before_commit"): gc()
        return out

    if name == "global_publish_before_bridges":
        global_live = {"A", "B"}; out["promotion_committed"] = 1
        if takeover == "stale" or abort == "before_commit": out["stale_authority_commit"] = 1
        if resp == "commit" or overlap == "new_id": out["duplicate_promotion"] = 1
        if gcp == "before_first_shard": gc()
        bridge("A", "first_shard")
        if fault == "after_first_shard": stopped = True
        if gcp == "between_shards": gc()
        if not stopped: bridge("B", "second_shard")
        if fault == "after_both_shards": stopped = True
        if gcp == "after_both_before_commit": gc()
        if fenced != {"A", "B"}: out["partial_authoritative_promotion"] = 1
        out["recovery_reads"] += 1
        return out

    if gcp == "before_first_shard": gc()
    bridge("A", "first_shard")
    if fault == "after_first_shard": stopped = True
    if gcp == "between_shards": gc()
    if not stopped: bridge("B", "second_shard")
    if fault == "after_both_shards": stopped = True
    if gcp == "after_both_before_commit": gc()

    can_commit = (not stopped and fenced == {"A", "B"} and all(copy.values()) and abort != "before_commit")
    if can_commit:
        global_live = {"A", "B"}; out["promotion_committed"] = 1
        if name == "sequential_bridges_no_intent":
            if takeover == "stale": out["stale_authority_commit"] = 1
            if resp == "commit" or overlap == "new_id": out["duplicate_promotion"] = 1
        elif resp == "commit":
            out["response_reconcile"] = 1; out["recovery_reads"] += 1
    else:
        out["promotion_blocked"] = 1
        if name == "durable_intent_bridges_commit": out["recovery_reads"] += 1
        elif fenced: out["orphan_prepared"] = 1
    if blocked_gc_precommit and not out["promotion_committed"]: out["false_blockage"] = 1
    out["recovery_reads"] += 1
    return out

if __name__ == "__main__":
    print("scenarios", len(SCENARIOS), "strategy_evaluations", len(SCENARIOS) * len(STRATEGIES))
    for name in STRATEGIES:
        total = Counter()
        for s in SCENARIOS: total.update(evaluate(s, name))
        print(name, dict(total))
