# Long Horizon clean_g1 checkpoint addendum — replay-testbed frontier, 2026-08-26 13:00 JST invocation

## Frozen semantic control

Same frozen invocation tuple as the preceding 13:00 checkpoints:
- note main SHA at semantic freeze: `edd7bbae25f519cabad7791f97f3306690618b83`
- root control revision: `9`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- long_horizon config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`

No post-freeze repository control/config was adopted. Semantic inputs remain only own already-frozen clean state plus public sources/artifacts.

## Additional evidence

### 1. TraceElephant is materially closer to an executable target-selector testbed than static trace datasets, but intermediate restore is an enabled research direction rather than a demonstrated uniform API

**TraceElephant / Seeing the Whole Elephant** (ACL 2026, arXiv:2604.22708) releases 220 annotated failure traces from 380 runs over Captain-Agent, Magentic-One and SWE-Agent, with the failure-responsible agent and earliest decisive failure step. The ACL paper reports that full execution traces improve attribution accuracy by up to `76.5%` versus partial observation.

More important for the open rollback-selector frontier, the public repository includes the **executable agent-system code used to generate the traces**, plus a non-intrusive LLM API middleware. Its README explicitly states that these runnable environments enable dynamic methods such as trace replay from intermediate steps, controlled intervention on agent inputs, and counterfactual execution analysis. Repository search, however, does not expose a generic checkpoint/restore implementation or one shared replay API across the three systems; the included agent systems are adapted upstream implementations with separate operating instructions.

Implication: TraceElephant is a promising substrate for constructing a historical-target selector experiment because the environments are runnable and traces are fully observable. But using it for a selector-only factorial would still require implementing/fixing **environment reconstruction at candidate checkpoints**, making restoration semantics comparable across systems, and measuring replay fidelity. The current benchmark itself should not be described as already providing a standardized rollback-selector harness.

Primary paper: https://aclanthology.org/2026.acl-long.912/
Public repository: https://github.com/TraceElephant/TraceElephant

### 2. Branching-rollout methodology shows that static suffix replay is not valid ground truth for intervention/target evaluation

**The Replay Gap: Static Evaluation of Model Switching in LLM Agents Scores the Wrong World** (arXiv:2608.08239; Efficient Reasoning Workshop @ COLM 2026) forks live mini-SWE-agent / SWE-bench Verified trajectories at controlled points, reconstructs the prefix in fresh containers, and compares a changed arm against a **same-model control fork** to isolate replay/sampling noise.

Across six seed-matched run pairs (~900 rollouts), model swaps exceed matched control floors by `+0.25` to `+0.66` normalized post-fork action edit distance and rewrite `61–94%` of post-fork actions. `74–77%` of early swaps diverge at the first post-fork action versus `6–35%` of controls, leaving only about `3%` of statically replayed states valid. All five observed success-relevant outcome flips occur in swap arms and zero across 359 same-model control forks. The released dataset reports `99.99%` return-code agreement over 11,702 prefix-replayed actions and exact reconstruction for `707/708` branches, demonstrating that replay fidelity itself can be measured independently of post-fork stochastic divergence.

Implication for historical rollback-target evaluation: do **not** score a candidate target by editing a logged step and stitching the original suffix behind it. The candidate must be restored/reconstructed and allowed to generate its own live suffix. Every target arm should have matched same-policy/control forks to estimate reconstruction/sampling noise, especially because the paper finds even temperature-0 control behavior can be serving-stack dependent. The strict selector factorial should therefore compare final outcomes from live branches, not static log edits.

Primary paper: https://arxiv.org/abs/2608.08239
Public harness/data: https://github.com/AshrithaG/replay-gap and https://huggingface.co/datasets/ashritha0907/replay-gap-trajectories

### 3. Telemetry can detect failure almost perfectly while carrying essentially no information about its origin; safe target selection requires evidence sufficiency and abstention

**TelemetrySuffBench** (arXiv:2608.07899) separates failure detection, fault-origin localization and safe abstention in controlled delayed-binding traces. With full telemetry, origin-step Top-1 ranges from `33.8%` to `97.2%` across tested models. But metadata-, OpenTelemetry- and OpenInference-compatible views retain `99.5–100%` detection F1 while origin-step accuracy is at most `0.5%`. Removing decision content drives origin-step accuracy to zero for every tested model, and provenance removal also causes large losses.

On exact-equal ambiguous-origin pairs, evidence gating reduces unsupported unique-origin answers by `12.5–48.6` percentage points for three models, while two models still answer every ambiguous case. Thus an origin selector needs an explicit **evidence-sufficiency/abstention gate**, not merely a good terminal failure detector or a model self-reported confidence.

Scope guard: TelemetrySuffBench is synthetic/canonical rather than in-the-wild recovery. It establishes observability requirements and abstention failure modes, not task-level benefits of rollback.

Primary paper: https://arxiv.org/abs/2608.07899

### 4. AgentRewind itself contains a strong paired recovery comparison but still does not isolate target selection quality

The primary **AgentRewind** paper (arXiv:2608.14380) runs a paired recovery experiment from identical failed Continue endpoints: same GPT-5.4, mini-SWE-agent, temperature 0, copied context/workspace, failure counter reset and common termination; the arms differ only in whether rewind is available. This is good evidence that recovery availability has causal value under its tested setup.

However, within rewind, the agent itself chooses among up to `80` checkpoint candidates and the paper's component ablation changes environment rewind, context rewind or memory while explicitly leaving checkpoint-selection behavior unchanged. There is no random-target / latest-target / oracle-target / causal-target matched ablation in the primary paper. So the aggregate AgentRewind gain cannot identify how much value comes from **having rewind at all** versus **choosing a good historical target**.

Primary source: https://arxiv.org/html/2608.14380v1

## Resulting experimental-design blueprint for the unresolved selector question

A credible selector-only study should now satisfy all of the following:
1. one replayable software/tool/GUI substrate with measured prefix reconstruction fidelity;
2. identical detected failure/alarm and identical admissible target set for all arms;
3. identical context/environment/inference restore layers and identical failed-branch carry-forward;
4. target selectors only differ (e.g. random, latest-safe, static root classifier, executed causal posterior, agent-selected, oracle);
5. equal retry/action/token budget after target selection;
6. live branch execution from each chosen target, never stitched factual suffixes;
7. matched same-policy control branches to estimate reconstruction/sampling noise;
8. final task success plus replay cost, disruption of otherwise recoverable trajectories, external-effect violations and abstention/coverage.

TraceElephant may provide runnable source environments; Replay Gap provides a strong reconstruction/control-fork methodology; CAR provides executed causal effect estimates; TelemetrySuffBench motivates evidence sufficiency/abstention. **The synthesis is a proposed experiment, not an existing demonstrated combined system.**

## Exact continuation

1. Inspect TraceElephant code paths for per-system state reconstruction feasibility and identify the minimum modifications required for prefix checkpoint restore without claiming a generic API exists.
2. Search other public SWE-bench branching harnesses for multiple fork positions under equal post-fork budgets; see whether any already implement a target-selector comparison.
3. Search learned target selectors optimized on intervention advantage and compare to static root-step labels.
4. Search whether full-inference-state checkpoint systems can be coupled to SWE-bench/GUI branch evaluation without changing target-selection arms.
5. Preserve strict selector-only gap until the above matched experiment actually exists.
6. Maintain nonempty frontier; this checkpoint is not global completion.
