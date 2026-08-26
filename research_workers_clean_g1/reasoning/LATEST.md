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
38. `2026-08-26T1359JST-followup7.md`
39. `2026-08-26T1427JST.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Implement/validate a causal decision journal before any randomized policy/OPE collection: committed decision before frontier consume/effect, immutable proposal-batch consumption binding, committed outcome before next randomized decision.
2. Execute the F0–F7 fault-injection matrix and epsilon=0 semantic/resource equivalence tests specified in `2026-08-26T1427JST.md`.
3. Canonicalize journal serialization/hash/idempotency/conflict semantics and define the recovery/event-reader state machine; unmatched committed decisions remain censored, never zero-return by default.
4. Remove mutable per-action attribution of shared provider-batch costs from learning evidence; provider request/usage/charge events remain immutable and joins are append-only.
5. Stage-A v0 representation remains frozen at 154 text-free candidate channels in `STAGE_A_V0_FEATURE_MANIFEST.json`; training normalization remains unfitted and split-safe.
6. Dataset split unit is theorem/task, grouping all runs/decisions/batch siblings from the same theorem.
7. Preserve terminal verified success, local verified progress and multidimensional real cost as separate raw label layers.
8. Prespecify safe-epsilon legal-pool rule, exact propensities, support diagnostics and deterministic fallback before randomized outcomes are observed.
9. Provider deterministic pilot retains prospective 95% task-bootstrap CI half-width target <=5 percentage points for major mean cost shares, subject to collection cap.
10. Pilot decides whether post-generation Stage A has enough cost headroom; if selected-execution share is small, move upstream to Stage B generation/retrieval/model routing.
11. Instrumentation overhead and journal backend/version remain frozen/matched across causal arms; wall-clock is measured as overhead rather than required to be identical in epsilon=0 equivalence.
12. Continue narrow compact fixed/factored controller public-source search only as secondary work.

## Current synthesis and newest updates

- **C171:** current CSSC records choice/action events only in mutable run state and persists them only after result construction; crashes can erase behavior decisions.
- **C172:** safe order is durable decision commit -> immutable batch join -> consume/execute -> durable outcome commit -> next randomized decision.
- **C173:** first journal needs stable decision/run/task ids, frozen ordered choice set/mask, exact behavior propensities, budget/cost-estimator refs, workspace version, immutable batch join, and separate outcome/progress/cost fields.
- **C174:** F0–F7 injection boundaries now have explicit expected censoring/effect semantics.
- **C175:** epsilon=0 equivalence compares semantic outputs and resource/cost observations exactly, while journal wall-clock overhead is measured separately.
- **C176:** shared generated proposal batches require immutable provider events plus append-only consumption joins; current `attribute_proposal_batch` rewrite is not a trustworthy per-action cost label.
- **C177:** provider generation can incur real cost and fail before any execution decision; this is a required negative-control case.

## Exact continuation

1. Define canonical SQLite schema, event serialization/hash, uniqueness/idempotency and transaction constraints for decision/join/outcome.
2. Define recovery reader states for matched transition, censored before known effect, censored after possible effect, and invalid/conflicting history.
3. Implement/execute the journal fault matrix and epsilon=0 equivalence contracts against pinned CSSC fixtures.
4. Prespecify safe-epsilon support/fallback and multiobjective evaluation/Pareto reporting.
5. Only after journal validation, run deterministic provider cost-share pilot under the frozen precision rule.
6. Decide Stage A vs Stage B from observed headroom; randomized collection only if Stage A is justified.
7. Keep public-source search narrow/secondary.
8. Keep frontier nonempty. `2026-08-26T1427JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
