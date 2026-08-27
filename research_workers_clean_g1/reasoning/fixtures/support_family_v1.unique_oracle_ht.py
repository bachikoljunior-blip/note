from __future__ import annotations

import itertools
import json
import math
import random

import numpy as np

N = 8
SUPPORTS = [{0, 1}, {2, 3}, {4, 5}, {0, 2, 4, 6, 7}]
BUDGETS = (64, 96, 128, 160, 192, 224, 256)
REPLICATES = 1000
ALL_MASKS = tuple(range(1 << N))


def utility(mask: int) -> int:
    return int(any(all(mask & (1 << i) for i in support) for support in SUPPORTS))


V = tuple(utility(mask) for mask in ALL_MASKS)


def exact_shapley() -> np.ndarray:
    out = np.zeros(N)
    nf = math.factorial(N)
    for i in range(N):
        for s in ALL_MASKS:
            if s & (1 << i):
                continue
            k = s.bit_count()
            w = math.factorial(k) * math.factorial(N - k - 1) / nf
            out[i] += w * (V[s | (1 << i)] - V[s])
    return out


EXACT = exact_shapley()


def path_masks(perm: list[int]) -> tuple[int, ...]:
    masks = [0]
    mask = 0
    for i in perm:
        mask |= 1 << i
        masks.append(mask)
    return tuple(masks)


def estimate_permutations(perms: list[list[int]]) -> np.ndarray:
    sums = np.zeros(N)
    counts = np.zeros(N, dtype=int)
    for perm in perms:
        mask = 0
        for i in perm:
            nxt = mask | (1 << i)
            sums[i] += V[nxt] - V[mask]
            counts[i] += 1
            mask = nxt
    return sums / counts


def permutation_cache(seed: int, budget: int, antithetic: bool) -> dict:
    rng = random.Random(seed)
    cache: set[int] = set()
    accepted: list[list[int]] = []
    attempts = 0
    while len(cache) < budget and attempts < 100000:
        perm = list(range(N))
        rng.shuffle(perm)
        batch = [perm, list(reversed(perm))] if antithetic else [perm]
        needed = set()
        for p in batch:
            needed.update(path_masks(p))
        new_needed = needed - cache
        if len(cache) + len(new_needed) <= budget:
            cache.update(new_needed)
            accepted.extend(batch)
        attempts += 1
    if len(cache) == 1 << N:
        estimate = EXACT.copy()
    else:
        estimate = estimate_permutations(accepted)
    return {
        "estimate": estimate,
        "unique_oracle_calls": len(cache),
        "completed_permutations": len(accepted),
    }


def coalition_wor_ht(seed: int, budget: int) -> dict:
    """Uniformly sample B coalition values without replacement.

    A directed Shapley marginal edge (S, S union {i}) is observed iff both
    endpoint coalitions are sampled. Under simple random sampling of B
    coalitions from M=2^N, the inclusion probability of each distinct endpoint
    pair is B(B-1)/(M(M-1)). Horvitz-Thompson scaling therefore gives an
    unbiased point estimator for each Shapley value.
    """
    rng = random.Random(seed)
    observed = set(rng.sample(ALL_MASKS, budget))
    if budget == 1 << N:
        return {"estimate": EXACT.copy(), "unique_oracle_calls": budget}
    M = 1 << N
    pair_inclusion = budget * (budget - 1) / (M * (M - 1))
    estimate = np.zeros(N)
    nf = math.factorial(N)
    for i in range(N):
        total = 0.0
        for s in ALL_MASKS:
            if s & (1 << i):
                continue
            t = s | (1 << i)
            if s in observed and t in observed:
                k = s.bit_count()
                w = math.factorial(k) * math.factorial(N - k - 1) / nf
                total += w * (V[t] - V[s])
        estimate[i] = total / pair_inclusion
    return {"estimate": estimate, "unique_oracle_calls": budget}


def summarize() -> dict:
    methods = {
        "iid_permutation_cache": lambda seed, budget: permutation_cache(seed, budget, False),
        "reverse_antithetic_cache": lambda seed, budget: permutation_cache(seed, budget, True),
        "coalition_uniform_without_replacement_ht": coalition_wor_ht,
    }
    results: dict[str, dict[str, dict]] = {}
    for budget in BUDGETS:
        results[str(budget)] = {}
        for name, fn in methods.items():
            estimates = []
            unique_calls = []
            permutation_counts = []
            for seed in range(REPLICATES):
                row = fn(seed, budget)
                estimates.append(row["estimate"])
                unique_calls.append(row["unique_oracle_calls"])
                if "completed_permutations" in row:
                    permutation_counts.append(row["completed_permutations"])
            A = np.asarray(estimates)
            rmses = np.sqrt(np.mean((A - EXACT) ** 2, axis=1))
            rare = A[:, 6]
            results[str(budget)][name] = {
                "replicates": REPLICATES,
                "median_unique_oracle_calls": float(np.median(unique_calls)),
                "median_rmse": float(np.median(rmses)),
                "p95_rmse": float(np.quantile(rmses, 0.95)),
                "mean_vector": A.mean(axis=0).tolist(),
                "max_abs_mean_bias": float(np.max(np.abs(A.mean(axis=0) - EXACT))),
                "rare_player_true_value": float(EXACT[6]),
                "rare_player_zero_rate": float(np.mean(rare == 0.0)),
                "rare_player_mean_estimate": float(np.mean(rare)),
                "rare_player_median_estimate": float(np.median(rare)),
                "median_completed_permutations": (
                    float(np.median(permutation_counts)) if permutation_counts else None
                ),
            }
    return {
        "schema_version": "SupportFamilyUniqueOracleComparisonV0",
        "game": {
            "players": [f"p{i}" for i in range(N)],
            "minimal_supports": [sorted(s) for s in SUPPORTS],
            "coalition_count": 1 << N,
            "exact_shapley": EXACT.tolist(),
            "rare_players": [6, 7],
            "rare_value": float(EXACT[6]),
        },
        "matching": {
            "primitive": "unique coalition-utility oracle calls",
            "replicates": REPLICATES,
            "seed_range": "0..999",
            "budgets": list(BUDGETS),
        },
        "methods": {
            "iid_permutation_cache": "random permutations with replacement; coalition values cached",
            "reverse_antithetic_cache": "random permutation plus reverse; coalition values cached",
            "coalition_uniform_without_replacement_ht": "sample B coalition vertices uniformly without replacement; Horvitz-Thompson edge estimator",
        },
        "results": results,
        "scope": [
            "synthetic deterministic monotone support game only",
            "sampled zero is not safe demotion evidence",
            "aggregate RMSE and rare-positive detection are separate objectives",
            "exact completion occurs only at all 2^N coalition values under this fixed-budget comparison",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(summarize(), indent=2, sort_keys=True))
