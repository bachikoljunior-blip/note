# Self-improvement Phase-1 — Promptbreeder Chat-native self-referential switching audit

- role: `self_improvement`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- selected leaf: `ROOTV5-PUBLIC-OPTIMIZER-PROMPTBREEDER`
- mechanism: `PROMPTBREEDER-CHAT-META-v1`
- semantic work observed at: `2026-08-29T12:01:22.489095+09:00`
- frozen bootstrap main SHA: `8ad91c7c03ab86e116b3248d65c586618eaf212f`
- frozen root: `automation_control/DESIRED_STATE.json` blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`, control revision `25`
- frozen config: `automation_control/roles/self_improvement.json` blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`, control revision `14`, config revision `7`

## 1. Public mechanism audit

Primary source: Fernando et al., *Promptbreeder: Self-Referential Self-Improvement via Prompt Evolution*, ICML 2024 / PMLR 235, https://proceedings.mlr.press/v235/fernando24a.html ; arXiv:2309.16797, https://arxiv.org/abs/2309.16797 . The paper evolves a population of task-prompts, evaluates fitness on training data, and repeats over generations. Its defining self-referential move is that the mutation-prompts governing task-prompt mutation are themselves generated and improved during evolution.

This audit does not reproduce the paper's benchmark claims. The Phase-1 question is narrower: can mutation-of-mutation be represented as recurring-Chat assignment switching without letting self-reference rewrite control, semantic-input, safety, authority or credit boundaries?

## 2. Safe recurring-Chat reduction

`PROMPTBREEDER-CHAT-META-v1` separates two kinds of evolving text:

1. **Task-policy candidate.** A role-local assignment plan with stable candidate identity and terminal-transition lineage.
2. **Mutator-policy candidate.** A bounded variation tactic that may change how future task-policy candidates are proposed, but cannot mutate the immutable envelope.

The immutable envelope is root/config/control binding, CLEAN semantic-input allow/deny rules, safety/protected-authority rules, stable transition identity/dedup semantics and immutable-evidence-before-credit. Meta-mutation may change only bounded variation tactic text, the ordering of already-authorized variation operators, and non-authority-changing generation heuristics.

The anti-self-reward rule is prospective: a mutator-policy cannot score or activate itself from its own text. It becomes eligible only after at least one *independent terminal child transition produced under it* is durably read back. Duplicate terminal IDs count once, and activation is delayed until a later transition so the outcome used to establish evidence cannot be retroactively influenced by the new mutator.

Recovery still dominates optimization: durable `pending_switch` is resumed first. Unsafe/unevidenced/protected-when-Chat-capable-work-remains candidates are filtered before value comparison. Exact ties keep the incumbent. Task-policy credit and mutator-policy evidence both remain durability-bound.

## 3. Frozen OPRO guard comparison

Machine-readable evidence was written and read back at `research_workers_clean_g1/self_improvement/phase1_promptbreeder_chat_native_ablation_v1_2026-08-29T1201_JST.json`, blob `4269645962dadd4530212d00a7c444d58d02122c`.

The exact sequence-117 `OPRO-HIST-SWITCH-v1` guard traces were not changed or retuned: pending resume, transition dedup, unsafe filtering, evidence filtering, ordinary improvement, tie stability, readback-before-credit and current-root protected-only boundary. Result: `PROMPTBREEDER-CHAT-META-v1 = 8/8`; frozen OPRO remains `8/8` on those same traces.

## 4. Self-reference counterexamples and EvoPrompt comparison

Nine separately labeled meta-layer cases were checked. Promptbreeder reduction passed **9/9**:

- safe mutator promotion requires an independently terminal, durably read-back child outcome;
- attempted root/config rewrite is quarantined;
- attempted semantic-input boundary rewrite is quarantined;
- attempted protected-authority rewrite is quarantined;
- self-asserted mutator credit without child outcome gives `0`;
- child outcome before durable readback gives mutator credit `0`;
- duplicate child transition IDs count once;
- safe mutator activation is delayed to a later transition;
- an evidenced but mechanically worse mutator does not replace the incumbent mutator.

`EVOPROMPT-CHAT-EVO-v1` remains safe on the shared immutable-envelope cases, but it has no evolving mutator-policy state. Four of the safe self-reference cases are therefore labeled `NO_META_LAYER`, not failures. The exact-scope conclusion is expressivity only: Promptbreeder's self-referential abstraction can be represented safely by adding a second evidence-gated mutator-policy layer. This is **not** evidence of superior real-task quality over EvoPrompt or OPRO.

## 5. Exact-scope outcome and prospective calibration

Predeclared frontier item `ROOTV5-PUBLIC-OPTIMIZER-PROMPTBREEDER`: **SATISFIED_EXACT_SCOPE**.

Stable terminal transition ID: `ROOTV5-PUBLIC-OPTIMIZER-PROMPTBREEDER:SATISFIED:PROMPTBREEDER-CHAT-META-v1:20260829T1202JST`.

This is the second eligible natural own-role terminal transition after the sequence-117 predeclaration of `ROOTV5-OPRO-HISTORY-REAL-OUTCOME-CALIBRATION`. No selector rule is retuned from this result; the panel remains open until at least four eligible transitions exist.

All safely Chat-capable work for this exact leaf is complete. `generic_residual_capability_boundary = null` for this leaf.

## 6. Conflict and scope checks

No O/O-derived state, other-worker state/config/output, downstream state, shared execution ledger, other-role receipt or legacy/pre-independence research was used. No protected authority, primary lease/fence/frozen request/execution state, cross-role path or `DESIRED_STATE.json` was mutated. Public claims are bounded to the cited Promptbreeder paper; controller conclusions are bounded to the constructed traces.

## 7. Next non-conflicting frontier predeclared before semantic read

`ROOTV5-PUBLIC-OPTIMIZER-PROTEGI`

Exact acceptance: audit ProTeGi / textual-gradient prompt optimization from a primary public source as a distinct critique/edit/search family; identify which textual-gradient, candidate-edit and selection mechanisms can be reduced to recurring-Chat assignment switching while retaining the same frozen recovery/safety/evidence/durability guards. Compare the reduction against the frozen eight OPRO guard traces and on separately labeled critique-poisoning / evaluator-circularity counterexamples. Do not read ProTeGi public semantics until this predeclaration is durably present and read back in controller state.

Exact next action: bind sequence 119 with the Promptbreeder terminal transition, increment the frozen prospective OPRO-history calibration panel to two eligible transitions, preserve its selector unchanged, and persist `ROOTV5-PUBLIC-OPTIMIZER-PROTEGI` as the next OPEN leaf. After durable state/LATEST readback, the same frozen-control invocation may resume that predeclared leaf before any new optimizer-family reselection.
