# Long Horizon clean_g1 checkpoint — 2026-08-26 09:00 JST invocation

## Clean boundary and frozen control

This invocation used only the sanitized root control, the `long_horizon` role-local config, this worker's own clean namespace, and public sources. It did not read O/O-derived state, other worker state/configs, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, the shared execution ledger, or other-role receipts.

Semantic-freeze tuple:
- note main SHA at freeze: `57ce90e2b1c84e11468b29954ce20bbce50cae11`
- root control revision: `9`
- root control blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- long_horizon config revision: `5`
- role-config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`

A post-semantic SHA-only head check still observed the same main SHA. No newer control/config was adopted after the semantic-freeze barrier.

## New primary-source findings

### 1. The exact execution-edit checker now has a verified first-party runnable repository

The arXiv metadata for **When Can Agents Safely Checkpoint, Fork, Restore, and Merge? Exact Checking for Execution Edits** links the public repository `eunomia-bpf/agent-check-restore-safety`. Direct repository verification confirms it is public and active. Its README describes a runnable research prototype built around durable execution records, stable external Operation identities, state replay, history-bound rule changes, Python/Lean reference semantics, tests, and several restore/replacement demos including real VM/container boundaries.

Important scope guard: repository availability and runnable demos strengthen implementability/reproducibility evidence only. The README explicitly says the system is a research prototype rather than production-ready. This does not establish that the checker improves generic agent task success or that its target-selection policy is optimal.

### 2. Semantic handoff failure is directly measurable even when each component skill appears strong in isolation

**Diagnosing Semantic Handoff Failures in Agent-Orchestrated Vision-Language-Action Skill Composition** (arXiv:2607.06256v2) evaluates the same VLA skill checkpoints under two initial-state distributions: clean skill-boundary snapshots versus chained terminal states left by predecessor skills. Selected navigation, grasping, placement, and door-opening skills reach 77–100% success from clean snapshots, yet composed rollouts still frequently stall from chained states and end-to-end task success is described as near zero. Failure traces attribute the gap to next-skill readiness, target grounding, and low-level execution.

Implication: a completed subgoal cannot be represented only by its local success bit or compact outcome summary. Long-horizon state must preserve or verify a successor-relevant handoff contract: what state was actually left behind, what the successor requires, and whether a restore/repair step is needed before advancing.

Scope guard: this is robotics/VLA evidence in BEHAVIOR-1K. It directly validates the existence of semantic handoff failure, but does not by itself prove a specific generic-agent transition-memory design.

### 3. Folding can create a training-state distribution problem, not only an information-loss problem

**FoldAct: Efficient and Stable Context Folding for Long-Horizon Search Agents** (arXiv:2512.22733) identifies a distinct failure mode for learned folding: summary actions change the agent's future observation distribution, making the observation process policy-dependent and non-stationary. The paper attributes instability to gradient dilution and self-conditioning, including training collapse, and introduces separated summary/action losses plus full-context consistency and selective segment training. It reports a 5.19× training speedup for its method.

Implication: folding policy evaluation should include not only final-task retention/loss of facts, but also whether learned summaries induce a self-reinforcing distribution shift that destabilizes later policy updates. This is especially relevant when the same model both generates summaries and learns from trajectories conditioned on those summaries.

Scope guard: this is training-stability evidence for long-horizon search agents, not proof that inference-time folding is harmful in general.

## Search result on the two strict factorial frontiers

Targeted searches again did not surface a study that cleanly fixes alarm, candidate checkpoints, restore/carry-forward, model, retry/token budget and varies only historical rollback target while measuring final software/tool/GUI task success. Hydra remains the closest prior finding but differs in retry/fallback behavior across selectors.

Likewise, no study was found that varies detector quality/calibration while holding one recovery actuator, safe-cut rule, carry-forward policy, model/tasks and intervention budget fixed and reports both recovered failures and disrupted would-have-succeeded trajectories. `Accurate Failure Prediction in Agents Does Not Imply Effective Failure Prevention` remains strong evidence that offline detector quality cannot substitute for closed-loop utility, but it is not the desired fixed-actuator detector factorial.

These are retained as explicit research gaps rather than inferred closed findings.

## Updated synthesis

The long-horizon controller decomposition remains:

`failure sensing -> intervention decision -> safe cut timing -> candidate checkpoint/edit set -> exact admissibility filter -> historical target selector -> failed-branch carry-forward -> restore all relevant local/inference layers -> transition/handoff readiness check -> external-effect settlement -> commit-time revalidation -> repair stopping`

New refinement: the transition/handoff readiness check is not optional bookkeeping. Clean local completion can coexist with catastrophic chained-state failure, so successor-readiness belongs in the causal state that must survive compression, rollback and handoff.

## Exact continuation

1. Continue searching for a strict historical-target selector factorial with identical alarm, checkpoint set, restore/carry-forward, model and retry/token budget, prioritizing software/tool/GUI agents and final task success.
2. Continue searching for a detector-quality/calibration factorial with a fixed recovery actuator/cut/carry-forward and both recovery and disruption outcomes.
3. Inspect the semantic-handoff paper's full tables/appendix for skill-by-skill clean-vs-chained degradation and any intervention that restores successor readiness; keep diagnostic evidence separate from repair evidence.
4. Inspect FoldAct and Context-Folding ablations for fold frequency/depth/summary-quality regimes where compression becomes harmful; prioritize matched final-task outcomes over token reduction alone.
5. For implementation evidence, inspect the first-party `agent-check-restore-safety` tests/proof structure at a pinned public revision. Continue searching for a first-party Hydra code artifact, but do not treat search failure as evidence that none exists.
6. Maintain a nonempty frontier; this checkpoint is not global completion.
