from dataclasses import dataclass
from typing import Dict, Optional
import uuid


class Conflict(Exception):
    pass


class Missing(Exception):
    pass


class Stale(Exception):
    pass


@dataclass
class TaskRow:
    task_id: str
    op_id: str
    intent: str
    status: str = "working"
    claim_generation: int = 0
    claimed: bool = False
    scheduled: bool = False
    effect_count: int = 0
    result: Optional[str] = None


class StockManager:
    """Source-equivalent model of rmcp-v3.1.4 stock TaskManager boundaries.

    It intentionally models only the properties relevant to this probe:
    process-memory storage, a fresh UUID task id per spawn, and no caller-stable
    create-or-get operation identity.
    """

    def __init__(self):
        self.tasks: Dict[str, TaskRow] = {}

    def spawn(self, intent: str) -> TaskRow:
        task_id = str(uuid.uuid4())
        row = TaskRow(task_id, task_id, intent, scheduled=True)
        self.tasks[task_id] = row
        return row

    def get(self, task_id: str) -> TaskRow:
        if task_id not in self.tasks:
            raise Missing(task_id)
        return self.tasks[task_id]


class PersistentStore:
    """Candidate application-layer persistent create-or-get boundary.

    This is NOT an rmcp stock implementation.  It separates stable handle
    recovery from execution claims and from external-effect idempotency.
    """

    def __init__(self, durable=None):
        self.rows = durable if durable is not None else {}

    def create_or_get(self, op_id: str, intent: str):
        row = self.rows.get(op_id)
        if row is None:
            row = TaskRow(op_id, op_id, intent, scheduled=False)
            self.rows[op_id] = row
            return row, True
        if row.intent != intent:
            raise Conflict((row.intent, intent))
        return row, False

    def claim(self, op_id: str):
        row = self.rows[op_id]
        if row.claimed:
            return None
        row.claimed = True
        row.claim_generation += 1
        return row.claim_generation

    def takeover(self, op_id: str):
        row = self.rows[op_id]
        row.claim_generation += 1
        row.claimed = True
        return row.claim_generation

    def complete(self, op_id: str, generation: int, result: str):
        row = self.rows[op_id]
        if generation != row.claim_generation:
            raise Stale((generation, row.claim_generation))
        row.status = "completed"
        row.result = result
        row.claimed = False

    def release(self, op_id: str, generation: int):
        row = self.rows[op_id]
        if generation == row.claim_generation:
            row.claimed = False


def test_stock_lost_response_blind_retry_duplicates():
    store = StockManager()
    first = store.spawn("sum:1+2")
    retry = store.spawn("sum:1+2")
    assert first.task_id != retry.task_id
    assert len(store.tasks) == 2


def test_stock_restart_loses_task():
    store = StockManager()
    first = store.spawn("x")
    restarted = StockManager()
    try:
        restarted.get(first.task_id)
    except Missing:
        return
    raise AssertionError("stock process restart unexpectedly retained task")


def test_persistent_create_or_get_same_handle():
    backing = {}
    store = PersistentStore(backing)
    first, first_new = store.create_or_get("op-1", "x")
    retry, retry_new = store.create_or_get("op-1", "x")
    assert first.task_id == retry.task_id == "op-1"
    assert first_new and not retry_new


def test_persistent_intent_conflict():
    store = PersistentStore()
    store.create_or_get("op-1", "x")
    try:
        store.create_or_get("op-1", "y")
    except Conflict:
        return
    raise AssertionError("intent conflict was not rejected")


def test_persistent_restart_retains_handle():
    backing = {}
    store = PersistentStore(backing)
    store.create_or_get("op-1", "x")
    restarted = PersistentStore(backing)
    row, is_new = restarted.create_or_get("op-1", "x")
    assert row.task_id == "op-1" and not is_new


def test_create_before_schedule_orphan_is_visible_but_not_live():
    store = PersistentStore()
    row, _ = store.create_or_get("op-1", "x")
    assert row.status == "working"
    assert not row.scheduled
    assert row.effect_count == 0


def test_redrive_claim_after_restart():
    backing = {}
    store = PersistentStore(backing)
    store.create_or_get("op-1", "x")
    restarted = PersistentStore(backing)
    generation = restarted.claim("op-1")
    assert generation == 1
    row = backing["op-1"]
    row.scheduled = True
    row.effect_count += 1
    restarted.complete("op-1", generation, "ok")
    assert row.status == "completed" and row.effect_count == 1


def test_concurrent_claim_single_winner():
    store = PersistentStore()
    store.create_or_get("op-1", "x")
    winner = store.claim("op-1")
    loser = store.claim("op-1")
    assert winner == 1 and loser is None


def test_stale_completion_rejected_after_takeover():
    store = PersistentStore()
    store.create_or_get("op-1", "x")
    first_generation = store.claim("op-1")
    store.release("op-1", first_generation)
    takeover_generation = store.takeover("op-1")
    try:
        store.complete("op-1", first_generation, "stale")
    except Stale:
        assert store.rows["op-1"].claim_generation == takeover_generation
        return
    raise AssertionError("stale completion was accepted")


def test_generation_fence_does_not_make_external_effect_exactly_once():
    store = PersistentStore()
    store.create_or_get("op-1", "charge")
    first_generation = store.claim("op-1")
    row = store.rows["op-1"]
    row.effect_count += 1  # stale attempt reaches non-idempotent external effect
    store.release("op-1", first_generation)
    takeover_generation = store.takeover("op-1")
    row.effect_count += 1  # retry duplicates the external effect
    store.complete("op-1", takeover_generation, "done")
    assert row.effect_count == 2


if __name__ == "__main__":
    tests = [
        value
        for name, value in list(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)}/{len(tests)} PASS")
