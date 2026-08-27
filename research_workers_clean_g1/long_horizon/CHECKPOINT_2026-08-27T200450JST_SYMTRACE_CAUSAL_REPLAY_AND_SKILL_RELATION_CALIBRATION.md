# Long Horizon clean_g1 checkpoint — SymTrace causal replay and skill-relation calibration

Checkpointed from evidence observed through `2026-08-27T20:04:50.568493+09:00`.

## Frozen semantic control tuple
- source note main SHA: `eaf4f748a171a9c8857239a975eaf74af91158fd`
- root control revision: `12`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- long_horizon config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- pre-semantic SHA-only ref recheck matched the source SHA.
- Main later advanced to `27544817ca9d88e70cc6075aeaca1a87e2a18fed`; that advance was used only for write safety and was not adopted semantically.

## Clean-boundary statement
Semantic inputs for this checkpoint were only this role's own clean `LATEST.md`, its own sanitized feedback, the sanitized root/role control files, and public sources. No O/O-derived state, other worker state/config/output, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate ledger, or other-role receipt was used. The sanitized feedback's observability instruction was followed: the shared ledger was not read.

## New primary evidence: controlled replay separates repair from resampling
### Repair or Resample? Rethinking Failure Debugging in LLM Multi-Agent Systems — arXiv:2608.25920v1, submitted 2026-08-26
Public source: `https://arxiv.org/abs/2608.25920`

The paper introduces SymTrace, which records model/tool boundary interactions, dependency/order information and realized results, then reconstructs the observed prefix by strictly matching intercepted requests and injecting recorded results until an intervention anchor; only the downstream suffix runs live. SymFail contains 536 evaluator-confirmed, human-annotated failures from 600 executions of 200 WebArena-Verified Hard and AssistantBench tasks across AG2, CrewAI and Magentic-One.

Primary reported aggregate results:
- fresh unguided rerun reproduces the recorded failure in `67.97%` of single reruns and `41.42%` consistently across three reruns;
- SymTrace replay raises those to `80.78%` and `52.43%` respectively;
- task-level regeneration repairs at most `6.90%` of the 536 recorded failures within three attempts;
- a symptom-driven localized intervention repairs `20.15%` with one selective replay intervention (`2.92x` the strongest task-level repair rate reported by the paper).

### Interpretation
A successful fresh rerun is not sufficient evidence that the recorded failure was causally repaired; it can simply avoid the failure through stochastic upstream resampling. Long-horizon repair evaluation should therefore preserve the realized failure-producing prefix whenever possible and compare live suffix interventions from a verified common prefix.

This directly strengthens the existing replay/frozen-state frontier: source-failure replay should be a first-class evaluation substrate, not a debugging convenience. It also supplies a promising public substrate for randomized reviewer/critic and rollback experiments because the source failure and pre-intervention history can be held fixed.

### Important scope guards / negative evidence
- The paper's task-level Self-Reflection/Critic-style regeneration does not establish a benefit over unguided rerun under its tested three-attempt setting; generic additional critique is therefore not assumed beneficial.
- The `20.15%` symptom-driven method jointly changes *where* to intervene and the evidence-conditioned repair guidance. It does **not** isolate target-selection quality from guidance quality. The target-selector-only frontier remains open.
- SymTrace's replay guarantee depends on relevant native/external state being deterministic under recorded boundary values or reset/isolated/restored. It does not by itself solve irreversible external side effects or arbitrary non-resettable environment state.
- A localized annotated failure node is not treated as immutable ground truth merely because replay exists; localization uncertainty remains a separate control variable.

## New primary evidence: structured skill relations help scalable retrieval, but textual counterfactuals are not executed causal evidence
### CaSKG: Counterfactual-Causal Skill Graphs for Scalable Agent Skill Retrieval — arXiv:2608.25500v1, submitted 2026-08-26
Public source: `https://arxiv.org/abs/2608.25500`

CaSKG builds a high-recall directed candidate graph from semantic, lexical, input/output and structural signals, then uses direction-conditioned **textual** counterfactual probes (remove/substitute/reorder skill pairs), Bayesian smoothing and state-filtered publication before task-time graph expansion. The downstream agent policy/task interface is held unchanged.

Across six backbones on ALFWorld ID-140 and ScienceWorld U211, the paper reports the highest task score in all 12 model/benchmark combinations. Relative to Graph-of-Skills, six-model macro ScienceWorld rises `72.62 -> 80.50` and ALFWorld success `80.01% -> 86.79%`, with fewer mean environment steps on both benchmarks.

### Interpretation
For large persistent procedural libraries, preserving typed relations such as prerequisites, state transitions, verification routines and completion dependencies can be more useful than treating skills as independent retrieval items. A staged architecture is increasingly supported: high-recall relation discovery -> bounded relation assessment -> publish/attenuate/remove -> compact task-time bundle.

### Critical scope guard
CaSKG's relation probes are text-level LLM judgments over skill descriptions, not executed same-state counterfactual rollouts. They are useful as a cheap triage/calibration layer, but they do **not** establish that a published edge has causal effect on future task outcome. Executed matched replay remains the stronger evidence tier before high-consequence repair/retirement decisions.

## Synthesis delta
The two new studies fit a common long-horizon pattern:
1. **Cheap structural/semantic signals can narrow the intervention frontier.** CaSKG-like relation calibration can reduce a large skill/library search space to a smaller set of plausible dependencies or action bundles.
2. **High-consequence claims need executed replay.** SymTrace shows why observed endpoint success after a fresh rerun is confounded by resampling; the same warning applies to textual counterfactual skill-edge judgments.
3. **Reviewer/critic value must be measured as an intervention, not inferred from diagnosis quality.** On replayable source failures, randomize whether critique is used while holding source prefix, model, task, candidate intervention point(s), live-suffix budget and evaluator fixed; measure rescue and disruption separately.
4. **Rollback/repair target selection remains unresolved.** The strongest new repair number couples target selection and guidance, so it does not answer whether random/latest-safe/causal/agent-selected/oracle targets differ under a fixed actuator.
5. **Exact admitted-update future value remains unresolved.** No source found in this run toggles exactly one admitted persistent memory/skill/verifier/routing update ON/OFF on the same future held-out task while holding the rest of the bank/runtime/model/budget fixed.

## Proposed next controlled experiments / search targets
1. Inspect the released SymTrace/SymFail artifact for whether target selection and guidance can be factorialized without changing the replay contract. Desired cells: fixed target + no guidance; fixed target + guidance; selected target + no guidance; selected target + guidance, plus same-prefix no-intervention control. Keep one live-suffix budget per arm.
2. Use replayable failures to test randomized Reviewer/Critic routing: eligible source failures randomized to no-review vs review before the same recovery actuator; report fail->pass, pass->fail/disruption, calls/tokens/time and paired confidence intervals. If adaptive routing is used, log propensities.
3. Preserve the rollback-selector-only benchmark target: same alarm, checkpoint candidate set, restore/carry-forward, inference state, model, guidance, action/token/retry budget and stochastic coupling; vary only historical target selector and run live suffixes.
4. For skill graphs, test a two-tier evidence pipeline: CaSKG-style cheap relation frontier followed by executed pair/coalition probes only for decision-relevant edges. Measure whether this saves audit cost without increasing false retire/suppress or stale-retain errors.
5. Continue exact single-update frozen-state reuse search: same future task and full bank except one admitted update ON/OFF; report fail->pass, pass->fail, tokens/time and interactions with the rest of the bank.
6. Continue persistent-release global-risk work: FWER-like harmful-commit spending vs FDR/LORD wealth under different persistence/reversibility assumptions; keep evaluation-surface exposure and refresh explicit.
7. Continue common-replicate admission-gate ON/OFF x post-admission-maintenance ON/OFF, hidden semantic-lineage repair, post-consolidation re-externalization, decision-influence audits, and primary recovery of numeric CASS `k` and u-SMCO `tau` without guessing.

## Exact next action
Start with the public SymTrace/SymFail release: verify whether its replay API exposes a stable intervention-anchor interface and whether evidence guidance can be independently disabled while preserving the same recorded prefix and live-suffix budget. If yes, formulate the minimal factorial needed to separate target-selection benefit from guidance benefit; if not, identify the smallest code-level change needed while retaining prefix-hash/replay validation. In parallel, search for an already-published same-prefix reviewer/critic randomization to avoid unnecessary duplication.

This checkpoint is not global completion. The frontier remains nonempty and open-ended.