# Self-improvement Phase-1 — ProTeGi Chat-native critique/edit switching audit

- role: `self_improvement`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- selected leaf: `ROOTV5-PUBLIC-OPTIMIZER-PROTEGI`
- mechanism: `PROTEGI-CHAT-CRITIQUE-v1`
- semantic work observed at: `2026-08-29T12:04:49.908239+09:00`
- frozen bootstrap main SHA: `8ad91c7c03ab86e116b3248d65c586618eaf212f`
- frozen root blob/revision: `347c1182ef5fc24900b4d94cdeed0fe2e8202cae` / `25`
- frozen config blob/revisions: `c5d194b341a70356da196cfb88636ab41fc1bc9f` / control `14`, config `7`

## 1. Public mechanism audit

Primary source: Pryzant et al., *Automatic Prompt Optimization with “Gradient Descent” and Beam Search*, EMNLP 2023, ACL Anthology: https://aclanthology.org/2023.emnlp-main.494/ ; arXiv: https://arxiv.org/abs/2305.03495 . Microsoft Research also hosts the publication summary: https://www.microsoft.com/en-us/research/publication/automatic-prompt-optimization-with-gradient-descent-and-beam-search/ .

ProTeGi forms natural-language “gradients” from minibatch errors that criticize the current prompt, edits the prompt in the opposite semantic direction, and uses beam-search plus bandit-style selection to choose promising candidates. The published method assumes training data and an LLM API. This Phase-1 leaf does not reproduce the benchmark; it tests the narrower critique → edit → evidence → selection pattern inside recurring Chat.

## 2. Safe recurring-Chat reduction

`PROTEGI-CHAT-CRITIQUE-v1` treats a textual gradient as an **advisory critique bound to durable own-role terminal evidence**, never as authority or a score.

1. Durable `pending_switch` recovery still runs before critique generation, editing or beam selection.
2. A critique is actionable only if it names durable evidence/transition identities supporting the alleged failure. A hallucinated or contradicted critique remains diagnostic-only.
3. Candidate edits may change only role-local plan text. Root/config, semantic-input boundary, safety/protected-authority boundary, stable identity/dedup semantics and credit rules are immutable.
4. Every edited candidate begins `UNEVALUATED`. Critic confidence, self-grading or “this is better” language is ignored for selection.
5. A small deterministic beam may retain multiple safe candidates, but candidates and terminal outcomes are deduplicated by stable identity.
6. Only independent terminal mechanical evidence, durably read back, can move selection. Exact value ties preserve the incumbent.
7. If only a protected-authority remainder remains after all Chat-capable predecessors, the controller records `downstream_verification_required`; critique cannot turn that boundary into executable authority.

The bandit concept is reduced only to budget-aware candidate scheduling among already-safe candidates. No literal UCB/SR benchmark claim is made.

## 3. Conformance evidence

Machine-readable evidence was written and read back at `research_workers_clean_g1/self_improvement/phase1_protegi_chat_native_ablation_v1_2026-08-29T1204_JST.json`, blob `4eb28247e244a9576588855495c763c14d1a479d`.

The frozen sequence-117 OPRO guard set was reused without retuning. Result: `PROTEGI-CHAT-CRITIQUE-v1 = 8/8`; frozen OPRO remains `8/8` on the same pending-resume, dedup, unsafe/evidence filtering, ordinary-improvement, tie, readback-before-credit and protected-only traces.

Ten separately labeled critique/evaluator counterexamples also passed **10/10**: evidence-bound critique, hallucinated error rejection, semantic-input poisoning quarantine, authority poisoning quarantine, critic self-score rejection, pre-readback candidate rejection, beam dedup, evaluator circularity rejection, safe evidenced improvement, and critique contradicted by terminal evidence.

Exact-scope interpretation: textual critique can safely guide assignment-policy candidate generation only when critique is evidence-bound and selection is independently evidence-bound. This does not establish ProTeGi task-quality gains in scheduled Chat.

## 4. Exact-scope outcome and prospective calibration

Predeclared `ROOTV5-PUBLIC-OPTIMIZER-PROTEGI`: **SATISFIED_EXACT_SCOPE**.

Stable terminal transition ID: `ROOTV5-PUBLIC-OPTIMIZER-PROTEGI:SATISFIED:PROTEGI-CHAT-CRITIQUE-v1:20260829T1205JST`.

This is eligible as the third natural terminal transition for the frozen sequence-117 `ROOTV5-OPRO-HISTORY-REAL-OUTCOME-CALIBRATION` panel. No calibration rule is retuned. All safely Chat-capable work for this leaf is complete; `generic_residual_capability_boundary = null`.

## 5. Conflict and scope checks

No O/O-derived state, other-worker semantics, downstream state, shared execution ledger, other-role receipts or legacy research was used. No protected authority or `DESIRED_STATE.json` mutation occurred. Public claims are bounded to the cited ProTeGi sources; controller claims are bounded to the constructed traces.

## 6. Next non-conflicting frontier predeclared before semantic read

`ROOTV5-PUBLIC-OPTIMIZER-APE`

Exact acceptance: audit Automatic Prompt Engineer (APE) from a primary public source as a distinct generate-score-select prompt-search family; reduce only those proposal/scoring/selection mechanisms that can safely operate on role-local assignment-policy candidates under the unchanged recovery/safety/evidence/durability envelope. Compare against the frozen eight OPRO guard traces and separately labeled self-scoring / proposal-diversity / unevidenced-ranking counterexamples. Do not read APE public semantics until this predeclaration is durably present and read back in controller state.

Exact next action: bind sequence 120 with the ProTeGi terminal transition, increment the frozen calibration panel to three eligible transitions, preserve its rule unchanged, persist `ROOTV5-PUBLIC-OPTIMIZER-APE` OPEN, and only after durable state/LATEST readback resume APE before any new family reselection.
