from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class ContractViolation(RuntimeError):
    pass


@dataclass
class Task:
    task_id: str
    status: str = "working"
    scheduled: int = 0
    effect_count: int = 0


class ConformingTaskStore:
    """Model the published IMcpTaskStore CreateTaskAsync contract: create NEW unique tasks."""
    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.seq = 0

    def create_new(self) -> Task:
        self.seq += 1
        task_id = f"task-{self.seq}"
        assert task_id not in self.tasks
        task = Task(task_id)
        self.tasks[task_id] = task
        return task

    def create_with_requested_id(self, task_id: str) -> Task:
        if task_id in self.tasks:
            raise ContractViolation("CreateTaskAsync cannot conformingly return an existing task")
        task = Task(task_id)
        self.tasks[task_id] = task
        return task


class GetOrCreateExtension(ConformingTaskStore):
    """Deliberate NON-STOCK extension: returns existing task for requested ID."""
    def create_with_requested_id(self, task_id: str) -> Task:
        existing = self.tasks.get(task_id)
        if existing is not None:
            return existing
        return super().create_with_requested_id(task_id)


@dataclass
class Claim:
    generation: int
    owner: str
    expires_at: int


class ClaimStore:
    def __init__(self):
        self.generation = 0
        self.claim: Optional[Claim] = None

    def acquire(self, owner: str, now: int, ttl: int) -> Optional[Claim]:
        if self.claim is not None and self.claim.expires_at > now:
            return None
        self.generation += 1
        self.claim = Claim(self.generation, owner, now + ttl)
        return self.claim

    def is_current(self, claim: Claim, now: int) -> bool:
        return (
            self.claim is not None
            and claim.generation == self.claim.generation
            and claim.owner == self.claim.owner
            and claim.expires_at > now
        )


class EffectSink:
    def __init__(self):
        self.raw_effects = 0
        self.by_idempotency_key: dict[str, str] = {}
        self.highest_generation: dict[str, int] = {}

    def unsafe_effect(self, payload: str) -> None:
        self.raw_effects += 1

    def idempotent_effect(self, key: str, payload: str) -> None:
        existing = self.by_idempotency_key.get(key)
        if existing is None:
            self.by_idempotency_key[key] = payload
            self.raw_effects += 1
        elif existing != payload:
            raise RuntimeError("same idempotency key reused for different intent")

    def generation_cas_effect(self, op_id: str, generation: int, payload: str) -> bool:
        highest = self.highest_generation.get(op_id, 0)
        if generation <= highest:
            return False
        self.highest_generation[op_id] = generation
        self.raw_effects += 1
        return True


@dataclass
class KV:
    value: str
    version: int
    create_revision: int
    mod_revision: int


class EtcdModel:
    """Small model for documented etcd VERSION/MOD/CREATE compares and atomic Txn."""
    def __init__(self):
        self.rev = 0
        self.kv: dict[str, KV] = {}

    def _put(self, key: str, value: str) -> KV:
        self.rev += 1
        old = self.kv.get(key)
        if old is None:
            item = KV(value=value, version=1, create_revision=self.rev, mod_revision=self.rev)
        else:
            item = KV(
                value=value,
                version=old.version + 1,
                create_revision=old.create_revision,
                mod_revision=self.rev,
            )
        self.kv[key] = item
        return item

    def put(self, key: str, value: str) -> KV:
        return self._put(key, value)

    def delete(self, key: str) -> None:
        if key in self.kv:
            self.rev += 1
            del self.kv[key]

    def range_linearizable(self, key: str) -> Optional[KV]:
        return self.kv.get(key)

    def txn_create_or_get(self, key: str, value: str) -> tuple[bool, KV]:
        # Compare VERSION(key) == 0. The whole compare + selected branch is atomic.
        current = self.kv.get(key)
        if current is None:
            return True, self._put(key, value)
        # Failure branch Range returns the current same-key value.
        return False, current

    def txn_mod_cas(self, key: str, expected_mod: int, new_value: str) -> tuple[bool, Optional[KV]]:
        current = self.kv.get(key)
        if current is None or current.mod_revision != expected_mod:
            return False, current
        return True, self._put(key, new_value)


def test_stock_create_before_schedule_orphan():
    store = ConformingTaskStore()
    task = store.create_new()  # durable create
    # crash before Task.Run equivalent
    assert task.scheduled == 0 and task.status == "working"


def test_conforming_create_rejects_same_task_redrive():
    store = ConformingTaskStore()
    store.create_with_requested_id("op-1")
    try:
        store.create_with_requested_id("op-1")
    except ContractViolation:
        return
    raise AssertionError("same existing task was incorrectly treated as a new conforming create")


def test_return_existing_enables_redrive_but_is_nonconforming_extension():
    store = GetOrCreateExtension()
    first = store.create_with_requested_id("op-1")
    second = store.create_with_requested_id("op-1")
    assert first is second
    second.scheduled += 1
    assert second.scheduled == 1


def test_generation_blocks_stale_before_start():
    claims = ClaimStore()
    stale = claims.acquire("worker-a", now=0, ttl=5)
    assert stale is not None
    fresh = claims.acquire("worker-b", now=6, ttl=5)
    assert fresh is not None and fresh.generation > stale.generation
    assert not claims.is_current(stale, now=6)
    assert claims.is_current(fresh, now=6)


def test_active_claim_prevents_concurrent_reschedule():
    claims = ClaimStore()
    first = claims.acquire("worker-a", now=0, ttl=10)
    assert first is not None
    assert claims.acquire("worker-b", now=1, ttl=10) is None


def test_no_attempt_local_generation_allows_two_workers_to_share_current_generation():
    # Merely reading "current generation" from the durable record is not an attempt identity.
    current_generation = 7
    worker_a_seen = current_generation
    worker_b_seen = current_generation
    assert worker_a_seen == worker_b_seen == current_generation


def test_lease_expiry_mid_effect_duplicates_without_effect_fence():
    sink = EffectSink()
    claims = ClaimStore()
    a = claims.acquire("a", now=0, ttl=5)
    assert a is not None and claims.is_current(a, now=0)
    # A starts an external effect; its lease then expires before it records completion.
    sink.unsafe_effect("charge")
    b = claims.acquire("b", now=6, ttl=5)
    assert b is not None
    sink.unsafe_effect("charge")
    assert sink.raw_effects == 2


def test_effect_side_idempotency_key_closes_duplicate():
    sink = EffectSink()
    sink.idempotent_effect("op-123", "charge")
    sink.idempotent_effect("op-123", "charge")
    assert sink.raw_effects == 1


def test_effect_side_generation_cas_rejects_stale():
    sink = EffectSink()
    assert sink.generation_cas_effect("op-123", 2, "write")
    assert not sink.generation_cas_effect("op-123", 1, "write")
    assert sink.raw_effects == 1


def test_generation_without_effect_dedup_not_exactly_once():
    claims = ClaimStore()
    sink = EffectSink()
    a = claims.acquire("a", now=0, ttl=1)
    assert a is not None
    sink.unsafe_effect("non-idempotent")
    b = claims.acquire("b", now=2, ttl=1)
    assert b is not None
    sink.unsafe_effect("non-idempotent")
    assert a.generation != b.generation and sink.raw_effects == 2


def test_etcd_txn_create_first_success():
    e = EtcdModel()
    created, item = e.txn_create_or_get("/ops/op-1", "intent-A")
    assert created and item.version == 1 and item.create_revision == item.mod_revision


def test_etcd_lost_response_retry_adopts_exact_existing_intent():
    e = EtcdModel()
    created, first = e.txn_create_or_get("/ops/op-1", "intent-A")
    assert created
    # Simulate response loss; retry the same atomic create-or-get.
    created2, existing = e.txn_create_or_get("/ops/op-1", "intent-A")
    assert not created2 and existing.value == "intent-A"
    assert existing.create_revision == first.create_revision


def test_etcd_existing_intent_mismatch_blocks_adoption():
    e = EtcdModel()
    e.txn_create_or_get("/ops/op-1", "intent-A")
    created, existing = e.txn_create_or_get("/ops/op-1", "intent-B")
    assert not created and existing.value != "intent-B"


def test_etcd_mod_revision_cas_rejects_stale_update():
    e = EtcdModel()
    first = e.put("/ops/op-1", "v1")
    ok, second = e.txn_mod_cas("/ops/op-1", first.mod_revision, "v2")
    assert ok and second is not None
    ok2, current = e.txn_mod_cas("/ops/op-1", first.mod_revision, "stale")
    assert not ok2 and current is not None and current.value == "v2"


def test_etcd_version_only_aba_is_insufficient_but_mod_revision_detects_recreate():
    e = EtcdModel()
    first = e.put("/ops/op-1", "v1")
    assert first.version == 1
    old_mod = first.mod_revision
    e.delete("/ops/op-1")
    recreated = e.put("/ops/op-1", "v1")
    assert recreated.version == 1  # VERSION alone has ABA ambiguity across delete/recreate.
    assert recreated.mod_revision != old_mod
    ok, _ = e.txn_mod_cas("/ops/op-1", old_mod, "stale-update")
    assert not ok


TESTS = [
    test_stock_create_before_schedule_orphan,
    test_conforming_create_rejects_same_task_redrive,
    test_return_existing_enables_redrive_but_is_nonconforming_extension,
    test_generation_blocks_stale_before_start,
    test_active_claim_prevents_concurrent_reschedule,
    test_no_attempt_local_generation_allows_two_workers_to_share_current_generation,
    test_lease_expiry_mid_effect_duplicates_without_effect_fence,
    test_effect_side_idempotency_key_closes_duplicate,
    test_effect_side_generation_cas_rejects_stale,
    test_generation_without_effect_dedup_not_exactly_once,
    test_etcd_txn_create_first_success,
    test_etcd_lost_response_retry_adopts_exact_existing_intent,
    test_etcd_existing_intent_mismatch_blocks_adoption,
    test_etcd_mod_revision_cas_rejects_stale_update,
    test_etcd_version_only_aba_is_insufficient_but_mod_revision_detects_recreate,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS {len(TESTS)}/{len(TESTS)}")
