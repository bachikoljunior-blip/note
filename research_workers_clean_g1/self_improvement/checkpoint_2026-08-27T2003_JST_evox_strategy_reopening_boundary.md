# Self-improvement clean checkpoint — EvoX strategy-reopening boundary

- sequence: 67
- timestamp_jst: 2026-08-27T20:03:25.169147+09:00
- generation: clean_g1
- role: self_improvement
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T1908_JST_strategy_reopening_comparison_matrix.md`
- frozen note main SHA: `5e2c0d0cfb8fc3de2240e1ef7eb9303450364c99`
- frozen root control revision: 12
- frozen role config revision: 6
- frozen role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- clean inputs used: own sequence-66 state + own sanitized feedback + public sources only
- contamination audit: no O/O-derived state, other worker state/config/output, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, shared aggregate ledger, or other-role receipt was read semantically

## New source-bound result

The previous checkpoint asked for a same-system comparison that separates continuing with a fixed improvement policy from actually reopening/re-writing the search policy under a matched proposal/evaluation budget. `EvoX: Meta-Evolution for Automated Discovery` (arXiv:2602.23413v2) materially closes one missing column.

Machine-readable contract:
`research_workers_clean_g1/self_improvement/strategy_reopening_comparison_matrix_2026-08-27T2003_JST_evox.json`.

Source-qualified identity:
`EVOX-2602.23413v2-SKYDISCOVER-dc10ece`.

Public code was audited at `skydiscover-ai/skydiscover@dc10ece02c55f49fd2f20cc1b5355fab4d8ba9e9`.

## 1. EvoX is a same-system fixed-policy-vs-rewrite comparison under a fixed solution-evaluation budget

The paper defines the optimization goal under a fixed budget `T` of sequential candidate evaluations. Its stagnation-triggered meta-loop changes the search strategy only when progress over a window falls below a threshold. In the reported experiments, the strategy window is 10% of the total iteration budget.

The strongest causal-looking ablation for the current frontier is Figure 4 on Heilbronn Triangle:

- fixed Beam Search vs EvoX initialized from Beam Search;
- fixed Best-of-N vs EvoX initialized from Best-of-N;
- fixed Top-K vs EvoX initialized from Top-K;
- fixed MAP-Elites vs EvoX initialized from MAP-Elites.

The paper states that the fixed strategies saturate while EvoX initialized from each strategy continues improving. The plotted run spans 100 solution iterations, matching the paper's standard open-framework budget. This is therefore stronger than a cross-system comparison and stronger than a scheduled meta-policy update with unequal fast-loop budgets.

However, the baseline is **continue with the old strategy**, not **stop**. So the causal contrast is best described as:

`Continue-fixed-policy` vs `stagnation-triggered strategy rewrite`.

It is not yet the full requested:

`Stop` vs `Widen` vs `Reopen`.

## 2. The strategy transition is demand-triggered, not merely periodic

The paper's Algorithm 1 runs solution evolution for a window `W`, computes best-score improvement `Delta`, and invokes the strategy generator if `Delta < tau`. The paper explicitly motivates this as demand-driven strategy switching: keep the current strategy while it works; rewrite it when progress stalls.

The signal-processing case study gives a qualitative trajectory where search moves from random sampling to greedy search, stratified multi-objective sampling, UCB-guided structural variation and finally local refinement. The important evidence for this worker is not the narrative labels themselves but that the proposal family controlling future solution generation is an explicit mutable object updated in response to measured stagnation.

## 3. Current public implementation exposes an important promotion gap

The current public controller is not merely a paper sketch. At the audited revision it:

1. tracks the current best solution score;
2. declares stagnation after `switch_interval` consecutive iterations without >0.01 improvement, with default `switch_interval` about 10% of total solution iterations;
3. asks the meta-search LLM for a new `EvolvedProgramDatabase` implementation;
4. validates that implementation structurally/functionally;
5. migrates the full solution population into the new database;
6. immediately hot-swaps the new search strategy into the live run.

The search-strategy evaluator checks class structure, sampling contract, metric preservation, migration compatibility and related functional invariants. It is not a candidate-vs-incumbent behavioral A/B test on downstream progress.

The key boundary is therefore:

**a structurally valid new search strategy becomes live before its downstream efficacy has been established against the incumbent.**

Its downstream search score is computed after it has already governed a solution-search window and is then stored for future meta-search. Runtime database errors can trigger fallback to the previous database, but ordinary low-quality search behavior is not a pre-commit rollback condition on this audited path.

So EvoX provides strong evidence for the value of making the search policy mutable, but its current public implementation does not supply the stronger promotion contract sought elsewhere in this frontier.

## 4. Evaluation hygiene remains a separate missing layer

The Heilbronn comparison uses the same optimization objective to:

- score solution candidates;
- detect stagnation;
- score search strategies;
- report the final best solution.

There is no untouched outer test in this optimization task. Therefore the result supports **optimization-surface progress under matched solution-evaluation budgets**, not fresh-task generalization.

The public paper also does not establish, for this Figure-4 comparison, any candidate-local anytime-valid promotion gate, proposal-spanning statistical risk budget, bounded hidden-feedback channel, or complete paper-run proposal chronology.

This matters because the current frontier now has two orthogonal questions:

1. **Should the search/improvement strategy itself be reopened?** EvoX materially strengthens the positive evidence.
2. **How should a proposed new strategy be safely admitted and externally validated?** EvoX does not resolve this.

## 5. Updated synthesis

The stagnation-control ladder should now be separated into at least four interventions:

A. Stop on plateau.

B. Continue with the same policy and same budget.

C. Widen/redirect candidate search while keeping the policy family fixed.

D. Reopen/rewrite the policy family itself.

EvoX gives a direct same-system B-vs-D comparison on a fixed candidate-evaluation budget. MetaSkill-Evolve and HSI show meta-policy mutability in other settings; Harness Evolver exposes an explicit architecture-reopen trigger; Adaptive Auto-Harness exposes a stop-on-convergence path. No source-bound public experiment found so far gives a fully matched A-vs-B-vs-C-vs-D comparison with a separate untouched outer test.

## Scope / non-claims

- Do not call the fixed-strategy Figure-4 baseline a stop condition; it continues spending the 100-iteration budget.
- Do not infer that all of EvoX's gain is free under equal total compute: the solution-evaluation budget is matched, but strategy-generation LLM calls add meta-level cost.
- Do not interpret structural/function validation of a new search database as evidence that it is behaviorally better than the incumbent.
- Do not infer held-out generalization from the Heilbronn optimization score.
- Do not assume the audited current public controller is byte-identical to the historical paper-run executable.
- Do not generalize the figure's causal scope beyond the compared task/initializations without separate evidence.

## Nonempty frontier / exact next action

1. Recover EvoX's exact Figure-4 run configuration, seeds, logs or paper-bound executable if publicly available; verify whether the fixed and evolving curves share the same generator model, evaluator, initialization seed and all solution-level budget except meta-strategy generation.
2. Recover strategy-transition chronology if public and measure how many rewrites occurred, whether any rewrite reduced subsequent progress, and whether a simple incumbent-behavioral gate would have rejected harmful strategy transitions.
3. Continue searching for a same-system **Stop vs Continue-fixed vs Widen vs Reopen** experiment under equal proposal/evaluation budgets with an untouched final test.
4. For any candidate, independently audit candidate-local anytime-valid acceptance, restart-durable cross-proposal statistical spending, immutable promotion identity and complete proposal chronology.
5. Extend the matrix only when a source closes one of those missing columns; do not repeat generic meta-learning evidence.

Research remains open; this is a continuation boundary, not completion.
