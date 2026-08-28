"""Fixed-horizon fresh-process capture with falsifiable process-epoch identity.

All challenge/attempt identities are globally precommitted before observation.
Each Pool worker receives one process-epoch nonce in its initializer. The nonce is
stable for that worker's lifetime and is NOT derived from the job. With
maxtasksperchild=1, any accidental worker reuse across observations becomes
visible as a repeated process_epoch_id and fails closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import secrets
from typing import Any

SCHEMA_VERSION = 2
CHILD_PROGRAM_VERSION = "toy_hash_score_v3"
_PROCESS_EPOCH_NONCE: str | None = None


def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _schedule_from_precommit(doc: dict[str, Any]) -> list[dict[str, Any]]:
    n = int(doc["planned_challenge_count"])
    gen = str(doc["capture_generation_id"])
    schedule = [
        {
            "index": i,
            "challenge_id": f"{gen}-challenge-{i:04d}",
            "attempt_id": f"{gen}-attempt-{i:04d}",
        }
        for i in range(n)
    ]
    got = hashlib.sha256(_canon(schedule)).hexdigest()
    if got != str(doc["precommitted_schedule_sha256"]):
        raise RuntimeError("precommit schedule digest mismatch")
    if list(doc.get("index_range", [])) != [0, n - 1]:
        raise RuntimeError("precommit index_range mismatch")
    if doc.get("process_epoch_identity_contract") != "worker initializer creates one random epoch nonce; process_epoch_id=sha256(pid,ppid,epoch_nonce); job identity excluded; duplicate process_epoch_id across observations fails closed":
        raise RuntimeError("process epoch identity contract mismatch")
    return schedule


def _init_worker() -> None:
    global _PROCESS_EPOCH_NONCE
    if _PROCESS_EPOCH_NONCE is not None:
        raise RuntimeError("worker epoch nonce initialized twice")
    _PROCESS_EPOCH_NONCE = secrets.token_hex(32)


def _child(job: tuple[int, str, str]) -> dict[str, Any]:
    index, side, attempt_id = job
    if _PROCESS_EPOCH_NONCE is None:
        raise RuntimeError("worker epoch nonce missing")
    pid = os.getpid()
    ppid = os.getppid()
    epoch_payload = {"pid": pid, "ppid": ppid, "epoch_nonce": _PROCESS_EPOCH_NONCE}
    process_epoch_id = hashlib.sha256(_canon(epoch_payload)).hexdigest()
    value_digest = hashlib.sha256(("toy_hash_score_v3|" + attempt_id).encode("utf-8")).hexdigest()
    return {
        "index": index,
        "side": side,
        "attempt_id": attempt_id,
        "pid": pid,
        "ppid": ppid,
        "process_epoch_nonce": _PROCESS_EPOCH_NONCE,
        "process_epoch_id": process_epoch_id,
        "protected_value_digest": value_digest,
    }


def capture_shard(*, precommit: dict[str, Any], start_index: int, count: int, workers: int) -> dict[str, Any]:
    if workers < 1:
        raise ValueError("workers must be positive")
    schedule = _schedule_from_precommit(precommit)
    n = len(schedule)
    if count < 1 or start_index < 0 or start_index + count > n:
        raise ValueError("invalid shard range")
    shard_schedule = schedule[start_index:start_index + count]
    jobs = [
        (int(row["index"]), side, str(row["attempt_id"]))
        for row in shard_schedule
        for side in ("a", "b")
    ]
    ctx = mp.get_context("spawn")
    with ctx.Pool(processes=workers, initializer=_init_worker, maxtasksperchild=1) as pool:
        results = pool.map(_child, jobs, chunksize=1)

    by_key: dict[tuple[int, str], dict[str, Any]] = {}
    process_epoch_ids: set[str] = set()
    for out0 in results:
        out = dict(out0)
        key = (int(out["index"]), str(out["side"]))
        if key in by_key:
            raise RuntimeError(f"duplicate observation for {key}")
        epoch_id = str(out["process_epoch_id"])
        if epoch_id in process_epoch_ids:
            raise RuntimeError("worker process epoch reused across observations")
        expected_epoch_id = hashlib.sha256(_canon({
            "pid": int(out["pid"]),
            "ppid": int(out["ppid"]),
            "epoch_nonce": str(out["process_epoch_nonce"]),
        })).hexdigest()
        if epoch_id != expected_epoch_id:
            raise RuntimeError("process epoch identity digest mismatch")
        process_epoch_ids.add(epoch_id)
        by_key[key] = out
    if len(by_key) != 2 * count or len(process_epoch_ids) != 2 * count:
        raise RuntimeError("observed shard does not contain one unique process epoch per observation")

    pairs = []
    for row in shard_schedule:
        i = int(row["index"])
        a = by_key[(i, "a")]
        b = by_key[(i, "b")]
        if a["attempt_id"] != row["attempt_id"] or b["attempt_id"] != row["attempt_id"]:
            raise RuntimeError("attempt_id drift")
        if a["process_epoch_id"] == b["process_epoch_id"]:
            raise RuntimeError("challenge pair reused one process epoch")
        pairs.append({
            "index": i,
            "challenge_id": row["challenge_id"],
            "attempt_id": row["attempt_id"],
            "process_epoch_id_a": a["process_epoch_id"],
            "process_epoch_id_b": b["process_epoch_id"],
            "pid_a": a["pid"],
            "pid_b": b["pid"],
            "ppid_a": a["ppid"],
            "ppid_b": b["ppid"],
            "process_epoch_nonce_a": a["process_epoch_nonce"],
            "process_epoch_nonce_b": b["process_epoch_nonce"],
            "protected_value_digest_a": a["protected_value_digest"],
            "protected_value_digest_b": b["protected_value_digest"],
        })
    mismatches = sum(p["protected_value_digest_a"] != p["protected_value_digest_b"] for p in pairs)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "child_program_version": CHILD_PROGRAM_VERSION,
        "capture_generation_id": str(precommit["capture_generation_id"]),
        "precommitted_schedule_sha256": str(precommit["precommitted_schedule_sha256"]),
        "planned_challenge_count": n,
        "shard_start_index": start_index,
        "shard_count": count,
        "capture_contract": "precommitted global schedule; spawn workers; initializer-stable process epoch nonce; maxtasksperchild=1; exactly one unique process epoch per observation; complete shard only",
        "challenge_pairs": pairs,
        "mismatches": mismatches,
        "unique_process_epoch_count": len(process_epoch_ids),
    }
    payload["shard_payload_sha256"] = hashlib.sha256(_canon(payload)).hexdigest()
    return payload


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--precommit", required=True)
    ap.add_argument("--start-index", type=int, required=True)
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--output", required=True)
    ns = ap.parse_args()
    precommit = json.loads(Path(ns.precommit).read_text(encoding="utf-8"))
    doc = capture_shard(precommit=precommit, start_index=ns.start_index, count=ns.count, workers=ns.workers)
    raw = _canon(doc) + b"\n"
    out = Path(ns.output)
    if out.exists():
        raise RuntimeError("refusing to overwrite existing shard output")
    out.write_bytes(raw)
    print(json.dumps({
        "capture_generation_id": doc["capture_generation_id"],
        "shard_start_index": doc["shard_start_index"],
        "shard_count": doc["shard_count"],
        "fresh_process_observations": 2 * doc["shard_count"],
        "unique_process_epoch_count": doc["unique_process_epoch_count"],
        "mismatches": doc["mismatches"],
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "shard_payload_sha256": doc["shard_payload_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
