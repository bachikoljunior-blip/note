from itertools import product
from collections import Counter

LATE = ["none", "B_late", "A_reacquire"]
STALE = [False, True]
REUSE = ["none", "A", "B"]
RRESP = ["observed_success", "applied_response_lost", "not_applied_response_lost"]
RRATE = ["none", "A"]
CLEANUP = ["keep_terminal", "delete_after_abort"]
GC = ["none", "A", "B"]
SCENARIOS = list(product(LATE, STALE, REUSE, RRESP, RRATE, CLEANUP, GC))
STRATEGIES = ["cleanup_by_delete", "release_then_abort", "abort_then_release_name_only",
              "monotonic_abort_epoch_release", "fail_closed"]

def evaluate(s, name):
    late, stale, reuse, rresp, rrate, cleanup, gct = s
    out = Counter(post_abort_resurrection=0, late_bridge_accepted=0,
                  stale_release_deleted_new_reservation=0, live_root_deleted_by_gc=0,
                  unreconstructible_orphan=0, stranded_old_reservation=0,
                  duplicate_release_attempt=0, false_blockage=0,
                  new_promotion_blocked=0, dead_copy_deleted_by_gc=0,
                  recovery_reads=0, terminal_witness_retained=0)
    res = {"A": "P", "B": None}
    intent = "PREPARED"
    compact_terminal = False
    new_live = set()

    def accept_old_bridge(target):
        if res[target] is None:
            res[target] = "P"; out["late_bridge_accepted"] = 1; return True
        return False

    def release_A_name():
        if rrate == "A": return
        if rresp != "not_applied_response_lost": res["A"] = None
        if rresp == "applied_response_lost": out["duplicate_release_attempt"] = 1

    def release_A_epoch():
        if rrate == "A": return
        if rresp != "not_applied_response_lost" and res["A"] == "P": res["A"] = None
        if rresp in ("applied_response_lost", "not_applied_response_lost"):
            out["recovery_reads"] += 1
            if rresp == "not_applied_response_lost" and res["A"] == "P": res["A"] = None

    if name == "fail_closed":
        if reuse == "A": out["new_promotion_blocked"] = 1
        if gct == "A": out["false_blockage"] = 1
        out["recovery_reads"] = 1; return out

    blind_retry_pending = False
    if name == "cleanup_by_delete":
        intent = None
        if late == "B_late" or (stale and late == "none"):
            accept_old_bridge("B")
        elif late == "A_reacquire":
            release_A_name(); blind_retry_pending = rresp == "applied_response_lost"; accept_old_bridge("A")
        else:
            release_A_name(); blind_retry_pending = rresp == "applied_response_lost"
    elif name == "release_then_abort":
        release_A_name(); blind_retry_pending = rresp == "applied_response_lost"
        if late == "A_reacquire" or (stale and late == "none"): accept_old_bridge("A")
        elif late == "B_late": accept_old_bridge("B")
        intent = "ABORTED"
        if cleanup == "delete_after_abort": intent = None
        else: out["terminal_witness_retained"] = 1
    elif name == "abort_then_release_name_only":
        intent = "ABORTED"
        if cleanup == "delete_after_abort": intent = None
        else: out["terminal_witness_retained"] = 1
        if intent is None and (late != "none" or stale):
            accept_old_bridge("B" if late == "B_late" else "A")
        release_A_name(); blind_retry_pending = rresp == "applied_response_lost"
    elif name == "monotonic_abort_epoch_release":
        intent = "ABORTED"; compact_terminal = True; out["terminal_witness_retained"] = 1
        release_A_epoch()

    if intent in ("ABORTED", None) and any(v == "P" for v in res.values()) and out["late_bridge_accepted"]:
        out["post_abort_resurrection"] = 1

    if reuse != "none":
        if res[reuse] is None:
            res[reuse] = "N"; new_live.add(reuse)
        else:
            out["new_promotion_blocked"] = 1

    if blind_retry_pending:
        if res["A"] == "N":
            res["A"] = None; out["stale_release_deleted_new_reservation"] = 1
        elif res["A"] == "P":
            res["A"] = None

    if name in ("cleanup_by_delete", "abort_then_release_name_only") and intent is None and stale:
        if res["B"] is None:
            accept_old_bridge("B"); out["post_abort_resurrection"] = 1

    if any(v == "P" for v in res.values()):
        out["stranded_old_reservation"] = 1
        if intent is None and not compact_terminal: out["unreconstructible_orphan"] = 1

    if gct != "none":
        if gct in new_live:
            if res[gct] != "N": out["live_root_deleted_by_gc"] = 1
        elif res[gct] is None:
            out["dead_copy_deleted_by_gc"] = 1
        elif res[gct] == "P":
            out["false_blockage"] = 1

    out["recovery_reads"] += 1
    return out

if __name__ == "__main__":
    print("scenarios", len(SCENARIOS), "strategy_evaluations", len(SCENARIOS) * len(STRATEGIES))
    for name in STRATEGIES:
        total = Counter()
        for s in SCENARIOS: total.update(evaluate(s, name))
        print(name, dict(total))
