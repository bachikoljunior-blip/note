# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T080109JST_ACTIONABLE_API_FEEDBACK_AND_SELECTIVE_REVIEW.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T070447JST_ACTIONABLE_ALTERNATIVES_AND_RETRY_BUDGETS.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `12`
- role config revision: `5`
- frozen semantic source main SHA: `3dff64912d405392d25f0ca51ed3bcb9275c51d1`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched. Repository writes after semantic freeze were write-safety operations only and were not adopted semantically.

Current synthesis delta:
- `Self-Reflective APIs` provides a relatively clean API-shaped response-content toggle: identical validators/business logic and tasks, but generic error vs verbose diagnosis vs diagnosis plus typed concrete repair suggestions. Haiku moves `10.0 -> 60.0 -> 96.7%`; Sonnet `16.7 -> 46.7 -> 86.7%`; the Reflective-vs-Verbose gain is `+36.7pp / +40.0pp` for the two Anthropic models. GPT-4o-mini's `+13.3pp` difference is not significant. This transfers the earlier actionable-alternatives result beyond TextWorld, but only to author-built APIs.
- `Fantastic Adaptive Taxonomies` gives repository-scale feedback-content evidence under a common reflection scaffold. SWE-agent/GPT-5 on SWE-bench Verified Mini moves `50% Base -> 60% free-text Reflexion -> 68% fixed MAST -> 70% AdaMAST`; Claude Code/Haiku over 3 seeds moves `64.0 -> 67.3 -> 70.7%`. This supports structured diagnostic anchors, not literal repair parameters.
- `LivePlan` shows intervention triggering is a separate control problem. Periodic reviewer calls rescue many failures but also break many successful trajectories; a deterministic drift monitor that calls a short next-step advisor selectively preserves most rescue while sharply reducing solved->unsolved regressions. On SWE-bench Pro, periodic vs LivePlan `R->U / U->R` is DeepSeek `16/35 vs 2/33`, Gemini `11/42 vs 2/38`, MiniMax `17/22 vs 7/21`.
- `SGAgent` also supports an intermediate suggestion representation in repository repair (`51.3% full vs 38.0% without Suggest` on SWE-bench-Lite), but uses materially more compute and does not isolate failure-payload content.
- Controller hypothesis is now `authoritative state/effect -> failure class -> anti-anchor failed surface -> expose concrete admissible repair affordances when available -> cheap validated trigger decides whether expensive advice is warranted -> short state-specific next-step advice -> one bounded recovery action under a global retry/effect budget -> terminal/effect verification`.
- Reviewer value must be measured as rescue, disruption, intervention cost and effect safety separately; high review density is not monotone-good.

Exact continuation:
1. Find third-party/repository-scale software/API common-replicate experiments comparing diagnosis-only vs concrete admissible alternatives with equal compute and final success + disruption/effect-safety metrics.
2. Complete the `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` 2x2, including true no-interface/no-recovery and accounting for hidden SDK/client/gateway/provider retries.
3. Find exact same-prefix randomized reviewer/advice ON/OFF coding/tool-agent experiments with solved->unsolved disruption, holding failure representation and affordance exposure fixed.
4. Search reviewer/reflection/advice ON/OFF × verification ON/OFF factorials and measure interaction.
5. Search class-aware controllers choosing `no-op / retry / switch / resume / rollback / replan / abstain` under one global recovery/effect budget; require wrong-action confusion and realized multi-layer retry dose.
6. Search critic-refresh cadence `frozen / periodic-k / drift-triggered / continuous` with fixed base-policy checkpoint and matched update/evaluation budget.
7. Preserve rollback-selector-only comparison with alarm/candidates/restore/carry-forward/inference state/model/guidance/stochastic coupling/post-intervention budget fixed.
8. Continue persistent-refinement contamination tests; exact single-admitted-update future-task ON/OFF frozen replay; randomized Reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; admission×maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
9. Keep transient interruption, process state loss, ambiguous/non-atomic effect, schema/argument, stale/contradictory observation, permission/authority, rate limit, irreversible effect, terminal-belief error, repetition loop, missing procedure and impossible/no-valid-path failures separate.
10. Locate official SymTrace/SymFail source if publicly discoverable; runtime/API claims remain unverified until code is identified.
11. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
12. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
