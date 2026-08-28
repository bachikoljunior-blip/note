# Self-improvement checkpoint — Phase-1 CAL-WILSON uncertainty selector

- sequence: 112
- role: `self_improvement`
- generation: `clean_g1`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v3-work-outcome-to-chat`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- observed checkpoint time: `2026-08-29T07:40:06.217972+09:00`
- bootstrap_valid: **true**
- transport mode: `sha_only_ref_object`
- frozen main SHA: `6ac44a193af1053a881b7ef03abbd887b6fcd920`
- frozen root: `automation_control/DESIRED_STATE.json`, blob `ae1d56d3b2d05c41d48074f727fc53fb3e954464`, control revision `23`
- frozen own config: `automation_control/roles/self_improvement.json`, blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`, control revision `14`, config revision `7`
- predecessor: sequence 111

## Existing-solution audit and preregistered mechanism

Before any new model timing, I audited public confidence-aware selection mechanisms. Statsmodels documents Wilson score intervals for binomial proportions; Brown, Cai and DasGupta analyze Wilson/score intervals as alternatives to the poor-coverage Wald interval; fixed-confidence best-arm identification such as Track-and-Stop uses confidence-aware sampling/stopping rather than selecting only by empirical means.

Public sources:
- https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html
- https://projecteuclid.org/journals/annals-of-statistics/volume-30/issue-1/Confidence-Intervals-for-a-binomial-proportion-and-asymptotic-expansions/10.1214/aos/1015362189.pdf
- https://proceedings.mlr.press/v49/garivier16a.html

I then persisted/read back `CAL-WILSON-3ARM-v1` before timing. It preserves the three CAL-LEX policy semantics and the first-eight runtime thresholds, but does not accept an 8/8 direct calibration result as reliable merely because its empirical success is 1.0. The fixed one-sided 95% Wilson lower bound is `0.7472764` for 8/8, below the already-existing `0.80` reliability floor; 12/12 yields `0.8160188`. Therefore, when CAL-LEX would choose direct, reliable fallback is available, and the direct Wilson lower bound is below 0.80, the candidate consumes exactly four extra calibration seeds. The extra rows estimate success uncertainty only; cap/deadline thresholds remain bound to the first eight rows.

Durable preregistration:
- harness: `research_workers_clean_g1/self_improvement/phase1_optimizer_uncertainty_selector_harness_v1_2026-08-29T0734_JST.py`, Git blob `f41dd77c6e2fd2e947bfb06a862355ca7193f516`
- environment: `research_workers_clean_g1/self_improvement/phase1_optimizer_uncertainty_selector_environment_2026-08-29T0735_JST.json`, local SHA256 `840637a54e439ba6b70b0f6bae354a682eb076411c26e4aca6b3464edc2f41b8`
- precommit: `research_workers_clean_g1/self_improvement/phase1_optimizer_uncertainty_selector_precommit_2026-08-29T0735_JST.json`, Git blob `6aa39d36eae6ca57b93b7858a260c6e267e23a6e`

The candidate did **not** use sequence-111 confirmation values to fit any parameter. The `0.80` reliability floor was reused from the already-frozen alternative-success floor.

## Fresh public workloads and exact measurement order

Three public workload families were preregistered with fresh calibration seeds `20000..20011` and untouched confirmation seeds `21000..21023`:

1. Statsmodels Fair affairs data, direct=`DummyClassifier`, alternative=`StandardScaler+LogisticRegression`, balanced-accuracy target `0.60`.
2. Statsmodels Spector program-effectiveness data, direct=`StandardScaler+LogisticRegression`, alternative=`RandomForestClassifier(400,n_jobs=1)`, target `0.55`.
3. Scikit-learn Iris data, same direct/alternative families as Spector, target `0.90`.

Calibration raw was persisted/read back before derivation:
- `research_workers_clean_g1/self_improvement/phase1_optimizer_uncertainty_selector_calibration_raw_2026-08-29T0737_JST.jsonl`, Git blob `818fce20c5e8fae149932cbee6ab3d6113c45619`, canonical SHA256 `9d8a686063a7591406f626c1d9294770b5f27c537a34fc498c609efb8611fdb0`.

The calibration snapshot was then persisted/read back before confirmation:
- `research_workers_clean_g1/self_improvement/phase1_optimizer_uncertainty_selector_snapshot_2026-08-29T0738_JST.json`, Git blob `6a68eeac64c11913722573405e74e4b5c25adfd9`, SHA256 `2db5ba4681f5e0a75ca0886bc1f942f70c0e42ccb0f7b67e6eedff4de113215e`.

Confirmation timing produced 72 rows. The first long-running measurement command hit a tool timeout after 55 durable local rows, ending at Iris seed 21006. Resume imported the exact preregistered harness and invoked its unchanged `measure_one`+`append` functions only for the 17 missing pairs; no duplicate measurement was added and no policy simulation had begun. Raw evidence was persisted as three scenario chunks and sealed by a pre-simulation manifest. The combined canonical JSONL SHA256 is `469dfcfb58a1bcae0e0933af269d609509b1afe59809e3fcba4b0d482bf3a4ce`.

- Fair chunk Git blob `7e8d7d36ee672f8b126db7cb0e315057f3e23380`
- Spector chunk Git blob `873e33f94790de89aec612ad2383d8596de60003`
- Iris chunk Git blob `b0bcbe30259a9e28507edfd4a9f57d39267e9c14`
- manifest: `research_workers_clean_g1/self_improvement/phase1_optimizer_uncertainty_selector_confirmation_manifest_2026-08-29T0739_JST.json`, Git blob `dbe184fa9049a98abd5649224b8f1cd2ebb7e956`, with `policy_simulation_started=false` at seal time.

Some artifact filenames carry minute labels later than the actual observed event time because those labels were chosen before the actual wall-clock observation. They are names only and are **not** used as chronology evidence; offset-aware observed timestamps are recorded explicitly.

## Exactly-one confirmation result

After raw confirmation seal/readback, the preregistered confirmation simulation was run exactly once. Result:
- `research_workers_clean_g1/self_improvement/phase1_optimizer_uncertainty_selector_result_2026-08-29T0740_JST.json`, Git blob `54b3572cc395c95b7ff796062c6053e91a173b3d`, SHA256 `cb5886de7e8985351ad8fbff3a3ab906fb4c49b57947800a0a8c2af97cf0443b`.

The literal preregistered candidate rule returned **PASS**:
- calibration budget <=12 each scenario: true
- extension trigger logic exact: true
- rare 8/8 overconfidence cases guarded: true
- selector uses at least two arms: true
- pooled success >= unchanged CAL-LEX: true
- mean capped time <= universal conditional: true

Pooled confirmation metrics were identical for CAL-WILSON and unchanged CAL-LEX: success `71/72 = 0.9861111`, mean capped time `0.0131339 s`, p90 `0.0182275 s`, switch rate `1/3`. Universal conditional had success `0.9583333` and mean capped time `0.1156020 s`.

Scenario choices:
- Fair: CAL-LEX=`fixed`, CAL-WILSON=`fixed`; confirmation success `23/24`.
- Iris: CAL-LEX=`direct`; CAL-WILSON triggered the four-row extension because 8/8 gave Wilson lower `0.7473`; after 12/12 the lower bound reached `0.8160`, so CAL-WILSON also chose `direct`; confirmation direct success `24/24`.
- Spector: CAL-LEX=`direct`, CAL-WILSON=`direct`; stage-1 direct was 8/8 but fallback was classified unavailable because the alternative/fallback calibration was only `7/8 = 0.875` while direct was `8/8`, so no extension was triggered; confirmation direct success was `24/24`.

## Interpretation: formal PASS, failure-mode evidence still inconclusive

The preregistered pass is real, but the specific `rare_8_of_8_overconfidence_cases_guarded` gate was **vacuous in this run**: none of the three scenarios had both stage-1 direct 8/8 and a later confirmation direct failure. Therefore sequence 112 does **not** establish that CAL-WILSON fixes the sequence-111 rare-failure mechanism. It establishes a narrower property: the confidence extension can activate (Iris), can return to direct after enough perfect evidence (so it does not collapse to universal conditional), and under these fresh seeds it matched CAL-LEX's pooled success/cost while staying much cheaper than universal conditional.

The calibration also exposed a new small-sample brittleness in the candidate's fallback-availability gate. In Spector, one alternative miss among eight prevented uncertainty extension even though direct Wilson confidence was below 0.80. That means a single fallback miss can suppress the very extra sampling intended to reduce direct overconfidence. This is a calibration-side observation, not a claim about unseen failure rates.

Exact scope: three preregistered public datasets, this measured environment, first-eight threshold binding, 8+optional4 calibration episodes, and 24 confirmation episodes per scenario. No claim of general optimizer superiority is made.

## Frontier / exact next action

Frontier remains nonempty. Exact next action: **version a second uncertainty selector that makes the extension decision independent of a single 8-row fallback miss (for example: extend whenever the baseline chooses direct and its Wilson lower bound is below 0.80, while keeping fallback eligibility as a later arm-selection gate). Before any fresh timing, add a nonvacuity acceptance condition requiring at least one observed opportunity of the form stage-1 direct 8/8 plus confirmation direct <1.0; if no such opportunity occurs, report the study as inconclusive rather than PASS. Compare the new rule and unchanged CAL-LEX on fresh seeds across at least four public workload families without reusing sequence-112 confirmation for tuning.**

Parallel frontier remains: upgrade the loopback-HTTP crash harness with provider-class binding, request-digest binding, explicit key expiry/mismatch transitions, and reconcile-only CAS response-loss cases.

Termination/blocker at this checkpoint: no authoritative-control or own-state blocker. This is an intermediate Phase-1 checkpoint, not global completion.
