from __future__ import annotations

import itertools
import json
import math
import random

import numpy as np
from scipy.stats import beta

PREMISES = {
    "a_P": ("fact", "P"),
    "b_P_implies_R": ("rule", "P", "R"),
    "c_Q": ("fact", "Q"),
    "d_Q_implies_R": ("rule", "Q", "R"),
    "e_P_implies_Q": ("rule", "P", "Q"),
}
NAMES = list(PREMISES)
N = len(NAMES)
TARGET = "R"
EXACT = np.array([17 / 60, 1 / 5, 1 / 5, 17 / 60, 1 / 30], dtype=float)
BUDGETS = (40, 80, 160, 320, 640)
REPLICATES = 1000
ALPHA = 0.05


def derives(selected: set[str]) -> bool:
    facts: set[str] = set()
    rules: list[tuple[str, str]] = []
    for name in selected:
        item = PREMISES[name]
        if item[0] == "fact":
            facts.add(item[1])
        else:
            rules.append((item[1], item[2]))
    changed = True
    while changed:
        changed = False
        for antecedent, consequent in rules:
            if antecedent in facts and consequent not in facts:
                facts.add(consequent)
                changed = True
    return TARGET in facts


def utility(coalition: frozenset[int]) -> int:
    return int(derives({NAMES[i] for i in coalition}))


def coalition_tables() -> dict[tuple[int, int], tuple[frozenset[int], ...]]:
    out: dict[tuple[int, int], tuple[frozenset[int], ...]] = {}
    for i in range(N):
        others = [j for j in range(N) if j != i]
        for k in range(N):
            out[(i, k)] = tuple(frozenset(c) for c in itertools.combinations(others, k))
    return out


COALITIONS = coalition_tables()


def cp_tables(max_m: int) -> tuple[list[np.ndarray], list[np.ndarray]]:
    strata = N * N
    los: list[np.ndarray] = [np.array([0.0])]
    his: list[np.ndarray] = [np.array([1.0])]
    for m in range(1, max_m + 1):
        alpha_m = ALPHA * 6.0 / (math.pi**2 * strata * m * m)
        lo = np.empty(m + 1)
        hi = np.empty(m + 1)
        for s in range(m + 1):
            lo[s] = 0.0 if s == 0 else beta.ppf(alpha_m / 2.0, s, m - s + 1)
            hi[s] = 1.0 if s == m else beta.ppf(1.0 - alpha_m / 2.0, s + 1, m - s)
        los.append(lo)
        his.append(hi)
    return los, his


CP_LO, CP_HI = cp_tables(max(BUDGETS))


def exact_from_cache(cache: dict[frozenset[int], int]) -> np.ndarray:
    if len(cache) != 2**N:
        raise ValueError("exact completion requires every coalition utility")
    sums = np.zeros(N)
    for order in itertools.permutations(range(N)):
        coalition = frozenset()
        for i in order:
            nxt = frozenset(set(coalition) | {i})
            sums[i] += cache[nxt] - cache[coalition]
            coalition = nxt
    return sums / math.factorial(N)


def adaptive_run(seed: int, budget: int) -> tuple[np.ndarray, np.ndarray, int]:
    """Reproduce the existing adaptive allocator, but make oracle reuse explicit.

    The raw estimate is unchanged. The cache-aware estimate switches to exact
    Shapley only when all 2^N characteristic-function values have already been
    paid for and cached. No extra oracle call is charged at that switch.
    """
    rng = random.Random(seed)
    m = np.zeros((N, N), dtype=int)
    s = np.zeros((N, N), dtype=int)
    cache: dict[frozenset[int], int] = {}
    observations = 0

    def eval_cached(coalition: frozenset[int]) -> int:
        if coalition not in cache:
            cache[coalition] = utility(coalition)
        return cache[coalition]

    def sample(i: int, k: int) -> None:
        nonlocal observations
        coalition = rng.choice(COALITIONS[(i, k)])
        with_i = frozenset(set(coalition) | {i})
        y = eval_cached(with_i) - eval_cached(coalition)
        m[i, k] += 1
        s[i, k] += y
        observations += 1

    pairs = [(i, k) for i in range(N) for k in range(N)]
    rng.shuffle(pairs)
    for pair in pairs:
        sample(*pair)

    while observations < budget:
        width = np.empty((N, N))
        for i in range(N):
            for k in range(N):
                mm = int(m[i, k])
                ss = int(s[i, k])
                width[i, k] = CP_HI[mm][ss] - CP_LO[mm][ss]
        player_width = width.mean(axis=1)
        max_pw = float(player_width.max())
        players = [i for i in range(N) if abs(player_width[i] - max_pw) < 1e-15]
        i = rng.choice(players)
        max_sw = float(width[i].max())
        strata = [k for k in range(N) if abs(width[i, k] - max_sw) < 1e-15]
        sample(i, rng.choice(strata))

    raw = np.array([(s[i] / m[i]).mean() for i in range(N)])
    cache_aware = exact_from_cache(cache) if len(cache) == 2**N else raw.copy()
    return raw, cache_aware, len(cache)


def summarize() -> dict:
    rows = []
    for budget in BUDGETS:
        raw_zero: list[float] = []
        cache_zero: list[float] = []
        raw_rmse: list[float] = []
        cache_rmse: list[float] = []
        unique: list[int] = []
        for seed in range(REPLICATES):
            raw, cache_aware, unique_count = adaptive_run(seed, budget)
            raw_zero.append(float(raw[4] == 0.0))
            cache_zero.append(float(cache_aware[4] == 0.0))
            raw_rmse.append(float(np.sqrt(np.mean((raw - EXACT) ** 2))))
            cache_rmse.append(float(np.sqrt(np.mean((cache_aware - EXACT) ** 2))))
            unique.append(unique_count)
        u = np.array(unique)
        rows.append({
            "marginal_observations": budget,
            "cache_complete_rate": float(np.mean(u == 2**N)),
            "median_unique_coalitions": float(np.median(u)),
            "p05_unique_coalitions": float(np.quantile(u, 0.05)),
            "p95_unique_coalitions": float(np.quantile(u, 0.95)),
            "raw_bridge_zero_rate": float(np.mean(raw_zero)),
            "cache_completion_bridge_zero_rate": float(np.mean(cache_zero)),
            "raw_median_rmse": float(np.median(raw_rmse)),
            "cache_completion_median_rmse": float(np.median(cache_rmse)),
            "cache_completion_p95_rmse": float(np.quantile(cache_rmse, 0.95)),
        })
    return {
        "schema_version": "SupportFamilyCacheExactCompletionV0",
        "replicates": REPLICATES,
        "seeds": "integers 0 through 999",
        "players": NAMES,
        "exact_shapley": dict(zip(NAMES, EXACT.tolist())),
        "cache_model": {
            "oracle_key": "coalition frozenset",
            "cache_reuse": "all repeated coalition evaluations are reused",
            "max_unique_coalitions": 2**N,
            "exact_completion_rule": "if all 2^N coalition utilities are cached, compute exact Shapley without another oracle call",
        },
        "results": rows,
        "scope": "five-player engineering calibration only; larger candidate universes need a remaining-exact-cost gate",
    }


if __name__ == "__main__":
    print(json.dumps(summarize(), indent=2, sort_keys=True))
