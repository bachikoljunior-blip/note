# Phase-1 claim/effect ABA after GC and key reuse

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic tuple: note main `9c76f42557b6dee420c8ff1f424f66b619465b5f`, root control revision `22`, root blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, role config revision `6`, role blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`.
- semantic inputs: own immediately preceding Phase-1 retention/compaction artifact, public Kubernetes/Redis documentation, and this finite synthetic model only. No other worker/config/receipt/downstream/shared-ledger semantic state was read.

## Leaf objective

Retention/compaction exposed a second GC question: even if old event payloads can be deleted, when can a claim/incarnation witness itself be deleted without creating an ABA problem?

The ABA trace is generic:

`logical key K held by A -> A lease expires / record is GC'd -> K is reused by B -> delayed A result/effect/release arrives -> system mistakes historical A for current B because the mutable name/key looks the same again`.

This leaf compares stable logical keys, per-acquisition tokens, epochs, parent incarnation identity, and immutable staging under deliberate restart/reset and GC failures.

## Public mechanism evidence

Kubernetes explicitly separates **Name** from **UID**. A resource name can be reused after the old object is deleted, while every created object gets a distinct UID intended to distinguish historical occurrences of similar entities. Kubernetes also exposes `resourceVersion`; conditional updates with a stale `resourceVersion` are rejected with `409 Conflict`.

- https://kubernetes.io/docs/concepts/overview/working-with-objects/names/
- https://kubernetes.io/docs/reference/using-api/api-concepts/

This is a useful public analogy for the distinction between a reusable logical task key and an immutable task/parent incarnation.

Redis's official distributed-lock documentation requires the lock value/token to be unique across clients and lock requests, and releases a lock only if the stored token still matches. The reason given is the exact stale-owner trace: A's lock expires, B acquires the same key, and A must not later delete B's lock. The same Redis documentation separately warns that long-running correctness-sensitive work should use **fencing tokens** and should not assume a lock remains owned merely because the original process is still alive.

- https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/
- https://redis.io/docs/latest/commands/set/

A unique random token therefore solves stale **release ownership** only when checked; it does not by itself authorize a delayed result or external effect unless that authoritative sink also checks the current acquisition/incarnation.

## Finite model

The executable enumerates **1,152 equal-weight synthetic scenarios** over:

- delayed stale action: result / external effect / lock release;
- new incarnation B phase: claim live / integrated+claim live / integrated+claim row GC'd;
- acquisition token: unique-per-acquire vs incorrectly reused/key-derived;
- epoch: persistent monotonic vs reset to the same value on restart;
- parent identity: unique new UID vs name-only reuse;
- task spec: same vs drifted under the same human/logical key;
- effect key: same exclusive effect vs disjoint effect;
- old result carries parent UID vs missing incarnation metadata;
- highest-epoch/fence witness retained after GC vs deleted.

Compared policies:

1. `key_only_ttl` — mutable logical key/name plus lease expiry only.
2. `random_token_release_only` — unique token protects lock release, but result/effect sink remains key-only.
3. `current_token_sink` — every authoritative action must present the currently live acquisition token; absence of a live claim fails closed.
4. `epoch_fence` — numeric fencing only; epoch may reset and the retained highest-epoch witness may be GC'd.
5. `incarnation_epoch_token` — parent incarnation + acquisition token + epoch; missing incarnation metadata fails closed and current-incarnation witness persists.
6. `immutable_stage_fenced_integrator` — leaf can only append to immutable incarnation-scoped staging; one current integrator performs authoritative publication/effect; release is token/incarnation checked.

## Main results

| policy | unsafe scenarios | ABA accepts | duplicate authoritative-effect scenarios | stale-result accepts | new-claim deletions |
|---|---:|---:|---:|---:|---:|
| key_only_ttl | **1,024 / 1,152 = 88.89%** | 1,024 | 128 | 384 | 256 |
| random_token_release_only | **896 = 77.78%** | 896 | 128 | 384 | 128 |
| current_token_sink | 384 = 33.33% | 384 | 32 | 128 | 128 |
| epoch_fence | **576 = 50.00%** | 576 | 80 | 224 | 128 |
| incarnation_epoch_token | 64 = 5.56% | 64 | 8 | 24 | 16 |
| immutable_stage_fenced_integrator | **32 = 2.78%** | 32 | **0** | **0** | 32 |

These aggregate rates intentionally include broken identity-generation dimensions. They are not production rates. The important positive-capability slices are below.

## Result 1: a reusable key is not an incarnation

In the 192-scenario `same_key_spec_drift` slice, a historical task has the same logical/display key as B but a different spec.

- key-only TTL: **192 / 192 wrong-spec stale results accepted**;
- release-only token: **192 / 192** (because the token is not checked by result authority);
- epoch-only: 112 / 192;
- current-token sink: 64 / 192, exactly the modeled token-reuse collisions;
- incarnation+epoch+token: 12 / 192, only deeper identity-collision cases;
- immutable staging + current integrator: **0 / 192**.

The candidate therefore keeps `task_key` for logical dedupe/search but binds result authority to a separate immutable `task_incarnation_id` plus task-spec/input/effect-contract digest.

Kubernetes's reusable Name plus distinct lifetime UID is the closest public mechanism analogy used here.

## Result 2: a random lock token protects release only if every authority sink checks it

The release-only token policy halves stale new-lock deletion from 256 to 128 aggregate cases, but does nothing to its 384 stale-result and 128 duplicate-effect cases.

By contrast, in the **576-scenario unique-per-acquisition-token positive slice**, both `current_token_sink` and `incarnation_epoch_token` have **unsafe 0**, and immutable staging/integrator also has unsafe 0. Key-only remains unsafe in 512 cases and release-only remains unsafe in 384.

This sharpens the Redis analogy: compare-and-delete prevents A from deleting B's lock, but a result DB, canonical manifest, payment sink, or other exclusive effect must independently reject A's stale token/incarnation if it can be reached directly.

## Result 3: numeric fencing fails if its domain can reset or its witness is garbage-collected

`epoch_fence` is unsafe in **576 / 1,152 = 50%** overall. In the 576 restart-reset scenarios it is unsafe in **512**. In the `after_claim_gc` slice (384 scenarios), epoch-only is unsafe in **192** because deleting the retained highest-epoch witness lets old epoch 1 become acceptable again.

Even in the **288-scenario unique-incarnation + unique-token** slice, epoch-only has 144 unsafe cases because that policy deliberately ignores those identity fields and relies on a resettable/GC-able numeric fence alone.

Therefore a fencing number is useful only inside a durable, non-rewinding authority domain whose previous maximum cannot silently disappear. If that persistence cannot be proved, pair it with an immutable acquisition/incarnation identity and keep the relevant sink witness beyond claim-row TTL.

## Result 4: after claim-row GC, absence must not mean authority

The `after_claim_gc` slice has 384 scenarios:

- key-only: **256 unsafe / 256 ABA accepts**;
- release-only token: **256 / 256**;
- epoch-only: **192 / 192** when the fence witness is lost;
- current-token sink: **0 / 0** because no live current claim means reject, not "unclaimed so accept";
- immutable staging/integrator: **0 / 0**;
- incarnation+epoch+token: 16 / 16 only in full modeled identity-collision branches.

This is the GC rule: deleting the lease row does not authorize historical messages. The integration/effect sink needs a retained current-incarnation/consumption witness or must fail closed.

## Result 5: all identity layers can be defeated if they are allowed to collide together

The explicit `full_aba_identity_collision` slice combines key-derived token reuse, epoch reset, and parent-name reuse. It contains 144 scenarios. No metadata-based policy can magically distinguish two incarnations when every field it trusts is identical; even the stronger incarnation policy is unsafe in 64 cases and immutable staging has 16 stale-release failures when the release identity collides.

This is not an argument for redundant random fields alone. It is a requirement that at least one authority-controlled identity source have a **non-reuse contract**: server-generated UID/incarnation, unique acquisition token, or a durable monotonic fence domain. The sink must check that source, not just store it cosmetically.

## Current candidate protocol

1. Separate reusable logical `task_key` / `effect_key` from immutable `task_incarnation_id` / `parent_incarnation_id`.
2. Every successful claim acquisition gets a fresh unique `reservation_id` and, where available, a durable monotonic `epoch` scoped to a non-rewinding coordinator domain.
3. Worker result metadata binds `{task_key, task_incarnation_id, parent_incarnation_id, reservation_id, epoch, task_spec_hash, input_digest, effect_contract_digest}`.
4. Lease release is compare-and-delete on the current reservation/incarnation, never `DEL key` / delete-by-name alone.
5. Authoritative result/effect publication performs the same current-incarnation check at the sink. A token that is checked only by lock release is not a fencing mechanism for downstream effects.
6. If the live claim row has been GC'd, a delayed result/effect is rejected unless a retained immutable completion/incarnation witness explicitly authorizes that exact identity. "No row" never means "old result may claim authority." 
7. Keep the last accepted incarnation/trigger witness across raw claim/event GC. Do not reset an epoch counter without simultaneously moving to a new immutable coordinator/incarnation domain that the sink also checks.
8. Prefer immutable incarnation-scoped staging plus one current fenced integrator when leaf workers cannot safely touch the authoritative sink directly.

## Persistence note

The repository stores the source-qualified result and an inspectable compact form of the model. As in the preceding leaf, the locally executed source and repository script are not claimed byte-identical unless repository blob/readback proves it; receipts bind persisted Git blob IDs rather than overstating execution-byte identity.

## Exact Phase-1 continuation

Continue with **when an incarnation/fence witness may itself be garbage-collected**.

Next finite grammar:

- known vs unknown maximum stale-worker lifetime;
- explicit worker cancellation/termination acknowledgement vs best-effort cancel;
- durable queue/redelivery and replay surfaces that can resurrect an old result after process death;
- witness TTL shorter/equal/longer than each stale-writer/replay horizon;
- parent/task incarnation permanently retired vs logical key scheduled for reuse;
- sink has independent durable consumption identity vs relies only on claim witness;
- compactor/GC crash and takeover;
- compare time-only witness TTL, cancel-ack + TTL, source-qualified quiescence certificate, permanent compact terminal witness, and external-sink durable single-use identity;
- measure stale-after-GC acceptance, duplicate effect, false exclusion/storage burden, safe reclamation coverage, and proof dependencies.

Public-source audit target: official delete/precondition/finalizer/UID mechanisms and durable queue retry/redelivery boundaries. The goal is not "retain every claim forever" but to derive the minimum **source-qualified quiescence proof** required before identity evidence can be deleted. Keep a nonempty Phase-1 frontier afterward.
