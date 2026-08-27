# Primary verification audit — C22 self_improvement Harness Evolver strategy reopening

Observed: 2026-08-27T22:00:00+09:00
Verifier semantic tuple remains frozen at note `76f8f14c697b65938f3dbabcda310b47293faf12` / control revision 28 / primary_source_verifier config revision 8.
Clean source tuple: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T1804_JST_strategy_reopening_implementation_boundary.md` @ blob `aa1c4b973e3d8623e154926fea4637d3d2ea59ab`.
Public implementation: `raphaelchristi/harness-evolver@87fa7612358acccb01d34abf72426a7e47329642`.

## Verdict

**SOURCE-LEVEL MECHANISM VERIFIED; CAUSAL BENEFIT UNVERIFIED.** The pinned public implementation really does include an explicit plateau/regression-triggered architectural reopening path, and it repeatedly uses a split named `held_out` for candidate winner selection. The source does not provide a matched experiment establishing that the architect trigger improves an untouched outer test relative to plateau stopping or scheduled extra architecture search at equal compute.

## 1. Reopening trigger and architectural scope

`skills/evolve/SKILL.md` explicitly auto-triggers the Opus `harness-architect` when `3 consecutive iterations` are within `1%` or the score drops.

The same skill separately defines stopping/gate heuristics:

- `3 scores within 2%` -> consider architect or stop;
- target reached -> stop;
- average improvement `<0.5%` over 5 iterations -> stop.

So the public control contract does not define a single evidence-validated policy for whether a plateau should terminate search or reopen the strategy family; reopening and stopping can be candidates under nearby performance patterns.

`agents/harness-architect.md` confirms that the reopening agent scans the broader codebase, classifies topology (single-call, chain, RAG, ReAct, hierarchical, parallel), and may recommend topology migrations such as single-call -> tools/RAG, chain -> parallel, ReAct -> improved stopping/hierarchical routing, or adding ensemble/verification at an accuracy ceiling. Each migration is required to fit in one proposer iteration.

## 2. The repeatedly queried `held_out` split is a selection surface, not an untouched outer lockbox

`tools/setup.py` defines `assign_splits(..., train_pct=70)`, randomly shuffles the examples once, assigns the first 70% to `train`, and the remainder to `held_out`.

In the evolve loop, candidate comparison is then performed each iteration with:

`read_results.py ... --split held_out`

and optional pairwise comparison also uses `--split held_out`. The winner is explicitly the highest score on held-out data before constraint/efficiency gating and merge.

Therefore the 30% split is held apart from the ordinary `train` split, but it is **adaptively reused for candidate selection across iterations**. Naming it `held_out` does not make it an untouched final test after repeated selection pressure. In the audited setup/evolve contract, no distinct third outer-evaluation split is created.

## 3. Scope guard

This audit establishes implementation properties only:

- plateau/regression can trigger a real architectural/meta-strategy analysis rather than another purely local edit;
- the same public loop also contains independent stopping rules;
- candidate selection repeatedly queries the 30% `held_out` surface.

It does **not** establish:

- that the architect trigger causally improves final generalization;
- that reopening is superior to stopping under matched proposal/evaluation compute;
- that the exact `1%`, `2%`, or `0.5%` thresholds transfer to other systems;
- that repeated held-out use actually caused a measured overfitting failure in a reported run.

The clean worker's proposed experiment remains appropriate: hold model, proposer/candidate budget, promotion rule, total evaluation budget and seeds fixed, compare plateau stop versus heuristic reopen versus scheduled reopen versus separately budgeted evidence-triggered reopen, and report an untouched outer test plus false-reopen rate.

No exploration worker state, worker feedback, comparator output, O state, or feed was modified by this audit.