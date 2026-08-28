# Self-improvement checkpoint — Phase-1 three-arm calibration-only meta-selector

- sequence: 107
- role: `self_improvement`
- generation: `clean_g1`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v2-active-pool`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- source continuation: sequence 106, which established a fixed-vs-conditional calibration selector but exposed a missing direct/no-switch arm.
- frozen leaf authority: main `30220cad6e601df2e1432f9a73138762ec152936`; root control revision 22/blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`; role control revision 14 / role revision 7 / blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`; own LATEST sequence 106 / blob `7127eac867ee935fc1a81db5235937051482cc9a`.

## Hypothesis and preregistration

This is a **fresh leaf**, not a retune of sequence 106. Sequence-106 holdout seeds `13000..13011` were excluded from all calibration/tuning here. Fresh calibration seeds were `14000..14007`; fresh confirmation seeds were `15000..15011`.

Candidate `CAL-LEX-3ARM-v1` treats `direct/no-switch`, `fixed`, and `conditional` as first-class arms. Per scenario, calibration-only counterfactual policy metrics determine the arm: lexicographically maximize deadline-success rate, then minimize mean capped time; exact tie priority is `direct`, then `fixed`, then `conditional`. Fixed/conditional cap construction remained unchanged from the prior leaf.

Before any workload timing, the following were persisted and read back:
- harness `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_selector_harness_v1_2026-08-29T0617_JST.py`, SHA256 `086d041e59a038906962c3e93e939e522c8aadea659bab3396ee77c570a39a11`, Git blob `60c5ed5ca3498107e26f024a13973b665c9a9933`.
- environment `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_selector_environment_2026-08-29T0617_JST.json`, SHA256 `b90a757635e985ee467892653b79d21b498e148c222b7f2bd5ee3278b6b86320`, Git blob `b5c12be041e3335560a1c18e60c37283c41dcd1c`.
- precommit `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_selector_precommit_2026-08-29T0617_JST.json`, authoritative remote Git blob `adbf540b549bb5e252e092674fae5ead0522535b`, full readback before timing.

The preregistered confirmation gate required: alternative calibration success >=0.80 in every scenario; >=2 distinct selected arms; selected arm non-dominated against every other arm per scenario; pooled selector success >= every universal arm; pooled selector mean capped time <= every universal arm.

## Calibration and frozen selector snapshot

Calibration raw:
- path `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_selector_calibration_raw_2026-08-29T0617_JST.jsonl`
- 16 rows
- SHA256 `09931cfe2f8c09af2665a3a909b4bdbe8c4a429e60f035aa9a2cf40c0b87a85e`
- Git blob `52809903c088871778e6b16fa4f859948d179380`

Derived snapshot:
- path `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_selector_snapshot_2026-08-29T0617_JST.json`
- SHA256 `299ef60788e3f7b2cf13e5de5d93227398c4829c5f3b4f2f7bc212bdd22c87e5`
- Git blob `65eb8747a0df750ff112117327aa25a87708417b`

Calibration chose:
- Wine: **direct**. Direct and conditional both had success 1.0 and identical mean `0.0078977s` because every direct calibration run finished before the conditional cap; exact tie priority therefore chose direct. Fixed also had success 1.0 but mean `0.9113867s`.
- Breast Cancer: **fixed**. Fixed and conditional both had success 1.0; fixed mean `0.0281680s` versus conditional `0.0292477s`; direct success was 0.

The snapshot was persisted/read back before any confirmation seed was measured.

## Independent confirmation

Confirmation raw:
- path `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_selector_confirmation_raw_2026-08-29T0617_JST.jsonl`
- 24 rows
- SHA256 `97b9dff53ae5b3f9a48abfb643844f72d6325eccbd6b93708a962d654bb19d1a`
- Git blob `afccce60424867bb0872609e8ad8a827ca51a66e`

All confirmation rows were persisted/read back before the **single** preregistered simulation.

Result:
- path `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_selector_result_2026-08-29T0617_JST.json`
- SHA256 `070022af69b97266137d67ba28ee049263320ab83bb91e13b2b30918a5b3bf40`
- Git blob `0a5d10e283e67953ac4a1a52ac0aa17bdbe105f4`
- preregistered candidate rule: **PASS**.

Pooled holdout metrics:
- direct universal: success `0.5000000`, mean capped time `0.0217929s`
- fixed universal: success `0.9166667`, mean capped time `0.4638054s`
- conditional universal: success `0.8750000`, mean capped time `0.0191134s`
- three-arm selector: success `0.9166667`, mean capped time `0.0186072s`

Therefore the three-arm selector:
- versus universal direct: `+0.4166667` absolute success and about `14.62%` lower mean capped time;
- versus universal fixed: equal success and about `95.99%` lower mean capped time;
- versus universal conditional: `+0.0416667` absolute success and about `2.65%` lower mean capped time.

Scenario holdout:
- Wine selected direct: success `1.0`, mean `0.0078041s`; conditional was exactly equal because no holdout direct run crossed the conditional cap; fixed success `1.0` but mean `0.8982005s`.
- Breast Cancer selected fixed: success `0.8333333`, mean `0.0294103s`; conditional success `0.75`, mean `0.0304227s`; direct success `0.0`.

## Interpretation

This repairs the specific incompleteness exposed by sequence 106: a calibration-only meta-optimizer should be allowed to choose **not to switch**. Under a fresh preregistered confirmation, the simple calibration empirical-risk selector over `direct/fixed/conditional` was non-dominated per scenario and dominated every universal arm on the preregistered pooled gates.

The claim remains deliberately narrow. The scenario/model families were inherited from the leaf that motivated the repair, so this is an independent fresh-seed confirmation of the correction, **not yet cross-dataset transfer evidence**. Confirmation seeds `15000..15011` are now consumed and must never be used to tune this candidate.

## Frontier / exact next action

Frontier is nonempty.

Exact next action: freeze `CAL-LEX-3ARM-v1` **without changing its selector rule, cap multipliers, tie priority or pass logic**, and preregister a transfer test on at least one public non-synthetic dataset/scenario not used in constructing this leaf (exclude Wine, Breast Cancer, and the earlier Digits confirmation family for the first transfer). Use fresh calibration/confirmation seeds and persist/readback the executable workload adapter plus raw calibration -> frozen selector snapshot -> raw confirmation -> exactly-one simulation. Primary transfer question: does the unchanged calibration-only three-arm selector remain non-dominated and pooled-competitive when scenario identity/model family changes? Independently preserve the local-HTTP crash-safe provider acceptance frontier (`reconcilable -> recover`, `neither -> UNKNOWN/fail-closed`).

Termination/blocker: no authoritative-control blocker at this checkpoint. This is an intermediate continuation, not global completion.
