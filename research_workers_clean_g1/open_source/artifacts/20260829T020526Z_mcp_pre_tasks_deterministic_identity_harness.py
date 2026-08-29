#!/usr/bin/env python3
"""
Source-equivalent regression harness for MCP Tasks lost-CreateTaskResult recovery.

Models the exact v2.2.0 ordering observed at csharp-sdk commit
6fa3825973949a9c4f0cd8af344e15a8db09dc35:
  pre-Tasks alternate-result filter -> Tasks filter -> durable CreateTaskAsync
  -> in-memory Task.Run scheduling -> ordinary tool pipeline.

It tests a custom composition:
  * round 1 returns a signed requestState without creating a task;
  * round 2 derives deterministic taskId == server-minted op_id;
  * custom store atomically create-fails on duplicate op_id;
  * pre-Tasks filter catches that duplicate and returns the already-created handle.

This closes the unknown-handle / blind-retry duplication window, but deliberately
includes a negative fixture for the still-open durable-create -> Task.Run crash
window in stock WithTasks.
"""
from __future__ import annotations
from dataclasses import dataclass
import base64, hashlib, hmac, json, threading

SECRET = b"fixture-secret"

class ExistingOperationTask(Exception): pass
class IntentConflict(Exception): pass
class TokenRejected(Exception): pass

def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

def unb64u(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * ((4 - len(s) % 4) % 4))

def canonical(method, tool, args, principal):
    return json.dumps(
        {"method": method, "tool": tool, "args": args, "principal": principal},
        sort_keys=True, separators=(",", ":")
    ).encode()

def intent_hash(method, tool, args, principal):
    return hashlib.sha256(canonical(method, tool, args, principal)).hexdigest()

def mint_token(op_id, method, tool, args, principal, exp):
    body = {
        "v": 1, "op_id": op_id, "method": method, "tool": tool,
        "intent_hash": intent_hash(method, tool, args, principal),
        "principal": principal, "exp": exp,
    }
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    sig = hmac.new(SECRET, raw, hashlib.sha256).digest()
    return f"{b64u(raw)}.{b64u(sig)}"

def verify_token(token, method, tool, args, principal, now):
    try:
        raw64, sig64 = token.split(".")
        raw, sig = unb64u(raw64), unb64u(sig64)
    except Exception as exc:
        raise TokenRejected("malformed") from exc
    good = hmac.new(SECRET, raw, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, good):
        raise TokenRejected("signature")
    body = json.loads(raw)
    if body["exp"] < now:
        raise TokenRejected("expired")
    if body["method"] != method or body["tool"] != tool or body["principal"] != principal:
        raise TokenRejected("context")
    if body["intent_hash"] != intent_hash(method, tool, args, principal):
        raise TokenRejected("intent")
    return body

@dataclass
class TaskRow:
    task_id: str
    intent_hash: str
    principal: str
    scheduled: int = 0
    effects: int = 0

class DurableStore:
    """Atomic durable task+intent row keyed by deterministic op_id."""
    def __init__(self):
        self._lock = threading.Lock()
        self._rows = {}

    def get(self, task_id):
        with self._lock:
            row = self._rows.get(task_id)
            return None if row is None else TaskRow(**vars(row))

    def create_unique(self, op_id, ih, principal):
        with self._lock:
            old = self._rows.get(op_id)
            if old is not None:
                if old.intent_hash != ih or old.principal != principal:
                    raise IntentConflict(op_id)
                # Models CreateTaskAsync failing before stock WithTasks reaches Task.Run.
                raise ExistingOperationTask(op_id)
            row = TaskRow(op_id, ih, principal)
            self._rows[op_id] = row
            return TaskRow(**vars(row))

    def schedule_effect(self, task_id):
        with self._lock:
            row = self._rows[task_id]
            row.scheduled += 1
            row.effects += 1

class PreTasksFilter:
    def __init__(self, store):
        self.store = store
        self._counter = 0
        self._counter_lock = threading.Lock()

    def _new_op_id(self):
        with self._counter_lock:
            self._counter += 1
            return f"op_{self._counter:08d}"

    def preflight(self, method, tool, args, principal, now):
        op_id = self._new_op_id()
        return {
            "type": "input_required",
            "requestState": mint_token(op_id, method, tool, args, principal, now + 300),
        }

    def execute(self, token, method, tool, args, principal, now,
                barrier=None, crash_after_create=False):
        body = verify_token(token, method, tool, args, principal, now)
        op_id, ih = body["op_id"], body["intent_hash"]

        old = self.store.get(op_id)
        if old is not None:
            if old.intent_hash != ih or old.principal != principal:
                raise IntentConflict(op_id)
            return {"type": "task", "taskId": op_id, "recovered": True}

        # Forces both concurrent retry fixtures past the pre-check.
        if barrier is not None:
            barrier.wait()

        try:
            row = self.store.create_unique(op_id, ih, principal)
        except ExistingOperationTask:
            old = self.store.get(op_id)
            if old is None or old.intent_hash != ih or old.principal != principal:
                raise IntentConflict(op_id)
            return {"type": "task", "taskId": op_id, "recovered": True}

        # Exact stock ordering has a crash window here:
        # durable CreateTaskAsync has returned, but Task.Run has not been scheduled yet.
        if crash_after_create:
            return {"type": "crashed_after_create", "taskId": row.task_id}

        self.store.schedule_effect(row.task_id)
        return {"type": "task", "taskId": row.task_id, "recovered": False}

def mutate(token):
    a, b = token.split(".")
    raw = bytearray(unb64u(a))
    raw[-1] ^= 1
    return f"{b64u(bytes(raw))}.{b}"

def expect_reject(fn):
    try:
        fn()
    except Exception:
        return True
    return False

def main():
    passed = []
    def check(name, cond):
        assert cond, name
        passed.append(name)

    now = 1_000_000
    s = DurableStore()
    f = PreTasksFilter(s)

    pf = f.preflight("tools/call", "charge", {"amount": 10}, "alice", now)
    check("preflight_zero_task", s._rows == {})

    first = f.execute(pf["requestState"], "tools/call", "charge", {"amount": 10}, "alice", now + 1)
    row = s.get(first["taskId"])
    check("first_execute_one_schedule_one_effect",
          row.scheduled == 1 and row.effects == 1 and first["recovered"] is False)

    retry = f.execute(pf["requestState"], "tools/call", "charge", {"amount": 10}, "alice", now + 2)
    row = s.get(retry["taskId"])
    check("lost_response_retry_same_task_no_duplicate",
          retry["taskId"] == first["taskId"] and retry["recovered"]
          and row.scheduled == 1 and row.effects == 1)

    # Concurrent identical second-round retries: both pre-check absent.
    s2 = DurableStore()
    f2 = PreTasksFilter(s2)
    pf2 = f2.preflight("tools/call", "ship", {"sku": "x"}, "bob", now)
    barrier = threading.Barrier(2)
    out, errors = [], []
    def worker():
        try:
            out.append(f2.execute(
                pf2["requestState"], "tools/call", "ship", {"sku": "x"}, "bob",
                now + 1, barrier=barrier))
        except Exception as exc:
            errors.append(exc)
    threads = [threading.Thread(target=worker) for _ in range(2)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    op = verify_token(pf2["requestState"], "tools/call", "ship", {"sku": "x"}, "bob", now + 1)["op_id"]
    row = s2.get(op)
    check("concurrent_retry_atomic_conflict_one_schedule",
          not errors and len(out) == 2 and row.scheduled == 1 and row.effects == 1
          and all(x["taskId"] == op for x in out))

    # Exact stock WithTasks negative: durable create can precede Task.Run scheduling.
    s3 = DurableStore()
    f3 = PreTasksFilter(s3)
    pf3 = f3.preflight("tools/call", "ship", {"sku": "y"}, "carol", now)
    crashed = f3.execute(
        pf3["requestState"], "tools/call", "ship", {"sku": "y"}, "carol",
        now + 1, crash_after_create=True)
    row = s3.get(crashed["taskId"])
    check("create_before_schedule_orphan_window_exists",
          row is not None and row.scheduled == 0 and row.effects == 0)
    recovered_handle = f3.execute(
        pf3["requestState"], "tools/call", "ship", {"sku": "y"}, "carol", now + 2)
    row = s3.get(recovered_handle["taskId"])
    check("handle_recovery_does_not_redrive_orphan",
          recovered_handle["recovered"] and row.scheduled == 0 and row.effects == 0)

    for name, tok, method, tool, args, principal, ts in [
        ("tamper_rejected", mutate(pf["requestState"]),
         "tools/call", "charge", {"amount": 10}, "alice", now + 1),
        ("principal_rejected", pf["requestState"],
         "tools/call", "charge", {"amount": 10}, "mallory", now + 1),
        ("args_rejected", pf["requestState"],
         "tools/call", "charge", {"amount": 11}, "alice", now + 1),
        ("method_rejected", pf["requestState"],
         "prompts/get", "charge", {"amount": 10}, "alice", now + 1),
        ("tool_rejected", pf["requestState"],
         "tools/call", "refund", {"amount": 10}, "alice", now + 1),
        ("expiry_rejected", pf["requestState"],
         "tools/call", "charge", {"amount": 10}, "alice", now + 301),
    ]:
        check(name, expect_reject(
            lambda tok=tok, method=method, tool=tool, args=args, principal=principal, ts=ts:
                f.execute(tok, method, tool, args, principal, ts)))

    s4 = DurableStore()
    f4 = PreTasksFilter(s4)
    pf4 = f4.preflight("tools/call", "ship", {"sku": "z"}, "dana", now)
    body = verify_token(pf4["requestState"], "tools/call", "ship", {"sku": "z"}, "dana", now + 1)
    s4._rows[body["op_id"]] = TaskRow(body["op_id"], "wrong-intent", "dana")
    check("preexisting_task_intent_mismatch_blocked", expect_reject(
        lambda: f4.execute(pf4["requestState"], "tools/call", "ship", {"sku": "z"}, "dana", now + 1)))

    print(f"{len(passed)}/{len(passed)} PASS")
    for name in passed:
        print("PASS", name)

if __name__ == "__main__":
    main()
