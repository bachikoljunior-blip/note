from itertools import product
from collections import Counter

PROMOTION = ["none", "A", "B", "both"]
OVERLAP = [False, True]
RATE = ["none", "A", "B"]
RESPONSE = ["observed_success", "applied_response_lost"]
REINC = ["none", "A", "B"]
CHURN = ["none", "global_unrelated", "A_unrelated", "B_unrelated"]
SCENARIOS = list(product(PROMOTION, OVERLAP, RATE, RESPONSE, REINC, CHURN))
STRATEGIES = ["global_single_ref_batch", "global_root_check_then_shard_delete",
              "shard_local_no_bridge", "shard_local_with_bridge", "no_delete"]

def promoted(p):
    return set() if p == "none" else ({"A", "B"} if p == "both" else {p})

def singleton(x):
    return set() if x == "none" else {x}

def evaluate(s, name):
    promotion, overlap, rate, response, reinc, churn = s
    live, rate_s, reinc_s = promoted(promotion), singleton(rate), singleton(reinc)
    out = Counter(deleted_live_root=0, deleted_dead_copy=0, wrong_incarnation_delete=0,
                  blocked_dead_copy=0, duplicate_delete_attempt=0, false_conflict_dead=0,
                  rate_limited_dead=0, publication_units=0, batch_abort=0,
                  overlap_conflict=0, response_reconcile=0, reads=0)
    targets = ["A", "B"]

    if name == "global_single_ref_batch":
        out["reads"] = 3
        if live or reinc_s or rate_s or churn != "none":
            out["batch_abort"] = 1
            for t in targets:
                if t not in live and t not in reinc_s:
                    out["blocked_dead_copy"] += 1
                    if t in rate_s: out["rate_limited_dead"] += 1
                    if churn != "none" or (live and t not in live): out["false_conflict_dead"] += 1
        else:
            out["publication_units"] = 1
            out["deleted_dead_copy"] = 2
            if overlap: out["overlap_conflict"] = 1
            if response == "applied_response_lost":
                out["reads"] += 1
                out["response_reconcile"] = 1

    elif name == "global_root_check_then_shard_delete":
        out["reads"] = 4
        for t in targets:
            if t not in rate_s and t not in reinc_s:
                out["publication_units"] += 1
                if t in live: out["deleted_live_root"] += 1
                else: out["deleted_dead_copy"] += 1
                if overlap: out["duplicate_delete_attempt"] += 1
                if response == "applied_response_lost": out["duplicate_delete_attempt"] += 1
            elif t not in live and t not in reinc_s:
                out["blocked_dead_copy"] += 1
                if t in rate_s: out["rate_limited_dead"] += 1

    elif name in ("shard_local_no_bridge", "shard_local_with_bridge"):
        out["reads"] = 4
        bridge = name == "shard_local_with_bridge"
        for t in targets:
            shard_churn = churn == f"{t}_unrelated"
            promoted_block = bridge and t in live
            can = not promoted_block and t not in rate_s and t not in reinc_s and not shard_churn
            if can:
                out["publication_units"] += 1
                if t in live: out["deleted_live_root"] += 1
                else: out["deleted_dead_copy"] += 1
                if overlap: out["overlap_conflict"] += 1
                if response == "applied_response_lost":
                    out["reads"] += 1
                    out["response_reconcile"] += 1
            elif t not in live and t not in reinc_s:
                out["blocked_dead_copy"] += 1
                if t in rate_s: out["rate_limited_dead"] += 1
                if shard_churn: out["false_conflict_dead"] += 1

    else:
        out["reads"] = 1
        out["batch_abort"] = 1
        for t in targets:
            if t not in live and t not in reinc_s: out["blocked_dead_copy"] += 1
    return out

if __name__ == "__main__":
    print("scenarios", len(SCENARIOS), "strategy_evaluations", len(SCENARIOS) * len(STRATEGIES))
    for name in STRATEGIES:
        total = Counter()
        for s in SCENARIOS: total.update(evaluate(s, name))
        print(name, dict(total))
