"""Multiprocessing validation for stable-sidecar journal fencing.

This is a contract-faithful durability/concurrency stress for the ADMIT ->
RESERVE -> scorer -> SLOT/COMMIT -> CLOSE event order. It intentionally does
not claim byte-execution of every historical reporting/e-process sibling.
"""
from __future__ import annotations

from hashlib import sha256
import json
import multiprocessing as mp
import os
from pathlib import Path
import random
import tempfile
import time
from typing import Any

from stable_sidecar_journal_io_2026_08_28 import (
    StableLockCASMismatch,
    StableSidecarJournalIO,
)


def canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def encode_frame(event: dict[str, Any]) -> bytes:
    body = canon(event)
    return f"{len(body):08x}:{sha256(body).hexdigest()}:".encode("ascii") + body + b"\n"


def decode_valid_prefix(blob: bytes) -> tuple[list[dict[str, Any]], int, str]:
    events: list[dict[str, Any]] = []
    pos = 0
    while pos < len(blob):
        start = pos
        if len(blob) - pos < 74:
            return events, start, "partial_header"
        try:
            n = int(blob[pos:pos+8].decode("ascii"), 16)
        except Exception:
            return events, start, "bad_length"
        pos += 8
        if blob[pos:pos+1] != b":":
            return events, start, "bad_header_sep"
        pos += 1
        digest = blob[pos:pos+64]
        pos += 64
        if blob[pos:pos+1] != b":":
            return events, start, "bad_digest_sep"
        pos += 1
        if len(blob) - pos < n + 1:
            return events, start, "partial_body"
        body = blob[pos:pos+n]
        pos += n
        if blob[pos:pos+1] != b"\n":
            return events, start, "missing_newline"
        pos += 1
        if sha256(body).hexdigest().encode("ascii") != digest:
            return events, start, "checksum_mismatch"
        try:
            events.append(json.loads(body.decode("utf-8")))
        except Exception:
            return events, start, "bad_json"
    return events, pos, "clean_eof"


def digest_obj(obj: Any) -> str:
    return sha256(canon(obj)).hexdigest()


def append_worker(path: str, expected: bytes, frame: bytes, delay: float, q: mp.Queue, tag: str) -> None:
    if delay > 0:
        time.sleep(delay)
    io = StableSidecarJournalIO(path)
    try:
        out = io.append_fsync_readback(expected, frame)
        q.put((tag, "ok", sha256(out).hexdigest()))
    except Exception as exc:
        q.put((tag, type(exc).__name__, str(exc)))


def reserve_worker(
    ledger_path: str,
    expected: bytes,
    frame: bytes,
    delay: float,
    q: mp.Queue,
    score_count: mp.Value,
) -> None:
    if delay > 0:
        time.sleep(delay)
    io = StableSidecarJournalIO(ledger_path)
    try:
        out = io.append_fsync_readback(expected, frame)
        with score_count.get_lock():
            score_count.value += 1
        q.put(("reserve", "ok", sha256(out).hexdigest()))
    except Exception as exc:
        q.put(("reserve", type(exc).__name__, str(exc)))


def slot_worker(
    main_path: str,
    ledger_path: str,
    main_expected: bytes,
    slot_frame: bytes,
    ledger_expected: bytes,
    commit_frame: bytes,
    delay: float,
    q: mp.Queue,
) -> None:
    if delay > 0:
        time.sleep(delay)
    main_io = StableSidecarJournalIO(main_path)
    ledger_io = StableSidecarJournalIO(ledger_path)
    try:
        main_after = main_io.append_fsync_readback(main_expected, slot_frame)
    except Exception as exc:
        q.put(("slot", type(exc).__name__, str(exc)))
        return
    try:
        ledger_after = ledger_io.append_fsync_readback(ledger_expected, commit_frame)
    except Exception as exc:
        q.put(("slot_commit", type(exc).__name__, str(exc)))
        return
    q.put(("slot", "ok", sha256(main_after + b"\0" + ledger_after).hexdigest()))


def close_worker(main_path: str, expected: bytes, frame: bytes, delay: float, q: mp.Queue) -> None:
    append_worker(main_path, expected, frame, delay, q, "close")


def torn_crash_worker(path: str, expected: bytes, frame: bytes, cut: int) -> None:
    io = StableSidecarJournalIO(path)
    with io.locked():
        fd = os.open(io.path, os.O_RDWR | os.O_CREAT, io.mode)
        try:
            current = io._read_all(fd)
            if current != expected:
                os._exit(71)
            os.lseek(fd, 0, os.SEEK_END)
            io._write_all(fd, frame[:cut])
            os.fsync(fd)
            os._exit(73)
        finally:
            os.close(fd)


def replay_contract(main_blob: bytes, ledger_blob: bytes, *, block_id: str, slot_id: str) -> dict[str, Any]:
    me, mn, ms = decode_valid_prefix(main_blob)
    le, ln, ls = decode_valid_prefix(ledger_blob)
    if ms != "clean_eof" or mn != len(main_blob) or ls != "clean_eof" or ln != len(ledger_blob):
        raise AssertionError("unclean final journal")
    admits = [e for e in me if e.get("kind") == "ADMIT" and e.get("block_id") == block_id]
    slots = [e for e in me if e.get("kind") == "SLOT" and e.get("block_id") == block_id and e.get("slot_id") == slot_id]
    closes = [e for e in me if e.get("kind") == "CLOSE" and e.get("block_id") == block_id]
    reserves = [e for e in le if e.get("kind") == "RESERVE" and e.get("block_id") == block_id and e.get("slot_id") == slot_id]
    commits = [e for e in le if e.get("kind") == "COMMIT" and e.get("block_id") == block_id and e.get("slot_id") == slot_id]
    if len(admits) != 1 or len(reserves) != 1 or len(closes) != 1:
        raise AssertionError((len(admits), len(reserves), len(closes)))
    if len(slots) > 1 or len(commits) > 1:
        raise AssertionError("duplicate slot/commit")
    if len(slots) != len(commits):
        raise AssertionError("SLOT/COMMIT mismatch")
    score = float(slots[0]["score"]) if slots else 1.0
    return {
        "admit_count": len(admits),
        "reserve_count": len(reserves),
        "slot_count": len(slots),
        "commit_count": len(commits),
        "close_count": len(closes),
        "block_score": score,
        "fail_closed": not bool(slots),
        "main_digest": sha256(main_blob).hexdigest(),
        "ledger_digest": sha256(ledger_blob).hexdigest(),
    }


def run_campaign(seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    with tempfile.TemporaryDirectory(prefix="eval-sidecar-race-") as td:
        root = Path(td)
        main_path = root / "main.journal"
        ledger_path = root / "attempt.ledger"
        main_io = StableSidecarJournalIO(main_path)
        ledger_io = StableSidecarJournalIO(ledger_path)

        bogus = encode_frame({"kind": "TORN", "seed": seed, "payload": "x" * 64})
        cut = rng.randint(1, len(bogus) - 1)
        p = mp.Process(target=torn_crash_worker, args=(str(main_path), b"", bogus, cut))
        p.start(); p.join(10)
        if p.is_alive():
            p.kill(); p.join()
            raise AssertionError("torn writer hung")
        if p.exitcode != 73:
            raise AssertionError(f"unexpected torn writer exit {p.exitcode}")
        lock_identity = os.stat(main_io.lock_path).st_dev, os.stat(main_io.lock_path).st_ino
        repaired, repair_meta = main_io.repair_valid_prefix(decode_valid_prefix)
        if repaired != b"" or not repair_meta["repaired"]:
            raise AssertionError("torn empty journal did not repair to empty prefix")

        block_id = f"b{seed}"
        slot_id = "s0"
        admit = {
            "schema_version": 1, "kind": "ADMIT", "event_id": f"admit:{block_id}",
            "block_id": block_id, "slot_ids": [slot_id], "admitted_at": 0.0,
            "deadline": 1.0, "b_cap": 1,
            "reserved_score_runtime_contract": {"schema_version": 1, "enforce_for_new_reservations": True},
        }
        admit_frame = encode_frame(admit)

        q = mp.Queue()
        delays = [rng.random() * 0.004, rng.random() * 0.004]
        ps = [
            mp.Process(target=append_worker, args=(str(main_path), b"", admit_frame, delays[i], q, f"admit{i}"))
            for i in range(2)
        ]
        for x in ps: x.start()
        for x in ps: x.join(10)
        results = [q.get(timeout=2) for _ in range(2)]
        if sum(1 for r in results if r[1] == "ok") != 1:
            raise AssertionError(("duplicate ADMIT winner count", results))
        main_admit = main_path.read_bytes()
        if main_admit != admit_frame:
            raise AssertionError("unexpected ADMIT bytes")
        if (os.stat(main_io.lock_path).st_dev, os.stat(main_io.lock_path).st_ino) != lock_identity:
            raise AssertionError("main sidecar lock inode changed")

        reservation_payload = {
            "block_id": block_id,
            "slot_id": slot_id,
            "attempt_id": sha256(f"{block_id}:{slot_id}".encode()).hexdigest(),
            "retry_policy": "fail_closed_unresolved",
            "request_binding_digest": sha256(f"req:{seed}".encode()).hexdigest(),
        }
        reserve = {
            "schema_version": 1, "kind": "RESERVE", "event_id": f"reserve:{block_id}:{slot_id}",
            "block_id": block_id, "slot_id": slot_id,
            "reservation": reservation_payload,
            "reservation_digest": digest_obj(reservation_payload),
        }
        reserve_frame = encode_frame(reserve)
        score_count = mp.Value("i", 0)
        delays = [rng.random() * 0.004, rng.random() * 0.004]
        ps = [
            mp.Process(
                target=reserve_worker,
                args=(str(ledger_path), b"", reserve_frame, delays[i], q, score_count),
            )
            for i in range(2)
        ]
        for x in ps: x.start()
        for x in ps: x.join(10)
        results2 = [q.get(timeout=2) for _ in range(2)]
        if sum(1 for r in results2 if r[1] == "ok") != 1:
            raise AssertionError(("duplicate RESERVE winner count", results2))
        if score_count.value != 1:
            raise AssertionError(("scorer launch count", score_count.value))
        ledger_reserve = ledger_path.read_bytes()
        if ledger_reserve != reserve_frame:
            raise AssertionError("unexpected RESERVE bytes")
        ledger_lock_identity = os.stat(ledger_io.lock_path).st_dev, os.stat(ledger_io.lock_path).st_ino

        score = 0.0 if seed % 2 == 0 else 0.25
        slot = {
            "schema_version": 1, "kind": "SLOT", "event_id": f"slot:{block_id}:{slot_id}",
            "block_id": block_id, "slot_id": slot_id, "score": score, "observed_at": 1.0,
            "attempt_id": reservation_payload["attempt_id"],
            "reservation_digest": reserve["reservation_digest"],
        }
        slot_frame = encode_frame(slot)
        commit = {
            "schema_version": 1, "kind": "COMMIT", "event_id": f"commit:{block_id}:{slot_id}",
            "block_id": block_id, "slot_id": slot_id,
            "reservation_digest": reserve["reservation_digest"],
            "slot_event_digest": digest_obj(slot),
            "committed_at": 1.0,
        }
        commit_frame = encode_frame(commit)
        close = {
            "schema_version": 1, "kind": "CLOSE", "event_id": f"close:{block_id}",
            "block_id": block_id, "closed_at": 1.0,
            "reservation_runtime_provenance_contract": {"pre_score_admit_binding_required_for_enforcement": True},
        }
        close_frame = encode_frame(close)

        dslot, dclose = rng.random() * 0.006, rng.random() * 0.006
        pslot = mp.Process(
            target=slot_worker,
            args=(str(main_path), str(ledger_path), main_admit, slot_frame, ledger_reserve, commit_frame, dslot, q),
        )
        pclose = mp.Process(target=close_worker, args=(str(main_path), main_admit, close_frame, dclose, q))
        pslot.start(); pclose.start()
        pslot.join(10); pclose.join(10)
        rslot = q.get(timeout=2); rclose = q.get(timeout=2)
        bytag = {rslot[0]: rslot, rclose[0]: rclose}
        main_now = main_path.read_bytes()
        events, n, status = decode_valid_prefix(main_now)
        if status != "clean_eof" or n != len(main_now):
            raise AssertionError("main became torn during SLOT/CLOSE race")
        kinds = [e.get("kind") for e in events]
        if "CLOSE" not in kinds:
            if "SLOT" not in kinds:
                raise AssertionError(("neither SLOT nor CLOSE durable", bytag))
            led_events, ln, ls = decode_valid_prefix(ledger_path.read_bytes())
            if ls != "clean_eof" or ln != len(ledger_path.read_bytes()) or not any(e.get("kind") == "COMMIT" for e in led_events):
                raise AssertionError("SLOT durable without COMMIT before retry CLOSE")
            main_now = main_io.append_fsync_readback(main_now, close_frame)

        final_main = main_path.read_bytes()
        final_ledger = ledger_path.read_bytes()
        replay1 = replay_contract(final_main, final_ledger, block_id=block_id, slot_id=slot_id)
        replay2 = replay_contract(main_path.read_bytes(), ledger_path.read_bytes(), block_id=block_id, slot_id=slot_id)
        if replay1 != replay2:
            raise AssertionError("restart replay mismatch")
        if (os.stat(main_io.lock_path).st_dev, os.stat(main_io.lock_path).st_ino) != lock_identity:
            raise AssertionError("main sidecar lock inode changed after lifecycle")
        if (os.stat(ledger_io.lock_path).st_dev, os.stat(ledger_io.lock_path).st_ino) != ledger_lock_identity:
            raise AssertionError("ledger sidecar lock inode changed after lifecycle")
        replay1.update({
            "seed": seed,
            "scorer_launch_count": score_count.value,
            "repair_removed_bytes": int(repair_meta["removed_bytes"]),
            "slot_race_status": bytag.get("slot", bytag.get("slot_commit")),
            "close_race_status": bytag.get("close"),
        })
        return replay1


def main() -> None:
    mp.set_start_method("fork", force=True)
    campaigns = 400
    rows = [run_campaign(i) for i in range(campaigns)]
    summary = {
        "schema_version": 1,
        "campaigns": campaigns,
        "failures": 0,
        "exactly_one_scorer_launch": sum(r["scorer_launch_count"] == 1 for r in rows),
        "slot_won_before_close": sum(r["slot_count"] == 1 for r in rows),
        "close_won_fail_closed": sum(r["slot_count"] == 0 and r["fail_closed"] for r in rows),
        "all_replays_clean": sum(r["admit_count"] == r["reserve_count"] == r["close_count"] == 1 for r in rows),
        "repair_removed_bytes_min": min(r["repair_removed_bytes"] for r in rows),
        "repair_removed_bytes_max": max(r["repair_removed_bytes"] for r in rows),
        "notes": [
            "Each campaign starts with a process death while holding the stable sidecar flock after fsyncing a torn frame prefix; recovery repairs only to the decoder-valid prefix.",
            "Duplicate ADMIT and duplicate RESERVE races use the same expected prefix and yield exactly one CAS winner.",
            "Only the durable RESERVE winner increments the scorer-launch counter.",
            "SLOT and deadline CLOSE race from the same main prefix. If CLOSE wins first, the slot remains fail-closed; if SLOT wins, COMMIT is required before retrying CLOSE.",
            "Final replay is repeated from durable bytes and must match exactly; sidecar lock inode identity is checked across the lifecycle.",
        ],
    }
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
