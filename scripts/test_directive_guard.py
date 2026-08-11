#!/usr/bin/env python3
"""Validate exact-directive injection and one-review-per-user-turn behavior."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "tools" / "directive_guard.py"
CORE = (ROOT / "OPERATIONS" / "CORE_DIRECTIVE.md").read_text(encoding="utf-8").strip()
FAILURES: list[str] = []


def run(mode: str, session: str, home: Path, *, repo_root: Path | None = ROOT) -> tuple[int, str]:
    env = dict(os.environ, HOME=str(home))
    if repo_root is not None:
        env["REVENUE_REPO_ROOT"] = str(repo_root)
    result = subprocess.run(
        [sys.executable, str(GUARD), mode],
        input=json.dumps({"session_id": session}),
        capture_output=True, text=True, env=env,
    )
    return result.returncode, result.stdout


def check(label: str, ok: bool) -> None:
    print("{}  {}".format("PASS" if ok else "FAIL", label))
    if not ok:
        FAILURES.append(label)


def decision(out: str) -> str | None:
    try:
        return json.loads(out).get("decision")
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)
        code, out = run("session-start", "s1", home)
        payload = json.loads(out)
        context = payload["hookSpecificOutput"]["additionalContext"]
        superseded_tags = tuple("A" + str(n) for n in (1, 2, 9, 10, 12, 13, 14))
        check("SessionStart injects the complete current directive", CORE in context)
        check("SessionStart contains no superseded numbered tags", not any(tag in context for tag in superseded_tags))
        check("SessionStart does not block", code == 0 and "decision" not in payload)

        _, fallback_out = run("session-start", "fallback", home, repo_root=home / "missing")
        fallback_context = json.loads(fallback_out)["hookSpecificOutput"]["additionalContext"]
        check("Embedded fallback is the complete current directive", CORE in fallback_context)

        first_payload = json.loads(run("stop", "s1", home)[1])
        reason = first_payload.get("reason", "")
        check("First Stop blocks", first_payload.get("decision") == "block")
        for phrase in ("到達予測", "本人操作", "最新使用量", "主実行と監視"):
            check("Stop review includes " + phrase, phrase in reason)
        check("Second Stop passes", decision(run("stop", "s1", home)[1]) is None)
        check("Third Stop passes", decision(run("stop", "s1", home)[1]) is None)

        run("prompt-submit", "s1", home)
        check("A new prompt resets review", decision(run("stop", "s1", home)[1]) == "block")
        check("A different session is independent", decision(run("stop", "s2", home)[1]) == "block")

        code, _ = run("stop", "s3", home / "nope" / "deeper", repo_root=ROOT)
        check("An unwritable state path does not crash", code == 0)

    print()
    if FAILURES:
        print("{} checks failed: {}".format(len(FAILURES), ", ".join(FAILURES)))
        return 1
    print("All directive guard checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
