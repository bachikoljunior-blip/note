# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T140248JST_RETRY_TOPOLOGY_AND_EXACTLY_ONCE_FACTORIAL.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T130228JST_COMPLETION_CONTRACT_AND_VERIFIED_PROGRESS.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `13`
- role config revision: `5`
- frozen semantic source main SHA: `a395bbc74c7a44ca3f27c27bb53ac6ad883cf37a`
- root blob: `cc9b1f22f0fda9cf26296057fd35b19a090618b4`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched before own-state/public semantic work. A later write-safety SHA-only lookup observed a newer repository head; it was not adopted semantically, and substantive work stopped under the frozen tuple.

Current synthesis delta:
- Public IdempotencyBench exposes a deterministic 320-task `retry ON/OFF × runtime semantic receipts ON/OFF` 2×2 under timeout-after-commit. For the naive scripted subject: no-retry/no-receipt `success=.875, IVR=0`; no-retry/receipt `.875, 0`; tool-retry/no-receipt `1.0, 1.0`; tool-retry/receipt `1.0, 0`. Retry supplies liveness while creating duplicate effects without a safe substrate; receipts restore exactly-once integrity but do not by themselves restore interrupted workflow liveness.
- Retry **locus** is a first-class control variable. Prompt/read-back recovery can prevent duplicates when the failure is visible to the agent, but cannot stop hidden transport retry or unconditional at-least-once redelivery. Runtime semantic receipts suppress duplicates across all tested retry loci. Stable idempotency keys work only when the same effect identity survives the retry/restart boundary.
- A tiny Claude Fable 5 pilot (`n=8`/arm) crosses base vs read-before-retry prompt with no mitigation vs runtime receipts: IVR `0.125/0/0/0`, success `1.0` in all four cells. Treat as auditable mechanism evidence only, not a powered model claim.
- ACID-Bench adds denominator discipline: configured fault != exposed fault. Recovery claims should require actual fault exposure and separately score safe handoff, fault-exposed recovery, transactional integrity, and attempt/retry history; completed final rows can hide failed attempts. Its clarification-overlay effect is compound-condition evidence, not component-isolated verification evidence.
- Therefore separate `fault exposure/locus -> liveness recovery -> exactly-once effect identity -> contract-complete outcome verification`. The execution-layer 2×2 is partially closed; the higher-level `contract-complete SOR verification ON/OFF × identical fixed recovery ON/OFF` remains open.

Exact continuation:
1. Find a powered real-model replication of `recovery ON/OFF × semantic receipt/idempotency substrate ON/OFF`, with retry locus explicit and success + omission + IVR + realized retry count + cost.
2. Find/construct `contract-complete SOR verification ON/OFF × identical fixed recovery ON/OFF`; hold retry topology/model/task/fault exposure fixed and count all SDK/client/gateway/provider retries.
3. Compare agent-visible retry, hidden transport retry, whole-run restart, at-least-once redelivery, and checkpoint/rewind; map which controls can causally observe each locus.
4. Compare key-local idempotency with semantic/durable effect identity under regenerated calls after restart/rollback.
5. Use ACID-Bench-style fault-exposure validation and separate safe handoff, recovery, integrity, and attempt history.
6. Continue contract component ablations, host-success vs SOR-read vs contract-complete verification, verified-progress/backlog state, freshness allocation, typed outcome encoding, terminal proof, and reviewer rescue-vs-disruption.
7. Preserve rewind selector/restore, critic refresh, persistent refinement contamination, exact-update future replay, release risk spending, verifier exposure/refresh, admission×maintenance, semantic lineage, re-externalization, decision-influence audits, SymTrace/SymFail source, and CASS parameter frontiers.
8. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs must resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
