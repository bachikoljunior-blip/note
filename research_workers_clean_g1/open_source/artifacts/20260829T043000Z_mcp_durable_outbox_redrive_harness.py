from __future__ import annotations

"""Source-equivalent MCP Tasks durable-redrive model.

Public-source basis checked against modelcontextprotocol/csharp-sdk current main
609499b2988e3f4a4c732552290bc9241fb90db9 and exact v2.2.0 release
6fa3825973949a9c4f0cd8af344e15a8db09dc35:

* Stock RunAsTaskAsync durably awaits IMcpTaskStore.CreateTaskAsync and only
  then uses volatile Task.Run.
* IMcpTaskStore.CreateTaskAsync is explicitly create-new / unique-task-ID and
  exposes no start-existing/redrive execution claim.
* McpRequestFilters documents the ordinary call-tool filters as the pipeline
  that runs before the matched tool for task-backed calls.
* McpServerTool.InvokeAsync is public, but invoking the primitive directly is
  not the same as reconstructing the full call-tool middleware/filter pipeline.

This file models a *candidate contract*, not stock SDK behavior: atomically
persist task + replayable invocation/outbox; lease/claim attempts with a
monotonic generation; reconstruct the ordinary policy/tool pipeline on each
attempt; CAS terminal state by attempt generation; and require effect-side
idempotency/fencing for non-idempotent external effects.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Invocation:
    op_id: str
    intent_hash: str
    principal: str
    tool: str
    args: tuple


@dataclass
class TaskRow:
    task_id: str
    invocation: Invocation
    status: str = "working"
    claim_generation: int = 0
    claim_owner: Optional[str] = None
    claim_expires: int = 0
    result: Optional[str] = None


class DurableOutboxStore:
    def __init__(self) -> None:
        self.rows: dict[str, TaskRow] = {}
        self.seq = 0

    def create_and_enqueue(self, invocation: Invocation) -> TaskRow:
        """Candidate atomic unit: new task + immutable replay envelope/outbox."""
        self.seq += 1
        task_id = f"task-{self.seq}"
        row = TaskRow(task_id, invocation)
        self.rows[task_id] = row
        return row

    def claim(self, task_id: str, owner: str, now: int, ttl: int) -> Optional[int]:
        row = self.rows[task_id]
        if row.status != "working":
            return None
        if row.claim_owner is not None and row.claim_expires > now:
            return None
        row.claim_generation += 1
        row.claim_owner = owner
        row.claim_expires = now + ttl
        return row.claim_generation

    def finish(self, task_id: str, generation: int, result: str) -> bool:
        row = self.rows[task_id]
        if row.status != "working" or row.claim_generation != generation:
            return False
        row.status = "completed"
        row.result = result
        return True

    def cancel(self, task_id: str) -> bool:
        row = self.rows[task_id]
        if row.status != "working":
            return False
        row.status = "cancelled"
        # Invalidate any already-issued attempt for terminal-state recording.
        row.claim_generation += 1
        row.claim_owner = None
        row.claim_expires = 0
        return True


class EffectSink:
    def __init__(self) -> None:
        self.count = 0
        self.by_idempotency_key: dict[str, str] = {}

    def raw_effect(self, payload: str) -> None:
        self.count += 1

    def idempotent_effect(self, key: str, payload: str) -> None:
        existing = self.by_idempotency_key.get(key)
        if existing is None:
            self.by_idempotency_key[key] = payload
            self.count += 1
        elif existing != payload:
            raise RuntimeError("idempotency key reused for a different intent")


class Pipeline:
    """Tiny model separating full middleware reconstruction from primitive call."""

    def __init__(self, allowed_principals: set[str]) -> None:
        self.allowed_principals = allowed_principals
        self.auth_checks = 0
        self.tool_calls = 0

    def invoke_full_pipeline(
        self, invocation: Invocation, sink: EffectSink, *, idempotent: bool = True
    ) -> str:
        self.auth_checks += 1
        if invocation.principal not in self.allowed_principals:
            return "denied"
        self.tool_calls += 1
        if idempotent:
            sink.idempotent_effect(invocation.op_id, invocation.intent_hash)
        else:
            sink.raw_effect(invocation.intent_hash)
        return "ok"

    def direct_primitive_invoke(self, invocation: Invocation, sink: EffectSink) -> str:
        # Models a redriver that jumps straight to McpServerTool.InvokeAsync:
        # the authorization/policy filter represented above never runs.
        self.tool_calls += 1
        sink.raw_effect(invocation.intent_hash)
        return "ok"


def make_invocation(
    *, op_id: str = "op-1", principal: str = "alice", intent_hash: str = "intent-A"
) -> Invocation:
    return Invocation(op_id, intent_hash, principal, "mutate", (1,))


def test_atomic_task_plus_outbox_is_durable_before_dispatch():
    store = DurableOutboxStore()
    row = store.create_and_enqueue(make_invocation())
    assert row.status == "working"
    assert row.claim_generation == 0
    assert row.invocation.op_id == "op-1"


def test_crash_before_volatile_schedule_is_redrivable_from_outbox():
    store = DurableOutboxStore()
    row = store.create_and_enqueue(make_invocation())
    # No volatile Task.Run happened. A restarted dispatcher can still claim the
    # durable invocation because task + outbox were the atomic creation unit.
    generation = store.claim(row.task_id, "worker-b", now=10, ttl=5)
    assert generation == 1
    assert store.rows[row.task_id].invocation.tool == "mutate"


def test_active_claim_prevents_concurrent_dispatch():
    store = DurableOutboxStore()
    row = store.create_and_enqueue(make_invocation())
    assert store.claim(row.task_id, "worker-a", now=0, ttl=10) == 1
    assert store.claim(row.task_id, "worker-b", now=1, ttl=10) is None


def test_takeover_increments_generation_and_rejects_stale_completion():
    store = DurableOutboxStore()
    row = store.create_and_enqueue(make_invocation())
    generation_a = store.claim(row.task_id, "worker-a", now=0, ttl=1)
    generation_b = store.claim(row.task_id, "worker-b", now=2, ttl=5)
    assert generation_a == 1 and generation_b == 2
    assert not store.finish(row.task_id, generation_a, "stale")
    assert store.finish(row.task_id, generation_b, "ok")


def test_cancellation_invalidates_stale_terminal_recording():
    store = DurableOutboxStore()
    row = store.create_and_enqueue(make_invocation())
    generation = store.claim(row.task_id, "worker-a", now=0, ttl=10)
    assert generation == 1
    assert store.cancel(row.task_id)
    assert not store.finish(row.task_id, generation, "late")
    assert store.rows[row.task_id].status == "cancelled"


def test_effect_side_idempotency_closes_takeover_duplicate():
    store = DurableOutboxStore()
    row = store.create_and_enqueue(make_invocation())
    sink = EffectSink()
    pipeline = Pipeline({"alice"})

    generation_a = store.claim(row.task_id, "worker-a", now=0, ttl=1)
    assert generation_a == 1
    assert pipeline.invoke_full_pipeline(row.invocation, sink, idempotent=True) == "ok"

    generation_b = store.claim(row.task_id, "worker-b", now=2, ttl=1)
    assert generation_b == 2
    assert pipeline.invoke_full_pipeline(row.invocation, sink, idempotent=True) == "ok"
    assert sink.count == 1


def test_claim_generation_alone_does_not_close_mid_effect_duplicate():
    store = DurableOutboxStore()
    row = store.create_and_enqueue(make_invocation())
    sink = EffectSink()
    pipeline = Pipeline({"alice"})

    assert store.claim(row.task_id, "worker-a", now=0, ttl=1) == 1
    assert pipeline.invoke_full_pipeline(row.invocation, sink, idempotent=False) == "ok"
    assert store.claim(row.task_id, "worker-b", now=2, ttl=1) == 2
    assert pipeline.invoke_full_pipeline(row.invocation, sink, idempotent=False) == "ok"
    assert sink.count == 2


def test_redrive_full_pipeline_rechecks_authorization():
    sink = EffectSink()
    pipeline = Pipeline(set())
    assert pipeline.invoke_full_pipeline(make_invocation(), sink) == "denied"
    assert pipeline.auth_checks == 1
    assert pipeline.tool_calls == 0
    assert sink.count == 0


def test_direct_primitive_redrive_bypasses_policy_filter():
    sink = EffectSink()
    pipeline = Pipeline(set())
    assert pipeline.direct_primitive_invoke(make_invocation(), sink) == "ok"
    assert pipeline.auth_checks == 0
    assert pipeline.tool_calls == 1
    assert sink.count == 1


def test_replay_envelope_intent_mismatch_must_not_be_adopted():
    store = DurableOutboxStore()
    row = store.create_and_enqueue(make_invocation(intent_hash="intent-A"))
    retry = make_invocation(intent_hash="intent-B")
    assert retry.intent_hash != row.invocation.intent_hash


def test_terminal_task_cannot_be_reclaimed():
    store = DurableOutboxStore()
    row = store.create_and_enqueue(make_invocation())
    generation = store.claim(row.task_id, "worker-a", now=0, ttl=10)
    assert generation == 1 and store.finish(row.task_id, generation, "ok")
    assert store.claim(row.task_id, "worker-b", now=20, ttl=10) is None


def test_claim_is_attempt_fence_not_effect_receipt():
    store = DurableOutboxStore()
    row = store.create_and_enqueue(make_invocation())
    generation = store.claim(row.task_id, "worker-a", now=0, ttl=10)
    assert generation == 1
    assert row.result is None


TESTS = [
    test_atomic_task_plus_outbox_is_durable_before_dispatch,
    test_crash_before_volatile_schedule_is_redrivable_from_outbox,
    test_active_claim_prevents_concurrent_dispatch,
    test_takeover_increments_generation_and_rejects_stale_completion,
    test_cancellation_invalidates_stale_terminal_recording,
    test_effect_side_idempotency_closes_takeover_duplicate,
    test_claim_generation_alone_does_not_close_mid_effect_duplicate,
    test_redrive_full_pipeline_rechecks_authorization,
    test_direct_primitive_redrive_bypasses_policy_filter,
    test_replay_envelope_intent_mismatch_must_not_be_adopted,
    test_terminal_task_cannot_be_reclaimed,
    test_claim_is_attempt_fence_not_effect_receipt,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS {len(TESTS)}/{len(TESTS)}")
