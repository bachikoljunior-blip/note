#!/usr/bin/env python3
"""Finite synthetic stress test for bounded evidence retention/compaction.
Equal-weight mechanism counts; not empirical failure rates.
"""
from itertools import product
from collections import Counter, defaultdict
import json

FINALITY_BOUND = {"bound3": 3, "bound30": 30, "unknown": None}
GRACE = [3, 30, 90]
LATE_TRANSITION_AGE = [None, 2, 10, 40, 100]
DELIVERY = ["delivered", "lost"]
STATUS_LOOKUP = [False, True]
TOMBSTONE = [3, 30, 90]
DUPLICATE_AGE = [2, 10, 40, 100]
ARCHIVE = ["none", "provider30", "own_indefinite"]
CRASH = ["none", "after_snapshot_before_truncate", "after_truncate_before_commit_marker"]
SCHEMA = ["current", "old_migratable", "old_unmigratable"]
STALE_COMPACTOR = [False, True]
POLICIES = [
    "raw_append_finality_gate",
    "neg_snapshot_truncate_immediate",
    "snapshot_tombstone_source_gate",
    "versioned_snapshot_terminal_witness",
    "archive_replay_fallback",
]

def contract_consistent(bound, late_age):
    return late_age is None or bound is None or late_age <= bound

def finality_window_closed(bound, grace):
    return bound is not None and grace >= bound

def archive_horizon(archive):
    if archive == "own_indefinite": return float("inf")
    if archive == "provider30": return 30
    return 0

def transition_known_by_grace(late_age, delivery, status_lookup, archive, grace):
    if late_age is None or late_age > grace: return True
    if delivery == "delivered": return True
    if status_lookup: return True
    return late_age <= archive_horizon(archive)

def source_gated_terminality(bound, grace, late_age, delivery, status_lookup, archive):
    if not finality_window_closed(bound, grace): return False, False
    if not transition_known_by_grace(late_age, delivery, status_lookup, archive, grace): return False, False
    return True, False

def evaluate(policy, bound, grace, late_age, delivery, status_lookup, tomb, dup_age, archive, crash, schema, stale):
    r = Counter()
    transition_occurs = late_age is not None
    transition_before_grace = transition_occurs and late_age <= grace
    if policy == "raw_append_finality_gate":
        r["storage_units"] = 8; r["recovery_io"] = 8
        terminal, false = source_gated_terminality(bound, grace, late_age, delivery, status_lookup, archive)
        r["terminal"] = int(terminal); r["false_terminal"] = int(false); r["unresolved"] = int(not terminal)
        if transition_before_grace and delivery == "delivered":
            r["late_transition_processed"] = 1; r["comp_trigger_count"] = 1
        elif transition_before_grace and status_lookup:
            r["status_lookup_used"] = 1; r["late_transition_processed"] = 1; r["comp_trigger_count"] = 1
        elif transition_before_grace and late_age <= archive_horizon(archive):
            r["archive_replay_used"] = 1; r["late_transition_processed"] = 1; r["comp_trigger_count"] = 1
        if transition_before_grace and not transition_known_by_grace(late_age, delivery, status_lookup, archive, grace): r["missed_late_transition"] = 1
        return r
    if policy == "neg_snapshot_truncate_immediate":
        r["storage_units"] = 1; r["recovery_io"] = 1; r["terminal"] = 1
        r["false_terminal"] = int(transition_occurs)
        if transition_before_grace and delivery == "lost" and not status_lookup: r["missed_late_transition"] = 1
        r["duplicate_trigger"] = 1; r["comp_trigger_count"] = 1
        if crash != "none": r["crash_ambiguous"] = 1
        if schema != "current": r["migration_error"] = 1
        if stale: r["stale_compactor_accept"] = 1
        return r
    if policy == "snapshot_tombstone_source_gate":
        r["storage_units"] = 3; r["recovery_io"] = 2
        terminal, false = source_gated_terminality(bound, grace, late_age, delivery, status_lookup, archive)
        r["terminal"] = int(terminal); r["false_terminal"] = int(false); r["unresolved"] = int(not terminal)
        if transition_before_grace:
            if delivery == "delivered" or status_lookup or late_age <= archive_horizon(archive): r["late_transition_processed"] = 1; r["comp_trigger_count"] += 1
            else: r["missed_late_transition"] = 1
        if dup_age > tomb: r["duplicate_trigger"] = 1; r["comp_trigger_count"] += 1
        if crash == "after_truncate_before_commit_marker": r["crash_ambiguous"] = 1
        if schema == "old_unmigratable": r["migration_block"] = 1; r["terminal"] = 0; r["unresolved"] = 1
        if stale:
            r["stale_compactor_accept"] = 1
            if terminal or transition_before_grace: r["false_terminal"] = 1
        return r
    if policy == "versioned_snapshot_terminal_witness":
        r["storage_units"] = 4; r["recovery_io"] = 2
        terminal, false = source_gated_terminality(bound, grace, late_age, delivery, status_lookup, archive)
        r["terminal"] = int(terminal); r["false_terminal"] = int(false); r["unresolved"] = int(not terminal)
        if transition_before_grace:
            if delivery == "delivered" or status_lookup or late_age <= archive_horizon(archive): r["late_transition_processed"] = 1; r["comp_trigger_count"] = 1
            else: r["missed_late_transition"] = 1
        r["duplicate_trigger"] = 0; r["crash_ambiguous"] = 0
        if schema == "old_unmigratable": r["migration_block"] = 1; r["terminal"] = 0; r["unresolved"] = 1
        if stale: r["stale_compactor_blocked"] = 1
        return r
    if policy == "archive_replay_fallback":
        r["storage_units"] = 5 if archive == "own_indefinite" else 2; r["recovery_io"] = 4
        terminal, false = source_gated_terminality(bound, grace, late_age, delivery, status_lookup, archive)
        r["terminal"] = int(terminal); r["false_terminal"] = int(false); r["unresolved"] = int(not terminal)
        if transition_before_grace:
            if delivery == "delivered": r["late_transition_processed"] = 1; r["comp_trigger_count"] = 1
            elif status_lookup: r["status_lookup_used"] = 1; r["late_transition_processed"] = 1; r["comp_trigger_count"] = 1
            elif late_age <= archive_horizon(archive): r["archive_replay_used"] = 1; r["late_transition_processed"] = 1; r["comp_trigger_count"] = 1
            else: r["missed_late_transition"] = 1
        r["duplicate_trigger"] = 0
        if crash != "none":
            if archive == "none" and not status_lookup: r["crash_ambiguous"] = 1
            else:
                r["archive_replay_used"] += int(archive != "none"); r["status_lookup_used"] += int(archive == "none" and status_lookup); r["recovery_io"] += 2
        if schema == "old_unmigratable": r["migration_block"] = 1; r["terminal"] = 0; r["unresolved"] = 1
        if stale: r["stale_compactor_blocked"] = 1
        return r
    raise ValueError(policy)

def unsafe(r):
    return int(bool(r["false_terminal"] or r["duplicate_trigger"] or r["stale_compactor_accept"] or r["migration_error"] or r["crash_ambiguous"]))

def main():
    totals = {p: Counter() for p in POLICIES}; slices = defaultdict(Counter); n = 0
    for (bound_name, bound), grace, late_age, delivery, status_lookup, tomb, dup_age, archive, crash, schema, stale in product(FINALITY_BOUND.items(), GRACE, LATE_TRANSITION_AGE, DELIVERY, STATUS_LOOKUP, TOMBSTONE, DUPLICATE_AGE, ARCHIVE, CRASH, SCHEMA, STALE_COMPACTOR):
        if not contract_consistent(bound, late_age): continue
        n += 1; results = {}
        for p in POLICIES:
            r = evaluate(p, bound, grace, late_age, delivery, status_lookup, tomb, dup_age, archive, crash, schema, stale); r["unsafe"] = unsafe(r); results[p] = r
            totals[p]["scenarios"] += 1
            for k,v in r.items(): totals[p][k] += v
            if r["terminal"]: totals[p]["terminal_scenarios"] += 1
            if r["unsafe"]: totals[p]["unsafe_scenarios"] += 1
            if r["false_terminal"]: totals[p]["false_terminal_scenarios"] += 1
            if r["duplicate_trigger"]: totals[p]["duplicate_trigger_scenarios"] += 1
            if r["missed_late_transition"]: totals[p]["missed_late_transition_scenarios"] += 1
            if r["crash_ambiguous"]: totals[p]["crash_ambiguous_scenarios"] += 1
            if r["stale_compactor_accept"]: totals[p]["stale_compactor_accept_scenarios"] += 1
            if r["migration_block"]: totals[p]["migration_block_scenarios"] += 1
        if bound_name == "unknown" and late_age is not None:
            s=slices["unknown_finality_bound_with_future_transition"]; s["scenarios"] += 1
            for p,r in results.items(): s[p+"_terminal"] += int(r["terminal"]); s[p+"_false_terminal"] += int(r["false_terminal"])
        if dup_age > tomb:
            s=slices["duplicate_after_tombstone_expiry"]; s["scenarios"] += 1
            for p,r in results.items(): s[p+"_duplicate_trigger"] += int(r["duplicate_trigger"])
        if crash != "none":
            s=slices["compaction_crash"]; s["scenarios"] += 1
            for p,r in results.items(): s[p+"_ambiguous"] += int(r["crash_ambiguous"])
        if stale:
            s=slices["stale_compactor_takeover"]; s["scenarios"] += 1
            for p,r in results.items(): s[p+"_unsafe"] += int(r["unsafe"]); s[p+"_blocked"] += int(r["stale_compactor_blocked"])
        if dup_age > tomb and dup_age <= 30:
            s=slices["provider_replay_surface_outlives_local_tombstone"]; s["scenarios"] += 1
            for p,r in results.items(): s[p+"_duplicate_trigger"] += int(r["duplicate_trigger"])
        if late_age is not None and late_age <= grace and delivery == "lost" and not status_lookup:
            s=slices["lost_late_event_before_certification"]; s["scenarios"] += 1
            for p,r in results.items(): s[p+"_terminal"] += int(r["terminal"]); s[p+"_missed"] += int(r["missed_late_transition"]); s[p+"_archive_replay_used"] += int(r["archive_replay_used"])
    out={"model":{"scenario_count":n,"equal_weight_synthetic":True,"empirical_rate_claim":False,"dimensions":{"source_finality_bound":list(FINALITY_BOUND),"terminal_grace":GRACE,"late_transition_age":LATE_TRANSITION_AGE,"delivery":DELIVERY,"status_lookup":STATUS_LOOKUP,"tombstone_horizon":TOMBSTONE,"duplicate_age":DUPLICATE_AGE,"archive":ARCHIVE,"crash":CRASH,"schema":SCHEMA,"stale_compactor":STALE_COMPACTOR}},"policies":{},"slices":{k:dict(v) for k,v in slices.items()},"scope_limits":["Finite mechanism lattice only; counts are not production probabilities.","A source finality bound is an explicit modeled contract; it is never inferred from webhook retry, manual resend, event retrieval, or archive retention windows.","Known-bound scenarios exclude late transitions after the modeled bound; unknown-bound scenarios keep them possible.","Provider30 archive is a synthetic 30-day replay/retrieval capability used only to test horizon mismatch; own_indefinite is a strong positive capability assumption.","Storage and recovery-I/O units are ordinal synthetic costs, not bytes or latency measurements."]}
    for p,c in totals.items():
        d=dict(c); d["terminal_coverage"]=c["terminal_scenarios"]/n; d["unsafe_rate"]=c["unsafe_scenarios"]/n; d["avg_storage_units"]=c["storage_units"]/n; d["avg_recovery_io"]=c["recovery_io"]/n; out["policies"][p]=d
    print(json.dumps(out, indent=2, sort_keys=True))
if __name__ == '__main__': main()
