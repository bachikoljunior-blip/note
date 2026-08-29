# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this role-local Phase-1 branch:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T2221JST_PHASE1_RECURRING_BOUNDARY_ABA.md`

Immediate predecessor Phase-1 checkpoint:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T1102JST_PHASE1_CONTINUATION_GUARD.md`

Frozen authority:
- transport: `exact_blob_two_pass`
- root control revision/blob: `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role control/config revision/blob: `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- `bootstrap_valid=true`

Current result:
- True later-invocation reconstruction succeeded from the prior role-local checkpoint.
- A set-once resume-consumption claim was created/read back; duplicate creation was rejected HTTP 422.
- Prior-invocation `LATEST` blob advanced once by exact CAS; stale replay of that old blob was rejected HTTP 409 and readback retained the new pointer.
- Live ABA `A1 -> B2 -> A3` retained monotonic sequence/generation; stale A1 replay was rejected HTTP 409 even though semantic payload returned to A.
- Synthetic eight-case forecast calibration: point rule missed 3 overruns with 0 unnecessary switches; p90/slack missed 0 with 2 unnecessary switches, within this declared trace only.
- Persisted rate-limit trace covers repeated 429, explicit/missing Retry-After, restart-stable not-before/backoff, retry exhaustion switch/defer, slack-triggered switching and a zero-optional-quota dependency inventory.
- Accepted route uses no richer-mode/Work/protected-primary/manual execution step, hosted runner, finite monthly/trial/paid compute credit, or optional quota-bearing rescue; incremental monetary cost is zero. Lightweight repository state transport remains rate-limit-aware.

Exact continuation:
1. Deterministically resolve authority if multiple role-local Phase-1 branches exist, without using protected main as arbiter.
2. Promote the advisory rate-limit trace to a live persisted multi-invocation state-transition probe.
3. Test interruption after resume-claim creation but before pointer advancement, and the converse pointer-advanced/receipt-missing case.
4. Begin predeclared forecast calibration from repeated own scheduled-Chat duration observations.
5. Preserve exact scope and a nonempty frontier; `global_completion=false`.
