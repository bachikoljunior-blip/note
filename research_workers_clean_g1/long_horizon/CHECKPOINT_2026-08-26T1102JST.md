# Long Horizon clean_g1 checkpoint — 2026-08-26 11:02 JST invocation

## Clean boundary and frozen control

This invocation used only the sanitized root control, the `long_horizon` role-local config, this worker's own clean namespace, and public sources / first-party public artifacts. It did not read O/O-derived state, other worker state/configs, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, the shared execution ledger, or other-role receipts.

Semantic-freeze tuple:
- note main SHA at freeze: `dd294332184997939909490d0a5d7ec4c7cc6d62`
- root control revision: `9`
- root control blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- long_horizon config revision: `5`
- role-config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`

A second SHA-only lookup before the first substantive semantic read matched the frozen SHA. A post-semantic SHA-only lookup observed note main advance to `a93db574e98bb3080fd4bfcaabd6936af67af8d9`. Per the hard semantic-freeze rule, no newer control/config or semantic state was adopted; this checkpoint remains bound to the frozen tuple.

## New evidence and synthesis

### 1. Fixed rollback depth now has a relatively clean behavioral ablation in an embodied agent, but not yet in software/tool/GUI agents

**VLA-in-the-Loop: Online Policy Correction with World Models for Robust Robotic Grasping** (ICLR 2026 submission / OpenReview) varies rollback depth inside the same event-triggered correction pipeline. The supervisor trigger and correction mechanism are held conceptually fixed while the rollback depth is changed across `5 / 10 / 15 / 20` steps.

Reported average task success over four manipulation tasks:
- correction without rollback: `56.3%`
- rollback 5 steps: `54.2%`
- rollback 10 steps: `61.5%`
- rollback 15 steps: `59.4%`
- rollback 20 steps: `63.5%`

Per-task outcomes are non-monotone even though the paper describes a general trend toward improvement with deeper rollback. For example, `Stack green on yellow` peaks at 10/15 steps (`41.7%`) and falls at 20 (`37.5%`), while `Put spoon on towel` peaks at 20 (`75.0%`).

Implication: historical target depth materially affects final task success even when recovery machinery is otherwise similar, and "deeper is always better" is not supported. This partially closes the generic depth question, but not the strict target-selector frontier: the domain is robotic manipulation, candidate targets are fixed temporal offsets rather than semantic checkpoints, deeper rollback changes replayed physical work/cost, and the paper does not provide an equal-token/equal-action-budget selector-only factorial.

Primary source: https://openreview.net/pdf?id=aT4LG8c6DE

### 2. Rewind-IL cleanly separates `when to recover` from `where to recover`, but explicitly cannot ablate them independently

**Rewind-IL: Online Failure Detection and State Respawning for Imitation Learning** (arXiv:2604.16683) is architecturally useful because it uses two distinct control objects:
- `when`: TIDE, a conformal-calibrated temporal inter-chunk discrepancy detector;
- `where`: the latest already-peaked VLM-verified semantic checkpoint, selected by policy-feature similarity.

On recovery it replays the action snapshot associated with that checkpoint, clears the temporal ensembler/action queue, and resumes from a clean policy state. The paper's own evaluation section explicitly says detection and respawning are not independently ablatable: detection without respawning reduces to termination, while respawning requires a trigger.

Integrated task-success results are strong but should remain attributed to the whole stack: real-world natural runs average `66.7% -> 80.0%`; perturbed runs `18.3% -> 76.7%`; RoboCasa tasks improve from `55/60/55` to `70/80/70`.

Implication: this provides a concrete implementation pattern for separating trigger and target logic, but it does not identify the causal value of the historical target selector. The selector remains `latest verified safe state`; no matched comparison against earliest-safe, root-cause, random-safe, fixed-depth, or learned-value target selection is reported.

First-party project: https://sjay05.github.io/rewind-il/
Paper: https://arxiv.org/abs/2604.16683

### 3. Before choosing a rollback target, test whether the failure regime is stably localizable at all

A first-party public artifact from **Before the Fall: Delta Minimal Failing Prefixes for Local Tool-Use Agent Failures** (ICML 2026 FAGEN workshop, non-archival) materially sharpens the target-selection problem. Delta-MFP restores saved prefixes and samples independent continuations to estimate the replay failure probability for each prefix.

Released results on 25 natural failed traces at replay budget `N=3`:
- nontrivial later failure basin: `13/25`
- failure already reproduces from prefix 0: `5/25`
- unstable / no-Delta localization: `7/25`

The most important finite-budget result is stronger than the aggregate counts suggest. On 50 soft perturbation traces, the aggregate number of nontrivial localizations stays `7/50` when increasing replay budget from `N=2` to `N=5`, but only **1 of the original 7** remains nontrivial; `37/50` traces retain their regime at all. Six different traces enter the nontrivial class.

Implication: a rollback controller should not force a historical target merely because a finite replay oracle names one. Add a pre-selector state such as `localization_confident / prefix0 / unstable`. If localization is unstable under available replay budget, target selection should defer, gather more evidence, or use a conservative recovery path rather than treating the argmax/threshold crossing as ground truth.

The same artifact warns against over-reading small repair probes: on soft traces its no-repair baseline is `0.667` while a fault-label Oracle is `0.083`, with wide Wilson intervals and an explicit warning not to rank repair methods from those cells. This is a useful negative control: even a seemingly informative diagnosis/intervention can underperform when the failure regime is weak or unstable.

First-party artifact: https://github.com/DaoyuanLi2816/delta-mfp-local-agents
Workshop paper link is in the repository README.

## Updated controller decomposition

The recovery controller is refined to:

`failure/risk sensing -> intervention-advantage estimation -> intervention decision -> safe cut timing -> candidate checkpoint/edit set -> exact admissibility filter -> failure-regime/localization-confidence test -> historical target selector -> failed-branch carry-forward -> restore all relevant local/inference layers -> transition/handoff readiness check -> external-effect settlement -> commit-time revalidation -> repair stopping`

New distinction: **target selection should be conditional on target identifiability**. A system can possess many technically restorable checkpoints while still lacking enough counterfactual evidence to say which historical prefix actually entered a reproducible failure basin.

## Remaining gaps and exact continuation

1. Continue searching for the strict selector-only factorial in software/tool/GUI agents: identical alarm, checkpoint set, restore/carry-forward, model, retry/token/action budget; vary only historical target selector and report final task success plus recovery cost.
2. Specifically search for comparisons among `latest-safe`, `earliest-causal/root-cause`, `fixed-depth`, `random-safe`, and learned/counterfactual-value selectors under a common actuator.
3. Search for replay-budget-aware target-selection policies that propagate localization uncertainty into the control decision instead of collapsing to one target.
4. Narrow the detector frontier to representation/discrimination or intervention-value quality under a fixed recovery actuator, cut rule and carry-forward policy; require both recovered-failure and disruption accounting.
5. Search for same-prefix/action-conditioned intervention experiments where the actuator is local rollback/replay rather than expert handoff/re-answer.
6. Continue handoff-recovery and fold-frequency/depth searches only when they provide matched final-outcome ablations rather than component-only metrics.
7. Maintain a nonempty frontier; this checkpoint is not global completion.
