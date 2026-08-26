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
30. `2026-08-26T1259JST.md`
31. `2026-08-26T1359JST.md`
32. `2026-08-26T1359JST-followup.md`
33. `2026-08-26T1359JST-followup2.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Append-durable causal events before any policy learning; interrupted high-cost runs must remain as censored trajectories.
2. Lossless decision candidates use full `ActionFrontierNode.to_dict()` plus decision-local rank, raw budget admission, effective runtime eligibility and experiment eligibility.
3. Preserve separate order-invariant candidate-set and scheduler-order hashes.
4. The legal production mask is **not** raw budget admission when remaining-budget enforcement is disabled; log both layers explicitly.
5. Safe epsilon exploration perturbs only around the exact deterministic production baseline and only when that baseline is in a P0 low-effect pool with at least two actions.
6. Immediate reward is verifier-grounded only; structural edits receive sequential credit rather than hand-written pseudo-reward.
7. Shared proposal-generation events stay immutable/batch-scoped; consumption is a separate zero-cost append-only join.
8. Stable event IDs, idempotent append and unmatched-decision censoring are required before OPE.
9. Reuse the existing atomic JSONL primitive through an optional nonsemantic controller event sink.
10. First learned Stage-A state should be compact/text-free by default: structured frontier/workspace/budget/cost/history signals, not raw proof/error/goal text.
11. OPE readiness is gated by measured support/overlap and ESS; unsupported target-policy mass falls back to deterministic baseline or is outside the identified estimand.
12. Separate execution status from proof outcome so infrastructure failure is not learned as theorem difficulty.
13. Epsilon=0 instrumentation-equivalence tests must prove no change to selected actions, checker/model budgets, final acceptance or cost reconciliation except trace I/O overhead.
14. Measure provider-generation/execution/assembly cost shares with a precision-driven deterministic pilot before assuming Stage-A has economic headroom.
15. Stage B later moves upstream to retrieval/refill/model-tier/generate-vs-skip control only after Stage A is causally measurable.
16. Continue the narrow compact fixed-substrate controller literature gap search with bounded absence language.

## Current synthesis and newest updates

- **C129:** CSSC already has the exact raw-vs-effective budget regression fixture; extend rather than invent a new case.
- **C130:** atomic trace append is tested, but duplicate complete-result append is intentionally allowed; idempotence should apply specifically to stable-id decision events.
- **C131:** the existing real action-runtime ledger test is a strong epsilon=0 instrumentation-equivalence control.
- **C132:** a small Stage-A selector can use existing structured signals (`depth`, attempts, stall, unlock/progress/info signals, budget/cost/action metadata) and initially exclude raw theorem/proof/error/goal text.
- **C133:** log propensities are necessary but not sufficient; require coverage, zero-support mass, weight diagnostics and ESS before causal OPE claims.
- **C134:** `execution_status` and `proof_outcome` are orthogonal; censored crash is absence of outcome, not a fake failure status.
- **C135:** replacing mutable proposal-batch attribution with causal consumption joins restores consistency with the ledger's append-only accounting contract.
- **C121–C128:** raw/effective/experiment eligibility, event sink, idempotence, precision-driven pilot and canonical hashes remain active prerequisites.

## Exact continuation

1. Freeze the exact Stage-A numeric/categorical feature vector and missing-value/status encoding from current `CostEstimate`, frontier signals, workspace and budget schema.
2. Define the instrumentation-equivalence test matrix: budget on/off, structural edit, checked implementation, multi-proposal provider batch, trace-store replace failure, and exception-after-decision.
3. Specify event-reader invariants and censored-trajectory reconstruction.
4. Implement/specify deterministic-baseline + safe-pool epsilon behavior with frozen PRNG seed and verify empirical action frequencies in simulation.
5. Define Stage-A baseline model suite and support/OPE diagnostics under a fixed prover/cost estimator/substrate.
6. Run a precision-driven deterministic provider cost-share pilot before randomized collection.
7. Continue narrow source search for fixed/factored compact heterogeneous proof controllers.
8. Keep the frontier nonempty. `2026-08-26T1359JST-followup2.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
