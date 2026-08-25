# Self Improvement Scan — CLEAN g1 state

Updated: 2026-08-25T17:25:00+09:00
Generation: clean_g1
Independence: clean generation only. No legacy `research_workers/self_improvement/`, other workers, comparators, integrator output, O, or O-derived state was read. Continuation is only from this file plus public external sources checked in this worker.

## Search bias
Benchmark-first / ablation-first self-improvement and meta-learning. Trace mechanisms backward from quantitative gains, failures, held-out transfer, and matched controls; do not promote architecture claims without evidence.

## Checked sources

1. **The Meta-Agent Challenge (MAC)** — arXiv:2606.04455 (2026-06-03), primary paper.
2. **EvoAgentBench** — arXiv:2607.05202 (2026-07-06), primary abstract + author benchmark page.
3. **MetaSkill-Evolve** — arXiv:2607.05297 (2026-07-06), primary abstract; detailed marginal ablation still pending primary verification.
4. **Knowledge-Centric Self-Improvement (KSI)** — arXiv:2607.19592 (2026-07-21), primary paper + author project page; some exact project-page numbers still pending primary-table cross-check.
5. **Meta-Harness: End-to-End Optimization of Model Harnesses** — arXiv:2603.28052 (2026-03-30), primary HTML.
6. **AutoDesign: Meta-Harness Optimization for Long-Horizon Agentic Design** — arXiv:2608.13560 (2026-08-13), primary HTML.
7. **Recursive Self-Evolving Agents via Held-Out Selection (RSEA)** — arXiv:2606.28374 (2026-06-17), primary HTML; reached independently by following AutoDesign's held-out-selection citation.
8. **Self-Improvements in Modern Agentic Systems: A Survey** — arXiv:2607.13104; used only as a map, not as efficacy evidence.

## Candidate mechanisms / evidence

### C1 — Ability-supported held-out transfer exposes routing/extraction failures
**Source:** EvoAgentBench.

- 528 training / 267 test tasks across web research, algorithmic reasoning, software engineering, and knowledge work.
- Author page reports 24 scaffold–backbone–domain configurations, matched Vanilla baselines, and 3 independent runs per instance.
- Curator-routed **Anchor Skill** improves every configuration, showing useful procedural information exists when extraction/routing is correct.
- No tested automatic method (Memento, ReasoningBank, GEPA) stays positive everywhere.
- Extreme negative transfer: Memento on Nanobot / Qwen3.5-27B / software engineering **45.8 → 9.5 (−36.3 points)**.

**Evidence strength:** strong benchmark evidence for negative transfer; Anchor is a diagnostic oracle-like reference, not an automatic deployable method.

**Mechanism hypothesis:** evaluate self-improvement as `experience → reusable procedure → routing → held-out uptake`, explicitly measuring negative transfer.

### C2 — Autonomous meta-agent development is high-variance and optimization-sensitive
**Source:** MAC.

- Only **5/39** configurations exceed the corresponding human-baseline average; 4/5 use proprietary frontier models.
- **33%** of configurations have run-to-run std > 0.1; human baselines max at **0.053**.
- Claude-Sonnet-4.6 on Meta-GPQA: 0.565, 0.585, 0.000 → **0.383 ± 0.332**.
- Zero-resource red-team: **7/8** trials produced clear policy violations; 1 valid artifact; audit agent matched human verdicts on all 8.
- Meta-SWE-Bench example: Claude-Opus-4.7/Claude Code **0.609 ± 0.064** vs Terminus-2 human baseline **0.637 ± 0.030**.

**Evidence strength:** strong primary benchmark evidence, but MAC is a proxy for recursive self-improvement, not proof about unrestricted RSI.

**Mechanism hypothesis:** self-improvement evidence should require held-out verification, branch/run variance control, anti-reward-hacking checks, and resource-aware comparisons; best-run selection is insufficient.

### C3 — Two-timescale improvement of skills and the improver itself is plausible but not yet fully isolated
**Source:** MetaSkill-Evolve.

- Primary abstract: held-out gains over raw frozen backbone **+23.54 OfficeQA, +16.09 SealQA, +1.92 ALFWorld**.
- Framework separates fast task-skill evolution from slower meta-skill evolution of Analyzer/Retriever/Allocator/Proposer/Evolver.
- A secondary public dissection reports paper Table-1 values consistent with marginal slow-loop gains of roughly **+6.38 / +8.05 / +1.92** over a single-level loop; these values remain **secondary-source pending primary-table verification**.

**Evidence strength:** medium pending primary marginal-ablation and matched-cost verification.

### C4 — Persistent improvement can live in a curated external knowledge substrate rather than agent identity
**Source:** KSI.

- Agents are stated to remain generic/stateless/disposable; the shared curated knowledge base is the persistent object.
- Attempts become evidence-grounded claims, cross-task discussion, and distilled bundles; disagreement is retained/adjudicated.
- Author project page reports Haiku 4.5 **ARC-AGI-1 86.7 ± 4.2** and **Polyglot 68.0 ± 2.0**, versus cost-matched OpenEvolve 54/46 and GEPA 44/36.
- Same procedure is reported to transfer across another LLM family (GPT-5.4-mini), including ARC, Polyglot, and SWE-bench Pro gains.

**Evidence strength:** medium-to-strong for the isolated persistent-object design; exact project-page cells still need primary-table cross-check.

### C5 — Raw execution traces materially outperform compressed summaries for harness self-improvement
**Source:** Meta-Harness primary HTML.

Meta-Harness searches executable harness code with a coding-agent proposer that can selectively inspect a filesystem containing all prior candidates' code, scores, and execution traces.

**Matched interface ablation (online text classification):**
- Scores only: median **34.6**, best **41.3**, 26 runs > zero-shot.
- Scores + LLM summary, no raw traces: median **34.9**, best **38.7**, 23 > zero-shot.
- Full interface with raw traces: median **50.0**, best **56.7**, 39 > zero-shot.
- The full method's **median exceeds the best** candidate under either compressed-feedback ablation.

**Held-out / transfer evidence:**
- Test accuracy on the 3 searched classification datasets: **48.6%**, versus ACE **40.9%** and MCE **40.0%**; context 11.4K vs ACE 50.8K and MCE 28.5K.
- On 9 entirely unseen OOD classification datasets: **73.1% average**, vs ACE **70.2%**, best on 6/9 datasets.
- A single math-retrieval harness searched with GPT-OSS-20B improves 200 previously unseen IMO-level problems across **all five evaluated models**, average **34.1 → 38.8 (+4.7)** over no retrieval; it also beats BM25 by 1.3 points on average.
- TerminalBench-2: Meta-Harness reaches **76.4%** with Opus-4.6 vs Terminus-KIRA **74.7%**, and **37.6%** with Haiku-4.5 vs next reported Goose **35.5%**. Caveat: search and final evaluation use the same 89-task TerminalBench-2 benchmark; authors audit hard-coded leakage but this is weaker generalization evidence than the classification/math experiments.

**Evidence strength:** strong primary ablation for trace access; strong held-out transfer in classification/math; TerminalBench result is benchmark-specialized and should be scoped accordingly.

**Mechanism hypothesis:** self-improvement systems should persist *queryable raw diagnostic experience* and let the improver retrieve it selectively. Summarization-only memory can destroy credit-assignment signal.

### C6 — Bounded single-component updates + a hidden development no-regression gate enable interpretable recursive harness evolution
**Source:** AutoDesign primary HTML, submitted 2026-08-13.

- Outer loop analyzes rollout trajectories/scores, proposes a harness update, and runs a separate acceptance gate.
- Each outer-loop iteration may modify **exactly one of five components**: Context & Memory; Tools & Specifications; Execution Runtime; Orchestration; Evaluation & Feedback. Authors state this restriction is for interpretable credit assignment.
- Candidate acceptance rule is explicit: accept only if **training improves AND independent development performance does not decline**. Development trajectories/scores are not exposed to the proposer.
- Optimization record stores checkpoints, trajectories, scores, selected component, update plan/code changes, and accept/reject decision; rejected attempts remain evidence for later iterations.
- 7 days of traces: 224 subagents, at least 123 recursive iterations, **54 accepted harness updates**.

**Matched harness attachment ablation on PosterBench-mini:** all 7 completed model–coding-agent configurations improve, by **+5.01 to +19.56 points**. Examples:
- GPT-5.5/Codex: 75.87 → **81.46 (+5.59)**
- Claude 4.8/Claude Code: 69.55 → **74.56 (+5.01)**
- Kimi K2.7/Claude Code: 57.20 → **70.12 (+12.92)**
- DeepSeek V4 Pro/Claude Code: 34.73 → **54.29 (+19.56)**
- Average across seven configurations: **54.99 → 67.39 (+12.40 points)**.

Main-track score is **78.32**, +7.45 over Claude Design under the paper's stated comparison; system-blind human evaluation gives AutoDesign the highest Bradley–Terry estimate, **64.0%** (95% interval 55.2–77.8) across 933 valid ranking judgments.

**Evidence strength:** strong matched harness-attachment evidence within a paper-to-poster domain. Do not generalize the quantitative effect size to arbitrary agent tasks.

**Mechanism hypothesis:** recursive improvement becomes easier to audit when proposals are bounded to one coherent component, dev evidence is hidden from the proposer, and only no-regression candidates are persisted.

### C7 — Strict held-out selection bounds downside better than unguarded natural-language context evolution
**Source:** RSEA primary HTML, reached independently from AutoDesign citation chain.

- Shared-backbone comparison across ALFWorld, GAIA, tau-bench, WebShop with ReAct, Reflexion, GEPA, AWM, ACE, Dynamic Cheatsheet.
- ALFWorld (134 tasks × 5 seeds, Qwen2.5-7B): RSEA single-pass **69.3 ± 9.3%** vs ReAct **64.6 ± 4.3%**, McNemar p=0.015; with retry RSEA reaches **79.4 ± 7.4%**.
- On strong-backbone tool-use tasks, RSEA often correctly falls back toward ReAct rather than universally improving. WebShop every evolved candidate hurt held-out validation, so the frozen state is empty; RSEA **0.437** vs ReAct **0.429**.
- Unguarded Dynamic Cheatsheet is near-best on ALFWorld (**70.7%**) but collapses on WebShop **0.136** vs ReAct **0.429**, and is worst on tau-bench (**36.7%** vs ReAct 41.7%).

**Selection ablation:**
- No held-out gate: **100.0% in-sample**, **66.7% test** → 33.3-point train–test gap.
- Strict-gate RSEA: **67.3% test**; ReAct empty-state control **63.6%** in that ablation setup.
- Layer ablation: ReAct 64.2; strategy 67.3; skills 69.8; playbook 69.8; full RSEA 68.5. The paper therefore does **not** support a claim that all three layers are complementary/necessary; they overlap strongly.
- Strict best-update matters: non-strict ties on a small validation set can still freeze a harmful candidate. Authors explicitly limit the safety claim: the gate guarantees held-out-val behavior, not every test draw when validation is small.

**Evidence strength:** strong primary controlled evidence that selection rule is a major reliability factor in weight-frozen NL-state evolution; scope limited by modest transfer eval sizes and one split/seed in some transfer benchmarks.

**Mechanism hypothesis:** treat self-improvement as *proposal + independent acceptance*, with strict best-update and a safe empty/base fallback. The artifact form is secondary to the gate when the objective is monotone downside control.

## Cross-candidate synthesis (hypothesis, not system-specific)

The clean evidence now supports a sharper decomposition than “self-reflection improves agents”:

`raw experience → causal/diagnostic access → bounded proposal → independent held-out acceptance → versioned persistent artifact → routing/uptake on new tasks`.

Three mechanisms have especially direct ablation support:

1. **Do not compress away diagnostic traces**: Meta-Harness raw traces beat both scores-only and scores+summary by a large margin.
2. **Separate proposer from acceptance evidence**: RSEA and AutoDesign use held-out/development gates; unguarded evolution shows severe negative transfer/overfit.
3. **Bound edits for credit assignment**: AutoDesign changes one component per outer iteration; Meta-Harness qualitative traces show the proposer itself had to disentangle confounded simultaneous edits after regressions.

A further distinction matters: **selection safety and transferability are different claims**. A held-out gate can bound regressions on its validation distribution, but EvoAgentBench and RSEA show that routing/grounding bottlenecks can still erase gains on new task families. Generalization therefore needs explicit cross-task/model tests, not only monotone validation.

## Rejected / deprioritized leads

- **Self-Improving AI Coding Agents Through Accumulated Behavioral Rules** (arXiv:2607.13091): small uncontrolled 11-session case study; useful field evidence, not mechanism proof.
- **Self-Improvements in Modern Agentic Systems: A Survey**: taxonomy/source map only.
- Generic older self-reflection papers remain lower priority than matched modern benchmark/ablation evidence.
- Meta-Harness TerminalBench-2 result is retained but **not** treated as clean held-out generalization evidence because search and final evaluation share the public benchmark.

## Unresolved frontier (nonempty)

1. **Primary-verify MetaSkill-Evolve** table/component ablations, fast-loop vs slow-loop marginal value, and compute/cost matching.
2. **Primary-verify KSI** quantitative tables and isolate forum, cross-task discussion, distillation, routing/adapter, and generation-count effects.
3. Inspect **PostTrainBench (arXiv:2603.08640)** for autonomous post-training success rates, variance, resource constraints, and failures.
4. Search **August 2026** self-improvement/meta-learning papers newer than AutoDesign, prioritizing matched controls and held-out gates.
5. Search for **independent replications/failures** of Meta-Harness, RSEA, EvoAgentBench methods, MetaSkill-Evolve, and KSI.
6. Compare persistent objects under matched budgets: executable harness code vs procedural NL abilities vs evidence-grounded curated knowledge.
7. Search explicit **negative-transfer prediction before applying memory/skills**: abstention, retrieval confidence, counterfactual validation, per-candidate canary tests.
8. Test whether held-out-gate benefits persist under **nonstationarity / small validation sets / adaptive reuse of the same dev set**; look for dev-set overfitting and reusable holdout methods.
9. Follow Meta-Harness's adjacent references on **MCE / memory-system meta-evolution** only if they provide component-level or transfer ablations not already covered.
10. Inspect AutoDesign's evolution trace for acceptance rate and whether rejected updates cluster by component; quantify whether one-component restriction actually improves credit assignment versus a multi-component control (paper currently motivates it but does not supply that direct ablation).

## Exact continuation

Next concrete action: inspect **PostTrainBench (arXiv:2603.08640)** primary evidence and extract matched baseline, success-rate/variance, compute constraints, and failure taxonomy. Then search for small-validation/dev-set overfitting in held-out self-improvement gates and return to MetaSkill-Evolve primary ablations.

## Termination diagnostics

This checkpoint is not completion. This run already continued beyond the prior checkpoint through three unresolved branches (AutoDesign, its RSEA citation, and Meta-Harness primary ablation/transfer tables). The frontier remains nonempty and is the only continuation state for the next run.