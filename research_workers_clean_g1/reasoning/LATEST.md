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
34. `2026-08-26T1359JST-followup3.md`
35. `2026-08-26T1359JST-followup4.md`
36. `2026-08-26T1359JST-followup5.md`
37. `2026-08-26T1359JST-followup6.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Validate the causal journal before any policy/OPE collection. SQLite WAL/FULL is the leading prototype; whole-file per-decision replacement is rejected as too write-amplifying for the default.
2. Journal ordering is causal: committed decision before action, batch provenance binding before executing a shared generated proposal, outcome before next randomized decision. Persistence failure is fail-closed for subsequent randomization.
3. Raw journal is lossless and independent of learned features. Unmatched decisions are censored, not negative labels; monetary/resource CostLedger remains separate and immutable.
4. Stage-A v0 feature semantics are now frozen in `STAGE_A_V0_FEATURE_MANIFEST.json`, blob `e14b0f51605f47f63a724db4a417e92f183aecbe`, semantic-body SHA-256 `c1f8cacb3b8eedc8ed665869a378e9e71a7a36653fd3efa717c36cc940a81838`.
5. Expanded v0 representation has 154 channels/candidate before optional train-split-only standardization; raw proof/theorem/error/goal text and task/node IDs are excluded from v0 predictive inputs but retained as provenance where appropriate.
6. Action space is the seven current structured proposal kinds plus OTHER; future additional meta-actions require an explicit new version.
7. Safe epsilon collection still uses exact deterministic production baseline, stable node ordering, exact probability vector/realized draw and known propensities; unsupported states/actions fallback to baseline.
8. OPE readiness requires measured support/overlap/ESS; no causal score for material zero-support target mass.
9. Instrumentation itself must be identical across causal arms and measured for journal latency/bytes/fsync/wall-clock overhead.
10. Complete fault injection and epsilon=0 behavioral-equivalence tests before provider collection.
11. Provider-enabled pilot uses a prespecified precision stopping rule for proposal-generation/selected-execution/assembly/other cost shares. Do not assume Stage-A headroom before observing it.
12. If selected execution cost share is small, move earlier to Stage-B generation/retrieval/model-tier control; if material, collect safe epsilon Stage-A data.
13. Continue narrow fixed/factored compact heterogeneous-controller literature search only as secondary work; broad proof RL is already established.

## Current synthesis and newest updates

- **C145–C149:** local synthetic storage benchmark strongly favors a dedicated journal over whole-file replacement; backend/version is part of the frozen experimental substrate.
- **C150–C158:** concrete SQLite event schema/transaction/idempotence/export contract, replayable epsilon sampler and feature/dataset versioning are defined.
- **C159:** frozen v0 expands to 154 candidate channels before fitted normalization.
- **C160:** feature schema was frozen before provider outcomes/policy labels, reducing adaptive test-set feature selection risk.
- **C161:** distinguish raw event compatibility from predictive feature/substrate compatibility before pooling traces.
- **C162:** v0 action vocabulary deliberately matches the seven supported structured proposal kinds, not the broader workspace enum.
- **C163:** raw v0 manifest is parent to later train-split-fitted preprocessing/model artifacts; objectives should share the same representation for clean comparison.

## Exact continuation

1. Define executable SQLite fault-injection/recovery tests and event-reader invariants.
2. Define the full instrumentation-equivalence matrix and exact equality/tolerance assertions on existing CSSC fixtures.
3. Define theorem/task-level data split, censored-decision treatment and sequential return labels for BC/weighted/value/bandit comparisons.
4. Prespecify provider pilot precision target/stopping rule and bootstrap unit.
5. Run deterministic provider-enabled cost-share pilot only after journal/equivalence validation.
6. Decide Stage A versus Stage B based on observed cost/solve headroom, then collect randomized data only if justified.
7. Continue narrow literature search as secondary work.
8. Keep the frontier nonempty. `2026-08-26T1359JST-followup6.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
