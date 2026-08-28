"""Capture raw fresh-process challenge evidence for the toy replay statistic.

Each protected-statistic observation is computed in a worker process that handles
exactly one job (`maxtasksperchild=1`). The parent precommits the full list of
attempt/side jobs before observing outcomes, then requires exactly two distinct
fresh-process observations per attempt and no process-identity reuse.

This is a capture harness only. It does not issue or authorize a certificate.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import lzma
import multiprocessing as mp
import os
from pathlib import Path
import secrets
from typing import Any

SCHEMA_VERSION = 1
CHILD_PROGRAM_VERSION = "toy_hash_score_v3"


def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _child(job: tuple[int, str]) -> dict[str, Any]:
    index, side = job
    attempt_id = f"toy-v3-attempt-{index:04d}"
    value_digest = hashlib.sha256(("toy_hash_score_v3|" + attempt_id).encode("utf-8")).hexdigest()
    return {
        "index": index,
        "side": side,
        "pid": os.getpid(),
        "boot_nonce": secrets.token_hex(16),
        "protected_value_digest": value_digest,
    }


def capture(*, challenge_count: int, workers: int) -> dict[str, Any]:
    if challenge_count < 1:
        raise ValueError("challenge_count must be positive")
    if workers < 1:
        raise ValueError("workers must be positive")
    jobs = [(i, side) for i in range(challenge_count) for side in ("a", "b")]
    # Spawn + maxtasksperchild=1 is part of the statistical trial-unit contract:
    # every job is executed in a process that exits after that one observation.
    ctx = mp.get_context("spawn")
    with ctx.Pool(processes=workers, maxtasksperchild=1) as pool:
        results = pool.map(_child, jobs, chunksize=1)
    by_key: dict[tuple[int, str], dict[str, Any]] = {}
    process_ids: set[str] = set()
    for out in results:
        key = (int(out["index"]), str(out["side"]))
        if key in by_key:
            raise RuntimeError(f"duplicate observation for {key}")
        process_id = f"pid={out['pid']};boot={out['boot_nonce']};job={key[0]}:{key[1]}"
        if process_id in process_ids:
            raise RuntimeError("fresh process identifier reuse")
        process_ids.add(process_id)
        out = dict(out)
        out["fresh_process_id"] = process_id
        by_key[key] = out
    if len(by_key) != 2 * challenge_count:
        raise RuntimeError("observed challenge count differs from precommitted horizon")
    pairs = []
    for i in range(challenge_count):
        a = by_key[(i, "a")]
        b = by_key[(i, "b")]
        if a["fresh_process_id"] == b["fresh_process_id"]:
            raise RuntimeError("challenge pair reused one process")
        pairs.append({
            "challenge_id": f"toy-v3-challenge-{i:04d}",
            "attempt_id": f"toy-v3-attempt-{i:04d}",
            "fresh_process_id_a": a["fresh_process_id"],
            "fresh_process_id_b": b["fresh_process_id"],
            "protected_value_digest_a": a["protected_value_digest"],
            "protected_value_digest_b": b["protected_value_digest"],
        })
    return {
        "schema_version": SCHEMA_VERSION,
        "child_program_version": CHILD_PROGRAM_VERSION,
        "capture_contract": "precommitted jobs; spawn workers; maxtasksperchild=1; one protected-statistic observation per fresh process",
        "planned_challenge_count": challenge_count,
        "challenge_pairs": pairs,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--challenge-count", type=int, default=1060)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--output", required=True)
    ap.add_argument("--compressed-output")
    ns = ap.parse_args()
    doc = capture(challenge_count=ns.challenge_count, workers=ns.workers)
    raw = _canon(doc) + b"\n"
    Path(ns.output).write_bytes(raw)
    if ns.compressed_output:
        container = {
            "schema_version": 1,
            "encoding": "lzma+base64",
            "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "payload_b64": base64.b64encode(lzma.compress(raw, preset=9)).decode("ascii"),
        }
        Path(ns.compressed_output).write_text(json.dumps(container, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    mismatches = sum(p["protected_value_digest_a"] != p["protected_value_digest_b"] for p in doc["challenge_pairs"])
    print(json.dumps({
        "challenge_count": len(doc["challenge_pairs"]),
        "fresh_process_observations": 2 * len(doc["challenge_pairs"]),
        "mismatches": mismatches,
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
