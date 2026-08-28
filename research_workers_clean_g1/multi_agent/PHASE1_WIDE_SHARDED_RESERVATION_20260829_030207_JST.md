# Phase-1 wide / sharded multi-effect reservation stress test

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- frozen note main SHA: `9ca1695fe221fab5042a26664d1b2dd3a40b93c6`
- frozen root control revision: `20`
- frozen root manifest blob: `d686fb31eb05333bef7853e79c26c3875c937b4c`
- frozen role config revision: `6`
- frozen role config blob: `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- control freshness: SHA-only Git ref lookup was stable at the pre-semantic barrier. After semantic work began, a SHA-only recheck observed main `8cbb88365b3853e717f4da543713c4786200497f`; no newer control/config semantic content was read. New semantic work stopped at that point and only frozen-tuple packaging/persistence continued.
- semantic inputs used: sanitized root manifest revision 20; own role config revision 6; own `LATEST.json`; own immediately preceding Phase-1 checkpoint; official/public DynamoDB, CockroachDB and etcd/Cockroach transaction documentation already opened before the post-barrier head drift; own finite synthetic model. No O/O-derived state, downstream state, other-worker state/config/receipts, shared aggregate ledger, or legacy/pre-independence research was used.

## Leaf objective

Stress the previous leaf's unresolved case where one logical task needs more exclusive-effect claims than one bounded atomic reservation can cover. Compare:

1. one `TransactWriteItems`-style atomic reservation when the whole claim set fits one transaction,
2. deterministic per-shard reservations with only an in-memory complete certificate,
3. a durable reservation-intent plus shard receipts and an explicit committed state,
4. speculative immutable computation plus one fenced authoritative integrator,
5. a negative control that treats each successfully claimed shard as immediate effect authority.

The model separates four questions that must not be collapsed:

- can non-conflicting computation run in parallel,
- can non-conflicting authoritative effects run in parallel,
- can a restart reconstruct whether the *whole* effect set was reserved,
- can any partial reservation authorize an external effect.

## Public mechanism facts used

### Bounded atomic reservation

AWS documents `TransactWriteItems` as an all-or-nothing transaction with up to 100 actions. No two actions may target the same item; tables must be in the same AWS account and Region; aggregate item size is limited to 4 MB. `ClientRequestToken` makes identical requests idempotent for 10 minutes after the first request completes; after that the same token is treated as a new request.

- https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html
- https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Constraints.html

Therefore a single atomic task/effect reservation is a strong primitive only inside its documented scope. A 120-effect task plus reservation/task metadata is intentionally outside the modeled 100-action envelope.

### Conflict/cancellation is whole-transaction, not partial authority

AWS's DynamoDB transaction guidance states that transactions are all-or-nothing and that item contention can cancel/fail a transaction. That is useful precisely because a failed small transaction does not expose a successful prefix as authority.

- https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/BestPractices_PessimisticLocking.html

### TTL is cleanup, not a fencing proof

DynamoDB TTL deletion is asynchronous and can take more than 48 hours; AWS explicitly warns not to rely on TTL deletion for lock records/state management that need prompt stale cleanup.

- https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/data-modeling-blocks.html
- https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html

The model therefore treats lease validity as application metadata checked by the authority path. Physical row deletion is not used as proof that an old claimant cannot act.

### Transaction record + intents is an architectural precedent, not a drop-in guarantee

CockroachDB's public architecture material describes a durable transaction record plus per-key write intents: intents are staged, the transaction record determines committed/aborted visibility, and cleanup can happen later. Its Parallel Commits description goes further: a `STAGING` transaction is only implicitly committed if every listed write can be proven successful with the correct epoch/timestamp; recovery decides commit/abort from the transaction record plus distributed write evidence.

- https://www.cockroachlabs.com/blog/how-cockroachdb-distributes-atomic-transactions/
- https://www.cockroachlabs.com/blog/parallel-commits/

This is used only as a public architectural precedent for separating *prepared shard state* from *commit authority*. It is not claimed that an application-layer reservation record automatically inherits CockroachDB's internal transaction guarantees.

## Finite model

The executable enumerates **3,456** equal-weight synthetic scenarios over:

- effect width: `80` vs `120`,
- relation between two tasks' exclusive-effect sets: disjoint / one-shard overlap / multi-shard overlap,
- synthetic duplicate-item/alias input,
- first write result: success / ambiguous-applied / ambiguous-not-applied,
- API idempotency token fresh vs expired,
- no crash / early crash / crash after all shard attempts but before publication,
- stable parent vs parent supersession after the first unit,
- valid lease vs expiry before publication,
- no shard cancellation vs shard-2 transaction cancellation,
- restart with full local state vs only `reservation_id` persisted.

Counts are mechanism stress counts, not operational incident probabilities. Synthetic aliasing is deliberately balanced and is not a hash-collision estimate.

## Full-lattice comparison

| protocol | safe terminals | unsafe terminals | orphan/unreconstructible reservations | structural blocks | parallel compute admissions | parallel effect admissions | wasted computation units |
|---|---:|---:|---:|---:|---:|---:|---:|
| single atomic `<=100` | 216 | 0 | 0 | **1,728** | 72 | 72 | 0 |
| per-shard + in-memory complete cert | 264 | 0 | **1,680** | 0 | 88 | 88 | 0 |
| durable intent + shard receipts | 432 | 0 | 0 | 0 | 144 | 144 | 0 |
| staged + one fenced integrator | **864** | 0 | 0 | 0 | **288** | **0** | **5,760** |
| NEG: shard-local partial authority | 3,168 terminals | **3,036 unsafe** | 0 | 0 | 44 | 44 | 0 |

The table is deliberately not a scalar ranking. Each protocol pays for a different safety/liveness mechanism.

### What the bounded atomic primitive buys

Inside the 80-effect scope, the reservation marker is in the same all-or-nothing write as the effect claims. That gives the recovery path one durable identity to check after an ambiguous response. In the modeled strong variant there are no partial reservations and no orphan state after recovery/cleanup.

But the exact same primitive is structurally unavailable for every `wide120` scenario: **1,728 / 3,456** lattice cells are outside the one-transaction width. In the nominal wide slice, all three overlap relations are blocked by the bounded atomic candidate while the sharded/intented candidates can proceed.

This is a scope boundary, not evidence that atomic transactions are inferior: when the complete set fits, one atomic reservation is the simplest proof object tested here.

### Bare per-shard reservation loses reconstructibility

The critical discriminator is restart state. A bare deterministic per-shard scheme can be safe while the original worker still remembers the full effect set and all expected shard keys, because it can require a complete certificate before issuing effects. It becomes non-reconstructible when only `reservation_id` survives and no durable record lists the expected shards.

In the **18** wide scenarios with a crash, expired token, stable parent/lease, no hot cancellation, and restart with only `reservation_id`:

- bare per-shard: **0/18 terminal, 18/18 orphan/unreconstructible**,
- durable intent + shards: **18/18 safe terminal, 0 orphan** after 72 modeled recovery reads and 6 modeled recovery writes,
- staged fenced integrator: **18/18 safe terminal, 0 orphan**, but effect publication remains serialized.

In the narrower **6** wide scenarios with an expired idempotency window, ambiguous request result, no crash, and only `reservation_id` persisted:

- bare per-shard: **0/6 terminal, 6/6 orphan/unreconstructible**,
- durable intent + shards: **6/6 safe terminal, 0 orphan**.

The result is not that `reservation_id` is magical. It is only useful if it indexes a durable record containing the exact expected effect/shard contract. Without that contract, observed shard rows cannot prove that no missing shard was intended.

### Partial shard claims are not authority

The negative control issues/authorizes effects as soon as one shard claim succeeds instead of waiting for a whole-reservation proof. It terminalizes 3,168 scenarios, but **3,036 / 3,168 = 95.83%** of those terminal claims are unsafe in this stress lattice. In **1,056** scenarios the same mechanism also admits a duplicate authoritative effect after lease expiry on overlapping effect sets.

Two narrow examples are especially direct:

- parent supersedes after the first shard: negative control is unsafe in **6/6** tested wide reservation-only cases;
- shard-2 transaction is canceled after shard-1 success: negative control is unsafe in **6/6** tested wide full-state cases.

Thus a successful shard reservation is at most a *prepared intent*. It cannot be an external-effect capability until a higher-level proof says the complete logical reservation is current.

### A durable intent fixes restart identity, but not every cross-shard race

The positive `intent+shards` model stores the full canonical effect list/shard map before claiming shards, stores shard receipts under the same `reservation_id`, and allows authority only after all expected receipts are verified and the parent/lease gates are current. This eliminates the restart-orphan cases represented in this finite grammar.

However, this leaf does **not** model an adversarial interleaving in the narrow window:

`verify all shard receipts current -> one shard expires/is taken over -> write root COMMITTED record`.

Therefore the current positive result is exact only for the modeled commit-time observation semantics. It is **not yet** a production proof that a plain application-level root commit record can atomically fence independently expiring shard claims. The next leaf must stress that verification-to-commit race explicitly.

The CockroachDB Parallel Commits architecture is relevant precisely because its `STAGING` state is not treated as committed by name alone; recovery requires proof over the listed writes with the correct transaction epoch/timestamp. That is adjacent evidence for the unresolved gate, not proof of this application protocol.

### Deterministic shard order is a liveness requirement

A separate two-worker/three-shard micro-model enumerates all **36** pairs of shard acquisition permutations under alternating one-key-at-a-time acquisition while claims are held until commit/abort:

- arbitrary independent orders: **24/36 deadlock**, 12/36 both finish,
- one enforced canonical global shard order: **0 deadlock** in the same micro-model.

This is a toy scheduling model, not a production deadlock rate. It demonstrates the hold-and-wait mechanism: if sharded reservation is used, every claimant needs the same total shard order or a protocol that actively aborts/releases partial acquisitions on conflict.

### Same-item canonicalization is required before bounded transactions

DynamoDB forbids two actions against the same item in one transaction. Therefore an effect list must be canonicalized/deduplicated by the *canonical effect identity* before constructing a transaction. Key equality alone is not enough: the stored canonical identity still has to match, so an alias/collision fails closed rather than silently coalescing unrelated effects.

## Current candidate hierarchy

The evidence now supports a capability-ordered protocol rather than one universal claim mechanism:

1. **If the entire canonical task + exclusive-effect claim set fits one documented atomic transaction**, reserve it together with one durable `reservation_id`/marker, parent generation and current claimant epoch. Recover ambiguous responses by reading that marker before retrying.
2. **If the set is wider**, first persist a reservation intent containing the complete canonical effect contract and deterministic shard map. Shard rows are only prepared intents; they carry reservation ID, parent generation, claimant/shard epoch and effect digest.
3. Acquire shard intents in one canonical total order. Cancellation or parent change aborts the root intent and releases/ages out prepared rows; TTL deletion itself is never the fence.
4. Do not authorize effects from partial shard success. A root commit/certificate is necessary, but the exact cross-shard fence between shard verification and root commit remains an unresolved proof obligation from this leaf.
5. If that fence cannot be provided cheaply, preserve parallel speculative computation but serialize authoritative effect issuance through one current fenced integrator. This avoids orphan reservations in the current model but deliberately gives up parallel effect publication and wastes computation on overlapping work.

## Scope limits

- The strong `intent+shards` result assumes the modeled shard-currentness observation is sufficient at commit time; takeover between final verification and root commit is not yet enumerated.
- The model uses three logical shards and one bounded transaction limit; it does not estimate real partition placement or throughput.
- Hot-shard cancellation is a binary mechanism stressor, not a DynamoDB capacity model.
- Global-table cross-Region replication is outside the positive atomic scope; AWS documents transaction ACID guarantees in the Region where the write originates and global replicas can transiently observe partial replication.
- External systems that do not honor the same reservation/fencing metadata are outside scope.
- The staged-integrator positive result assumes a single current authoritative integrator with its own previously tested parent/integrator epoch and persistent integration identity.
- Recovery read/write totals are abstract protocol operations, not provider billing or latency estimates.
- Counts are finite equal-weight synthetic counts, not empirical frequencies.

## Exact Phase-1 continuation

Resolve/freeze the latest sanitized control via SHA-only `refs/heads/main` lookup before any semantic read. If `phase1-clean-multi-agent-concurrency-claims` remains active, continue with the unresolved **cross-shard finality/fencing race** rather than restoring base work.

Next finite grammar:

- root intent states `PENDING / STAGING / COMMITTED / ABORTED`,
- shard receipt states with independent epochs and expiries,
- `verify shard i -> takeover/expiry -> root commit` interleavings,
- integrator/coordinator takeover between verification and commit,
- root-commit response loss and restart with only reservation ID,
- partial cleanup plus a new claimant for an overlapping effect,
- canonical total-order acquisition vs abort-on-conflict,
- hierarchical shard certificates versus sink-time revalidation of every shard,
- a negative control where root `COMMITTED` is trusted without proving the listed shard epochs are still valid,
- a positive candidate inspired only architecturally by transaction-record + intents: commit authority must be derivable from one durable root identity plus exact shard membership/epoch evidence, or fail closed.

Measure false terminalization, duplicate authoritative effect, orphan prepared intents, recovery I/O, safe parallel effect admission, and verification-to-commit race exposure separately. Preserve `staged + one fenced integrator` as the safety fallback/control, not as an assumed throughput optimum.
