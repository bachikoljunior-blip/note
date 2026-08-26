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

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Causal decision logging remains prerequisite to any Stage-A learning/OPE; unmatched decisions are censored, not fake failures.
2. Lossless full candidate events keep separate raw budget admission, effective production eligibility, and experiment eligibility.
3. Exact production selector defines deterministic baseline; safe epsilon only perturbs when baseline is inside a low-effect pool with `L>=2`.
4. Immediate reward remains verifier-grounded; structural edits get downstream sequential credit only.
5. Shared provider-generation events remain immutable and batch-scoped; consumption is a zero-cost causal join, not ledger mutation.
6. Event IDs are stable/idempotent and use existing UUID4 `sample_id` as run id.
7. **Do not naïvely use current whole-file `_atomic_append_text` per decision:** it rewrites the entire trace each append, causing roughly `(M+1)/2` final-file-size write amplification for `M` equal-sized events and contaminating cost/wall-clock experiments.
8. Introduce a `DecisionEventJournal` (segmented immutable JSON or SQLite) with O(1)-ish per-event durable writes; compact to existing JSONL afterward.
9. Randomized collection fails closed if the pre-action decision or batch-consumption event cannot be durably written; outcome-write failure stops further randomized decisions.
10. Stage-A v0 should be a small text-free shared candidate scorer over existing frontier/workspace/budget/cost signals, with explicit missing masks/status categories.
11. Keep task/node/obligation/batch ids and raw proof/error/goal text in provenance but outside v0 predictive features to reduce memorization/confounding.
12. OPE is reported only with measured support/overlap/ESS; zero-support target mass must fallback/restrict rather than be silently extrapolated.
13. Separate execution status from proof outcome; infrastructure errors are not theorem failures.
14. Instrumentation itself gets matched-overhead evaluation and is identical in baseline/treatment arms.
15. Provider-generation/execution/assembly cost shares must be measured with a precision-driven deterministic pilot before assuming Stage-A economic headroom.
16. Stage B later moves upstream to retrieval/refill/model-tier/generate-vs-skip control only if warranted by the pilot.
17. Continue narrow compact fixed/factored controller literature search with bounded absence language.

## Current synthesis and newest updates

- **C136:** current atomic JSONL append is whole-file copy+replace; per-decision use is quadratically write-amplifying and can distort wall-clock.
- **C137:** prefer a separate durable decision journal (segmented JSON or SQLite) and compact later; event id is the idempotence key.
- **C138:** during randomized collection, failed pre-action persistence means no action execution; failed outcome persistence stops further randomized decisions and leaves a censored decision.
- **C139:** existing UUID4 `state.sample_id` is the correct run identity; do not invent another run UUID.
- **C140:** v0 feature schema is fixed around unified budget, workspace counts, branch depth/attempt/stall/unlock/progress/info, action/source/tier/rank, cost-estimate and eligibility fields.
- **C141:** every optional numeric cost has value+known mask; unknown/unavailable must never collapse to numerical zero.
- **C142:** use one small shared per-candidate scorer with legal-set mask; BC/weighted/value/bandit objectives share the representation.
- **C143:** log exact probability vector plus realized random draw/sampler version for replay; seed is provenance, not a predictive feature.
- **C144:** measure trace bytes/fsync/wall-time overhead and keep identical instrumentation in baseline/treatment arms.
- **C129–C135:** existing CSSC tests provide strong insertion points for budget semantics, trace durability and real action-runtime equivalence; OPE support and execution/proof outcome separation remain active.

## Exact continuation

1. Benchmark segmented-JSON versus SQLite journaling on synthetic 10/100/1000-event traces for bytes written, fsyncs, append latency and crash/idempotence behavior; choose the lower-distortion durable substrate.
2. Write an exact versioned v0 feature manifest/category vocabulary and split-safe normalization rule.
3. Specify deterministic epsilon sampler/replay tests and journal failure-injection tests.
4. Complete epsilon=0 instrumentation-equivalence matrix using existing CSSC fixtures.
5. Define event-reader invariants and censored-trajectory reconstruction.
6. Run precision-driven provider cost-share pilot; if post-generation execution is a small share, prioritize Stage-B generation control rather than forcing Stage-A learning.
7. Continue narrow source search for fixed/factored compact heterogeneous proof controllers.
8. Keep the frontier nonempty. `2026-08-26T1359JST-followup3.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
