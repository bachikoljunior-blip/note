"""Concrete single-writer append+fsync+readback implementation for evaluation journal.

The writer implements the DurableAppendWriter contract required by
``durable_launch_capability_gate_2026-08-28.py``.

Crash/retry semantics
---------------------
- current bytes == expected_before: append exactly frame, fsync file, fsync parent
  directory when the file was newly created, then read back and verify.
- current bytes == expected_before + frame: treat as an exact idempotent retry of
  a prior uncertain acknowledgement; fsync/readback again and return success
  without appending a duplicate frame.
- any other current bytes: fail closed as CAS mismatch. A torn frame must be
  repaired/truncated to the last independently verified valid journal prefix by
  the journal recovery layer before retry.

The optional fault_hook is for deterministic crash injection in validation and
must be omitted in production.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable


class DurableWriteError(RuntimeError):
    pass


class InjectedCrash(RuntimeError):
    pass


class FileDurableAppendWriter:
    def __init__(self, path: str | os.PathLike[str], *, fault_hook: Callable[[str, int], None] | None = None) -> None:
        self.path = Path(path)
        self.fault_hook = fault_hook

    def _fault(self, stage: str, fd: int) -> None:
        if self.fault_hook is not None:
            self.fault_hook(stage, fd)

    @staticmethod
    def _read_all(fd: int) -> bytes:
        os.lseek(fd, 0, os.SEEK_SET)
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)

    @staticmethod
    def _write_all(fd: int, data: bytes) -> None:
        view = memoryview(data)
        done = 0
        while done < len(view):
            n = os.write(fd, view[done:])
            if n <= 0:
                raise DurableWriteError("short/zero append")
            done += n

    def _fsync_parent_if_created(self, created: bool) -> None:
        if not created:
            return
        parent = self.path.parent
        flags = os.O_RDONLY
        if hasattr(os, "O_DIRECTORY"):
            flags |= os.O_DIRECTORY
        dfd = os.open(parent, flags)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)

    def append_fsync_readback(self, expected_before: bytes, frame: bytes) -> bytes:
        before = bytes(expected_before)
        fr = bytes(frame)
        after = before + fr
        self.path.parent.mkdir(parents=True, exist_ok=True)
        created = not self.path.exists()

        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            current = self._read_all(fd)
            if current == before:
                os.lseek(fd, 0, os.SEEK_END)
                self._write_all(fd, fr)
                self._fault("after_append_before_fsync", fd)
            elif current == after:
                # Exact uncertain-ack retry: do not append a duplicate frame.
                self._fault("exact_retry_before_fsync", fd)
            else:
                raise DurableWriteError("expected-before CAS mismatch or torn/conflicting tail")

            os.fsync(fd)
            self._fsync_parent_if_created(created)
            self._fault("after_fsync_before_readback", fd)

            readback = self._read_all(fd)
            if readback != after:
                raise DurableWriteError("post-fsync full readback mismatch")
            self._fault("after_readback_before_return", fd)
            return readback
        finally:
            os.close(fd)


__all__ = ["DurableWriteError", "InjectedCrash", "FileDurableAppendWriter"]
