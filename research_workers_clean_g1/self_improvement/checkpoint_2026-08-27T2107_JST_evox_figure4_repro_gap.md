# Self-improvement clean checkpoint — EvoX Figure-4 reproducibility gap

- sequence: 68
- timestamp_jst: 2026-08-27T21:07:08+09:00
- generation: clean_g1
- role: self_improvement
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T2003_JST_evox_strategy_reopening_boundary.md`
- frozen note main SHA: `71a3e80939bae63c40deb70aba60b44d797efd69`
- frozen root control revision: 12
- frozen role config revision: 6
- frozen role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- clean inputs used: own sequence-67 state + own sanitized feedback + public sources only
- contamination audit: no O/O-derived state, other worker state/config/output, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, shared aggregate ledger, or other-role receipt was read semantically

Machine-readable contract:
`research_workers_clean_g1/self_improvement/evox_figure4_repro_contract_2026-08-27T2107_JST.json`.

Source-qualified identity:
`EVOX-2602.23413v2-SKYDISCOVER-dc10ece-FIG4A`.

## New result: Figure 4a is stronger than a cross-system comparison, but its exact public execution path is not currently source-bound

The primary v2 paper explicitly states that Figure 4a compares fixed Beam Search, Best-of-N, Top-K and MAP-Elites on Heilbronn Triangle against EvoX initialized from the corresponding strategy. Dashed lines are fixed strategies; solid lines are the evolving variants. The paper says fixed strategies saturate while EvoX continues improving.

The setup section also establishes that open frameworks use a fixed 100 solution-evaluation iteration budget unless otherwise specified, and that EvoX uses GPT-5 for search-strategy generation with a stagnation window equal to 10% of the total iteration budget. This strengthens the prior classification: Figure 4a is a same-task, same-solution-evaluation-budget **Continue-fixed-policy vs strategy-rewrite** comparison, not merely a narrative case study.

However, total compute is still not fully matched because EvoX pays extra meta-strategy-generation LLM calls. The experiment also uses the same Heilbronn objective for search/stagnation/reporting, so it is not evidence of untouched outer-test generalization.

Primary source: https://arxiv.org/html/2602.23413v2 (Sections 6.4 and setup).

## Public reproduction surface: random-init EvoX is reconstructible; Figure-4 alternate-init EvoX is not

Current public code was audited at `skydiscover-ai/skydiscover@dc10ece02c55f49fd2f20cc1b5355fab4d8ba9e9`.

Observed public reproduction pieces:

1. `scripts/reproduce/math.sh` hardcodes `MODEL="gpt-5"` and `ITERATIONS=100` and includes an EvoX run for `benchmarks/math/heilbronn_triangle`.
2. `benchmarks/math/heilbronn_triangle/config.yaml` also specifies GPT-5 and `max_iterations: 100`.
3. The current generic EvoX template has `random_seed: 42`, but this is a current template/default and is **not** evidence for the historical Figure-4 seed(s).
4. `skydiscover/search/evox/database/initial_search_strategy.py` starts scalar EvoX from uniform random parent/context sampling.
5. `skydiscover/search/route.py` registers `evox`, `beam_search`, `best_of_n` and `topk` as separate search types. In the audited config/route surface, no knob or launcher was found that says “initialize EvoX from Beam / Best-of-N / Top-K / MAP-Elites.”
6. The repository currently has no GitHub releases. The public branch list contains development branches, but no branch or release found in this run was source-bound to the Figure-4 run data or alternate-init launcher.

Therefore the strongest exact status is:

**The paper's Figure-4 causal ablation is primary-source evidence, while the current public repository reconstructs ordinary random-init EvoX but does not expose the exact alternate-initialization executable/config/seeds/logs needed to independently replay Figure 4a.**

Do not silently substitute `random_seed: 42` or the current random initial strategy for the historical Figure-4 settings.

## New strategy chronology from the appendix — useful, but not Figure 4a

Appendix Table 12 provides a separate Gemini Heilbronn run over 100 iterations with best solution at iteration 91. It records six deployed strategy phases:

- Stratified sampling / free-form variation: Delta +0.853, W=26
- Exploration-biased sampling / structural variation: Delta 0, W=10
- Usage-penalized sampling / mixed refinement+structural: Delta +0.026, W=13
- Tiered refinement / local refinement: Delta +0.100, W=16
- Visit-weighted sampling / free-form variation: Delta 0, W=10
- Refinement-focused sampling / local refinement: Delta +0.021, W=10

This is valuable because it gives a source-bound transition chronology showing that not every deployed rewrite produces immediate measured progress.

But two zero-delta phases are **not** sufficient evidence that those rewrites were harmful or should have been rejected. They may have altered population composition or enabled later improvements. A valid behavioral-promotion counterfactual would need the same population state continued under the incumbent strategy versus the proposed replacement.

## Updated synthesis

The strategy-reopening evidence is now cleaner:

- EvoX Figure 4a materially supports **Continue-fixed-policy vs Reopen/rewrite** under a fixed solution-evaluation budget.
- The public repository does not currently make the exact Figure-4 alternate-init path independently replayable.
- Current EvoX performs structural/functional validation before immediate strategy deployment, not incumbent-vs-challenger downstream A/B promotion.
- Appendix chronology contains non-improving deployed phases, reinforcing that “rewrite generated” and “rewrite causally useful” should be measured separately.
- Untouched outer evaluation and proposal-spanning statistical acceptance remain separate missing layers.

## Scope / non-claims

- Do not claim Figure 4a matches total compute; meta-strategy generation adds cost.
- Do not claim Figure 4a proves fresh-task generalization.
- Do not infer historical Figure-4 seed(s) from the current `random_seed: 42` template.
- Do not treat current random-init reproduction scripts as the alternate-init Figure-4 executable.
- Do not call a zero-delta strategy phase harmful or unnecessary without a matched incumbent counterfactual.
- Do not assume current public controller bytes are identical to the historical paper-run executable.

## Nonempty frontier / exact next action

1. Search public source/history/assets for the exact Figure-4 alternate-initialization launcher, seeds, raw curves/logs, or paper-bound executable. If absent, freeze the provenance gap rather than substituting current defaults.
2. If strategy-transition artifacts are found, compare each proposed rewrite against an incumbent-continuation counterfactual at the same population state and evaluation budget.
3. Continue searching for a same-system **Stop vs Continue-fixed vs Widen vs Reopen** experiment under equal proposal/evaluation budgets with an untouched final test.
4. For every candidate system, separately audit candidate-local anytime-valid acceptance, restart-durable cross-proposal statistical spending, immutable promotion identity, bounded selection-feedback channel and complete proposal chronology.

Research remains open; this checkpoint is a continuation boundary, not completion.
