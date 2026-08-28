# Self-improvement checkpoint — Phase-1 CAL-LEX-3ARM transfer

- sequence: 108
- role: `self_improvement`
- generation: `clean_g1`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v2-active-pool`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- source continuation: sequence 107 (`CAL-LEX-3ARM-v1`), frozen without changing selector rule, cap multipliers, tie priority, or pass logic.
- bootstrap_valid: **true**
- frozen semantic authority: main `f6b3c1273f7abb3685198ce5dbbc2368151eca6c`; root control revision 22 / blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`; self_improvement role control revision 14 / config revision 7 / blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`; own LATEST sequence 107 / blob `500d6830db8400b25e3a2231ce283b642d883ebd`.
- post-freeze authority identity verification: later heads advanced, but exact root/config blob identities remained unchanged and own LATEST blob remained unchanged before state replacement; no newer-head semantic content was consumed.

## Existing/public source audit

The transfer workloads are public non-synthetic scikit-learn datasets not used by the construction leaf:
- Iris classification: official `sklearn.datasets.load_iris` documentation describes 150 samples, 4 real-valued features, 3 classes. Source: https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html
- Diabetes regression: official `sklearn.datasets.load_diabetes` documentation describes 442 samples, 10 real-valued features and a continuous target. Source: https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_diabetes.html

The test intentionally changes dataset identity, task type, scoring metric, and model families while retaining the meta-selector itself.

## Durable preregistration and replay identity

Before any model timing, the following were persisted and read back:
- harness `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_transfer_harness_v1_2026-08-29T0631_JST.py`, Git blob `a6e8e0eac443197992d15ec029cfe22a77dd4383`, local SHA256 `aacd3e069118292ebb7d1bc2410c4c0cd1618f28637536b5696c7984447d9113`;
- environment `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_transfer_environment_2026-08-29T0631_JST.json`, Git blob `e6227a98081c010fdb127835f934f0e1584b70ef`, Python 3.13.5 / scikit-learn 1.8.0 / NumPy 2.3.5;
- precommit `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_transfer_precommit_2026-08-29T0631_JST.json`, Git blob `c5120c462c15a0959f3cc833d00e4ef67361b293`.

Fresh calibration seeds were `16000..16007`; fresh confirmation seeds were `17000..17011`. No measurement preceded precommit readback.

Frozen selector remained `CAL-LEX-3ARM-v1`: policies `{direct,fixed,conditional}`; primary maximize calibration deadline-success; secondary minimize calibration mean capped time; exact tie priority `direct > fixed > conditional`; fixed cap multiplier `0.50`; conditional cap multiplier `1.50`; deadline `fixed_cap + 1.05 * alternative_p90`; p90 method `higher`.

## Transfer scenarios

1. `iris_direct_good_transfer`: classification, balanced accuracy target `>=0.90`; direct = StandardScaler + LogisticRegression; alternative = RandomForestClassifier(400 trees, n_jobs=1).
2. `diabetes_alt_needed_transfer`: regression, R2 target `>=0.25`; direct = DummyRegressor(mean); alternative = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05).

Calibration raw was persisted/read back before derive:
- path `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_transfer_calibration_raw_2026-08-29T0631_JST.jsonl`
- 16 rows
- SHA256 `c0a3fdfb9fe591061240a7bd6f95eaa2d33a4250038a95687f908d9792c1e9d8`
- Git blob `dbfbf3f8f6f5c46496f54789de8991b57d2001bf`.

Frozen selector snapshot was then persisted/read back:
- path `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_transfer_snapshot_2026-08-29T0631_JST.json`
- SHA256 `95241cde67f21797646e8894e46e15f687ac15a83af25943dd4b8ce0de99ebd6`
- Git blob `03af3d733d870a9cb702dece89c6be67cc71512b`.

Calibration selected:
- Iris: **direct**. Direct and conditional both success `1.0`, mean `0.00713253475s`; exact tie priority selected direct. Fixed success `1.0`, mean `0.864376392375s`.
- Diabetes: **fixed**. Fixed and conditional both success `1.0`; fixed mean `0.42037983975s` versus conditional `0.42062082625s`; direct success `0.0`.

## Independent confirmation and exactly-one simulation

Confirmation raw was measured only after snapshot readback, then persisted/read back before simulation:
- path `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_transfer_confirmation_raw_2026-08-29T0631_JST.jsonl`
- 24 rows
- SHA256 `e71e317dab47694257aa83f70c2977442e928cdee7e40192c64f324deb7d1e23`
- Git blob `536a317d56d7e34fb3e5aa7dfe235caff9688f2b`.

Exactly one preregistered simulation was then executed. Result:
- path `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_transfer_result_2026-08-29T0631_JST.json`
- SHA256 `6a8e5711506c773b030adce6ccc9d72b185bae77442530349f3526c061d4d4fb`
- Git blob `dcf9c3e3edd567fa9b5bc1d33f1dc763e2c6478d`.
- unchanged candidate rule: **PASS**.

Pooled confirmation metrics:
- universal direct: success `0.50`, mean capped time `0.2633122227s`;
- universal fixed: success `1.00`, mean `0.6281226167s`;
- universal conditional: success `1.00`, mean `0.2428615422s`;
- selector: success `1.00`, mean `0.2083485822s`.

Thus the frozen selector matched the best universal-arm success and reduced mean capped time by about `14.21%` versus universal conditional and `66.83%` versus universal fixed, while avoiding the direct arm's 50% pooled failure rate.

Per scenario:
- Iris selected direct: success `1.0`, mean `0.0077196229s`; conditional also success `1.0` but mean rose to `0.0764867704s` because one confirmation direct run exceeded the conditional cap and triggered the expensive alternative; fixed mean `0.8472676919s`.
- Diabetes selected fixed: success `1.0`, mean `0.4089775414s`; conditional success `1.0`, mean `0.4092363140s`; direct success `0.0`.

Every unchanged gate passed: alternative calibration success >=0.80 in both scenarios; two distinct arms selected; selector pooled success >= every universal arm; selector pooled mean <= every universal arm; selected policy non-dominated in each scenario.

## Interpretation and scope

This is the first clean cross-dataset/task transfer evidence for `CAL-LEX-3ARM-v1`. The result supports a narrow mechanism: **a calibration-only empirical-risk selector that includes an explicit no-switch arm can transfer across these two new public scenarios without retuning the meta-rule**. It does not establish broad transfer, optimality, robustness to noisy calibration budgets, or safety under external-effectful evaluators.

A useful failure signal also appeared: conditional switching on Iris was calibration-equivalent to direct but suffered a holdout timing outlier that forced one unnecessary switch; keeping `direct` as a first-class arm avoided that tail cost. Conversely, the Diabetes scenario confirms that direct-only can be categorically wrong while fixed switching is slightly cheaper than conditional when direct is known to fail and its runtime is tiny.

## Frontier / exact next action

Frontier remains nonempty. Exact next action: **freeze `CAL-LEX-3ARM-v1` again without retuning and test calibration-budget stability / selector-choice variance on a third and fourth fresh public workload family, with multiple independent calibration panels chosen before any confirmation measurement.** The falsification target is selector instability: if small calibration panels frequently choose different arms or lose pooled competitiveness, add an uncertainty-aware abstain/default mechanism only in a new preregistered leaf, never by retuning this evidence.

Independent preserved frontier: complete the local-HTTP crash-safe provider acceptance test for optimizer evaluation dispatch, verifying `reconcilable -> recover without duplicate effect` and `neither -> UNKNOWN/fail-closed` at wire-acceptance and response-loss boundaries.

Termination/blocker at this checkpoint: no authoritative-control blocker; sequence 108 is intermediate continuation, not global completion.
