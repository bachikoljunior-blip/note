#!/usr/bin/env python3
"""push して、実在する SHA だけを返す。

## なぜ道具にしたか（段4）

2026-08-08、報告に「Simple 4ba6d5c」と書いた。**存在しない番号だった**（実際は 9ed1ef2）。
`git push ... | tail -1` で受けていて、**SHA を一度も見ていなかった。**
中身は正しく届いていたので、読み直すまで誰も気づけない形だった。

最初は終了前フックに質問を足した（段2）。**同じ日に段2は3回破られている。**
質問は答えを自分で書けるので、思い出した番号でも通ってしまう。

だから経路を変える。**push と読み直しを1つの操作にして、
戻り値として origin から読んだ SHA しか返さない。**
思い出した番号を報告に書く余地を、道具の側から消す。

    python tools/gitsafe.py push <branch> [--also-main]
    python tools/gitsafe.py sha <branch>

`push` は成功すると、origin から読み直した SHA と件名を印字する。
**印字されたものだけを報告に写すこと。** それ以外の番号は、どこから来たものであれ書かない。
"""
from __future__ import annotations

import subprocess
import sys


class GitError(RuntimeError):
    pass


def run(args: list[str], cwd: str | None = None) -> str:
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise GitError(f"git {' '.join(args)} が失敗: {proc.stderr.strip()[:300]}")
    return proc.stdout.strip()


def remote_sha(branch: str, *, cwd: str | None = None) -> tuple[str, str]:
    """origin から読み直した (sha, 件名) を返す。ローカルの値は使わない。"""
    run(["fetch", "origin", branch], cwd=cwd)
    sha = run(["log", f"origin/{branch}", "-1", "--format=%h"], cwd=cwd)
    subject = run(["log", f"origin/{branch}", "-1", "--format=%s"], cwd=cwd)
    if not sha:
        raise GitError(f"origin/{branch} の SHA を読めなかった")
    return sha, subject


def push(branch: str, *, also_main: bool = False, cwd: str | None = None) -> dict:
    """push して、**origin から読み直した** SHA を返す。

    push の出力は戻り値に使わない。成功したと書いてあることと、
    実際にその内容が origin に在ることは別だから。
    """
    run(["push", "-u", "origin", branch], cwd=cwd)
    sha, subject = remote_sha(branch, cwd=cwd)
    result = {"branch": branch, "sha": sha, "subject": subject}

    if also_main:
        run(["push", "origin", f"{branch}:main"], cwd=cwd)
        main_sha, main_subject = remote_sha("main", cwd=cwd)
        result["main_sha"] = main_sha
        result["main_subject"] = main_subject
        if main_sha != sha:
            result["warning"] = (
                f"main({main_sha}) と {branch}({sha}) が違う。"
                "誰かが先に push した可能性がある。報告する前に確かめること")
    return result


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    mode, branch = sys.argv[1], sys.argv[2]
    also_main = "--also-main" in sys.argv

    try:
        if mode == "sha":
            sha, subject = remote_sha(branch)
            print(f"{sha}  {subject}")
        elif mode == "push":
            r = push(branch, also_main=also_main)
            print(f"{r['branch']:<44} {r['sha']}  {r['subject']}")
            if "main_sha" in r:
                print(f"{'main':<44} {r['main_sha']}  {r['main_subject']}")
            if "warning" in r:
                print("警告: " + r["warning"])
            print()
            print("↑ origin から読み直した値です。報告にはこれだけを写すこと。")
        else:
            print(f"知らない指示: {mode}")
            return 2
    except GitError as exc:
        print(f"失敗: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
