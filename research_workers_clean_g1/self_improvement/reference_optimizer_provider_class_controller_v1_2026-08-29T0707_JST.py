#!/usr/bin/env python3
"""Reference recovery controller for documented provider contract classes.

This is a deterministic local acceptance harness. It does not call external providers.
It tests controller transitions for four public-contract classes established by the
source audit: idempotent+reconcile, idempotent-only, reconcile-only, and neither.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

TERMINAL = {"COMPLETE", "BLOCKED_UNKNOWN", "BLOCKED_MISMATCH", "CONFLICT"}


def canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_request(target_key: str, expected_base_version: int, intended_value: str) -> str:
    body = {
        "expected_base_version": int(expected_base_version),
        "intended_value": intended_value,
        "target_key": target_key,
    }
    return hashlib.sha256(canon(body).encode("utf-8")).hexdigest()


class Provider:
    def __init__(self, path: Path):
        self.path = path
        with self._cx() as cx:
            cx.executescript(
                """
                PRAGMA journal_mode=WAL;
                PRAGMA synchronous=FULL;
                CREATE TABLE IF NOT EXISTS effects(
                    effect_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    op_id TEXT,
                    request_digest TEXT NOT NULL,
                    target_key TEXT NOT NULL,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS idempotency(
                    op_id TEXT PRIMARY KEY,
                    request_digest TEXT NOT NULL,
                    effect_id INTEGER NOT NULL,
                    expires_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS targets(
                    target_key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    version INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS stats(
                    name TEXT PRIMARY KEY,
                    count INTEGER NOT NULL
                );
                INSERT OR IGNORE INTO stats(name,count) VALUES
                    ('execute',0),('reconcile',0),('effect',0);
                """
            )

    def _cx(self):
        return sqlite3.connect(self.path)

    def _inc(self, cx: sqlite3.Connection, name: str, n: int = 1) -> None:
        cx.execute("UPDATE stats SET count=count+? WHERE name=?", (n, name))

    def stats(self) -> dict[str, int]:
        with self._cx() as cx:
            return {r[0]: int(r[1]) for r in cx.execute("SELECT name,count FROM stats")}

    def _new_effect(self, cx: sqlite3.Connection, op_id: str | None, request_digest: str,
                    target_key: str, value: str) -> int:
        cur = cx.execute(
            "INSERT INTO effects(op_id,request_digest,target_key,value) VALUES(?,?,?,?)",
            (op_id, request_digest, target_key, value),
        )
        self._inc(cx, "effect")
        return int(cur.lastrowid)

    def execute_idempotent(self, op_id: str, request_digest: str, target_key: str,
                           value: str, now: float, ttl: float) -> dict[str, Any]:
        with self._cx() as cx:
            self._inc(cx, "execute")
            row = cx.execute(
                "SELECT request_digest,effect_id,expires_at FROM idempotency WHERE op_id=?",
                (op_id,),
            ).fetchone()
            if row is not None and now <= float(row[2]):
                if row[0] != request_digest:
                    return {"status": "MISMATCH"}
                eff = cx.execute(
                    "SELECT target_key,value FROM effects WHERE effect_id=?", (int(row[1]),)
                ).fetchone()
                return {"status": "REPLAY", "effect_id": int(row[1]), "target_key": eff[0], "value": eff[1]}
            effect_id = self._new_effect(cx, op_id, request_digest, target_key, value)
            cx.execute(
                "INSERT OR REPLACE INTO idempotency(op_id,request_digest,effect_id,expires_at) VALUES(?,?,?,?)",
                (op_id, request_digest, effect_id, now + ttl),
            )
            return {"status": "CREATED", "effect_id": effect_id, "target_key": target_key, "value": value}

    def reconcile_by_op_id(self, op_id: str) -> dict[str, Any] | None:
        with self._cx() as cx:
            self._inc(cx, "reconcile")
            row = cx.execute(
                "SELECT effect_id,request_digest,target_key,value FROM effects WHERE op_id=? ORDER BY effect_id LIMIT 1",
                (op_id,),
            ).fetchone()
            if row is None:
                return None
            return {
                "effect_id": int(row[0]),
                "request_digest": row[1],
                "target_key": row[2],
                "value": row[3],
            }

    def seed_target(self, target_key: str, value: str, version: int) -> None:
        with self._cx() as cx:
            cx.execute(
                "INSERT OR REPLACE INTO targets(target_key,value,version) VALUES(?,?,?)",
                (target_key, value, int(version)),
            )

    def reconcile_target(self, target_key: str) -> dict[str, Any] | None:
        with self._cx() as cx:
            self._inc(cx, "reconcile")
            row = cx.execute(
                "SELECT value,version FROM targets WHERE target_key=?", (target_key,)
            ).fetchone()
            if row is None:
                return None
            return {"value": row[0], "version": int(row[1])}

    def execute_cas(self, request_digest: str, target_key: str, value: str,
                    expected_base_version: int) -> dict[str, Any]:
        with self._cx() as cx:
            self._inc(cx, "execute")
            row = cx.execute(
                "SELECT value,version FROM targets WHERE target_key=?", (target_key,)
            ).fetchone()
            current_version = 0 if row is None else int(row[1])
            if current_version != int(expected_base_version):
                return {"status": "CONFLICT", "current_version": current_version}
            effect_id = self._new_effect(cx, None, request_digest, target_key, value)
            cx.execute(
                "INSERT OR REPLACE INTO targets(target_key,value,version) VALUES(?,?,?)",
                (target_key, value, current_version + 1),
            )
            return {"status": "CREATED", "effect_id": effect_id, "version": current_version + 1}


class Controller:
    def __init__(self, path: Path, provider: Provider):
        self.path = path
        self.provider = provider
        with self._cx() as cx:
            cx.executescript(
                """
                PRAGMA journal_mode=WAL;
                PRAGMA synchronous=FULL;
                CREATE TABLE IF NOT EXISTS attempts(
                    attempt_id TEXT PRIMARY KEY,
                    provider_class TEXT NOT NULL,
                    op_id TEXT NOT NULL,
                    request_digest TEXT NOT NULL,
                    target_key TEXT NOT NULL,
                    expected_base_version INTEGER NOT NULL,
                    intended_value TEXT NOT NULL,
                    expiry_at REAL,
                    state TEXT NOT NULL,
                    result_json TEXT
                );
                """
            )

    def _cx(self):
        return sqlite3.connect(self.path)

    def create_intent(self, attempt_id: str, provider_class: str, op_id: str,
                      target_key: str, expected_base_version: int, intended_value: str,
                      expiry_at: float | None) -> str:
        request_digest = digest_request(target_key, expected_base_version, intended_value)
        with self._cx() as cx:
            cx.execute(
                "INSERT INTO attempts VALUES(?,?,?,?,?,?,?,?,?,NULL)",
                (
                    attempt_id, provider_class, op_id, request_digest, target_key,
                    int(expected_base_version), intended_value, expiry_at, "DISPATCHING",
                ),
            )
        return request_digest

    def _load(self, attempt_id: str) -> dict[str, Any]:
        with self._cx() as cx:
            row = cx.execute(
                "SELECT attempt_id,provider_class,op_id,request_digest,target_key,expected_base_version,intended_value,expiry_at,state,result_json FROM attempts WHERE attempt_id=?",
                (attempt_id,),
            ).fetchone()
        if row is None:
            raise KeyError(attempt_id)
        keys = ["attempt_id", "provider_class", "op_id", "request_digest", "target_key",
                "expected_base_version", "intended_value", "expiry_at", "state", "result_json"]
        return dict(zip(keys, row))

    def _finish(self, attempt_id: str, state: str, result: dict[str, Any]) -> dict[str, Any]:
        with self._cx() as cx:
            cx.execute(
                "UPDATE attempts SET state=?,result_json=? WHERE attempt_id=?",
                (state, canon(result), attempt_id),
            )
        return {"state": state, "result": result}

    def resume(self, attempt_id: str, now: float, idempotency_ttl: float = 24.0) -> dict[str, Any]:
        a = self._load(attempt_id)
        if a["state"] in TERMINAL:
            return {"state": a["state"], "result": json.loads(a["result_json"] or "{}"), "terminal_cache": True}

        recomputed = digest_request(a["target_key"], int(a["expected_base_version"]), a["intended_value"])
        if recomputed != a["request_digest"]:
            return self._finish(attempt_id, "BLOCKED_MISMATCH", {"reason": "local_request_digest_mismatch"})

        cls = a["provider_class"]
        if cls == "idempotent_plus_reconcile":
            found = self.provider.reconcile_by_op_id(a["op_id"])
            if found is not None:
                if found["request_digest"] != a["request_digest"] or found["target_key"] != a["target_key"] or found["value"] != a["intended_value"]:
                    return self._finish(attempt_id, "BLOCKED_MISMATCH", {"reason": "reconciled_effect_mismatch"})
                return self._finish(attempt_id, "COMPLETE", {"source": "reconcile", "effect_id": found["effect_id"]})
            if a["expiry_at"] is not None and now > float(a["expiry_at"]):
                return self._finish(attempt_id, "BLOCKED_UNKNOWN", {"reason": "idempotency_window_expired_after_reconcile_miss"})
            r = self.provider.execute_idempotent(
                a["op_id"], a["request_digest"], a["target_key"], a["intended_value"], now, idempotency_ttl
            )
            if r["status"] == "MISMATCH":
                return self._finish(attempt_id, "BLOCKED_MISMATCH", {"reason": "provider_idempotency_mismatch"})
            return self._finish(attempt_id, "COMPLETE", {"source": "same_identity_replay", "effect_id": r["effect_id"]})

        if cls == "idempotent_only":
            if a["expiry_at"] is None or now > float(a["expiry_at"]):
                return self._finish(attempt_id, "BLOCKED_UNKNOWN", {"reason": "idempotency_window_expired"})
            r = self.provider.execute_idempotent(
                a["op_id"], a["request_digest"], a["target_key"], a["intended_value"], now, idempotency_ttl
            )
            if r["status"] == "MISMATCH":
                return self._finish(attempt_id, "BLOCKED_MISMATCH", {"reason": "provider_idempotency_mismatch"})
            return self._finish(attempt_id, "COMPLETE", {"source": "same_identity_replay", "effect_id": r["effect_id"]})

        if cls == "reconcile_only":
            found = self.provider.reconcile_target(a["target_key"])
            if found is not None and found["value"] == a["intended_value"] and found["version"] == int(a["expected_base_version"]) + 1:
                return self._finish(attempt_id, "COMPLETE", {"source": "target_reconcile", "version": found["version"]})
            if found is not None and found["version"] != int(a["expected_base_version"]):
                return self._finish(attempt_id, "CONFLICT", {"reason": "base_version_changed", "current_version": found["version"]})
            r = self.provider.execute_cas(
                a["request_digest"], a["target_key"], a["intended_value"], int(a["expected_base_version"])
            )
            if r["status"] == "CONFLICT":
                return self._finish(attempt_id, "CONFLICT", {"reason": "cas_conflict", "current_version": r["current_version"]})
            return self._finish(attempt_id, "COMPLETE", {"source": "cas_retry", "effect_id": r["effect_id"]})

        if cls == "neither":
            return self._finish(attempt_id, "BLOCKED_UNKNOWN", {"reason": "ambiguous_dispatch_without_recovery_primitive"})

        raise ValueError(cls)


def stats_delta(before: dict[str, int], after: dict[str, int]) -> dict[str, int]:
    return {k: int(after[k] - before[k]) for k in sorted(before)}


def run_case(name: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="provider-class-") as td:
        root = Path(td)
        p = Provider(root / "provider.db")
        c = Controller(root / "controller.db", p)
        now = 100.0
        ttl = 24.0
        attempt = "attempt-1"
        target = "target-1"
        value = "value-v1"
        op = "op-1"

        expected_state = "COMPLETE"
        expected_resume_delta: dict[str, int] | None = None
        expected_effect_total: int | None = None

        if name == "idempotent_plus_reconcile_existing":
            d = c.create_intent(attempt, "idempotent_plus_reconcile", op, target, 0, value, now + ttl)
            p.execute_idempotent(op, d, target, value, now, ttl)
            expected_resume_delta = {"effect": 0, "execute": 0, "reconcile": 1}
            expected_effect_total = 1
        elif name == "idempotent_plus_reconcile_missing":
            c.create_intent(attempt, "idempotent_plus_reconcile", op, target, 0, value, now + ttl)
            expected_resume_delta = {"effect": 1, "execute": 1, "reconcile": 1}
            expected_effect_total = 1
        elif name == "idempotent_only_cached":
            d = c.create_intent(attempt, "idempotent_only", op, target, 0, value, now + ttl)
            p.execute_idempotent(op, d, target, value, now, ttl)
            expected_resume_delta = {"effect": 0, "execute": 1, "reconcile": 0}
            expected_effect_total = 1
        elif name == "idempotent_only_expired":
            d = c.create_intent(attempt, "idempotent_only", op, target, 0, value, now + 5.0)
            p.execute_idempotent(op, d, target, value, now, 5.0)
            now = now + 6.0
            expected_state = "BLOCKED_UNKNOWN"
            expected_resume_delta = {"effect": 0, "execute": 0, "reconcile": 0}
            expected_effect_total = 1
        elif name == "reconcile_only_existing_exact":
            c.create_intent(attempt, "reconcile_only", op, target, 0, value, None)
            p.seed_target(target, value, 1)
            expected_resume_delta = {"effect": 0, "execute": 0, "reconcile": 1}
            expected_effect_total = 0
        elif name == "reconcile_only_missing_base_unchanged":
            c.create_intent(attempt, "reconcile_only", op, target, 0, value, None)
            expected_resume_delta = {"effect": 1, "execute": 1, "reconcile": 1}
            expected_effect_total = 1
        elif name == "reconcile_only_conflict":
            c.create_intent(attempt, "reconcile_only", op, target, 0, value, None)
            p.seed_target(target, "other-value", 1)
            expected_state = "CONFLICT"
            expected_resume_delta = {"effect": 0, "execute": 0, "reconcile": 1}
            expected_effect_total = 0
        elif name == "neither_ambiguous":
            c.create_intent(attempt, "neither", op, target, 0, value, None)
            expected_state = "BLOCKED_UNKNOWN"
            expected_resume_delta = {"effect": 0, "execute": 0, "reconcile": 0}
            expected_effect_total = 0
        elif name == "local_payload_mismatch":
            c.create_intent(attempt, "idempotent_plus_reconcile", op, target, 0, value, now + ttl)
            with c._cx() as cx:
                cx.execute("UPDATE attempts SET intended_value=? WHERE attempt_id=?", ("mutated-value", attempt))
            expected_state = "BLOCKED_MISMATCH"
            expected_resume_delta = {"effect": 0, "execute": 0, "reconcile": 0}
            expected_effect_total = 0
        else:
            raise ValueError(name)

        before = p.stats()
        first = c.resume(attempt, now, ttl)
        after = p.stats()
        first_delta = stats_delta(before, after)
        before_second = p.stats()
        second = Controller(root / "controller.db", p).resume(attempt, now, ttl)
        after_second = p.stats()
        second_delta = stats_delta(before_second, after_second)

        checks = {
            "first_state": first["state"] == expected_state,
            "first_provider_delta": first_delta == expected_resume_delta,
            "effect_total": after["effect"] == expected_effect_total,
            "second_state_same": second["state"] == expected_state,
            "second_resume_provider_call_free": second_delta == {"effect": 0, "execute": 0, "reconcile": 0},
        }
        return {
            "case": name,
            "expected_state": expected_state,
            "first": first,
            "first_provider_delta": first_delta,
            "provider_after_first": after,
            "second": second,
            "second_provider_delta": second_delta,
            "checks": checks,
            "pass": all(checks.values()),
        }


def acceptance() -> dict[str, Any]:
    names = [
        "idempotent_plus_reconcile_existing",
        "idempotent_plus_reconcile_missing",
        "idempotent_only_cached",
        "idempotent_only_expired",
        "reconcile_only_existing_exact",
        "reconcile_only_missing_base_unchanged",
        "reconcile_only_conflict",
        "neither_ambiguous",
        "local_payload_mismatch",
    ]
    cases = [run_case(name) for name in names]
    return {
        "schema_version": 1,
        "harness": "reference_optimizer_provider_class_controller_v1",
        "case_count": len(cases),
        "pass_count": sum(1 for c in cases if c["pass"]),
        "all_pass": all(c["pass"] for c in cases),
        "cases": cases,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    result = acceptance()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError(out)
    out.write_text(canon(result) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
