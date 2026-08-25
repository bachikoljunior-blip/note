#!/usr/bin/env python3
"""Exact selection-layer corruption replay for Loreley Zstandard formal records.

This tool replays the *public deterministic finalist selection layer* only.
It does not reconstruct hidden candidate generation, archive insertion/eviction,
or parent-selection dynamics.

Noise model:
- false-admit q_fp: a clean-ineligible non-root finalist is treated as eligible.
- false-reject q_fn: a clean-eligible non-root finalist is treated as ineligible.
- root is fixed eligible by default because Loreley's published validation_eligible()
  treats root as an unconditional fallback. Use --corrupt-root for sensitivity only.

Because selection priority is deterministic, winner probabilities are computed
exactly (no Monte Carlo): P(i wins) = P(i eligible) * product(P(higher priority
candidate ineligible)).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

DEFAULT_GRID = (0.0, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50)


def validation_eligible(row: Mapping[str, Any]) -> tuple[bool, float]:
    """Match Loreley's public build_zstd_formal_records.py exactly."""
    if row.get("is_root"):
        return True, 1.0
    metrics = row.get("metrics") if isinstance(row.get("metrics"), Mapping) else {}
    score = float(metrics.get("compression_lower_95") or 0.0)
    eligible = bool(
        row.get("passed") is True
        and score > 1.0
        and float(metrics.get("decompression_geomean") or 0.0) >= 0.995
        and float(metrics.get("worst_cell_speedup") or 0.0) >= 0.98
    )
    return eligible, score


def selection_key(identity: str, row: Mapping[str, Any]) -> tuple[float, int, int, str, str]:
    eligible, score = validation_eligible(row)
    _ = eligible
    return (
        -score,
        0 if row.get("is_root") else 1,
        int(row.get("diff_lines") or 0),
        str(row.get("commit") or ""),
        identity,
    )


def clean_winner(
    finalists: Sequence[Mapping[str, Any]],
    evaluations: Mapping[str, Mapping[str, Any]],
) -> str | None:
    eligible = []
    for finalist in finalists:
        identity = str(finalist["identity"])
        row = evaluations[identity]
        ok, _ = validation_eligible(row)
        if ok:
            eligible.append(identity)
    if not eligible:
        return None
    return min(eligible, key=lambda identity: selection_key(identity, evaluations[identity]))


def post_corruption_eligibility_probability(
    row: Mapping[str, Any],
    *,
    q_fp: float,
    q_fn: float,
    corrupt_root: bool,
) -> float:
    clean_ok, _ = validation_eligible(row)
    if row.get("is_root") and not corrupt_root:
        return 1.0
    return (1.0 - q_fn) if clean_ok else q_fp


def exact_winner_distribution(
    finalists: Sequence[Mapping[str, Any]],
    evaluations: Mapping[str, Mapping[str, Any]],
    *,
    q_fp: float,
    q_fn: float,
    corrupt_root: bool = False,
) -> dict[str | None, float]:
    if not (0.0 <= q_fp <= 1.0 and 0.0 <= q_fn <= 1.0):
        raise ValueError("q_fp and q_fn must lie in [0,1]")
    identities = [str(row["identity"]) for row in finalists]
    ordered = sorted(identities, key=lambda identity: selection_key(identity, evaluations[identity]))
    dist: dict[str | None, float] = {}
    prefix_ineligible = 1.0
    for identity in ordered:
        p_eligible = post_corruption_eligibility_probability(
            evaluations[identity], q_fp=q_fp, q_fn=q_fn, corrupt_root=corrupt_root
        )
        p_win = prefix_ineligible * p_eligible
        if p_win:
            dist[identity] = dist.get(identity, 0.0) + p_win
        prefix_ineligible *= 1.0 - p_eligible
    if prefix_ineligible:
        dist[None] = prefix_ineligible
    total = sum(dist.values())
    if not math.isclose(total, 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise AssertionError(f"winner distribution does not sum to one: {total}")
    return dist


def conservative_holdout_score(row: Mapping[str, Any]) -> float | None:
    metrics = row.get("metrics") if isinstance(row.get("metrics"), Mapping) else {}
    if "compression_geomean" not in metrics:
        return None
    return float(metrics["compression_geomean"]) if row.get("passed") is True else 1.0


def summarize_groups(
    groups: Sequence[Mapping[str, Any]],
    evaluations: Mapping[str, Mapping[str, Any]],
    holdout_evaluations: Mapping[str, Mapping[str, Any]],
    *,
    q_fp: float,
    q_fn: float,
    corrupt_root: bool,
) -> dict[str, Any]:
    if not groups:
        return {"group_count": 0}

    winner_error = 0.0
    selected_clean_ineligible = 0.0
    root_selected = 0.0
    no_selection = 0.0
    clean_winner_reject_event = 0.0
    fp_preempt_event = 0.0
    fp_or_fn_union = 0.0
    measurable_winner_mass = 0.0
    paired_regret_mass = 0.0
    paired_regret_weighted_sum = 0.0
    paired_abs_regret_weighted_sum = 0.0
    clean_winner_holdout_available_groups = 0

    per_group = []
    for group in groups:
        finalists = list(group["finalists"])
        clean = clean_winner(finalists, evaluations)
        expected = group.get("top10_winner_identity")
        if clean != expected:
            raise AssertionError(
                f"published winner replay mismatch block={group.get('block')} "
                f"arm={group.get('arm')} checkpoint={group.get('checkpoint')}: "
                f"computed={clean!r}, published={expected!r}"
            )
        dist = exact_winner_distribution(
            finalists,
            evaluations,
            q_fp=q_fp,
            q_fn=q_fn,
            corrupt_root=corrupt_root,
        )
        p_clean = dist.get(clean, 0.0)
        p_error = 1.0 - p_clean
        winner_error += p_error
        no_selection += dist.get(None, 0.0)

        clean_row = evaluations[clean] if clean is not None else None
        clean_holdout = holdout_evaluations.get(clean) if clean is not None else None
        clean_holdout_score = (
            conservative_holdout_score(clean_holdout) if clean_holdout is not None else None
        )
        if clean_holdout_score is not None:
            clean_winner_holdout_available_groups += 1

        ordered = sorted(
            [str(row["identity"]) for row in finalists],
            key=lambda identity: selection_key(identity, evaluations[identity]),
        )
        clean_pos = ordered.index(clean) if clean is not None else len(ordered)
        higher = ordered[:clean_pos]
        p_no_fp_preempt = 1.0
        for identity in higher:
            row = evaluations[identity]
            clean_ok, _ = validation_eligible(row)
            if not clean_ok and not row.get("is_root"):
                p_no_fp_preempt *= 1.0 - q_fp
        p_fp_preempt = 1.0 - p_no_fp_preempt
        fp_preempt_event += p_fp_preempt

        if clean_row is not None:
            clean_ok, _ = validation_eligible(clean_row)
            if clean_row.get("is_root") and not corrupt_root:
                p_clean_reject = 0.0
            else:
                p_clean_reject = q_fn if clean_ok else 0.0
        else:
            p_clean_reject = 0.0
        clean_winner_reject_event += p_clean_reject
        fp_or_fn_union += 1.0 - (1.0 - p_fp_preempt) * (1.0 - p_clean_reject)

        group_measurable_mass = 0.0
        group_paired_regret_mass = 0.0
        group_paired_regret_sum = 0.0
        for identity, p_win in dist.items():
            if identity is None:
                continue
            row = evaluations[identity]
            clean_ok, _ = validation_eligible(row)
            if not clean_ok:
                selected_clean_ineligible += p_win
            if row.get("is_root"):
                root_selected += p_win
            h = holdout_evaluations.get(identity)
            h_score = conservative_holdout_score(h) if h is not None else None
            if h_score is not None:
                measurable_winner_mass += p_win
                group_measurable_mass += p_win
                if clean_holdout_score is not None:
                    regret = clean_holdout_score - h_score
                    paired_regret_mass += p_win
                    group_paired_regret_mass += p_win
                    paired_regret_weighted_sum += p_win * regret
                    paired_abs_regret_weighted_sum += p_win * abs(regret)
                    group_paired_regret_sum += p_win * regret

        per_group.append(
            {
                "block": group.get("block"),
                "arm": group.get("arm"),
                "checkpoint": group.get("checkpoint"),
                "clean_winner_identity": clean,
                "winner_identity_error_probability": p_error,
                "selected_winner_holdout_observable_probability": group_measurable_mass,
                "paired_holdout_regret_observable_probability": group_paired_regret_mass,
                "paired_holdout_regret_weighted_sum": group_paired_regret_sum,
            }
        )

    n = float(len(groups))
    result = {
        "group_count": len(groups),
        "q_fp": q_fp,
        "q_fn": q_fn,
        "corrupt_root": corrupt_root,
        "mean_winner_identity_error_probability": winner_error / n,
        "mean_selected_clean_ineligible_probability": selected_clean_ineligible / n,
        "mean_clean_winner_false_reject_event_probability": clean_winner_reject_event / n,
        "mean_false_admit_preemption_event_probability": fp_preempt_event / n,
        "mean_union_of_clean_winner_reject_or_fp_preemption": fp_or_fn_union / n,
        "mean_root_selected_probability": root_selected / n,
        "mean_no_selection_probability": no_selection / n,
        "mean_selected_winner_holdout_observable_probability": measurable_winner_mass / n,
        "clean_winner_holdout_available_group_fraction": clean_winner_holdout_available_groups / n,
        "mean_paired_holdout_regret_observable_probability": paired_regret_mass / n,
        "conditional_mean_paired_holdout_regret": (
            paired_regret_weighted_sum / paired_regret_mass if paired_regret_mass else None
        ),
        "conditional_mean_absolute_paired_holdout_regret": (
            paired_abs_regret_weighted_sum / paired_regret_mass if paired_regret_mass else None
        ),
        "per_group": per_group,
    }
    if not math.isclose(
        result["mean_winner_identity_error_probability"],
        result["mean_union_of_clean_winner_reject_or_fp_preemption"],
        rel_tol=1e-10,
        abs_tol=1e-10,
    ):
        raise AssertionError("error decomposition invariant failed")
    return result


def parse_grid(text: str) -> tuple[float, ...]:
    values = tuple(float(piece.strip()) for piece in text.split(",") if piece.strip())
    if not values or any(value < 0 or value > 1 for value in values):
        raise argparse.ArgumentTypeError("grid must contain comma-separated probabilities in [0,1]")
    return values


def load_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 3 or payload.get("target") != "Zstandard":
        raise ValueError("expected Loreley Zstandard formal record schema_version=3")
    return payload


def merged_holdout(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    official = dict(payload.get("holdout_evaluations") or {})
    extra = dict(
        ((payload.get("top5_posthoc_sensitivity") or {}).get("new_holdout_evaluations") or {})
    )
    official.update(extra)
    return official


def validate_public_record(payload: Mapping[str, Any]) -> dict[str, Any]:
    groups = list(payload.get("selection_groups") or [])
    evaluations = dict(payload.get("validation_evaluations") or {})
    if len(groups) != 126:
        raise AssertionError(f"expected 126 selection groups, observed {len(groups)}")
    replayed = 0
    for group in groups:
        computed = clean_winner(group["finalists"], evaluations)
        if computed != group.get("top10_winner_identity"):
            raise AssertionError(
                f"clean selection mismatch at {group.get('block')}/"
                f"{group.get('arm')}/{group.get('checkpoint')}"
            )
        replayed += 1
    endpoint = [g for g in groups if int(g.get("checkpoint")) == 48]
    if len(endpoint) != 21:
        raise AssertionError(f"expected 21 endpoint selection groups, observed {len(endpoint)}")
    return {
        "selection_groups": len(groups),
        "clean_winners_replayed_exactly": replayed,
        "endpoint_groups_checkpoint_48": len(endpoint),
        "validation_evaluation_count": len(evaluations),
        "official_holdout_evaluation_count": len(payload.get("holdout_evaluations") or {}),
        "extra_top5_holdout_evaluation_count": len(
            ((payload.get("top5_posthoc_sensitivity") or {}).get("new_holdout_evaluations") or {})
        ),
        "merged_holdout_evaluation_count": len(merged_holdout(payload)),
    }


def sweep(
    payload: Mapping[str, Any],
    grid: Sequence[float],
    *,
    corrupt_root: bool,
) -> dict[str, Any]:
    groups = list(payload["selection_groups"])
    endpoint = [g for g in groups if int(g["checkpoint"]) == 48]
    evaluations = dict(payload["validation_evaluations"])
    holdout = merged_holdout(payload)

    scenarios = []
    for mode in ("fp_only", "fn_only", "symmetric"):
        for p in grid:
            q_fp = p if mode in ("fp_only", "symmetric") else 0.0
            q_fn = p if mode in ("fn_only", "symmetric") else 0.0
            scenarios.append(
                {
                    "mode": mode,
                    "p": p,
                    "all_groups": summarize_groups(
                        groups, evaluations, holdout,
                        q_fp=q_fp, q_fn=q_fn, corrupt_root=corrupt_root,
                    ),
                    "endpoint_checkpoint_48": summarize_groups(
                        endpoint, evaluations, holdout,
                        q_fp=q_fp, q_fn=q_fn, corrupt_root=corrupt_root,
                    ),
                }
            )
    return {
        "schema_version": 1,
        "experiment": "loreley_public_selection_layer_corruption_exact",
        "scope": (
            "Exact replay of released fixed-finalist validation eligibility/selection only; "
            "not a replay of hidden candidate generation, online archive insertion/eviction, "
            "or parent-selection feedback."
        ),
        "noise_model": {
            "false_admit": "clean-ineligible non-root eligibility flipped on with probability q_fp",
            "false_reject": "clean-eligible non-root eligibility flipped off with probability q_fn",
            "root_fixed_eligible": not corrupt_root,
            "independence": "candidate eligibility corruptions independent within each group",
            "calculation": "closed-form exact winner probabilities; no Monte Carlo",
        },
        "record_validation": validate_public_record(payload),
        "grid": list(grid),
        "scenarios": scenarios,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="path to released zstd_formal_records.json")
    parser.add_argument("--output", type=Path, help="write JSON result to this path")
    parser.add_argument(
        "--grid",
        type=parse_grid,
        default=DEFAULT_GRID,
        help="comma-separated probabilities (default: 0,.05,.10,.20,.30,.40,.50)",
    )
    parser.add_argument(
        "--corrupt-root",
        action="store_true",
        help="sensitivity mode: allow false rejection of the root fallback too",
    )
    args = parser.parse_args()
    payload = load_payload(args.record)
    result = sweep(payload, args.grid, corrupt_root=args.corrupt_root)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
