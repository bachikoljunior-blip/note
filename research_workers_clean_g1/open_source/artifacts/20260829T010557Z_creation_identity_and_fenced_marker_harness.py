"""Source-equivalent safety harness for open_source exploration.

Covers two reusable patterns:
1) MRTR preflight -> integrity-bound stable operation identity -> create-or-get.
2) Fenced event/HEAD commit marker using lease generation + expected old leaf.

Stdlib-only; exits non-zero if any fixture fails.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass, field

SECRET = b"test-secret-32-bytes-minimum........"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def mint_state(op_id, method, args, principal, exp=9_999_999_999):
    payload = {
        "op_id": op_id,
        "method": method,
        "args_hash": digest(args),
        "principal_hash": digest(principal),
        "exp": exp,
    }
    raw = canonical(payload)
    mac = hmac.new(SECRET, raw, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(raw + mac).decode()


def verify_state(token, method, args, principal, now=0):
    data = base64.urlsafe_b64decode(token.encode())
    raw, mac = data[:-32], data[-32:]
    expected = hmac.new(SECRET, raw, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected):
        raise ValueError("bad mac")
    payload = json.loads(raw)
    if payload["exp"] < now:
        raise ValueError("expired")
    if (
        payload["method"] != method
        or payload["args_hash"] != digest(args)
        or payload["principal_hash"] != digest(principal)
    ):
        raise ValueError("binding mismatch")
    return payload


@dataclass
class IdempotentStore:
    by_op: dict = field(default_factory=dict)
    tasks: dict = field(default_factory=dict)
    effects: int = 0
    seq: int = 0

    def create_or_get(self, op_id, intent_hash):
        if op_id in self.by_op:
            task_id = self.by_op[op_id]
            record = self.tasks[task_id]
            if record["intent_hash"] != intent_hash:
                raise ValueError("intent conflict")
            return task_id, False
        self.seq += 1
        task_id = f"t-{self.seq}"
        self.by_op[op_id] = task_id
        self.tasks[task_id] = {
            "task_id": task_id,
            "op_id": op_id,
            "intent_hash": intent_hash,
            "status": "working",
        }
        self.effects += 1
        return task_id, True


def preflight(method, args, principal):
    # Deliberately side-effect-free: mint only continuation identity/provenance.
    return mint_state(secrets.token_hex(8), method, args, principal)


def execute(store, token, request_id, method, args, principal):
    payload = verify_state(token, method, args, principal)
    # JSON-RPC request_id is intentionally not used as logical operation identity.
    _ = request_id
    intent_hash = digest({"method": method, "args": args, "principal": principal})
    return store.create_or_get(payload["op_id"], intent_hash)


def event_hash(event):
    return digest(event)


@dataclass
class HeadState:
    generation: int
    head: str | None
    events: dict = field(default_factory=dict)
    marker: dict | None = None


def begin_marker(state, expected_old, event):
    if state.head != expected_old:
        raise ValueError("old head mismatch")
    state.marker = {
        "generation": state.generation,
        "expected_old": expected_old,
        "event_id": event["id"],
        "event_hash": event_hash(event),
    }


def append_event(state, event):
    state.events[event["id"]] = copy.deepcopy(event)


def finish_or_recover(state):
    marker = state.marker
    if not marker:
        return "none"
    if marker["generation"] != state.generation:
        raise ValueError("generation mismatch")
    event = state.events.get(marker["event_id"])
    if event is None:
        return "pending-no-event"
    if event_hash(event) != marker["event_hash"]:
        raise ValueError("event hash mismatch")
    if event.get("parent") != marker["expected_old"]:
        raise ValueError("parent mismatch")
    if state.head == marker["event_id"]:
        state.marker = None
        return "cleared-applied"
    if state.head != marker["expected_old"]:
        raise ValueError("head moved")
    state.head = marker["event_id"]
    state.marker = None
    return "committed"


def expect_error(fn, contains):
    try:
        fn()
    except ValueError as exc:
        return contains in str(exc)
    return False


def run():
    fixtures = []

    store = IdempotentStore()
    token = preflight("tools/call", {"x": 1}, {"sub": "u"})
    fixtures.append(("preflight_no_effect", store.effects == 0))
    t1, first = execute(store, token, 1, "tools/call", {"x": 1}, {"sub": "u"})
    t2, second = execute(store, token, 2, "tools/call", {"x": 1}, {"sub": "u"})
    fixtures.append(("lost_response_fresh_rpc_id_same_task", t1 == t2 and first and not second and store.effects == 1))
    fixtures.append(("args_binding", expect_error(lambda: execute(store, token, 3, "tools/call", {"x": 2}, {"sub": "u"}), "binding")))
    fixtures.append(("principal_binding", expect_error(lambda: execute(store, token, 4, "tools/call", {"x": 1}, {"sub": "v"}), "binding")))
    fixtures.append(("method_binding", expect_error(lambda: execute(store, token, 5, "resources/read", {"x": 1}, {"sub": "u"}), "binding")))
    tampered = token[:-2] + ("AA" if token[-2:] != "AA" else "BB")
    fixtures.append(("integrity_binding", expect_error(lambda: execute(store, tampered, 6, "tools/call", {"x": 1}, {"sub": "u"}), "mac")))

    class RequestIdOnlyStore:
        def __init__(self):
            self.by_request = {}
            self.effects = 0
        def create(self, request_id):
            if request_id not in self.by_request:
                self.by_request[request_id] = f"t-{len(self.by_request) + 1}"
                self.effects += 1
            return self.by_request[request_id]

    bad = RequestIdOnlyStore()
    a, b = bad.create(1), bad.create(2)
    fixtures.append(("rpc_id_not_logical_id_negative", a != b and bad.effects == 2))

    event = {"id": "e1", "parent": "e0", "kind": "message"}
    state = HeadState(4, "e0")
    begin_marker(state, "e0", event)
    append_event(state, event)
    fixtures.append(("crash_after_append_recover", finish_or_recover(state) == "committed" and state.head == "e1" and state.marker is None))

    state = HeadState(4, "e0")
    begin_marker(state, "e0", event)
    append_event(state, event)
    state.generation = 5
    fixtures.append(("generation_fence", expect_error(lambda: finish_or_recover(state), "generation")))

    state = HeadState(4, "e0")
    begin_marker(state, "e0", event)
    append_event(state, event)
    state.head = "fork"
    fixtures.append(("head_moved_fail_closed", expect_error(lambda: finish_or_recover(state), "head moved")))

    state = HeadState(4, "e0")
    begin_marker(state, "e0", event)
    append_event(state, {"id": "e1", "parent": "e0", "kind": "tampered"})
    fixtures.append(("hash_mismatch_fail_closed", expect_error(lambda: finish_or_recover(state), "hash")))

    bad_event = {"id": "e1", "parent": "other", "kind": "message"}
    state = HeadState(4, "e0", marker={"generation": 4, "expected_old": "e0", "event_id": "e1", "event_hash": event_hash(bad_event)})
    append_event(state, bad_event)
    fixtures.append(("parent_mismatch_fail_closed", expect_error(lambda: finish_or_recover(state), "parent")))

    state = HeadState(4, "e1", events={"e1": copy.deepcopy(event)}, marker={"generation": 4, "expected_old": "e0", "event_id": "e1", "event_hash": event_hash(event)})
    fixtures.append(("idempotent_clear_after_applied", finish_or_recover(state) == "cleared-applied" and state.head == "e1" and state.marker is None))

    state = HeadState(4, "e0", events={"e1": copy.deepcopy(event)})
    fixtures.append(("no_marker_no_implicit_repair", finish_or_recover(state) == "none" and state.head == "e0"))

    failed = [name for name, ok in fixtures if not ok]
    print(json.dumps({"passed": len(fixtures) - len(failed), "total": len(fixtures), "failed": failed, "fixtures": fixtures}, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
