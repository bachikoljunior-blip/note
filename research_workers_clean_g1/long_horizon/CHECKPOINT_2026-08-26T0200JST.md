# Long Horizon external research — clean_g1 checkpoint — 2026-08-26 02:00 JST

## Boundary / provenance
- Generation: `clean_g1`.
- Worker: `long_horizon`.
- Effective repository control read first: `automation_control/DESIRED_STATE.json`, control_revision 5, role `long_horizon`, config_revision 3, enabled_desired=true, control blob `016cc4eed3b34413a15fdcc1f5303286b56061fd`.
- Semantic continuation was limited to this worker's own clean namespace, public sources, and own sanitized feedback.
- Own sanitized feedback `research_feedback_clean_g1/long_horizon/FEEDBACK.json` was read and followed. No shared `EXECUTION_LEDGER.json`, no other-role receipt, no O/O-derived state, no other worker, no comparator/integrator/index/feed, and no legacy/pre-independence research was used as semantic context.
- `LATEST.json` / `LATEST.md` were absent, so repository chronology selected the newest source-qualified own checkpoint `CHECKPOINT_2026-08-26T0100JST.md` (blob `91df93a781c6fe0e44baf3fa1503a8e57156027d`) as continuation authority. Older `STATE.md` was not allowed to override it.

## Search target this run
Highest-priority target remained a matched or factorial experiment that separates **causal fault localization** from **historical temporal rewind target selection**, while holding alarms, candidate checkpoints, restore/replay mechanics, model, and compute budget fixed.

No primary study located in this run cleanly isolates only the historical rewind-target rule. This remains an explicit research gap. Two adjacent controls did produce strong new evidence: (A) when iterative repair should stop, and (B) monitoring-guided rollback that derives a target from detector history but remains component-confounded. A third source strengthens safe-cut/commit-boundary evidence for durable effects.

## New primary-source finding A — VRR-Stop: repair stopping should compare expected fix benefit against damage risk
Primary: `Verify, Repair, Repeat, or Stop? Robust Stopping for Noisy Verify-Repair Loops in LLM Agents`, arXiv:2607.17641v1, 2026-07-20, https://arxiv.org/abs/2607.17641 .

### Mechanism
The paper explicitly models both noisy verification and non-monotone repair:
- verifier false acceptance `rho0`;
- verifier false rejection `rho1`;
- repair probability `alpha = P(invalid -> valid | repair)`;
- damage probability `beta = P(valid -> invalid | repair)`.

For posterior current-plan validity `b_k`, one additional repair has expected marginal gain
`G_k = (1-b_k) alpha - b_k beta`.
With zero extra-cost threshold, the repair/commit boundary is
`b* = alpha/(alpha+beta)`.
Thus repair should continue only while expected error-fixing benefit exceeds expected damage to already-correct state. This is a direct formalization of the repair-stopping control missing from fixed-round loops.

### End-to-end stress result
GSM8K / Qwen2.5-3B prompt-mismatch stress, `N=500`, `M=8`, `Kmax=5`:
- No repair: true validity 0.700 [0.658, 0.740], avg repairs 0.00.
- Majority stopping: 0.690 [0.648, 0.730], avg 0.92.
- Confidence stop 0.85: 0.562 [0.518, 0.604], avg 1.92.
- Fixed repair K=5: 0.116 [0.088, 0.144], avg 5.00.
- VRR-Stop: 0.722 [0.682, 0.760], avg 0.72.
- Ground-truth-parameter reference: 0.694 [0.652, 0.734], avg 0.89.

VRR-Stop vs fixed-five repair: +60.6 percentage points, 95% CI [+56.0,+65.0], McNemar `p < 2e-85`. It also beats majority stopping by +3.2 pp (`p < 2e-4`). The +2.2 pp difference versus no-repair has a CI crossing zero, so do not claim a confirmed superiority over no-repair in this cell.

### Direct evidence that repair can damage correct state
On the same N=500 stress traces:
- 55% of instances experience a correct plan being repaired into an incorrect one.
- 24% of those damaging repairs nevertheless win majority verifier acceptance.

Fixed-budget iterative-feedback deployments on the same stress trajectory batches end at 0.095 / 0.080 for Reflexion / Self-Refine, while VRR-Stop on those batches reaches 0.740 / 0.710. The paper explicitly treats this as an audit of the fixed-budget deployment mode, not a reproduction claim for the original training methods.

### Stopping calibration itself can fail
Stopping-sign reliability depends jointly on verifier discrimination `J = 1-rho0-rho1` and decision margin, not simply parameter-estimation error magnitude.
- Controlled flip probability: 0.183 when `J <= .15` and decision margin <= .10, versus 0.014 when `J >= .4` or margin >= .30 (~13x lower).
- Llama-3-8B verifier has `J=0.03`; calibrated stopping collapses from a ground-truth-parameter reference 0.803 to 0.223 (-58.0 pp), while the estimation-free guarded fallback reaches 0.793.
- Qwen-7B stress: no repair 0.875, fixed-five 0.075, VRR-Stop 0.875 — the learned policy correctly chooses zero repairs on average.

### Scope / limitations
- Binary plan-validity abstraction and locally stationary transition model.
- Myopic one-step expected gain rather than multi-step optimal stopping.
- Main strongest quantitative evidence is GSM8K/Qwen stress plus additional model/domain replications; it is not a generic long-horizon environment recovery benchmark.
- This solves **how long to keep repairing**, not **which historical checkpoint to rewind to**.

### Design implication
A recovery controller should not allocate repair/retry budget by fixed iteration count. It should estimate the expected marginal value of one more repair as `fix probability × invalid-state belief - damage probability × valid-state belief`, include cost/risk margins, and fail conservatively when the sign of that gain is not identifiable.

## New primary-source finding B — MGT-B: detector-reset history can define a rollback target, but the evidence is composite and statistically uncertain
Primary: `CUSUM-Shaped Inference-Time Monitoring and Targeted Re-Decoding for Quantized Small Language Model Reasoning`, arXiv:2607.20129v1, 2026-07-22, https://arxiv.org/abs/2607.20129 .

### Mechanism
MGT-B monitors one autoregressive trajectory with overlapping-window uncertainty, repetition and local-change features. A CUSUM-shaped statistic accumulates evidence. On alarm, the controller:
1. scans backward to the most recent nonpositive detector statistic;
2. maps that reset point to a token position;
3. extends rollback earlier by a fixed 64-token margin;
4. truncates tokens and KV cache and rebuilds monitor/repetition state;
5. re-decodes with lower temperature, repetition penalty, and suspect n-gram blocking.

This is a concrete **change-point-style temporal rollback selector derived from detector history**, but it is not a clean target-selector experiment because trigger, rollback localization, state restoration and re-decoding policy are coupled.

### Chronology-aware primary result
To reduce threshold-selection contamination, the paper removes IDs observed before/manual-threshold selection and retains the first later seed-matched pair, yielding 240 pairs:
- vanilla: 82/240 = 34.17%;
- MGT-B: 88/240 = 36.67%;
- delta +2.50 pp;
- 13 corrections / 7 regressions;
- exact McNemar `p=0.2632`;
- paired bootstrap 95% interval [-1.25,+6.25] pp.

Direction is positive but statistically uncertain; do not report this as confirmed improvement.

### Exploratory broader set and controls
Historical-coverage set, 467 pairs:
- vanilla 146/467 = 31.26%;
- MGT-B 167/467 = 35.76%; +4.50 pp, nominal `p=0.000753`;
- however 200 seed-1 IDs were available before/during manual threshold selection, so this is explicitly exploratory rather than independent confirmation.
- all 316 no-alarm outputs are identical to vanilla;
- 151 alarmed trajectories contain 29 corrections / 8 regressions.

Budget-relaxed intervention controls on that same exploratory set receive slightly larger permitted per-item budgets than MGT-B. Reported aggregate accuracies:
- vanilla 31.26%;
- MGT-B 35.76%;
- random rollback 31.69%;
- periodic rollback 26.55%;
- full restart 24.63%;
- generic self-correction 30.19%.

This suggests backtracking alone or uninformed schedules do not explain the exploratory gain, but the paper explicitly warns that the policies differ in trigger, rollback placement and subsequent decoding. Therefore this does **not** isolate a superior historical target-selection rule.

### Scope / limitations
- Central evidence is one 4-bit 1.5B distilled reasoner on MATH-500.
- The empirical detector is CUSUM-shaped, not proven anytime-valid or a certified e-detector.
- The chronology audit is retrospectively reconstructed rather than preregistered.
- Components remain coupled and complete component attribution is absent.

### Design implication
Detector reset history is a plausible information source for temporal target selection, analogous to change-point localization. It should enter the future selector-factorial experiment as one candidate rule, but must be compared under identical alarms, checkpoint candidates, restoration mechanics and re-decoding policy before claiming superiority.

## New primary-source finding C — commit-time authorization: safe recovery/cut must be evaluated at the durable-effect boundary, not only by visible task completion
Primary: `Temporary Authority, Permanent Effects: Commit-Time Authorization for LLM Agents`, arXiv:2607.10487v1, 2026-07-11, https://arxiv.org/abs/2607.10487 .

### Controlled invalidation evidence
The study preserves the requested task/payload shape while invalidating the authority relation before durability across browser, tool/state and multi-agent workflows.
Primary 54-task / 270-run matrix:
- endpoint success 262/270;
- authorized completions only 55/270;
- unauthorized durable commits 207/270;
- safe non-completions 8/270;
- all 54/54 clean controls authorized.

Among invalidating rows, visible endpoint success therefore often survives after the path that authorized the durable effect has become stale, misbound, reordered, cancelled or superseded.

Fixed matched mechanism comparison holds endpoint success constant: all 18/18 clean controls and 18/18 paired perturbations reach the endpoint; controls are authorized 18/18 while perturbations are unauthorized 18/18 (exact sign test `p=7.6e-6`). Authority-preserving benign timing/presentation negative controls have 0/54 unauthorized commits.

### Commit boundary
A protected durable effect is authorized only if four conditions still hold at commit:
1. witness freshness;
2. causal priority / predecessor completion;
3. effect binding to the same concrete target/version/branch;
4. live commit eligibility.

The runtime must either refresh/rebind/replan or refuse when those conditions fail. A visible successful endpoint is not proof that a durable effect is still entitled to commit.

### Mitigation trade-off
On calibrated drift probes, prompt-only caution often preserves visible success while leaving unauthorized commits. Version pinning, replanning or commit gating can reduce unauthorized commit to zero but often convert the unsafe half of matched perturbations into conservative aborts, reducing visible success to ~50% in those probe cells.

CommitGuard enforcement:
- matched replay: 18/18 shadow perturbed rows unauthorized -> 18/18 boundary perturbed rows guarded abort;
- fixed 18-task enforcement: 18/18 clean controls remain authorized, 18/18 perturbed rows become guarded abort, 0 unsafe commits;
- when a fresh witness can be reacquired before durability, narrower recovery comparisons reauthorize 18/18 replay perturbations and 6/6 recovery cases.

The guarantee is scoped to protected commit surfaces with emitted witness/dependency/binding/eligibility evidence and an atomic final check-and-commit primitive; hidden dependencies, bypassing side effects or forged evidence remain outside scope.

### Design implication
`when to cut` is not only an alarm-time question. For externally consequential actions, the controller needs an **effect-settled/authorization-valid boundary** at durability. Recovery quality should separately report visible task success, authorized completion, unsafe commit, safe non-completion, and infrastructure failure. A recovery that gets the endpoint right while committing from stale authority is not a successful safe recovery.

## Updated synthesis
Long-horizon recovery now has at least eight independently testable controls:
1. checkpoint/audit placement;
2. whether to intervene;
3. when to cut after alarm / before durable effect;
4. which causal object/state element is wrong;
5. which historical checkpoint/time to resume from;
6. what artifact/state to carry across recovery;
7. how much repair/retry budget to spend and when to stop repairing;
8. whether the final durable effect remains freshly authorized/bound/eligible at commit.

The direct historical temporal-target selector remains the least well isolated experimentally. Current evidence is stronger for placement, trigger, causal localization, repair stopping, and commit-boundary gating than for choosing among historical rewind positions.

## Tempered / rejected hypotheses added this run
- `A fixed repair budget is a safe default`: directly rejected in VRR-Stop stress experiments; K=5 can catastrophically damage validity.
- `A strong verifier makes repair stopping safe`: rejected as universal; low discrimination can make stopping calibration collapse even with apparently useful margins, requiring fallback behavior.
- `Increasing verifier acceptance proves repair is improving`: rejected; damaging repairs can still win majority acceptance.
- `Any backtracking is better than continuing`: rejected in the MGT-B exploratory controls; random/periodic/restart can be neutral or worse, and the composite MGT-B benefit cannot be attributed to rollback target alone.
- `Monitoring-guided rollback proves its temporal target selector is best`: rejected; trigger, localization and re-decoding are coupled.
- `Visible endpoint success is enough to validate a recovery`: rejected in commit-time authorization stress tests; durable effects can be unauthorized even when the endpoint is correct.

## Direct historical rewind-target selector gap status
Still unresolved. No primary study found this run that keeps alarm events, candidate checkpoint set, restoration/replay mechanism, policy/model and budget fixed while changing only the historical temporal target selector.

Do not infer a winner from AgentRewind, DART, GA-Rollback, WebRollback, MGT-B, self-backtracking, BRA-Audit, graph rectification, or commit-boundary gating. Each changes another control variable or relies on a different state/effect abstraction.

## Nonempty frontier
1. **Causal-object × temporal-target factorial experiment** remains highest value: independently vary fault localization and resume checkpoint under identical alarms/restoration/budget.
2. **Direct temporal target-selector ablation**: include detector-reset/change-point, fixed-depth, latest-good, dependency/root-cause time, semantic-admissible, value-ranked, random, and agent-selected selectors.
3. **Repair-stopping transfer**: test expected fix-vs-damage stopping in actual tool/GUI/software trajectories with reversible and irreversible effects, not only plan-validity loops.
4. **Automatic safe-cut/effect-settled discovery**: compare immediate alarm, action/transaction completion, semantic boundary, and commit-authorization boundary under matched detector.
5. **Artifact carryover policy**: none / raw diff / compact failed-branch lesson / dependency-local state / full context, on matched true- and false-alarm trajectories.
6. **Verifier-monitor fallback**: characterize when low-discrimination or distribution shift should disable calibrated intervention in favor of guarded keep-best/no-op.
7. **Subgoal/folding negative evidence** remains open: wrong decomposition, stale folded state, or aggressive compression causing downstream degradation.

## Exact continuation
Next run first action: continue searching for a **matched causal-object × temporal-target factorial** or direct historical target-selector ablation, including classic planning/workflow recovery, transactional process recovery and recent LLM-agent runtimes. Require identical alarms, candidate checkpoints, restore/replay mechanism, model and budget before treating selector deltas as causal. In parallel, search for tool/GUI/software-agent studies that transfer expected fix-vs-damage repair stopping or compare safe-cut boundaries under matched alarms. Preserve the target-selector gap if the experiment still does not exist rather than filling it from confounded systems.