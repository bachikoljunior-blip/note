"""Role-local external-validation analysis for LAJ-Gherkin repeated GPT-4o Mini runs.

Public source is pinned to inflaton/LAJ-Gherkin commit
  ee8649376b51f9e4c5b955369a88c4a5a6bba5da
No O, other-worker, downstream, or legacy state is read.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import statsmodels.api as sm

SHA = "ee8649376b51f9e4c5b955369a88c4a5a6bba5da"
ROOT = f"https://raw.githubusercontent.com/inflaton/LAJ-Gherkin/{SHA}"
GT_URL = f"{ROOT}/dataset/jira_coverage_ground_truth.csv"
RUN_URL = f"{ROOT}/results/r{{run}}/jira_coverage_gpt-4o-mini.csv"
# Token/retry-derived published summary at the same pinned commit.
ADJUSTED_COST_PER_1K_EVALS_USD = 1.0080101800710406


def load():
    gt = pd.read_csv(GT_URL).sort_values("jira_id").reset_index(drop=True)
    runs = []
    for r in range(1, 6):
        df = pd.read_csv(RUN_URL.format(run=r)).sort_values("jira_id").reset_index(drop=True)
        assert np.array_equal(df["jira_id"].to_numpy(), gt["jira_id"].to_numpy())
        runs.append(df)
    return gt, runs


def paired_bootstrap_diff(err_a, err_b, seed=0, draws=20000):
    rng = np.random.default_rng(seed)
    n = len(err_a)
    idx = rng.integers(0, n, size=(draws, n))
    d = (err_a[idx] - err_b[idx]).mean(axis=1)
    return float(d.mean()), tuple(np.quantile(d, [0.025, 0.975]))


def main():
    gt_df, run_dfs = load()
    y = gt_df["coverage_percentage"].to_numpy(dtype=float)
    R = np.vstack([d["coverage_percentage"].to_numpy(dtype=float) for d in run_dfs])

    print("Uniform K curves (first K repeats; arithmetic mean):")
    for k in range(1, 6):
        pred = R[:k].mean(axis=0)
        err = np.abs(pred - y)
        range_k = np.ptp(R[:k], axis=0)
        cost = ADJUSTED_COST_PER_1K_EVALS_USD * (100 * k) / 1000
        print({
            "K": k,
            "MAE": float(err.mean()),
            "RMSE": float(np.sqrt(np.mean((pred-y)**2))),
            "mean_range": float(range_k.mean()),
            "all_same_pct": float(np.mean(range_k == 0) * 100),
            "eval_calls": 100*k,
            "adjusted_cost_usd_approx": cost,
        })

    pred5 = R.mean(axis=0)
    err5 = np.abs(pred5-y)
    range5 = np.ptp(R, axis=0)
    d12 = np.abs(R[0]-R[1])
    stable = range5 == 0
    print("Five-run stability:", {
        "stable_items": int(stable.sum()),
        "stable_wrong_items": int(np.sum(stable & (err5 > 0))),
        "stable_error_gt5_items": int(np.sum(stable & (err5 > 5))),
        "mean_error_stable": float(err5[stable].mean()),
        "mean_error_unstable": float(err5[~stable].mean()),
        "spearman_range_vs_error": tuple(map(float, spearmanr(range5, err5))),
    })
    print("Early r1/r2 disagreement:", {
        "disagree_items": int(np.sum(d12 > 0)),
        "mean_final_error_agree": float(err5[d12 == 0].mean()),
        "mean_final_error_disagree": float(err5[d12 > 0].mean()),
        "spearman_absdiff_vs_error": tuple(map(float, spearmanr(d12, err5))),
    })

    # Control for the expert score level available in this dataset. This is an
    # analysis-only covariate, not a deployable routing feature.
    X = pd.DataFrame({
        "range5": range5,
        "gt80": (y == 80).astype(int),
        "gt70": (y == 70).astype(int),
    })
    fit = sm.OLS(err5, sm.add_constant(X)).fit(cov_type="HC3")
    print("HC3 OLS coefficients:", fit.params.to_dict())
    print("HC3 OLS pvalues:", fit.pvalues.to_dict())

    # Simple disagreement-triggered policy: buy r3..r5 only if r1 != r2;
    # use a median for the five-repeat branch to limit one-off score movement.
    pred_adapt = (R[0] + R[1]) / 2
    mask = d12 > 0
    pred_adapt[mask] = np.median(R[:, mask], axis=0)
    calls = 200 + 3 * int(mask.sum())
    err_adapt = np.abs(pred_adapt-y)
    err_k2 = np.abs(R[:2].mean(axis=0)-y)
    err_k1 = np.abs(R[0]-y)
    print("Adaptive repeat policy:", {
        "calls": calls,
        "adjusted_cost_usd_approx": ADJUSTED_COST_PER_1K_EVALS_USD*calls/1000,
        "MAE": float(err_adapt.mean()),
        "K2_MAE": float(err_k2.mean()),
        "K1_MAE": float(err_k1.mean()),
        "paired_bootstrap_adapt_minus_K2": paired_bootstrap_diff(err_adapt, err_k2),
        "paired_bootstrap_adapt_minus_K1": paired_bootstrap_diff(err_adapt, err_k1, seed=1),
    })


if __name__ == "__main__":
    main()
