# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T180021JST_CONFORMAL_SET_VLLM_CRN.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T170124JST_CAUSAL_ROUTING_CRN.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `10`
- role config revision: `5`
- frozen source main SHA: `cc9cb9fae8c79c150521a860142ab7d7b0e27e85`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- pre-semantic second SHA-only lookup matched the frozen SHA; later repository writes did not alter the semantic control tuple for this invocation.

Current synthesis delta:
- Conformal Agent Error Attribution supplies a calibrated contiguous *candidate region* for one decisive-error label, not a guarantee of final recovery. Its own rollback table separates coverage from utility: on Right Dense, VCP had coverage `1.00` but success `0.70` and redo cost `0.66`, while LF had coverage `0.82`, success `0.75`, cost `0.40`.
- Its rollback success is not selector-only evidence because restart also receives failed-trace corrective context. Therefore target, redo depth and carry-forward guidance are bundled.
- A useful controller split is now: calibrated uncertainty region -> admissibility/safe-boundary filter -> historical target selector -> abstention/probe when evidence is insufficient -> live outcome/cost/disruption evaluation.
- Current vLLM main provides a practical partial model-side CRN primitive: Gumbel noise is keyed by request seed, absolute token position and token id. This can couple divergent logits at the same decode position, but it is position-keyed rather than semantic-event-keyed, so prefix-length/position shifts can break causal alignment.
- vLLM trace replay (documented Aug. 20, 2026) can force a recorded decoded prefix while computing real logprobs/ranks. It is useful for prefix reconstruction audits, but the documented request stops after the trace and does not itself provide a same-request trace-replay-to-live-branch handoff.
- The strict selector-only gap remains open.

Exact continuation:
1. Audit conformal localization against executed-replay causal targets rather than injected/annotated decisive-error labels.
2. Search conformal/selective localization robust to distribution shift or non-exchangeable sequential agent traces.
3. Quantify vLLM seed+position+token-id Gumbel CRN fidelity across divergent contexts and shifted prefix lengths; distinguish aligned token positions from semantic event identities.
4. Search for or prototype a verified trace-replay -> live-sampling handoff with equivalent prefix/KV state.
5. Continue searching rollback work reporting realized post-rollback model calls, admissible actions, environment steps and successful tool calls, not only nominal budgets.
6. Add `conformal_candidate_region`, `coverage_assumption_status`, `model_crn_alignment_span`, `trace_replay_verified_prefix`, and `live_handoff_equivalence` to the strict selector harness.
7. Keep decisive-error label, earliest causal origin, first sufficient intervention, latest rescue/point-of-commitment, latest safe checkpoint and intended semantic version separate.
8. Preserve the strict selector-only gap unless all non-target variables are controlled.
9. Maintain a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
