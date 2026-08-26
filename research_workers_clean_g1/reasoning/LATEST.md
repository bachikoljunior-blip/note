# Reasoning Systems — clean_g1 latest pointer

Latest checkpoints in order:
1. `2026-08-25T1902JST.md`
2. `2026-08-25T1902JST-followup.md`
3. `2026-08-25T1957JST.md`
4. `2026-08-25T2057JST.md`
5. `2026-08-25T2157JST.md`
6. `2026-08-25T2258JST.md`
7. `2026-08-26T0002JST.md`
8. `2026-08-26T0002JST-followup.md`
9. `2026-08-26T0102JST.md`
10. `2026-08-26T0102JST-followup.md`
11. `2026-08-26T0200JST.md`
12. `2026-08-26T0302JST.md`
13. `2026-08-26T0302JST-followup.md`
14. `2026-08-26T0302JST-followup2.md`
15. `2026-08-26T0302JST-followup3.md`
16. `2026-08-26T0302JST-followup4.md`
17. `2026-08-26T0400JST.md`
18. `2026-08-26T0458JST.md`
19. `2026-08-26T0458JST-followup.md`
20. `2026-08-26T0458JST-followup2.md`
21. `2026-08-26T0558JST.md`
22. `2026-08-26T0657JST.md`
23. `2026-08-26T0657JST-followup.md`
24. `2026-08-26T0657JST-followup2.md`
25. `2026-08-26T0802JST.md`
26. `2026-08-26T0903JST.md`
27. `2026-08-26T1000JST.md`
28. `2026-08-26T1101JST.md`
29. `2026-08-26T1157JST.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. **Two-stage controller factorization:** current CSSC `select_admissible_action` runs only after retrieval, model routing, provider spend and proposal generation. Treat post-generation ExecutionSelection and upstream GenerationControl as separate causal policy boundaries.
2. **ExecutionDecisionEvent instrumentation:** log the version-pinned current frontier, budget snapshot, candidate provenance/costs, experiment-safe legal mask, deterministic baseline, full behavior distribution, chosen propensity and pre-execution ledger boundary immediately before `frontier.consume`; log outcomes separately.
3. **Minimal current-frontier legal mask:** because proposal validation and stale/version/readiness pruning already occur before selection, Stage-A legality can be `current frontier × budget admission × experiment effect gate`. Preserve absent-vs-illegal semantics; broader action-generation ablations still need `allowed_action_kinds` or equivalent.
4. **Safe Stage-A randomized subset:** start with already-generated structural workspace actions (`DECOMPOSE`, `PROPOSE_ARGUMENT`, `REFINE_ARGUMENT`, `CHANGE_REPRESENTATION`). Keep checker/file-backed execution gated until replay/idempotency/lifecycle semantics are frozen.
5. **Batch-cost accounting:** proposal generation is batch-scoped and sunk before ExecutionSelection. Preserve `proposal_batch_id`; do not treat late `action_id` attribution as unique causal action cost. Keep run total, generation/batch cost and selected execution cost separate.
6. **Headroom diagnostic before policy training:** quantify what fraction of total real cost occurs before selection. If proposal generation dominates, Stage A is mainly a scheduling/quality experiment; large cost savings require Stage-B GenerationControl.
7. **GenerationDecisionEvent:** later expose branch/cache refill, retrieval, cheap/strong model route, generate/skip/refill and escalation decisions with legal masks, effect semantics, exact propensities and provider-batch receipts.
8. **Learn value while freezing cost:** keep CSSC's frozen/fingerprinted execution cost estimator fixed initially; learn only verified-success/progress value/advantage, but evaluate primary utility at run-level total cost so sunk generation spend is not omitted.
9. **Compact-controller gap, not broad RL gap:** full formal-proof agents already learn tool behavior under RL and the June-2026 Lean cost-quality router learns a small continue/restart decision. Continue searching only for a separate compact heterogeneous controller over fixed/factored low-level execution.
10. **Matched external evaluation:** freeze benchmark split, Lean/Mathlib, low-level proposal model/prompts, retrieval, action semantics, checker/SafeVerify, cost estimator and actual budget. Compare deterministic baseline, BC, terminal-AW, sequential value/advantage, contextual bandit and conservative cost-aware policies only at the intended policy boundary.
11. **OPE-identifiable collection:** log exact behavior propensities over the legal set. Never reconstruct hidden planner probabilities or pool adaptive rescue regimes as stationary behavior.
12. **Conservative deployment under shift:** learned control falls back to deterministic baseline in weak-support/uncertain regions; test theorem-family, repository, Lean/Mathlib and low-level-prover shifts.
13. **Leanstral substrate provenance:** current official open weights + function calling + LeanstralSafeVerify + FLTEval are strong fixed-substrate components, but no official OPE-ready training trajectory logger with masks/propensities was found in the current bounded pass.
14. **Reproducibility:** keep public source commit/blob identities and exact semantic-control tuple in every checkpoint/receipt; never broaden absence-of-evidence claims into global nonexistence.

## Current synthesis and newest updates

- **C99 — selector boundary correction:** current CSSC post-generation selector cannot learn retrieval/model escalation/proposal generation because those happen in `_fill_action_cache` before `select_admissible_action`. The experiment should be explicitly split into ExecutionSelection and GenerationControl.
- **C100 — mask simplification:** for the existing selector boundary, cached frontier nodes have already passed proposal validation and exact workspace/branch/obligation/readiness checks. Stage-A mask can be defined over current frontier membership plus budget/effect gates. A separate upstream action-kind mask is still needed for richer action-space generation ablations.
- **C101 — minimal decision event:** current runtime already exposes nearly all fields needed for a causal scheduler dataset. Insert the decision record after the frozen selection inputs exist and before `frontier.consume`; keep the post-execution outcome in a separate event to avoid leakage.
- **C102 — execution effect split:** structural actions are deterministic local workspace transforms after proposal generation; capability testing invokes Lean; implement/repair materialize/check candidates and should remain effect-gated initially. Proposal-generation provider effects are upstream for every action kind.
- **C103 — shared proposal-batch cost:** provider request/usage/charge events are recorded at proposal-batch scope before selection and later assigned an `action_id` when a node consumes that batch. Multiple proposals may share a batch, so policy learning must keep batch cost separate from selected execution cost and evaluate run-level total cost.
- **C104 — mask roadmap still open:** current public CSSC roadmap still lists explicit `allowed_action_kinds` or equivalent as unfinished.
- **C105 — Leanstral reproducible substrate, not OPE data:** Mistral now publicly provides Leanstral 1.5 open weights/function calling, SafeVerify and FLTEval; its release describes CISPO RL environments, but the bounded official-source pass did not expose authoritative per-decision training trajectories with legal masks/propensities.
- **C106 — factorization gap remains bounded-open:** the closest current Lean control-plane paper learns a much smaller continue/restart routing decision. No new exact compact heterogeneous fixed-substrate controller match was found in this pass.
- **C93–C98 remain prerequisites:** CSSC is a mature typed/cost-instrumented heuristic substrate with a precise mask/logging gap, and its cost estimator/value policy asymmetry enables clean policy-replacement ablations.
- **C84/C85 remain important controls:** high supervised strategy-classification accuracy can fail to maximize end-to-end proof success; train on verifier-grounded utility per real cost rather than action imitation accuracy.
- **C86/C89 remain broad positive controls:** full-agent RL can learn selective tool use, but it does not isolate the compact-controller causal contribution.

## Exact continuation

1. Inspect trace-store/serialization code to test whether `proposal_cache_events`, workspace snapshots and cost ledger preserve event ordering sufficiently to reconstruct `ExecutionDecisionEvent`; identify missing fields exactly.
2. Inspect tests/traces for multiple nodes sharing one `proposal_batch_id` and repeated consumption. Verify whether late `action_id` attribution is overwritten; define a batch-cost invariant/regression test either way.
3. Find any public CSSC pilot traces with provider cost and partition total cost into pre-selection generation, selected execution/checking and terminal assembly. Use this as the headroom estimate before training a selector.
4. Define Stage-A mask precisely over valid current frontier nodes. Randomize only when at least two P0 legal alternatives exist; otherwise deterministic fallback.
5. Specify an epsilon-mixture or other propensity-known behavior policy under variable legal-set size, with exact closed-form `mu(a|s)` and deterministic baseline probability.
6. Define terminal/reusable-verified-progress reward labels while keeping shared proposal-batch cost outside per-action execution labels. Keep primary evaluation at run-level total cost.
7. Specify Stage-B GenerationDecisionEvent and safe action ontology for retrieve/skip/refill/model-tier/escalate choices before any provider request is issued.
8. Continue targeted source-level search for a separate compact heterogeneous controller trained by RL/bandit/value/offline RL with low-level proof/tool execution fixed or clearly factored.
9. Recheck official Leanstral/Mistral releases for public CISPO environment/trainer/trajectory logging; do not infer one from evaluation infrastructure.
10. Keep the frontier nonempty. `2026-08-26T1157JST.md` is the newest checkpoint and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
