#!/usr/bin/env python3
"""SOURCE-EQUIVALENT MODEL for rmcp v3.1.4 Tasks policy/idempotency boundaries.

This is not an upstream Rust SDK executable test.  It models the exact source
shape observed at commit 4a738b9dd99eaca418b614afa433a0cbdaf8d056:
- stock-like task branch may spawn before ToolRouter.call;
- ToolRouter owns a disabled-route gate;
- RequestContext exposes JSON-RPC request id + _meta;
- CallToolRequestParams exposes request_state.

The positive candidate adds a side-effect-free signed request_state preflight,
current-policy recheck, and persistent atomic create-or-get keyed by a stable op_id.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any

SECRET = b"source-equivalent-test-key"
NOW = 2_000_000_000


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def intent_hash(method: str, tool: str, args: dict[str, Any], principal: str) -> str:
    return hashlib.sha256(canon({"m": method, "t": tool, "a": args, "p": principal}).encode()).hexdigest()


def sign_state(*, op_id: str, method: str, tool: str, args: dict[str, Any], principal: str, exp: int) -> str:
    payload = {
        "op_id": op_id,
        "method": method,
        "tool": tool,
        "args_hash": hashlib.sha256(canon(args).encode()).hexdigest(),
        "principal": principal,
        "exp": exp,
    }
    raw = canon(payload).encode()
    sig = hmac.new(SECRET, raw, hashlib.sha256).hexdigest()
    return canon({"p": payload, "s": sig})


def verify_state(token: str, *, method: str, tool: str, args: dict[str, Any], principal: str, now: int) -> dict[str, Any]:
    outer = json.loads(token)
    payload = outer["p"]
    sig = outer["s"]
    expected = hmac.new(SECRET, canon(payload).encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        raise ValueError("tampered")
    if payload["exp"] < now:
        raise ValueError("expired")
    if payload["method"] != method:
        raise ValueError("method mismatch")
    if payload["tool"] != tool:
        raise ValueError("tool mismatch")
    if payload["principal"] != principal:
        raise ValueError("principal mismatch")
    if payload["args_hash"] != hashlib.sha256(canon(args).encode()).hexdigest():
        raise ValueError("args mismatch")
    return payload


@dataclass
class TaskRow:
    task_id: str
    op_id: str
    intent: str
    scheduled: bool = False


class PersistentTaskStore:
    def __init__(self) -> None:
        self.by_op: dict[str, TaskRow] = {}
        self.effects = 0

    def create_or_get(self, *, op_id: str, intent: str) -> tuple[TaskRow, bool]:
        old = self.by_op.get(op_id)
        if old is not None:
            if old.intent != intent:
                raise ValueError("intent conflict")
            return old, False
        row = TaskRow(task_id=f"task:{op_id}", op_id=op_id, intent=intent)
        self.by_op[op_id] = row
        return row, True

    def schedule_once(self, row: TaskRow) -> None:
        if row.scheduled:
            return
        row.scheduled = True
        self.effects += 1


class Policy:
    def __init__(self) -> None:
        self.disabled: set[str] = set()

    def allow(self, tool: str) -> bool:
        return tool not in self.disabled


class ModelServer:
    def __init__(self) -> None:
        self.policy = Policy()
        self.store = PersistentTaskStore()
        self.stock_task_schedules = 0

    def sync_router_call(self, *, tool: str, args: dict[str, Any]) -> str:
        if not self.policy.allow(tool):
            raise PermissionError("tool not found")
        if tool == "slow_sum":
            _parse_sum(args)
        return "sync-ok"

    def stock_like_task_branch(self, *, tool: str, args: dict[str, Any]) -> str:
        # Models TaskDemo's branch-before-ToolRouter shape: manual parse + direct spawn.
        if tool == "slow_sum":
            _parse_sum(args)
            self.stock_task_schedules += 1
            return f"stock-task-{self.stock_task_schedules}"
        return self.sync_router_call(tool=tool, args=args)

    def round1_preflight(self, *, method: str, tool: str, args: dict[str, Any], principal: str, op_id: str) -> str:
        # Must be side-effect-free and must check current policy before issuing authority.
        if not self.policy.allow(tool):
            raise PermissionError("disabled")
        if tool == "slow_sum":
            _parse_sum(args)
        return sign_state(op_id=op_id, method=method, tool=tool, args=args, principal=principal, exp=NOW + 60)

    def round2_execute(self, *, request_state: str, method: str, tool: str, args: dict[str, Any], principal: str, now: int = NOW) -> str:
        p = verify_state(request_state, method=method, tool=tool, args=args, principal=principal, now=now)
        # Recheck *current* policy: a prior token is not current authorization.
        if not self.policy.allow(tool):
            raise PermissionError("revoked")
        ih = intent_hash(method, tool, args, principal)
        row, created = self.store.create_or_get(op_id=p["op_id"], intent=ih)
        if created:
            self.store.schedule_once(row)
        return row.task_id


def _parse_sum(args: dict[str, Any]) -> tuple[float, float]:
    if set(args) != {"a", "b"}:
        raise ValueError("malformed")
    a, b = args["a"], args["b"]
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise ValueError("malformed")
    return float(a), float(b)


def expect_raises(exc: type[BaseException], fn) -> None:
    try:
        fn()
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__}")


def run() -> None:
    tests: list[tuple[str, callable]] = []

    def T(name: str):
        def deco(fn):
            tests.append((name, fn)); return fn
        return deco

    @T("enabled sync route allowed")
    def _():
        s=ModelServer(); assert s.sync_router_call(tool="slow_sum", args={"a":1,"b":2}) == "sync-ok"

    @T("disabled sync route rejected")
    def _():
        s=ModelServer(); s.policy.disabled.add("slow_sum"); expect_raises(PermissionError, lambda: s.sync_router_call(tool="slow_sum", args={"a":1,"b":2})); assert s.stock_task_schedules == 0

    @T("disabled stock-like direct task branch bypasses router gate")
    def _():
        s=ModelServer(); s.policy.disabled.add("slow_sum"); tid=s.stock_like_task_branch(tool="slow_sum", args={"a":1,"b":2}); assert tid == "stock-task-1" and s.stock_task_schedules == 1

    @T("shared preflight rejects disabled task with zero creation/effect")
    def _():
        s=ModelServer(); s.policy.disabled.add("slow_sum"); expect_raises(PermissionError, lambda: s.round1_preflight(method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="alice",op_id="op1")); assert not s.store.by_op and s.store.effects == 0

    @T("malformed args rejected before token/task")
    def _():
        s=ModelServer(); expect_raises(ValueError, lambda: s.round1_preflight(method="tools/call",tool="slow_sum",args={"a":1},principal="alice",op_id="op1")); assert not s.store.by_op

    @T("caller meta op_id alone is transport not authority")
    def _():
        s=ModelServer(); caller_meta_op="chosen-by-client"; assert caller_meta_op not in s.store.by_op
        # No signed request_state => execute cannot proceed.
        expect_raises(Exception, lambda: s.round2_execute(request_state=caller_meta_op,method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="alice"))
        assert s.store.effects == 0

    @T("signed requestState + create-or-get survives response loss")
    def _():
        s=ModelServer(); tok=s.round1_preflight(method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="alice",op_id="op1")
        t1=s.round2_execute(request_state=tok,method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="alice")
        # Response lost; fresh JSON-RPC request correlation is irrelevant, retry same logical state.
        t2=s.round2_execute(request_state=tok,method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="alice")
        assert t1 == t2 == "task:op1" and s.store.effects == 1

    @T("args mismatch rejected")
    def _():
        s=ModelServer(); tok=s.round1_preflight(method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="alice",op_id="op1")
        expect_raises(ValueError, lambda: s.round2_execute(request_state=tok,method="tools/call",tool="slow_sum",args={"a":1,"b":3},principal="alice")); assert s.store.effects == 0

    @T("principal mismatch rejected")
    def _():
        s=ModelServer(); tok=s.round1_preflight(method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="alice",op_id="op1")
        expect_raises(ValueError, lambda: s.round2_execute(request_state=tok,method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="bob")); assert s.store.effects == 0

    @T("tool mismatch rejected")
    def _():
        s=ModelServer(); tok=s.round1_preflight(method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="alice",op_id="op1")
        expect_raises(ValueError, lambda: s.round2_execute(request_state=tok,method="tools/call",tool="other",args={"a":1,"b":2},principal="alice")); assert s.store.effects == 0

    @T("policy revoked between rounds rejects even valid prior op token")
    def _():
        s=ModelServer(); tok=s.round1_preflight(method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="alice",op_id="op1"); s.policy.disabled.add("slow_sum")
        expect_raises(PermissionError, lambda: s.round2_execute(request_state=tok,method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="alice")); assert s.store.effects == 0

    @T("tampered state rejected")
    def _():
        s=ModelServer(); tok=s.round1_preflight(method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="alice",op_id="op1")
        o=json.loads(tok); o["p"]["op_id"]="evil"; tampered=canon(o)
        expect_raises(ValueError, lambda: s.round2_execute(request_state=tampered,method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="alice")); assert s.store.effects == 0

    @T("expired state rejected")
    def _():
        s=ModelServer(); tok=sign_state(op_id="op1",method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="alice",exp=NOW-1)
        expect_raises(ValueError, lambda: s.round2_execute(request_state=tok,method="tools/call",tool="slow_sum",args={"a":1,"b":2},principal="alice",now=NOW)); assert s.store.effects == 0

    passed=0
    for name, fn in tests:
        fn(); passed += 1; print(f"PASS {passed:02d}: {name}")
    print(f"RESULT {passed}/{len(tests)} PASS")

if __name__ == "__main__":
    run()
