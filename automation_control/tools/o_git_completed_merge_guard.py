"""Clear proven completed local Git merge metadata, never an unfinished merge.

This workspace can expose old MERGE_HEAD again across tool calls. Run this
guard and the dependent Git command in the same Python process. No worktree,
index, branch or remote content is discarded by the guard.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess


class IncompleteMerge(RuntimeError):
    pass


def completed_merge_guard(root: Path) -> dict:
    root = root.resolve()

    def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(['git', '-C', str(root), *args], text=True,
                              capture_output=True, check=check)

    head = git('rev-parse', '--verify', 'HEAD').stdout.strip()
    merge_path = Path(git('rev-parse', '--git-path', 'MERGE_HEAD').stdout.strip())
    if not merge_path.is_absolute():
        merge_path = root / merge_path
    if not merge_path.exists():
        return {'action': 'no_merge_metadata', 'head': head}
    merge_heads = merge_path.read_text().splitlines()
    if not merge_heads or any(len(h) not in (40, 64) or any(c not in '0123456789abcdef' for c in h) for h in merge_heads):
        raise IncompleteMerge('malformed MERGE_HEAD; preserve and inspect')
    if git('ls-files', '--unmerged').stdout.strip():
        raise IncompleteMerge('unresolved index entries; preserve merge')
    for args in [('diff', '--quiet'), ('diff', '--cached', '--quiet')]:
        if git(*args, check=False).returncode:
            raise IncompleteMerge('tracked worktree or index changes; preserve merge')
    for parent in merge_heads:
        if git('merge-base', '--is-ancestor', parent, head, check=False).returncode:
            raise IncompleteMerge('MERGE_HEAD is not an ancestor of HEAD; preserve merge')
    git('merge', '--quit')
    if merge_path.exists() or git('rev-parse', 'HEAD').stdout.strip() != head:
        raise IncompleteMerge('cleanup readback mismatch; do not continue')
    if git('diff', '--quiet', check=False).returncode or git('diff', '--cached', '--quiet', check=False).returncode:
        raise IncompleteMerge('cleanup changed tracked data; do not continue')
    return {'action': 'cleared_completed_merge_metadata', 'head': head,
            'completed_merge_heads': merge_heads, 'tracked_data_unchanged': True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('git_args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    result = completed_merge_guard(args.root)
    print(json.dumps(result), flush=True)
    command = args.git_args
    if command[:1] == ['--']:
        command = command[1:]
    if command:
        subprocess.run(['git', '-C', str(args.root.resolve()), *command], check=True)


if __name__ == '__main__':
    main()
