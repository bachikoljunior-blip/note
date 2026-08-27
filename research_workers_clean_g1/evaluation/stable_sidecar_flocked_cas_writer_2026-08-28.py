"""Single-host cooperative append/repair serialization with a stable sidecar lock.

Unlike locking the journal data inode itself, this protocol acquires a dedicated
lock inode *before* opening or atomically replacing the data pathname.  All
cooperative append and repair operations must use the same sidecar lock file,
and the protocol must never rename/unlink/replace that lock file.

Scope: local filesystems with reliable POSIX flock semantics.  This is not a
multi-host/distributed fencing protocol and does not constrain bypassing callers.
"""
from __future__ import annotations
import fcntl
import os
from pathlib import Path


class StableLockCASMismatch(RuntimeError):
    pass


class StableLockReadbackMismatch(RuntimeError):
    pass


class StableSidecarFlockedCASWriter:
    def __init__(self, path: str | os.PathLike[str], mode: int = 0o600) -> None:
        self.path = Path(path)
        self.lock_path = self.path.with_name(self.path.name + ".lock")
        self.mode = int(mode)

    @staticmethod
    def _read_all(fd: int) -> bytes:
        os.lseek(fd, 0, os.SEEK_SET)
        chunks: list[bytes] = []
        while True:
            c = os.read(fd, 1 << 20)
            if not c:
                break
            chunks.append(c)
        return b"".join(chunks)

    @staticmethod
    def _write_all(fd: int, data: bytes) -> None:
        view = memoryview(data)
        off = 0
        while off < len(view):
            n = os.write(fd, view[off:])
            if n <= 0:
                raise OSError("short write")
            off += n

    def _lock(self) -> int:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.lock_path, os.O_RDWR | os.O_CREAT, self.mode)
        fcntl.flock(fd, fcntl.LOCK_EX)
        return fd

    def append_fsync_readback(self, expected_before: bytes, frame: bytes) -> bytes:
        expected = bytes(expected_before)
        frame = bytes(frame)
        lfd = self._lock()
        try:
            fd = os.open(self.path, os.O_RDWR | os.O_CREAT, self.mode)
            try:
                current = self._read_all(fd)
                if current != expected:
                    raise StableLockCASMismatch("append CAS mismatch")
                os.lseek(fd, 0, os.SEEK_END)
                self._write_all(fd, frame)
                os.fsync(fd)
                durable = self._read_all(fd)
                if durable != expected + frame:
                    raise StableLockReadbackMismatch("append readback mismatch")
                return durable
            finally:
                os.close(fd)
        finally:
            fcntl.flock(lfd, fcntl.LOCK_UN)
            os.close(lfd)

    def replace_if_exact(self, expected_before: bytes, replacement: bytes) -> bytes:
        """Atomically replace the data path only while holding the stable lock."""
        expected = bytes(expected_before)
        replacement = bytes(replacement)
        lfd = self._lock()
        try:
            try:
                current = self.path.read_bytes()
            except FileNotFoundError:
                current = b""
            if current != expected:
                raise StableLockCASMismatch("repair CAS mismatch")
            tmp = self.path.with_name(self.path.name + f".repair.{os.getpid()}")
            with open(tmp, "wb") as f:
                f.write(replacement)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.path)
            dfd = os.open(self.path.parent, os.O_RDONLY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
            durable = self.path.read_bytes()
            if durable != replacement:
                raise StableLockReadbackMismatch("repair readback mismatch")
            return durable
        finally:
            fcntl.flock(lfd, fcntl.LOCK_UN)
            os.close(lfd)


__all__ = [
    "StableLockCASMismatch", "StableLockReadbackMismatch",
    "StableSidecarFlockedCASWriter",
]
