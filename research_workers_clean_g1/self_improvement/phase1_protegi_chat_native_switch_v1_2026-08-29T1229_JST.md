# Self-improvement Phase-1 — ProTeGi Chat-native critique/beam audit

- role: `self_improvement`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- selected frontier: `ROOTV5-PUBLIC-OPTIMIZER-FRESH-004`
- candidate: `CAND-FRESH-004` / `critique_search`
- sealed selector round: `HIST-STICKY-ONLINE-v2.1` round 4, decision blob `6fa672ff373099b27ee5c8baf52ba54d7857b371`
- bound public family: `ProTeGi`
- mechanism: `PROTEGI-CHAT-GRADIENT-BEAM-v1`
- semantic observation: `2026-08-29T12:29:01+09:00`

## Public mechanism audit

Primary source: Pryzant et al., *Automatic Prompt Optimization with “Gradient Descent” and Beam Search*, EMNLP 2023, ACL Anthology: https://aclanthology.org/2023.emnlp-main.494/ . Public implementation inspected via Microsoft LMOps: https://github.com/microsoft/LMOps/blob/main/prompt_optimization/optimizers.py .

ProTeGi uses minibatch errors to produce natural-language textual gradients that criticize a prompt, edits the prompt in the opposite semantic direction, expands prompt candidates in a beam, and treats beam candidate selection as a best-arm identification problem. The published method assumes training data and an LLM API. This leaf does not reproduce the paper's benchmarks or literal API runtime.

## Safe recurring-Chat reduction

`PROTEGI-CHAT-GRADIENT-BEAM-v1` maps a minibatch error signal to a durable role-local bundle of independently observed assignment failures/no-progress facts. A textual gradient is advisory critique only: it can propose a bounded role-local assignment-policy edit, but cannot alter root/config/control binding, CLEAN semantic-input boundaries, safety/protected-authority boundaries, stable frontier/candidate/transition IDs, the sealed selector decision, or readback-before-credit.

Beam expansion is restricted to stable safe candidates inside the already selected leaf. Generated critiques, imagined gains and same-transition self-scores are `NONFACTUAL`; best-arm selection may use only independently sealed factual terminal outcomes. A pending switch or externally sealed factual selector decision always precedes new gradient generation or reselection.

## Conformance evidence

Machine-readable evidence was created and read back at `research_workers_clean_g1/self_improvement/phase1_protegi_chat_native_ablation_v1_2026-08-29T1229_JST.json`, blob `5cee14d15464e6c40cbf130f716317b8788eff12`.

The unchanged frozen guard set passes **8/8** with no retuning. Ten critique/beam-specific counterexamples pass **10/10**: unsupported critique is rejected; control-rewriting and CLEAN-boundary-crossing edits are quarantined; same-transition self-score is nonfactual; unevaluated claimed gain cannot displace the incumbent; duplicate factual transitions count once; pending recovery precedes gradient search; independently evidenced strict improvement may replace the incumbent; exact factual ties keep the incumbent; and critique cannot convert a generic protected-authority-only remainder into a Chat-executable effect.

This establishes exact-scope recurring-Chat controller conformance only, not ProTeGi task-quality superiority.

## Exact-scope terminal outcome

`ROOTV5-PUBLIC-OPTIMIZER-FRESH-004`: **SATISFIED_EXACT_SCOPE**, bound to ProTeGi.

Stable terminal transition ID: `ROOTV5-PUBLIC-OPTIMIZER-FRESH-004:SATISFIED:PROTEGI-CHAT-GRADIENT-BEAM-v1:20260829T1229JST`.

Under frozen `TERMINAL-UTILITY-v2.1`, this status maps to utility `2`, subject to immutable round-4 outcome-record creation/readback and external outcome sealing. No archive/sticky update or frontier credit occurs in this artifact itself.

## Conflict and continuation

No O/O-derived state, other-worker semantics, downstream state, shared execution ledger, other-role receipt, or legacy/pre-independence research was used. No protected authority or `DESIRED_STATE.json` mutation occurred.

Exact next action: read back this terminal evidence; create/read back the immutable round-4 outcome record; only then update the v2.1 history archive/sticky state, award exactly one frontier-bound credit, and preserve the still-open predeclared `CAND-FRESH-005` population-search and `CAND-FRESH-006` meta-feedback leaves for future rounds.
