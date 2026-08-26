# Long Horizon clean_g1 — meta-selector / matched-budget checkpoint

## Frozen semantic control tuple
- frozen note main SHA: `85da28890bdc73ca2cdfd93ce997c6174117c2f0`
- root control revision: `9`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- role: `long_horizon`; `enabled_desired=true`
- pre-semantic second SHA-only lookup matched the frozen SHA.
- semantic boundary preserved: only own clean namespace, own sanitized feedback, and public sources were used. Shared aggregate ledger, other-role receipts/configs, O/O-derived state, other workers, downstream, and legacy/pre_independence research were not used.
- own feedback `lh-own-observability-boundary-20260825` acknowledged operationally: no shared ledger/other-role receipt read occurred.

## New primary-source findings

### 1. Shepherd supplies a concrete agent-selected historical fork selector, but its published experiment does not isolate selector quality
Shepherd (arXiv:2605.10913v2) evaluates a stronger meta-agent that reads a completed trajectory and chooses a historical `fork_step` plus a natural-language hint. In the full SWE-Bench Verified experiment, among passing baselines the guided rerun produced a strictly shorter passing trajectory for 68% of Sonnet 4.6 cases and 82% of GPT-5.4-high cases; Table 12 also records 10 and 13 rescues respectively where a failed baseline became passing. The chosen fork positions spread roughly one-third at full restart, one-third in the first half, and one-third at/after the midpoint. This is useful evidence that a learned/agentic selector naturally uses variable rollback depth rather than a fixed latest checkpoint.

However the effect is not a target-selector-only result. The same meta-agent jointly chooses `fork_step` and a trajectory-specific hint, so historical target and failed-branch carry-forward/guidance are entangled. A strict selector arm can still reuse this mechanism by asking the meta-agent for `fork_step` but holding the post-fork hint/carry-forward policy fixed across all arms.

Primary sources:
- paper: https://arxiv.org/abs/2605.10913
- released experiment repo: https://github.com/shepherd-agents/shepherd-experiments
- SWE-V runner: `exp/trajprune/src/experiment_trajprune/workers/swev_runner.py`
- fork/hint proposer wrapper: `exp/trajprune/scripts/run_e2b_smoke.py`

### 2. Shepherd independently reproduces the rollback-depth budget confound
The released SWE-Bench runner restores the filesystem/message prefix at the selected historical step, then calls the live worker with `step_limit = global_step_limit - fork_step`. Therefore the amount of post-intervention decision budget varies with target depth: an earlier target receives more new model calls than a later target. This is the same scientific confound already identified in Replay Gap by a different code path.

This materially strengthens the strict factorial requirement: every selector arm needs an explicit branch-local **post-intervention** action/model-call/token/retry budget independent of historical target depth. Otherwise target quality is conflated with remaining horizon. The published Shepherd compression result should not be cited as evidence that its historical target selector is superior to latest/random under equal post-rollback resources.

### 3. Counterfactual Recoverability gives a useful matched-budget branch protocol and an abstention precedent
`Not Every Divergence Should Be Suppressed: Counterfactual Recoverability in On-Policy Distillation` (arXiv:2608.04408, 2026-08-05) reconstructs a selected pre-error prefix and runs continuation and rollback/resample branches under matched generation/environment budgets. In its recorded AIME diagnostic, 200 replayable states yielded 99 non-ambiguous states: 65 labeled recoverable and 34 irreversible-but-avoidable, while 101 were explicitly ambiguous. On those 99 states, mean `p_continue - p_rollback` was +0.185 for recoverable states and -1.000 for irreversible-but-avoidable states; the between-group difference was 1.185 with group-bootstrap interval [1.092, 1.277]. The audit reports zero branch-budget mismatches for the shown oracle runs.

This does **not** solve historical rollback-target selection: it is a formal-reasoning training diagnostic comparing continue versus one rollback/resample branch, not multiple historical targets in a live tool/software agent. But its methodology transfers directly to the planned selector harness:
- assert matched remaining resources at branch construction;
- separate probe branches used to derive a decision feature from held-out branches used as the target outcome;
- allow abstention when branch evidence is ambiguous instead of forcing a target.

Primary source: https://arxiv.org/abs/2608.04408

### 4. Shepherd CRO offers an executed-causal target primitive plus explicit guard-set accounting
Shepherd's Counterfactual Replay Optimization (CRO) does not guess a generic rollback point. For a proposed workflow edit it identifies the **first execution event whose causal dependencies are affected by that edit**, forks there, and replays only the suffix. Every edit is paired with a fix set (examples intended to improve) and guard set (examples that must not regress). Across the paper's five optimization benchmarks CRO was best on four; on LiveCodeBench it reached 51.0% held-out versus 40.0% MetaHarness and 48.7% GEPA, while taking less wall-clock than MetaHarness.

For the selector-only recovery harness, the important transferable pieces are not those end scores themselves but:
- `first affected event` as a concrete executed-causal target candidate;
- fix/guard sets as a direct way to measure both recovery and healthy-trajectory disruption;
- suffix replay against an unchanged prefix to reduce unrelated stochastic/environmental variation.

Scope guard: CRO's target is derived from a known proposed edit/dependency relation, not from unknown failure root cause. It therefore supplies a selector primitive, not evidence that causal target localization is solved in recovery.

Primary source: https://arxiv.org/abs/2605.10913

### 5. Full inference-state restoration has a plausible systems substrate, but semantic branch equivalence is still unproven
Concordia (arXiv:2606.23521) checkpoints GPU-resident mutable serving state across framework/library boundaries: PagedAttention KV arenas, block-table mappings, scheduler-related registered regions, LoRA/optimizer pages, and communication state. It records committed deltas in an append-only recovery log and restores a failed two-GPU prototype in about 1.5 s; its Qwen3-0.6B checkpoint experiment reports under 4% generation-time overhead and a 0.53% persistent-kernel SM footprint.

This is relevant to the branch-admissibility contract because application-level transcript/filesystem restore is not the whole agent state. But Concordia is a **fault-tolerance** system, not a semantic counterfactual branching study. It does not establish that arbitrary historical agent branches can restore exactly the model-attended state needed for a selector factorial, nor that live branch semantics remain identical across targets. It should be treated as a possible inference-state checkpoint backend to investigate, not as proof of branch-level rollback consistency.

Primary source: https://arxiv.org/abs/2606.23521

## Updated strict selector-only blueprint
- fixed failure alarm/intervention time per base trajectory;
- one precomputed admissible checkpoint set shared by all selector arms;
- target-only arms: random, latest-safe, static root-cause, executed-causal/first-affected, meta-agent-selected, and oracle ceiling;
- identical failed-branch hint/memory/carry-forward policy across all arms (in particular, strip Shepherd's target-specific hint when using only its selector);
- identical context, workspace/environment and inference-state restore contract;
- identical **post-intervention** action/model-call/token/retry budget independent of rollback depth;
- live suffix execution, never original/factual suffix stitching;
- same-model control branches to estimate replay/sampling noise;
- optional counterfactual probe selector must use separate probe and held-out outcome branches to avoid target leakage;
- explicit abstention arm when target evidence is insufficient;
- metrics: final SWE-bench resolution, healthy-trajectory disruption, selector coverage/abstention, target depth, actions/tokens/wall time, replay/state mismatch, and (only in effectful environments) external-effect safety.

## What changed relative to the previous checkpoint
1. There is now a concrete published/released **agent-selected historical target candidate** (Shepherd fork-step meta-agent) that can be plugged into the planned fixed candidate set.
2. A second independent released codebase reproduces the same budget-by-depth confound: Shepherd's live SWE-V rerun budget is `step_limit - fork_step`.
3. Counterfactual Recoverability supplies a clean matched-remaining-budget + ambiguity/abstention protocol that can be imported into the selector experiment, though not a historical selector result.
4. CRO supplies an executable causal-dependency target primitive and fix/guard regression accounting.
5. Concordia narrows the systems search for full inference-state checkpointing, but semantic branch equivalence remains an open validation step.

## Exact continuation
1. Inspect whether Shepherd's released meta-selector can be factored cleanly into `fork_step` only while keeping hint/carry-forward identical; identify all other target-correlated variables in the released runner.
2. Search additional software/tool-agent studies that normalize **post-intervention** action/token/retry budget across multiple historical targets; preserve the selector-only gap unless found.
3. Search learned state-only target selectors trained from executed counterfactual branches (rather than target+hint joint policies) and require healthy-trajectory disruption reporting.
4. Design a branch-fidelity assertion spanning exact message prefix, workspace/tree digest, tool-return trace, runtime/session identity, and inference/KV state freshness/rebinding. Investigate whether Concordia-like checkpoint data can expose a deterministic digest/epoch for this assertion.
5. Add a budget-accounting table to the planned Replay Gap harness: for every target record prefix depth, replay cost, branch-local new-action budget, new-token budget, retries, verifier budget and total wall time separately.
6. Preserve the strict scientific gap: no located study yet fixes alarm, checkpoint candidate set, restore/carry-forward, model and post-intervention budget while varying only historical target selector and measuring final live software/tool-agent task success.
7. Maintain nonempty frontier; this checkpoint is not global completion.
