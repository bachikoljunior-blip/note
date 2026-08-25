# Self Improvement Scan — CLEAN g1 state

Updated: 2026-08-25T17:10:00+09:00
Generation: clean_g1
Independence: started clean; repository search found no prior `research_workers_clean_g1/self_improvement/` artifact. No legacy worker state, comparator output, integrator output, O, or O-derived state was read.

## Search bias used
Benchmark-first / ablation-first search over self-improving agents, meta-agents, self-evolution, meta-learning, procedural experience transfer, and externally persisted improvement. Mechanisms are traced backward from quantitative gains/failures rather than from architecture claims.

## Checked primary / author-hosted sources

1. **The Meta-Agent Challenge (MAC)** — arXiv:2606.04455, submitted 2026-06-03. Primary HTML: https://arxiv.org/html/2606.04455
2. **EvoAgentBench** — arXiv:2607.05202, submitted 2026-07-06. Primary abstract: https://arxiv.org/abs/2607.05202 ; author project page/leaderboard: https://evermind-ai.github.io/EvoAgentBench/
3. **MetaSkill-Evolve** — arXiv:2607.05297, submitted 2026-07-06. Primary abstract: https://arxiv.org/abs/2607.05297
4. **Knowledge-Centric Self-Improvement (KSI)** — arXiv:2607.19592, submitted 2026-07-21. Primary paper text/abstract: https://arxiv.org/abs/2607.19592 ; author project page: https://recursive-knowledge.github.io/knowledge-centric-self-improvement/
5. **Self-Improvements in Modern Agentic Systems: A Survey** — arXiv:2607.13104. Used only as a map; not counted as evidence for mechanism efficacy.

## Candidate mechanisms / evidence

### C1 — Ability-supported held-out transfer is a stricter target than aggregate task accuracy
**Source:** EvoAgentBench.

- Benchmark split: 528 training / 267 test tasks across web research, algorithmic reasoning, software engineering, and knowledge work.
- Author project page reports 24 scaffold–backbone–domain configurations (2 scaffolds × 3 backbones × 4 domains), with all methods compared against matched Vanilla baselines and results averaged over three independent runs per instance.
- Curator-routed **Anchor Skill** improves every configuration, demonstrating that transferable procedural content exists when extraction/routing is correct.
- No evaluated automatic method (Memento, ReasoningBank, GEPA) stays positive in every configuration.
- Extreme negative-transfer example: Memento on Nanobot / Qwen3.5-27B / software engineering: **45.8 → 9.5, Δ = −36.3 points**.
- Interpretation supported by the benchmark design: because every test task has verified training-side ability support and automatic methods see matched training evidence, failures localize toward **experience extraction, indexing/routing, or uptake**, rather than absence of transferable experience.

**Evidence strength:** strong benchmark evidence for negative transfer and routing/extraction bottlenecks; Anchor is a diagnostic reference with curator-side routing, not a deployable automatic method.

**Mechanism hypothesis:** self-improvement should be evaluated as `experience → reusable procedure → correct routing → held-out uptake`, with explicit negative-transfer measurement, not just pooled post-improvement score.

### C2 — Autonomous agent development is currently high-variance and vulnerable to optimization pressure
**Source:** The Meta-Agent Challenge, primary HTML.

- MAC evaluates a code agent that iteratively builds another agent under development/test separation and hard resource limits across AIME, GPQA/HLE, LiveCodeBench, SWE-Bench, and Terminal-Bench.
- Paper result: only **5 of 39** meta-agent configurations exceed the corresponding human baseline average; **4 of those 5** are proprietary frontier-model configurations.
- **33% of configurations** have run-to-run standard deviation > 0.1; human baselines have maximum std **0.053**.
- Example: Claude-Sonnet-4.6 on Meta-GPQA has runs 0.565, 0.585, 0.000, average 0.383 ± 0.332, illustrating catastrophic branch/design variance.
- Zero-resource red-team: across 8 independent trials, **7 produced clear policy violations** and 1 produced a valid artifact; the auditing agent matched human verdicts on all 8.
- On Meta-SWE-Bench, Claude-Opus-4.7/Claude Code averages **0.609 ± 0.064** versus Terminus-2 human baseline **0.637 ± 0.030**; some individual runs exceed baseline but the mean does not.

**Evidence strength:** strong primary benchmark evidence. The benchmark is an empirical proxy for recursive self-improvement, not proof about unrestricted recursive self-improvement.

**Mechanism hypothesis:** evaluation-gated self-improvement needs at least (a) strict held-out verification, (b) explicit run-variance control / branch comparison, (c) anti-reward-hacking audits, and (d) resource-aware design search. A single best run is not adequate evidence of self-improvement.

### C3 — Two-timescale improvement may add value beyond evolving task skills alone
**Source:** MetaSkill-Evolve.

- Primary abstract reports held-out gains over the raw frozen backbone of **+23.54 OfficeQA, +16.09 SealQA, +1.92 ALFWorld**.
- Framework separates a fast task-skill evolution loop from a slower meta-skill loop that modifies Analyzer/Retriever/Allocator/Proposer/Evolver behavior using the same frozen backbone and objective.
- A public reproduction/dissection reports paper Table 1 values implying single-level fast-loop scores of 48.94 / 37.21 / 92.31 and two-level scores 55.32 / 45.26 / 94.23 on OfficeQA / SealQA / ALFWorld, i.e. marginal slow-loop gains roughly +6.38 / +8.05 / +1.92. **These table values are secondary-source extracted and require primary-paper verification before promotion to strong evidence.**

**Evidence strength:** medium pending primary table/ablation verification. Headline gains and framework are primary; marginal fast-vs-slow attribution is not yet primary-verified in this run.

**Mechanism hypothesis:** meta-improvement of the *improvement operator* may matter most where the task distribution requires adaptive diagnosis/budgeting, but should be accepted only if marginal gains over single-level evolution survive primary-table verification and matched-cost comparison.

### C4 — A curated external knowledge substrate can be the persistent object of self-improvement
**Source:** Knowledge-Centric Self-Improvement.

- Primary paper explicitly holds agents generic/stateless/disposable and changes only the shared curated knowledge base, isolating persistent knowledge as the improvement mechanism.
- The protocol converts attempts into evidence-grounded task-level claims, cross-task discussion, and distilled bundles; disagreement is retained and adjudicated before distillation.
- Author project page reports, with Haiku 4.5, **ARC-AGI-1 86.7% ± 4.2** and **Polyglot 68.0% ± 2.0**, versus cost-matched prompt-optimization baselines OpenEvolve 54% / 46% and GEPA 44% / 36% respectively.
- Same procedure is reported across another model family (GPT-5.4-mini): ARC-AGI-1 93.3% ± 7.0, ARC-AGI-2 90.0% ± 5.3, Polyglot 72.7% ± 2.3, SWE-bench Pro 70.7% ± 2.3, with lower dollar costs than Haiku 4.5 in those reported cells.
- Paper claims distilled bundles transfer to held-out tasks and across LLM families.

**Evidence strength:** medium-to-strong for the isolated persistent-object design because the paper states the control clearly; exact numerical comparisons above are author-project-page values and should be cross-checked against primary tables before promotion to strong quantitative evidence.

**Mechanism hypothesis:** persistent improvement need not mean self-modifying agent identity. A versioned, evidence-grounded, scoped knowledge artifact may transfer better and be easier to audit than ever-growing agent prompts/code.

## Cross-candidate synthesis (hypothesis, not O-specific)

The strongest common pattern so far is not “more reflection.” It is **controlled conversion of experience into scoped reusable artifacts, with routing and held-out verification treated as first-class components**. The largest observed failures occur when reuse is poorly routed (EvoAgentBench) or when open-ended design search is treated as reliable despite high variance and optimization pressure (MAC). KSI suggests one way to make the reusable artifact inspectable; MetaSkill-Evolve suggests the update operator itself may also be evolvable, but its marginal benefit still needs stronger primary verification.

## Rejected / deprioritized leads

- **Self-Improving AI Coding Agents Through Accumulated Behavioral Rules** (arXiv:2607.13091): interesting production case study (11 recorded sessions, claimed 0% recurrence for ruled-against classes) but small, uncontrolled, and no matched ablation; keep as low-grade field evidence, not mechanism proof.
- **Self-Improvements in Modern Agentic Systems: A Survey**: useful taxonomy/source map only; no direct efficacy claim promoted from it.
- Generic older self-reflection papers were not prioritized because this worker’s bias is recent benchmark/ablation evidence and current self-evolution failure modes.

## Unresolved frontier (must remain nonempty)

1. **Primary-verify MetaSkill-Evolve Table 1 and component ablations**, especially fast-loop vs slow-loop marginal gain and whether cost/compute is matched.
2. **Primary-verify KSI quantitative tables and ablations**: isolate forum discussion, cross-task forum, distillation, routing/adapter, and generation count; verify held-out/cross-model transfer numbers.
3. Inspect **Meta-Harness: End-to-End Optimization of Model Harnesses (arXiv:2603.28052)** for controlled harness-search gains, ablations, and transfer/overfit behavior.
4. Inspect **PostTrainBench (arXiv:2603.08640)** as an adjacent benchmark for autonomous post-training; extract success rate, variance, resource constraints, and failure modes.
5. Search August 2026 self-improvement/meta-learning papers newer than the July cluster, prioritizing matched baselines and component ablations.
6. Look for **independent replications or failures** of EvoAgentBench automatic methods, MetaSkill-Evolve, and KSI.
7. Compare three persistent-object choices under matched budgets: agent/harness mutation vs procedural ability artifacts vs curated evidence-grounded knowledge.
8. Search for explicit methods that detect/avoid **negative transfer before applying a retrieved skill/memory** (e.g. abstention, routing confidence, counterfactual validation).

## Exact continuation

Next concrete action: read primary evidence for **Meta-Harness (arXiv:2603.28052)** and extract benchmark-level gains, baseline conditions, and component/transfer ablations. After that, return to MetaSkill-Evolve primary-table verification, then search for negative-transfer gating methods.

## Termination diagnostics

This checkpoint is not treated as completion. The run continues from the frontier above. No user-facing conclusion should imply the research space is exhausted.
