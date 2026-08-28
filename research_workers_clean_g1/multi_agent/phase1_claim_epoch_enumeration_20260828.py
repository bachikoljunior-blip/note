from itertools import product

ACTIONS = [
    "A_acq", "B_acq", "expire", "A_write", "B_write", "A_integrate", "B_integrate"
]


def run(seq, fenced):
    owner = None
    epoch = 0
    expired = False
    token = {"A": None, "B": None}
    results = set()
    canonical = None
    unsafe_events = []

    for index, action in enumerate(seq):
        if action.endswith("_acq"):
            worker = action[0]
            # Model atomic acquire/steal. A successful takeover increments epoch.
            if owner is None or expired:
                epoch += 1
                owner = worker
                expired = False
                token[worker] = epoch
        elif action == "expire":
            if owner is not None:
                expired = True
        elif action.endswith("_write"):
            worker = action[0]
            if token[worker] is not None:
                # Worker outputs are immutable/staged and may be written even by a stale worker.
                results.add((worker, token[worker]))
        elif action.endswith("_integrate"):
            worker = action[0]
            worker_epoch = token[worker]
            if (
                worker_epoch is not None
                and (worker, worker_epoch) in results
                and canonical is None
            ):
                current = (
                    owner == worker
                    and epoch == worker_epoch
                    and not expired
                )
                if fenced:
                    if current:
                        canonical = (worker, worker_epoch)
                else:
                    canonical = (worker, worker_epoch)
                    if not current:
                        unsafe_events.append(
                            {
                                "index": index,
                                "action": action,
                                "current_owner": owner,
                                "current_epoch": epoch,
                                "claim_expired": expired,
                                "worker_epoch": worker_epoch,
                            }
                        )

    return canonical, unsafe_events


def enumerate_length(length):
    out = {}
    for fenced in (False, True):
        total = 0
        terminal = 0
        unsafe = 0
        first_counterexample = None
        for seq in product(ACTIONS, repeat=length):
            total += 1
            canonical, unsafe_events = run(seq, fenced)
            if canonical is not None:
                terminal += 1
            if unsafe_events:
                unsafe += 1
                if first_counterexample is None:
                    first_counterexample = {
                        "sequence": list(seq),
                        "unsafe_events": unsafe_events,
                    }
        out["fenced" if fenced else "naive"] = {
            "total_action_strings": total,
            "terminal_action_strings": terminal,
            "unsafe_integration_action_strings": unsafe,
            "first_counterexample": first_counterexample,
        }
    return out


if __name__ == "__main__":
    import json

    result = {
        "scope": "Two workers, one claim, atomic acquire/steal, lease expiry, immutable staged outputs, and one canonical integration slot. Equal enumeration is a mechanism stress test, not an incidence estimate.",
        "length_5": enumerate_length(5),
        "length_6": enumerate_length(6),
        "targeted_stale_owner_trace": {
            "sequence": ["A_acq", "expire", "B_acq", "A_write", "A_integrate"],
            "naive": run(["A_acq", "expire", "B_acq", "A_write", "A_integrate"], False),
            "fenced": run(["A_acq", "expire", "B_acq", "A_write", "A_integrate"], True),
        },
    }
    print(json.dumps(result, indent=2, default=list))
