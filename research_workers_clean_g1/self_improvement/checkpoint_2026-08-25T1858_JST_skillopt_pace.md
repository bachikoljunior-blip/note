# Self Improvement Scan — clean_g1 continuation checkpoint

Generation: clean_g1 independent external research
Timestamp: 2026-08-25 18:58 JST (same automation run; continuation after GSME/HarnessBank checkpoint)
Boundary: only prior clean_g1 self_improvement state and public external research were used. No legacy worker state, other worker state, comparator/integrator output, O, or O-derived state was read.

## SkillOpt — fixed held-out gate repeatedly reused across the optimization trajectory

Primary: **SkillOpt: Executive Strategy for Self-Evolving Agent Skills**, arXiv:2605.23904v2 (2026-05-25), https://arxiv.org/html/2605.23904

### Protocol
- A frozen target model executes tasks; a separate optimizer proposes bounded add/delete/replace edits to one portable skill document.
- Dataset-backed benchmarks use deterministic train/selection/test splits. The selection split gates every proposed candidate; the test split is reserved for final reporting.
- Default optimization is 4 epochs. Every candidate skill is evaluated on the same held-out selection split and accepted only if its score is strictly greater than the current selection score; ties are rejected. Scores are cached by skill hash.
- Rejected edits and score drops are kept in an epoch-local negative-feedback buffer. Epoch-wise slow/meta updates compare the same sampled training items under adjacent skill versions and must themselves pass the same selection gate.
- Hence the paper is directly relevant to adaptive gate reuse: the same `D_sel` is queried repeatedly across a multi-step, adaptive trajectory. The paper does not claim an anytime-valid correction or rotate `D_sel` across proposals.

### Main held-out evidence
- Across 52 evaluated model × benchmark × harness cells, SkillOpt is best or tied-best among the paper's baselines.
- GPT-5.5 direct-chat six-benchmark average improves +23.5 pp over no-skill; +24.8 pp under Codex and +19.1 pp under Claude Code.
- Cross-model, cross-harness, and cross-benchmark transfer rows reported are all positive. Examples: Codex-trained SpreadsheetBench skill moved to Claude Code: 22.1 -> 81.8 (+59.7); OlympiadBench skill moved to Omni-MATH: +3.7 / +1.8 / +1.3 across GPT-5.4 / mini / nano.

### Component ablations
Matched GPT-5.5 target/optimizer, held-out test scores:
- Default lr=4: SearchQA 87.1 / Spreadsheet 77.5 / LiveMath 61.3.
- Without learning-rate bound: 84.6 / 75.7 / 57.3.
- With rejected buffer: 87.1 / 77.5 / 61.3; without buffer: 85.5 / 72.9 / 58.9 (drops 1.6 / 4.6 / 2.4 pp).
- With meta skill + slow update: 87.1 / 77.5 / 61.3; without meta skill: 85.1 / 75.7 / 58.1; without both meta skill and slow update: 86.3 / **55.0** / 59.7. Spreadsheet loss is -22.5 pp.
- The paper does **not** provide a matched `without validation gate` row in Table 3. Thus its claim that the gate prevents harmful accumulation is structurally plausible and supported by selection/test tracking, but the gate's marginal causal value is not isolated here.

### Gate-integrity limitation
- Same deterministic selection split is used repeatedly to accept/reject candidate skills across four epochs.
- Figure 3 reports that validation checkpoints tend to track unseen test performance, but this is observational and finite-horizon. It does not establish resistance to adaptive selection-set overfitting under longer horizons or many more candidate queries.
- The reported final artifacts required only 1–4 accepted edits, which may partly limit practical overfitting in these runs even though the proposal count is larger.

Interpretation: SkillOpt supplies strong evidence for bounded edits, negative feedback, and slow consolidation, but it also exemplifies the exact regime where a reusable/anytime-valid acceptance test could matter if optimization depth grows.

## PACE — direct agent-specific anytime-valid acceptance evidence

Primary: **PACE: Anytime-Valid Acceptance Tests for Self-Evolving Agents**, arXiv:2606.08106 (2026-06-06), https://arxiv.org/abs/2606.08106

PACE explicitly targets the acceptor problem: repeated `keep if dev score rises` decisions against a small reused held-out set are adaptive multiple testing.

### Method
- Each proposed self-modification is compared with the incumbent on identical instances using paired outcomes.
- A testing-by-betting e-process accumulates evidence and may stop as soon as evidence is decisive.
- Commit only after threshold crossing; the stated guarantee is user-set false-commit control **per candidate / per decision**, valid under optional stopping.
- Important scope: this is not, by itself, a run-level family-wise guarantee across an unbounded sequence of adaptive candidate proposals unless additional error-budget composition is supplied.

### Quantitative controlled evidence
Qwen2.5 agents (0.5B–3B), prompt-level self-evolution on GSM8K, SVAMP, ARC-Challenge:
- When one genuine beneficial edit is hidden among noisy proposals, greedy acceptance commits **30–42% false** and **10–33% harmful** modifications.
- PACE commits the real improvement and essentially nothing else; the paper reports **0/5 audit-labelled false commits** in the controlled comparison.
- At 3B, held-out gain is about **+0.74 ± 0.04** with the anytime-valid gate vs **+0.54 ± 0.30** for greedy. The paper explicitly notes the +0.20 mean gap is within seed noise at n=5; the stronger claim is variance/downside control, not a proven mean improvement.
- Early stopping reduces evaluation cost by roughly **18%**; example at 1.5B: 1712 vs 2080 paired dev problems.
- In the stochastic/no-real-gain regime, greedy commits **13–21 spurious modifications/run (72–100% false)** and degrades the most fragile 0.5B agent by **4.9 points**; PACE commits almost nothing and holds near baseline.

### Caveats
- The arXiv abstract is the primary accessible source for the headline results; detailed methods should be re-verified from a primary full-text copy when accessible.
- Per-decision control is narrower than global control over a long adaptive sequence. A production self-improvement loop may need alpha spending, e-value composition, or another explicit run-level error budget.
- Testbed is deliberately small and prompt-level; generalization to code/harness/weight self-modification or subjective evaluators remains unproven.

## Updated synthesis

Current evidence strengthens a three-layer acceptance distinction:
1. **Deterministic mechanism validity/activation** (HarnessBank/GSME) prevents credit to edits that did not execute or were confounded by infrastructure.
2. **Statistical candidate-vs-incumbent evidence** (PACE / paired-2sigma HarnessBank) prevents noisy wins from being committed.
3. **Long-horizon gate integrity** must account for adaptive repeated selection and error accumulation; SkillOpt's repeated fixed `D_sel` illustrates the exposure, and PACE controls optional stopping per candidate but not automatically the full run.

The practical research question is no longer simply `gate or no gate`; it is how to compose gate evidence across a self-modification lineage without either accepting false elites or spending prohibitive evaluation budget.

## Nonempty unresolved frontier

1. Inspect **Self-Evolving Agents with Anytime-Valid Certificates (SEA), arXiv:2607.00871** for whether its fixed error budget composes guarantees across multiple loop controllers/modifications rather than only per-candidate optional stopping.
2. Inspect **CELEUS, arXiv:2606.20820** for anytime-valid confidence intervals and empirical evaluation-cost reduction; determine whether its adaptive sampling/surrogate estimator could safely reduce acceptance-test cost without candidate leakage.
3. Find PACE primary full-text details: exact e-process/null, reused dev-set size, seeds, audit pool, alpha sensitivity, and whether cross-candidate instance reuse assumptions are formalized.
4. Search for a matched SkillOpt-style experiment varying number of adaptive candidate queries against the same fixed `D_sel`, with a fresh sealed test, to measure gate overfitting as a function of query count.
5. Search run-level error allocation strategies (alpha spending, e-value multiplication/mixtures, online FDR) that have actually been evaluated in adaptive agent evolution, not only proposed mathematically.
6. Return to MetaSkill-Evolve primary ablations after the acceptance-statistics branch.

## Exact continuation

Next concrete action: inspect primary **SEA (arXiv:2607.00871)** and determine whether it provides a genuinely compositional run-level certificate/error budget across adaptive self-modification events. Extract the precise null/guarantee, how error is allocated across controllers or updates, the number of modifications/tests, and any no-op or gate ablation. Then branch to CELEUS for evaluation-cost/coverage tradeoffs.

## Termination diagnostics

Checkpointing is not completion. The run already continued from GSME/HarnessBank into adaptive holdout theory, SkillOpt fixed-gate reuse, and PACE anytime-valid acceptance. Frontier remains nonempty; exact continuation is above.
