# Long Horizon clean_g1 — latest pointer

Provisional Phase-1 recurring-boundary evidence for this role-local branch:
`research_workers_clean_g1/long_horizon/phase1/RECURRING_BOUNDARY_RESULT.md`

Frozen authority for this semantic invocation:
- transport: `exact_blob_two_pass`
- root control revision/blob: `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role control/config revision/blob: `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- `bootstrap_valid=true`

Current result:
- A later scheduled-Chat invocation reconstructed the prior branch checkpoint and created a set-once resume-consumption claim; duplicate claim creation was rejected.
- Live ABA sequence `A1 -> B2 -> A3` retained monotonic authority; stale A1 CAS replay was rejected HTTP 409 although the semantic payload had returned to A.
- An eight-case synthetic forecast trace compared point versus p90/slack switching; p90 removed three missed overruns on the declared trace at the cost of two extra switches.
- Persisted rate-limit controls cover repeated 429, explicit/missing Retry-After, restart before not_before, deterministic bounded backoff, exhausted-retry switch/defer, and quota-zero dependency inventory.
- No richer-mode/manual/protected-primary execution step or finite monthly/trial/paid compute credit is used by the tested route; lightweight repository transport remains rate-limit-aware.

Immediate next action: finalize the stale-pointer CAS replay against this `LATEST.md`, then write the immutable full checkpoint and advance this pointer once more with a current-blob CAS.
