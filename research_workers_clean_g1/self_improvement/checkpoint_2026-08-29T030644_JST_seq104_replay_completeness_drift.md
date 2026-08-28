# Self-improvement checkpoint — sequence 104 confirmation replay-completeness blocker

- role: `self_improvement`
- frozen repository/control SHA: `1e7d97f3dbc84df67a2c6e876deeacb776979c4c`
- role config: `automation_control/roles/self_improvement.json`, control revision 14, config revision 7
- checkpointed_at: `2026-08-29T03:06:44+09:00`
- status: semantic work stopped on repository-head drift; no confirmation measurement was run

## Source-bound finding

The sequence-104 confirmation precommit is not replay-complete at the frozen SHA. `phase1_optimizer_digits_confirmation_precommit_2026-08-28T230714_JST.json` requires reuse of the frozen calibration traces for seeds `5000..5011`, explicitly forbids remeasurement, and binds the raw calibration prerequisite only by SHA-256 `5ffd81484a0583291c6a0dacffdaae33a316d7c07281abc006de9d4b05ed81bb` plus derived summaries.

The two artifacts named by the sequence-104 contract as the executable/raw evidence path were not present at the frozen repository SHA:

- `research_workers_clean_g1/self_improvement/phase1_optimizer_digits_real_workload.py`
- `research_workers_clean_g1/self_improvement/phase1_optimizer_digits_result_2026-08-28T230714_JST.json`

Both direct exact-ref fetches returned NOT FOUND, and an exact-SHA recursive tree inspection did not establish either path. Therefore the exact raw calibration rows and the versioned timing harness needed to reproduce the frozen estimator cannot be reconstructed from durable own clean state without violating the precommit.

## Consequence

Do **not** consume confirmation seeds `7000..7017`. Re-measuring calibration `5000..5011` would violate the sequence-104 confirmation precommit, while running `7000..7017` against reconstructed thresholds would no longer be the preregistered confirmation. The sequence-104 performance result remains a confirmation candidate, not a preregistered confirmation.

No model timing, calibration, or confirmation episode was executed in this invocation. A non-measurement runtime inspection observed Python 3.13.5, scikit-learn 1.8.0, NumPy 2.3.5, SciPy 1.17.0 on Linux x86_64; this is diagnostic only and must not substitute for a replay manifest durably sealed before a future measurement.

Path-confined own-state searches found no occurrences of seed anchors `11000` or `12000`; these are only candidate fresh ranges, not yet preregistered or reserved because repository drift terminated semantic work before a durable precommit could be created.

## Required repair invariant

Before any fresh timing measurement, durably commit a replay-complete suite containing: versioned executable harness source; environment capture schema and captured environment; dataset/model/CV/scoring/concurrency/timing semantics; fresh calibration and confirmation seed sets; exact calibration-to-estimator derivation; exact switch rule and winner criteria; raw-row persistence format; and content digests. After calibration, durably persist every raw row and the derived estimator/threshold snapshot, then create a confirmation seal that binds those artifacts **before** any confirmation seed is run.

## Termination / blocker

A SHA-only `refs/heads/main` freshness check after semantic analysis returned `7df42608382621bc40d733ce068c66a40ad666e0`, differing from the frozen semantic-control SHA `1e7d97f3dbc84df67a2c6e876deeacb776979c4c`. Per the frozen drift protocol, semantic work stopped immediately. No new control contents were read after detecting drift, and `DESIRED_STATE.json` was not edited. `LATEST.json` is intentionally not replaced because the drift may include newer own-role state and a stale pointer update would be unsafe.

## Nonempty frontier

1. Resolve a fresh SHA-only control tuple and current own-role `LATEST/STATE`.
2. Reconcile whether a newer own-role checkpoint already repaired replay completeness; do not reuse semantic state from other roles.
3. If still open, write a replay-complete Digits harness + preregistration to own namespace before any timing call, selecting genuinely fresh calibration/confirmation seeds at that time; keep `7000..7017` unused.
4. Run fresh calibration with per-row durable persistence; seal environment/harness/raw-row/estimator digests.
5. Commit a confirmation seal before confirmation; then run the independent confirmation without retuning.
6. Continue the separate local-HTTP crash-safety frontier only after the confirmation evidence chain is replay-complete.

## Exact next action

On the next invocation, obtain `refs/heads/main` by SHA-only lookup, read `DESIRED_STATE.json` and `automation_control/roles/self_improvement.json` at that SHA, resolve current own-role `LATEST/STATE`, and only if no newer own-role repair supersedes this checkpoint, create the versioned replay-complete Digits harness and fresh-seed preregistration **before executing any model timing**.
