from itertools import product
from collections import Counter

MARKED_DEAD = [False, True]
CURRENT_ROOT = ["dead", "live"]
ROOT_FLIP = ["none", "becomes_live"]
PATH_EVENT = ["same", "recreated"]
SWEEPER_EPOCH = ["current", "stale"]
HEAD_EVENT = ["same", "advanced"]
DELETE_RESPONSE = ["observed_success", "applied_response_lost", "not_applied_response_lost"]
TRANSPORT = ["ok", "rate_limit"]
SCENARIOS = list(product(MARKED_DEAD, CURRENT_ROOT, ROOT_FLIP, PATH_EVENT,
                         SWEEPER_EPOCH, HEAD_EVENT, DELETE_RESPONSE, TRANSPORT))
STRATEGIES = ["age_only", "mark_sweep_unfenced", "recheck_then_contents_delete_sha",
              "single_ref_commit_fenced", "no_delete_fail_closed"]

def evaluate(s, name):
    marked_dead, current_root, root_flip, path_event, sweeper_epoch, head_event, response, transport = s
    live_final = current_root == "live" or root_flip == "becomes_live"
    dead_final = not live_final
    old_copy_exists = path_event == "same"
    out = dict(deleted_live_root=0, deleted_wrong_incarnation=0, deleted_dead_copy=0,
               leaked_dead_copy=0, duplicate_delete_attempt=0, fail_closed=0,
               false_blockage=0, reads=0)

    def apply_delete():
        if live_final: out["deleted_live_root"] = 1
        elif path_event == "recreated": out["deleted_wrong_incarnation"] = 1
        else: out["deleted_dead_copy"] = 1

    if name == "age_only":
        out["reads"] = 1
        if transport == "rate_limit": out["fail_closed"] = 1
        else:
            apply_delete()
            if response == "applied_response_lost": out["duplicate_delete_attempt"] = 1

    elif name == "mark_sweep_unfenced":
        out["reads"] = 1
        if not marked_dead:
            if dead_final and old_copy_exists: out["leaked_dead_copy"] = 1
        elif transport == "rate_limit":
            out["fail_closed"] = 1
            if dead_final and old_copy_exists: out["leaked_dead_copy"] = 1
        else:
            apply_delete()
            if response == "applied_response_lost": out["duplicate_delete_attempt"] = 1

    elif name == "recheck_then_contents_delete_sha":
        out["reads"] = 3
        if transport == "rate_limit" or not marked_dead or current_root == "live" or sweeper_epoch == "stale":
            out["fail_closed"] = 1
            if dead_final and old_copy_exists:
                out["leaked_dead_copy"] = 1
                if transport != "rate_limit": out["false_blockage"] = 1
        elif path_event == "recreated":
            out["fail_closed"] = 1
        else:
            apply_delete()
            if response == "applied_response_lost": out["duplicate_delete_attempt"] = 1

    elif name == "single_ref_commit_fenced":
        out["reads"] = 3
        if transport == "rate_limit" or not marked_dead or current_root == "live" or sweeper_epoch == "stale":
            out["fail_closed"] = 1
            if dead_final and old_copy_exists:
                out["leaked_dead_copy"] = 1
                if transport != "rate_limit": out["false_blockage"] = 1
        elif root_flip == "becomes_live" or path_event == "recreated" or head_event == "advanced":
            out["fail_closed"] = 1
            if dead_final and old_copy_exists:
                out["leaked_dead_copy"] = 1
                out["false_blockage"] = 1
        else:
            out["deleted_dead_copy"] = 1
            if response == "applied_response_lost": out["reads"] += 1

    else:
        out["reads"] = 1
        out["fail_closed"] = 1
        if dead_final and old_copy_exists:
            out["leaked_dead_copy"] = 1
            out["false_blockage"] = 1
    return out

if __name__ == "__main__":
    print("scenarios", len(SCENARIOS), "strategy_evaluations", len(SCENARIOS) * len(STRATEGIES))
    for name in STRATEGIES:
        total = Counter()
        for s in SCENARIOS: total.update(evaluate(s, name))
        print(name, dict(total), "avg_reads", round(total["reads"] / len(SCENARIOS), 4))
