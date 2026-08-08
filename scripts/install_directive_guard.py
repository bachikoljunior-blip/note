#!/usr/bin/env python3
"""恒久指示のフックを ~/.claude へ設置する（何度実行しても安全）。

コンテナは使い捨てなので `~/.claude/` は次のセッションに残らない。
残るのはリポジトリだけなので、実体をここに置き、起動時にこれを実行して設置する。

    python scripts/install_directive_guard.py          # 設置
    python scripts/install_directive_guard.py --check  # 設置済みか確認するだけ

ハーネス側の `~/.claude/launcher-settings.json` は触らない。別ファイルなので、
両方のフックがマージされて動く。
"""
from __future__ import annotations

import argparse
import errno
import json
import os
import shutil
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "directive_guard.py"
HOME_CLAUDE = Path.home() / ".claude"
TARGET = HOME_CLAUDE / "directive-guard.py"
SETTINGS = HOME_CLAUDE / "settings.json"

HOOKS = {
    "SessionStart": ("session-start", "恒久指示を読み込み中"),
    "UserPromptSubmit": ("prompt-submit", None),
    "Stop": ("stop", "終わるのが最善か確認中"),
}


def running_in_codex() -> bool:
    """Return true when Claude hook installation is not part of this runtime.

    Codex reads the repository bootstrap directly and does not execute Claude's
    ~/.claude hooks. Some Codex sandboxes also expose the home directory as
    read-only, so failing the whole bootstrap on that path is both noisy and
    incapable of adding protection.
    """
    return any(
        os.environ.get(name)
        for name in ("CODEX_PRIMARY_RUNTIME", "CODEX_CI", "CODEX_THREAD_ID")
    )


def codex_skip_payload(exc: OSError | None = None) -> dict:
    payload: dict = {
        "installed": False,
        "supported": False,
        "skipped": True,
        "runtime": "codex",
        "reason": "claude_hooks_not_used_in_codex_runtime",
        "directive_source_verified": SOURCE.is_file(),
        "required_follow_up": "run scripts/check_directive_integrity.py",
    }
    if exc is not None:
        payload["target_write_error"] = type(exc).__name__
        payload["target_write_errno"] = exc.errno
    return payload


def desired(event: str) -> dict:
    mode, status = HOOKS[event]
    hook: dict = {"type": "command", "command": f"~/.claude/directive-guard.py {mode}", "timeout": 10}
    if status:
        hook["statusMessage"] = status
    entry: dict = {"hooks": [hook]}
    if event == "Stop":
        entry["matcher"] = ""
    return entry


def installed_ok() -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not TARGET.is_file():
        problems.append("directive-guard.py が未設置")
    elif SOURCE.is_file() and TARGET.read_bytes() != SOURCE.read_bytes():
        problems.append("directive-guard.py がリポジトリ側と一致しない")
    if not SETTINGS.is_file():
        problems.append("settings.json が無い")
        return False, problems
    try:
        settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        problems.append(f"settings.json が壊れている: {exc}")
        return False, problems
    for event, (mode, _) in HOOKS.items():
        want = f"~/.claude/directive-guard.py {mode}"
        found = any(
            hook.get("command") == want
            for entry in settings.get("hooks", {}).get(event, [])
            for hook in entry.get("hooks", [])
        )
        if not found:
            problems.append(f"{event} フックが登録されていない")
    return not problems, problems


def install() -> None:
    HOME_CLAUDE.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, TARGET)
    TARGET.chmod(TARGET.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    settings: dict = {}
    if SETTINGS.is_file():
        try:
            settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            backup = SETTINGS.with_suffix(".json.broken")
            shutil.copyfile(SETTINGS, backup)
            print(f"settings.json が壊れていたので {backup.name} へ退避して作り直します")
            settings = {}

    settings.setdefault("$schema", "https://json.schemastore.org/claude-code-settings.json")
    hooks = settings.setdefault("hooks", {})
    for event, (mode, _) in HOOKS.items():
        want = f"~/.claude/directive-guard.py {mode}"
        entries = hooks.setdefault(event, [])
        # 既存の他フックは消さない。自分のものだけ入れ替える。
        entries[:] = [
            e for e in entries
            if not any(h.get("command") == want for h in e.get("hooks", []))
        ]
        entries.append(desired(event))
    SETTINGS.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if not SOURCE.is_file():
        print(f"元ファイルがありません: {SOURCE}")
        return 1

    if args.check:
        ok, problems = installed_ok()
        if not ok and running_in_codex():
            payload = codex_skip_payload()
            payload["problems"] = problems
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0
        print(json.dumps({"installed": ok, "problems": problems}, ensure_ascii=False, indent=2))
        return 0 if ok else 1

    try:
        install()
    except OSError as exc:
        if running_in_codex() and exc.errno in (errno.EACCES, errno.EPERM, errno.EROFS):
            print(json.dumps(codex_skip_payload(exc), ensure_ascii=False, indent=2))
            return 0
        raise
    ok, problems = installed_ok()
    print(json.dumps({"installed": ok, "problems": problems,
                      "target": str(TARGET), "settings": str(SETTINGS)},
                     ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
