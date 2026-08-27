"""Single-host cross-process serialized append writer for evaluation journals.

The writer combines an OS-held exclusive flock with exact whole-file CAS and
fsync/readback while the lock remains held. It is intended for the existing
ADMIT/SLOT/CLOSE and RESERVE/COMMIT append protocols, whose cross-file partial
orders are already handled by fail-closed recovery.

Scope: cooperative processes on a filesystem where POSIX flock is a reliable
single-host exclusion primitive. This is not a distributed lease and makes no
claim for NFS/object-store semantics or callers that bypass this writer.
"""
from __future__ import annotations
import fcntl
import os
from pathlib import Path


class AppendCASMismatch(RuntimeError):
    pass


class AppendReadbackMismatch(RuntimeError):
    pass


class PosixFlockedCASAppendWriter:
    def __init__(self, path: str | os.PathLike[str], mode: int = 0o600) -> None:
        self.path = Path(path)
        self.mode = int(mode)

    @staticmethod
    def _read_all(fd: int) -> bytes:
        os.lseek(fd, 0, os.SEEK_SET)
        parts = []
        while True:
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                break
            parts.append(chunk)
        return b"".join(parts)

    @staticmethod
    def _write_all(fd: int, data: bytes) -> None:
        view = memoryview(data)
        offset = 0
        while offset < len(view):
            n = os.write(fd, view[offset:])
            if n <= 0:
                raise OSError("short append write")
            offset += n

    def append_fsync_readback(self, expected_before: bytes, frame: bytes) -> bytes:
        expected = bytes(expected_before)
        frame = bytes(frame)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, self.mode)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            current = self._read_all(fd)
            if current != expected:
                raise AppendCASMismatch("durable prefix differs from expected_before")
            os.lseek(fd, 0, os.SEEK_END)
            self._write_all(fd, frame)
            os.fsync(fd)
            durable = self._read_all(fd)
            wanted = expected + frame
            if durable != wanted:
                raise AppendReadbackMismatch("post-fsync exact readback mismatch")
            return durable
        finally:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)


__all__ = [
    "AppendCASMismatch", "AppendReadbackMismatch",
    "PosixFlockedCASAppendWriter",
]
