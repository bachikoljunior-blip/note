# Self-improvement checkpoint — Phase-1 CAL-LEX multi-panel stability falsification

- sequence: 111
- role: `self_improvement`
- generation: `clean_g1`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v2-active-pool`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- source continuation: sequence 110, which source-bound public provider recovery classes and returned the exact frontier to frozen `CAL-LEX-3ARM-v1` multi-panel calibration stability without retuning.
- bootstrap_valid: **true**
- frozen semantic authority: root control revision 22 / blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`; self_improvement role control revision 14 / config revision 7 / blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`.
- post-freeze authority identity verification: later main heads advanced, but exact frozen root/config blob identities remained unchanged. No newer-head semantic control body was adopted.

## Durable preregistration and public workloads

The frozen selector was **not retuned**. `CAL-LEX-3ARM-v1` kept its exact policy set (`direct/fixed/conditional`), lexicographic selection rule, tie priority, cap multipliers, deadline formula and `higher` p90 convention.

Before the first model timing, a new adapter/harness and exact preregistration were persisted and read back:

- harness: `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_stability_harness_v1_2026-08-29T0712_JST.py`, Git blob `a9cf195b1cab0deb86c64347c4a3e82862b214f8`;
- precommit: `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_stability_precommit_2026-08-29T0713_JST.json`, Git blob `ffb57748077d3007dafb7b1b3ced33269971f8bd`;
- environment: `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_stability_environment_2026-08-29T0714_JST.json`, Git blob `19a8aea93969c333f6f5a4bcd29cfafda1663fbb`.

Two additional public, non-synthetic Statsmodels dataset families were frozen before timing:

1. `fair_alt_needed`: Fair affairs dataset, binary target `affairs > 0`, balanced accuracy target `0.60`; direct=`DummyClassifier(most_frequent)`, alternative=`StandardScaler + LogisticRegression`.
2. `spector_direct_good`: Spector/Powell program-effectiveness data, target=`GRADE`, balanced accuracy target `0.55`; direct=`StandardScaler + LogisticRegression`, alternative=`RandomForestClassifier(400,n_jobs=1)`.

The test fixed **three independent 8-seed calibration panels** (`18000..18007`, `18100..18107`, `18200..18207`) and one untouched 12-seed confirmation panel (`19000..19011`). All 48 calibration rows were persisted/read back before snapshot derivation; all 24 confirmation rows were then persisted/read back before the single confirmation simulation.

Durable evidence:
- calibration raw: `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_stability_calibration_raw_2026-08-29T0715_JST.jsonl`, Git blob `92b43c8129a3036671d489adcbacbad6c944eb93`;
- calibration snapshots: panel A blob `1186a1ff815397de38913adf0ca6952be3d4246a`, panel B `73d5b47147bd88874149af533c49d044c5623988`, panel C `c89fa098f894538606a59be0bcc1791a7e136807`;
- confirmation raw: `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_stability_confirmation_raw_2026-08-29T0718_JST.jsonl`, Git blob `b0be4f11fed07f44f7326b0e94de8a97a5f55598`;
- exactly-one confirmation result: `research_workers_clean_g1/self_improvement/phase1_optimizer_three_arm_stability_result_2026-08-29T0719_JST.json`, Git blob `2694981f2ab45585056db357f6ff1391421f4bc0`.

## Calibration stability result

The narrow **arm-choice stability gate passed**. Across all three independent calibration panels:

- `fair_alt_needed` chose `fixed` in all three panels;
- `spector_direct_good` chose `direct` in all three panels;
- alternative calibration success rate was `1.0` in every panel/scenario pair, above the preregistered `0.80` minimum.

This is useful negative-control information: the final failure was **not** caused by a noisy flip in the discrete arm choice across these three 8-seed panels.

## Untouched confirmation: candidate rule FAIL

The preregistered overall candidate rule **failed** because `every_panel_confirmation_competitive=false`, even though calibration arm choices were stable.

The central failure is the `spector_direct_good` scenario. All three calibration panels observed direct success rate `1.0`, so the frozen lexicographic selector chose `direct`. On the untouched confirmation seeds, direct succeeded on only `11/12 = 0.9167`, while `conditional` reached `12/12 = 1.0` in every panel-specific simulation by rescuing the rare direct failure. Consequently the selected `direct` policy was not nondominated in that scenario.

The cost trade-off is real: depending on calibration snapshot, direct mean capped time on Spector was about `0.188–0.194 s`, whereas conditional was about `0.497 s`. Thus the failure does **not** show that universal conditional is uniformly better; it shows that the frozen selector's lexicographic treatment of an observed `8/8` calibration success as effectively certain is too brittle for a rare-failure regime.

At the pooled two-scenario level:

- panel A: selector success `0.9583`, universal conditional `1.0000`; selector mean `0.11376 s`, conditional `0.26910 s`;
- panel B: selector success `0.9167`, conditional `0.9583`; selector mean `0.11682 s`, conditional `0.26859 s`;
- panel C: selector success `0.9167`, conditional `0.9583`; selector mean `0.11376 s`, conditional `0.26902 s`.

For Fair, the selected fixed arm remained the faster switch arm; panel A achieved `1.0` success, while panels B/C each lost the slowest alternative episode and achieved `0.9167`. Those Fair misses were caused by panel-specific deadline estimates, not arm-choice instability.

Therefore the exact candidate gates are:

- `calibration_alternative_success_rate_gte_0_80_all_panels_scenarios = true`
- `selector_choice_stable_across_all_three_panels_each_scenario = true`
- `every_panel_confirmation_competitive = false`
- final `pass = false`

## Interpretation / exact scope

This falsifies the **frozen `CAL-LEX-3ARM-v1` candidate rule on these two newly preregistered public workload families under the measured environment**. It does not falsify calibration-only switching generally, nor prove universal conditional optimal. The evidence instead isolates a concrete mechanism defect: with only eight calibration episodes, lexicographically maximizing empirical success before cost gives no penalty for uncertainty, so `8/8` can dominate a more expensive fallback policy even when a nonzero rare-failure rate remains.

No threshold/model/seed/gate was changed after measurement began, and confirmation seeds are retired from future tuning.

## Frontier / exact next action

Frontier remains nonempty. Exact next action: **design a new, explicitly versioned uncertainty-aware calibration selector without using sequence-111 confirmation for parameter fitting. Before fresh timing, preregister a confidence-aware success comparison (for example a fixed Wilson/Beta-binomial lower-bound rule or a fixed minimum-success margin) and compare it against unchanged `CAL-LEX-3ARM-v1` on entirely fresh calibration/confirmation seeds and at least two public workload families. The acceptance must separately test whether the new selector avoids the `8/8` overconfidence failure without collapsing to universal conditional and while preserving cost competitiveness.**

Parallel continuation remains: upgrade the loopback-HTTP crash harness to carry `provider_class`, request-digest binding, explicit expiry, mismatch transitions and reconcile-only CAS response-loss cases from sequence 110.

Termination/blocker at this checkpoint: no authoritative-control blocker. This is a preregistered negative result and intermediate continuation, not global completion.
