#!/usr/bin/env python3
"""Conservative Assistants API migration helper.

Only a transformation proven to be one-to-one by the official migration guide is
applied automatically: an empty Thread creation becomes an empty Conversation
creation. Everything else is reported for human review.
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", "__pycache__", ".venv", "venv", ".next", "target"}
SUFFIXES = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}

# The official guide shows empty threads and empty conversations as equivalent.
# Thread creation with messages is deliberately excluded: messages must become items.
SAFE_REWRITES = [
    (
        "empty threads.create() -> conversations.create()",
        re.compile(r"\bbeta\.threads\.create\s*\(\s*\)"),
        "conversations.create()",
    ),
]

FLAGS = [
    ("assistant configuration", re.compile(r"\bbeta\.assistants\b|\bassistant_?[Ii]d\b"),
     "Assistants become dashboard-managed prompts; choose and configure a prompt ID."),
    ("thread with initial messages", re.compile(r"\bbeta\.threads\.create\s*\((?!\s*\))"),
     "Thread messages must become Conversation items; argument shapes differ."),
    ("thread messages", re.compile(r"\bbeta\.threads\.messages\b"),
     "Move user input into responses.create(input=...) or Conversation items."),
    ("runs", re.compile(r"\bbeta\.threads\.runs\b|\bruns\.(?:poll|stream|createAndPoll|create_and_poll)\b"),
     "Runs become Responses; model/prompt, input, polling, streaming and tool loops require design changes."),
    ("thread identifier", re.compile(r"\bthread_?[Ii]d\b"),
     "Migrate stored thread IDs to conversation IDs; do not blindly rename endpoint arguments."),
    ("run identifier", re.compile(r"\brun_?[Ii]d\b"),
     "Response IDs and lifecycle semantics differ from Run IDs."),
    ("hosted tools", re.compile(r"\b(?:vector_stores?|file_search|code_interpreter)\b"),
     "Verify tool configuration and result handling against the current Responses API docs."),
]


def walk(root: Path):
    if root.is_file():
        yield root
        return
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUFFIXES and not any(part in SKIP_DIRS for part in path.parts):
            yield path


def process(root: Path, apply: bool) -> dict:
    changed_files = []
    needs_human = []
    total_rewrites = 0
    for path in walk(root):
        try:
            original = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rewritten = original
        counts = {}
        for label, pattern, replacement in SAFE_REWRITES:
            rewritten, count = pattern.subn(replacement, rewritten)
            if count:
                counts[label] = count
                total_rewrites += count
        for lineno, line in enumerate(original.splitlines(), 1):
            for kind, pattern, why in FLAGS:
                if pattern.search(line):
                    needs_human.append({"file": str(path), "line": lineno, "kind": kind,
                                        "why": why, "text": line.strip()[:160]})
        if counts:
            diff = "".join(difflib.unified_diff(
                original.splitlines(keepends=True), rewritten.splitlines(keepends=True),
                fromfile=str(path), tofile=str(path) + " (proposed)"))
            changed_files.append({"file": str(path), "rewrites": counts, "diff": diff})
            if apply:
                path.with_suffix(path.suffix + ".bak").write_text(original, encoding="utf-8")
                path.write_text(rewritten, encoding="utf-8")
    return {"applied": apply, "rewritten_sites": total_rewrites,
            "changed_files": changed_files, "needs_human": needs_human,
            "sunset_date": "2026-08-26"}


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python codemod.py <path> [--apply] [--json]")
        return 2
    root = Path(sys.argv[1])
    if not root.exists():
        print(f"not found: {root}")
        return 1
    result = process(root, "--apply" in sys.argv)
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    print(f"Safe automatic rewrites: {result['rewritten_sites']}")
    for item in result["changed_files"]:
        print(item["diff"], end="")
    print(f"Human-review findings: {len(result['needs_human'])}")
    for item in result["needs_human"][:20]:
        print(f"  {item['file']}:{item['line']} [{item['kind']}] {item['why']}")
    if result["applied"]:
        print("Applied safe rewrites. Original files were preserved as .bak files.")
    else:
        print("Dry run only. Add --apply to write the safe subset.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
