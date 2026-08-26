#!/usr/bin/env python3
"""Predeclared external-validation protocol for multi-agent judge routing.

This script intentionally pins the public corpus by commit and never reads O,
other clean workers, downstream state, or legacy research.

Important scope note:
- This corpus has two prompt variants per judge, not same-prompt repeated calls.
- Therefore the matched extra-call control is a *same-model prompt intervention*,
  not a same-judge stochastic repeat.
- The heterogeneous arm uses a different judge under the same v1 prompt.
- All model/rule selection happens on the training split only.
"""
from __future__ import annotations

import hashlib
import io
import itertools
import urllib.request
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, cohen_kappa_score

REPO = "noureddinekhender-alt/judge-human-agreement"
COMMIT = "63b98c57426742d19169af0dc7ec9f888f928d8c"
BASE = f"https://raw.githubusercontent.com/{REPO}/{COMMIT}"
ERROR_THRESHOLD = 2.5
EXTRA_RATE = 0.30
BOOTSTRAP_SEED = 20260826
N_BOOT = 5000


def read_csv(path: str) -> pd.DataFrame:
    with urllib.request.urlopen(f"{BASE}/{path}") as r:
        return pd.read_csv(io.BytesIO(r.read()))


def stable_u01(item_id: str) -> float:
    h = hashlib.sha256(("multi-agent-second-corpus-v1|" + item_id).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2**64


def binary_verdict(v: object) -> float:
    if pd.isna(v):
        return np.nan
    return float(str(v).upper() != "PASS")


def paired_bootstrap(a: np.ndarray, b: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """Return mean accuracy difference a-b and paired percentile interval."""
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    n = len(y)
    observed = accuracy_score(y, a) - accuracy_score(y, b)
    draws = []
    for _ in range(N_BOOT):
        idx = rng.integers(0, n, n)
        draws.append(accuracy_score(y[idx], a[idx]) - accuracy_score(y[idx], b[idx]))
    lo, hi = np.quantile(draws, [0.025, 0.975])
    return float(observed), float(lo), float(hi)


@dataclass(frozen=True)
class Rule:
    kind: str
    value: str | float

    def mask(self, base: pd.DataFrame) -> pd.Series:
        if self.kind == "confidence_lt":
            return base["confidence"].fillna(-1.0) < float(self.value)
        if self.kind == "verdict_is":
            return base["verdict"].astype(str).str.upper() == str(self.value)
        raise ValueError(self)


def candidate_rules() -> list[Rule]:
    return [
        Rule("confidence_lt", 0.50),
        Rule("confidence_lt", 0.75),
        Rule("confidence_lt", 0.90),
        Rule("verdict_is", "PASS"),
        Rule("verdict_is", "REJECT"),
        Rule("verdict_is", "MAJOR_ERROR"),
    ]


def cap_mask(mask: pd.Series, item_ids: pd.Series, rate: float = EXTRA_RATE) -> pd.Series:
    """Keep at most rate*n routed items deterministically; no test labels used."""
    n_cap = int(np.floor(rate * len(mask)))
    candidates = pd.DataFrame({"idx": mask.index, "item_id": item_ids, "on": mask.values})
    candidates = candidates[candidates.on].copy()
    candidates["tie"] = candidates.item_id.map(stable_u01)
    keep = set(candidates.sort_values(["tie", "item_id"]).head(n_cap)["idx"])
    return pd.Series([i in keep for i in mask.index], index=mask.index)


def score_arm(base_pred: np.ndarray, extra_pred: np.ndarray, route: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    pred = base_pred.copy()
    pred[route] = extra_pred[route]
    return accuracy_score(y, pred), cohen_kappa_score(y, pred)


def main() -> None:
    audit = read_csv("data/audit/audited_items.csv").set_index("item_id")
    calls = read_csv("data/judges/judge_calls.csv")

    # Human target exactly matches the public reproduction artifact.
    panel = audit["human_mean_factuality"].astype(float)
    human_err = (panel <= ERROR_THRESHOLD).astype(int)

    v1 = calls[calls.prompt_variant.eq("v1_original")].dropna(subset=["verdict"]).copy()
    v2 = calls[calls.prompt_variant.eq("v2_rubric")].dropna(subset=["verdict"]).copy()
    judges = sorted(set(v1.critic) & set(v2.critic))

    counts = v1.groupby("item_id")["critic"].nunique()
    common = sorted(counts[counts == len(judges)].index)
    common = [i for i in common if i in human_err.index]

    # Deterministic 100/remaining split fixed before looking at labels or judge outcomes.
    ordered = sorted(common, key=lambda x: (stable_u01(x), x))
    train_ids, test_ids = set(ordered[:100]), set(ordered[100:])

    def frame(prompt_df: pd.DataFrame, judge: str, ids: set[str]) -> pd.DataFrame:
        z = prompt_df[(prompt_df.critic == judge) & (prompt_df.item_id.isin(ids))].copy()
        z = z.drop_duplicates("item_id", keep="first").set_index("item_id")
        return z

    # Training-only selection. Optimize heterogeneous routing gain over base at fixed <=30% extra calls.
    best = None
    for base_judge, hetero_judge in itertools.permutations(judges, 2):
        b = frame(v1, base_judge, train_ids)
        h = frame(v1, hetero_judge, train_ids)
        s = frame(v2, base_judge, train_ids)  # same-model prompt-intervention control
        ids = sorted(set(b.index) & set(h.index) & set(s.index))
        if len(ids) < 90:
            continue
        b, h, s = b.loc[ids], h.loc[ids], s.loc[ids]
        y = human_err.loc[ids].to_numpy(int)
        bp = b.verdict.map(binary_verdict).to_numpy(int)
        hp = h.verdict.map(binary_verdict).to_numpy(int)
        sp = s.verdict.map(binary_verdict).to_numpy(int)
        for rule in candidate_rules():
            raw = rule.mask(b)
            routed = cap_mask(raw, pd.Series(ids, index=b.index)).to_numpy(bool)
            if routed.sum() == 0:
                continue
            acc_h, _ = score_arm(bp, hp, routed, y)
            acc_s, _ = score_arm(bp, sp, routed, y)
            base_acc = accuracy_score(y, bp)
            key = (acc_h - base_acc, acc_h - acc_s, -routed.sum(), base_judge, hetero_judge, rule.kind, str(rule.value))
            if best is None or key > best[0]:
                best = (key, base_judge, hetero_judge, rule)

    if best is None:
        raise RuntimeError("No complete train configuration")
    _, base_judge, hetero_judge, rule = best

    # Untouched test: freeze selected base, hetero judge, and rule before evaluation.
    b = frame(v1, base_judge, test_ids)
    h = frame(v1, hetero_judge, test_ids)
    s = frame(v2, base_judge, test_ids)
    ids = sorted(set(b.index) & set(h.index) & set(s.index))
    b, h, s = b.loc[ids], h.loc[ids], s.loc[ids]
    y = human_err.loc[ids].to_numpy(int)
    bp = b.verdict.map(binary_verdict).to_numpy(int)
    hp = h.verdict.map(binary_verdict).to_numpy(int)
    sp = s.verdict.map(binary_verdict).to_numpy(int)
    route = cap_mask(rule.mask(b), pd.Series(ids, index=b.index)).to_numpy(bool)

    hetero = bp.copy(); hetero[route] = hp[route]
    same_model_prompt = bp.copy(); same_model_prompt[route] = sp[route]

    print(f"pinned_commit={COMMIT}")
    print(f"common_items={len(common)} train={len(train_ids)} test={len(ids)}")
    print(f"base={base_judge} hetero={hetero_judge} rule={rule.kind}:{rule.value} routed={route.sum()}/{len(ids)}")
    for name, pred in [("base_v1", bp), ("same_model_v2", same_model_prompt), ("hetero_v1", hetero)]:
        print(name, "accuracy", accuracy_score(y, pred), "kappa", cohen_kappa_score(y, pred))
    d, lo, hi = paired_bootstrap(hetero, same_model_prompt, y)
    print("hetero_minus_same_model_prompt_accuracy", d, "95pct", lo, hi)
    print("scope: same_model_v2 is a prompt intervention, NOT a stochastic repeat; match is by extra call count, not dollars")


if __name__ == "__main__":
    main()
