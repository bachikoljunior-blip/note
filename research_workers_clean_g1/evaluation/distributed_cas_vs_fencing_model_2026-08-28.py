"""Small state model: distributed conditional writes versus lease-only writers.

The model isolates the scientific journal/attempt-ledger mutation contract. It
shows when a storage-enforced object-generation CAS can replace a local flock,
and when an additional fencing token is necessary.

This is a model, not a deployment benchmark.
"""
from __future__ import annotations
from dataclasses import dataclass
import itertools
import json
from typing import Any


@dataclass
class ObjectState:
    generation: int = 0
    value: bytes = b""


class GenerationCASStore:
    def __init__(self) -> None:
        self.obj = ObjectState()

    def read(self) -> tuple[int, bytes]:
        return self.obj.generation, self.obj.value

    def put_if_generation(self, expected_generation: int, value: bytes) -> bool:
        if self.obj.generation != expected_generation:
            return False
        self.obj = ObjectState(self.obj.generation + 1, bytes(value))
        return True


class LeaseOnlyStore:
    """Lease ownership is not checked by the data write itself."""
    def __init__(self) -> None:
        self.value = b""
        self.current_owner = None

    def acquire(self, owner: str) -> None:
        self.current_owner = owner

    def write_without_fence(self, owner: str, value: bytes) -> bool:
        self.value = bytes(value)
        return True


class FencedStore:
    def __init__(self) -> None:
        self.value = b""
        self.last_fence = 0

    def write(self, fence: int, value: bytes) -> bool:
        if int(fence) < self.last_fence:
            return False
        self.last_fence = int(fence)
        self.value = bytes(value)
        return True


def generation_cas_two_writer_exhaustive() -> dict:
    rows = []
    for order in itertools.permutations(("A", "B")):
        s = GenerationCASStore()
        reads = {"A": s.read()[0], "B": s.read()[0]}
        success = {}
        for who in order:
            success[who] = s.put_if_generation(reads[who], who.encode())
        rows.append({
            "order": order,
            "success": success,
            "winner_count": sum(success.values()),
            "final_generation": s.obj.generation,
            "final_value": s.obj.value.decode(),
        })
    assert all(r["winner_count"] == 1 for r in rows)
    return {"cases": rows, "all_exactly_one_winner": True}


def duplicate_reservation_launch_gate() -> dict:
    s = GenerationCASStore()
    gen_a, _ = s.read()
    gen_b, _ = s.read()
    a = s.put_if_generation(gen_a, b"reserve:A")
    b = s.put_if_generation(gen_b, b"reserve:B")
    launches = int(a) + int(b)
    assert launches == 1
    return {
        "a_reserve_success": a,
        "b_reserve_success": b,
        "scorer_launches_if_only_success_mints_permit": launches,
        "final_generation": s.obj.generation,
    }


def lost_ack_fail_closed() -> dict:
    s = GenerationCASStore()
    g, _ = s.read()
    first = s.put_if_generation(g, b"reservation:attempt-1")
    retry = s.put_if_generation(g, b"reservation:attempt-1")
    g2, v2 = s.read()
    assert first and not retry and v2 == b"reservation:attempt-1"
    return {
        "first_storage_mutation_succeeded": first,
        "retry_with_stale_generation_succeeded": retry,
        "durable_identity_matches": v2 == b"reservation:attempt-1",
        "recovery_policy": "fail_closed_no_new_stochastic_launch_permit",
        "generation": g2,
    }


def lease_counterexample() -> dict:
    s = LeaseOnlyStore()
    s.acquire("A")
    s.acquire("B")
    b = s.write_without_fence("B", b"new")
    a = s.write_without_fence("A", b"stale")
    assert a and b and s.value == b"stale"
    return {
        "new_owner_write_succeeded": b,
        "stale_owner_write_succeeded": a,
        "final_value": s.value.decode(),
        "unsafe": True,
    }


def fencing_counterexample_repaired() -> dict:
    s = FencedStore()
    b = s.write(2, b"new")
    a = s.write(1, b"stale")
    assert b and not a and s.value == b"new"
    return {
        "new_fence_write_succeeded": b,
        "stale_fence_write_succeeded": a,
        "final_value": s.value.decode(),
        "safe_against_stale_fence": True,
    }


def main() -> None:
    out = {
        "schema_version": 1,
        "generation_cas": generation_cas_two_writer_exhaustive(),
        "duplicate_reservation": duplicate_reservation_launch_gate(),
        "lost_ack": lost_ack_fail_closed(),
        "lease_only": lease_counterexample(),
        "fencing": fencing_counterexample_repaired(),
        "derived_rule": (
            "For journal/ledger objects, a storage-enforced atomic generation/ETag CAS "
            "is sufficient to reject stale same-object writers if every scientific mutation "
            "uses the precondition and scorer launch is causally downstream of a uniquely "
            "successful durable reservation. A lease without data-plane enforcement is not "
            "sufficient. A monotonic fence is required when the protected side effect cannot "
            "itself be guarded by the same storage CAS/version predicate."
        ),
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
