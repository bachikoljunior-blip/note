# Self Improvement Scan — clean_g1 checkpoint

Run time: 2026-08-25 21:59 JST
Generation: clean_g1
Search bias: benchmark-first / ablation-first self-improvement and meta-learning; prefer primary quantitative evidence, matched controls, held-out transfer, and explicit failure scope.

## Independence / continuity boundary

Semantic continuation for this run used only `checkpoint_2026-08-25T2102_JST_clean_g1_turn1.md` plus public sources. No O repository/state, comparator output, integrator/index/feed output, legacy/pre_independence research, or other-worker state was read. The worker-specific sanitized feedback file was read only for a mechanical ID-stability correction and acknowledged; it was not used to steer hypotheses.

An older `STATE.md` in this same worker namespace was opened before the latest checkpoint was discovered. Its content was discarded and was not used for candidate choice, quantitative claims, synthesis, or frontier selection. All evidence below was independently re-established from the 21:02 clean checkpoint and public primary sources.

## New primary evidence

### SRC-HYPERAGENTS-PARENTSEL — Editable parent selection is learnable, but did not beat the handcrafted selector

Primary: Hyperagents, arXiv:2603.19461, Appendix E.5.

The previous clean checkpoint established that full DGM-H outperformed compound ablations without meta self-improvement or open-ended exploration, but it did not isolate specific internal meta mechanisms such as persistent memory, performance tracking, or parent selection.

Appendix E.5 provides a more granular parent-selection experiment:
- Baseline `random`: random parent selection throughout.
- `modifiable`: initialize from random parent selection and allow the hyperagent to edit the parent-selection mechanism.
- `score-child-prop`: the carefully handcrafted selector used in the main experiments.
- Each method is repeated across 5 runs.
- On held-out paper-review + robotics-reward-design test tasks, average best-agent performance rises from initial 0.030 to:
  - random: **0.428**, CI **0.407–0.432**
  - modifiable: **0.491**, CI **0.387–0.512**
  - handcrafted score-child-prop: **0.532**, CI **0.384–0.586**
- Differences are reported as **not statistically significant (p > 0.05)**.
- Qualitatively, every modifiable run rediscovers structured exploration/exploitation mechanisms such as UCB-style bonuses, temperature-controlled softmax, adaptive exploration weights, diversity/recency bonuses, and stagnation detection.

Interpretation: editable meta-control can rediscover useful search heuristics from a weak random initializer, but this experiment does **not** establish a significant parent-selection advantage and does not beat the handcrafted selector. It therefore narrows the earlier Hyperagents claim: persistent memory/performance tracking remain qualitative correlates of transfer, while parent selection has one explicit granular test whose current evidence is directional but statistically inconclusive.

Scope limits:
- This is not an ablation of persistent memory or performance tracking.
- The modifiable selector begins from random, whereas score-child-prop begins from a strong human prior; the comparison is not an equal-initialization test of learned-vs-fixed selector quality.
- The result should not be generalized to arbitrary archive search algorithms.

### SRC-SKILLPROX-PROX — Counterfactual deletion can improve evolved skills; forward gates and retrospective shrinkage act at different timescales

Primary: SkillProx: Self-Evolving Agent Skills via Proximal Textual Gradient Descent, arXiv:2608.07449, submitted 2026-08-07.

Mechanism:
- Forward stage: diagnose an edit, patch, re-execute on the same task batch, accept only non-regressive candidates, otherwise rollback/retry and feed measured rejection outcomes into later diagnoses.
- Backward stage: decompose the evolved skill into auditable units, run a **frozen leave-one-out utility audit** on a validation split, then validation-gate consolidation/demotion/removal.
- A negative unit utility means that removing the unit improves validation performance.

Direct evidence:
- A representative utility-aware consolidation removes **3.12%** of skill size while improving OJ hard accuracy **46% → 54%**.
- SpreadsheetBench component ablation with Qwen3.6-27B:
  - w/o closed-loop diagnosis: **53.0 ± 1.0**
  - w/o Prox: **52.0 ± 1.0**
  - full SkillProx: **54.5 ± 0.5**
  Thus the backward proximal stage contributes **+2.5 pp** over forward-only, while the closed-loop stage contributes **+1.5 pp** over Prox-only in this matched setup.
- Threshold sweep on closed-loop skills: no-Prox anchor **50.3%**; at tau=-0.001, **52.3%** with **25.7% compression**; at tau=0.005, **52.0%** with **41.5% compression**; even at tau=0.050, **74.9%** of skill text is removed while retaining **51.0%**. Performance begins to decline beyond roughly 80% compression.
- Ten-seed matched open-loop vs closed-loop forward comparison: six wins, two ties, two losses; mean hard gain **+1.10 pp**, cross-seed std falls **2.50 → 1.51**, minimum rises **46 → 49**. The paper's cautious interpretation is lower-tail stabilization rather than uniform upper-bound improvement.
- In one gate trace, 10 iterations generate 22 edit attempts; **8 hard regressions are blocked**, and one entire iteration is reverted.
- Closed-loop alone still leaves negative-utility content detectable on broader validation, motivating the separate backward audit.

OOD/main-table evidence:
- Across Qwen3.5-4B, Qwen3.5-27B, and Qwen3.6-27B, SkillProx is strongest or competitive on SpreadsheetBench IID and WikiTQ/HiTab OOD; the abstract reports **+3.0 pp average** over the strongest gradient-based baseline.

Interpretation: this is direct evidence for a two-timescale acceptance architecture: immediate same-batch rollback intercepts obvious harmful updates, while later counterfactual deletion on a broader held-out panel can remove content whose harm was invisible at write time. More persistent text is not monotonically better.

Scope limits:
- The representative 46→54 deletion case is a case study, not an average treatment effect.
- The utility audit is frozen before Prox; interactions can change after earlier edits, so every realized shrink trial is re-evaluated.
- One appendix case uses only 20 validation tasks, so small-panel uncertainty remains relevant.

### SRC-SKILLSV-VALUATION — Structure-aware counterfactual deletion separates content value from context cost and supports disjoint-panel pruning

Primary: What Is a Skill Worth? Structure-Aware Shapley Valuation of Agent Skills, arXiv:2608.04562, submitted 2026-08-05.

SkillSV treats a fixed optimized skill as a structured artifact and asks which internal units are causally useful under held-out tasks. Key methodological controls:
- Compile units, dependencies, and hierarchy so deletion counterfactuals remain valid skills rather than malformed prompts.
- Use paired hard deletion and **length-neutral padding** to separate semantic content value from prompt-length/context cost.
- Evaluate only feasible structure-respecting coalitions; plain leave-one-out can misvalue redundant or complementary units.
- Use panel A to estimate values; perform one attribution-guided refinement; evaluate the revised skill once on **disjoint panel B**.

Quantitative evidence:
- Pooled pruning AUC is higher than Closure-LOO by **+0.026**, an LLM judge by **+0.049**, and random by **+0.082**; reported 95% CIs do not include zero.
- After SkillSV-guided single-step refinement, retained token fractions and held-out changes are:
  - LiveMath: 96% tokens, **61.3 → 56.5**, delta −4.8, CI [−14.5,+4.8]
  - OfficeQA: 80%, **64.0 → 65.1**, +1.2, CI [−7.0,+9.3]
  - Spreadsheet: 57%, **73.6 → 73.6**, 0.0, CI [−5.0,+5.0]
  - ALFWorld: 42%, **89.1 → 87.5**, −1.6, CI [−9.4,+4.7]
  - Mean retained tokens: **69%**; mean score change **−1.3**, with no benchmark showing a statistically significant change in this table.
- Value is highly concentrated: top 10% of units account for 21% of measured value mass on OfficeQA, 35% LiveMath, 60% Spreadsheet, and 100% ALFWorld.

Interpretation: counterfactual artifact deletion can be made more causally meaningful by respecting dependencies and controlling context length. It also provides a practical diagnostic distinction: positive content with high context cost should be compressed, not simply deleted. This complements SkillProx's evolving-skill shrinkage with a cleaner post-hoc valuation methodology.

Scope limits:
- The method values a **fixed** skill under a fixed agent/distribution; it is not itself an online self-improvement algorithm.
- Safe compression means no significant loss was detected under the reported panel sizes; it is not proof of exact equivalence.
- Shapley-style values depend on the declared feasible-order distribution; the authors do not claim a unique canonical value.

### SRC-SEPO-ARCHIVE — Archive-based open-ended prompt evolution beats latest-only linear search under the same self-referential system

Primary: SePO: Self-Evolving Prompt Agent for System Prompt Optimization, arXiv:2606.04465, submitted 2026-06-03.

SePO optimizes both task-agent system prompts and the prompt agent's own prompt. Its archive retains candidate prompts as stepping stones. A direct component ablation compares:
- full SePO-Generalist
- w/o self-improvement (skip prompt-agent pretraining; use handwritten seed)
- w/o open-ended evolution (replace archive-based search with linear latest-candidate search)

Five-task test accuracy (AIME'25 / ARC-AGI-1 / GPQA / MBPP / Sudoku / average):
- Manual-CoT: 57.55 / 37.30 / 76.46 / 91.20 / 96.95 / **71.89**
- SePO-Generalist: 64.22 / 43.39 / 78.18 / 96.20 / 99.90 / **76.38**
- w/o self-improvement: 62.81 / 39.76 / 76.21 / 95.95 / 99.95 / **74.94**
- w/o open-ended evolution: 57.24 / 41.58 / 73.74 / 91.10 / 99.55 / **72.64**

Thus the average drop from removing prompt-agent self-improvement is **−1.44 pp**, while replacing archive search with latest-only linear search costs **−3.74 pp**. The largest archive-ablation drop is AIME'25, **−6.98 pp**.

Transfer/model robustness:
- With a swapped task/prompt model pair (Gemini 3.1 Flash-Lite Preview / Claude Opus 4.6), SePO-Generalist beats Manual-CoT on all five tasks, average **67.95 → 70.08 (+2.13 pp)**.
- Sudoku is absent from every pretraining mixture yet improves **96.95 → 99.90**, providing limited cross-task evidence that the prompt-improvement procedure is not only memorizing task-specific prompts.
- Generalist pretraining cost is amortized: one **$37.14** pretraining run across five tasks (~$7.43/task) plus $2.41–$15.51/task fine-tuning; inference budget is matched across methods.

Interpretation: this provides an archive-vs-latest-only ablation outside Hyperagents/DGM-H, supporting the stepping-stone hypothesis in a prompt-optimization domain. The effect is still system-specific; it does not prove every population/archive beats every single-lineage search.

Scope limits:
- The archive ablation changes search history availability, not only population size; exact proposal trajectories are not matched one-for-one.
- Reported table values do not by themselves establish statistical significance for each component drop.
- Cross-task transfer spans five benchmark families but remains within prompt optimization and the paper's chosen model pairs.

## Cross-source synthesis (hypotheses, not architecture mandate)

The new evidence sharpens three distinct credit-control problems:

1. **Search-lineage credit:** Hyperagents parent-selection modification and SePO archive ablation show that which ancestors remain reachable changes future improvement quality. A learned selector can rediscover classical exploration heuristics, but a good handcrafted selector still wins in the explicit Hyperagents test; archive availability itself has stronger direct ablation support than unconstrained selector self-modification.
2. **Write-time credit:** SkillProx shows that immediately re-running a proposed edit and rolling back regressions reduces lower-tail failures, but same-batch acceptance misses harms that appear on broader validation.
3. **Persistence credit:** SkillProx and SkillSV show that accumulated text contains low/negative-value or redundant units. Counterfactual deletion should respect artifact structure, be separated from prompt-length effects, and be verified on held-out/disjoint panels before durable removal.

A more evidence-aligned self-improvement loop is therefore not simply `propose -> append -> reuse`. It is closer to:
`maintain multiple viable lineages -> bounded proposal -> immediate outcome gate/rollback -> structured counterfactual audit of accumulated artifacts -> disjoint-panel verification -> versioned persistence`.

This remains a hypothesis synthesized from several bounded systems, not a claim of universal optimality.

## Rejected / narrowed interpretations

- Hyperagents does not currently provide a matched single-feature ablation proving persistent memory or performance tracking causes transfer; these remain qualitative features of transfer hyperagents.
- Editable parent selection does not significantly beat random or handcrafted selection in the reported five-run Hyperagents experiment; do not present it as a proven gain.
- SkillProx's large single-case 46→54 removal gain is not an average effect.
- SkillSV's pruning result is evidence for value-guided compression of fixed skills, not direct proof that online self-improvement improves by 31% token removal.
- SePO's archive benefit is direct within prompt evolution but is not yet a compute-matched universal archive theorem.

## Nonempty frontier

1. Search for **independent replications / failure reports** of SePO, SkillProx, SkillSV, or their closest methods; prioritize released run artifacts over commentary.
2. Find **matched-compute archive/population vs single-lineage** experiments where proposal count, evaluation budget, and selection rule are held fixed more tightly than SePO/Hyperagents.
3. Search for **counterfactual corruption/replacement**, not only deletion, of persistent skills/memory to test whether attribution methods identify sign and dependency correctly under adversarial or stale artifacts.
4. Investigate **adaptive reuse of small held-out panels** in evolving-skill gates: repeated validation queries, selection-induced overfitting, reusable-holdout/sequential-testing defenses, and whether SkillProx/SkillOpt-style validation remains calibrated over many edits.
5. Search for **interaction-aware online pruning**: whether values are recomputed after each accepted change, versus freezing pre-edit utilities, and the empirical cost/benefit of recomputation.
6. Look for a **direct persistent-memory/performance-tracking ablation in Hyperagents** released logs or follow-up work; if absent, keep those mechanisms qualitative rather than causal.
7. Compare **length-neutral padding vs hard deletion** in other agent-memory/skill papers to test whether apparent memory benefit is often context-budget benefit.

## Exact continuation

Next run: open this checkpoint as the only semantic continuation artifact. Start with frontier item 1 by searching public repositories/papers for independent reproduction or failure evidence around SkillProx / SkillSV / SePO. If no credible independent replication exists, branch immediately to item 4 (adaptive reuse of held-out panels) and extract a quantitative sequential-testing/reusable-holdout result applicable to repeated self-improvement gates. Keep source-qualified candidate IDs and checkpoint a nonempty frontier before returning.
