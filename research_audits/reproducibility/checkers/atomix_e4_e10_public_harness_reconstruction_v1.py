"""Independent reconstruction of two public Atomix controlled harnesses.

Does not import Atomix. It transcribes only the public experimental contracts at
mpi-dsg/atomix@61e411be662bb021634f0e84bc184bf6074905b4:
- scripts/run_b3_irreversible.py (E4/B3 irreversible policy table)
- scripts/run_e10_annotation_errors.py (E10 deterministic seeded simulator)
"""
from __future__ import annotations

import random

ABORT_SOURCES = ("tool_failure", "losing_speculation", "stale_read", "pre_commit_veto", "timeout")
BASELINES = (
    "Tx-Full", "Saga-Compensation", "Checkpoint-Replay", "No-Tx",
    "TCC-Confirm", "Mutex+WAL+Rollback", "Atomix-MisclassifiedIrreversible",
)


def externalizes_invalid(baseline: str, abort_source: str) -> bool:
    if baseline in {"Tx-Full", "TCC-Confirm", "Mutex+WAL+Rollback"}:
        return False
    if baseline == "Atomix-MisclassifiedIrreversible":
        return abort_source in {"losing_speculation", "stale_read", "timeout"}
    if baseline == "Saga-Compensation":
        return abort_source != "pre_commit_veto"
    if baseline == "Checkpoint-Replay":
        return abort_source in {"tool_failure", "timeout"}
    if baseline == "No-Tx":
        return True
    raise ValueError(baseline)


def reconstruct_e4(trials_per_abort_source: int = 100) -> dict[str, int]:
    return {
        b: sum(externalizes_invalid(b, s) for s in ABORT_SOURCES) * trials_per_abort_source
        for b in BASELINES
    }


def reconstruct_e10(trials: int = 200) -> dict[str, tuple[int, int, int]]:
    cats = ("control", "E10-OB", "E10-TN", "E10-WC", "E10-MC")
    out = {}
    seed = 0
    for cat in cats:
        iv = leak = wait = 0
        for _ in range(trials):
            seed += 1
            rng = random.Random(seed)
            has_conflict = rng.random() < 0.3
            has_irreversible = rng.random() < 0.2
            if cat == "control":
                o = (False, False, False)
            elif cat == "E10-OB":
                o = (False, False, rng.random() < 0.5)
            elif cat == "E10-TN":
                o = (has_conflict, False, False)
            elif cat == "E10-WC":
                o = (False, has_irreversible and rng.random() < 0.4, False)
            else:
                tool_failed = rng.random() < 0.2
                o = (False, tool_failed, False)
            iv += int(o[0]); leak += int(o[1]); wait += int(o[2])
        out[cat] = (iv, leak, wait)
    return out


def main() -> None:
    e4 = reconstruct_e4()
    assert e4["Tx-Full"] == 0
    assert e4["Checkpoint-Replay"] == 200
    assert e4["Saga-Compensation"] == 400
    assert e4["No-Tx"] == 500
    assert e4["Atomix-MisclassifiedIrreversible"] == 300

    e10 = reconstruct_e10()
    assert e10["control"] == (0, 0, 0)
    assert e10["E10-OB"] == (0, 0, 95)
    assert e10["E10-TN"] == (66, 0, 0)
    assert e10["E10-WC"] == (0, 17, 0)
    assert e10["E10-MC"] == (0, 35, 0)
    print({"E4_invalid_leaks_per_500": e4, "E10_iv_leak_wait_per_200": e10})


if __name__ == "__main__":
    main()
