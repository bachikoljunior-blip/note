# Self-improvement Phase-1 — MIPROv2 Chat-native instruction/surrogate audit

- role: `self_improvement`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- selected frontier: `ROOTV5-STICKY-DISAGREE-STRESS-008B`
- candidate: `CAND-STRESS-008B` / `textual_edit_search`
- sealed selector round: `HIST-STICKY-ONLINE-v2.1` round 8, decision blob `d4cddfa150b834c13faa2e2fb3266b8b65c79523`
- policy disagreement: HISTORY=`CAND-STRESS-007B`, STICKY=`CAND-STRESS-008B`; scheduled factual policy=`STICKY`
- bound public family: `MIPROv2`
- mechanism: `MIPROV2-CHAT-SURROGATE-v1`
- semantic observation: `2026-08-29T12:46:06+09:00`

## Public mechanism audit

Primary/public sources: Opsahl-Ong et al., *Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs*, EMNLP 2024 / arXiv:2406.11695, https://arxiv.org/abs/2406.11695 ; current DSPy MIPROv2 documentation, https://dspy.ai/api/optimizers/MIPROv2/ .

The paper factorizes prompt optimization into free-form instructions and few-shot demonstrations, uses program/data-aware instruction proposals, stochastic minibatch evaluation and a surrogate objective, and describes meta-optimization of proposal construction. Current DSPy documentation describes MIPROv2 as jointly optimizing instructions and demonstrations, or instructions alone, and using Bayesian Optimization to choose combinations. This leaf uses only the instruction-search abstraction and does not execute DSPy, model calls, Bayesian trials or published benchmarks.

## Safe recurring-Chat reduction

`MIPROV2-CHAT-SURROGATE-v1` treats an instruction proposal as an `UNEVALUATED` stable role-local assignment-policy candidate. Program/data-aware proposal text is advisory and cannot alter frozen root/config/control binding, CLEAN semantic-input boundaries, safety/protected-authority boundaries, stable frontier/candidate/transition IDs, the sealed selector decision, or readback-before-credit.

A Bayesian/surrogate score is exploration-only `NONFACTUAL`: it cannot create terminal evidence, archive utility, completion or credit. Only predeclared mechanical checks and independently read-back terminal evidence create factual utility. Proposal-heuristic meta-optimization stays inside the selected leaf and cannot self-certify or rewrite the immutable envelope. Durable pending recovery and the sealed factual selector decision precede proposal generation, surrogate search and reselection.

## Conformance evidence

Machine-readable evidence was created and read back at `research_workers_clean_g1/self_improvement/phase1_miprov2_chat_native_ablation_v1_2026-08-29T1246_JST.json`, blob `25ddd01007e1e18ac74b9ccdfc894f6f30af5c06`.

The unchanged frozen guard set passes **8/8** without retuning. Ten surrogate/program-specific counterexamples pass **10/10**: surrogate score cannot become credit; control- or CLEAN-boundary-changing proposals are quarantined; bootstrapped demonstrations are not evidence; minibatch score before readback is not factual utility; proposal meta-optimization cannot self-certify; duplicate terminal transitions count once; pending recovery precedes Bayesian exploration; independent safe improvement may be selected; and optimized wording cannot turn a generic protected-only remainder into Chat-executable authority.

Counterfactual `CAND-STRESS-007B` family semantics were not read and no counterfactual outcome was imputed.

## Exact-scope terminal outcome

`ROOTV5-STICKY-DISAGREE-STRESS-008B`: **SATISFIED_EXACT_SCOPE**, bound to MIPROv2.

Stable terminal transition ID: `ROOTV5-STICKY-DISAGREE-STRESS-008B:SATISFIED:MIPROV2-CHAT-SURROGATE-v1:20260829T1246JST`.

Under frozen `TERMINAL-UTILITY-v2.1`, this maps to utility `2`, subject to immutable round-8 outcome-record creation/readback and external outcome sealing. This is the scheduled STICKY factual side of a sealed policy-disagreement round.

## Conflict and continuation

No O/O-derived state, other-worker semantics, downstream state, shared execution ledger, other-role receipt, or legacy/pre-independence research was used. No protected authority or `DESIRED_STATE.json` mutation occurred.

Exact next action: read back this evidence; create/read back the immutable round-8 outcome record; only then update history/sticky state, award exactly one frontier-bound credit, and record the first STICKY-side policy-disagreement exposure. Do not semantically inspect or credit counterfactual `CAND-STRESS-007B`.
