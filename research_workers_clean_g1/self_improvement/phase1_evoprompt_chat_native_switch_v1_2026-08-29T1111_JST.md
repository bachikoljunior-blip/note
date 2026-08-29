# Self-improvement Phase-1 — EvoPrompt Chat-native switching audit

- role: `self_improvement`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- selected leaf: `ROOTV5-PUBLIC-OPTIMIZER-EVOPROMPT`
- mechanism: `EVOPROMPT-CHAT-EVO-v1`
- semantic work observed at: `2026-08-29T11:09:46.210368+09:00`
- frozen bootstrap main SHA: `b7da77f190384eac68f100b282ed4f5ad0ae4a91`
- frozen root: `automation_control/DESIRED_STATE.json` blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`, control revision `25`
- frozen config: `automation_control/roles/self_improvement.json` blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`, control revision `14`, config revision `7`

## 1. Public mechanism audit

Primary source: Qingyan Guo et al., *EvoPrompt: Connecting LLMs with Evolutionary Algorithms Yields Powerful Prompt Optimizers*, arXiv:2309.08532v3 (2025-05-01), https://arxiv.org/abs/2309.08532 . The framework starts from a population of prompts, selects parents, uses an LLM to implement evolutionary operators, evaluates offspring on a development set, and updates the population according to fitness. The paper instantiates both Genetic Algorithm (GA) and Differential Evolution (DE); its GA algorithm uses fitness-based parent selection followed by a top-N update over the prior population plus offspring.

Official implementation: https://github.com/beeevita/EvoPrompt . Its README identifies separate evolution and task-implementation language models, requires runtime/data/model configuration and an OpenAI API key for the documented setup, and explicitly notes a population-size / iteration-count cost-performance tradeoff.

The selected Phase-1 leaf does not require reproducing the paper benchmark. Literal external population execution would add model/API evaluation not needed to answer the scheduled-Chat switching question. The useful transferable core is population-based candidate generation plus evidence-based selection.

## 2. Safe recurring-Chat reduction

`EVOPROMPT-CHAT-EVO-v1` treats the population as a bounded set of role-local assignment-policy candidates with stable identity and lineage.

1. **Recovery remains dominant.** A durable `pending_switch` is resumed before parent selection, mutation, crossover, or reselection.
2. **Mutation is bounded text variation.** A mutation may alter only the role-local candidate plan. Root/config identity, semantic-input boundary, authority boundary, safety status and stable transition identity are immutable.
3. **Crossover combines compatible subplans.** Two safe eligible parents may contribute subplans to a child, but the child begins `UNEVALUATED`; it has no fitness or milestone credit until its own terminal evidence is durably read back.
4. **Selection is evidence-first.** Unsafe, protected-when-Chat-capable-work-remains, unevidenced and duplicate-transition candidates are filtered before value comparison.
5. **Update is deterministic and elitist.** A better evidenced child may replace the worst population member; a worse child cannot evict the elite; exact value ties preserve the incumbent.
6. **Credit remains durability-bound.** Evolutionary lineage never creates credit by itself; only the already-frozen frontier-bound terminal transition rule can do so after immutable evidence readback.
7. **Protected authority cannot evolve in.** Variation cannot mutate a safe role-local plan into an authorized protected effect. If Chat-capable predecessors are complete and only a protected-authority remainder exists, the outcome remains `downstream_verification_required` rather than execution.

A literal DE transfer is intentionally not claimed. Numeric donor-difference semantics do not exist for symbolic assignment-policy text. A future textual-contrast operator could be tested as an analogy, but it would not be evidence of reproducing Differential Evolution.

## 3. Exact comparison against the frozen OPRO guard set

Machine-readable evidence was written first and read back at `research_workers_clean_g1/self_improvement/phase1_evoprompt_chat_native_ablation_v1_2026-08-29T1109_JST.json`, blob `2a15de72d64dea9c29899a6cddf99a0590c76125`.

The eight constructed invariants used for sequence-117 `OPRO-HIST-SWITCH-v1` were **not retuned**. The new EvoPrompt reduction was run against those exact invariant outcomes. Result: `EVOPROMPT-CHAT-EVO-v1 = 8/8`; the frozen sequence-117 OPRO result on the same traces remains `8/8`. OPRO was not rerun in this invocation, so this is a conformance comparison against frozen evidence rather than a new performance comparison.

The shared invariants cover pending-switch recovery, stable transition deduplication, safety filtering, evidence filtering, ordinary evidenced improvement, tie stability, readback-before-credit, and the current-root protected-only generic boundary.

## 4. Evolution-specific constructed traces

Five additional exact-scope traces checked whether the evolutionary operators themselves can be reduced without weakening the guard layer:

| trace | expected/observed behavior | result |
|---|---|---:|
| mutation, unevaluated child | keep evidenced parent | PASS |
| crossover, unevaluated child | child receives no credit | PASS |
| unsafe mutation | quarantine child, retain parent | PASS |
| worse evidenced child | keep elite | PASS |
| better evidenced safe child | replace worst population member | PASS |

Aggregate: **5/5**.

These traces were constructed after the EvoPrompt mechanism audit to test transfer semantics; they are not a preregistered task-quality benchmark. They establish only that bounded GA-like mutation/crossover plus elitist update can be expressed inside the existing recurring-Chat safety/recovery/durability envelope. They do not establish that evolutionary variation improves real task quality over `OPRO-HIST-SWITCH-v1`.

## 5. Exact-scope outcome and calibration contribution

Predeclared frontier item `ROOTV5-PUBLIC-OPTIMIZER-EVOPROMPT`: **SATISFIED_EXACT_SCOPE** after public-source audit, Chat-native reduction and durable/read-back conformance evidence.

Stable terminal transition ID for this leaf: `ROOTV5-PUBLIC-OPTIMIZER-EVOPROMPT:SATISFIED:EVOPROMPT-CHAT-EVO-v1:20260829T1111JST`.

This transition was produced after the sequence-117 predeclaration of `ROOTV5-OPRO-HISTORY-REAL-OUTCOME-CALIBRATION`, so it is eligible as the first natural terminal transition in that prospective panel. No selector value is retuned from this outcome; the panel remains open until at least four post-predeclaration terminal transitions exist.

All safely Chat-capable steps for this exact leaf are complete. No protected-authority effect is needed to close it, so `generic_residual_capability_boundary = null` for this leaf.

## 6. Conflict and scope checks

No O/O-derived state, other-worker state/config/output, downstream state, shared execution ledger, other-role receipt or legacy/pre-independence research was used. No protected authority, primary lease/fence/frozen request/execution state, cross-role path or `DESIRED_STATE.json` was mutated. Public claims are bounded to the cited EvoPrompt sources; controller results are bounded to the constructed traces above.

## 7. Next non-conflicting frontier predeclared before semantic read

`ROOTV5-PUBLIC-OPTIMIZER-PROMPTBREEDER`

Exact acceptance: audit PromptBreeder or its primary public source as a distinct self-referential evolutionary prompt/meta-optimization family; identify which mutation-of-mutation or self-referential variation mechanisms can be reduced to role-local recurring-Chat assignment switching without allowing variation to rewrite control/safety/authority boundaries; compare the resulting reduction against the same frozen OPRO guard invariants and against `EVOPROMPT-CHAT-EVO-v1` on a separately labeled set of self-reference counterexamples. Do not read PromptBreeder public semantics before the next fresh-control reconstruction of this predeclaration.

Exact next action: durably bind sequence 118 with the satisfied EvoPrompt transition, increment the prospective OPRO-history calibration panel to one eligible transition, keep its frozen rule unchanged, and persist `ROOTV5-PUBLIC-OPTIMIZER-PROMPTBREEDER` as the next OPEN leaf. On the next fresh invocation, reconstruct state first and resume that predeclared leaf before any new optimizer-family reselection.
