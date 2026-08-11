#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "directive_integrity_tests.json"

FILES = [
    "OPERATIONS/CORE_DIRECTIVE.md",
    "OPERATIONS/CORE_DIRECTIVE_MIRROR.md",
    "OPERATIONS/CORE_DIRECTIVE.b64",
    "OPERATIONS/DIRECTIVE_MANIFEST.json",
    "OPERATIONS/DIRECTIVE_BOUNDARY.md",
    "OPERATIONS/ASSISTANT_OPERATING_POLICY.md",
    "OPERATIONS/BOOTSTRAP.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    "scripts/check_directive_integrity.py",
    "tools/directive_guard.py",
    "scripts/test_directive_guard.py",
    "scripts/check_before_ending.py",
]


def make_case() -> Path:
    case = Path(tempfile.mkdtemp(prefix="directive-integrity-"))
    for rel in FILES:
        source = ROOT / rel
        target = case / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return case


def run(case: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(case / "scripts/check_directive_integrity.py"), *args],
        cwd=case,
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )


def test_baseline() -> dict[str, object]:
    case = make_case()
    result = run(case)
    return {"name": "baseline_passes", "ok": result.returncode == 0, "returncode": result.returncode}


def test_assistant_text_contamination() -> dict[str, object]:
    case = make_case()
    path = case / "OPERATIONS/CORE_DIRECTIVE.md"
    path.write_text(path.read_text(encoding="utf-8") + "\n合法・安全・持続可能な範囲で\n", encoding="utf-8")
    result = run(case)
    return {"name": "assistant_text_in_core_fails", "ok": result.returncode != 0, "returncode": result.returncode}


def test_single_copy_repair() -> dict[str, object]:
    case = make_case()
    canonical = case / "OPERATIONS/CORE_DIRECTIVE.md"
    mirror = case / "OPERATIONS/CORE_DIRECTIVE_MIRROR.md"
    mirror.write_text("damaged\n", encoding="utf-8")
    result = run(case, "--repair")
    repaired = mirror.read_bytes() == canonical.read_bytes()
    return {
        "name": "single_copy_repairs_from_two_exact_copies",
        "ok": result.returncode == 0 and repaired,
        "returncode": result.returncode,
        "repaired": repaired,
    }


def test_two_copy_corruption_fails_closed() -> dict[str, object]:
    case = make_case()
    (case / "OPERATIONS/CORE_DIRECTIVE_MIRROR.md").write_text("damaged\n", encoding="utf-8")
    (case / "OPERATIONS/CORE_DIRECTIVE.b64").write_text("not-base64\n", encoding="ascii")
    result = run(case, "--repair")
    return {
        "name": "two_copy_corruption_fails_closed",
        "ok": result.returncode != 0,
        "returncode": result.returncode,
    }


def test_missing_assistant_policy_fails_separation() -> dict[str, object]:
    case = make_case()
    (case / "OPERATIONS/ASSISTANT_OPERATING_POLICY.md").unlink()
    result = run(case)
    return {
        "name": "missing_separate_assistant_policy_fails",
        "ok": result.returncode != 0,
        "returncode": result.returncode,
    }


def main() -> int:
    tests = [
        test_baseline(),
        test_assistant_text_contamination(),
        test_single_copy_repair(),
        test_two_copy_corruption_fails_closed(),
        test_missing_assistant_policy_fails_separation(),
    ]
    errors = [test["name"] for test in tests if not test["ok"]]
    payload = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "tests": tests,
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
