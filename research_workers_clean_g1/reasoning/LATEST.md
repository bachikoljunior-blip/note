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
40. `2026-08-26T1427JST-followup.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Implement/validate the causal SQLite journal before randomized policy/OPE collection. First protocol freezes WAL + synchronous=FULL, append-only decision/batch-consumption/outcome events, canonical hashes, and fail-closed conflicts.
2. Execute the F0–F7 injected-failure matrix and epsilon=0 semantic/resource equivalence tests from `2026-08-26T1427JST.md`.
3. Implement the conservative recovery reader: unmatched committed decision = censored; no reward/cost zero-imputation; no guessing about execution effects without independent durable evidence.
4. Replace mutable shared-provider-batch attribution in learning evidence with immutable provider events + append-only `decision -> batch -> node` joins.
5. Logging-policy v0 is prespecified before outcomes: D0-ranked effective legal pool capped at 5, epsilon=1/4, exact rational propensities, minimum behavior support 1/20. Offline target policies remain inside observed pool support; otherwise deterministic D0 fallback.
6. Stage-A v0 representation remains frozen at 154 text-free candidate channels; theorem/task is the split unit and training normalization remains split-safe.
7. Preserve terminal verified success, local verified progress and multidimensional real cost as separate raw labels. Evaluate success-under-budget/Pareto curves first; scalar reward is not raw evidence.
8. Provider deterministic pilot retains prospective 95% task-bootstrap CI half-width target <=5 percentage points for major mean cost shares, subject to collection cap.
9. Pilot decides whether post-generation Stage A has enough headroom. If selected execution is a small share, move upstream to Stage B generation/retrieval/model routing.
10. Journal I/O overhead is measured separately from epsilon=0 semantic equivalence; journal/version/backend are matched across causal arms.
11. Keep narrow compact fixed/factored controller public-source search secondary.

## Current synthesis and newest updates

- **C171:** current CSSC persists behavior decisions only after result construction; interrupted runs can lose the chosen action/choice set.
- **C172:** safe order is durable decision commit -> immutable batch join -> consume/execute -> durable outcome commit -> next randomized decision.
- **C173:** first journal schema needs stable ids, frozen ordered choice set/mask, exact behavior propensities, budget/cost-estimator refs, workspace version, immutable batch join and separate outcome/progress/cost fields.
- **C174:** F0–F7 injection boundaries now have explicit expected censoring/effect semantics.
- **C175:** epsilon=0 equivalence compares semantic outputs and resource observations exactly; wall-clock journal overhead is separate.
- **C176:** current shared proposal-batch `action_id` rewrite is not a trustworthy per-action generation-cost label.
- **C177:** provider generation may incur cost and fail before any execution decision; this is a required negative control.
- **C178:** WAL + synchronous=FULL is the first journal durability setting; scope remains subject to SQLite VFS/storage assumptions.
- **C179:** append-only `journal_event` + update/delete denial triggers is sufficient for the first schema.
- **C180:** canonical payload hashes avoid binary-float ambiguity; epsilon/propensities are exact reduced rationals.
- **C181:** reader separates behavior-decision rows from matched transition rows; censored decisions remain explicit.
- **C182:** logging-policy v0 freezes epsilon=1/4 and randomized pool size <=5, giving minimum behavior propensity 1/20.
- **C183:** deficient support is handled by target-policy restriction/fallback, not unsupported reward extrapolation; report propensity/weight/ESS/support diagnostics.
- **C184:** primary evaluation is kernel-verified success under matched resource budgets and Pareto/cost-per-solved views; raw objectives stay separate.

## Exact continuation

1. Convert C179–C181 into executable JournalWriter/JournalReader transaction pseudocode and F0–F7 exception hooks.
2. Add epsilon=0 equivalence projection and epsilon=1/4 exact-propensity property tests for L=1..5.
3. Define immutable cost-ledger joins and reader property/fuzz tests for truncation, duplicate replay, conflicting payload, illegal sequence and missing batch link.
4. Validate journal/equivalence before any randomized collection.
5. Then run deterministic provider cost-share pilot under frozen precision rule and decide Stage A vs Stage B.
6. Keep public-source search narrow/secondary.
7. Keep frontier nonempty. `2026-08-26T1427JST-followup.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
