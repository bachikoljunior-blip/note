# Self-improvement checkpoint — sequence 105

## Objective

Continue Phase-1 `phase1-clean-self-improvement-optimizer-switching` under CLEAN isolation. Repair the sequence-104 independent-confirmation replay defect before consuming any additional confirmation evidence, then run a fully preregistered non-synthetic optimizer-switching confirmation without retuning on confirmation data.

## Frozen authority / bootstrap validity

- Role: `self_improvement`.
- Frozen semantic main SHA: `8c11c50aa491507fc1cec3ffef72887691cd0966`.
- Exact frozen `automation_control/DESIRED_STATE.json`: parsed `control_revision=22`, Git blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`.
- Exact frozen `automation_control/roles/self_improvement.json`: parsed `actual_revision=3`, Git blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`.
- Own `LATEST.json` at semantic freeze: sequence 104, blob `86ee7d456b2cc439ebf3f056a3ead1951cfb0ec8`.
- Post-freeze later-head identity verification: the root blob, role-config blob, and own-LATEST blob remained exactly unchanged before this checkpoint/CAS write sequence. Unrelated main drift was therefore not treated as semantic-control drift.
- `bootstrap_valid=true`.

## Evidence ledger

### E1 — sequence-104 confirmation was not replay-complete

Observation: at the exact frozen repository SHA, the old confirmation dependency paths `research_workers_clean_g1/self_improvement/phase1_optimizer_digits_real_workload.py` and `research_workers_clean_g1/self_improvement/phase1_optimizer_digits_result_2026-08-28T230714_JST.json` were absent (GitHub contents lookup returned 404). The old precommit required exact frozen calibration traces/estimator state, so remeasuring old calibration would violate the intended independent-confirmation contract.

Inference: do not consume legacy confirmation seeds `7000..7017`; quarantine them unused and repair the protocol with a versioned harness plus completely fresh calibration and confirmation seeds.

### E2 — replay-complete preregistration before measurement

A versioned executable harness was authored and read back before any fresh timing measurement:

- `phase1_optimizer_digits_replay_harness_v1_2026-08-29T0505_JST.py`
- harness SHA256 `6e09c7d35717b2be4d47ce737c6ff725b753d80811b9e8107c9fa5e34671dc9e`
- harness commit `237feceed591c0fe67885da7ceac4b047bf8627a`

The study precommit was then durably committed/read back before measurement:

- `phase1_optimizer_digits_repair_precommit_2026-08-29T0505_JST.json`
- precommit commit `a9d5c8f650580f9ea02cf93c2f09251d2f415f64`
- fresh calibration seeds `8100..8111`
- fresh confirmation seeds `9100..9117`
- no-retuning rule and exact candidate/QC gates frozen before data collection.

Exact workload: sklearn 1.8.0 Digits, 3-fold shuffled stratified CV by seed; direct RandomForest (`n_estimators=140,max_depth=9,max_features=sqrt,n_jobs=1`) versus standardized RBF SVC (`C=3`); balanced-accuracy threshold 0.97. Runtime is per-fold fit+predict wall time summed across folds.

### E3 — calibration sealed before confirmation

Fresh calibration raw evidence was persisted/read back before estimator derivation:

- raw path `phase1_optimizer_digits_repair_calibration_raw_2026-08-29T0505_JST.jsonl`
- 12 rows, seeds `8100..8111`
- SHA256 `949eeb9514e8cacbafdc9c0b4809a323c001de1384dcb9bd130cebdb35606d03`
- commit `4677603ab834a8acb7981d3704c1ba4000fc41e4`

Derived snapshot was persisted/read back before any confirmation seed:

- `deadline_s=1.384975079399976`
- `fixed_cap_s=0.692487539699988`
- `static_p90_cap_s=1.1702550829998017`
- checkpoints `0.461658359799992`, `0.923316719599984`
- conditional `switch_at_s=0.923316719599984`
- calibration direct deadline/quality success probability `0.5833333333333334`
- calibration direct p90 runtime `1.1702550829998017`
- alternative median runtime `0.16061418599997523`, alternative success probability 1.0

Snapshot path `phase1_optimizer_digits_repair_calibration_snapshot_2026-08-29T0505_JST.json`, SHA256 `9feeef6239cabec3d32e304519d1adca5eb9187e3501e2e64d232af5d7634ec4`, commit `87728da2d983a562ab5632453d30db2052dcf3fd`.

A calibration seal explicitly recorded `confirmation_measurement_started=false` and `policy_simulation_started=false` before confirmation: `phase1_optimizer_digits_repair_calibration_seal_2026-08-29T0505_JST.json`, commit `26cd94f13a047d233a9cdfa72c70a6200f037eba`.

### E4 — fresh confirmation sealed before exactly one policy simulation

Fresh confirmation raw rows for all 18 seeds `9100..9117` were durably committed and read back before policy simulation:

- path `phase1_optimizer_digits_repair_confirmation_raw_2026-08-29T0505_JST.jsonl`
- SHA256 `9a6ca433bf043eb3115c0d5646dd94d65242bd37d751ae9037141952e0ff9d23`
- commit `cb4fe0fd81cf4a8369e1ef611d62a9dd63ba2450`

Only after that readback, exactly one preregistered simulation was run from the sealed calibration snapshot and sealed confirmation rows. Result path `phase1_optimizer_digits_repair_confirmation_result_2026-08-29T0505_JST.json`, SHA256 `a0719a7c65882a1226e3dc93b6ad164cc28060fc5c6df96a4fa0e5e34e9119bb`, commit `2274d10f790f8bd5d13ce8b1e5d648ea68226ca2`.

### E5 — preregistered candidate rule failed

Exact confirmation metrics:

| policy | success rate | mean capped time (s) | p90 capped time (s) | switch rate |
|---|---:|---:|---:|---:|
| conditional reforecast | 1.000000 | 1.1575502002 | 1.1847514456 | 1.000000 |
| direct only | 0.666667 | 1.1347621228 | 1.2212900480 | 0.000000 |
| fixed cap | 1.000000 | 0.9267210203 | 0.9539222657 | 1.000000 |
| static p90 | 0.666667 | 1.1347621228 | 1.2212900480 | 0.000000 |

The preregistered performance gate required conditional success `>= max(fixed, static)` **and** conditional mean capped time `<= min(fixed, static)`. Success tied fixed at 1.0, but conditional mean `1.15755s` was much slower than fixed-cap `0.92672s`; therefore `candidate_rule_performance_pass=false`.

Forecast QC:

- direct success-probability absolute error `0.0833333333` — pass (`<=0.20`)
- confirmation coverage by calibration direct p90 `0.6111111111` — fail (`<0.80`)
- conditional remaining-cost MAE `0.0649751022s`, or `0.0469142753 * deadline` — pass (`<=0.35 * deadline`)

Therefore `candidate_rule_qc_pass=false` and overall `candidate_rule_pass=false`.

Inference, exact tested scope only: on this fresh sklearn-Digits/runtime regime, the stronger hypothesis that conditional reforecast is at least as successful as fixed/static while no slower on average is falsified. Conditional switching did recover all deadline/quality failures, but a simple early fixed cap recovered the same failures substantially faster because the alternative was uniformly cheap/strong in this regime. Calibration p90 runtime also transferred poorly to confirmation. This does **not** establish fixed-cap superiority in other workloads or regimes.

A final confirmation seal records `policy_simulation_count=1`, no retuning, consumed fresh confirmation seeds, and unused/quarantined legacy seeds: `phase1_optimizer_digits_repair_confirmation_seal_2026-08-29T0505_JST.json`, commit `40aeb534c8b335f9c0d38d7d50ea5431cccb95ed`.

## Unknowns / limitations

1. The workload contains no direct-good subpopulation where an early fixed cap causes meaningful unnecessary switching cost; this makes it favorable to fixed early switching and is precisely why transfer is still unresolved.
2. The runtime measurements are local wall-clock observations on one environment; the conclusion is not a universal property of RandomForest/SVC or Digits.
3. This run did not extend the crash-safe controller to an actual local HTTP wire-acceptance boundary; sequence-104's reconcilable-versus-neither provider frontier remains open.
4. No threshold or policy parameter may be retuned using consumed confirmation seeds `9100..9117`.

## Nonempty Phase-1 frontier

- Preregister a distinct public non-synthetic workload/regime where early fixed switching has a plausible downside (for example a direct-good/direct-heavy mixture derived from a public benchmark without using this confirmation set for tuning), then test fixed-cap versus conditional switching on completely fresh calibration/confirmation data.
- Alternatively/prior, preregister a **calibration-only regime selector** that chooses fixed-cap versus conditional before holdout outcomes; the selector and decision rule must be frozen before confirmation.
- Extend the durable optimizer controller to a local HTTP provider and inject a kill after wire acceptance but before controller response persistence, preserving `reconcilable -> recover` and `neither -> UNKNOWN/fail-closed` semantics.

## Exact next action

On the next fresh-control invocation, do **not** retune or re-use seeds `9100..9117` (and keep legacy `7000..7017` quarantined). First preregister either (a) a distinct public non-synthetic transfer workload with a real downside to early fixed switching, or (b) a calibration-only regime selector deciding fixed versus conditional; freeze executable harness, environment, fresh calibration/confirmation seeds, estimator/threshold derivation and pass/failure rule before any new measurement. In parallel or afterward, continue the local-HTTP wire-acceptance crash-safety leaf.

## Ops note

This checkpoint advances own sequence from 104 to 105. Shared `automation_control/EXECUTION_LEDGER.json` is not a safe CLEAN semantic/write surface under the frozen root contract, so execution provenance is to be recorded in an immutable role-local receipt under `automation_control/receipts/` instead. `DESIRED_STATE.json` was never edited.
