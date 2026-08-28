"""Resumable fixed-horizon fresh-process challenge capture for the toy replay statistic.

The full 1..N challenge identity schedule is precommitted in a separate manifest
before any v4 observation is launched. This harness captures one contiguous shard
of that immutable schedule. Each protected-statistic observation is computed in a
spawned worker process that handles exactly one job (`maxtasksperchild=1`) and then
exits. Shards are non-certifying until the full precommitted horizon is present.

A shard that may have launched an observation but failed to durably emit its
complete shard record MUST NOT be retried; the capture generation is invalidated
instead. This avoids choose-among-retries in the very evidence used to assess
replay determinism.
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

SCHEMA_VERSION = 1
CHILD_PROGRAM_VERSION = "toy_hash_score_v3"


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
    return schedule


def _child(job: tuple[int, str, str]) -> dict[str, Any]:
    index, side, attempt_id = job
    value_digest = hashlib.sha256(("toy_hash_score_v3|" + attempt_id).encode("utf-8")).hexdigest()
    return {
        "index": index,
        "side": side,
        "attempt_id": attempt_id,
        "pid": os.getpid(),
        "boot_nonce": secrets.token_hex(16),
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
    # Spawn + maxtasksperchild=1 is part of the statistical trial-unit contract.
    ctx = mp.get_context("spawn")
    with ctx.Pool(processes=workers, maxtasksperchild=1) as pool:
        results = pool.map(_child, jobs, chunksize=1)

    by_key: dict[tuple[int, str], dict[str, Any]] = {}
    process_ids: set[str] = set()
    for out0 in results:
        out = dict(out0)
        key = (int(out["index"]), str(out["side"]))
        if key in by_key:
            raise RuntimeError(f"duplicate observation for {key}")
        process_id = f"pid={out['pid']};boot={out['boot_nonce']};job={key[0]}:{key[1]}"
        if process_id in process_ids:
            raise RuntimeError("fresh process identifier reuse within shard")
        process_ids.add(process_id)
        out["fresh_process_id"] = process_id
        by_key[key] = out
    if len(by_key) != 2 * count:
        raise RuntimeError("observed shard size differs from precommitted shard")

    pairs = []
    for row in shard_schedule:
        i = int(row["index"])
        a = by_key[(i, "a")]
        b = by_key[(i, "b")]
        if a["attempt_id"] != row["attempt_id"] or b["attempt_id"] != row["attempt_id"]:
            raise RuntimeError("attempt_id drift")
        if a["fresh_process_id"] == b["fresh_process_id"]:
            raise RuntimeError("challenge pair reused one process")
        pairs.append({
            "index": i,
            "challenge_id": row["challenge_id"],
            "attempt_id": row["attempt_id"],
            "fresh_process_id_a": a["fresh_process_id"],
            "fresh_process_id_b": b["fresh_process_id"],
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
        "capture_contract": "precommitted global schedule; spawn workers; maxtasksperchild=1; one protected-statistic observation per fresh process; complete shard only",
        "challenge_pairs": pairs,
        "mismatches": mismatches,
    }
    payload["shard_payload_sha256"] = hashlib.sha256(_canon(payload)).hexdigest()
    return payload


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--precommit", required=True)
    ap.add_argument("--start-index", type=int, required=True)
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--output", required=True)
    ns = ap.parse_args()
    precommit = json.loads(Path(ns.precommit).read_text(encoding="utf-8"))
    doc = capture_shard(
        precommit=precommit,
        start_index=ns.start_index,
        count=ns.count,
        workers=ns.workers,
    )
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
        "mismatches": doc["mismatches"],
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "shard_payload_sha256": doc["shard_payload_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
