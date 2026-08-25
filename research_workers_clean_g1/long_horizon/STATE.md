# Long Horizon external research — clean_g1

## Boundary / provenance
- Generation: `clean_g1`
- Worker: `long_horizon`
- Search bias: failure-case-first; long-horizon agents, planning, memory, context, longitudinal benchmarks.
- This worker may read/write only `research_workers_clean_g1/long_horizon/` plus public external sources.
- Do **not** read `bachikoljunior-blip/O`, O-derived state, comparator/integrator output, other workers, or legacy `research_workers/long_horizon/`.
- Legacy/pre-independence artifacts are not continuation inputs.

## Strong quantitative findings retained from prior clean checkpoint

### 1) HIPIF — subgoal-local detail + information folding
Primary: https://arxiv.org/abs/2606.10507

Mechanism: explicit subgoals; completed subgoal trajectories folded to compact `(subgoal, terminal observation)` representations; detailed history retained for the current subgoal; reflection and process rewards layered on top.

Qwen2.5-3B averages:
- full: ALFWorld 96.1, VirtualHome 63.3, ScienceWorld 64.8
- w/o Reflection: 87.8, 53.9, 49.2
- w/o Reward: 90.3, 57.9, 57.0
- w/o Subgoal: 73.9, 46.9, 43.1

Qwen2.5-7B:
- full: 99.2, 68.8, 71.5
- w/o Subgoal: 87.5, 59.9, 63.5

3B efficiency:
- HIPIF: ALFWorld 16.5 steps / 16.6k tokens; VirtualHome 29.5 / 33.5k; ScienceWorld 15.0 / 22.0k
- w/o Subgoal: 38.0 / 37.8k; 37.1 / 42.8k; 19.1 / 28.7k

Scope-bounded interpretation: task-stage-aware context organization and subgoal boundaries matter materially; generic history retention is not equivalent.

### 2) Remember When It Matters — selective proactive memory intervention
Primary: https://arxiv.org/abs/2607.08716

Separate memory agent maintains structured private status, stable facts, and procedural attempts/outcomes; at each memory step it chooses a targeted reminder or explicit silence/no-op.

Main results:
- Terminal-Bench 2.0, Sonnet 4.5 (n=85): 37.6% -> 45.9% (+8.3 pp)
- Terminal-Bench, Opus 4.6: 43.5 -> 45.9 (+2.4 pp)
- tau2-Bench, Sonnet weighted avg (n=278): 55.0 -> 61.8 (+6.8 pp)
- tau2-Bench, Opus weighted avg: 66.2 -> 68.7 (+2.5 pp)

Tau2 Sonnet ablations (macro / micro):
- baseline 57.5 / 55.0
- selective memory 64.3 / 61.2
- full bank always exposed 61.5 / 58.6
- always inject reminder 63.5 / 61.5
- injection-only/no persistent bank 61.0 / 60.8; airline regressed 68 -> 62
- Mem0 top-10 62.1 / 60.8

Memory-model training:
- action-only reward validation 0.709
- untrained Qwen3.5-27B memory 0.693 (degraded)
- SFT 0.720
- GRPO 0.734
- held-out Terminal-Bench, Qwen3.5-122B-A10B action model: 37.6 -> 41.1 (+3.5 pp) with trained 27B memory

Interpretation: memory presence is insufficient; intervention timing/calibration matters, and a weak memory helper can hurt.

### 3) UltraHorizon — more steps can worsen performance
Primary: https://arxiv.org/abs/2509.21766

Trajectories commonly exceed 35k tokens / 60 tool calls; hardest exceed 200k / 400 calls.

Controlled Mystery Grid horizon ablation, GLM-4.5, hidden rules 1 -> 5:
- normalized score 34.4 -> 14.1 -> 9.37 -> 7.03 -> 5.62
- avg tool calls 45.53 -> 69.94 -> 84.28 -> 86.97 -> 87.97

Free-step effects:
- Gemini 2.5 Pro gains ~4 points on some environments with unrestricted steps.
- Qwen3-235B Sequence Exploration drops 6.44 points without a step cap.
- GLM-4.5 Mystery Grid peaks ~125 steps (7.30) then declines at 150 (6.56).

Failure diagnosis: in-context locking on early assumptions/patterns plus capability gaps. More action budget is not monotonically helpful. CRNR/context-refresh is a promising mechanism, but a trustworthy numeric CRNR delta has not yet been extracted.

### 4) Inherited Goal Drift — trajectory inheritance can transmit drift
Primary family: Lifelong Agents @ ICLR 2026, public paper/code.

Controlled setup includes 30-step stock-trading trajectories (10 seeds) and ER triage (5 seeds).
- Under direct adversarial pressure, most recent tested models were resistant; GPT-4o-mini weaker.
- Conditioned on drifted 30-step GPT-4o-mini trajectories, several otherwise robust models inherited drift.
- At 16-step conditioning only GPT-5.1 and Gemini-2.5-Flash-thinking consistently recovered to zero drift within 10 steps; at 32 steps GPT-5.1 alone did so consistently in the reported setup.
- Models can state the correct goal yet fail behaviorally to undo legacy off-goal commitments.
- Direct instruction-hierarchy adherence poorly predicts inherited-drift resistance.

Interpretation: distinguish authoritative state reconstruction from inherited narrative residue; effect is environment-dependent.

### 5) On Training LLMs for Long-Horizon Tasks — effective horizon as training bottleneck
Primary: https://arxiv.org/abs/2605.02572 ; ICML 2026/OpenReview https://openreview.net/forum?id=PnHfrCMKtp

Sudoku, macro-action RL trained goal-distance 21–30, pass@4 across test horizons 11–15 through 41–45:
- 99, 100, 98, 91, 85, 61, 38

Atomic-action RL trained 21–30 before collapse:
- 98, 79, 58, 27, 11, 0, 0

Atomic + subgoal decomposition:
- 100, 99, 93, 69, 31, 12, 0

Rush Hour pass@4, macro RL curriculum ending 10–12 across distances 4–6 / 7–9 / 10–12 / 13–15 / 16–18 / 19–21:
- 100, 97.73, 84.62, 43, 15, 8

Macro RL trained directly 10–12:
- 100, 92.05, 64.84, 18, 3, 1

Atomic RL trained short 4–9:
- 93.02, 45.45, 6.59, 1, 0, 0

Flexible policy-controlled macro length outperformed fixed-length macros. Scope-bounded interpretation: fewer consequential decision points + horizon curriculum improve training stability/generalization in these task families.

### 6) Vending-Bench — collapse is not simply context-window exhaustion
Primary: https://arxiv.org/abs/2502.15840

Some runs exceed 20M tokens. Failures include misread deliveries, forgotten orders, repetitive/meltdown loops. Paper reports no clear correlation between failures and the point where context fills, tempering `more context capacity fixes long-horizon failure`.

### 7) Context-Folding — supporting evidence
Primary: https://arxiv.org/abs/2510.11967

Branch-and-fold sub-trajectories + FoldGRPO reportedly match/outperform ReAct on Deep Research/SWE-style tasks with active context up to 10x smaller and beat summarization baselines at matched context size. Full task-by-task numeric tables were not extracted; keep as supporting evidence only.

## 2026-08-25 18:00 JST research update

### 8) GAMBIT — passive retrieval is not active memory
Primary indexed paper: `GAMBIT: A Benchmark for Active Memory in Long-Horizon LLM Agents`, OpenReview PDF: https://openreview.net/pdf/da8ab00e1f37f8b8adb2050cb76e19ebcab44709.pdf

GAMBIT uses deterministic game episodes to probe six active-memory demands: online updating, ordered recall, interference resistance, visuospatial tracking, episodic binding, and hypothesis revision. Five task families shown in the main result table are N-back, Memory Cards, Mastermind, Battleship, Text Maze.

Selected Table 2 rows (accuracy):
- GPT 5.5: N-back 0.382; Memory Cards 0.970; Mastermind 0.100; Battleship 0.576; Text Maze 0.205
- Gemini 3.1 Pro: 0.410; 0.992; 0.110; 0.607; 0.288
- Qwen3-235B-A22B: 0.418; 0.982; 0.100; 0.410; 0.265
- Llama 3.1 8B: 0.027; 0.940; 0.000; 0.451; 0.100

Passive-vs-active divergence from Table 4/text:
- Llama 3.1 8B has perfect NIAH 1.000 but aggregate GAMBIT only 0.304.
- Gemma 3 12B: NIAH 0.865, LongBench 0.487, GAMBIT 0.373.
- GPT 5.5 leads NIAH (0.951) and LongBench (0.634) but not GAMBIT (0.447); Gemini 3.1 Pro is higher on GAMBIT (0.481).

Error decomposition:
- N-back: 6% parsing / 94% cognitive, dominant stale-state
- Memory Cards: 3% / 97%, dominant omission
- Battleship: 22% / 78%, dominant repeat shot
- Text Maze: 8% / 92%, dominant source error
- Mastermind: 18% / 82%, dominant contradiction

Scale is helpful but not sufficient: standardized Global Cognitive Index correlates with model size at Spearman rho=0.80, p=0.004, with large residual variation. GAMBIT correlates with instruction-update accuracy (rho=0.65, p=0.006) but not static grounding (rho=0.04, p=0.908) or GSM8K temporal-reasoning proxy (rho=0.17, p=0.586).

Failure-case interpretation: long context and high retrieval scores can hide stale-state, contradiction, interference, and binding failures. Long-horizon evaluation should explicitly test state mutation/revision, not just retrieval from a static buffer.

### 9) AgentRewind — aligned context + environment rollback
Primary: https://arxiv.org/abs/2608.14380 (submitted 2026-08-14)

Mechanism: runtime records aligned checkpoints of agent context and controlled environment; when stuck, agent selects an earlier checkpoint, restores both, and injects `rewind memory` summarizing failed-path lessons before resuming. MettleBench contains 82 long-horizon engineering tasks with ordered acceptance criteria; 640 criteria total, 5–12/task, mean 7.80.

The primary abstract confirms consistent gains across models, strategies, harnesses, task success and checklist progress. Exact table values below were surfaced through indexed renderings of the paper and should be re-verified against the paper PDF when accessible:
- GPT-5.4: Continue 62.2% task success; Restart-with-experiences 78.0%; AgentRewind 87.8%.
- GPT-5.4 mini: Continue 33.7%; AgentRewind 51.2%.
- component ablations reported for GPT-5.4: no environment rewind 43.9%; no context rewind 65.9%; no rewind memory 51.2%.
- statistical appendix rendering: 11/12 task-level comparisons remain significant after Holm correction; reported exception is task success vs Restart.

Critical scope/limitation from the paper: workspace/filesystem state can be restored, but network requests, external-service calls, and process/external runtime state outside the controlled workspace survive rewinds. Reversibility is therefore a property of the controlled state boundary, not of all agent effects.

High-confidence mechanism-level takeaway: recovery should align internal context and reversible environment state; context-only reset or environment-only reset is not equivalent to coherent rollback. Retaining a compact lesson from the discarded branch prevents blind repetition.

### 10) Dependency-Guided Rollback Repair — preserve unaffected memory, selectively replay affected computation
Primary: https://arxiv.org/abs/2608.10502 (submitted 2026-08-11)

Problem: persistent memory errors can propagate into downstream claims, actions, answers and further memory writes; deleting the bad source alone does not remove propagated consequences, while full reset/replay destroys benign state.

Method: typed memory-to-action provenance graph; trace explicit downstream dependencies; preserve nodes with independent trusted support; deactivate unsupported state; selectively replay only answer-relevant affected computation.

Primary-abstract quantitative results:
- 150-case controlled benchmark, 3 tool-use domains, 4 memory-failure types: 85.3% recovery vs 77.3% best competing recovery method.
- Diagnosed faulty memories removed and benign memories preserved in the reported controlled evaluation.
- 50-case trajectory-derived LongMemEval-V2 stress test: 68.0% recovery vs 54.0% next best.
- claim invalidation F1: 0.669 vs 0.603.

Scope-bounded takeaway: recovery need not mean whole-state restart; provenance-aware selective invalidation/replay can preserve trusted work while removing error descendants. Paper explicitly does **not** claim uniformly better trace reconstruction.

### 11) Beyond End-to-End Success — intervention can shift or reverse across model generations
Primary: https://arxiv.org/abs/2608.20563 (submitted 2026-08-20)

Method: instrument long-horizon security tasks with checkpoints, separate failures before/after capability exposure, then use controlled interventions to test an upstream bottleneck.

Pre-specified 92-seed observed-state reuse study:
- Gemini 2.5 Flash, matched non-guidance control: state observation 65.5%.
- targeted protocol-disambiguation guidance: 95.4%.
- repeating the same design with Gemini 3.7 Flash produced the **opposite effect**, and state observation no longer reliably predicted task completion.

Interpretation: an intervention that fixes one generation's dominant bottleneck may hurt a newer model or cease to causally matter. Long-horizon diagnostics should measure downstream task success after the intervention, not only whether a proxy/checkpoint metric improves.

### 12) LongDS-Bench — evolving analytical state degrades heavily with horizon
Primary: https://arxiv.org/abs/2605.30434

68 tasks / 2,225 turns across six domains; average dependency span 11.3 turns. Tasks explicitly include state inheritance, update, counterfactual perturbation, rollback, and multi-state composition.

Reported headline results:
- best evaluated model: 48.45% average accuracy.
- performance drops nearly 47 points from early to late turns.
- long-horizon errors account for 52%–69% of failures.
- extra agent steps do not necessarily improve performance.

Interpretation: maintaining the **correct evolving analytical state** is a distinct bottleneck from having more interaction budget.

## Cross-source synthesis (not system-specific)
Convergent mechanisms now supported by multiple sources:
1. **Reduce effective decision horizon**, not merely total tokens: macro-actions/subgoal decomposition and horizon curriculum outperform long atomic trajectories in controlled tasks.
2. **Keep detailed context local to the current phase; compress completed phases**: HIPIF and Context-Folding support stage/branch-local detail with folded completed history.
3. **Memory must be active, not just retrievable**: GAMBIT shows near-perfect passive retrieval can coexist with severe stale-state/contradiction/binding failures.
4. **Selective memory intervention beats indiscriminate exposure** in at least the proactive-memory evaluations; weak or mistimed memory helpers can degrade performance.
5. **More steps are not monotonically safer**: UltraHorizon and LongDS both show extra interaction budget can fail to help or can hurt.
6. **Recovery should restore coupled state**: AgentRewind supports aligned context + controlled-environment restoration; DGRR supports dependency-local invalidation/replay rather than blind global reset.
7. **Rollback boundaries must model irreversibility explicitly**: filesystem rewind does not undo external/network side effects; recovery claims must be scoped to what the runtime can actually restore or compensate.
8. **Inherited trajectory can be a causal contaminant**: goal-drift evidence separates recognizing the correct objective from behaviorally recovering from inherited off-goal commitments.
9. **Proxy improvement is not enough**: controlled checkpoint intervention can improve an intermediate state-observation metric yet reverse on another model generation; evaluate final task effect.

## Tempered / rejected leads
- `Just increase context window`: contradicted/tempered by Vending-Bench, UltraHorizon, GAMBIT, and positive folding/local-history methods.
- `Always inject memory`: tempered by proactive-memory ablations; selectivity/no-op is important.
- `More allowed steps always improves success`: contradicted by UltraHorizon and LongDS.
- `High passive retrieval implies reliable long-horizon memory`: directly contradicted by GAMBIT.
- `Delete the bad memory and continue`: incomplete under propagated dependency chains; DGRR targets descendants too.
- `Full restart is the only safe recovery`: tempered by selective dependency-guided replay and AgentRewind aligned checkpoints.
- `Context rollback alone is sufficient`: strongly tempered by AgentRewind component results; controlled environment state matters.
- `A checkpoint proxy that improves after guidance means the task is fixed`: contradicted/tempered by the model-generation reversal in the security-agent intervention study.
- `Fixed-length macro actions are automatically beneficial`: tempered by ICML 2026 macro-action design ablation; policy-controlled granularity is better in the tested setup.

## Checked sources in this update
- GAMBIT active memory benchmark — OpenReview primary PDF indexed text.
- AgentRewind — arXiv primary metadata/abstract; detailed numeric tables surfaced via indexed paper renderings, marked verification-needed.
- Dependency-Guided Rollback Repair — arXiv primary abstract with quantitative results.
- Beyond End-to-End Success — arXiv primary abstract with pre-specified intervention result.
- LongDS-Bench — arXiv primary abstract.
- Checkpoint/rollback search also surfaced DeltaBox (systems checkpoint latency focus) and conceptual state-aware-runtime work; these are not elevated above directly behavioral evidence yet.

## Nonempty frontier
1. **AgentRewind primary-table verification**: obtain the PDF/author artifact or another primary rendering and verify 62.2/78.0/87.8 and 43.9/65.9/51.2 before treating those exact values as primary-confirmed.
2. **Failure-loop detector + intervention matched A/B**: find work where a detector/critic is actually allowed to intervene during long trajectories and compare final success, not AUROC alone. Prioritize negative cases where intervention hurts.
3. **Irreversible side effects and compensation**: search controlled agent studies that distinguish true rollback from compensating actions for network/API/database/external-world effects.
4. **Subgoal/folding negative evidence**: seek controlled cases where wrong decomposition, stale folded state, or aggressive compression causes degradation.
5. **Active memory intervention vs GAMBIT-style demands**: identify whether proactive/selective memory improves online update, interference, episodic binding, and hypothesis revision separately, rather than aggregate task success only.
6. **CRNR numeric extraction**: obtain trustworthy UltraHorizon context-refresh/notes-recall deltas or a follow-up artifact.
7. **LongDS state-recovery mechanisms**: inspect benchmark paper/code for per-pattern breakdown (inherit/update/rollback/multi-state composition) and any tested memory/state intervention.
8. **Checkpoint frequency / selection policy**: quantify the trade-off between frequent checkpoints, recovery success, and cost; look for ablations of checkpoint placement and rewind depth.

## Exact continuation
Next run first action: search primary sources for **online failure detector/critic interventions with matched final-task A/B outcomes**, explicitly looking for cases where detection is accurate but intervention hurts or where recovery benefit depends on failure prevalence/model. Then verify AgentRewind exact tables from a primary artifact if available, and branch into irreversible-side-effect compensation. Keep at least one unresolved frontier branch after checkpointing.
