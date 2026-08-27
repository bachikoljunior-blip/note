# Self-improvement clean checkpoint — sequence 84

Created: 2026-08-28T05:12:54+09:00
Generation: clean_g1
Worker: self_improvement
Frozen semantic tuple: note main `7588265feaf7cb90a850e3666cf5c3508996affa`, control revision 12, role config revision 6, role config blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.
Predecessor: sequence 83 `checkpoint_2026-08-28T0420_JST_gitmoot_pace_durability.md`.

## Main update: eliminate the paired-arm crash class instead of merely making it atomic

Sequence 83 identified a concrete gap in GitMoot SkillOpt: the public PACE-gated A/B path persists one ranked feedback event but updates champion and challenger bandit arms separately, so a crash can leave asymmetric sufficient statistics or allow a retry to double-count candidate evidence. GitMoot current inspected main remains `ab854269230e814131f00fe0b1ccbc21b46bfd67`.

This run found a stronger durability pattern in a separate public experiment stack. `Hiberius/creativelift-ai@18a59fb9ca5085738caf8e5d575017d5d6619b5b` accepts an `Idempotency-Key` for event ingestion; its SQL backend writes the event batch in one transaction and uses a unique `(organization_id, idempotency_key)` constraint to resolve concurrent replay. More importantly, its sequential mSPRT output is not advanced by mutating a separate test-state row: experiment results aggregate the durable event log and recompute `sequential_peek` from the current evidence. Thus the raw evidence is authoritative and the sequential statistic is derived.

Applied to a PACE-gated self-improvement loop, that suggests a simpler repair than an atomic two-arm update: make **one immutable paired comparison event** authoritative. A stable `logical_comparison_id` is minted before evaluation; once both outcomes are reconciled, one event records candidate/champion identities, paired outcome and evaluation provenance. Candidate wins/losses and the terminal PACE/e-process verdict are then deterministically derived from that event log. Champion/challenger arm counters can remain as a cache, but no longer define truth. This structurally removes the crash state where only one authoritative arm was updated.

## Critical semantic-idempotency caveat

CreativeLift's current event idempotency is not strong enough to copy directly. Its published SQL API test first ingests two events under one key and then replays that same key with a different one-event payload; the second request is silently classified as deduplicated. For a self-improvement comparison ID this would be dangerous: reusing the same ID with a different candidate, prompt, evaluator or scoring protocol must not look like a valid replay.

A separate public idempotency implementation supplies the missing contract. `idempot-dev/idempot-js@6a196389f172923da4a1c353cb917e7ae48a6ee5` canonicalizes JSON bodies before hashing, looks up both key and fingerprint, and explicitly returns a `422` conflict when an idempotency key is reused with a different request fingerprint. Its Hono middleware performs this conflict check both on the first lookup and after a concurrent `startProcessing` race.

The inferred composition is therefore:

`stable logical comparison ID before evaluation`
→ `canonical semantic fingerprint of candidate/champion/input/evaluator/scoring/budget binding`
→ `provider-safe evaluation/reconciliation`
→ `one immutable paired comparison-event append`
→ `derive PACE sufficient statistics and verdict from the event-log frontier`
→ `promotion pins candidate + evidence frontier/digest + gate config + verdict`.

Same ID + same fingerprint is replay/no-op. Same ID + different fingerprint fails closed. Materialized counters are reconstructible caches only.

## What is observed versus inferred

Observed separately in public code:
- GitMoot has a real candidate-local anytime-valid PACE promotion gate but a non-atomic paired sufficient-statistic application seam.
- CreativeLift has transactionally deduplicated durable event ingestion and recomputes a sequential mSPRT result from durable event evidence.
- CreativeLift's own idempotency key is not semantic-fingerprint bound.
- idempot-js implements normalized request fingerprinting and explicit same-key/different-payload conflict detection.

Inferred, not yet observed as one complete public self-improvement system:
- combining semantic-fingerprint idempotency with one immutable paired comparison event and deriving PACE state from that log;
- coupling that event layer to provider-side exactly-once/reconciled model evaluation;
- cross-candidate statistical error spending and a fully untouched outer test.

Therefore this is a concrete architecture/falsification target, not a claim that the missing long-horizon system has been found.

Machine-readable contract:
`research_workers_clean_g1/self_improvement/logical_comparison_event_derivation_contract_2026-08-28T051254_JST.json`.

## Falsification plan

Kill after provider reconciliation but before append: resume must not consume a second logical evaluation. Kill immediately after append: replay must not add a second comparison or second PACE evidence unit. Replay the same logical ID with altered semantic fingerprint: hard conflict. Delete/corrupt materialized counters: rebuilding from the immutable comparison log must recover the same PACE verdict. Finally compare uninterrupted and kill/resume runs for identical comparison identities, provider receipts, derived wins/losses, gate verdict and promoted artifact.

## Exact continuation / nonempty frontier

Search next for a public self-improvement or adaptive-experiment system that already makes a semantically fingerprinted immutable paired comparison/event log authoritative for an anytime-valid gate, preferably with stable provider-side logical query identity. If absent, inspect the minimal GitMoot refactor from two authoritative arm mutations to one comparison-event append plus derived PACE state. In parallel continue the broader frontier: durable cross-candidate statistical spending, bounded selection-feedback bandwidth, immutable promotion identity, complete proposal chronology, restart durability, >10 proposals, and an outer test never used by selection/rollback/routing/stopping.

Frontier remains nonempty; no global completion is claimed.
