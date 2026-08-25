# Long Horizon clean_g1 checkpoint — 2026-08-26 08:00 JST invocation

## Clean boundary and frozen control

This invocation used only the sanitized root control, the `long_horizon` role-local config, this worker's own clean namespace, this worker's own sanitized feedback, and public sources. It did **not** read O/O-derived state, other worker state/configs, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, the shared execution ledger, or other-role receipts. The sanitized feedback item `lh-own-observability-boundary-20260825` was acknowledged and obeyed.

Semantic-freeze tuple for this invocation:
- note main SHA at freeze: `3c8b381c8545e65f986aab45df0535c8b532a638`
- root control revision: `9`
- root control blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- long_horizon config revision: `5`
- role-config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- post-freeze head later observed: `93df151a52c07589a2b33bfb95b759ea081abcce`; no newer control/config was adopted after the first semantic read.

## New primary-source findings

### 1. Historical rollback should be preceded by an exact admissibility filter

A new primary paper, **When Can Agents Safely Checkpoint, Fork, Restore, and Merge? Exact Checking for Execution Edits** (arXiv:2608.22928, submitted 2026-08-24), formalizes Checkpoint/Fork/Restore/Merge as execution edits. Its central observation is that an edit cannot erase earlier authorization, a tool request that was already sent, an outstanding result that remains required, or an in-flight causal dependency. The proposed runtime derives from the execution record exactly which earlier actions/results must remain preserved and decides whether an edit is safe by enumerating policy-compliant completions. If no safe completion remains it can return a checkable proof; otherwise the surviving completions define the allowed continuations. The paper reports formal coverage of Checkpoint and six forms of Fork/Restore/Merge, a Lean mechanization, and executable tests.

**Implication:** do not treat every historical checkpoint as an optimization candidate. Long-horizon recovery should first compute the candidate edit/checkpoint set, run an exact/history-derived admissibility filter, and only then optimize which admissible historical target to choose.

**Scope guard:** this is formal safety/correctness evidence for execution edits, not behavioral evidence that the checker improves end-task success or that any target selector is optimal.

### 2. Hydra remains the closest direct target-selector comparison, but not a strict selector-only factorial

Primary PDF verification of **Hydra: Efficient, Correct Code Generation via Checkpoint-and-Rollback Support** (arXiv:2605.15238) confirms Appendix E's comparison on 100 C++ tasks that initially compile-fail under Qwen2.5-32B. The same Hydra runtime compares:
- Random: uniformly select a rollback point after an error;
- Backwards: walk prior progress nodes toward the root;
- Entropy: select the progress node preceding the maximum-entropy token;
- TokPol: maintain a belief over root-cause distance and select a rollback candidate to minimize expected token cost plus future fallback cost.

TokPol has substantially lower latency and token consumption than the other three in the reported experiment. However, the comparison is not a literal selector-only factorial with an identical retry budget: Appendix E sets Backwards candidate attempts to `a=1`, Entropy to `a=2`, and TokPol updates its posterior after failed attempts. The principal outcome is recovery efficiency/static correctness rather than final GUI/tool-agent task success.

**Conclusion:** Hydra materially narrows the historical-target gap, but does not close the stronger frontier: same alarm, same checkpoint candidate set, same restore/carry-forward, same model, same retry/token budget, varying only target selection and measuring final task success.

### 3. Detector quality and closed-loop recovery remain separable

**Real-Time Detection and Repair of LLM Agent Failures** (arXiv:2608.02464) provides a useful near-factorial on the same episodes/objective labels. Deterministic task checks had zero false positives in the reported samples while a behavioral monitor had materially higher false-positive rates; the same paper separately evaluates rollback-and-rerun recovery from the same checkpoint/prefix. On 55 genuinely wrong episodes, simple resampling recovered 16% while a located failure signal recovered 45%; over 120 episodes, the located strategy increased task success from 52% to 73% in that tested setup.

However, the repair table does **not** replay different detector variants under one fixed actuator/cut/carry-forward configuration. Therefore a strict detector-quality factorial remains unresolved. High detection AUROC/precision still cannot be treated as equivalent to positive closed-loop utility without recovery and disruption measured under the same actuator.

### 4. Long-horizon memory should represent transition contracts, not only subtask summaries

**Don't Drop the BATON: Long-Horizon Robot Manipulation via Agentic Subtask Exploration and Transition-aware Memory** (arXiv:2608.16889) treats subtasks as exploration units but also stores transition-aware information: readiness conditions before invoking a VLA policy, handoff entry conditions plus restore actions, and lookahead conditions that make the current subtask's outcome useful to the successor. The reported RoboMemArena result is 57.7% task success and 78.8% compositional success, +11.6 and +14.9 points over the strongest reported baseline in that paper.

**Implication:** a subgoal/folding system should consider edges/handoffs as first-class memory. A node/subtask can be individually successful yet leave an incompatible successor entry state.

**Scope guard:** BATON is a combined robotics system; the retrieved primary evidence does not isolate all three transition-memory components in a clean generic-agent factorial.

## Updated synthesis

The recovery controller should now be decomposed at least as:

`failure sensing -> intervention decision -> safe cut timing -> candidate checkpoint/edit set -> exact admissibility filter -> historical target selector among admissible candidates -> failed-branch carry-forward policy -> restore all relevant local/inference layers -> external-effect settlement -> commit-time revalidation -> repair stopping`

Two refinements follow:
1. **Safety before optimization:** target selection is conditional on admissibility. An attractive rollback point is irrelevant if restoring it would duplicate an already-authorized effect, discard a still-required result, or cross an incompatible in-flight dependency.
2. **Transitions are state:** subgoal compression/folding should preserve the entry/exit contracts needed by neighboring subtasks, not just a summary of the completed subtask itself.

## Explicit non-findings / gaps retained

- No strict detector-quality/calibration factorial was found that fixes the recovery actuator, cut rule, carry-forward, policy/tasks and FPR budget while varying detector quality and reporting final success plus disruption.
- No strict historical-target selector factorial was found that fixes alarm, checkpoint candidate set, restore/carry-forward, model and retry/token budget while varying only the chosen checkpoint and reporting final tool/GUI/software-agent task success.
- The execution-edit checker is formal safety evidence, not evidence of behavioral task improvement.
- BATON is combined robotics evidence and should not be generalized to generic long-horizon agents without a matched ablation.

## Exact continuation

1. Search for a target-selector-only factorial with identical alarm, checkpoint set, restore/carry-forward, model and retry/token budget, prioritizing software/tool/GUI agents and final task success.
2. Search for a detector-quality/calibration factorial where the actuator and recovery mechanics are fixed across detector variants and both recovery and disruption are reported.
3. Verify the first-party code artifacts for arXiv:2608.22928 and Hydra only as source/implementation verification; do not treat implementation availability as adoption evidence.
4. Keep the subgoal/folding negative-evidence branch active, prioritizing transition/handoff failures, stale folded summaries and over-aggressive compression that reduce final task success.
5. Maintain a nonempty frontier; this checkpoint is not global completion.
