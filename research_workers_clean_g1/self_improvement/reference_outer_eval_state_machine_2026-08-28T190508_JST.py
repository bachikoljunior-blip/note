from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def connect(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(path, timeout=30, isolation_level=None)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=FULL")
    return con


def init_local(path: Path) -> None:
    con = connect(path)
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS attempts(
          attempt_id TEXT PRIMARY KEY,
          request_digest TEXT NOT NULL,
          request_json TEXT NOT NULL,
          state TEXT NOT NULL,
          certificate_json TEXT,
          certificate_digest TEXT
        );
        CREATE TABLE IF NOT EXISTS cells(
          attempt_id TEXT NOT NULL,
          cell_id TEXT NOT NULL,
          request_digest TEXT NOT NULL,
          request_json TEXT NOT NULL,
          state TEXT NOT NULL,
          outcome_json TEXT,
          outcome_digest TEXT,
          PRIMARY KEY(attempt_id, cell_id)
        );
        CREATE TABLE IF NOT EXISTS audit_events(
          seq INTEGER PRIMARY KEY AUTOINCREMENT,
          event_type TEXT NOT NULL,
          payload_json TEXT NOT NULL
        );
        """
    )
    con.close()


def init_provider(path: Path) -> None:
    con = connect(path)
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS effects(
          cell_id TEXT PRIMARY KEY,
          request_digest TEXT NOT NULL,
          outcome_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS calls(
          seq INTEGER PRIMARY KEY AUTOINCREMENT,
          kind TEXT NOT NULL,
          cell_id TEXT NOT NULL,
          request_digest TEXT NOT NULL
        );
        """
    )
    con.close()


def append_audit(con: sqlite3.Connection, event_type: str, payload: Any) -> None:
    con.execute(
        "INSERT INTO audit_events(event_type,payload_json) VALUES (?,?)",
        (event_type, canonical(payload)),
    )


def provider_reconcile(provider_db: Path, cell_id: str, request_digest: str) -> dict[str, Any] | None:
    con = connect(provider_db)
    con.execute(
        "INSERT INTO calls(kind,cell_id,request_digest) VALUES ('reconcile',?,?)",
        (cell_id, request_digest),
    )
    row = con.execute(
        "SELECT request_digest,outcome_json FROM effects WHERE cell_id=?", (cell_id,)
    ).fetchone()
    con.close()
    if row is None:
        return None
    if row["request_digest"] != request_digest:
        raise RuntimeError("provider cell_id digest mismatch")
    return json.loads(row["outcome_json"])


def provider_execute(provider_db: Path, cell_id: str, request_digest: str, request: dict[str, Any]) -> dict[str, Any]:
    con = connect(provider_db)
    con.execute("BEGIN IMMEDIATE")
    con.execute(
        "INSERT INTO calls(kind,cell_id,request_digest) VALUES ('execute',?,?)",
        (cell_id, request_digest),
    )
    row = con.execute(
        "SELECT request_digest,outcome_json FROM effects WHERE cell_id=?", (cell_id,)
    ).fetchone()
    if row is None:
        score = int(sha256_text(canonical(request))[:8], 16) % 1000 / 1000.0
        outcome = {"cell_id": cell_id, "score": score, "ok": score >= 0.0}
        con.execute(
            "INSERT INTO effects(cell_id,request_digest,outcome_json) VALUES (?,?,?)",
            (cell_id, request_digest, canonical(outcome)),
        )
    else:
        if row["request_digest"] != request_digest:
            con.execute("ROLLBACK")
            con.close()
            raise RuntimeError("provider reused cell_id with changed semantics")
        outcome = json.loads(row["outcome_json"])
    con.execute("COMMIT")
    con.close()
    return outcome


def write_marker(marker_dir: Path | None, stage: str) -> None:
    if marker_dir is None:
        return
    marker_dir.mkdir(parents=True, exist_ok=True)
    (marker_dir / stage).write_text("ready", encoding="utf-8")


def maybe_pause(killpoint: str | None, stage: str, marker_dir: Path | None) -> None:
    if killpoint != stage:
        return
    write_marker(marker_dir, stage)
    while True:
        signal.pause()


@dataclass(frozen=True)
class FrozenRequest:
    candidate_digest: str
    evaluator_digest: str
    dataset_digest: str
    split: str
    cells: tuple[str, ...]

    def payload(self) -> dict[str, Any]:
        return {
            "candidate_digest": self.candidate_digest,
            "evaluator_digest": self.evaluator_digest,
            "dataset_digest": self.dataset_digest,
            "split": self.split,
            "cells": list(self.cells),
        }


def deterministic_attempt_id(req: FrozenRequest) -> tuple[str, str]:
    digest = sha256_text(canonical(req.payload()))
    return f"outer-{digest[:24]}", digest


def cell_payload(req: FrozenRequest, cell_key: str) -> dict[str, Any]:
    return {
        "candidate_digest": req.candidate_digest,
        "evaluator_digest": req.evaluator_digest,
        "dataset_digest": req.dataset_digest,
        "split": req.split,
        "cell_key": cell_key,
    }


def certify(
    local_db: Path,
    provider_db: Path,
    req: FrozenRequest,
    killpoint: str | None = None,
    marker_dir: Path | None = None,
    explicit_attempt_id: str | None = None,
) -> dict[str, Any]:
    if req.split != "OUTER":
        raise ValueError("certify is reserved for OUTER")

    attempt_id, digest = deterministic_attempt_id(req)
    if explicit_attempt_id is not None:
        attempt_id = explicit_attempt_id

    con = connect(local_db)
    row = con.execute("SELECT * FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
    if row is not None:
        if row["request_digest"] != digest:
            con.close()
            raise RuntimeError("attempt_id reused with changed semantic request")
        if row["state"] == "SEALED":
            cert = json.loads(row["certificate_json"])
            append_audit(con, "CERTIFICATE_CACHE_HIT", {"attempt_id": attempt_id})
            con.close()
            return cert
    else:
        con.execute("BEGIN IMMEDIATE")
        con.execute(
            "INSERT INTO attempts(attempt_id,request_digest,request_json,state) VALUES (?,?,?,'RUNNING')",
            (attempt_id, digest, canonical(req.payload())),
        )
        for cell_key in req.cells:
            payload = cell_payload(req, cell_key)
            cdigest = sha256_text(canonical(payload))
            cell_id = f"cell-{cdigest[:24]}"
            con.execute(
                "INSERT INTO cells(attempt_id,cell_id,request_digest,request_json,state) VALUES (?,?,?,?, 'PLANNED')",
                (attempt_id, cell_id, cdigest, canonical(payload)),
            )
        append_audit(con, "OUTER_INTENT_COMMITTED", {"attempt_id": attempt_id, "request_digest": digest})
        con.execute("COMMIT")

    maybe_pause(killpoint, "after_intent_before_dispatch", marker_dir)

    cells = con.execute(
        "SELECT * FROM cells WHERE attempt_id=? ORDER BY cell_id", (attempt_id,)
    ).fetchall()
    persisted_count = sum(1 for c in cells if c["state"] == "COMPLETED")

    for cell in cells:
        if cell["state"] == "COMPLETED":
            continue
        payload = json.loads(cell["request_json"])
        outcome = provider_reconcile(provider_db, cell["cell_id"], cell["request_digest"])
        if outcome is None:
            outcome = provider_execute(provider_db, cell["cell_id"], cell["request_digest"], payload)
            if persisted_count == 0:
                maybe_pause(killpoint, "after_remote_before_local", marker_dir)
        odigest = sha256_text(canonical(outcome))
        con.execute("BEGIN IMMEDIATE")
        current = con.execute(
            "SELECT state,outcome_digest FROM cells WHERE attempt_id=? AND cell_id=?",
            (attempt_id, cell["cell_id"]),
        ).fetchone()
        if current["state"] == "COMPLETED":
            if current["outcome_digest"] != odigest:
                con.execute("ROLLBACK")
                con.close()
                raise RuntimeError("conflicting immutable cell outcome")
        else:
            con.execute(
                "UPDATE cells SET state='COMPLETED', outcome_json=?, outcome_digest=? WHERE attempt_id=? AND cell_id=?",
                (canonical(outcome), odigest, attempt_id, cell["cell_id"]),
            )
            append_audit(con, "CELL_OUTCOME_COMMITTED", {"attempt_id": attempt_id, "cell_id": cell["cell_id"], "outcome_digest": odigest})
        con.execute("COMMIT")
        persisted_count += 1
        if persisted_count == 1:
            maybe_pause(killpoint, "after_first_local", marker_dir)
        if persisted_count == max(1, len(cells) - 1):
            maybe_pause(killpoint, "after_partial", marker_dir)

    completed = con.execute(
        "SELECT cell_id,outcome_json,outcome_digest FROM cells WHERE attempt_id=? ORDER BY cell_id",
        (attempt_id,),
    ).fetchall()
    if len(completed) != len(req.cells) or any(r["outcome_json"] is None for r in completed):
        con.close()
        raise RuntimeError("attempt incomplete")
    scores = [json.loads(r["outcome_json"])["score"] for r in completed]
    certificate = {
        "attempt_id": attempt_id,
        "request_digest": digest,
        "cell_outcome_digests": [r["outcome_digest"] for r in completed],
        "mean_score": sum(scores) / len(scores),
        "num_cells": len(scores),
    }
    cert_digest = sha256_text(canonical(certificate))

    current = con.execute("SELECT state,certificate_digest FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
    if current["state"] == "RUNNING":
        con.execute("BEGIN IMMEDIATE")
        con.execute(
            "UPDATE attempts SET state='CERTIFICATE_WRITTEN', certificate_json=?, certificate_digest=? WHERE attempt_id=?",
            (canonical(certificate), cert_digest, attempt_id),
        )
        append_audit(con, "CERTIFICATE_WRITTEN", {"attempt_id": attempt_id, "certificate_digest": cert_digest})
        con.execute("COMMIT")
    elif current["certificate_digest"] != cert_digest:
        con.close()
        raise RuntimeError("certificate mismatch during recovery")

    maybe_pause(killpoint, "after_final_artifact_before_seal", marker_dir)

    current = con.execute("SELECT state,certificate_digest FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
    if current["state"] != "SEALED":
        if current["certificate_digest"] != cert_digest:
            con.close()
            raise RuntimeError("cannot seal mismatched certificate")
        con.execute("BEGIN IMMEDIATE")
        con.execute("UPDATE attempts SET state='SEALED' WHERE attempt_id=?", (attempt_id,))
        append_audit(con, "OUTER_SEALED", {"attempt_id": attempt_id, "certificate_digest": cert_digest})
        con.execute("COMMIT")

    maybe_pause(killpoint, "after_seal", marker_dir)
    con.close()
    return certificate


def generic_evaluate(split: str) -> None:
    if split == "OUTER":
        raise PermissionError("OUTER is only queryable through certify() terminal authority")


def provider_counts(provider_db: Path) -> dict[str, int]:
    con = connect(provider_db)
    rows = con.execute("SELECT kind,COUNT(*) c FROM calls GROUP BY kind").fetchall()
    effects = con.execute("SELECT COUNT(*) c FROM effects").fetchone()["c"]
    con.close()
    out = {"execute": 0, "reconcile": 0, "effects": effects}
    for r in rows:
        out[r["kind"]] = r["c"]
    return out


def run_controller(args: argparse.Namespace) -> int:
    req = FrozenRequest(args.candidate, args.evaluator, args.dataset, "OUTER", tuple(args.cells.split(",")))
    cert = certify(
        Path(args.local_db),
        Path(args.provider_db),
        req,
        killpoint=args.killpoint,
        marker_dir=Path(args.marker_dir) if args.marker_dir else None,
    )
    print(canonical(cert))
    return 0


def wait_for_marker(path: Path, timeout: float = 10.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if path.exists():
            return
        time.sleep(0.02)
    raise TimeoutError(f"marker not observed: {path}")


def self_test() -> dict[str, Any]:
    killpoints = [
        "after_intent_before_dispatch",
        "after_remote_before_local",
        "after_first_local",
        "after_partial",
        "after_final_artifact_before_seal",
        "after_seal",
    ]
    cases: list[dict[str, Any]] = []
    for kp in killpoints:
        with tempfile.TemporaryDirectory(prefix="outer_ref_") as td:
            root = Path(td)
            local_db = root / "local.sqlite"
            provider_db = root / "provider.sqlite"
            marker_dir = root / "markers"
            init_local(local_db)
            init_provider(provider_db)
            base_cmd = [
                sys.executable, __file__, "controller",
                "--local-db", str(local_db),
                "--provider-db", str(provider_db),
                "--candidate", "cand:abc",
                "--evaluator", "eval:v1",
                "--dataset", "data:outer-v1",
                "--cells", "a,b,c",
                "--marker-dir", str(marker_dir),
            ]
            p = subprocess.Popen(base_cmd + ["--killpoint", kp], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            wait_for_marker(marker_dir / kp)
            os.kill(p.pid, signal.SIGKILL)
            p.wait(timeout=5)
            if p.returncode != -signal.SIGKILL:
                raise AssertionError((kp, p.returncode))
            before_resume = provider_counts(provider_db)
            resumed = subprocess.run(base_cmd, capture_output=True, text=True, check=True, timeout=10)
            cert = json.loads(resumed.stdout.strip().splitlines()[-1])
            after_resume = provider_counts(provider_db)
            assert after_resume["effects"] == 3, (kp, after_resume)
            assert after_resume["execute"] == 3, (kp, after_resume)
            counts_before_second = provider_counts(provider_db)
            second = subprocess.run(base_cmd, capture_output=True, text=True, check=True, timeout=10)
            cert2 = json.loads(second.stdout.strip().splitlines()[-1])
            counts_after_second = provider_counts(provider_db)
            assert cert2 == cert
            assert counts_after_second == counts_before_second, (kp, counts_before_second, counts_after_second)
            try:
                generic_evaluate("OUTER")
            except PermissionError:
                gate_ok = True
            else:
                gate_ok = False
            assert gate_ok
            req = FrozenRequest("cand:abc", "eval:v1", "data:outer-v1", "OUTER", ("a", "b", "c"))
            attempt_id, _ = deterministic_attempt_id(req)
            mismatched = FrozenRequest("cand:changed", "eval:v1", "data:outer-v1", "OUTER", ("a", "b", "c"))
            mismatch_before = provider_counts(provider_db)
            mismatch_rejected = False
            try:
                certify(local_db, provider_db, mismatched, explicit_attempt_id=attempt_id)
            except RuntimeError as e:
                mismatch_rejected = "changed semantic request" in str(e)
            mismatch_after = provider_counts(provider_db)
            assert mismatch_rejected
            assert mismatch_after == mismatch_before
            cases.append({
                "killpoint": kp,
                "controller_exit": p.returncode,
                "provider_before_resume": before_resume,
                "provider_after_resume": after_resume,
                "provider_after_second_certify": counts_after_second,
                "certificate_digest": sha256_text(canonical(cert)),
                "cache_only_second_certify": counts_after_second == counts_before_second,
                "generic_outer_gate": gate_ok,
                "semantic_reuse_rejected_pre_provider": mismatch_rejected and mismatch_after == mismatch_before,
            })
    return {
        "schema_version": 1,
        "test": "cross_process_sigkill_outer_evaluation_reference",
        "killpoints": killpoints,
        "all_passed": all(
            c["controller_exit"] == -signal.SIGKILL
            and c["provider_after_resume"]["effects"] == 3
            and c["provider_after_resume"]["execute"] == 3
            and c["cache_only_second_certify"]
            and c["generic_outer_gate"]
            and c["semantic_reuse_rejected_pre_provider"]
            for c in cases
        ),
        "cases": cases,
        "invariants": {
            "pre_dispatch_content_bound_intent": True,
            "stable_cell_id_provider_idempotency": True,
            "reconcile_before_execute_on_restart": True,
            "immutable_cell_outcomes": True,
            "missing_cell_only_resume": True,
            "certificate_derived_from_cells": True,
            "terminal_lookup_before_provider_access": True,
            "generic_outer_api_forbidden": True,
        },
        "scope_note": "Reference implementation with a deterministic SQLite-backed provider simulator; demonstrates controller crash semantics and ordering, not a claim about exactly-once behavior of arbitrary real providers.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    cp = sub.add_parser("controller")
    cp.add_argument("--local-db", required=True)
    cp.add_argument("--provider-db", required=True)
    cp.add_argument("--candidate", required=True)
    cp.add_argument("--evaluator", required=True)
    cp.add_argument("--dataset", required=True)
    cp.add_argument("--cells", required=True)
    cp.add_argument("--killpoint")
    cp.add_argument("--marker-dir")
    sub.add_parser("self-test")
    args = ap.parse_args()
    if args.cmd == "controller":
        return run_controller(args)
    report = self_test()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
