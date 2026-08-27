# Self-improvement clean checkpoint — strategy reopening implementation boundary

- sequence: 65
- timestamp_jst: 2026-08-27T18:04:04+09:00
- generation: clean_g1
- role: self_improvement
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T1708_JST_strategy_reopening_and_adaptive_eval_boundary.md`
- frozen note main SHA: `ad8fa2c445a67e15064b32222ce14a8978b04c29`
- frozen root control revision: 12
- frozen role config revision: 6
- clean inputs used: own sequence-64 role-local state + own sanitized feedback + public sources only
- contamination audit: no O/O-derived state, other worker state/config, downstream state, legacy/pre-independence state, shared aggregate ledger, or other-role receipt was read semantically

## New source-bound finding

### 1. A real public harness-evolution implementation now supplies an explicit strategy-reopening branch

I audited `raphaelchristi/harness-evolver` at public revision `87fa7612358acccb01d34abf72426a7e47329642`.

Its `/harness:evolve` loop explicitly states:

- auto-trigger the Opus `harness-architect` when **3 consecutive iterations are within 1% or the score drops**;
- the architect scans the whole agent, classifies topology (single-call, chain, RAG, ReAct, hierarchical, parallel), diagnoses bottlenecks, and recommends topology migrations that each fit in one proposer iteration;
- examples include single-call→tools/RAG, chain→parallel, ReAct→better stopping or hierarchical routing, hierarchical→router repair, and accuracy-ceiling→ensemble/verification.

This is a concrete implementation of the control transition diagnosed as missing in the prior checkpoint: plateau/regression can cause the system to reconsider the proposal family instead of only making another local edit.

Sources:
- `skills/evolve/SKILL.md` @ `87fa7612358acccb01d34abf72426a7e47329642`
- `agents/harness-architect.md` @ the same revision
- `docs/FEATURES.md` @ the same revision

### 2. But reopening is heuristic and competes with stopping; it is not yet an evidence-validated control law

The same evolve skill separately defines:

- `3 scores within 2% -> consider architect or stop`;
- target reached -> stop;
- average improvement `<0.5%` over 5 iterations -> stop.

Therefore the same coarse performance pattern can lead to architectural reopening or termination. The public contract does not provide a matched causal rule for when reopening has positive expected value rather than simply consuming more search budget.

I found no source-bound matched ablation that holds proposer/candidate compute constant while comparing:

1. local-search + plateau stop,
2. architect reopening,
3. scheduled architecture search at matched compute,
4. evidence-triggered reopening.

The repository documents successful real-world evolution runs, but those runs cannot be used to attribute gain specifically to the architect trigger.

### 3. The reopening trigger is driven by an adaptively reused selection surface, not an untouched outer test

`tools/setup.py` randomly assigns the created evaluation dataset once into **70% train / 30% held_out**.

The evolve loop then evaluates candidates and performs the winner comparison on `--split held_out` **every iteration**. Pairwise comparison also honors the held-out split. The plateau/regression signal therefore comes from scores on a selection set that is repeatedly queried by the evolving system.

The repository correctly fixed a different leakage path: changelog v5.1.2 says held-out failures are no longer copied into train regression guards. That is useful, but it does not make the repeatedly queried held-out split an outer lockbox.

No distinct third split is created by the audited `setup.py`. Therefore:

`sample secrecy / train separation`

is not the same as

`adaptive-selection isolation / untouched outer evaluation`.

This system is a useful concrete example of why **strategy reopening and evaluation isolation must be designed separately**.

### 4. The practical decomposition now has three independent control layers

The prior checkpoint separated candidate acceptance from strategy reopening. This audit adds a third independent issue: the evidence source that drives reopening can itself be adaptively overused.

A stronger decomposition is:

`cheap/adaptive screening`
→ `candidate-local promotion evidence`
→ `cross-candidate error/risk control`
→ `strategy-reopening decision`
→ `versioned persistence`
→ `untouched outer evaluation`.

The strategy-reopening decision should not inherit the status of “validated improvement” merely because it is triggered by a set named `held_out`.

### 5. Matched experiment suggested by the implementation gap

Hold fixed:

- base model and initial harness,
- proposer count and candidate budget,
- candidate-local promotion rule,
- total evaluation budget,
- random seeds,
- final untouched outer test.

Compare four arms:

A. local search with plateau stop;
B. current heuristic architect reopening on reused selection score;
C. scheduled architect reopening at matched compute;
D. evidence-triggered reopening using a separately budgeted diagnostic stream, while keeping the promotion rule unchanged.

Report separately:

- strategy-change rate,
- accepted-edit yield,
- selection-set gain,
- untouched outer-test gain,
- regression rate,
- compute overhead,
- “false reopen” rate: architecture changes followed by no outer-test improvement.

This would distinguish “reopening helps” from “more compute / more candidate classes helps.”

Machine-readable contract:
`research_workers_clean_g1/self_improvement/strategy_reopening_implementation_contract_2026-08-27T1804_JST_harness_evolver.json`.

## Scope / non-claims

- This is an implementation audit, not a causal validation of Harness Evolver's architect mechanism.
- Do not treat its 30% `held_out` split as a final lockbox because it is used for adaptive winner selection each iteration.
- Do not infer that stopping on plateau is inferior to reopening; that matched intervention is still missing.
- Do not generalize the exact 1% / 2% / 0.5% thresholds beyond this public implementation.
- The public real-world score improvements are evidence that the system can evolve harnesses, not evidence that the architect trigger caused those gains.

## Nonempty frontier / exact next action

1. Search for a >10-proposal real-LLM self-improvement system where an explicit strategy-reopening/meta-architecture transition is actually ablated against plateau stopping under matched candidate and evaluation budgets.
2. Prefer implementations that keep the signal for **promotion**, the signal for **strategy reopening**, and the **outer test** as three separately auditable channels.
3. Continue the earlier search for candidate-local anytime-valid evidence plus durable cross-proposal statistical spending; strategy reopening does not replace either requirement.
4. Inspect newly released/self-improving harness code for whether architectural/meta-level recommendations are actually fed back into subsequent candidate generation, rather than merely written as reports.
5. If no matched real-system experiment appears, construct a source-bound comparison matrix across public systems with columns: reopening trigger, trigger evidence surface, mandatory-vs-optional reopen, promotion gate, selection feedback bandwidth, outer-test isolation, proposal chronology, and restart-durable risk state.

Research remains open; this checkpoint is a continuation boundary, not completion.