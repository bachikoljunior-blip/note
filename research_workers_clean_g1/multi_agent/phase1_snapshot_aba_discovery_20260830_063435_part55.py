from itertools import product
import json

MUTATIONS = [("none", "none")] + [
    (kind, timing)
    for kind in ("create", "delete", "delete_recreate")
    for timing in ("before_start", "between_reads", "after_snapshot")
]
STRATEGIES = (
    "moving_main_contents",
    "recursive_pinned_tree",
    "pinned_multisubtree",
    "mixed_ref_subtrees",
    "verified_merkle_summary",
)

def scenarios():
    i = 0
    for mutation, recursive_truncated, response_restart, authority_change, checkpoint_delete_new_head, summary_lag, head_rewind_aba in product(
        MUTATIONS, (False, True), (False, True), (False, True), (False, True), (False, True), (False, True)
    ):
        i += 1
        yield {
            "id": i,
            "mutation_kind": mutation[0],
            "mutation_timing": mutation[1],
            "recursive_truncated": recursive_truncated,
            "response_loss_restart": response_restart,
            "authority_change_after_snapshot": authority_change,
            "checkpoint_delete_new_head_during_traversal": checkpoint_delete_new_head,
            "summary_lag": summary_lag,
            "head_rewind_aba": head_rewind_aba,
        }

def moving_phantoms(sc):
    timing = sc["mutation_timing"]
    kind = sc["mutation_kind"]
    inconsistent = timing in ("between_reads", "after_snapshot") or sc["head_rewind_aba"]
    omission = (
        (kind in ("delete", "delete_recreate") and timing in ("between_reads", "after_snapshot"))
        or sc["checkpoint_delete_new_head_during_traversal"]
    )
    addition = kind in ("create", "delete_recreate") and timing in ("between_reads", "after_snapshot")
    duplicate = (
        kind == "delete_recreate"
        and sc["response_loss_restart"]
        and (timing in ("between_reads", "after_snapshot") or (timing == "before_start" and sc["head_rewind_aba"]))
    )
    return inconsistent, omission, addition, duplicate

def run(sc, strategy):
    inconsistent = omission = addition = duplicate = False
    fail_closed = sc["authority_change_after_snapshot"]

    if strategy in ("moving_main_contents", "mixed_ref_subtrees"):
        inconsistent, omission, addition, duplicate = moving_phantoms(sc)
        base = 3 if strategy == "moving_main_contents" else 7
        reads = base + int(sc["response_loss_restart"]) + int(sc["head_rewind_aba"])

    elif strategy == "recursive_pinned_tree":
        reads = 2 + int(sc["recursive_truncated"])
        fail_closed = fail_closed or sc["recursive_truncated"]

    elif strategy == "pinned_multisubtree":
        reads = 5 + int(sc["response_loss_restart"])

    elif strategy == "verified_merkle_summary":
        # A stale summary is an accelerator miss, not authority. It is checked
        # against the pinned source-tree SHA and falls back to the pinned tree.
        if sc["summary_lag"]:
            reads = (4 if sc["authority_change_after_snapshot"] else 6) + int(sc["response_loss_restart"])
        else:
            reads = 3 + int(sc["response_loss_restart"])

    return {
        **sc,
        "strategy": strategy,
        "snapshot_inconsistent": inconsistent,
        "phantom_omission": omission,
        "phantom_addition": addition,
        "duplicate_discovery": duplicate,
        "false_phantom_omission": omission and not fail_closed,
        "false_phantom_addition": addition and not fail_closed,
        "false_duplicate_selection": duplicate and not fail_closed,
        "stale_selection": False,  # all strong selector rows revalidate authority
        "fail_closed": fail_closed,
        "recovery_reads": reads,
    }

def aggregate(rows):
    out = {}
    for strategy in STRATEGIES:
        rr = [r for r in rows if r["strategy"] == strategy]
        out[strategy] = {
            "scenarios": len(rr),
            "snapshot_inconsistent_scenarios": sum(r["snapshot_inconsistent"] for r in rr),
            "phantom_omission_scenarios": sum(r["phantom_omission"] for r in rr),
            "phantom_addition_scenarios": sum(r["phantom_addition"] for r in rr),
            "duplicate_discovery_scenarios": sum(r["duplicate_discovery"] for r in rr),
            "false_phantom_omission_scenarios": sum(r["false_phantom_omission"] for r in rr),
            "false_phantom_addition_scenarios": sum(r["false_phantom_addition"] for r in rr),
            "false_duplicate_selection_scenarios": sum(r["false_duplicate_selection"] for r in rr),
            "stale_selection_scenarios": sum(r["stale_selection"] for r in rr),
            "fail_closed_scenarios": sum(r["fail_closed"] for r in rr),
            "avg_recovery_reads": sum(r["recovery_reads"] for r in rr) / len(rr),
            "max_recovery_reads": max(r["recovery_reads"] for r in rr),
        }
    return out

if __name__ == "__main__":
    sc = list(scenarios())
    rows = [run(s, strategy) for s in sc for strategy in STRATEGIES]
    print(json.dumps({
        "scenario_count": len(sc),
        "strategy_evaluations": len(rows),
        "strategies": aggregate(rows),
    }, indent=2, sort_keys=True))
