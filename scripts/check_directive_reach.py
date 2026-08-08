#!/usr/bin/env python3
"""恒久指示が「実際に作業が起きるブランチ」に届いているかを測る。

`propagate_directive.py` はチェックアウト済みリポジトリの作業ツリーへ書くだけで、
**自動実行がどのブランチで走っているかを見ていなかった**。
2026-08-08 に測ったところ、毎日と6時間おきの収益自動実行はどちらも、
恒久指示が載っていないブランチで動いていた。届いていないものは設計ではない。

    python scripts/check_directive_reach.py                 # 測るだけ
    python scripts/check_directive_reach.py --fix           # 足りないブランチへ書いて push

対象は `config/directive_reach.json`。A2 により
`Simple-browser-cookie-clicker-game` の `main` だけは対象外にし、理由ごと出力する。
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "directive_reach.json"
REPORT = ROOT / "state" / "directive_reach.json"

sys.path.insert(0, str(ROOT / "scripts"))
from propagate_directive import BEGIN, END, build_block, manifest  # noqa: E402

MARKER = re.compile(r"sha256=([0-9a-f]{64})")


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=check,
    )


def block_version(text: str) -> str | None:
    if BEGIN not in text:
        return None
    found = MARKER.search(text[: text.find(END) if END in text else len(text)])
    return found.group(1) if found else None


def read_branch_file(repo: Path, branch: str) -> str | None:
    git(repo, "fetch", "origin", branch, check=False)
    result = git(repo, "show", f"origin/{branch}:CLAUDE.md", check=False)
    return result.stdout if result.returncode == 0 else None


def apply_to_branch(repo: Path, branch: str, block: str) -> dict:
    """作業ツリーを汚さずに、そのブランチの CLAUDE.md だけを更新して push する。"""
    existing = read_branch_file(repo, branch)
    if existing is None:
        existing = ""
    if BEGIN in existing and END in existing:
        head, _, rest = existing.partition(BEGIN)
        _, _, tail = rest.partition(END)
        updated = head.lstrip("\n") + block.strip() + "\n" + tail.lstrip("\n")
    else:
        updated = block.strip() + "\n\n" + existing

    worktree = repo / ".directive-reach-worktree"
    git(repo, "worktree", "remove", "--force", str(worktree), check=False)
    created = git(repo, "worktree", "add", "--force", str(worktree), f"origin/{branch}", check=False)
    if created.returncode != 0:
        return {"branch": branch, "status": "worktree_failed", "detail": created.stderr.strip()[:200]}
    try:
        git(worktree, "checkout", "-B", f"directive-reach/{branch.replace('/', '-')}")
        (worktree / "CLAUDE.md").write_text(updated, encoding="utf-8")
        git(worktree, "add", "CLAUDE.md")
        message = (
            "オーナーの恒久指示を、自動実行が実際に走るブランチへ載せる\n\n"
            "既定ブランチにだけ配っていたが、収益の自動実行はこのブランチで動いており、\n"
            "恒久指示が読み込まれていなかった。届いていないものは設計ではない。\n\n"
            "正本は bachikoljunior-blip/note の OPERATIONS/CORE_DIRECTIVE.md。\n"
            "手で編集せず、正本を直して scripts/propagate_directive.py を回すこと。\n\n"
            "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
        )
        committed = git(worktree, "commit", "-m", message, check=False)
        if committed.returncode != 0:
            return {"branch": branch, "status": "nothing_to_commit"}
        pushed = git(worktree, "push", "origin", f"HEAD:refs/heads/{branch}", check=False)
        if pushed.returncode != 0:
            return {"branch": branch, "status": "push_rejected",
                    "detail": pushed.stderr.strip().splitlines()[-1][:200] if pushed.stderr else ""}
        return {"branch": branch, "status": "pushed"}
    finally:
        git(repo, "worktree", "remove", "--force", str(worktree), check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--root", default="/home/user")
    args = parser.parse_args()

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    block = build_block(ROOT)
    expected = manifest(ROOT)["expected_sha256_utf8"]

    results: list[dict] = []
    for entry in config["targets"]:
        repo = Path(args.root) / entry["repo"]
        if entry.get("skip"):
            results.append({"repo": entry["repo"], "branch": entry.get("branch"),
                            "status": "skipped", "reason": entry["skip"]})
            continue
        if not (repo / ".git").exists():
            results.append({"repo": entry["repo"], "status": "not_checked_out"})
            continue
        for branch in entry["branches"]:
            text = read_branch_file(repo, branch)
            if text is None:
                state = "no_claude_md"
            else:
                version = block_version(text)
                state = "current" if version == expected else ("stale" if version else "missing_block")
            row = {"repo": entry["repo"], "branch": branch, "status": state}
            if args.fix and state != "current":
                row.update(apply_to_branch(repo, branch, block))
                row["status"] = row.get("status", state)
            results.append(row)

    reached = [r for r in results if r["status"] in {"current", "pushed"}]
    unreached = [r for r in results if r["status"] not in {"current", "pushed", "skipped"}]
    payload = {
        "checked_at": "see git history",
        "directive_sha256": expected,
        "reached": len(reached),
        "unreached": len(unreached),
        "ok": not unreached,
        "results": results,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
