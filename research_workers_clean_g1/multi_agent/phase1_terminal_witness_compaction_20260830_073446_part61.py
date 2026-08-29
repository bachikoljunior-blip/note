from itertools import product
from collections import Counter

ACTION = ["old_bridge", "old_release"]
SLOT = ["free_dead", "new_live"]
INC = ["same", "recreated_aba"]
TOPO = ["stable", "split_inherit", "split_reset", "merge_max", "merge_min"]
SNAP = ["current", "rolled_back_domain"]
FUP = ["applied", "lag"]
FRESP = ["observed", "applied_response_lost"]
RL = ["none", "floor_read_rate_limited"]
OLD_EPOCH = [1, 2]
HIST = [1, 16, 256]
SCENARIOS = list(product(ACTION, SLOT, INC, TOPO, SNAP, FUP, FRESP, RL, OLD_EPOCH, HIST))
STRATEGIES = ["delete_all_terminal", "per_promotion_tombstone", "per_target_floor_path_local",
              "per_target_floor_stable_incarnation", "per_shard_floor_unfenced",
              "per_shard_floor_topology_fenced", "fail_closed"]

def evaluate(s, name):
    action, slot, inc, topo, snap, fup, fresp, rl, old_epoch, hist = s
    out = Counter(old_writer_acceptance=0, stale_release_new_reservation=0,
                  live_root_deleted_by_gc=0, false_blockage=0, unresolved_rollback=0,
                  retained_state_units=0, recovery_reads=0, compaction_blocked=0,
                  tombstone_retained=0)
    if snap == "rolled_back_domain":
        out["unresolved_rollback"] = 1
        if name != "fail_closed":
            if action == "old_bridge" and slot == "free_dead": out["old_writer_acceptance"] = 1
            if action == "old_release" and slot == "new_live" and inc == "recreated_aba":
                out["stale_release_new_reservation"] = 1; out["live_root_deleted_by_gc"] = 1
        else: out["false_blockage"] = 1
        if name == "per_promotion_tombstone": out["retained_state_units"] += hist
        elif name in ("per_target_floor_path_local", "per_target_floor_stable_incarnation",
                      "per_shard_floor_unfenced", "per_shard_floor_topology_fenced"):
            out["retained_state_units"] += 1
        out["recovery_reads"] += 1
        return out

    if name == "delete_all_terminal":
        if action == "old_bridge" and slot == "free_dead": out["old_writer_acceptance"] = 1
        if action == "old_release" and slot == "new_live" and inc == "recreated_aba":
            out["stale_release_new_reservation"] = 1; out["live_root_deleted_by_gc"] = 1
        out["recovery_reads"] = 1; return out

    if name == "per_promotion_tombstone":
        out["retained_state_units"] += hist; out["recovery_reads"] += 1
        if rl == "floor_read_rate_limited": out["false_blockage"] = 1
        return out

    if name == "per_target_floor_path_local":
        out["retained_state_units"] += 1; out["recovery_reads"] += 1
        if rl == "floor_read_rate_limited": out["false_blockage"] = 1; return out
        if fup == "lag" or inc == "recreated_aba":
            if action == "old_bridge" and slot == "free_dead": out["old_writer_acceptance"] = 1
            if action == "old_release" and slot == "new_live" and inc == "recreated_aba":
                out["stale_release_new_reservation"] = 1; out["live_root_deleted_by_gc"] = 1
        return out

    if name == "per_target_floor_stable_incarnation":
        out["recovery_reads"] += 1
        if rl == "floor_read_rate_limited" or fup == "lag":
            out["compaction_blocked"] = 1; out["tombstone_retained"] = 1
            out["retained_state_units"] += hist + 1
            if rl == "floor_read_rate_limited": out["false_blockage"] = 1
            return out
        out["retained_state_units"] += 1
        if fresp == "applied_response_lost": out["recovery_reads"] += 1
        return out

    if name == "per_shard_floor_unfenced":
        out["retained_state_units"] += 1; out["recovery_reads"] += 1
        if rl == "floor_read_rate_limited": out["false_blockage"] = 1; return out
        floor_bad = fup == "lag" or topo in ("split_reset", "merge_min")
        if floor_bad:
            if action == "old_bridge" and slot == "free_dead": out["old_writer_acceptance"] = 1
            if action == "old_release" and slot == "new_live" and inc == "recreated_aba":
                out["stale_release_new_reservation"] = 1; out["live_root_deleted_by_gc"] = 1
        return out

    if name == "per_shard_floor_topology_fenced":
        out["recovery_reads"] += 1
        topo_ok = topo in ("stable", "split_inherit", "merge_max")
        if rl == "floor_read_rate_limited" or fup == "lag" or not topo_ok:
            out["compaction_blocked"] = 1; out["tombstone_retained"] = 1
            out["retained_state_units"] += hist + 1
            if rl == "floor_read_rate_limited" or not topo_ok: out["false_blockage"] = 1
            return out
        out["retained_state_units"] += 1
        if fresp == "applied_response_lost": out["recovery_reads"] += 1
        return out

    out["false_blockage"] = 1; out["compaction_blocked"] = 1
    out["retained_state_units"] += hist; out["recovery_reads"] = 1
    return out

if __name__ == "__main__":
    print("scenarios", len(SCENARIOS), "strategy_evaluations", len(SCENARIOS) * len(STRATEGIES))
    for name in STRATEGIES:
        total = Counter(); current = Counter()
        for s in SCENARIOS:
            r = evaluate(s, name); total.update(r)
            if s[4] == "current": current.update(r)
        print(name, "all", dict(total), "current_authority", dict(current))
