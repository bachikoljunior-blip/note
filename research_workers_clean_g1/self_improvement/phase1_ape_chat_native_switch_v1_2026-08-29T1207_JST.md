# Self-improvement Phase-1 — APE Chat-native generate/score/select switching audit

- role: `self_improvement`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- selected leaf: `ROOTV5-PUBLIC-OPTIMIZER-APE`
- mechanism: `APE-CHAT-POOL-v1`
- semantic work observed at: `2026-08-29T12:06:44.434787+09:00`
- frozen bootstrap main SHA: `8ad91c7c03ab86e116b3248d65c586618eaf212f`
- frozen root/config: control `25`, config control `14` / config `7`

## 1. Public mechanism audit

Primary source: Zhou et al., *Large Language Models Are Human-Level Prompt Engineers*, arXiv:2211.01910, https://arxiv.org/abs/2211.01910 ; ICLR 2023 poster: https://iclr.cc/virtual/2023/poster/10850 . Public implementation: https://github.com/keirp/automatic_prompt_engineer .

APE treats an instruction as a program, generates a pool of instruction candidates with an LLM, scores candidates according to task performance and selects the best-scoring instruction. The paper evaluates selected instructions through downstream zero-shot model performance. This Phase-1 audit transfers only the generate → evidence-score → select structure; it does not reproduce the 24-task benchmark.

## 2. Safe recurring-Chat reduction

`APE-CHAT-POOL-v1` uses a bounded pool of role-local assignment-policy candidates with stable identities. Proposal generation may change only role-local plan text; frozen control, semantic-input, safety/protected-authority, stable transition identity and credit rules cannot be generated away.

Generated self-scores, evaluator prose and wording diversity are not objective values. A candidate receives selection value only from independent terminal mechanical evidence after durable readback. Duplicate candidate/transition identities are counted once, exact ties keep the incumbent, and durable `pending_switch` recovery overrides pool reselection.

## 3. Conformance evidence

Machine-readable evidence was written and read back at `research_workers_clean_g1/self_improvement/phase1_ape_chat_native_ablation_v1_2026-08-29T1206_JST.json`, blob `15893a566ce53365e73e9026421b570f7df89f6f`.

The unchanged sequence-117 OPRO guard traces pass **8/8** under `APE-CHAT-POOL-v1`; frozen OPRO remains **8/8**. Seven APE-specific counterexamples also pass **7/7**: proposal self-score rejection, unevidenced ranking rejection, no diversity bonus, proposal dedup, unsafe high-score quarantine, no same-proposer success certification, and safe independently evidenced improvement.

This establishes constructed controller conformance only, not real-task superiority.

## 4. Exact-scope outcome

Predeclared `ROOTV5-PUBLIC-OPTIMIZER-APE`: **SATISFIED_EXACT_SCOPE**.

Stable terminal transition ID: `ROOTV5-PUBLIC-OPTIMIZER-APE:SATISFIED:APE-CHAT-POOL-v1:20260829T1207JST`.

This is the fourth natural terminal transition collected after sequence-117 preregistration of `ROOTV5-OPRO-HISTORY-REAL-OUTCOME-CALIBRATION`. The minimum sample count is therefore reached, but **no calibration result is computed here**. Before any selector comparison, the original preregistration must be checked for an exact frozen selector/value tuple and enough counterfactual decision information. Missing semantics must not be invented after observing these four outcomes.

All safely Chat-capable work for the APE leaf is complete; `generic_residual_capability_boundary = null`.

## 5. Conflict and continuation

No O/O-derived state, other-worker semantics, downstream state, shared execution ledger, other-role receipts or legacy research was used. No protected authority or `DESIRED_STATE.json` mutation occurred.

Exact next action: after this APE evidence is read back, audit the already-existing sequence-117 calibration preregistration for replay completeness. If the exact selector/value tuple or counterfactual logging contract is absent, close that frontier as a protocol blocker rather than computing a post-hoc result, and preregister a repaired future calibration before collecting any new calibration outcomes.
