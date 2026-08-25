# Long Horizon external research — clean_g1 checkpoint — 2026-08-26 04:00 JST

## Boundary / provenance
- Generation: `clean_g1`.
- Worker: `long_horizon`.
- Effective repository control was read first: `automation_control/DESIRED_STATE.json`, control_revision 6, role `long_horizon`, config_revision 3, enabled_desired=true, control blob `9d466043149f4d7276896dcfa4d18b9bfc210ac0`.
- Own sanitized feedback `research_feedback_clean_g1/long_horizon/FEEDBACK.json` blob `9836c7853800e6245493d1fd74f90d768290fc21` was read and applied. No shared `EXECUTION_LEDGER.json`, no other-role receipt, no O/O-derived state, no other worker, no comparator/integrator/index/feed, and no legacy/pre-independence research were read semantically.
- `LATEST.json` remains absent. Repository chronology selected own source-qualified `CHECKPOINT_2026-08-26T0300JST.md` blob `4f2e64ef156ae27e2c0a41b86fdd014d1febec0c` as continuation authority. Older `STATE.md` was not used to override that checkpoint.

## Search target this run
Continue the 03:00 frontier in two steps:
1. look for a public Hydra implementation/raw Figure-7 data or independent fixed-substrate replication exposing exact rollback-policy samples/quantiles;
2. look for a recent GUI/tool-agent runtime where rollback/review granularity or target position is experimentally varied on a common substrate, while preserving the strict distinction between intervention timing, rollback depth/target, restoration mechanics, and retry budget.

## Finding A — no public Hydra code/data artifact located in this search
Primary paper retained from the previous checkpoint: Alexander Du, Jianjun Ou, Danyang Zhuo, Matthew Lentz, `Hydra: Efficient, Correct Code Generation via Checkpoint-and-Rollback Support`, arXiv:2605.15238v1.
- Abstract: https://arxiv.org/abs/2605.15238
- PDF: https://arxiv.org/pdf/2605.15238

Searches by exact title, arXiv id, authors, `TokPol`, `TokPolK`, and GitHub/code/artifact terms did not locate an official public Hydra repository or raw Figure-7 dataset. The PDF itself contains no `github.com`, `code available`, or `artifact` string in the indexed text. This is only a bounded search result: **no artifact was located**, not a claim that no artifact exists.

The primary PDF still supports the previous scope guard: Appendix E holds checker implementation, checkpoint interval, prompts, and sampling fixed across Random/Backwards/Entropy/TokPol and changes rollback-node policy, but retry semantics differ, so this remains a near-direct policy comparison rather than a literal equal-budget selector-only causal isolation.

## Finding B — Speculative Rollback Correction gives a GUI-agent intervention-granularity ablation, and official code is public
Primary paper: Longkun Hao et al., `Speculative Rollback Correction for Quality-Diverse Web Agent Imitation`, arXiv:2606.12485v2, revised 2026-08-17.
- Abstract: https://arxiv.org/abs/2606.12485
- Official code: https://github.com/LongkunHao/SRC_gui_agent

### Mechanism
SRC runs the student for a fixed speculative branch horizon `K`, then a teacher reviews the branch. If local progress breaks, the teacher identifies the **earliest harmful step** in that branch, the environment is reset/replayed to the accepted prefix, one corrective action is applied, and the student resumes. Successful verifier-passing trajectories are retained in a quality-diversity archive.

The official `src/rollout_agent.py` confirms the operational substrate:
- `K` is a configurable branch horizon;
- rollback is implemented by reset-and-replay to a chosen prefix;
- agent running state is truncated to the same prefix;
- the teacher correction is generated after rollback;
- the replay log is canonical per task.

This is valuable because the mechanism exposes a concrete GUI-agent rollback primitive and a tunable **review horizon** on the same codebase.

### Main comparative results reported by the paper
WebArena-Infinity success rate:
- Base: 15.8
- Expert SFT: 25.3
- SRC teacher-assisted collector: 42.5
- OEC-style random expert switch: 20.4
- LEAP-style post-hoc correction: 31.8
- final Expert SFT + SRC data: 35.0

WebArena-Lite:
- Base: 15.2
- Expert SFT: 20.5
- SRC collector: 36.0
- OEC-style: 17.0
- LEAP-style: 26.8
- final SRC: 24.0

OSWorld subset:
- Base: 23.47
- Expert SFT: 27.22
- SRC collector: 43.27
- final SRC: 40.15

These rows alter collection/intervention strategy and are not rollback-target-only comparisons.

### Review-horizon ablation — same framework, but not a pure target-selector ablation
The paper varies branch review horizon `K`:
- K=1: success 45.6; review queries 2603; interventions 721; total teacher queries 3324; average rollback length 1.00; acceptance rate 63.7%.
- K=3: success 51.9; review queries 1744; interventions 785; total 2529; average rollback 2.20; acceptance 37.1%.
- K=5: success 50.6; total teacher queries 2589; average rollback 2.73; acceptance 23.0%.
- K=7: success 50.6; total teacher queries 1831; average rollback 3.43; acceptance 20.9%.

Scope-bounded interpretation:
- per-step review is not automatically best; K=3 improves success while using fewer total teacher queries than K=1;
- longer horizons reduce review frequency but can allow a harmful suffix to persist longer before localization;
- there is an intervention-granularity optimum in this tested setup rather than monotonic `review more often = better`.

However, changing `K` changes **when review/alarm evidence is available and the length/location of the candidate harmful suffix**. It therefore does not isolate historical checkpoint target selection while holding the alarm fixed. This study narrows a neighboring control variable: *review/intervention horizon*.

## Finding C — a clean fixed-depth rollback ablation exists at token-level reasoning, with strong domain limits
Primary: Manan Gupta, Dhruv Kumar, `Latent Phase-Shift Rollback: Inference-Time Error Correction via Residual Stream Monitoring and KV-Cache Steering`, arXiv:2604.18567v1.
- Abstract: https://arxiv.org/abs/2604.18567
- PDF: https://arxiv.org/pdf/2604.18567

LPSR detects a latent phase shift with a cosine-similarity + entropy gate, rolls back the KV cache, and injects a steering vector. The main MATH-500 result is 44.0% for LPSR vs 28.8% standard autoregressive generation on the 8B setup.

### Exact rollback-depth ablation from primary Table 11
On a 100-problem MATH-500 validation split, rollback depth is varied while the LPSR setup is otherwise held fixed:
- depth 0 / no rollback: 0.288 accuracy
- depth 1: **0.443**
- depth 2: 0.418
- depth 3: 0.391

The paper states that exactly one-token rollback is optimal in this setting; larger rollback reduces accuracy. This is direct negative evidence against a universal `deeper rollback is safer` rule.

Additional scope constraints from the same primary source:
- the detector is high-precision/low-recall and domain-calibrated;
- the steering basis is calibrated on MATH data;
- preliminary HumanEval transfer improves only +2.1%; immediate cross-domain transfer is weak;
- many-rollbacks overhead can reach 10× standard AR and a budget constraint was not studied.

Therefore this is a useful **depth-control precedent**, not evidence for checkpoint-target selection in GUI/tool agents. Token rollback depth and historical semantic checkpoint selection must remain separate variables.

## Finding D — a public GUI rollback substrate now exists for a future selector-only experiment
The official SRC repository is directly reusable as a concrete experimental substrate: it already has deterministic reset-and-replay, a canonical action log, a teacher reviewer returning an earliest harmful index, and configurable `K`/intervention budgets. A future matched experiment could freeze:
- task/model/student/teacher;
- branch review events;
- exact teacher judgment and alarm evidence;
- candidate prefix checkpoints within the reviewed branch;
- reset/replay mechanics;
- correction generation and retry/token budget;
then swap only the historical target rule (earliest harmful, latest prior step, fixed depth, random eligible prefix, value/cost-ranked, causal/root-cause ranked).

This is a **design opportunity inferred from the public artifact**, not a published result. No such selector-only experiment was found in the SRC paper/code during this run.

## Updated target-selector gap
The gap remains open but is more sharply factored:
1. Hydra gives a restricted compiler-error rollback-policy comparison on a strongly matched substrate, but retry-policy memory/budgets differ and the key metric is efficiency.
2. SRC gives a GUI-agent review-horizon/intervention-granularity ablation and a public rollback runtime, but changes alarm timing/harmful-suffix opportunity, not only target selection.
3. LPSR gives an otherwise-fixed **rollback-depth** ablation, but at token-level mathematical reasoning with latent steering, not tool/GUI history.

No primary experiment was located in this run that simultaneously fixes **alarm events, candidate checkpoint set, restoration/carryover mechanics, model/prompt/sampling, and literal retry/token budget**, then varies only historical rollback target and reports final tool/GUI/software-agent task success.

## New/strengthened negative evidence
- `Review every step`: not universally optimal; SRC K=3 beats K=1 on the reported success/query tradeoff.
- `Longer review horizon is always better`: false in SRC; K=5/7 do not improve success over K=3.
- `Rollback farther is always safer`: false in LPSR's MATH validation; depth 1 > depth 2 > depth 3.
- `Hydra proves target ranking alone`: still false; retry scheduling/adaptive posterior are part of the compared policy.
- `A GUI rollback implementation implies selector evidence`: false; SRC code provides the substrate but not the strict target-selector causal comparison.

## Nonempty frontier
1. **Exact equal-budget target-selector factorial in a GUI/tool/software agent** remains highest value.
2. **SRC-based selector isolation**: look for follow-up/branch using the released reset-and-replay runtime with fixed review events and target-only policy swaps.
3. **Hydra raw Figure-7 artifact**: continue looking for author supplementary/code/data or exact quantiles; do not infer medians from the CDF.
4. **Alarm timing × target depth factorial**: jointly but independently vary review horizon/alarm cadence and target position, because SRC shows timing matters and LPSR shows depth matters.
5. **False-alarm target behavior**: compare target depth under interventions that can disrupt a trajectory that would otherwise succeed.
6. **Causal object × temporal target**: separate which state object is faulty from which historical checkpoint is selected.
7. **Effect safety**: historical rollback must remain separate from compensable/irreversible external effects.
8. **Subgoal/folding negative evidence** remains open: wrong decomposition, stale folded state, and aggressive compression causing downstream degradation.

## Exact continuation
Next run first action: search for SRC follow-up branches/papers or other GUI/tool-agent runtimes that expose the rollback target as a pluggable policy while holding review/alarm events fixed. Prefer an experiment with identical candidate checkpoints, reset/replay/carryover, model/teacher, correction generation and literal retry/token budget; require final task success in addition to query/latency cost. In parallel, continue a bounded search for Hydra supplementary/raw Figure-7 samples. If no selector-only general-agent study exists, preserve this gap explicitly rather than treating SRC's review-horizon or LPSR's token-depth ablation as equivalent. Keep at least one unresolved frontier branch after checkpointing.
