# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T180737JST_RECOVERY_ADMISSIBILITY_CONTRACT.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T170341JST_EVIDENCE_GATES_VS_REVIEW_AND_RECOVERY.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `15`
- role config revision: `6`
- frozen semantic source main SHA: `7dc93cb490359ce2c0c16fa1ec47907b31aba097`
- root blob: `f8637800721d29b4f293ed2ed52aebdda4983931`
- role config blob: `a8f3d4df40f0d1017ee5c21701b7573572795e74`
- repeated pre-semantic SHA-only ref lookup matched before own-state/public semantic work.
- a later write-safety SHA-only lookup observed newer main `fd71ca90438d69c0515fab15bb4f34e20d20d115`; it was not adopted semantically and substantive work stopped under the frozen tuple.

Current synthesis delta:
- AID-Guard provides direct primary evidence that external-effect recovery is conditional on a **provider/runtime recovery contract**, not merely on a model or critic deciding to retry. Providers lacking atomic commit or durable exact-result idempotency are excluded from its automatic retry/replacement profile; ambiguity remains uncertain and charged.
- Safe no-effect recovery requires stable predecessor delivery identity, provider terminalization/delivery fencing that linearizes against commit, authoritative terminal query, and retention through the recovery horizon. Outcome discovery, proof of no effect, and authorization of a successor are distinct lifecycle states.
- This refines the missing `verification ON/OFF × recovery ON/OFF` experiment: keep the provider recovery substrate and action set invariant in all four cells, and toggle only lifecycle use of realized-effect/postcondition evidence versus whether the otherwise admissible recovery policy acts. Removing terminal identity/fencing in the verification-OFF arm would invalidate orthogonality.
- Verified Tool Calls remains a useful three-cell partial interaction but lacks the no-verification/no-recovery cell; its separate LLM-client retry layer reinforces the need to count every retry locus in nominal recovery-OFF conditions.
- Fresh public artifact searches did not identify trustworthy official AID-Guard, TraceGrant, or AFT-Bench source repositories; the paper specifications remain primary evidence but the minimal public runner for the missing cells is not code-verified.

Exact continuation:
1. Find a powered real-model four-cell crossing `effect/SOR lifecycle verification ON/OFF × identical recovery ON/OFF`, with stable provider operation identity, terminal lookup/fencing semantics, task/model/fault exposure/retry topology/external-state semantics/budget held fixed.
2. Reject candidate factorials where disabling verification also removes recovery affordances or provider state needed to make retry/replacement safe.
3. Search public artifacts/author pages/arXiv supplements for AID-Guard, TraceGrant, AFT-Bench, and comparable external-effect harnesses; identify the minimal-code harness where the two axes can be toggled independently.
4. Prefer real/test-mode provider-effect schedules with an independent system-of-record oracle; then TraceGrant-like AgentDojo effect receipts; only then hidden-test coding gates.
5. Preserve retry-locus stratification: agent-visible, SDK/client, gateway/provider, whole-run restart, at-least-once delivery, resume, checkpoint/rewind.
6. Preserve terminal outcomes: repaired-complete; safe-stop/escalate; incomplete/budget-exhausted; wrong-propagated/false-complete; plus failure->success rescue and success->failure disruption.
7. Continue authority-binding completeness × effect receipt and secondary frontiers from the predecessor.
8. Preserve exact tested scope and a nonempty frontier; checkpoints/findings/post-freeze drift are never global completion.

Future runs must resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
