from itertools import product
from collections import Counter
import json

AXES = {
    "pre_ticket_inflight": [0, 1, 2, 4],
    "post_ticket_local_attempts": [0, 2, 8],
    "retry_budget": [1, 2, 4, 8],
    "owner_event": ["normal", "crash", "rate_limit"],
    "takeover": [False, True],
    "response_lost": [False, True],
}
STRATEGIES = [
    "no_ticket_branch_retry",
    "cooperative_ticket_no_takeover_epoch",
    "cooperative_ticket_epoch_takeover",
    "global_root_every_admission",
    "global_serial_failclosed",
]

def evaluate(strategy, s):
    o = Counter()
    k = s["pre_ticket_inflight"]
    m = s["post_ticket_local_attempts"]
    budget = s["retry_budget"]
    interrupted = s["owner_event"] != "normal"
    active_owner = (not interrupted) or s["takeover"]

    if strategy == "no_ticket_branch_retry":
        # Adversarially place every available local commit between the wide base read
        # and ref update. Safety holds through force=false, but bounded retries can starve.
        conflicts = k + m
        if not active_owner:
            o["pending"] += 1
        elif budget > conflicts:
            o["terminal"] += 1
            o["retries"] += conflicts
            if s["response_lost"]:
                o["reconciled"] += 1
        else:
            o["retry_exhausted"] += 1
            o["pending"] += 1
            o["retries"] += budget

    elif strategy == "cooperative_ticket_no_takeover_epoch":
        # New locals observe REQUESTED and defer. Only operations already in flight
        # before the ticket can still advance the branch. Ticket is a liveness gate,
        # not the safety fence; the final wide ref update still touches all overlapping manifests.
        o["deferred_local_attempts"] += m
        if not active_owner:
            o["ticket_orphan"] += 1
            o["pending"] += 1
        elif budget > k:
            o["terminal"] += 1
            o["retries"] += k
            if interrupted and s["takeover"]:
                o["unsafe_old_owner"] += 1
            if s["response_lost"]:
                o["reconciled"] += 1
        else:
            o["retry_exhausted"] += 1
            o["pending"] += 1
            o["retries"] += budget

    elif strategy == "cooperative_ticket_epoch_takeover":
        o["deferred_local_attempts"] += m
        if not active_owner:
            o["ticket_orphan"] += 1
            o["pending"] += 1
        elif budget > k:
            o["terminal"] += 1
            o["retries"] += k
            if interrupted and s["takeover"]:
                o["takeover_reconciled"] += 1
            if s["response_lost"]:
                o["reconciled"] += 1
        else:
            o["retry_exhausted"] += 1
            o["pending"] += 1
            o["retries"] += budget

    elif strategy == "global_root_every_admission":
        # Stronger liveness fence: every local admission contends on the same root.
        o["global_hotspot_touches"] += k + m + 1
        o["deferred_local_attempts"] += k + m
        if not active_owner:
            o["ticket_orphan"] += 1
            o["pending"] += 1
        else:
            o["terminal"] += 1
            if interrupted and s["takeover"]:
                o["takeover_reconciled"] += 1
            if s["response_lost"]:
                o["reconciled"] += 1

    elif strategy == "global_serial_failclosed":
        o["global_hotspot_touches"] += 1
        o["deferred_local_attempts"] += k + m
        if interrupted:
            o["pending"] += 1
        else:
            o["terminal"] += 1
            if s["response_lost"]:
                o["pending"] += 1
                o["false_block_wide"] += 1
    return o

def run():
    scenarios = [dict(zip(AXES, vals)) for vals in product(*AXES.values())]
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
        "key_slices": {
            "no_ticket_post_ticket_stream_8_normal": {
                "scenarios": 64,
                "retry_exhausted": 64,
                "interpretation": "With up to 8 adversarial local commits available after every base read and retry budgets <=8, every bounded no-ticket wide attempt can be preempted."
            },
            "ticket_post_ticket_stream_8_normal": {
                "scenarios": 64,
                "terminal": 40,
                "retry_exhausted": 24,
                "deferred_local_attempts": 512,
                "interpretation": "Post-ticket arrivals stop increasing the conflict count; success depends only on the bounded pre-ticket in-flight set k and requires budget > k."
            },
            "epoch_takeover_after_interruption": {"scenarios": 192, "terminal": 120, "unsafe_old_owner": 0, "takeover_reconciled": 120},
            "no_epoch_takeover_after_interruption": {"scenarios": 192, "terminal": 120, "unsafe_old_owner": 120}
        },
        "scope": "Ticket protocol assumes cooperative workers read a durable REQUESTED ticket before starting a new PREPARED local transition. Safety still comes from touched-manifest SHA/ref fencing; the ticket is only a starvation-control mechanism. In-flight pre-ticket work is finite in the tested lattice."
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
