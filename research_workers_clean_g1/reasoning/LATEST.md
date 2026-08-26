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

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Freeze the causal decision journal before collection. Current whole-file JSONL replacement is fine for low-frequency final summaries but unsuitable per decision because it rewrites the whole trace.
2. SQLite WAL/FULL is the current leading Stage-A journal candidate; segmented immutable JSON remains an independent audit/reference implementation.
3. Journal causal ordering: commit decision before action; commit any shared-batch consumption binding before execution; commit outcome before the next randomized decision. Persistence failure is fail-closed for future randomization.
4. Event identity uses existing UUID4 run/sample id plus decision index/type; exact replay is idempotent, conflicting duplicate is an error.
5. One decision and at most one outcome per `(run_id,decision_index)`; zero-or-more batch-consumption joins; unmatched decision is censored, never negative reward.
6. Lossless raw events retain full candidates/workspace/budget/provenance; learned datasets are derived later and versioned separately.
7. Stage-A v0 is a small text-free shared per-candidate scorer over structured budget/workspace/branch/action/cost signals with explicit missing/status masks.
8. Freeze `feature_manifest_sha256`, fixed categorical vocabularies and train-split-only normalization; raw journal remains re-featurizable.
9. Safe epsilon policy uses exact deterministic production baseline, stable node ordering, exact probability vector and realized random draw. Unsupported states/actions fall back to baseline.
10. OPE claims require measured overlap/support/ESS; target mass with zero support is outside identification unless policy is restricted/fallback is built into the estimand.
11. Separate execution infrastructure status from proof outcome and verifier-grounded progress.
12. Instrumentation overhead is itself measured and matched across causal arms; journal backend/version becomes part of the frozen substrate.
13. Complete fault-injection and epsilon=0 instrumentation-equivalence tests before provider collection.
14. Run a precision-driven deterministic provider cost-share pilot before training. If post-generation execution is a small share of total cost, move earlier to Stage-B generation/retrieval/model-tier control.
15. Broad proof RL is already established; continue literature search only for the narrow fixed/factored compact heterogeneous-controller + exact propensity/OPE gap.

## Current synthesis and newest updates

- **C145:** local synthetic 1000-event benchmark confirmed whole-file per-decision copy+replace is high-overhead: ~7.52s median and ~1.097GB counted writes for a ~2.19MB logical stream.
- **C146:** on the same local benchmark SQLite WAL/FULL was ~0.67s median for 1000 events; segmented JSON ~2.04s. SQLite is the leading prototype, not yet a production portability claim.
- **C147:** journal latency must be compared to structural/Lean action latency; durable logging can itself bias the cost objective.
- **C148:** keep causal journal separate from immutable monetary/resource CostLedger, joining later by stable ids.
- **C149:** journal backend/pragmas/schema/canonicalization/export policy are part of the experimental substrate and must be frozen before randomized data collection.
- **C150:** SQL schema should enforce one decision/at-most-one outcome per decision index while allowing multiple batch-consumption joins.
- **C151:** idempotence requires canonical-payload comparison, not `INSERT OR IGNORE`.
- **C152:** do not transactionally combine pre-action decision with post-action outcome; preserving committed decision without outcome is the censoring evidence.
- **C153:** canonical JSONL is a derived export; online journal stays authoritative until export verification.
- **C154:** epsilon=0.25 synthetic sampler frequencies matched expected mixture probabilities closely across pool sizes 2/3/5.
- **C155:** stable randomized-pool ordering is required so a logged draw maps deterministically to the same node.
- **C156:** feature semantics need their own manifest hash distinct from raw event schema.
- **C157:** normalization/vocabularies are fitted/frozen on training split only; missingness semantics are preserved.
- **C158:** raw causal evidence and learned-policy dataset are deliberately decoupled, enabling re-featurization and support/OPE reanalysis without recollection.

## Exact continuation

1. Write the complete versioned `stage_a_v0` feature manifest: exact order, transformations, vocabularies, missing/status encodings and excluded provenance fields.
2. Specify SQLite fault-injection tests for decision/batch/outcome commit failures, process-kill recovery and conflicting duplicate replay.
3. Define the instrumentation-equivalence test matrix with exact equality assertions and wall-clock overhead reporting.
4. Define event-reader/dataset-builder invariants and censored-decision/sequential-return handling.
5. Define initial model/objective suite and split by theorem/task rather than decision to prevent trajectory leakage.
6. Then run the precision-driven provider cost-share pilot with frozen journal/feature/substrate versions.
7. Continue narrow source search only as secondary work; experimental identifiability is now higher value.
8. Keep the frontier nonempty. `2026-08-26T1359JST-followup5.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
