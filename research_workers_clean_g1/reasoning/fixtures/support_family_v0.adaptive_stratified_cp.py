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
TARGET = "R"
EXACT = np.array([17 / 60, 1 / 5, 1 / 5, 17 / 60, 1 / 30], dtype=float)
BUDGETS = (40, 80, 160, 320, 640)  # marginal-observation budgets
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


def marginal_tables() -> dict[tuple[int, int], tuple[int, ...]]:
    out: dict[tuple[int, int], tuple[int, ...]] = {}
    for i, name in enumerate(NAMES):
        others = [x for x in NAMES if x != name]
        for k in range(len(NAMES)):
            vals: list[int] = []
            for combo in itertools.combinations(others, k):
                coalition = set(combo)
                vals.append(
                    int(derives(coalition | {name})) - int(derives(coalition))
                )
            out[(i, k)] = tuple(vals)
    return out


MARGINALS = marginal_tables()


def cp_tables(max_m: int) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Time-uniform Clopper-Pearson tables via alpha spending.

    There are 25 player/coalition-size strata. At sample count m for a stratum,
    assign alpha_m = alpha * 6 / (pi^2 * 25 * m^2). Union-bounding over all
    strata and all positive m gives total failure probability <= alpha.
    """
    strata = len(NAMES) * len(NAMES)
    los: list[np.ndarray] = [np.array([0.0])]
    his: list[np.ndarray] = [np.array([1.0])]
    for m in range(1, max_m + 1):
        alpha_m = ALPHA * 6.0 / (math.pi**2 * strata * m * m)
        lo = np.empty(m + 1)
        hi = np.empty(m + 1)
        for s in range(m + 1):
            lo[s] = 0.0 if s == 0 else beta.ppf(alpha_m / 2.0, s, m - s + 1)
            hi[s] = (
                1.0
                if s == m
                else beta.ppf(1.0 - alpha_m / 2.0, s + 1, m - s)
            )
        los.append(lo)
        his.append(hi)
    return los, his


CP_LO, CP_HI = cp_tables(max(BUDGETS))


def iid_permutation_estimate(seed: int, permutations: int) -> np.ndarray:
    rng = random.Random(seed)
    sums = np.zeros(len(NAMES))
    for _ in range(permutations):
        order = list(range(len(NAMES)))
        rng.shuffle(order)
        coalition: set[int] = set()
        for i in order:
            before = int(derives({NAMES[j] for j in coalition}))
            coalition.add(i)
            after = int(derives({NAMES[j] for j in coalition}))
            sums[i] += after - before
    return sums / permutations


def adaptive_snapshots(seed: int) -> dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Minimax adaptive allocation over player/coalition-size strata.

    Warm-start with one uniformly sampled marginal from every stratum (25
    observations). Thereafter choose the player with the widest aggregate
    time-uniform interval and, within that player, the stratum with the widest
    interval. Ties are randomized by the deterministic seed. Sampling within a
    selected stratum is uniform with replacement.
    """
    rng = random.Random(seed)
    n = len(NAMES)
    m = np.zeros((n, n), dtype=int)
    s = np.zeros((n, n), dtype=int)
    q = 0
    snapshots: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}

    def sample(i: int, k: int) -> None:
        nonlocal q
        values = MARGINALS[(i, k)]
        y = values[rng.randrange(len(values))]
        m[i, k] += 1
        s[i, k] += y
        q += 1

    pairs = [(i, k) for i in range(n) for k in range(n)]
    rng.shuffle(pairs)
    for i, k in pairs:
        sample(i, k)

    while q < max(BUDGETS):
        low = np.zeros((n, n))
        high = np.ones((n, n))
        width = np.ones((n, n))
        for i in range(n):
            for k in range(n):
                mm = int(m[i, k])
                ss = int(s[i, k])
                low[i, k] = CP_LO[mm][ss]
                high[i, k] = CP_HI[mm][ss]
                width[i, k] = high[i, k] - low[i, k]

        player_width = width.mean(axis=1)
        max_pw = float(player_width.max())
        players = [i for i in range(n) if abs(player_width[i] - max_pw) < 1e-15]
        i = players[rng.randrange(len(players))]
        max_sw = float(width[i].max())
        strata = [k for k in range(n) if abs(width[i, k] - max_sw) < 1e-15]
        k = strata[rng.randrange(len(strata))]
        sample(i, k)

        if q in BUDGETS:
            estimate = np.array([(s[i] / m[i]).mean() for i in range(n)])
            phi_low = np.array(
                [
                    np.mean([CP_LO[int(m[i, k])][int(s[i, k])] for k in range(n)])
                    for i in range(n)
                ]
            )
            phi_high = np.array(
                [
                    np.mean([CP_HI[int(m[i, k])][int(s[i, k])] for k in range(n)])
                    for i in range(n)
                ]
            )
            snapshots[q] = (estimate, phi_low, phi_high)
    return snapshots


def summarize() -> dict:
    rows: dict[int, dict[str, list[float]]] = {
        b: {
            "adaptive_rmse": [],
            "adaptive_max_abs": [],
            "adaptive_bridge_zero": [],
            "adaptive_simultaneous_coverage": [],
            "adaptive_bridge_upper": [],
            "adaptive_max_player_interval_width": [],
            "iid_rmse": [],
            "iid_max_abs": [],
            "iid_bridge_zero": [],
        }
        for b in BUDGETS
    }
    for seed in range(REPLICATES):
        snaps = adaptive_snapshots(seed)
        for budget in BUDGETS:
            estimate, low, high = snaps[budget]
            error = estimate - EXACT
            r = rows[budget]
            r["adaptive_rmse"].append(float(np.sqrt(np.mean(error * error))))
            r["adaptive_max_abs"].append(float(np.max(np.abs(error))))
            r["adaptive_bridge_zero"].append(float(estimate[4] == 0.0))
            r["adaptive_simultaneous_coverage"].append(
                float(np.all((EXACT >= low) & (EXACT <= high)))
            )
            r["adaptive_bridge_upper"].append(float(high[4]))
            r["adaptive_max_player_interval_width"].append(float(np.max(high - low)))

            iid = iid_permutation_estimate(seed, budget // len(NAMES))
            iid_error = iid - EXACT
            r["iid_rmse"].append(float(np.sqrt(np.mean(iid_error * iid_error))))
            r["iid_max_abs"].append(float(np.max(np.abs(iid_error))))
            r["iid_bridge_zero"].append(float(iid[4] == 0.0))

    results = []
    for budget in BUDGETS:
        r = rows[budget]
        results.append(
            {
                "marginal_observations": budget,
                "iid_permutations": budget // len(NAMES),
                "adaptive": {
                    "median_rmse": float(np.median(r["adaptive_rmse"])),
                    "p95_rmse": float(np.quantile(r["adaptive_rmse"], 0.95)),
                    "median_max_abs_error": float(np.median(r["adaptive_max_abs"])),
                    "bridge_zero_estimate_rate": float(np.mean(r["adaptive_bridge_zero"])),
                    "simultaneous_interval_coverage": float(
                        np.mean(r["adaptive_simultaneous_coverage"])
                    ),
                    "median_bridge_upper_bound": float(
                        np.median(r["adaptive_bridge_upper"])
                    ),
                    "median_max_player_interval_width": float(
                        np.median(r["adaptive_max_player_interval_width"])
                    ),
                },
                "iid_permutation": {
                    "median_rmse": float(np.median(r["iid_rmse"])),
                    "p95_rmse": float(np.quantile(r["iid_rmse"], 0.95)),
                    "median_max_abs_error": float(np.median(r["iid_max_abs"])),
                    "bridge_zero_estimate_rate": float(np.mean(r["iid_bridge_zero"])),
                },
            }
        )
    return {
        "schema_version": "AdaptiveStratifiedCPFixtureAnalysisV0",
        "replicates": REPLICATES,
        "seeds": "integers 0 through 999",
        "exact_shapley": dict(zip(NAMES, EXACT.tolist())),
        "results": results,
        "notes": [
            "Budgets are matched by player-level marginal observations: one iid permutation yields five marginal observations.",
            "The adaptive allocator reduces median aggregate RMSE at higher budgets but can miss the rare positive bridge more often in its point estimate; average-error optimization is therefore not a safe elimination rule.",
            "The alpha-spending Clopper-Pearson intervals are time-uniform by a union bound over 25 strata and all sample counts, but are intentionally conservative; their practical stopping efficiency must be judged separately from coverage.",
            "For this five-player fixture exact enumeration is cheap (32 coalition utility values suffice), so exact Shapley remains preferable. The adaptive result is only a calibration warning for larger candidate universes."
        ],
    }


if __name__ == "__main__":
    print(json.dumps(summarize(), indent=2, sort_keys=True))
