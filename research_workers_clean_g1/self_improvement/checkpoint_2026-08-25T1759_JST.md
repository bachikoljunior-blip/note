# Self Improvement Scan — clean_g1 checkpoint

Generation: clean_g1 independent external research
Timestamp: 2026-08-25 17:59 JST
Search bias: self-improvement/meta-learning; benchmark-first, ablation-first; trace mechanisms backward from quantitative gains.
Boundary: this checkpoint was built from public external sources in this run only. No legacy self_improvement state, comparator/integrator output, or O/O-derived state was read.

## Checked primary sources and evidence

### EvoAgentBench — arXiv:2607.05202 (2026-07-06)
Primary: https://arxiv.org/html/2607.05202
- 528 train / 267 test tasks; two agent scaffolds, three backbones.
- Qwen3.5-27B average: Vanilla 37.5; Memento 35.1 (-2.4); ReasoningBank 41.1 (+3.6); GEPA 38.7 (+1.2); curated Ability-grounded Anchor 45.0 (+7.5).
- Qwen3.5-397B: Vanilla 49.2; Memento +1.5; ReasoningBank +2.4; GEPA +3.5; Anchor +10.5.
- Gemma-4-31B: Vanilla 36.7; Memento -0.7; ReasoningBank +0.4; GEPA +5.7; Anchor +5.8.
- Every automatic method has at least one negative setting; curated Anchor is positive across all reported settings.
- Severe negative-transfer examples include Memento on Nanobot/Qwen3.5-27B/SWE (-36.3 pp) and GEPA on OpenClaw/Qwen3.5-27B/knowledge-work (-12.3 pp).
Interpretation/scope: useful procedural information exists in the training side, but automatic extraction/indexing/routing/uptake is not robust. Curator-side cluster labels make Anchor an oracle-like diagnostic rather than a deployable mechanism.

### Rethinking the Evaluation of Harness Evolution for Agents — arXiv:2607.12227 (2026-07-14)
Primary: https://arxiv.org/html/2607.12227
- Without unit tests: initial harness 68.2 avg; parallel sampling 72.3; sequential refine 69.3; harness evolution 67.4; harness scaling 71.8.
- With unit tests: direct 72.9 pass@1; parallel sampling 86.0; sequential refine 84.3; harness evolution 75.8; harness scaling 82.6. pass@5: sequential 91.8 vs harness evolution 86.2 vs harness scaling 89.3.
- Disjoint 45 train / 10 val / 34 held-out: initial 67.7 vs evolved 68.3 (+0.6 avg); Claude +1.2; GPT-5.4 +0.0.
Interpretation/scope: same-benchmark harness gains can be repeated-search or optimization-set overfit. Persistent self-improvement claims need compute-matched direct-search baselines plus disjoint held-out generalization.

### Agentic Harness Engineering (AHE) — arXiv:2604.25850 (2026-04-28, revised 2026-05-18)
Primary: https://arxiv.org/html/2604.25850
- Terminal-Bench 2 main: 69.7 -> 77.0 pass@1 over 10 iterations with fixed backbone.
- Frozen transfer to SWE-bench Verified: 75.2 -> 75.6 pass@1 (+0.4 pp aggregate) while tokens fall from ~526k to ~461k (~12% reduction); per-repository results are mixed.
- Cross-model transfer on Terminal-Bench 2: DeepSeek-v4-flash +10.1 pp; Qwen-3.6-plus +6.3; Gemini-3.1-flash-lite-preview +5.1; GPT-5.4 medium/xhigh +2.3.
- Component ablation: seed 69.7; memory-only 75.3 (+5.6); tool-only 73.0 (+3.3); middleware-only 71.9 (+2.2); system-prompt-only 67.4 (-2.3); full 77.0 (+7.3). Positive isolated gains sum to +11.1, exceeding full gain, indicating non-additive interference/redundancy. On hard tasks memory-only 63.3 > full 53.3.
- Self-attribution: predicted fixes precision/recall 33.7%/51.4%; predicted regressions 11.8%/11.1%, showing regression blindness.
Interpretation/scope: change attribution should include falsifiable predicted fixes and regressions, but regression prediction is too weak to replace empirical regression gates. Large same-benchmark gains should not be equated with broad task transfer.

### Harness Updating Is Not Harness Benefit — arXiv:2605.30621 (2026-05-28)
Primary: https://arxiv.org/html/2605.30621
- Harness-updating gain is nearly flat with evolver capability; best–worst evolver gap <=3.1 pp on any benchmark.
- Weakest Qwen3.5-9B evolver can outperform stronger evolvers on SkillsBench update (+3.8 pp vs Opus 4.6 +2.3 pp and Qwen3-235B +1.5 pp).
- A strong task-solving agent with the worst evolver still beats a weak task-solving agent with the best evolver by 35.2 pp SWE, 32.3 pp MCP, and 18.6 pp SkillsBench.
- Artifact activation/adherence is a major bottleneck: e.g. skill-load rate Qwen3-32B .251 vs Opus .957; harness-following rate Qwen3-32B .142 vs Opus .757. Qwen3-235B loads skills at .961 but pass-when-loaded is .022 vs Opus .177.
Interpretation/scope: investing more capability in the improver does not guarantee harness benefit. Measure extraction/update, artifact activation, adherence, and pass-conditional-on-activation separately.

### Hierarchical Self-Improvement (HSI) — arXiv:2608.08466 (2026-08-09)
Primary: https://arxiv.org/html/2608.08466
- DeepSeek-V4-Flash initial avg across BabyAI/Crafter/TextWorld/MiniHack/NLE: 18.9; HSI meta-off 33.1; meta-on 41.4.
- Meta evolution vs meta-off adds +4.0 BabyAI, +8.2 Crafter, +19.0 TextWorld, +10.0 MiniHack, but only +0.2 NLE.
- Held-out sub-suite examples: BreakStop init .0333 -> test .98 meta-on / 1.0 meta-off; GoTo .1818 -> 1.0 / .9636; Make 0 -> .3625 / .3375.
Interpretation/scope: meta-evolution helps where ordinary evolution has informative reward and reachable capability/headroom; it does not rescue a near-zero-signal boundary such as NLE in these experiments.

### GDPevo — arXiv:2608.03764 (2026-08-04)
Primary: https://arxiv.org/html/2608.03764
- 24 task groups / 240 tasks in current generated suite; each group has 5 training + 5 held-out test tasks. Isolated containers prevent cross-attempt/evaluator leakage.
- Across four agents and supervision modes, every evolved combination improves within-group held-out accuracy by +2.59 to +16.44 pp; best fewshot is Opus-4.8/Claude Code 50.63 -> 67.07 (+16.44 pp).
- Fully informed oracle ceiling is 91.6%, leaving large extraction/application headroom.
- Cross-domain transfer: fewshot has 5/6 negative off-diagonal cells, worst -5.0 pp; reflect has 3/6 positive off-diagonals, best +6.5 pp and worst -1.0 pp. On-policy score feedback appears more transferable but less specialized than gold-answer fewshot.
- Controlled creator comparison, fixed agent + fewshot: GPT-5.5/Codex base 49.66; CC creator 62.15; Codex 62.19; DeepAgents 62.69; OpenCode 60.79; naive one-sentence creator 65.12. DeepSeek-V4-Pro/Codex base 42.48; creators 46.74–48.01, with naive best 48.01. Elaborate creator logic did not outperform the minimal creator.
Interpretation/scope: the quality/complexity of the distillation prompt is not necessarily the limiting factor; supervision type and underlying solver capability dominate here. Gold-label skill extraction specializes strongly and can transfer negatively; on-policy feedback yields more conservative cross-domain transfer.

### Benchmark-as-Teacher (BaT) — arXiv:2608.16211 (2026-08-17)
Primary: https://arxiv.org/html/2608.16211
- BiCuRL uses a fixed held-out evaluation only for aggregate stage diagnostics/checkpoint retention; raw held-out IDs, answers, paths, traces and reports do not enter training.
- Qwen3.5-9B baseline Overall 19.9; GRPO 31.9; BiCuRL 53.4. Qwen3.5-4B baseline 6.1; BiCuRL 22.9.
- Full three-pool curriculum (weak-stage S-target + remaining-stage S-mix + E2E surrogate) reaches 53.4; strongest partial mix E2E alone 31.9, a 21.5-point gap. Every leave-one-pool-out run trails full by at least 26 points.
- Raw per-round scores fluctuate; checkpoint retention/fallback preserves accepted gains through 10 rounds.
- BaT-9B Agent reaches 79.6 Overall on AutoMedBench-Lite vs Claude Opus 4.6 + Claude Code 77.5, but trails leaders on ABRA (70.6 vs 79.9) and MedXpertQA-Text (50.2 vs 65.0).
Interpretation/scope: improvement benefits from a curriculum that jointly targets the diagnosed weakness, rehearses non-target stages to control forgetting, and retains end-to-end coordination. The large full-vs-partial pool gap is matched on training controls, but it does not individually isolate the outer stage router, checkpoint gate, or GRPO algorithm.

## Cross-source mechanism hypotheses (not yet treated as causal facts)
1. Self-improvement should be instrumented as a chain: experience/signal quality -> extraction/distillation -> indexing/routing -> activation/adherence -> task outcome. Aggregate score alone hides failure location.
2. Persistent-change claims require compute-matched direct-search baselines and disjoint held-out evaluation; same-benchmark iterative gains are insufficient.
3. Regression control is a first-class mechanism: model-predicted regressions are weak, so empirical held-out/regression gating and rollback are needed.
4. More elaborate improver logic is not automatically valuable: GDPevo's naive creator beats more complex creators, and evolver strength can matter far less than solver activation/adherence.
5. Supervision type controls specialization vs transfer: gold-answer/fewshot signals can maximize in-domain gains while overfitting across domains; on-policy reward feedback may transfer more conservatively.
6. Curriculum needs both targeted repair and anti-forgetting/global-coordination rehearsal; BaT's full S-target + S-mix + E2E mixture strongly beats every partial mixture.
7. Meta-improvement budget should be conditioned on feedback fidelity and reachable capability; HSI's NLE near-zero result is a warning against spending meta-search in no-signal regimes.

## Rejected / de-prioritized interpretations
- Do NOT equate AHE's 69.7->77.0 same-benchmark gain with broad transferable capability; its frozen SWE-bench pass@1 gain is only +0.4 pp though token efficiency improves.
- Do NOT infer that a stronger/more expensive evolver necessarily produces more useful persistent improvements.
- Do NOT infer from BaT's whole-system result that any single component (stage routing, checkpoint fallback, GRPO, or one pool) independently causes the full gain.
- Do NOT infer that fewshot/gold-answer skill extraction is generally superior; GDPevo shows substantial off-domain negative transfer.
- Do NOT treat curator-derived Ability labels in EvoAgentBench Anchor as a deployable automatic solution.

## Nonempty unresolved frontier
1. Locate and inspect the primary GSME / gated semantic quality-diversity source referenced by recent HSI work; extract activation/significance gate definitions and matched ablations if available.
2. Deep-dive BaT external-transfer table and ablations to separate anti-forgetting effects of S-mix from cross-stage coordination effects of E2E and stage-targeting effects of S-target.
3. Search for independent replications or follow-up evaluations of GDPevo / EvoAgentBench-style procedural transfer, especially tests of routing/activation vs extraction.
4. Find quantitative experiments on adaptive overfitting from repeatedly reusing a held-out gate across many self-improvement rounds, and reusable-holdout / sequential-testing countermeasures.
5. Find self-improvement benchmarks with explicit intervention-level credit assignment: one-component-at-a-time vs coupled changes, predicted-regression calibration, and rollback ablations.
6. Investigate BaT/GDPevo evidence for whether on-policy score feedback yields broader transfer than gold-answer distillation outside the reported domains.

## Exact continuation
Next action: search public primary sources for the GSME (Gated Semantic Quality-Diversity) method cited by HSI, verify its bibliographic identity independently, then extract the exact validity/activation/significance gate equations, statistical thresholding protocol, and ablations that isolate each gate. If the source cannot be located or does not contain matched ablations, immediately branch to quantitative literature on adaptive held-out reuse / sequential acceptance testing in self-improving agents and persist that evidence as the next checkpoint.
