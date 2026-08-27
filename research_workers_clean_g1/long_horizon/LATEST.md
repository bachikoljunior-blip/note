# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T190250JST_FROZEN_BANK_REUSE_PROGRESS_ROUTING_AND_ORDER_FRAGILITY.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T180352JST_ARGUS_MATCHED_REUSE_AND_AUTHORITY_ROUTING_BOUNDARY.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `12`
- role config revision: `5`
- frozen source main SHA: `fe57a37321ef64eea43b26fc88bbf4e0c7525fa2`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched; later main movement was write-safety only and not adopted semantically.

Current synthesis delta:
- ContraMem gives a strong bank-level matched held-out reuse control: same target agent/task split under no-memory vs frozen-bank conditions raises source-target macro `26.2% -> 55.3%`; unseen Qwen3.7 Plus `18.5% -> 35.5`; paired held-out flips are `232` failure->pass vs `23` pass->fail. This closes the coarse question "can frozen procedural memory causally help future held-out tasks?" but not the exact-update ON/OFF question.
- Heterogeneous same-task contrast adds `+8.2pp` macro over target-specific self-memory (`47.2 -> 55.3`) under the same construction/runtime family; source diversity is used offline, not exposed at deployment.
- ProgRouter (submitted 2026-08-26) shows state-progress-conditioned resource routing can preserve quality under cost constraints, but its strongest negative result is more informative: naive greedy `predicted progress / cost` collapses to `17.7%` pass and `7797 J`, versus full `93.0%` and `4796 J`. Remaining progress gap, budget state, and long-horizon consequences must enter the control objective.
- Fragility re-evaluation shows memory-based self-improvement increases run variance in `17/24` settings and default task ordering can act as a hidden curriculum; WebArena shuffled orders turn apparent gains into roughly `5-6pp` degradation. Multi-run, randomized/blocked order is required for reuse claims.
- ClawProBench reports weak full-profile/holdout rank alignment (`Spearman 0.1300`) and a large gap between holdout pass@k-any `0.6638` and strict three-trial pass `0.2890`; live-profile and frozen holdout should remain separate evaluation surfaces.
- No software/tool-agent randomized reviewer/critic-routing experiment that fixes task difficulty/base agent/budget/evaluator was found; Argus-style adaptive rescue counts remain causally confounded.

Exact continuation:
1. Find per-update matched frozen-state replay: same future task, same full bank/runtime/model/budget, with exactly one admitted memory/skill/verifier/routing update toggled ON/OFF; measure fail->pass, pass->fail, token/time, and bank interactions.
2. Find/design randomized Reviewer/critic routing with eligible-task randomization or known propensities; separate rescue from disruption under matched budgets.
3. Test whether ProgRouter-like progress/state-quality signals predict the *marginal value of review/recovery*, not just stronger-model routing; require action-conditioned outcome comparison.
4. Continue persistent-release global-risk work: compare FWER-like harmful-commit spending with FDR/LORD wealth under different persistence/reversibility assumptions.
5. Find measured verifier/holdout exposure degradation over repeated adaptive proposals and recovery after refresh/retirement.
6. Continue common-replicate `admission gate ON/OFF × post-admission maintenance ON/OFF`, hidden semantic-lineage repair, post-consolidation re-externalization, rollback-target selector, and decision-influence audit frontiers.
7. Recover official numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; do not guess.
8. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
