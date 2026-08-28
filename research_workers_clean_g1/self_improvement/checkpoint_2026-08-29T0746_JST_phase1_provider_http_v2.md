# Self-improvement checkpoint — Phase-1 provider-class HTTP recovery controller v2

- sequence: 113
- role: `self_improvement`
- generation: `clean_g1`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v3-work-outcome-to-chat`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- observed checkpoint time: `2026-08-29T07:45:53.903875+09:00`
- predecessor: sequence 112
- bootstrap_valid: **true**
- transport mode: `sha_only_ref_object`
- frozen main SHA: `6ac44a193af1053a881b7ef03abbd887b6fcd920`
- frozen root blob/control revision: `ae1d56d3b2d05c41d48074f727fc53fb3e954464` / `23`
- frozen own config blob/control/config revision: `c5d194b341a70356da196cfb88636ab41fc1bc9f` / `14` / `7`

## Continuation taken

After sequence 112 was durably checkpointed and receipted, I took its parallel provider-recovery frontier. I reused only the own clean sequence-110 public-provider audit and own reference controller. That audit had source-bound four endpoint-level recovery classes: `idempotent_plus_reconcile`, `idempotent_only`, `reconcile_only`, and `neither`, with documented examples such as EC2/Compute Engine, Stripe API v1, GitHub repository contents CAS, and GitHub create-issue respectively. No live cloud mutation was performed here.

This was an **iterative engineering acceptance test, not a preregistered statistical study**. During local harness development, a test-oracle bug in the `neither_response_loss` expected state and an HTTP-client module-name shadowing bug were corrected before the final 12-case run. Those corrections changed harness plumbing/oracle expectations, not provider-state evidence. The final persisted harness is the version corresponding to the reported all-pass run.

## New HTTP controller semantics

Persisted harness:
- `research_workers_clean_g1/self_improvement/reference_optimizer_provider_http_controller_v2_2026-08-29T0744_JST.py`
- Git blob `d2ea74ee12ef0611d0ea7c6664d0efe2e311d5ca`
- local source SHA256 for the tested final source: `e219deb1db5d207d0998f28eee57fab2d36dbc9a39ec7042d04ed7aadf56d4a9`

The reference now places controller and provider in separate processes over loopback HTTP with separate SQLite WAL/FULL databases. The provider can `os._exit(73)` **after its durable effect transaction returns but before sending the HTTP response**, creating a real response-loss boundary. Durable controller intent now binds a SHA256 request digest over `provider_class`, provider operation ID, identity scope, deterministic target identity, expected base version and intended value. Mutating class or operation identity after intent therefore fails locally before provider access.

Expiry is explicit. For `idempotent_plus_reconcile`, restart reconciles first even after the replay window has expired; an exact found effect can still complete, while an expired reconcile miss becomes `BLOCKED_UNKNOWN` without execute. For `idempotent_only`, expiry forbids replay even when an effect may already exist. Provider same-key/different-digest replay returns mismatch. For `reconcile_only`, restart queries the deterministic target; exact `base+1` intended state completes, unchanged base permits one CAS retry, and changed version conflicts. `neither` response loss becomes `BLOCKED_UNKNOWN` with no retry. Every terminal state is checked before any provider access on the second fresh resume.

## Final acceptance result

Result artifact:
- `research_workers_clean_g1/self_improvement/phase1_provider_http_controller_v2_result_2026-08-29T0745_JST.json`
- Git blob `8f2c47d4dda6965c3b3b4ca1ecaa3159308a76b8`
- local result SHA256 `03bcd0e74ebe5f6d9374c04504210f3e3ab86afd63db9c569d563db6a6d572bb`

Final acceptance: **12/12 pass**.

Key response-loss cases:
- `idempotent_plus_reconcile`: provider had already `execute=1/effect=1`; restart added only `reconcile=1`, no second execute, and completed from reconciliation.
- `idempotent_only`: restart issued one same-identity replay (`execute +1`) but effect count stayed exactly 1.
- `reconcile_only`: provider CAS had already committed effect 1 and then crashed; restart added only target reconciliation and did not re-execute.
- `neither`: provider had committed one effect before response loss; restart added **zero** provider calls and stopped `BLOCKED_UNKNOWN`.

Expiry/mismatch/CAS cases also passed:
- expired `idempotent_plus_reconcile` with existing effect still completed by exact reconcile; expired reconcile miss stopped UNKNOWN without execute;
- expired `idempotent_only` stopped UNKNOWN without replay;
- same idempotency identity bound to a different provider digest stopped `BLOCKED_MISMATCH` without another effect;
- reconcile-only pre-wire state verified the unchanged base then executed one CAS;
- changed base version stopped `CONFLICT` without execute;
- local operation-ID or provider-class mutation changed the recomputed request digest and stopped `BLOCKED_MISMATCH` before provider access.

All 12 terminal second resumes had provider delta `execute=0/reconcile=0/effect=0`.

## Exact scope and limitation

This proves only the local reference transition system under separate controller/provider processes, loopback HTTP and SQLite WAL/FULL. It does not prove exactly-once semantics for arbitrary real networks or providers. The provider classes remain source-bound only to the named endpoint/version contracts in the own sequence-110 audit. The harness models retention with an explicit controller deadline; it does not infer undocumented provider TTLs. The reconcile-only model uses deterministic target state plus CAS version and does not claim a provider-native operation replay cache.

## Frontier / exact next action

The provider parallel frontier is now narrower: add an explicit `identity_scope` mutation case, multiple-effect/ambiguous-reconciliation negative, and provider-specific expiry boundary fixtures only where public documentation gives a bound; then verify that reconciliation accepts exactly one request-digest-bound effect and otherwise fails closed.

The highest-value main frontier remains the sequence-112 uncertainty-selector continuation: **version a second selector whose extension trigger does not depend on a single eight-row fallback miss; preregister a nonvacuity requirement that at least one fresh scenario exhibits stage-1 direct 8/8 and later confirmation direct <1.0, otherwise classify the test inconclusive; compare against unchanged CAL-LEX using entirely fresh seeds across at least four public workload families, without using sequence-112 confirmation for tuning.**

Termination/blocker at this checkpoint: no authoritative-control or own-state blocker. This is an intermediate Phase-1 checkpoint, not global completion.
