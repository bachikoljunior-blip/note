"""Independent source-shaped counterexamples for Argus planner verdict persistence evidence.

Scope: transcribes only the public planner_verdict_was_persisted scan semantics
from lbx154/Argus@ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98. It does not import Argus.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path


def current_boolean_scan(root: Path, delivery_id: str) -> bool:
    for path in sorted(root.glob("events.jsonl*")):
        if not path.is_file():
            continue
        try:
            with path.open(encoding="utf-8") as handle:
                for line in handle:
                    if delivery_id not in line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if (
                        event.get("type") == "life.planner.verdict"
                        and event.get("delivery_id") == delivery_id
                    ):
                        return True
        except OSError:
            continue
    return False


def run() -> None:
    target = "deadbeef"

    # Counterexample 1: target-bearing bytes exist but UTF-8 decoding fails.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "events.jsonl").write_bytes(
            b'{"type":"life.planner.verdict","delivery_id":"deadbeef","x":"\xff"}\n'
        )
        try:
            current_boolean_scan(root, target)
        except UnicodeDecodeError:
            pass
        else:
            raise AssertionError("expected UnicodeDecodeError to escape the current scan")

    # Counterexample 2: a malformed JSON row contains the exact target id.
    # Current code skips it and returns False, although target absence is not proven.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "events.jsonl").write_text(
            '{"type":"life.planner.verdict","delivery_id":"deadbeef", BAD}\n',
            encoding="utf-8",
        )
        assert current_boolean_scan(root, target) is False

    # Sanity: a complete well-formed scan can prove FOUND.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "events.jsonl").write_text(
            json.dumps({"type": "life.planner.verdict", "delivery_id": target}) + "\n",
            encoding="utf-8",
        )
        assert current_boolean_scan(root, target) is True

    print("PASS: current boolean surface conflates unprovable absence with False and can raise on UTF-8 corruption")


if __name__ == "__main__":
    run()
