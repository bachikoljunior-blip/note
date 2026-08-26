# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T180347JST_SHIFT_ROBUST_CONFORMAL.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T180021JST_CONFORMAL_SET_VLLM_CRN.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `10`
- role config revision: `5`
- frozen source main SHA: `cc9cb9fae8c79c150521a860142ab7d7b0e27e85`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- the pre-semantic second SHA-only lookup matched the frozen SHA; later repository writes did not alter the semantic control tuple for this invocation.

Current synthesis delta:
- Conformal rollback-localization should be treated as a calibrated candidate region / uncertainty layer, not final recovery utility. In Conformal Agent Error Attribution's Right Dense rollback table, VCP has coverage `1.00` but success `0.70` and redo cost `0.66`, while LF has lower coverage `0.82` but higher success `0.75` and lower cost `0.40`.
- That rollback experiment still bundles target selection with failed-trace corrective guidance, so the strict selector-only gap remains open.
- Conformal validity itself is fragile under distribution shift. A security-agent trajectory-certification study reports single-step miscoverage reaching 100% under cross-dataset deployment while raw accuracy remains 78%; this transfers only as a validity warning, not as direct rollback evidence.
- Online weighted conformal adaptation can itself collapse when density-ratio estimation degenerates in high-dimensional embeddings. Shift detection therefore needs adaptation-health diagnostics such as effective sample size/weight degeneracy and an explicit unknown/abstain state.
- For adaptive/non-exchangeable streams, recent anytime selective-risk work suggests that a sequential validity contract is conceptually preferable to silently reusing an exchangeable calibration guarantee, though this is not yet a rollback-localization method.
- Current vLLM main provides seed+absolute-position+token-id keyed Gumbel sampling as a practical partial model-side CRN primitive, plus trace replay for exact forced-prefix/logprob auditing. Position shifts can break CRN alignment and trace replay does not yet by itself provide a verified live-branch handoff.

Exact continuation:
1. Search for rollback/error-localization methods with sequential/e-process/conformal validity directly on adaptive agent traces.
2. Search whether causal/executed-replay localizers report calibration under distribution shift rather than only annotated-step accuracy.
3. Design an executed-replay audit of conformal candidate regions stratified by trace regime and semantic event class, measuring coverage, set width, abstention, live recovery success and redo cost separately.
4. Quantify vLLM same-position Gumbel CRN fidelity across divergent contexts and shifted prefix lengths, and find a verified trace-replay -> live-sampling handoff.
5. Continue searching rollback work that reports realized post-rollback model calls, admissible actions, environment steps and successful tool calls rather than only nominal budgets.
6. Extend the strict selector harness with `conformal_candidate_region`, `coverage_assumption_status`, `shift_state`, `adaptation_health`, `model_crn_alignment_span`, `trace_replay_verified_prefix`, and `live_handoff_equivalence`.
7. Preserve target semantics: decisive-error label, earliest causal origin, first sufficient intervention, latest rescue/point-of-commitment, latest safe checkpoint and intended semantic version remain distinct.
8. Preserve the strict selector-only gap unless all non-target variables are controlled.
9. Maintain a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
