# Phase-1 logical-effect claim-key granularity and sharded reservation stress test

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- packaging clock observation: `2026-08-29T02:05:00+09:00`
- frozen root control revision: `20`
- frozen root manifest blob: `d686fb31eb05333bef7853e79c26c3875c937b4c`
- frozen role config revision: `6`
- frozen role config blob: `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- pre-semantic root/config freshness: both files were fetched twice from default `main` before the first own-state/public-source semantic read and both blob identities were unchanged.
- head-SHA freshness transport defect: a SHA-only ref action was not discovered until after semantic work had begun, so the exact pre-barrier `note_main_sha` is unavailable for this invocation. This run therefore does **not** claim full compliance with the configured SHA-pinned freshness proof. The first later clean ref-object read observed `c30dbf0fbe76a994bda429b178e78eae56369399`; no newer semantic control was read or adopted after the barrier.
- semantic inputs used: sanitized root manifest revision 20; own role config revision 6; own `LATEST.json`; own immediately preceding Phase-1 checkpoint; official public AWS DynamoDB and Kubernetes Lease documentation; own finite synthetic model. No O/O-derived state, downstream state, other worker state/config/receipts, shared aggregate ledger, or legacy/pre-independence research was used.

## Leaf objective

Compare claim granularity for two workers without sharing semantic solution content:

1. one coarse global claim,
2. deterministic per-task claim keys,
3. deterministic per-exclusive-effect claim keys,
4. task-key + effect-key two-level reservation, and
5. immutable result staging + one current-parent/current-effect fenced integrator.

The key question is whether a claim namespace prevents duplicate *computation*, prevents duplicate *authoritative effects*, and still admits non-conflicting work in parallel. These are treated as different metrics.

## Public mechanism facts used

### Conditional first-claim

DynamoDB `PutItem` supports a conditional create with `attribute_not_exists(partition_key)` so a new item is added only if the same key does not already exist:

- https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_PutItem.html

This is a concrete public primitive for an atomic first reservation on one deterministic claim key. It does not by itself define task identity, effect identity, expiry, takeover, or sink fencing.

### Atomic multi-key reservation and retry scope

DynamoDB `TransactWriteItems` groups up to 100 item actions and completes them atomically: all succeed or all fail. Conditional checks can reject the entire transaction. Its `ClientRequestToken` makes identical calls idempotent only for a documented 10-minute window; after that, the same token is treated as a new request, and changing parameters within the window produces `IdempotentParameterMismatch`:

- https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html

This is a concrete candidate primitive for acquiring one task claim plus every exclusive-effect claim in one reservation **when all required claim items fit the documented transaction scope**. The positive result below assumes this all-or-nothing property; it does not generalize to multi-shard or >100-key reservation.

### TTL is not lease deletion

AWS documents DynamoDB TTL deletion as asynchronous and explicitly says not to rely on TTL deletes for lock records/state management when stale data must be cleaned up in less than 48 hours:

- https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/data-modeling-blocks.html

Therefore the candidate protocol treats `expires_at` as application-level lease metadata checked by conditional takeover, not as a promise that the claim row has physically disappeared.

### Holder transitions are separate metadata

Kubernetes Lease exposes `holderIdentity`, `leaseDurationSeconds`, `renewTime`, and `leaseTransitions` (the number of holder transitions):

- https://kubernetes.io/docs/reference/kubernetes-api/coordination/lease-v1/

This is used only as a public analogy that holder identity, expiry/renewal, and takeover generation are distinct fields. The test does **not** claim that Kubernetes `leaseTransitions` is automatically a fencing token for arbitrary downstream effects.

## Candidate claim record

A claim record needs more than a Boolean `claimed=true`:

- deterministic claim key scoped by claim kind and authority domain,
- canonical task/effect identity stored alongside the key,
- `parent_generation`,
- holder/attempt identity,
- monotonic takeover `epoch`,
- `reservation_id` shared by all rows in one multi-key reservation,
- application `expires_at`,
- task/effect contract digest,
- result/staging digest if a result is later bound to the claim.

If a deterministic hash/key aliases a different canonical identity, the record is treated as a collision/alias and fails closed; the authoritative sink never treats claim-key equality as proof that the logical identities are equal.

## Finite model

The companion executable enumerates **3,840** equal-weight synthetic scenarios over:

- task relation: exact same task; spec drift under the same display name; independent task,
- effect relation: no exclusive effect; same effect; overlapping multi-effect sets; disjoint effects,
- synthetic task-key alias/collision flag,
- synthetic effect-key alias/collision flag,
- first claim outcome: `ok / ambiguous-applied / ambiguous-not-applied`,
- restart with lost caller-local state,
- simultaneous vs later first attempt,
- lease expiry before integration,
- takeover after expiry,
- parent supersession before integration.

Synthetic alias flags are deliberately balanced at 50%; they are mechanism stressors and **not** cryptographic collision-rate estimates. Counts below are not operational incident probabilities.

Every positive claim-based protocol uses two independent integration gates: current parent generation and current claim epoch/reservation. An expired/taken-over holder may leave immutable staging output but cannot authorize canonical integration.

## Main comparison

Across the full 3,840-scenario stress lattice:

| protocol | safe parallel admissions | false parallel exclusions | duplicate computation | duplicate logical integration | duplicate authoritative effect | stale result acceptance |
|---|---:|---:|---:|---:|---:|---:|
| global claim | 0 | 768 | 192 | 0 | 0 | 0 |
| per-task key | 384 | 384 | 192 | 0 | **192** | 0 |
| per-effect keys | 576 | 192 | 480 | **192** | 0 | 0 |
| task+effect two-level | 288 | 480 | 192 | 0 | 0 | 0 |
| staged + fenced integrator | **768** | **0** | **768** | 0 | 0 | 0 |

The raw alias-lattice liveness numbers should not be read as production rates. They make the tradeoff visible:

- a global claim preserves safety but excludes every simultaneous non-conflicting pair;
- a task key deduplicates one logical task but does not arbitrate exclusive effects shared by different tasks;
- effect keys prevent shared-effect duplication but cannot deduplicate same read-only/no-effect work;
- two-level reservation covers both semantics but can false-exclude if either key namespace aliases;
- staged integration preserves authoritative safety and maximal leaf parallelism in this model, but deliberately pays the highest duplicate-computation cost.

## Collision-free sublattice

On the **960** scenarios where task/effect claim keys do not synthetically alias, there are 192 simultaneous non-conflicting parallel opportunities. Admission is:

- global: **0 / 192**,
- task key: **192 / 192**,
- effect keys: **192 / 192**,
- two-level: **192 / 192**,
- staged integrator: **192 / 192**.

But the safety/computation distinctions remain:

- per-task claims still create **96** duplicate-authoritative-effect cases because distinct tasks can share effects;
- effect-only claims create **48** duplicate logical integrations in the clean sublattice because same read-only work has no effect key to claim;
- two-level reservation has zero duplicate authoritative effects and zero duplicate logical integration in this finite model;
- staged integration also has zero duplicate authoritative/logical integration but computes duplicate same-task work more often.

## Exact discriminating slices

### Task identity is not effect authority

For 96 current-parent, unexpired, collision-free scenarios where two **different** tasks share the same/overlapping exclusive effect set:

- per-task key: **96 / 96 duplicate authoritative effects**,
- global: 0,
- per-effect keys: 0,
- two-level: 0,
- staged fenced integrator: 0.

Therefore `task_key` and `effect_key` are non-substitutable proof obligations.

### Effect identity is not duplicate-work identity

For 24 current-parent, unexpired, collision-free scenarios where two workers execute the **same read-only/no-exclusive-effect task**:

- effect-only claims: **24 / 24 duplicate computations** and **24 / 24 duplicate logical integrations**,
- task-key: 0 duplicate computation/integration,
- two-level: 0 duplicate computation/integration,
- global: 0 duplicate computation/integration,
- staged integrator: 24 / 24 duplicate computations but 0 duplicate logical integrations.

Thus effect reservation can protect authoritative side effects while still wasting pure computation unless a logical task identity is also claimed or deduplicated at integration.

### Display name is not a task identity

For 24 clean current scenarios with task-spec drift under the **same human-readable display name** and no conflicting effects, a name-only task claim false-excludes parallel work in **24 / 24** cases. Canonical task identity must include the actual task spec/input contract rather than presentation name alone.

### Lease expiry without epoch fencing is unsafe

In a 12-scenario clean slice where one worker's two-level lease expires, another worker takes over the same task/effect reservation, and the parent remains current, a negative control that still accepts the old holder's result produces:

- stale result acceptance: **12 / 12**,
- duplicate logical integration: **12 / 12**,
- duplicate authoritative effect: **12 / 12**.

This is the direct stale-owner counterexample. Expiry/takeover permits recomputation; only current epoch/reservation checks at the authoritative sink prevent the old computation from becoming a second effect.

## Ambiguous claim write / restart rule

For claim-based protocols, an ambiguous claim response or restart with lost local memory does not authorize a blind new claim. The candidate first reads durable claim state and matches the `reservation_id`/identity/epoch. DynamoDB's `ClientRequestToken` can make an identical transaction retry idempotent within its documented 10-minute window, but the protocol does not elevate that temporary API retry window into long-lived claim authority. After the window, or if the token is unavailable, durable claim state plus fencing is the recovery source.

## Recommended generic protocol from this leaf

1. Derive a **canonical task identity** from the full task spec/input contract, not display name.
2. Enumerate the task's **exclusive effect identities** separately from task identity.
3. If the set fits one atomic transaction, reserve `{task_key + all exclusive effect keys}` with one `reservation_id`, current `parent_generation`, holder, epoch, and conditional expiry/takeover rules.
4. Store canonical identities in the claim rows; key alias/mismatch fails closed rather than sharing authority.
5. Treat TTL/background deletion only as cleanup. Lease validity comes from explicit timestamps/epoch under conditional mutation.
6. On ambiguous claim response/restart, read durable reservation state before retry. Reuse an API idempotency token only inside its exact provider window and with unchanged payload.
7. Workers write only immutable/namespaced staged results.
8. Canonical integration rechecks current parent generation, current reservation/epoch, task identity, effect identity, and result digest.
9. If atomic reservation cannot cover the effect set, do **not** silently degrade to independent per-key leases; route to a wider coordinator or keep leaf work speculative and let one fenced integrator serialize authority.

## Scope limits

- The positive effect/two-level result assumes all required claim keys are acquired atomically. Partial cross-shard acquisition is not covered.
- The DynamoDB transaction mechanism is same-account/same-Region and up to 100 actions; larger/cross-Region reservation needs another protocol.
- Key collision flags are synthetic aliasing stressors. No cryptographic failure probability is estimated.
- The model treats canonical task/effect identity as exact at the authoritative sink and does not model malicious second-preimage attacks against the full identity representation.
- Network partitions, clock skew bounds, hot-partition throughput, transaction cancellation backoff, and cross-store external effects are outside this leaf.
- The model assumes task-level authoritative integration is all-or-nothing for a staged result; partial-effect tasks need a richer effect-vector model.
- Counts are finite equal-weight mechanism counts, not empirical frequencies.

## Exact Phase-1 continuation

Resolve/freeze the latest sanitized control using the now-discovered SHA-only Git ref endpoint **before** any semantic read. If `phase1-clean-multi-agent-concurrency-claims` remains active, continue with **wide / sharded multi-effect reservation**:

- compare one `TransactWriteItems`-style atomic reservation (within one store scope) against deterministic per-shard reservations, reservation-intent + shard commits, and speculative immutable staging + one fenced integrator;
- enumerate >100 effect keys, cross-shard overlap, same-item transaction prohibition, transaction cancellation/conflict, partial shard success, crash between shard reservations, parent supersession mid-reservation, claim-key alias recovery, hot-shard contention, expiry clock skew, ambiguous response after idempotency-token expiry, and restart with only `reservation_id` persisted;
- measure duplicate computation, duplicate authoritative effect, orphan reservation, false exclusion, recovery reads/writes, and safe parallel admission separately;
- require a negative control where partial shard claims are mistakenly treated as authority and a positive control where only a complete reservation certificate or fenced integrator can authorize effects.

Do not restore the base research objective while the Phase-1 overlay remains active.
