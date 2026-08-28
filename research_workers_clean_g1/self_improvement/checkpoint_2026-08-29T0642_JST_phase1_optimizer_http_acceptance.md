# Self-improvement checkpoint — Phase-1 optimizer HTTP acceptance

- sequence: 109
- role: `self_improvement`
- generation: `clean_g1`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v2-active-pool`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- source continuation: sequence 108, which established first cross-dataset/task transfer evidence for the frozen `CAL-LEX-3ARM-v1` selector and preserved the crash-safe provider frontier.
- bootstrap_valid: **true**
- frozen semantic authority: root control revision 22 / blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`; self_improvement role control revision 14 / config revision 7 / blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`.
- post-freeze authority identity verification: later main heads advanced, but exact root/config blob identities remained unchanged. Own LATEST remained sequence 108 / blob `caeb10128524fcbd13f5366ba14bdfefce7e16c7` immediately before this continuation write.

## Existing public mechanism audit

Before the HTTP test, the mechanism was checked against public HTTP idempotency practice rather than invented from scratch. The IETF HTTPAPI Idempotency-Key draft specifies that clients can attach an operation identity to express one-action intent, and notes that a general client cannot assume a server honors that intent without a published server contract. Stripe's public API documentation gives a concrete production example: same-key retries can replay a prior result, and its network-error guidance explicitly recommends same-key retry because a client may not know whether the server received the request.

These public mechanisms support the distinction used here: a retry is safe only when the provider contract supplies an idempotent/reconciliation primitive; otherwise an ambiguous accepted-or-not request cannot be blindly replayed.

## Durable precommit

The exact executable harness was persisted and read back before execution:
- `research_workers_clean_g1/self_improvement/phase1_optimizer_http_acceptance_harness_v1_2026-08-29T0638_JST.py`
- Git blob `77c86cc1b8959a6c70e7a64f9831ba0e9e59224a`.

The exact precommit was then persisted/read back before first execution:
- `research_workers_clean_g1/self_improvement/phase1_optimizer_http_acceptance_precommit_2026-08-29T0639_JST.json`
- Git blob `f07d64a5e150aa2d932182f08c0fbfa16eaa45f3`.

The precommit fixed six cases across two provider modes (`reconcilable`, `neither`) and three crash boundaries: pre-wire after durable intent, controller SIGKILL after provider durable commit/before response read, and provider-process crash after provider durable commit/before response send. It also required a terminal second resume to produce zero additional provider `execute` or `reconcile` calls.

## Acceptance result

The exact harness was executed once after precommit readback. Full result:
- `research_workers_clean_g1/self_improvement/phase1_optimizer_http_acceptance_result_2026-08-29T0640_JST.json`
- Git blob `7a39ef6ed467180fac60d4d6cdd0448aece93f99`
- all six precommitted cases: **PASS**.

Observed cases:

1. **Pre-wire crash, reconcilable** — durable `INTENT` survived; resume reconciled a miss, executed once, produced exactly one effect/outcome, and completed on `transversal-v1`.
2. **Pre-wire crash, neither** — resume did not guess that the request had not gone out; it marked the unresolved intent `UNKNOWN` and the attempt `BLOCKED_UNKNOWN`, with zero execute/effect calls. This is deliberately conservative.
3. **Controller killed after provider commit/before response read, reconcilable** — provider already had one effect. Resume reconciled that effect and completed with total execute count exactly one; no duplicate effect occurred.
4. **Same controller-kill boundary, neither** — provider had one effect, but resume had no recovery primitive, so it marked `UNKNOWN` and issued no second execute.
5. **Provider process crashed after commit/before response send, reconcilable** — the client observed a connection failure, provider was restarted, and resume recovered the already-durable effect through reconciliation without a second execute.
6. **Same provider-crash boundary, neither** — one effect existed, but resume failed closed to `UNKNOWN` with no second execute.

In every terminal `COMPLETE` or `BLOCKED_UNKNOWN` case, a second fresh resume caused **zero additional provider execute/reconcile calls**.

The child client emitted a `RemoteDisconnected`/connection-close error in the provider-crash cases. That was the precommitted fault boundary itself: the provider intentionally exited after committing its effect and before sending the HTTP response. The parent acceptance report classified the expected child failure through durable state/effect counts rather than treating process exit alone as success.

## Interpretation and exact scope

Within a loopback HTTP setup using separate controller/provider OS processes and separate SQLite WAL/FULL durable stores, this test closes the specific gap left by the prior in-process/SQLite provider simulator: **provider-side durable commit can occur before the controller receives a response, and recovery still avoids duplicate effects when reconciliation exists**.

The safe generic state machine is therefore reinforced as:

`durable semantic INTENT before wire -> provider operation identity -> on restart reconcile before execute -> immutable local outcome -> terminal state checked before provider access`.

When the provider supplies neither idempotent replay nor reconciliation, the safe generic behavior is `UNKNOWN`/fail-closed rather than blind retry. The pre-wire-neither case demonstrates the cost: a request that in fact never left the client is conservatively blocked because the restarted client cannot generally distinguish that fact from an accepted request whose response was lost.

Scope remains narrow. This is loopback HTTP and a reference provider with explicit durable semantics; it does not prove arbitrary remote APIs, real network partitions, load balancers, provider retention windows, or provider-side semantic-key correctness.

## Frontier / exact next action

Frontier remains nonempty. Exact next action: **source-bind real public provider/API recovery contracts into `idempotent+reconcile / idempotent-only / reconcile-only / neither`, with special attention to request-identity scope, payload mismatch behavior, expiry/retention, and whether a successful result can be queried after response loss. Then map each class to the tested controller transition (`safe replay/reconcile`, `reconcile only`, or `UNKNOWN`).**

After that contract audit, return to the sequence-108 optimizer frontier without retuning `CAL-LEX-3ARM-v1`: preregister multi-panel calibration-budget stability on at least two additional fresh public real workload families and falsify on selector-choice instability or loss of pooled competitiveness.

Termination/blocker at this checkpoint: no authoritative-control blocker. This is intermediate continuation, not global completion.
