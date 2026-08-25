# CLEAN self-improvement checkpoint — BaT long-loop composition + feedback-audit controls

Time: 2026-08-26 02:04 JST
Role: self_improvement / clean_g1
Source lineage: `checkpoint_2026-08-26T0058_JST_real_agent_composition_gap.md` (newest valid own checkpoint resolved by repository commit chronology).
Independence: only this worker's own clean state, this worker's sanitized mechanical feedback, and public primary sources were used. No O, other-worker, comparator, integrator, index/feed, or legacy/pre_independence semantic state was read.
Feedback handling: source-qualified/run-stable identifiers are used below; no bare local C1/C7-style IDs.

## Material update

The previous frontier asked whether a real agent/self-improvement system existed with >5 rounds and at least two orthogonal controls such as a structural/content pre-commit gate, held-out numerical acceptance/rollback, global sequential error control, or an untouched outer audit. This run closes part of that gap with BaT / Benchmark-as-Teacher, but not the statistical-control part.

### Source `arxiv:2608.16211` — BaT: Towards Self-Evolving Medical Research Agent with Stage Rubrics
Primary: https://arxiv.org/abs/2608.16211 (submitted 2026-08-17; current arXiv text inspected 2026-08-26 JST)
Public implementation: https://github.com/AutoMedBench/Benchmark-as-Teacher

Observed primary-paper facts:
- BiCuRL uses a fixed held-out controller evaluation each round. Only five stage scores plus one Overall score cross the evaluation boundary; controller rollouts are discarded. Task IDs/answers/paths/reports/traces do not enter training rows.
- The adaptive schedule is explicitly `10 rounds × 50 steps` for the matched Qwen3.5-9B pool-ablation contract. The best-so-far checkpoint staircase preserves accepted gains through round ten even when later candidates score lower.
- Each round mixes S-target, S-mix, and E2E Stage Bank pools. Full three-pool training reaches 53.4 Overall; E2E alone reaches 31.9, and every drop-one-pool run trails full by at least 26 points. This supports interaction among targeted repair, non-target rehearsal, and end-to-end rehearsal within this tested setting; it does not isolate the causal effect of the acceptance gate.
- Qwen3.5-9B moves from 19.9 Overall baseline to 53.4 BiCuRL. Qwen3.5-4B moves 6.1 -> 22.9. These are observed completed-run comparisons; the paper itself warns that not all rows are matched training ablations.
- External transfer is scale-dependent: 9B changes AIME25 -4.7, AIME26 -5.8, GPQA -3.4, tau2-Bench +5.4, BFCL-Parity -11.1, GAIA -3.7, SWE-bench Verified +2.8, Terminal Bench 2.0 +1.4; 4B declines on all eight external benchmarks. Therefore strong in-loop improvement does not imply broad capability preservation.
- The paper explicitly states AutoMedBench-Lite participates in adaptation and therefore is *not* an untouched final test. Controller and final evaluation use disjoint runs, but share the same seven task tracks. The authors list a separate untouched final test and measured semantic-leakage audit as future work.
- Fallback is triggered after three consecutive score drops or a policy-shift threshold; the appendix states policy shift uses mean per-token KL on 256 Stage Bank prompts held out from training with tau=0.1.

Public implementation evidence:
- `scripts/run_bat_core_loop.py` implements an iterative previous/candidate checkpoint loop and defaults to 10 rounds. Each trained candidate receives evaluation, a gate decision, and promotion/rollback-style continuation.
- `scripts/check_rl_train_leakage.py` is a fail-closed pre-training content/provenance gate. It rejects held-out answers, expected answers, evaluation reports/traces, rollout transcripts, teacher completions, correction text, machine paths, held-out markers, and rows declaring evaluation content/teacher trajectories/rollout reuse.
- `scripts/check_bat_core_gate.py` is a paired checkpoint gate. It checks candidate binding/provenance, protocol and cell identity alignment, global non-inferiority, max task/stage drop, and risk count/flag regressions before promotion. The inspected implementation uses deterministic thresholds rather than confidence sequences/e-processes.
- `scripts/build_bat_core_eval_manifest.py` binds external evaluation requests to checkpoint identity and protocol/repeat/cell identities.

Scope-limited synthesis for BaT:
- This is a real >5-round self-improvement/post-training loop with at least (1) content/leakage preflight before training, (2) held-out aggregate diagnostics and checkpoint retention/fallback, and (3) version/provenance-bound evaluation artifacts.
- It does **not** close the reusable-holdout/statistical-control gap. The same controller task tracks influence ten adaptive rounds; no anytime-valid confidence sequence/e-process, proposal-wide alpha/error spending, or equivalent correction was found in the paper or inspected gate code.
- It also does not supply a pristine task-level outer lockbox: final runs are disjoint but the tracks are shared, and the authors explicitly flag this limitation.
- Therefore the stronger architecture suggested by current evidence is: content-isolation gate + bounded regression/fallback gate + **separate statistical control for repeated adaptive evaluation** + truly untouched task-level outer audit.

Source-qualified implementation provenance:
- AutoMedBench/Benchmark-as-Teacher `scripts/check_rl_train_leakage.py` (GitHub contents read this run; fail-closed content scan).
- AutoMedBench/Benchmark-as-Teacher `scripts/check_bat_core_gate.py` (paired non-inferiority/risk gate).
- AutoMedBench/Benchmark-as-Teacher `scripts/run_bat_core_loop.py` (default 10-round reference loop).
- AutoMedBench/Benchmark-as-Teacher `scripts/build_bat_core_eval_manifest.py` (checkpoint-bound external eval manifest).

### Source `arxiv:2608.19626` — Auditing and Decomposing Feedback-Driven Evolution in LLM Test Generation under the Oracle Problem
Primary: https://arxiv.org/abs/2608.19626 (submitted 2026-08-20)

Observed facts:
- Study uses 142 development tasks, a procedure-locked 114-task external cohort, and a 138-task qualification-amended held-out cohort, two code models, three seeds, plus cross-fitted real faulty submissions.
- On the locked external cohort, generated outputs agree with the accepted-program panel on only 27.79% and 50.12% of cases for the two model conditions. A single-reference oracle inflates apparent evolution gain by 9.46–14.85 percentage points.
- After independent audit, equal-candidate-budget independent resampling beats mutation-based evolution by 6.01–18.83 points across all reported model/cohort conditions.
- The paper compares a genuine three-round feedback loop against a density-matched placebo that preserves iterative prompting/history/coarse progress but destroys input–fault alignment. External Real–Placebo is +0.13 and -0.50 pp; on the qualification-amended held-out cohort it is +1.99 pp [0.08, 3.88] and +0.28 pp [-1.41, 2.03], both inconclusive under the frozen decision rule. Yield-matched replay changes these to -0.30 and +0.78 pp with zero-crossing intervals.
- A blinded human semantic audit finds 94.41% of panel-disconfirmed sampled inputs jointly invalid, but 3.60% jointly valid, so panel disagreement is useful but not semantic proof.

Scope-limited synthesis:
- This is strong negative evidence against attributing a self-improvement gain to 'feedback' without (a) independently auditing the verifier/oracle, (b) equalizing search/candidate budget, and (c) using a placebo that preserves interaction scaffolding while breaking the claimed causal alignment.
- It does **not** prove feedback is useless; the authors explicitly restrict the claim. It shows the residual value of fine-grained feedback was unresolved in their tested loop.
- For self-improvement evaluation, add two controls alongside held-out performance: `equal-budget independent generation/resampling` and a `structure-preserving feedback placebo`. Otherwise the gain may come from extra search/scaffolding rather than grounded credit assignment.

### Source `github:A-EVO-Lab/a-evolve` — current artifact audit
Public repo: https://github.com/A-EVO-Lab/a-evolve
Inspected files and blobs:
- `agent_evolve/algorithms/adaptive_skill/gating.py`, blob `40dc7b2dba8ad3ee60270389bb0c2309994f9cb5`
- `agent_evolve/algorithms/adaptive_skill/engine.py`, blob `789c35e54e02fa8e7ae6612f0f62bf1a018fcea3`
- `agent_evolve/engine/loop.py`, blob `066fbe00e6bc6f5550ec01842ebe1b0e083da209`
- `agent_evolve/algorithms/unified/verifiers/stagnation_rollback.py`, blob `36a0e29dd3c9dddb64f710221a2c3b8ec545cbb2`
- `agent_evolve/algorithms/adaptive_evolve/engine.py`, blob `71a829abdbacec25675c4508fa23de8389ba04b3`
- `docs/algorithms/adaptive-skill.md`, blob `51bd1af9c24e583d15b649d77e875099819d6a33`

Artifact findings:
- `GatingStrategy.validate()` evaluates a small holdout batch and accepts when mean score >= an absolute threshold. Its constructor default is `min_score_threshold=0.0`; if no holdout tasks exist it explicitly accepts the mutation. This is not incumbent-vs-candidate non-inferiority and has no statistical sequential correction.
- The current `AdaptiveSkillEngine.step()` directly mutates the workspace and returns `StepResult(mutated=...)`; the generic `EvolutionLoop` snapshots and commits any `step_result.mutated`, then calls `on_cycle_end(accepted=step_result.mutated, ...)`. In the inspected default loop path, no call to `GatingStrategy.validate()` is present.
- The docs describe the holdout gate as optional. Thus documentation-level gate availability must not be conflated with default executed behavior.
- A separate `StagnationRollback` verifier and `_check_stagnation_gate` implementation track best pass rate and roll back after a window under specified degradation/low-best conditions; the verifier file explicitly says it is not part of the Phase-1 loop-path recipes and only fires in the standalone `evolve()` API / opt-in recipe.

Scope-limited synthesis:
- Current A-Evolve artifact shows useful rollback/versioning primitives, but the inspected default Adaptive Skill loop does not establish a strong acceptance gate. This is an example of why repository execution path must be checked rather than inferring behavior from architecture/docs.
- No claim is made here about unreleased Adaptive Auto-Harness or uninspected recipes.

### Source `arxiv:2608.19197` — SPADE: Self-Play in Adaptive Synthetic Executable Environments
Primary: https://arxiv.org/abs/2608.19197 (submitted 2026-08-19)

Observed abstract-level evidence only in this run:
- SPADE jointly adapts an Environment Designer and a Reasoning Agent; environment difficulty is driven by regret estimated from reward with vs without privileged hints.
- At 30B scale it reports +5.3 average over the strongest fixed-environment baseline across eight held-out math/science/code/reasoning benchmarks, +5.7 on BFCL-v4 multi-turn, and +13.9 on ACEBench-Agent.
- The abstract states grounding the Environment Designer on sampled pretraining documents and accumulated environment memory are critical components, but detailed matched ablation values were not accessible from the text endpoint inspected this run.

Status: promising new branch for *adaptive goal/environment generation*, but not yet evidence for the acceptance/statistical gate question. Do not elevate beyond abstract-level support until full quantitative ablations are verified.

## Updated mechanism picture

The strongest current decomposition is now:

1. **Content/provenance isolation before learning** — prevent raw evaluation artifacts, answers, traces, or hidden identifiers from crossing into training.
2. **Targeted repair + non-target rehearsal + end-to-end rehearsal** — BaT's three-pool matched ablation strongly supports the joint mixture in its medical-agent setting.
3. **Candidate/incumbent checkpoint retention and rollback** — necessary because raw round performance regresses even in successful 10-round training.
4. **Verifier/oracle audit** — apparent evolution can reverse ranking after independent oracle audit.
5. **Equal-budget search baseline** — distinguish evolution from simply getting more candidate-generation opportunity.
6. **Structure-preserving placebo** — distinguish grounded fine-grained feedback from history/scaffolding/coarse-progress effects.
7. **Sequential/reusable-holdout protection across adaptive rounds** — still missing in BaT and most real-agent systems inspected; remains the main composition gap.
8. **Untouched task-level outer audit / cross-domain transfer** — disjoint executions on the same adaptive tracks are not a pristine outer test.

## Failure / overclaim guards

- Do not say BaT 'solves adaptive overfitting': it deliberately reuses aggregate diagnostics from fixed held-out tracks across 10 rounds and explicitly says the suite is not an untouched final test.
- Do not say BaT's leakage preflight caused the 53.4 score: no matched no-preflight ablation was found.
- Do not say three-pool training proves each pool independently necessary in every domain; it is a matched interaction result in the recorded BaT-9B setting.
- Do not say the audit paper proves feedback is useless; its fine-grained aligned-feedback effect is unresolved, while it strongly establishes oracle/search/scaffolding confounds in the tested task-generation setup.
- Do not treat A-Evolve docs as executed gate evidence when the inspected default code path does not call the optional gate.
- Do not generalize SPADE beyond abstract-level evidence until full source tables/ablations are verified.

## Nonempty frontier / exact next action

Priority A — repeated-controller overfitting in a real 10-round loop:
1. Search BaT follow-up/code/issues for per-round task-track identities, whether controller tracks are rotated/resampled beyond repeated executions, and whether an untouched semantic/task lockbox has since been added.
2. Construct literature comparison for `fixed controller reused 10 rounds` versus PACE/SEA/SGM-style sequential evidence controls, keeping statistical guarantees and real-system evidence separate.
3. Find a real agent/post-training study that inserts anytime-valid confidence sequences/e-processes or alpha/error spending into a >5-round adaptive controller loop; this remains the key missing composition.

Priority B — causal feedback credit:
4. Search 2026-08 follow-ons using density-matched or structure-preserving placebos for agent self-improvement. Prefer experiments where feedback alignment is broken while prompt/history/candidate budget remain matched.
5. Look for analogous verifier-audit reversals outside test generation (tool use, coding agents, research agents).

Priority C — adaptive goal generation:
6. Verify SPADE full paper/repo ablation tables for document grounding, environment memory, regret/hint mechanism, curriculum diversity, and failure modes; compare to fixed/random environment generation under matched RL compute.

Priority D — artifact-path validation:
7. Inspect A-Evolve opt-in recipes and any released Adaptive Auto-Harness path to determine where strong gates actually execute. Require executable-path evidence, not docs-only claims.

Exact continuation: start with BaT's current repository/issues and paper appendices for repeated-track semantics / outer lockbox, then branch to SPADE quantitative ablations if no new sequential-control integration appears.
