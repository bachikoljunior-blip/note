#!/usr/bin/env python3
"""書いたら読み直す。無いと言うなら2つ目の観測を当てる。

2026-08-08 に同じ形の失敗を5回踏んだので、点で直すのをやめて共通化した。

    価格を 3800 と書いて、読み直したら $38 だった（通貨がUSDのまま）
    チャンネルのリンクが channels.list に無いので「無い」と言った → 実在した
    毎時自動実行が list_triggers に出ないので「無い」と言った → 実在した
    トリガーを「作った」と書いて読み直さなかった → 読んだら5本目が見つかった
    送客を「直した」と書いた → 踏めるか確かめていなかった

共通しているのは2つだけ。

  A. 書いた結果を読み直していない。応答の success=true を結果だと思っている
  B. 1つの観測で「無い」と結論している

このモジュールは、その2つを**手続きとして強制**する。終了前のフックは最後にしか
効かないが、こちらは書いた瞬間・言い切る瞬間に効く。

使い方:

    from tools.verified import write_and_verify, absent

    write_and_verify(
        label="Gumroadの価格",
        write=lambda: api_put(pid, price="3800"),
        read=lambda: api_get(pid)["formatted_price"],
        expect="¥3,800",
    )

    absent("チャンネルの外部リンク", [
        ("channels.list", lambda: not api_channels().get("links")),
        ("公開ページHTML", lambda: "http" not in fetch_channel_page()),
    ])
"""
from __future__ import annotations

import time
from typing import Any, Callable, Iterable


class VerificationError(AssertionError):
    """書いた結果が読み直しと食い違った。"""


class InsufficientObservations(AssertionError):
    """不在を1つの観測だけで主張しようとした。"""


def write_and_verify(
    *,
    label: str,
    write: Callable[[], Any],
    read: Callable[[], Any],
    expect: Any = None,
    matches: Callable[[Any], bool] | None = None,
    attempts: int = 5,
    delay_seconds: float = 3.0,
) -> Any:
    """書いて、読み直して、一致するまで確かめる。

    書き込み直後の読み取りは古い値を返すことがある（2026-08-08、YouTube と
    Gumroad の両方で実測）。だから1回の読みで失敗と決めず、`attempts` 回試す。
    それでも一致しなければ **例外で止める**。黙って進むと、直っていないものを
    直したと書くことになる。

    `expect` か `matches` のどちらかを必ず渡すこと。両方省略すると、
    このヘルパを通す意味が無いので拒否する。
    """
    if expect is None and matches is None:
        raise ValueError(f"{label}: expect か matches のどちらかが要る（読み直しの基準が無い）")

    write_result = write()

    check = matches if matches is not None else (lambda value: value == expect)
    seen: list[Any] = []
    for attempt in range(1, attempts + 1):
        observed = read()
        seen.append(observed)
        if check(observed):
            return write_result
        if attempt < attempts:
            time.sleep(delay_seconds)

    raise VerificationError(
        f"{label}: 書いたが、読み直しで確認できなかった。\n"
        f"  期待: {expect if matches is None else '(matches 関数)'}\n"
        f"  実際: {seen}\n"
        f"  書き込みの応答: {write_result!r}\n"
        "  応答が success を返しても、値が変わっていないことがある（黙って無視される型）。"
    )


def absent(
    label: str,
    observations: Iterable[tuple[str, Callable[[], bool]]],
    *,
    required: int = 2,
) -> bool:
    """「無い」と言ってよいかを判定する。独立した観測が `required` 個要る。

    各観測は (名前, 「無ければ True を返す関数」) の組。
    観測が足りなければ **例外で止める**。1つのAPI応答は、その機能の全体ではない。
    """
    checks = list(observations)
    if len(checks) < required:
        raise InsufficientObservations(
            f"{label}: 不在の主張に観測が {len(checks)} 個しかない（{required} 個要る）。\n"
            "  1つのAPI応答は、その機能の全体ではない。別の経路からもう一度当てること。\n"
            f"  いまある観測: {[name for name, _ in checks]}"
        )

    results = [(name, bool(fn())) for name, fn in checks]
    agree_absent = [name for name, missing in results if missing]

    if len(agree_absent) == len(results):
        return True
    found_by = [name for name, missing in results if not missing]
    raise VerificationError(
        f"{label}: 「無い」と言おうとしたが、{found_by} では見つかった。\n"
        f"  観測結果: {results}\n"
        "  1つの観測に無いことは、存在しないことではない。"
    )
