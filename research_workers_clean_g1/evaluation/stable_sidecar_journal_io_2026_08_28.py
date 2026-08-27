"""Stable-sidecar append/repair facade for single-host cooperative evaluation journals.

All append and torn-tail repair operations acquire a protocol-stable sidecar flock
*before* opening or replacing the data pathname. The sidecar pathname must never
be renamed, unlinked, or replaced by compliant callers.

This is local POSIX fencing only. It is not a multi-host/distributed lock.
"""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import os
from pathlib import Path
import tempfile
from typing import Callable, Iterator


class StableLockProtocolViolation(RuntimeError):
    pass


class StableLockCASMismatch(RuntimeError):
    pass


class StableLockReadbackMismatch(RuntimeError):
    pass


class StableSidecarJournalIO:
    def __init__(self, path: str | os.PathLike[str], mode: int = 0o600) -> None:
        self.path = Path(path)
        self.lock_path = self.path.with_name(self.path.name + ".lock")
        self.mode = int(mode)

    @staticmethod
    def _read_all(fd: int) -> bytes:
        os.lseek(fd, 0, os.SEEK_SET)
        out: list[bytes] = []
        while True:
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                return b"".join(out)
            out.append(chunk)

    @staticmethod
    def _write_all(fd: int, data: bytes) -> None:
        view = memoryview(data)
        pos = 0
        while pos < len(view):
            n = os.write(fd, view[pos:])
            if n <= 0:
                raise OSError("short write")
            pos += n

    @staticmethod
    def _identity_from_fd(fd: int) -> tuple[int, int]:
        st = os.fstat(fd)
        return int(st.st_dev), int(st.st_ino)

    @staticmethod
    def _identity_from_path(path: Path) -> tuple[int, int]:
        st = os.stat(path)
        return int(st.st_dev), int(st.st_ino)

    def _assert_lock_identity(self, lock_fd: int, expected: tuple[int, int]) -> None:
        if self._identity_from_fd(lock_fd) != expected:
            raise StableLockProtocolViolation("open sidecar lock inode changed unexpectedly")
        try:
            observed = self._identity_from_path(self.lock_path)
        except FileNotFoundError as exc:
            raise StableLockProtocolViolation("sidecar lock pathname disappeared") from exc
        if observed != expected:
            raise StableLockProtocolViolation("sidecar lock pathname was rebound to another inode")

    @contextmanager
    def locked(self) -> Iterator[int]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lock_fd = os.open(self.lock_path, os.O_RDWR | os.O_CREAT, self.mode)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            identity = self._identity_from_fd(lock_fd)
            self._assert_lock_identity(lock_fd, identity)
            yield lock_fd
            self._assert_lock_identity(lock_fd, identity)
        finally:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            finally:
                os.close(lock_fd)

    def read_locked(self) -> bytes:
        with self.locked():
            try:
                return self.path.read_bytes()
            except FileNotFoundError:
                return b""

    def append_fsync_readback(self, expected_before: bytes, frame: bytes) -> bytes:
        expected = bytes(expected_before)
        frame = bytes(frame)
        with self.locked():
            fd = os.open(self.path, os.O_RDWR | os.O_CREAT, self.mode)
            try:
                current = self._read_all(fd)
                if current != expected:
                    raise StableLockCASMismatch("append CAS mismatch")
                data_identity = self._identity_from_fd(fd)
                os.lseek(fd, 0, os.SEEK_END)
                self._write_all(fd, frame)
                os.fsync(fd)
                durable = self._read_all(fd)
                if durable != expected + frame:
                    raise StableLockReadbackMismatch("append readback mismatch")
                if self._identity_from_path(self.path) != data_identity:
                    raise StableLockProtocolViolation(
                        "data pathname changed inode while stable sidecar lock was held"
                    )
                return durable
            finally:
                os.close(fd)

    def repair_valid_prefix(
        self,
        decode_valid_prefix: Callable[[bytes], tuple[object, int, str]],
    ) -> tuple[bytes, dict[str, object]]:
        """Repair only a torn/invalid final tail to the decoder's valid prefix.

        The decoder is authoritative for the valid prefix. Already-valid earlier
        bytes are never rewritten semantically; repair only removes bytes after
        ``valid_len``. Clean EOF is a no-op.
        """
        with self.locked():
            try:
                current = self.path.read_bytes()
            except FileNotFoundError:
                current = b""
            _events, valid_len, tail_status = decode_valid_prefix(current)
            valid_len = int(valid_len)
            if not 0 <= valid_len <= len(current):
                raise StableLockProtocolViolation("decoder returned invalid prefix length")
            if tail_status == "clean_eof":
                if valid_len != len(current):
                    raise StableLockProtocolViolation("clean_eof with nonterminal valid_len")
                return current, {
                    "repaired": False,
                    "tail_status_before": tail_status,
                    "valid_len": valid_len,
                    "removed_bytes": 0,
                }
            replacement = current[:valid_len]
            fd, tmp_name = tempfile.mkstemp(
                prefix=self.path.name + ".repair.",
                dir=str(self.path.parent),
            )
            tmp = Path(tmp_name)
            try:
                os.fchmod(fd, self.mode)
                self._write_all(fd, replacement)
                os.fsync(fd)
                os.close(fd)
                fd = -1
                os.replace(tmp, self.path)
                dfd = os.open(self.path.parent, os.O_RDONLY)
                try:
                    os.fsync(dfd)
                finally:
                    os.close(dfd)
                durable = self.path.read_bytes()
                if durable != replacement:
                    raise StableLockReadbackMismatch("repair readback mismatch")
                _e2, n2, s2 = decode_valid_prefix(durable)
                if int(n2) != len(durable) or s2 != "clean_eof":
                    raise StableLockReadbackMismatch("repaired prefix does not decode cleanly")
                return durable, {
                    "repaired": True,
                    "tail_status_before": tail_status,
                    "valid_len": valid_len,
                    "removed_bytes": len(current) - valid_len,
                }
            finally:
                if fd >= 0:
                    os.close(fd)
                try:
                    tmp.unlink()
                except FileNotFoundError:
                    pass


__all__ = [
    "StableLockProtocolViolation",
    "StableLockCASMismatch",
    "StableLockReadbackMismatch",
    "StableSidecarJournalIO",
]
