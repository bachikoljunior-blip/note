#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import sys
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_public_page import fetch_public_page  # noqa: E402


class FakeResponse:
    def __init__(self, status: int, body: bytes, url: str) -> None:
        self.status = status
        self.body = body
        self.url = url

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def geturl(self) -> str:
        return self.url

    def read(self, limit: int) -> bytes:
        return self.body[:limit]


class SequenceOpener:
    def __init__(self, outcomes: list[object]) -> None:
        self.outcomes = list(outcomes)
        self.calls = 0

    def __call__(self, request: object, timeout: int) -> FakeResponse:
        del request, timeout
        outcome = self.outcomes[self.calls]
        self.calls += 1
        if isinstance(outcome, BaseException):
            raise outcome
        assert isinstance(outcome, FakeResponse)
        return outcome


def http_error(code: int, body: bytes = b"error") -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        "https://example.test/item",
        code,
        "test",
        hdrs=None,
        fp=io.BytesIO(body),
    )


def main() -> int:
    tests: list[dict[str, object]] = []

    sleeps: list[int] = []
    opener = SequenceOpener(
        [http_error(403), FakeResponse(200, b"published", "https://example.test/item")]
    )
    recovered = fetch_public_page(
        "https://example.test/item", opener=opener, sleeper=sleeps.append, delays=(1, 2)
    )
    tests.append(
        {
            "name": "transient_403_recovers",
            "ok": recovered["status"] == 200
            and recovered["terminal_error"] is None
            and len(recovered["attempts"]) == 2
            and sleeps == [1],
        }
    )

    sleeps = []
    opener = SequenceOpener([http_error(403), http_error(403), http_error(403)])
    persistent = fetch_public_page(
        "https://example.test/item", opener=opener, sleeper=sleeps.append, delays=(1, 2)
    )
    tests.append(
        {
            "name": "persistent_403_fails_closed",
            "ok": persistent["status"] == 403
            and persistent["terminal_error"] == "http_error:403"
            and len(persistent["attempts"]) == 3
            and sleeps == [1, 2],
        }
    )

    sleeps = []
    opener = SequenceOpener([http_error(404)])
    not_found = fetch_public_page(
        "https://example.test/item", opener=opener, sleeper=sleeps.append, delays=(1, 2)
    )
    tests.append(
        {
            "name": "not_found_does_not_retry",
            "ok": not_found["status"] == 404
            and not_found["terminal_error"] == "http_error:404"
            and len(not_found["attempts"]) == 1
            and sleeps == [],
        }
    )

    sleeps = []
    opener = SequenceOpener(
        [urllib.error.URLError("temporary"), FakeResponse(200, b"published", "https://example.test/item")]
    )
    network = fetch_public_page(
        "https://example.test/item", opener=opener, sleeper=sleeps.append, delays=(1, 2)
    )
    tests.append(
        {
            "name": "network_error_recovers",
            "ok": network["status"] == 200
            and network["terminal_error"] is None
            and len(network["attempts"]) == 2
            and sleeps == [1],
        }
    )

    errors = [str(item["name"]) for item in tests if not item["ok"]]
    payload = {"ok": not errors, "tests": tests, "errors": errors}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
