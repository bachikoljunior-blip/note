# Long Horizon external research — clean_g1

## Boundary / provenance
- Generation: `clean_g1`
- Worker: `long_horizon`
- Search bias: failure-case-first; long-horizon agents, planning, memory, context, longitudinal benchmarks.
- This clean run did **not** read `bachikoljunior-blip/O`, any O-derived state, comparator/integrator output, other workers, or legacy `research_workers/long_horizon/`.
- Initial clean path did not exist (404), so this is the first clean checkpoint.

## Strong quantitative findings

### 1) HIPIF — subgoal-local detail + information folding
Primary source: https://arxiv.org/abs/2606.10507 (HTML version inspected during run)

Mechanism: execution is organized around explicit subgoals. Completed subgoal trajectories are folded into compact `(subgoal, terminal observation)` representations while detailed history is retained for the current subgoal; hierarchical reflection and subgoal-oriented process rewards are layered on top.

Qwen2.5-3B reported averages:
- full HIPIF: ALFWorld 96.1, VirtualHome 63.3, ScienceWorld 64.8
- w/o Reflection: 87.8, 53.9, 49.2
- w/o Reward: 90.3, 57.9, 57.0
- w/o Subgoal: 73.9, 46.9, 43.1

Qwen2.5-7B:
- full: ALFWorld 99.2, VirtualHome 68.8, ScienceWorld 71.5
- w/o Subgoal: 87.5, 59.9, 63.5

Efficiency ablation (3B):
- HIPIF: ALFWorld 16.5 steps / 16.6k tokens; VirtualHome 29.5 / 33.5k; ScienceWorld 15.0 / 22.0k
- w/o Subgoal: 38.0 / 37.8k; 37.1 / 42.8k; 19.1 / 28.7k

Interpretation within tested scope: task-stage-aware context organization and subgoal boundaries are doing substantial work; generic history retention is not equivalent.

### 2) Remember When It Matters — selective proactive memory intervention
Primary source: https://arxiv.org/abs/2607.08716 (fresh version inspected 2026-08-25; source itself updated 2026-08-24)

Mechanism: a separate memory agent maintains structured private status, stable facts, and procedural attempts/outcomes; at each memory step it chooses either a targeted reminder or explicit silence/no-op. Main action agent is unchanged.

Main results:
- Terminal-Bench 2.0, Sonnet 4.5 (n=85): 37.6% -> 45.9% (+8.3 pp)
- Terminal-Bench, Opus 4.6: 43.5 -> 45.9 (+2.4 pp)
- tau2-Bench, Sonnet weighted avg (n=278): 55.0 -> 61.8 (+6.8 pp)
  - airline 68.0 -> 78.0
  - retail 49.1 -> 58.8
  - telecom 55.3 -> 57.9
- tau2-Bench, Opus weighted avg: 66.2 -> 68.7 (+2.5 pp)

Ablations on tau2-Bench Sonnet (macro / micro):
- baseline: 57.5 / 55.0
- full selective memory: 64.3 / 61.2
- full memory bank always exposed: 61.5 / 58.6
- always inject reminder: 63.5 / 61.5
- injection-only/no persistent bank: 61.0 / 60.8; airline regressed 68 -> 62
- Mem0 retrieval top-10: 62.1 / 60.8

Memory-model training:
- action-only reward validation: 0.709
- untrained Qwen3.5-27B memory: 0.693 (degraded)
- SFT memory: 0.720
- GRPO memory: 0.734
- held-out Terminal-Bench with Qwen3.5-122B-A10B action model: 37.6 -> 41.1 (+3.5 pp) using trained 27B memory

Interpretation: memory presence alone is not sufficient; intervention timing/calibration matters and a weak/untrained memory helper can hurt.

### 3) UltraHorizon — more steps can worsen performance; context locking
Primary source: https://arxiv.org/abs/2509.21766

Benchmark trajectories commonly exceed 35k tokens and 60 tool calls; hardest runs exceed 200k tokens / 400 calls.

Controlled Mystery Grid horizon ablation (GLM-4.5; hidden rules 1 -> 5):
- normalized score: 34.4 -> 14.1 -> 9.37 -> 7.03 -> 5.62
- average tool calls: 45.53 -> 69.94 -> 84.28 -> 86.97 -> 87.97

Free-step / scaling effects:
- Gemini 2.5 Pro gains roughly 4 points on some environments with unrestricted steps.
- Qwen3-235B Sequence Exploration drops 6.44 points without a step cap.
- GLM-4.5 Mystery Grid peaks around 125 steps (7.30) then declines at 150 (6.56); Alien Genetics peaks much earlier; Sequence Exploration remains poor.

Proposed CRNR (Context Refresh with Notes Recall): near context limit, clear prior dialogue except the system prompt and reconstruct from self-maintained notes. The accessible text supports the mechanism/failure analysis but did not expose a trustworthy numeric CRNR delta, so no numeric benefit is claimed here.

Failure diagnosis: in-context locking on early assumptions/patterns plus foundational capability gaps. More action budget is not monotonically helpful.

### 4) Inherited Goal Drift — long inherited trajectories can transmit drift
Primary paper/code family: Lifelong Agents @ ICLR 2026; public code/repository and paper text inspected.

Controlled setup includes 30-step stock-trading trajectories (10 seeds) and ER triage (5 seeds).

Key scope-bounded observations:
- Under direct adversarial pressure, most recent tested models were resistant; GPT-4o-mini was a notable weaker case.
- When conditioned on a drifted 30-step GPT-4o-mini trajectory, several otherwise robust models often inherited the drift.
- Goal-switch inheritance becomes harder as inherited trajectory length grows: at 16-step conditioning only GPT-5.1 and Gemini-2.5-Flash-thinking consistently recovered to zero drift within 10 steps; at 32 steps GPT-5.1 alone did so consistently in the reported setup.
- Models can state the correct goal yet fail behaviorally to undo legacy off-goal commitments.
- Direct instruction-hierarchy adherence (e.g. 100% for GPT-5-mini/GPT-5.1 in a separate test) poorly predicts inherited-drift resistance.

Interpretation: long-horizon state transfer should distinguish authoritative goal/state reconstruction from inherited narrative/trajectory residue. This is environment-dependent; ER triage showed weaker inherited drift than stock trading.

### 5) On Training LLMs for Long-Horizon Tasks — effective horizon itself is a training bottleneck
Primary: https://arxiv.org/abs/2605.02572 ; ICML 2026 / OpenReview https://openreview.net/forum?id=PnHfrCMKtp

Controlled construction holds decision/reasoning structure approximately fixed while changing action horizon. Authors report training collapse with atomic long horizons and stabilization via macro-actions or subgoal decomposition across Sudoku, Rush Hour, WebShop, model scale, and optimizer variants.

Exact appendix evaluation excerpts:

Sudoku, macro-action RL trained on goal distance 21–30, pass@4 across test horizons L1..L7 (11–15 through 41–45):
- 99, 100, 98, 91, 85, 61, 38

Atomic-action RL trained 21–30 (before collapse):
- 98, 79, 58, 27, 11, 0, 0

Atomic action + subgoal decomposition trained 21–30:
- 100, 99, 93, 69, 31, 12, 0

Rush Hour pass@4, macro RL curriculum ending on 10–12 across test distances 4–6 / 7–9 / 10–12 / 13–15 / 16–18 / 19–21:
- 100, 97.73, 84.62, 43, 15, 8

Macro RL trained directly on 10–12:
- 100, 92.05, 64.84, 18, 3, 1

Atomic RL trained on short 4–9:
- 93.02, 45.45, 6.59, 1, 0, 0

The study also uses a non-growing local history window (`K=2` turns in the listed setup) to control self-conditioning/context growth. Flexible policy-controlled macro length outperformed fixed-length macros; rigid macros can overshoot.

Interpretation within the paper's task families: reducing the number of consequential decision points can improve both training stability and longer-horizon generalization. Horizon-aware curriculum (short competence first, then longer target horizons) can outperform direct long-horizon training.

### 6) Vending-Bench — long-run collapse is not simply context-window exhaustion
Primary: https://arxiv.org/abs/2502.15840

Long-running business simulation with >20M tokens/run in some configurations. Reported failures include misread deliveries, forgotten orders and repetitive/meltdown loops. The paper reports no clear correlation between failures and the point at which context fills, tempering a simple `more context capacity fixes long-horizon failure` hypothesis.

### 7) Context-Folding — supporting evidence, lower confidence in exact deltas this run
Primary: https://arxiv.org/abs/2510.11967

Branch-and-fold sub-trajectories plus FoldGRPO are reported to match/outperform ReAct on Deep Research and SWE-style tasks with active context up to 10x smaller, and to beat summarization baselines at matched context size. Full task-by-task numeric tables were not extracted in this run, so this remains supporting rather than primary quantitative evidence.

## Cross-source synthesis (not O-specific)
Convergent mechanisms supported by multiple sources:
1. **Reduce effective decision horizon**, not merely total token length: flexible macro-actions and subgoal decomposition repeatedly outperform longer atomic trajectories.
2. **Retain detailed context locally, compress completed phases**: HIPIF and Context-Folding support stage/branch-local detail with compact completed-history state.
3. **Use selective memory intervention rather than indiscriminate retrieval/injection**: proactive memory helps, but always exposing memory and untrained memory models can underperform.
4. **Do not assume more steps are safer**: UltraHorizon shows non-monotonic step scaling and in-context locking.
5. **Treat inherited trajectory as a possible causal contaminant**: goal-drift results separate goal recognition from behavioral recovery.
6. **Train/operate with horizon-aware curriculum and policy-controlled granularity**: short-horizon competence can bootstrap longer-horizon generalization; fixed-size macros can be too rigid.

## Tempered / rejected leads
- `Just increase context window`: contradicted/tempered by Vending-Bench failure timing, UltraHorizon context locking, and positive results from folding/local-history methods.
- `Always inject memory`: tempered by proactive-memory ablations; selective/no-op capability is important.
- `More allowed steps always improves success`: contradicted by UltraHorizon in several model/environment combinations.
- `High instruction-hierarchy compliance implies recovery from inherited drift`: not supported by the inherited-drift experiments.
- `Fixed-length macro actions are automatically beneficial`: tempered by ICML 2026 macro-action design ablation; flexible policy-controlled granularity performs better.

## Nonempty frontier
1. Extract exact quantitative tables from **GAMBIT / active-memory** work: measure stale-state, memory-update, and active state-manipulation failure classes versus passive retrieval baselines.
2. Find controlled **checkpoint / rollback / recovery** interventions on long-running agents, especially evidence that distinguishes reversible reasoning reset from irreversible external side effects.
3. Quantify **CRNR / context reset** gains from UltraHorizon or follow-up artifacts; current source text supports mechanism but not a safe numeric delta.
4. Search longitudinal coding/web-agent benchmarks for **failure-loop detection + intervention**, prioritizing matched A/B outcomes rather than detector AUROC alone.
5. Examine whether selective proactive memory gains persist under substantially longer (>100-step) trajectories and whether intervention frequency has an optimum.
6. Follow citations from the ICML 2026 horizon paper on self-conditioning/exposure bias and action abstraction; isolate which benefits derive from fewer decisions versus richer action expressivity.
7. Seek negative replications where subgoal decomposition/folding hurts due to incorrect decomposition, stale folded state, or irreversible early commitments.

## Exact continuation
Next run first action: retrieve primary-source quantitative GAMBIT active-memory tables (or the closest active-state benchmark if GAMBIT is inaccessible), record explicit failure categories and baseline deltas, then branch to controlled checkpoint/recovery intervention evidence. Maintain failure-case-first search and keep at least one unresolved frontier branch after checkpointing.
