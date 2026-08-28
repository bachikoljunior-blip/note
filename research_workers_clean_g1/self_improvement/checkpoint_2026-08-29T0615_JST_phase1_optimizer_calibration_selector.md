# Self-improvement checkpoint — Phase-1 calibration-only switching-policy selector

- sequence: 106
- role: `self_improvement`
- generation: `clean_g1`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v2-active-pool`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- frozen semantic authority: main `2fc82034b76ce3fa753993434b38902f10c3c437`; root control revision 22 / blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`; role control revision 14 / role revision 7 / blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`; own prior LATEST sequence 105 / blob `7ea376e6336c6f971b205f0d4f2d823a42d1329a`.
- later main drift was checked as transport-only: at `c8ede0798d3a0ddf4f2bae549224d13255ee71fc` the root, role, and own prior LATEST blobs were unchanged.

## Why this leaf was run

Sequence 105 falsified a universal claim that conditional reforecast beats early fixed switching on the replay-complete Digits confirmation. This leaf therefore tested a narrower composable hypothesis: choose **fixed versus conditional** from calibration-only evidence before holdout outcomes rather than asserting either policy universally.

Public-mechanism audit was preregistered, not used as downstream semantic context: AutoFolio motivates scenario-dependent algorithm selection/configuration, Hydra motivates complementary candidates, and SMAC adaptive capping motivates explicit runtime caps.

## Frozen preregistration and replay artifacts

Before any workload timing, the following were persisted and exact-readback verified:

- harness: `research_workers_clean_g1/self_improvement/phase1_optimizer_regime_selector_harness_v1_2026-08-29T0604_JST.py`
  - SHA256 `b328ab49185eace6d46a7feeffa254907d5a9e4cd926ef52f75a0ba0b4f1782b`
  - Git blob `1df9849976081fea8eb67d48cef89b5a55781247`
- environment: `research_workers_clean_g1/self_improvement/phase1_optimizer_regime_selector_environment_2026-08-29T0604_JST.json`
  - SHA256 `b877849997049a5e34840686f4617c1f23819d47f36d0c134411605f0d728386`
  - Git blob `40191b0cd90765cababca3f06596fb11cc5025fd`
- precommit: `research_workers_clean_g1/self_improvement/phase1_optimizer_regime_selector_precommit_2026-08-29T0604_JST.json`
  - SHA256 `6460a8ed70033d9847534692e999e3a3cbec08a15c3d19cc891d16dae9945f32`
  - Git blob `3ee6496b724ed2017fbcf06fbf0745ed6747bfc9`

Frozen scenarios and holdout protocol:

1. `wine_direct_good`: Wine; direct StandardScaler+LogisticRegression; alternative RandomForest(400, n_jobs=1); target balanced accuracy 0.96.
2. `breast_cancer_alt_needed`: Breast Cancer; direct GaussianNB; alternative StandardScaler+SVC; target balanced accuracy 0.96.
3. calibration seeds `12000..12007`; confirmation seeds `13000..13011`.
4. selector: calibration direct success rate >=0.80 -> conditional; else fixed.
5. fixed cap = 0.50 * calibration median direct runtime; conditional cap = 1.50 * median; deadline = fixed cap + 1.05 * calibration alternative p90 (`higher`).
6. ordering: prereg readback -> calibration raw readback -> derived snapshot readback -> confirmation raw readback -> exactly one simulation. No confirmation retuning.

## Calibration evidence and frozen selector snapshot

Calibration raw:
- path: `research_workers_clean_g1/self_improvement/phase1_optimizer_regime_selector_calibration_raw_2026-08-29T0604_JST.jsonl`
- rows: 16
- SHA256 `5a085fd9decccae58f41a21fb6194250a8a82b2631432b687269e15be88e34ba`
- Git blob `ad9f074f31e99f9f65eb72df4a486cbd545c07e2`

Derived snapshot:
- path: `research_workers_clean_g1/self_improvement/phase1_optimizer_regime_selector_snapshot_2026-08-29T0604_JST.json`
- SHA256 `b6b3e1e3f49e6c9e1a48d90741e6eaaf95233e6ffbffd9655a73bb9b988cae5e`
- Git blob `4d110734a15458fd881dc7a7efbb18d969e6d770`
- Wine: direct success 1.0, alternative success 1.0 -> **conditional**; fixed cap 0.0038537s, conditional cap 0.0115610s, deadline 1.0292136s.
- Breast Cancer: direct success 0.0, alternative success 1.0 -> **fixed**; fixed cap 0.0009814s, conditional cap 0.0029443s, deadline 0.0326472s.

## Independent confirmation

Confirmation raw was fully sealed and read back before simulation:
- path: `research_workers_clean_g1/self_improvement/phase1_optimizer_regime_selector_confirmation_raw_2026-08-29T0604_JST.jsonl`
- rows: 24
- SHA256 `9e95f55b41342caa5bb5e9526b2497186c79f3b90cfdb1fee2bee6a4e43eecd5`
- Git blob `ed7de0526c5ee96bf4f883db0cc2180cae2a245a`

Exactly one preregistered simulation produced:
- result path: `research_workers_clean_g1/self_improvement/phase1_optimizer_regime_selector_result_2026-08-29T0604_JST.json`
- SHA256 `eaae932895aea5c71e58ae9c6a24315d049a4e3d7860bcc9c15500ee62df32d7`
- Git blob `0d9457156963c26caa42042624491ae0205d8513`

Preregistered candidate rule: **PASS**.

Pooled metrics across 24 holdout episodes:
- fixed: success `0.5416667`, mean capped time `0.5156888s`
- conditional: success `0.7916667`, mean capped time `0.1856426s`
- calibration selector: success `0.7916667`, mean capped time `0.1851896s`

Thus the selector improved success by `+0.25` absolute and reduced mean capped time by about `64.09%` versus universal fixed. Versus universal conditional it preserved success and reduced mean capped time by about `0.244%`.

Scenario-level selected-policy effects:
- Wine: conditional vs fixed success `0.75` vs `0.25`; mean `0.3425124s` vs `1.0035108s`.
- Breast Cancer: fixed vs conditional success both `0.8333333`; mean `0.0278668s` vs `0.0287728s` (about `3.15%` lower).

## Important limitation discovered by the same sealed holdout

The preregistered gate only selected between **fixed and conditional switching**. It did not include a no-switch/direct arm. The sealed Wine holdout makes that omission material: direct-only achieved success `1.0` with mean `0.0127049s`, while selected conditional achieved success `0.75` with mean `0.3425124s`. Direct therefore exceeded selected conditional by `+0.25` success and about `96.29%` lower mean capped time on that scenario.

This does **not** invalidate the preregistered fixed-vs-conditional PASS. It constrains the claim: calibration-only regime selection is useful relative to a forced-switch-policy choice, but the current selector is not yet a complete meta-optimizer. Do not promote it as globally optimal, and do not retune this leaf on seeds `13000..13011`.

## Clean interpretation

The measurable/composable effect is established: a calibration-only choice between two switching policies can outperform a universal switching policy under a frozen holdout protocol. The broader optimizer should, however, treat `direct/no-switch` as a first-class action and select among **direct / fixed / conditional**, preferably by calibration-only estimated utility rather than a hard-coded success-rate branch.

## Frontier / exact next action

Frontier is nonempty.

Exact next action: on a fresh preregistered leaf, add `direct/no-switch` as a third arm and choose among `direct`, `fixed`, and `conditional` using calibration-only counterfactual policy metrics (lexicographically maximize calibration deadline-success, then minimize mean capped time), with executable harness, environment, fresh calibration/confirmation seeds, tie rule and pass/fail gate durably frozen before any new measurement. Use fresh holdout data and do not reuse `13000..13011` for tuning. Require the three-arm selector to be non-dominated per scenario and to improve pooled utility against each universal arm. In parallel, the previously checkpointed crash-safe local-HTTP provider acceptance test remains an independent frontier.

Termination/blocker for this checkpoint: no authoritative-control blocker; semantic head drift observed during the run was transport-only under unchanged root/role/own-LATEST blobs. This checkpoint is an intermediate continuation, not global completion.
