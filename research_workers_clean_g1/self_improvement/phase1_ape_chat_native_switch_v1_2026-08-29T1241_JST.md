# Self-improvement Phase-1 — APE Chat-native textual program-search audit

- role: `self_improvement`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- selected frontier: `ROOTV5-HISTORY-DISAGREE-STRESS-007A`
- candidate: `CAND-STRESS-007A` / `textual_edit_search`
- sealed selector round: `HIST-STICKY-ONLINE-v2.1` round 7, decision blob `b7d5802696c06541dd0664b90409109c9156dc1a`
- policy disagreement: HISTORY=`CAND-STRESS-007A`, STICKY=`CAND-STRESS-007B`; scheduled factual policy=`HISTORY`
- bound public family: `Automatic Prompt Engineer (APE)`
- mechanism: `APE-CHAT-PROGRAM-SEARCH-v1`
- semantic observation: `2026-08-29T12:41:29+09:00`

## Public mechanism audit

Primary/public sources: Zhou et al., *Large Language Models Are Human-Level Prompt Engineers*, ICLR 2023 / arXiv:2211.01910, https://arxiv.org/abs/2211.01910 ; official repository https://github.com/keirp/automatic_prompt_engineer .

APE treats a natural-language instruction as a program, generates a pool of instruction candidates with an LLM, evaluates candidates using a chosen score function and selects high-scoring instructions. The public implementation exposes candidate-generation and evaluation templates and can use UCB-style sampling. This leaf does not reproduce APE benchmark results or literal model/API evaluation.

## Safe recurring-Chat reduction

`APE-CHAT-PROGRAM-SEARCH-v1` maps an instruction/program to a stable bounded role-local assignment-policy candidate. Generated instructions are `UNEVALUATED`: they cannot alter frozen root/config/control binding, CLEAN semantic-input boundaries, safety/protected-authority boundaries, stable frontier/candidate/transition identities, the sealed selector decision, or readback-before-credit.

Only predeclared mechanical checks and independently read-back terminal evidence produce factual utility. Generator claims, evaluator prose and same-transition self-scores are nonfactual. Selection is deterministic over safe factual candidates, with exact factual ties retaining the incumbent. Durable pending recovery and the sealed factual selector decision precede generation or reselection.

## Conformance evidence

Machine-readable evidence was created and read back at `research_workers_clean_g1/self_improvement/phase1_ape_chat_native_ablation_v1_2026-08-29T1241_JST.json`, blob `f32355e88c098911bacecac87489deaf3197a659`.

The unchanged frozen guard set passes **8/8** without retuning. Ten program-search counterexamples pass **10/10**: generated text is not evidence; control- and CLEAN-boundary-changing instructions are quarantined; generator self-score is nonfactual; evaluation before readback gives no factual utility; duplicate candidate IDs count once; pending recovery precedes generation; independent safe improvement may be selected; exact factual ties keep the incumbent; and prompt rewriting cannot turn a generic protected-only remainder into Chat-executable authority.

Counterfactual `CAND-STRESS-007B` family semantics were not read, and no counterfactual outcome was imputed.

## Exact-scope terminal outcome

`ROOTV5-HISTORY-DISAGREE-STRESS-007A`: **SATISFIED_EXACT_SCOPE**, bound to APE.

Stable terminal transition ID: `ROOTV5-HISTORY-DISAGREE-STRESS-007A:SATISFIED:APE-CHAT-PROGRAM-SEARCH-v1:20260829T1241JST`.

Under frozen `TERMINAL-UTILITY-v2.1`, this maps to utility `2`, subject to immutable round-7 outcome-record creation/readback and external outcome sealing. The policy-disagreement exposure is factual because the selector decision itself is sealed; only the scheduled HISTORY candidate receives an outcome.

## Conflict and continuation

No O/O-derived state, other-worker semantics, downstream state, shared execution ledger, other-role receipt, or legacy/pre-independence research was used. No protected authority or `DESIRED_STATE.json` mutation occurred.

Exact next action: read back this evidence; create/read back the immutable round-7 outcome record; only then update history/sticky state and record the first HISTORY-side policy-disagreement exposure. Do not credit or semantically inspect counterfactual CAND-STRESS-007B.
