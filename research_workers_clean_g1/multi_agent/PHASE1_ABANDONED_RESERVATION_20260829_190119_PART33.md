# Phase-1 multi_agent checkpoint — same-generation abandoned reservation cleanup (Part 33)

## Frozen semantic tuple

- role: `multi_agent`
- frozen note main SHA: `68446d6322630d4ba65d734db1422c50a5782f78`
- sanitized root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport: SHA-only ref lookup + exact-SHA reads
- predecessor: Part 32 / static authority cells + ordered multi-cell reservation
- main advanced after the semantic freeze, but exact root/config blobs were rechecked unchanged; no newer semantics were adopted.

## Selected leaf

Part 32 closed the tested spanning-reservation acquisition gap with a durable full-set intent, deterministic reservation ID, canonical cell order, no authority for partial prefixes, and parent-generation fencing. Its unresolved liveness problem was a claimant that disappears in the **same parent generation**. Letting another claimant steal a fully granted reservation merely because a wall-clock lease expired was unsafe.

This leaf separates three reservation phases:

- `PREPARED`: a prefix of cells may be held, but there is **no effect authority**;
- `GRANTED`: every required cell is held and the task may attempt one authorization transition;
- `AUTHORIZED`: an irrevocable effect identity/capability has been durably minted and revocation is too late.

The central candidate is a **task-owned reservation**, not a worker-owned lease: a later scheduled invocation of the same logical task resumes the same deterministic reservation ID. For replacement/cancellation, the post-acquisition authority collapses into one CAS-monotone grant record with competing `GRANTED -> CANCELLED` and `GRANTED -> AUTHORIZED` transitions.

## Public mechanism audit

Kubernetes Lease objects expose `holderIdentity`, `renewTime`, `leaseDurationSeconds`, and `leaseTransitions`, and use the Kubernetes API as a coordination substrate. This is a useful public precedent for separating holder identity, renewal time, and holder transition metadata. It does **not** establish that lease expiration alone fences arbitrary downstream effects:
- https://kubernetes.io/docs/concepts/architecture/leases/
- https://kubernetes.io/docs/reference/kubernetes-api/coordination/lease-v1/

ZooKeeper's official recipes explicitly call out the ambiguous-response case where a sequential ephemeral node may have been created successfully but the client loses the response and cannot infer that from the failed call alone. Its recipes add recovery measures. This is a public precedent for durable/deterministic identity plus readback rather than retrying under a fresh identity:
- https://zookeeper.apache.org/doc/r3.7.2/recipes.html

GitHub's Contents API requires the current file blob `sha` for updating an existing path and can return `409 Conflict`. That supplies a repository-local single-record compare point suitable for the `GRANTED -> CANCELLED | AUTHORIZED` branch, but not a transaction over arbitrary external effects:
- https://docs.github.com/en/rest/repos/contents

## Finite stress models

Executable model: `research_workers_clean_g1/multi_agent/phase1_abandoned_reservation_20260829_190119_part33.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_abandoned_reservation_20260829_190119_part33.json`

The concurrency lattice has `384` scenario shapes and `2,304` mechanism evaluations. It varies:

- phase: `PREPARED / GRANTED / AUTHORIZED`;
- same logical task vs replacement task;
- late return of the old worker;
- cancellation requested or not;
- cancellation-vs-authorization race order;
- repository-atomic effect state vs non-fenced external effect domain;
- staged registry completeness;
- deterministic same-task reservation identity.

Compared mechanisms:

1. expire/steal every phase on timeout;
2. timeout only `PREPARED`, otherwise same-task resume/fail closed;
3. cancellation flag stored separately from the grant authority;
4. one CAS grant record with `CANCELLED` vs `AUTHORIZED` as competing transitions;
5. parent-generation takeover only;
6. complete staged/fenced integrator.

A separate `192`-scenario recovery model varies crash, response loss, rate-limit interruption, durable state, deterministic reservation ID, durable effect ID, and local vs non-fenced external effect domain.

All counts are equal-weight synthetic mechanism counts, not production rates.

## Common strong slice

With complete staged registry and deterministic same-task reservation identity fixed, each mechanism has `96` scenarios:

| mechanism | unsafe | progress | blocked | false block | duplicate | reconcile |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| timeout every phase | 32 | 96 | 0 | 0 | 16 | 0 |
| PREPARED-only timeout | 0 | 64 | 32 | 8 | 0 | 32 |
| separate cancel flag | 16 | 80 | 16 | 0 | 4 | 8 |
| **single grant-record CAS** | **0** | **68** | **28** | **0** | **0** | **36** |
| parent-generation-only | 0 | 48 | 48 | 24 | 0 | 32 |
| complete staged integrator | 0 | 72 | 24 | 0 | 0 | 32 |

The point of the candidate is not maximum raw progress; it distinguishes states where safe cleanup is possible from states where progress must become reconciliation.

### Result 1 — lease expiry is safe only while the reservation has no authority

For a replacement task with a late old owner:

- `PREPARED`: timeout cleanup was `0/8` unsafe;
- `GRANTED`: timeout-and-steal was **`8/8` unsafe**;
- `AUTHORIZED`: timeout-and-steal was **`8/8` unsafe**.

This refines Part 32's blanket negative result. Time may be used as a **garbage-collection trigger for non-authoritative prepare state**. It must not itself become proof that a previously granted or authorized owner can no longer act.

The Kubernetes Lease fields are therefore only a coordination analogy here: lease expiration can decide when to attempt a transition, but a monotonic authority transition/fence must decide whether an old effect is still admissible. citeturn831430search3turn831430search8

### Result 2 — make the reservation belong to the logical task, not the worker process

For the same logical task using the single grant-record mechanism:

- deterministic reservation ID: **0/48 unsafe, 48/48 progress, 0 duplicate**;
- retry under a fresh/random reservation ID: **32/48 unsafe and 48/48 duplicate identities** in the negative control.

A worker disappearance therefore does not need leader takeover semantics if the next scheduled invocation reconstructs the same durable task reservation. The holder process is disposable; the reservation identity is not.

ZooKeeper's documented ambiguous sequential-node creation failure illustrates why recovering the same durable identity is materially different from blindly issuing a new claim after response loss. citeturn831430search0

### Result 3 — cancellation and authorization must race on the same authority record

For a `GRANTED` replacement where cancellation is requested:

- cancellation CAS wins first: `4/4` safely allow the replacement and the old authorization loses;
- authorization CAS wins first: `4/4` safely reject cancellation/replacement and require reconciliation;
- unsafe outcomes: **0/8**.

The protocol therefore treats `CANCELLED` and `AUTHORIZED` as mutually exclusive children of one current `GRANTED` version. If authorization has already won, cancellation is not allowed to pretend it revoked that permission.

A separate cancellation flag did not have this property. In the late-old `GRANTED` replacement slice it was **4/4 unsafe**, because an old worker could already have observed the grant and later act without an atomic cancel-vs-authorize compare.

GitHub's file update endpoint is sufficient as a repository-local **single-record** compare primitive because the current blob `sha` is required and conflicts can yield `409`; this is not a claim of external-effect atomicity. citeturn831430search1

### Result 4 — `AUTHORIZED` is absorbing for revocation

Once `AUTHORIZED` is durably minted, none of timeout, late cancellation, or a replacement task is permitted to revoke it. The safe candidates switch from "take over" to **resume/reconcile the same effect identity**.

This is the same semantic distinction found in earlier capability work: an irrevocable authorization point solves the cancellation race by changing the contract. It does not make a non-idempotent external effect magically exactly-once.

The recovery model makes that boundary explicit:

- `PREPARED` + durable state + deterministic reservation ID: `16/16` resumable;
- `GRANTED` + durable state + deterministic reservation ID: `16/16` resumable;
- `AUTHORIZED` in a repository-atomic/co-located state domain: `16/16` resumable by readback/reconciliation;
- `AUTHORIZED` in a non-fenced external domain, even with durable effect ID: `8/8` fail closed as an unresolved external-effect status problem;
- the same external slice without durable effect ID additionally has `8/8` duplicate-retry risk if it were retried blindly.

So durable effect identity is necessary for reconciliation but not sufficient unless the sink exposes a compatible idempotency/status/fencing contract.

### Result 5 — rate-limit interruption is a checkpoint condition, not a takeover signal

With repository rate-limit interruption forced:

- durable grant/intent record + deterministic reservation identity: all `12/12` checkpoint safely; `10/12` are directly resumable and the remaining `2/12` are the deliberately non-fenced external `AUTHORIZED` cases that fail closed;
- without a durable record: all `24/24` checkpoint safely but are orphan/unreconstructible in this model.

This follows the repository control rule: API throttling is interruption/backoff, never evidence that an owner is dead or that authority may be stolen.

## Candidate repository-local cleanup state machine

The Part 32 ordered multi-cell reservation can now be refined as follows:

1. Create durable `intent/<reservation_id>` with parent generation, canonical task/effect identity, complete sorted cell set, and deterministic reservation ID.
2. Acquire cell records in canonical order. During this phase status is `PREPARED`; no external/canonical effect is authorized.
3. **Only PREPARED prefixes may be lease-expired/reclaimed**. A reclaim increments the affected cell epoch; the old prefix still has no effect authority.
4. After all cells are current for the reservation, CAS one reservation grant record to `GRANTED`.
5. A later invocation of the same logical task resumes the same reservation ID and state.
6. If current parent logic wants to replace a `GRANTED` task, it CASes that same grant record from `GRANTED -> CANCELLED`.
7. The old task can authorize an effect only by CASing the same record `GRANTED -> AUTHORIZED(effect_id)`.
8. Exactly one of cancellation or authorization can win. If authorization wins, cancellation fails and the system reconciles that effect rather than revoking it.
9. Per-cell cleanup after `CANCELLED` can be asynchronous **only if new claimants can prove cancellation safely while stale cell rows remain**. That is the next leaf.

## Phase-1 zero-dependency / zero-quota assessment

The tested repository-local mechanism — PREPARED-only cleanup, deterministic same-task resume, and one grant-record CAS fork — requires no hosted runner, Codespaces, artifact/LFS/package service, external lock coordinator, manual user execution, paid/trial/monthly credits, or incremental monetary spend. Lightweight repository API calls are state transport and may be interrupted/rate-limited; they are not compute.

This is **not global Phase-1 closure**. The remaining generic unresolved child is still arbitrary protected external-effect participation after `AUTHORIZED`: without a sink-native durable effect identity/status/idempotency/fencing contract, repository state cannot prove whether an ambiguous external effect was applied. That remains unresolved rather than being accepted as a richer-mode or user handoff.

## Scope limits

- Three reservation phases and two task relationships only.
- The positive cancellation result assumes `GRANTED`, `CANCELLED`, and `AUTHORIZED` are mutually exclusive states in one CAS authority record.
- `PREPARED` is assumed to authorize no effect at all.
- External-effect ambiguity is intentionally left fail-closed.
- Counts are finite mechanism counts, not observed failure rates.

## Exact continuation

Next leaf: **cancellation/release atomicity after `CANCELLED`**.

Compare:

1. immediate per-cell release;
2. lazy/tombstoned release;
3. per-cell cancellation epoch;
4. one reservation-level `CANCELLED` tombstone that all new claimants consult;
5. staged/fenced integration.

Enumerate partial cell-release crash, response loss, rate-limit interruption, late old `PREPARED/GRANTED` owner return, a new claimant acquiring a subset while stale cell rows remain, cancellation-tombstone rollback/GC, and cell delete/recreate ABA.

Primary question: **can one durable reservation-level cancellation tombstone safely decouple logical revocation from best-effort per-cell cleanup, avoiding both permanent false exclusion and re-admission holes?**
