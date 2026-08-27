"""Multiprocessing stress for evaluation journal flock/replacement semantics.

This test byte-pins the current PosixFlockedCASAppendWriter source and then
checks a single-host failure surface not covered by same-inode append races:
if recovery replaces the journal pathname while a writer holds flock on the old
open file description, a second process can lock and mutate the replacement
inode concurrently.  A candidate repair is a stable sidecar lock inode acquired
*before* opening/replacing the data file; all cooperative append and repair
operations share that sidecar lock.

The test does not claim multi-host/NFS/object-store safety.
"""
from __future__ import annotations
import argparse
import fcntl
import hashlib
import importlib.util
import json
import multiprocessing as mp
import os
from pathlib import Path
import random
import tempfile
import time
from typing import Any

EXPECTED_WRITER_GIT_BLOB = "70843c8011eed717001d31cfe59028beb86739c4"
STABLE_FILENAME = "stable_sidecar_flocked_cas_writer_2026-08-28.py"


def git_blob_sha(path: Path) -> str:
    b = path.read_bytes()
    return hashlib.sha1(f"blob {len(b)}\0".encode() + b).hexdigest()


def load_current_writer(path: Path) -> Any:
    if git_blob_sha(path) != EXPECTED_WRITER_GIT_BLOB:
        raise RuntimeError("current writer source does not match frozen blob")
    spec = importlib.util.spec_from_file_location("_current_eval_writer", path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_stable_writer() -> Any:
    p = Path(__file__).resolve().with_name(STABLE_FILENAME)
    spec = importlib.util.spec_from_file_location("_stable_eval_writer", p)
    if spec is None or spec.loader is None:
        raise ImportError(p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _old_inode_holder(path: str, locked: mp.synchronize.Event, release: mp.synchronize.Event, q: mp.Queue) -> None:  # type: ignore[name-defined]
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.lseek(fd, 0, os.SEEK_SET)
        before = os.read(fd, 1 << 20)
        old_inode = os.fstat(fd).st_ino
        if before != b"BASE":
            q.put({"role": "old_writer", "ok": False, "reason": "unexpected prefix"})
            return
        locked.set()
        if not release.wait(10):
            q.put({"role": "old_writer", "ok": False, "reason": "release timeout"})
            return
        os.lseek(fd, 0, os.SEEK_END)
        os.write(fd, b"A")
        os.fsync(fd)
        os.lseek(fd, 0, os.SEEK_SET)
        readback = os.read(fd, 1 << 20)
        q.put({"role": "old_writer", "ok": readback == b"BASEA", "inode": old_inode, "readback": readback.decode()})
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def _new_inode_writer(path: str, module_path: str, q: mp.Queue) -> None:
    try:
        m = load_current_writer(Path(module_path))
        out = m.PosixFlockedCASAppendWriter(path).append_fsync_readback(b"BASE", b"C")
        q.put({"role": "new_writer", "ok": out == b"BASEC", "readback": out.decode(), "inode": os.stat(path).st_ino})
    except Exception as e:
        q.put({"role": "new_writer", "ok": False, "reason": f"{type(e).__name__}: {e}"})


def reproduce_path_replacement_hole(module_path: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as td:
        journal = Path(td) / "journal.bin"
        journal.write_bytes(b"BASE")
        original_inode = journal.stat().st_ino
        locked = mp.Event()
        release = mp.Event()
        q: mp.Queue = mp.Queue()
        p_old = mp.Process(target=_old_inode_holder, args=(str(journal), locked, release, q))
        p_old.start()
        if not locked.wait(10):
            p_old.terminate(); p_old.join()
            raise RuntimeError("old writer did not acquire lock")

        replacement = Path(td) / "repaired.tmp"
        replacement.write_bytes(b"BASE")
        os.replace(replacement, journal)
        replacement_inode = journal.stat().st_ino
        if replacement_inode == original_inode:
            raise RuntimeError("test filesystem reused inode unexpectedly")

        p_new = mp.Process(target=_new_inode_writer, args=(str(journal), str(module_path), q))
        p_new.start()
        p_new.join(10)
        if p_new.is_alive():
            p_new.terminate(); p_new.join()
            raise RuntimeError("new writer blocked on old inode flock; test assumption failed")
        release.set()
        p_old.join(10)
        messages = [q.get(timeout=2), q.get(timeout=2)]
        final_path = journal.read_bytes()
        return {
            "original_inode": original_inode,
            "replacement_inode": replacement_inode,
            "both_writers_reported_success": all(bool(x.get("ok")) for x in messages),
            "messages": sorted(messages, key=lambda x: x["role"]),
            "pathname_final": final_path.decode(),
            "old_inode_append_not_visible_at_path": final_path == b"BASEC",
            "hazard_reproduced": all(bool(x.get("ok")) for x in messages) and final_path == b"BASEC",
        }


def _preopened_then_locked_writer(path: str, opened: mp.synchronize.Event, repair_done: mp.synchronize.Event, release: mp.synchronize.Event, q: mp.Queue) -> None:  # type: ignore[name-defined]
    """Mirror current writer ordering: open pathname first, then acquire flock."""
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        old_inode = os.fstat(fd).st_ino
        opened.set()
        if not repair_done.wait(10):
            q.put({"role": "preopened_writer", "ok": False, "reason": "repair timeout"})
            return
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.lseek(fd, 0, os.SEEK_SET)
        before = os.read(fd, 1 << 20)
        if before != b"BASE":
            q.put({"role": "preopened_writer", "ok": False, "reason": f"unexpected old prefix {before!r}"})
            return
        if not release.wait(10):
            q.put({"role": "preopened_writer", "ok": False, "reason": "release timeout"})
            return
        os.lseek(fd, 0, os.SEEK_END)
        os.write(fd, b"A")
        os.fsync(fd)
        os.lseek(fd, 0, os.SEEK_SET)
        rb = os.read(fd, 1 << 20)
        q.put({"role": "preopened_writer", "ok": rb == b"BASEA", "inode": old_inode, "readback": rb.decode()})
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        except OSError:
            pass
        os.close(fd)


def _datafile_flocked_repair(path: str, opened: mp.synchronize.Event, repair_done: mp.synchronize.Event, q: mp.Queue) -> None:  # type: ignore[name-defined]
    if not opened.wait(10):
        q.put({"role": "repair", "ok": False, "reason": "open timeout"})
        return
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.lseek(fd, 0, os.SEEK_SET)
        before = os.read(fd, 1 << 20)
        old_inode = os.fstat(fd).st_ino
        if before != b"BASE":
            q.put({"role": "repair", "ok": False, "reason": "unexpected prefix"})
            return
        tmp = Path(path).with_name(Path(path).name + f".repair.{os.getpid()}")
        with open(tmp, "wb") as f:
            f.write(b"BASE")
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(Path(path).parent, os.O_RDONLY)
        try: os.fsync(dfd)
        finally: os.close(dfd)
        new_inode = os.stat(path).st_ino
        q.put({"role": "repair", "ok": True, "old_inode": old_inode, "new_inode": new_inode})
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
        repair_done.set()


def reproduce_open_before_lock_toctou(module_path: Path) -> dict[str, Any]:
    """Cooperative repair takes data-file flock, yet a preopened writer escapes it."""
    with tempfile.TemporaryDirectory() as td:
        journal = Path(td) / "journal.bin"
        journal.write_bytes(b"BASE")
        opened = mp.Event(); repair_done = mp.Event(); release = mp.Event(); q: mp.Queue = mp.Queue()
        pw = mp.Process(target=_preopened_then_locked_writer, args=(str(journal), opened, repair_done, release, q))
        pr = mp.Process(target=_datafile_flocked_repair, args=(str(journal), opened, repair_done, q))
        pw.start(); pr.start()
        if not repair_done.wait(10):
            for p in (pw,pr):
                if p.is_alive(): p.terminate(); p.join()
            raise RuntimeError("cooperative repair did not finish")
        pn = mp.Process(target=_new_inode_writer, args=(str(journal), str(module_path), q))
        pn.start(); pn.join(10)
        if pn.is_alive():
            pn.terminate(); pn.join(); raise RuntimeError("new inode writer blocked")
        release.set(); pw.join(10); pr.join(10)
        msgs=[q.get(timeout=2) for _ in range(3)]
        final=journal.read_bytes()
        byrole={m["role"]:m for m in msgs}
        return {
            "messages": sorted(msgs,key=lambda x:x["role"]),
            "all_three_operations_succeeded": all(bool(m.get("ok")) for m in msgs),
            "old_and_new_inode_differ": byrole["repair"].get("old_inode") != byrole["repair"].get("new_inode"),
            "pathname_final": final.decode(),
            "old_inode_append_not_visible_at_path": final == b"BASEC",
            "hazard_reproduced": all(bool(m.get("ok")) for m in msgs) and final == b"BASEC",
        }


def _stable_append_worker(path: str, expected: bytes, frame: bytes, q: mp.Queue, jitter: float) -> None:
    try:
        time.sleep(jitter)
        out = load_stable_writer().StableSidecarFlockedCASWriter(path).append_fsync_readback(expected, frame)
        q.put(("append", True, out))
    except Exception as e:
        q.put(("append", False, type(e).__name__))


def _stable_repair_worker(path: str, expected: bytes, replacement: bytes, q: mp.Queue, jitter: float) -> None:
    try:
        time.sleep(jitter)
        out = load_stable_writer().StableSidecarFlockedCASWriter(path).replace_if_exact(expected, replacement)
        q.put(("repair", True, out))
    except Exception as e:
        q.put(("repair", False, type(e).__name__))


def stress_stable_lock(rounds: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    append_wins = repair_wins = bad = 0
    duplicate_append_bad = 0
    for _ in range(rounds):
        with tempfile.TemporaryDirectory() as td:
            journal = Path(td) / "journal.bin"
            journal.write_bytes(b"BASEBAD")
            q: mp.Queue = mp.Queue()
            ps = [
                mp.Process(target=_stable_append_worker, args=(str(journal), b"BASEBAD", b"A", q, rng.random() / 1000)),
                mp.Process(target=_stable_repair_worker, args=(str(journal), b"BASEBAD", b"BASE", q, rng.random() / 1000)),
            ]
            rng.shuffle(ps)
            for p in ps: p.start()
            for p in ps: p.join(10)
            msgs = [q.get(timeout=2), q.get(timeout=2)]
            winners = [m for m in msgs if m[1]]
            final = journal.read_bytes()
            if len(winners) != 1:
                bad += 1
            elif winners[0][0] == "append":
                append_wins += 1
                if final != b"BASEBADA": bad += 1
            else:
                repair_wins += 1
                if final != b"BASE": bad += 1

        with tempfile.TemporaryDirectory() as td:
            journal = Path(td) / "journal.bin"
            journal.write_bytes(b"BASE")
            q2: mp.Queue = mp.Queue()
            ps2 = [
                mp.Process(target=_stable_append_worker, args=(str(journal), b"BASE", b"X", q2, rng.random() / 1000)),
                mp.Process(target=_stable_append_worker, args=(str(journal), b"BASE", b"Y", q2, rng.random() / 1000)),
            ]
            for p in ps2: p.start()
            for p in ps2: p.join(10)
            msgs2 = [q2.get(timeout=2), q2.get(timeout=2)]
            wins2 = [m for m in msgs2 if m[1]]
            if len(wins2) != 1 or journal.read_bytes() not in {b"BASEX", b"BASEY"}:
                duplicate_append_bad += 1

    return {
        "rounds": rounds,
        "append_vs_repair": {"append_wins": append_wins, "repair_wins": repair_wins, "bad_rounds": bad},
        "duplicate_append_bad_rounds": duplicate_append_bad,
        "stable_lock_candidate_passed": bad == 0 and duplicate_append_bad == 0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--writer", required=True)
    ap.add_argument("--rounds", type=int, default=500)
    ap.add_argument("--seed", type=int, default=280828)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    writer_path = Path(args.writer)
    blob = git_blob_sha(writer_path)
    hazard = reproduce_path_replacement_hole(writer_path)
    open_before_lock = reproduce_open_before_lock_toctou(writer_path)
    stress = stress_stable_lock(args.rounds, args.seed)
    result = {
        "schema_version": 1,
        "frozen_writer_git_blob": blob,
        "expected_writer_git_blob": EXPECTED_WRITER_GIT_BLOB,
        "writer_blob_exact": blob == EXPECTED_WRITER_GIT_BLOB,
        "path_replacement_hazard": hazard,
        "open_before_lock_cooperative_repair_hazard": open_before_lock,
        "stable_sidecar_candidate": stress,
        "scope": [
            "Linux/single-host/cooperative processes with POSIX flock semantics only.",
            "The hazard requires pathname replacement/rename while a writer still holds the data-file flock; same-inode append races alone do not expose it.",
            "The stable-sidecar result assumes every cooperative append and repair path acquires the same non-replaced lock inode before opening/replacing the data file.",
            "No multi-host, NFS, object-store, malicious bypass, arbitrary durable-byte corruption, or distributed fencing claim is made."
        ]
    }
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    mp.set_start_method("fork", force=True)
    main()
