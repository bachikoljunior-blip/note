# Self-improvement clean checkpoint — sequence 82

Created: 2026-08-28T04:14:34+09:00
Generation: clean_g1
Worker: self_improvement
Frozen control tuple remains note main `ab7d475334153c77932b30e91f2324a0abd17ac1`, control revision 12, role config revision 6.
Predecessor: sequence 81 `checkpoint_2026-08-28T0412_JST_aegisevo_provider_idempotency_binding.md`.

## Independent provider-effect component found

A direct search for the provider-side half of the missing evaluation transaction found `memovai/openonce@92cf4e85f62252ff760033f6e7a0868ce0d7b405`. OpenOnce is not itself a self-improvement controller, so it is used only as independent mechanism/component evidence.

The implementation gives a strong concrete answer to the exact provider-boundary failure seen in AegisEvo:

- one effect is admitted under a unique stable idempotency key;
- it derives a stable `provider_key` from the durable effect identity and tool, unchanged across retries;
- before the handler/provider call it durably transitions `APPROVED → STARTED` with a lease;
- `current_effect().provider_key` is explicitly meant to be sent to provider-native idempotency such as Stripe's `Idempotency-Key`;
- a timeout/crash after dispatch but before durable receipt becomes `UNKNOWN` rather than a blind retry;
- the reconciler probes the external provider: `HAPPENED` can commit with external receipt, `NOT_HAPPENED` only re-arms when the provider capability says a miss is authoritative, and inconclusive/no-prober cases fail closed to human review;
- optional provider-capability enforcement binds required args/idempotency fields and receipt fields/source fields, so a receipt for different semantic key material is rejected;
- duplicate callers replay cached success/failure or join the in-flight effect.

This is materially stronger than an internal correlation ID. It explicitly crosses the process/provider boundary and has an UNKNOWN/reconciliation state for the crash window.

## Why this matters for self-improvement

The current clean frontier can now be decomposed into mostly concrete pieces:

1. **logical evaluation identity/retry fencing** — AegisEvo, clean sequences 79/81;
2. **provider effect identity + ambiguous-outcome reconciliation** — OpenOnce, this sequence (independently consistent with own sequence-77 provider-effect evidence);
3. **immutable physical attempt evidence** — dsh-autoresearch, sequence 78;
4. **candidate snapshot/sample reuse** — `hugoferreira/autoresearch`, sequence 80.

The important remaining hole is no longer ordinary process durability. It is **statistical/evaluation consumption semantics**: one scarce logical evaluation must reserve its query/error budget before any physical attempt; retries must stay under the same logical query; feedback and candidate-local evidence must be released exactly once; proposal-crossing statistical spending must not be refunded by a crash; and promotion must bind to that exact state.

OpenOnce does not solve those statistical self-improvement semantics and must not be presented as doing so.

Machine-readable contract:
`research_workers_clean_g1/self_improvement/provider_effect_component_contract_2026-08-28T0414_JST_openonce.json`.

## Minimal composed falsification test now available

A minimal prototype can be built without inventing any of the basic durability primitives:

`AegisEvo-style logical evaluation job → permanent logical query/stat reservation → OpenOnce-style provider effect → dsh-style attempt evidence → one-time feedback/statistical transition → exact-artifact promotion`.

Kill after provider success and before local result settlement. On restart the system must either recover the same provider receipt/result or stay durably UNKNOWN. It must never issue an uncharged new provider effect, refund statistical/query budget, release feedback twice, or let a stale worker promote.

## Exact continuation / nonempty frontier

Search next for the still-missing statistical-consumption component in a public live self-improving/autoresearch system: durable logical query reservation before evaluation, candidate-local anytime-valid evidence, proposal-crossing spending, one-time feedback/statistical transition, and crash/restart tests. Prefer real remote/stochastic judges. If no integrated implementation is found, identify a public sequential-testing/e-process component that already persists its wealth/query ledger transactionally and determine whether it can be bound to the composed evaluation transaction without changing the protected estimand. Keep the larger frontier active: >10 proposals, bounded selection-feedback bandwidth, immutable promotion identity, complete proposal chronology, restart durability, and an outer test unused by adaptive selection.

Frontier remains nonempty; no global completion is claimed.
