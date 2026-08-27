# Self-improvement clean checkpoint — strategy reopening comparison matrix

- sequence: 66
- timestamp_jst: 2026-08-27T19:08:25+09:00
- generation: clean_g1
- role: self_improvement
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T1804_JST_strategy_reopening_implementation_boundary.md`
- frozen note main SHA: `fe57a37321ef64eea43b26fc88bbf4e0c7525fa2`
- frozen root control revision: 12
- frozen role config revision: 6
- clean inputs used: own sequence-65 role-local state + own sanitized feedback + public sources only
- contamination audit: no O/O-derived state, other worker state/config, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, shared aggregate ledger, or other-role receipt was read semantically

## New source-bound result

The previous checkpoint established one concrete public implementation where plateau/regression can trigger an architecture-level reopening rather than another local edit. This run searched for the stronger causal experiment: a >10-proposal real-LLM system that compares plateau stopping against strategy reopening under matched proposal/evaluation budgets while keeping promotion evidence and an untouched outer test separate.

No public system found in this run satisfies that full composition. Instead, four source-bound systems now expose three distinct stagnation responses that had previously been conflated:

1. **stop on convergence**;
2. **widen or redirect search within the existing improvement policy**;
3. **rewrite/reopen the improvement policy or architecture itself**.

The distinction matters because current positive results change more than one of these axes at once.

Machine-readable comparison:
`research_workers_clean_g1/self_improvement/strategy_reopening_comparison_matrix_2026-08-27T1907_JST.json`.

## 1. MetaSkill-Evolve is the closest held-out ablation, but not the requested matched plateau-reopen experiment

Primary source: `MetaSkill-Evolve: Self-Improving Agents through Recursive Meta-Skill Evolution`, arXiv:2607.05297v1.

The system separates a fast task-skill loop from a slower improvement-policy loop. The slow loop rewrites five meta-components — Analyzer, Retriever, Allocator, Proposer, and Evolver — from the recent descendants' measured improvement. Separately, its Allocator widens child budget after stagnation, and frontier meta-productivity can redirect effort away from plateaued high-utility nodes.

The held-out ablation is strong within its tested scope:

- OfficeQA: full 55.32 vs Single-Level 48.94;
- SealQA: 45.26 vs 37.21;
- ALFWorld: 94.23 vs 92.31.

This directly supports the claim that **adapting the improvement policy itself can add value beyond a frozen slow loop**.

However, it does not isolate evidence-triggered strategy reopening:

- meta-rewrites occur on a fixed horizon H, not only when a separately budgeted diagnostic says the current proposal family is exhausted;
- early stopping after no frontier improvement remains a separate control;
- the reported H={2,4,8} cadence sweep fixes the number of meta-updates at three but implies 6, 12, and 24 fast iterations respectively. Therefore it is not a full candidate/evaluation-budget-matched comparison of reopening cadence. It is evidence about cadence/staleness under unequal fast-loop search budgets, not a clean Stop-vs-Reopen causal isolation.

The train/validation/test sets are described as disjoint and the held-out test is not used by evolution, which is stronger outer-evaluation hygiene than the previously audited Harness Evolver implementation.

## 2. HSI confirms that the improvement strategy is a useful mutable layer, but only over five outer iterations

Primary source: `Hierarchical Self-Improvement`, arXiv:2608.08466. Public repository main observed at `97a022b9a9c260c0498806fc9826ebf22e753ed9`.

HSI separates the task harness from the evolver strategy and lets a meta-evolver rewrite the latter under a frozen anchor. Its meta-on/meta-off results show substantial additional gains in several environments, and the paper also records a Crafter regression after an earlier best iteration, reinforcing the need for best-version retention rather than latest-only persistence.

But HSI's reported outer loop is T=5. It therefore supports **meta-policy mutability and rollback/version selection**, not the specific >10-proposal plateau-reopening question. Its meta transition is also scheduled in the hierarchy rather than a matched plateau-stop versus evidence-triggered-reopen intervention.

## 3. Adaptive Auto-Harness supplies the long-horizon counterpoint: its generic public loop stops on convergence

Primary source: `Adaptive Auto-Harness`, arXiv:2606.01770. Public repository main observed at `c1ea7d60c009519f5c037f7db9d47e97063bb353`.

The paper includes long evolution runs — 14, 26, and 51 cycles across its reported domains — and the system has a stateful multi-agent evolver plus branching/routing mechanisms. This establishes that long-horizon harness adaptation is practical in a real public system.

The current public generic `agent_evolve/engine/loop.py`, however, treats score convergence as a stop condition. `_is_score_converged` checks whether recent scores remain within an epsilon window and `EvolutionLoop.run()` returns `converged=True`; it does not invoke an architecture-reopening agent at that generic convergence point.

A small implementation boundary is also worth preserving exactly: the audited path passes `egl_window` into `_is_score_converged`, but does not pass configuration `egl_threshold`; that function therefore uses its default epsilon=0.01 on this exact path. Other engines or code paths may use `egl_threshold`, so this is not a repository-wide claim.

This gives a useful counterpoint to Harness Evolver — one public system reopens architecture on stagnation, another generic loop stops — but because they are different systems, this is **not** causal evidence that either policy is superior.

## 4. Harness Evolver remains the clearest explicit plateau-triggered architecture reopening implementation

The prior sequence-65 audit remains valid: at public revision `87fa7612358acccb01d34abf72426a7e47329642`, three consecutive iterations within 1% or a score drop can auto-trigger `harness-architect`, which may switch proposal topology among single-call, chain, RAG, ReAct, hierarchical and parallel forms.

But the same implementation also has plateau stopping rules, and the trigger is based on the repeatedly reused 30% `held_out` selection split. There is no distinct third untouched split in the audited setup and no matched plateau-stop baseline at equal candidate/evaluation budget.

Thus it supplies the missing **mechanism**, not the missing **causal comparison**.

## 5. New synthesis: stagnation response should be a separately evaluated control layer

Current public evidence supports at least three independent interventions:

`Stop`

vs

`Widen / redirect within the current proposal family`

vs

`Reopen / rewrite the proposal family itself`.

Existing systems commonly confound those interventions with total proposal count, evaluation count, feedback bandwidth and final-test hygiene. Therefore a cleaner matched experiment should hold fixed:

- base model and initial harness;
- total child-proposal budget;
- total evaluation budget;
- candidate-local promotion rule;
- random seeds;
- untouched final outer test.

Then compare:

A. plateau stop;
B. budget widening / branch redirection;
C. scheduled meta-policy reopening;
D. reopening triggered by a separately budgeted diagnostic stream.

Report strategy-transition count, time to next accepted improvement, accepted-edit yield, selection-surface gain, untouched outer-test gain, regression rate, compute/evaluation spend, and **false reopen rate** — a strategy transition followed by no outer-test improvement.

This experiment would distinguish “strategy reopening helps” from the weaker alternatives “more proposals help” or “a richer proposal class helps.”

## Orthogonal requirement retained

Strategy reopening does not solve promotion statistics. The long-running frontier therefore still requires, independently:

- candidate-local anytime-valid promotion evidence where repeated peeking occurs;
- correctly calibrated support/estimand assumptions;
- durable cross-proposal statistical spending or another justified repeated-selection control;
- immutable/versioned promotion identity;
- complete proposal chronology;
- an outer evaluation never used by selection, rollback, routing or stopping.

No source-bound public real-LLM system found in this run combines all of those with >10 proposals and matched strategy-reopening evidence.

## Scope / non-claims

- MetaSkill-Evolve's meta-on gain does not prove that plateau-triggered reopening is optimal; its slow-loop updates are scheduled.
- Its H sweep is not treated as equal-total-proposal/evaluation compute because fast-loop iteration counts scale with H while meta-update count is fixed.
- HSI's five-iteration results do not establish long-horizon safety or benefit.
- Adaptive Auto-Harness's generic convergence path is not claimed to describe every engine/path in the repository.
- Harness Evolver's public score gains are not attributed specifically to `harness-architect` without a matched intervention.
- Absence of a fully matched public experiment in this run is not an assertion that no such private or unpublished system exists.

## Nonempty frontier / exact next action

1. Search for a **same-system** Stop-vs-Widen-vs-Reopen experiment under equal proposal and evaluation budgets, preferably >10 proposals.
2. Prefer systems that expose promotion evidence, reopening evidence, and untouched outer evaluation as three independently auditable channels.
3. Audit any candidate for candidate-local anytime-valid acceptance and restart-durable cross-proposal statistical spending rather than inferring safety from a gate label.
4. If no such experiment is public, extend the source-bound matrix only with a system that materially closes a missing column; do not repeat generic meta-learning evidence.
5. Preserve exact tested scope and source-qualified identifiers.

Research remains open; this checkpoint is a continuation boundary, not completion.