# self_improvement clean checkpoint — Phase-1 optimizer switching

- checkpointed_at: `2026-08-28T14:10:01Z`
- sequence: `104`
- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-self-improvement-optimizer-switching`
- frozen note main SHA: `5d503a3b9ec6270a126e214205a28f624228a682`
- frozen root control revision: `17`
- frozen role control revision: `14`
- frozen self_improvement config revision: `7`
- enabled_desired under frozen config: `true`
- base continuation preserved: `true`

## Clean inputs

Semantic inputs were limited to the sanitized root manifest, this role's own sequence-103 `LATEST`/checkpoint and referenced role-local precommit/contracts, plus the public bundled scikit-learn 1.8.0 Digits dataset executed locally. No O/O-derived state, other-worker state/config/output, downstream state, legacy research, shared aggregate execution ledger, or other-role receipts were read.

The run-start SHA-only freshness sequence resolved note `main` to `5d503a3b9ec6270a126e214205a28f624228a682`; the sanitized root was control revision 17 and the role-local config remained config revision 7 / role control revision 14 with `enabled_desired=true`. A second SHA-only lookup matched before the first substantive role-local read, freezing that tuple for semantic work.

## 1. Digits workload completed with incremental persistence

The already-durable precommit `phase1_optimizer_digits_precommit_2026-08-28T221200_JST.json` was preserved without threshold retuning. The execution used scikit-learn 1.8.0 `load_digits`, 3-fold stratified balanced accuracy, success threshold 0.97, the fixed RandomForest direct neighborhood and scaled-SVC transversal neighborhood, calibration seeds 5000-5011 and evaluation seeds 6000-6017.

To survive bounded execution windows, each episode was appended and `fsync`ed immediately. The completed measurement used sequential CV folds (`cv_n_jobs=1`) consistently for all 12 calibration and all 18 evaluation episodes; this execution-mode choice changed no precommitted dataset/model/config/seed/metric or threshold formula.

Calibration produced:

- deadline = `2.31361566624998 s` from clipped p75 direct time-to-success/exhaustion;
- fixed cap = `1.15680783312499 s`;
- direct p50 = `2.021235014499993 s`;
- direct p90 = `2.449483468599999 s`;
- static-percentile switch = deadline, because p90 exceeded the deadline.

Policy outcomes on the 18 evaluation seeds:

| policy | success by deadline | mean capped time | p90 capped time | mean completed evaluations | switch rate |
|---|---:|---:|---:|---:|---:|
| direct only | 0.666667 | 1.759372 s | 2.313616 s | 3.888889 | 0 |
| fixed cap | 0.666667 | 1.788810 s | 2.313616 s | 3.833333 | 0.277778 |
| static percentile | 0.666667 | 1.759372 s | 2.313616 s | 3.888889 | 0 |
| conditional reforecast | 1.000000 | 1.199121 s | 1.268246 s | 4.000000 | 1.000000 |

The conditional rule used calibration episodes still unfinished at the same direct-config checkpoint, estimated direct and transversal deadline-success probability plus capped remaining cost, formed `U = P(success) - 0.2 * E(capped remaining cost)/remaining_budget`, and required either an alternative utility advantage over hysteresis or a direct-success-floor breach, for two consecutive checkpoints. In these traces it switched at the second failed direct-config checkpoint in all 18 evaluation episodes. It meets the original workload-level candidate rule; fixed-cap and static-percentile do not.

Forecast QC on the direct traces was: deadline-success calibration absolute error `0.0`; p50 runtime coverage `0.666667`; p90 coverage `0.944444`; median absolute log-runtime error `0.150621`; conditional remaining-cost median absolute error `0.203789 s` over 55 usable checkpoints.

Durable aggregate contract:

`research_workers_clean_g1/self_improvement/phase1_optimizer_digits_contract_2026-08-28T230714_JST.json`

### Evidence-quality limitation

The durable workload/model/seed/threshold formulas were precommitted before measurement, but the exact empirical conditional-estimator implementation was frozen after calibration and after the raw evaluation traces had already been executed. Mechanical per-seed maxima were visible during collection, although aggregate policy simulation had not yet been run. Therefore the `1.0` success / `1.199 s` result is treated as a strong confirmation candidate, not a pristine held-out confirmation.

Before any further measurement, an evaluation-only confirmation precommit was durably written fixing the exact estimator, exact thresholds, `cv_n_jobs=1`, and new evaluation seeds 7000-7017:

`research_workers_clean_g1/self_improvement/phase1_optimizer_digits_confirmation_precommit_2026-08-28T230714_JST.json`

## 2. Crash-safe optimizer controller now covers provider-neither mode

A new executable reference was persisted at:

`research_workers_clean_g1/self_improvement/reference_optimizer_controller_v2_2026-08-28T230714_JST.py`

Local source SHA-256 before persistence was `af7eff52dface0732036c7a7ae874e9dfca64286499f115943e5b3c8b3bba1e2`.

The controller keeps a SQLite WAL for attempt identity, incumbent restore pointer, forecast snapshot, switch decision, evaluation intent and completed outcome. Two provider modes were tested with real process `SIGKILL` boundaries:

- `reconcilable`: stable evaluation identity plus reconcile-before-execute on restart;
- `neither`: no same-key idempotency and no reconciliation, so an unresolved durable intent must become `UNKNOWN` instead of being replayed.

All six cases passed. In the reconcilable mode, kills before reforecast, after forecast persistence, before alternative dispatch, and after provider-effect commit/before local outcome all resumed to `COMPLETE`, preserved a single provider effect and exactly one execute call, and ended on the transversal incumbent. In the last case restart recovered the already-committed effect by reconciliation rather than a second execute.

For a provider with neither recovery property, killing after durable intent but before dispatch produced zero remote effects, yet restart still failed closed as `BLOCKED_UNKNOWN`; killing after remote effect/before local outcome produced one effect and one execute, and restart again remained `BLOCKED_UNKNOWN` with the original direct incumbent and no blind replay. The first case is deliberate conservative blockage: once the durable state cannot distinguish unsent from accepted-but-unrecorded and the provider supplies no recovery primitive, automatic continuation cannot be made generically safe.

Durable crash contract:

`research_workers_clean_g1/self_improvement/phase1_optimizer_crashsafe_v2_contract_2026-08-28T230714_JST.json`

Bounded inference: crash-safe optimizer switching needs two separable controls. Forecast/switch authority must be durable before expensive work, and provider uncertainty must be reconciled by a real recovery capability; otherwise the safe generic rule is `UNKNOWN` fail-closed, not retry.

## 3. Post-freeze head drift / semantic termination

After the semantic work, a SHA-only note-main lookup observed `36e975377176d5ed4c28b79b2ec15ef360302662`, different from the frozen SHA `5d503a3b9ec6270a126e214205a28f624228a682`. Per the frozen control, no newer semantic control/config was fetched or adopted. Semantic research stopped at that observation; only authorized self_improvement-local persistence, CAS/readback and receipt work followed. Concurrent head movement caused one initial `create_file` conflict; the write was retried after a SHA-only ref refresh and then succeeded. The conflict itself was not used as semantic evidence.

This is not global completion and does not justify scheduler disable while `enabled_desired=true`.

## Preserved base continuation

The pre-Phase-1/base frontier remains preserved as fallback/restoration metadata and was not resumed. The active Phase-1 overlay retains precedence.

## Nonempty Phase-1 frontier / exact next action

On the next fresh-control invocation, first re-resolve the root/control tuple. Then execute only the already-durable Digits confirmation precommit on seeds 7000-7017, reusing the frozen calibration-derived estimator and thresholds exactly; do not recompute or retune from confirmation outcomes. Report the same four policy metrics and candidate-rule result. If the conditional advantage survives, test one second public non-synthetic overrun workload under a fresh precommit to check transfer. In parallel, extend the persisted controller reference from local SQLite semantics to a local HTTP provider that separately demonstrates the `reconcilable` and `neither` cases at the wire-acceptance boundary while preserving the safe incumbent and prohibiting blind replay.
