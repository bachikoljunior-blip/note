"""Validate simultaneous numeric reporting on the production V3 family.

The test creates deterministic synthetic CLOSED rows through the actual role-local
ADMIT/SLOT/CLOSE journal protocol, then feeds those immutable rows to:
  1. direct production-V3 decision streams at alpha=.05;
  2. the generic dual-channel reporter's decision streams at alpha=.05;
  3. the reporter's simultaneous numeric streams at alpha=.025/.025.

The synthetic data are wiring/finite-condition stress only, not production reliability.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from math import log
from pathlib import Path
import random
import statistics
import sys
from typing import Any


def _load_sibling(filename: str, module_name: str) -> Any:
    path = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


_ADAPTER = _load_sibling(
    "v3_simultaneous_reporting_adapter_2026-08-27.py",
    "_evaluation_v3_reporting_adapter",
)
_REPORTER = _load_sibling(
    "simultaneous_dual_channel_reporting_v1_2026_08_27.py",
    "_evaluation_simultaneous_reporter",
)
_JOURNAL = _load_sibling(
    "atomic_dual_channel_journal_2026-08-27T2107_JST.py",
    "_evaluation_atomic_journal",
)


def _quantile(xs: list[float], p: float) -> float:
    ys = sorted(float(x) for x in xs)
    x = (len(ys) - 1) * p
    i = int(x)
    f = x - i
    return ys[i] if i == len(ys) - 1 else ys[i] * (1.0 - f) + ys[i + 1] * f


def _canonical_rows_digest(rows: list[dict[str, Any]]) -> str:
    h = sha256()
    for row in rows:
        r = _REPORTER.SimultaneousDualChannelReporter._canonicalize_row(row)
        h.update(json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n")
    return h.hexdigest()


def _one_campaign(seed: int, campaign: int, horizon: int, p_mismatch: float, p_missing: float, tau: float) -> dict[str, Any]:
    rng = random.Random(seed + campaign * 100003)
    contract = _REPORTER.DualChannelReportingContract(
        alpha_decision=0.05,
        alpha_joint_report=0.05,
        alpha_report_equal=0.025,
        alpha_report_exposure=0.025,
        tau_equal=tau,
        tau_exposure=tau,
    )
    reporter = _REPORTER.SimultaneousDualChannelReporter(
        _ADAPTER.production_v3_stream_factory,
        contract,
    )
    direct_equal = _ADAPTER.production_v3_stream_factory(0.05)
    direct_exposure = _ADAPTER.production_v3_stream_factory(0.05)

    journal = _JOURNAL.AtomicDualChannelJournal()
    blob = bytearray()
    b_cap = 16
    B = 8
    first_decision: int | None = None
    first_reporting: int | None = None
    widening: tuple[float, float] | None = None
    max_decision_log_e_diff = 0.0
    max_decision_endpoint_diff = 0.0
    log_threshold_decision = log(20.0)
    log_threshold_reporting = log(40.0)

    for j in range(1, horizon + 1):
        block_id = f"c{campaign:03d}-b{j:04d}"
        slot_ids = [f"s{k:02d}" for k in range(B)]
        t0 = campaign * 1_000_000.0 + j * 10.0
        admit = journal.admit_event(block_id, slot_ids, t0, t0 + 1.0, b_cap)
        blob += journal.encode_frame(admit)
        if journal.apply(admit) != "admitted":
            raise AssertionError("ADMIT failed")
        for sid in slot_ids:
            if rng.random() < p_missing:
                continue
            score = 1.0 if rng.random() < p_mismatch else 0.0
            ev = journal.slot_event(block_id, sid, score, t0 + 0.5)
            blob += journal.encode_frame(ev)
            if journal.apply(ev) != "slot_accepted":
                raise AssertionError("SLOT failed")
        close = journal.close_event(block_id, t0 + 1.1)
        blob += journal.encode_frame(close)
        if journal.apply(close) != "closed":
            raise AssertionError("CLOSE failed")

        row = journal.closed_rows[-1]
        reporter.append_closed_row(row)
        direct_equal.append(1.0, row["block_score"])
        direct_exposure.append(row["exposure_weight"], row["block_score"])

        de = direct_equal.log_e(tau)
        dx = direct_exposure.log_e(tau)
        we = reporter.decision_equal.log_e(tau)
        wx = reporter.decision_exposure.log_e(tau)
        max_decision_log_e_diff = max(max_decision_log_e_diff, abs(de - we), abs(dx - wx))

        decision_safe = de >= log_threshold_decision and dx >= log_threshold_decision
        reporting_safe = (
            reporter.report_equal.log_e(tau) >= log_threshold_reporting
            and reporter.report_exposure.log_e(tau) >= log_threshold_reporting
        )

        if first_decision is None and decision_safe:
            first_decision = j
            direct_ub_equal = direct_equal.upper_endpoint()
            direct_ub_exposure = direct_exposure.upper_endpoint()
            snap = reporter.snapshot()
            marginal = snap["marginal_numeric_bounds"]
            simultaneous = snap["simultaneous_reporting_contract"]
            max_decision_endpoint_diff = max(
                max_decision_endpoint_diff,
                abs(direct_ub_equal - marginal["equal_upper"]),
                abs(direct_ub_exposure - marginal["exposure_upper"]),
            )
            widening = (
                simultaneous["equal_upper_widening_vs_marginal"],
                simultaneous["exposure_upper_widening_vs_marginal"],
            )
        if first_reporting is None and reporting_safe:
            first_reporting = j
        if first_decision is not None and first_reporting is not None and j >= first_reporting + 3:
            break

        B = 16 if row["block_score"] < 0.05 else 4

    recovered, valid_len, tail_status = _JOURNAL.AtomicDualChannelJournal.recover(bytes(blob))
    if valid_len != len(blob) or tail_status != "clean_eof":
        raise AssertionError("canonical journal did not replay cleanly")
    if recovered.closed_rows != journal.closed_rows:
        raise AssertionError("journal replay changed closed rows")

    replayed = _REPORTER.SimultaneousDualChannelReporter.replay(
        _ADAPTER.production_v3_stream_factory,
        recovered.closed_rows,
        contract,
    )
    live_snapshot = reporter.snapshot()
    replay_snapshot = replayed.snapshot()
    if live_snapshot["rows_digest"] != replay_snapshot["rows_digest"]:
        raise AssertionError("row digest mismatch")
    replay_log_e_diff = max(
        abs(reporter.decision_equal.log_e(tau) - replayed.decision_equal.log_e(tau)),
        abs(reporter.decision_exposure.log_e(tau) - replayed.decision_exposure.log_e(tau)),
        abs(reporter.report_equal.log_e(tau) - replayed.report_equal.log_e(tau)),
        abs(reporter.report_exposure.log_e(tau) - replayed.report_exposure.log_e(tau)),
    )
    replay_endpoint_diff = max(
        abs(live_snapshot["marginal_numeric_bounds"]["equal_upper"] - replay_snapshot["marginal_numeric_bounds"]["equal_upper"]),
        abs(live_snapshot["marginal_numeric_bounds"]["exposure_upper"] - replay_snapshot["marginal_numeric_bounds"]["exposure_upper"]),
        abs(live_snapshot["simultaneous_reporting_contract"]["equal_upper"] - replay_snapshot["simultaneous_reporting_contract"]["equal_upper"]),
        abs(live_snapshot["simultaneous_reporting_contract"]["exposure_upper"] - replay_snapshot["simultaneous_reporting_contract"]["exposure_upper"]),
    )
    return {
        "first_decision": first_decision,
        "first_reporting": first_reporting,
        "widening": widening,
        "rows": len(recovered.closed_rows),
        "row_digest": _canonical_rows_digest(recovered.closed_rows),
        "decision_log_e_max_diff": max_decision_log_e_diff,
        "decision_endpoint_max_diff": max_decision_endpoint_diff,
        "replay_log_e_max_diff": replay_log_e_diff,
        "replay_endpoint_max_diff": replay_endpoint_diff,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    seed = 20260827
    campaigns = 60
    horizon = 600
    results = [_one_campaign(seed, c, horizon, 0.01, 0.002, 0.05) for c in range(campaigns)]
    if any(r["first_decision"] is None or r["first_reporting"] is None or r["widening"] is None for r in results):
        raise AssertionError("stress did not resolve all campaigns")
    delays = [r["first_reporting"] - r["first_decision"] for r in results]
    equal_widen = [r["widening"][0] for r in results]
    exposure_widen = [r["widening"][1] for r in results]
    decision_stops = [r["first_decision"] for r in results]
    reporting_stops = [r["first_reporting"] for r in results]
    digest_of_digests = sha256(("\n".join(r["row_digest"] for r in results) + "\n").encode("utf-8")).hexdigest()
    out = {
        "schema_version": 1,
        "seed": seed,
        "campaigns": campaigns,
        "horizon": horizon,
        "slot_mismatch_probability": 0.01,
        "slot_missing_probability": 0.002,
        "tau_equal": 0.05,
        "tau_exposure": 0.05,
        "b_cap": 16,
        "adaptive_block_rule": "B1=8; thereafter B=16 iff prior CLOSED block_score < 0.05 else B=4",
        "decision_resolved": sum(r["first_decision"] is not None for r in results),
        "reporting_resolved": sum(r["first_reporting"] is not None for r in results),
        "decision_first_safe": {"median": _quantile(decision_stops, 0.5), "mean": statistics.mean(decision_stops), "p95": _quantile(decision_stops, 0.95)},
        "reporting_first_safe": {"median": _quantile(reporting_stops, 0.5), "mean": statistics.mean(reporting_stops), "p95": _quantile(reporting_stops, 0.95)},
        "report_minus_decision_delay": {"median": _quantile(delays, 0.5), "mean": statistics.mean(delays), "p95": _quantile(delays, 0.95), "min": min(delays), "max": max(delays)},
        "bound_widening_at_decision_safe": {
            "equal": {"mean": statistics.mean(equal_widen), "median": _quantile(equal_widen, 0.5), "p95": _quantile(equal_widen, 0.95), "max": max(equal_widen)},
            "exposure": {"mean": statistics.mean(exposure_widen), "median": _quantile(exposure_widen, 0.5), "p95": _quantile(exposure_widen, 0.95), "max": max(exposure_widen)},
        },
        "invariants": {
            "decision_log_e_max_diff": max(r["decision_log_e_max_diff"] for r in results),
            "decision_endpoint_max_diff": max(r["decision_endpoint_max_diff"] for r in results),
            "replay_log_e_max_diff": max(r["replay_log_e_max_diff"] for r in results),
            "replay_endpoint_max_diff": max(r["replay_endpoint_max_diff"] for r in results),
            "unique_row_digests": len({r["row_digest"] for r in results}),
        },
        "max_rows_consumed": max(r["rows"] for r in results),
        "campaign_digest_sha256": digest_of_digests,
        "scope_guard": "Synthetic finite-condition implementation/replay stress using the production V3 statistical family; not a production reliability, latency, or stopping-time estimate.",
    }
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
