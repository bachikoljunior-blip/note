# Phase-1 claim/witness coupling across independent authority domains

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `9aecbfd72ebddea92de34792a4587f81e58a744c`
- frozen DESIRED_STATE: control revision `22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- post-freeze authority identity verified: `true`
- predecessor leaf: `PHASE1_WITNESS_MEMBERSHIP_RECONFIGURATION_20260829_055930_JST.md`
- semantic inputs: own role-local Phase-1 state, public AWS/Microsoft dual-write/outbox documentation, and one finite synthetic cross-domain model.

## Leaf objective

The preceding leaves assumed that the claim epoch and the durable decision/effect witness could ultimately be validated in one authority history. This leaf separates them:

- consensus domain `X` owns the task/claim epoch;
- independent domain `Y` owns the effect/decision witness.

The model varies claim advancement before a read or after the final read but before the effect, fresh/stale X reads, authoritative Y status availability, ambiguous Y writes that may already have applied, takeover, and a durable effect-id dedupe contract.

Compared policies:

1. `x_authoritative` — current-looking X claim is sufficient to call Y.
2. `y_authoritative` — Y witness/status is sufficient to decide done/retry without a current X proof.
3. `read_both_then_act` — read X and Y before acting, but without an atomic cross-domain authorization point.
4. `intent_revocable` — write a durable Y intent linked to the X epoch, while continuing to treat X authority as revocable until effect time.
5. `intent_irrevocable` — atomically verify the X epoch and transition X to an irrevocable `AUTHORIZED(effect_id)` state; Y is then a conditional/idempotent consumer of that stable effect identity.
6. `single_domain_colocation` — benchmark that co-locates claim-currentness and effect authorization in one atomic authority transition.

## Public mechanism boundary

AWS's transactional-outbox guidance identifies the core dual-write problem: independently writing business state and an event/message can leave inconsistent state if either write fails, and the outbox solution puts the business update and outbox record in the **same transaction**. AWS also notes that downstream delivery can be duplicate and therefore consumers should be idempotent. Microsoft’s current Cosmos DB transactional-outbox sample makes the same scope boundary explicit: state plus event are written atomically only within one `TransactionalBatch`/logical partition, while change-feed delivery is at-least-once and consumers dedupe by event ID.

Sources:
- https://docs.aws.amazon.com/en_en/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
- https://learn.microsoft.com/en-us/samples/azure-samples/cosmos-db-design-patterns/transactional-outbox/

These are mechanism precedents for avoiding unconstrained dual writes and for stable event identity; the claim/effect authorization lattice below is synthetic.

## Finite model

The script enumerates **192 equal-weight synthetic scenarios** over:

- X claim advancement: none / before the worker read / after the final worker read;
- X read fresh/stale;
- Y status available/unavailable;
- Y conditional-idempotency contract absent/present;
- takeover absent/present;
- Y response clear success / clear failure / ambiguous;
- ambiguous Y request actually absent/applied.

### Aggregate comparison

| policy | unsafe | stale authority | duplicate | orphan | resolved |
|---|---:|---:|---:|---:|---:|
| X-authoritative | **92** | 84 | **20** | 20 | 80 |
| Y-authoritative | **88** | **88** | 0 | 60 | 44 |
| read both then act | **88** | 84 | 10 | 20 | 84 |
| revocable cross-domain intent | **66** | 66 | 0 | 50 | 76 |
| irrevocable X authorization + effect ID | **0** | 0 | 0 | 0 | **192** |
| single-domain co-location | **0** | 0 | 0 | 0 | **192** |

The two zero-unsafe policies deliberately use a different authorization contract: after the `AUTHORIZED(effect_id)` transition, later claim supersession does not revoke that already-authorized effect. This is not evidence that two revocable domains became atomic.

## Result 1: fresh reads from both domains still leave a cross-domain TOCTOU window

The `claim advances after final read but before effect` slice has **64** scenarios.

- `x_authoritative`: unsafe 56;
- `y_authoritative`: unsafe 44;
- `read_both_then_act`: unsafe **56**;
- `intent_revocable`: unsafe 44;
- `intent_irrevocable`: unsafe 0;
- `single_domain_colocation`: unsafe 0.

A fresh X read plus a fresh Y read proves only a snapshot pair. It does not make the interval from those reads to the external effect atomic. If X remains revocable until effect time, X can advance after the read and invalidate the effect.

## Result 2: a cross-domain intent record is not a revocation fence by itself

`intent_revocable` improves the aggregate unsafe count relative to the read-only baselines but still has **66 unsafe** scenarios. The durable intent improves restart identity and avoids some duplicate retries; it does not answer whether X may still revoke authority after the intent was written.

Thus `{claim_epoch, effect_id}` in Y is useful evidence, but its semantics must be explicit:

- either it is merely a proposal, in which case effect time still needs a current X authority proof and retains the cross-domain TOCTOU;
- or X atomically turns it into an **irrevocable authorization**, after which later X changes are compensation/new-work semantics, not retroactive revocation.

## Result 3: takeover does not manufacture an idempotency contract

A targeted four-scenario slice has an ambiguous Y request that actually applied, takeover, no dedupe contract, and no intervening X revocation.

- `x_authoritative` duplicates the effect in **4/4**;
- `read_both_then_act` duplicates in 2/4 where no authoritative Y status is available;
- the irrevocable-authorization candidate duplicates 0 because Y consumption is by one durable effect ID with conditional/idempotent semantics.

This repeats the earlier compensation result in a generic claim/effect setting: takeover identity and request identity are separate proofs.

## Result 4: safe cross-domain bridging is possible by changing the authorization point, not by pretending to have cross-domain atomic reads

Within this model, `intent_irrevocable` is safe and resolved in all 192 scenarios because:

1. X atomically verifies the current claim epoch and writes `AUTHORIZED(effect_id)`;
2. that authorization is explicitly non-revocable for this effect ID;
3. Y consumes the effect ID idempotently/conditionally;
4. ambiguous Y responses can be reconciled/retried by the same durable effect identity;
5. later X supersession cannot invalidate an effect that X already authorized.

This is analogous in spirit to the outbox principle of putting the **authorization-producing state transition and durable effect identity together in one transaction**, then delivering downstream separately and idempotently. It is not a distributed transaction across X and Y.

## Candidate protocol

1. Keep revocable claim ownership and irrevocable effect authorization as distinct states.
2. While a claim is `REVOCABLE`, cross-domain fresh reads are advisory only; do not expose an irreversible effect solely on read freshness.
3. At the authorization boundary in domain X, atomically compare current `{task, parent_generation, claim_epoch}` and write a stable `AUTHORIZED(effect_id, effect_contract_digest)` record.
4. After that transition, claim takeover may change who drives delivery but may not revoke or mint a second effect ID for the same authorization.
5. Domain Y consumes `effect_id` via a source-qualified conditional/idempotent contract and records finality independently.
6. If the business contract requires revocation to remain possible until Y application, fail closed unless the sink itself can validate X authority at the same atomic effect boundary.
7. Prefer co-location/outbox-style same-domain authorization when feasible; use the irrevocable capability pattern only when its one-way semantics are acceptable.

## Exact scope limits

- The safe `intent_irrevocable` policy assumes X has an atomic compare-and-authorize primitive and Y has a durable conditional/idempotent effect-ID primitive.
- The model changes semantics at X authorization: later supersession cannot cancel that effect. Applications requiring post-authorization cancellation need a compensation/cancel branch.
- No Byzantine storage, identity collision, sink-side late reversal, or effect-ID retention expiry.
- Counts are equal-weight synthetic mechanisms, not empirical rates.

## Exact Phase-1 continuation

Continue with **authorization cancellation and compensation after irrevocable effect minting**.

Next finite grammar:

- X states `REVOCABLE -> AUTHORIZED(effect_id) -> CANCEL_REQUESTED`;
- Y states `NOT_SEEN / PENDING / APPLIED / FAILED / REVERSED`;
- cancel before Y sees effect vs concurrent with apply vs after apply;
- sink supports atomic cancel-if-pending / compensating reverse / neither;
- ambiguous cancel response and takeover;
- compensation effect has separate identity/idempotency/finality;
- compare `pretend-revocation`, `cancel-if-pending`, `compensate-after-apply`, `manual irreversibility`, and safe archive;
- measure stale cancellation claims, lost authorized effects, duplicate compensation, false terminal cancellation, residual irreversible exposure, and safe terminal coverage.

Keep the Phase-1 frontier nonempty; do not restore unrelated base research while the overlay remains active.
