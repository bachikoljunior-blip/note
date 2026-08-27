"""Validate that audit-only reporting snapshots are exact functions of journal rows.

Uses the same deterministic V3 stress family as the reporting validator. No scientific
row history is stored in the snapshot; recovery must reconstruct from atomic-journal
CLOSED rows and reproduce the entire snapshot byte-for-byte after canonical JSON.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import random
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


_ADAPTER = _load_sibling("v3_simultaneous_reporting_adapter_2026-08-27.py", "_evaluation_snap_v3")
_REPORTER = _load_sibling("simultaneous_dual_channel_reporting_v1_2026_08_27.py", "_evaluation_snap_reporter")
_JOURNAL = _load_sibling("atomic_dual_channel_journal_2026-08-27T2107_JST.py", "_evaluation_snap_journal")
_SNAPSHOT = _load_sibling("simultaneous_reporting_snapshot_v1_2026_08_27.py", "_evaluation_snap_builder")


def _campaign(seed: int, campaign: int, blocks: int = 320) -> tuple[dict[str, Any], dict[str, Any]]:
    rng = random.Random(seed + campaign * 100003)
    contract = _REPORTER.DualChannelReportingContract(
        alpha_decision=0.05,
        alpha_joint_report=0.05,
        alpha_report_equal=0.025,
        alpha_report_exposure=0.025,
        tau_equal=0.05,
        tau_exposure=0.05,
    )
    live = _REPORTER.SimultaneousDualChannelReporter(_ADAPTER.production_v3_stream_factory, contract)
    journal = _JOURNAL.AtomicDualChannelJournal()
    blob = bytearray()
    b_cap = 16
    B = 8
    for j in range(1, blocks + 1):
        bid = f"c{campaign:03d}-b{j:04d}"
        slots = [f"s{k:02d}" for k in range(B)]
        t0 = campaign * 1_000_000.0 + j * 10.0
        admit = journal.admit_event(bid, slots, t0, t0 + 1.0, b_cap)
        blob += journal.encode_frame(admit)
        journal.apply(admit)
        for sid in slots:
            if rng.random() < 0.002:
                continue
            score = 1.0 if rng.random() < 0.01 else 0.0
            ev = journal.slot_event(bid, sid, score, t0 + 0.5)
            blob += journal.encode_frame(ev)
            journal.apply(ev)
        close = journal.close_event(bid, t0 + 1.1)
        blob += journal.encode_frame(close)
        journal.apply(close)
        row = journal.closed_rows[-1]
        live.append_closed_row(row)
        B = 16 if row["block_score"] < 0.05 else 4

    recovered, valid_len, tail_status = _JOURNAL.AtomicDualChannelJournal.recover(bytes(blob))
    if valid_len != len(blob) or tail_status != "clean_eof" or recovered.closed_rows != journal.closed_rows:
        raise AssertionError("journal replay mismatch")
    tag = "weighted_average_incremental_lsm_v3_warm_root_2026-08-27.py@54159990956368010b3445909f8bd8e8f569ecb7"
    stored = _SNAPSHOT.build_reporting_snapshot(live, tag)
    rebuilt = _SNAPSHOT.rebuild_snapshot_from_rows(
        _REPORTER.SimultaneousDualChannelReporter,
        _ADAPTER.production_v3_stream_factory,
        contract,
        recovered.closed_rows,
        tag,
    )
    _SNAPSHOT.assert_snapshot_matches(stored, rebuilt)
    if stored["scientific_history_embedded"] is not False or "closed_rows" in stored:
        raise AssertionError("snapshot embedded a second row history")
    return stored, rebuilt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    campaigns = 40
    mismatches = 0
    keys = set()
    for c in range(campaigns):
        try:
            a, b = _campaign(20260827, c)
            keys.add(a["snapshot_key"])
            if json.dumps(a, sort_keys=True, separators=(",", ":")) != json.dumps(b, sort_keys=True, separators=(",", ":")):
                mismatches += 1
        except Exception:
            mismatches += 1
    out = {
        "schema_version": 1,
        "campaigns": campaigns,
        "blocks_per_campaign": 320,
        "snapshot_identity_mismatches": mismatches,
        "unique_snapshot_keys": len(keys),
        "second_row_history_embedded": False,
        "scope_guard": "Synthetic implementation/replay stress only; snapshot remains an audit cache and never replaces the atomic journal CLOSED rows as scientific truth.",
    }
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
