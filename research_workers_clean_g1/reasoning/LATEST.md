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

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Validate SQLite journal under injected failures and prove epsilon=0 instrumentation equivalence before any policy/OPE collection.
2. Journal semantics remain: committed decision before action, batch provenance binding before executing shared generated proposal, outcome before next randomized decision; unmatched decision is censored.
3. Local abrupt-process smoke test observed committed SQLite WAL/FULL event survives `os._exit`, uncommitted event does not, and integrity check remained OK; this is local evidence only, not universal power-loss proof.
4. Stage-A v0 representation is frozen at 154 text-free candidate channels in `STAGE_A_V0_FEATURE_MANIFEST.json`; training normalization remains unfitted and split-safe.
5. Dataset split unit is theorem/task, grouping all runs/decisions/batch siblings from the same theorem to prevent trajectory leakage.
6. Preserve terminal verified success, local verified progress and real multidimensional cost as separate label layers; do not bake one arbitrary scalar reward into raw evidence.
7. Censored decisions can still support BC/behavior diagnostics where appropriate but are not zero-return examples for reward/value learning.
8. Initial fixed-representation model suite: deterministic heuristic, BC, verified-outcome/advantage-weighted classifier, compact Q/value scorer, and conservative bandit/OPE-selected policy with fallback outside support.
9. Safe epsilon policy still requires exact propensities and support diagnostics; pool ordering is stable/replayable.
10. Provider deterministic pilot has a prospective 95% task-bootstrap CI half-width target of <=5 percentage points for major mean cost shares, subject to a collection cap; if unmet report insufficient precision.
11. Pilot decides Stage-A headroom before randomized provider collection. If selected execution share is small, move upstream to Stage B.
12. Instrumentation overhead and journal backend/version are frozen/matched across causal arms.
13. Continue narrow compact fixed/factored controller source search only as secondary work.

## Current synthesis and newest updates

- **C164:** local process-kill SQLite smoke test matches desired committed-vs-uncommitted censoring semantics.
- **C165:** instrumentation-equivalence matrix can reuse current CSSC budget/frontier/structured-controller/trace fixtures plus a few targeted journal/shared-batch failure cases.
- **C166:** theorem/task-level grouping is required before decision expansion; repeated runs of one theorem remain one split group.
- **C167:** store terminal verified success, local verified progress and real cost vector separately so objectives/scalarizations remain auditable/recomputable.
- **C168:** censored decisions receive objective-specific treatment; never universal deletion or zero-reward imputation.
- **C169:** hold representation/action mask/prover/cost estimator fixed across D0/BC/weighted/Q/bandit comparisons.
- **C170:** prespecified deterministic provider pilot targets <=5 percentage-point half-width on major mean cost shares rather than an arbitrary task count.

## Exact continuation

1. Turn journal fault/equivalence matrix into executable test contracts and exact failure injection points.
2. Prespecify safe-epsilon support floor/pool-size rule and deployment fallback before observing randomized outcomes.
3. Define multiobjective Stage-A utility/evaluation without prematurely collapsing success/token/API/checker/wall cost into one scalar.
4. Finalize event-reader invariants and sequential-return construction for censored trajectories.
5. Validate journal/equivalence, then run deterministic provider cost-share pilot under frozen precision rule.
6. Decide Stage A vs Stage B based on observed headroom; randomized collection only if Stage A is justified.
7. Keep source search secondary and narrow.
8. Keep frontier nonempty. `2026-08-26T1359JST-followup7.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
