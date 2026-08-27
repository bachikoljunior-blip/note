"""Detection stress for uncooperative sidecar lock pathname replacement.

This does not make lock replacement safe. It only verifies that an operation
holding the old lock inode refuses to report success if the sidecar pathname is
rebound before operation exit.
"""
from __future__ import annotations
import multiprocessing as mp
import os
from pathlib import Path
import tempfile
from stable_sidecar_journal_io_2026_08_28 import StableSidecarJournalIO


def holder(path: str, ready: mp.Event, release: mp.Event, q: mp.Queue) -> None:
    io = StableSidecarJournalIO(path)
    try:
        with io.locked():
            ready.set()
            if not release.wait(5):
                q.put(("timeout", ""))
                return
        q.put(("unexpected_success", ""))
    except Exception as exc:
        q.put((type(exc).__name__, str(exc)))


def one() -> tuple[str, str]:
    with tempfile.TemporaryDirectory(prefix="eval-lock-tamper-") as td:
        pth = Path(td) / "main"
        io = StableSidecarJournalIO(pth)
        io.read_locked()
        ready = mp.Event(); release = mp.Event(); q = mp.Queue()
        p = mp.Process(target=holder, args=(str(pth), ready, release, q))
        p.start()
        if not ready.wait(5):
            p.kill(); p.join()
            raise AssertionError("holder never acquired lock")
        replacement = io.lock_path.with_name(io.lock_path.name + ".replacement")
        replacement.write_bytes(b"new lock inode")
        os.replace(replacement, io.lock_path)
        release.set()
        p.join(5)
        if p.is_alive():
            p.kill(); p.join()
            raise AssertionError("holder hung")
        return q.get(timeout=2)


def main():
    mp.set_start_method("fork", force=True)
    n = 100
    rows = [one() for _ in range(n)]
    detected = sum(r[0] == "StableLockProtocolViolation" for r in rows)
    unexpected = [r for r in rows if r[0] != "StableLockProtocolViolation"]
    import json
    print(json.dumps({"schema_version":1,"trials":n,"detected":detected,"unexpected":unexpected[:10]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
