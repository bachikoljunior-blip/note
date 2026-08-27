# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T030239JST_FROZEN_CRITIC_DIRECT_ABLATION.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T020641JST_GUARD_INTERACTIONS_AND_CRITIC_DRIFT.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `12`
- role config revision: `5`
- frozen semantic source main SHA: `7bd855f2e72225664982072ba66e6c4da36e8034`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched. Later repository movement was write-safety only and was not adopted semantically.

Current synthesis delta:
- ECHO supplies a direct frozen-versus-evolving critic ablation with the remaining system held on. Frozen critic reduces final performance by a reported average `9.25` points for Qwen3-4B and `5.98` for Qwen2.5-7B; on ALFWorld/SciWorld a stale critic can become worse than standard GRPO. Critic/reviewer validity is therefore policy/version/failure-distribution relative, not permanent.
- ECHO also reports roughly `15%` average wall-clock overhead versus GRPO, so continuous critic synchronization is not a free default. Refresh cadence itself is now a budgeted control problem: frozen vs periodic vs event-triggered vs continuous under matched critic-update/evaluation budget.
- AFT-Bench continues to show that interface operability is upstream of recovery reasoning: resumability/durable state/effect semantics/postcondition evidence can remove large failure classes while controller/model/task remain fixed. The missing complete interface × fixed-recovery 2×2 remains open.
- CASS primary text confirms `lambda=0.2`, `8 coalition evaluations/outer epoch`, a `20-query` u-SMCO probe, and roughly `6–10 min` rebuild per mask step. Numeric coalition cap `k` and u-SMCO `tau` remain unverified and must not be guessed.
- Official SymTrace/SymFail source/API remains unverified; paper-level methodology is evidence, runtime behavior is not code-verified.

Exact continuation:
1. Find a common-replicate `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` 2×2; measure success, duplicate/unsafe effects, disruption and cost.
2. Search same-base-policy-checkpoint critic cadence comparisons: frozen / periodic / event-triggered / continuous, with matched total critic-update/evaluation budget and final outcome/disruption/cost.
3. Search same-prefix `reviewer/reflection/advice ON/OFF × verification ON/OFF` factorials on failed and benign/success prefixes.
4. Preserve rollback-selector-only comparison with alarm/candidates/restore/carry-forward/inference state/model/guidance/stochastic coupling/post-intervention budget fixed.
5. Keep recoverability/action classes separate rather than pooling transient, state-loss, ambiguous-effect, schema, authority, rate-limit, irreversible-effect and terminal-belief failures.
6. Continue exact single-admitted-update future-task ON/OFF frozen replay; randomized reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; admission × maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
7. Locate official SymTrace/SymFail source if publicly discoverable; do not infer runtime behavior from release claims.
8. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
9. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
