# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T170124JST_CAUSAL_ROUTING_CRN.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1600JST_TARGET_SEMANTICS.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `10`
- role config revision: `5`
- frozen source main SHA: `456111f88cd26b8ad796866aaf64a6c44a176908`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- pre-semantic second SHA-only lookup matched the frozen SHA; later repository writes did not alter the semantic control tuple for this invocation.

Current synthesis delta:
- Executed-replay evidence now strongly rejects model confidence, fluency and generic judge/correctness scores as default rollback-target proxies without causal calibration: policy confidence routed roughly the same fraction of turns as pivotal-turn recall and was chance-level for pivotal targeting in the measured ALFWorld setting.
- AgentLocate sharpens target semantics: its decisive failure step is the earliest step where one corrected action reverses failure, which is a first-sufficient-intervention target rather than necessarily the earliest causal origin. Exact-step localization remains difficult, refinement is non-monotonic, and downstream visibility can bias blame.
- BranchPoint-Latent is best treated as a candidate/probe-budget allocator: it improves held-out Branch Recall@5 from 0.73 to 0.93 at zero replay-oracle cost, but does not establish the best historical restore target or final recovery utility.
- Equal nominal rollback budgets are not enough. Selector comparisons must report realized recovery dose/opportunity because target location can change how many admissible actions/model calls/tool calls are actually usable before termination.
- Common-random-number pairing needs causal alignment. A shared numeric seed with a stateful PRNG becomes invalid when branch control flow consumes a different draw sequence. Where possible, environment randomness should be event-keyed/counter-based; model-sampling divergence still needs same-model control branches and explicit residual replay-noise estimates.
- The strict selector-only scientific gap remains open: no located software/tool/GUI study fixes target objective, alarm, candidate set, restore/carry-forward, model/verifier, probe budget, allocated and realized recovery opportunity, and replay-noise treatment while varying only historical target selector and measuring final live task success.

Exact continuation:
1. Search selector studies reporting realized post-rollback model/tool/action counts, not only nominal limits, and test whether rollback depth changes effective opportunity.
2. Search state-only failure localizers that output calibrated top-k distributions, conformal sets or abstention, then audit them against executed replay rather than annotated correctness.
3. Search software/tool-agent systems using event-keyed or counter-based RNG for counterfactual branch coupling; distinguish environment coupling from LLM-sampler coupling.
4. Search local/open-model inference stacks for a practical token/event-keyed sampler or reproducible sampler-state checkpoint that can couple divergent branches after a historical target.
5. Extend the strict Replay Gap/Shepherd selector-harness blueprint with `realized_model_calls`, `realized_admissible_actions`, `realized_environment_steps`, `successful_tool_calls`, `unused_budget_reason`, `environment_CRN_method`, `model_CRN_method`, `event_identity_map`, and same-model control-branch variance.
6. Treat AgentLocate/BranchPoint-like methods as candidate/probe allocators unless held-out live rollback outcomes establish historical-target utility.
7. Preserve the target-semantics split: earliest causal origin, first sufficient intervention point, latest rescue/point-of-commitment, latest admissible/safe checkpoint, and intended semantic version are distinct labels.
8. Preserve the strict selector-only gap unless all non-target variables are genuinely controlled.
9. Maintain a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
