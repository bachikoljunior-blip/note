# Phase-1 multi_agent checkpoint — static authority cells + ordered multi-cell reservation (Part 32)

## Frozen semantic tuple

- role: `multi_agent`
- frozen note main SHA: `68446d6322630d4ba65d734db1422c50a5782f78`
- sanitized root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport: SHA-only ref lookup + exact-SHA reads
- predecessor: Part 31 / hierarchical range-generation hotspot avoidance
- post-freeze head movement was rechecked; root/config blob identities remained unchanged.

## Selected leaf

Part 31 showed that immutable logical cells remove physical split/merge from correctness, but a spanning predicate still has a multi-object atomicity gap if it merely reads several independent cell epochs. This leaf tests a stronger repository-local protocol: **durable intent + deterministic reservation ID + canonical ordered acquisition of every cell in the predicate cover, with partial acquisition carrying no authority**.

Two finite models were run:

- concurrency/reservation: `4,608` scenario shapes, evaluated across six mechanisms (`27,648` strategy evaluations);
- crash/recovery: `384` scenario shapes.

All counts are equal-weight synthetic mechanism counts, not production rates.

## Public mechanism audit

FoundationDB conflict ranges remain the public precedent for treating a stable logical range as the conflict domain rather than physical shards:
- https://apple.github.io/foundationdb/api-ruby.html
- https://apple.github.io/foundationdb/special-keys.html

PostgreSQL's current locking documentation explicitly recommends acquiring locks on multiple objects in the **same order** to avoid deadlocks. That supports the canonical-order liveness rule used here, but PostgreSQL itself is only a mechanism precedent, not an accepted hosted coordinator for Phase 1:
- https://www.postgresql.org/docs/current/sql-lock.html
- https://www.postgresql.org/docs/17/explicit-locking.html

GitHub's Contents API requires the current blob `sha` for an update and can return `409 Conflict`, so each authority-cell file can provide a per-cell compare point. It still does not document a multi-file atomic transaction; this model deliberately builds the spanning claim from ordered per-cell CAS rather than assuming one:
- https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28

## Model

Logical cells are `0..2`. Claims include three single-cell predicates plus `SPAN01`, `SPAN12`, and `SPAN012`.

Compared mechanisms:

1. one global root;
2. **ancestor-only** mapping to the smallest static hierarchy node, with no ancestor/descendant conflict propagation (negative control);
3. ordered multi-cell reservation that grants too early after a prefix (`ordered_weak`);
4. ordered multi-cell reservation that grants only after the full deterministic cover is held (`ordered_strong`);
5. ideal exact interval lock;
6. complete staged/fenced integrator.

Concurrency timing varies before acquisition, after the first cell, after all cells but before commit, and after commit. Flags vary parent supersession/fencing, same-generation lease expiry/steal, canonical order, and staged-registry completeness.

The crash/recovery model separately varies crash after intent/first/all cells, response loss on early/late cell CAS, repository rate-limit interruption, durable intent, and deterministic reservation identity.

## Common strong concurrency slice

The common slice fixes `parent_fence=true`, `same_generation_expiry=false`, `canonical_order=true`, and `registry_complete=true`; parent supersession still varies. It has `288` scenarios per strategy.

| mechanism | unsafe | false exclusions | blocked | grants | mean proof width | hot-authority touches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| global root | 0 | 60 | 216 | 72 | 1.00 | 288 |
| ancestor-only | 108 | 0 | 48 | 240 | 1.00 | 96 |
| ordered weak | 12 | 0 | 104 | 184 | 1.67 | 144 |
| **ordered strong** | **0** | **0** | 144 | 144 | 1.67 | 144 |
| exact interval lock | 0 | 0 | 156 | 132 | 1.00 | 288 |
| staged integrator | 0 | 0 | 156 | 132 | 1.00 | 288 |

`hot-authority touches` is a relative model metric: global mechanisms touch one shared authority structure on every scenario; ordered cells touch the designated hot cell only when the predicate contains that cell.

### Result 1 — smallest-ancestor identity alone is not a hierarchy protocol

Among `156` overlapping post-acquisition interactions in the common strong slice, ancestor-only mapping blocked only `48`; the other **`108/156` were unsafe** because overlapping predicates could map to different node IDs (for example, a leaf versus its parent span).

So a static hierarchy is not safe merely because every predicate has one canonical node name. Ancestor/descendant conflict must propagate, which either makes writers touch ancestor authority or reduces the problem back to acquiring the concrete intersecting cells.

### Result 2 — ordered cell acquisition closes the spanning-predicate atomicity gap in the tested repository-local scope

`ordered_strong` had **0 unsafe / 288** in the common slice, with no false exclusions. It requires:

- one durable intent containing the **complete expected cell set** before acquisition;
- a deterministic reservation ID;
- cells acquired in one canonical global order;
- partial acquisition marked `PREPARED` only — never authority;
- authority only after every expected cell is held by the same reservation/epoch;
- parent-generation fencing before final grant;
- no same-generation wall-clock expiry/steal while the reservation is live.

The negative `ordered_weak` protocol granted after the first cell. In the clean `after_first` slice with no parent supersession, **6/36** interactions were unsafe because the conflicting actor touched a later cell that the partial claimant did not yet own.

This is the key improvement over Part 31: multi-cell safety does **not** require a multi-file atomic acquisition if each cell individually fences effects and the reservation has no authority until the full set is acquired. The partial state is a recoverable prepare phase, not a terminal claim.

### Result 3 — canonical order is a liveness gate, not a fencing substitute

For two overlapping multi-cell reservations in the toy interleaving, canonical ordering had **0/26 potential deadlocks**. Allowing opposite orders produced **7/26** potential cycles.

This matches PostgreSQL's public guidance to acquire multiple locks in a consistent order. Canonical order does not create safety by itself; it only prevents a class of partial-hold deadlocks once per-cell fencing exists.

### Result 4 — same-generation time expiry reopens stale-owner effects

When an old reservation had acquired every cell and a same-generation wall-clock expiry allowed another claimant to steal an overlapping cell between final ownership and commit, `ordered_strong` became **26/26 unsafe** in that slice.

By contrast, parent supersession is a usable takeover boundary when the old claimant revalidates that parent generation: with parent fencing the supersession slice was **0/72 unsafe**; without it, **72/72 unsafe**.

So the current candidate deliberately does **not** treat time passage as authority. Same-generation abandonment remains a liveness problem rather than weakening the safety fence.

### Result 5 — durable intent and deterministic reservation ID solve distinct recovery failures

Crash after the first/all cells, with no separate transport interruption:

- durable full-set intent: **0/24 orphan, 24/24 resumable**;
- no durable intent: **24/24 orphan/unreconstructible** in this model.

With a durable intent already present, CAS response loss on the first/last cell:

- deterministic reservation ID: **0/12 self-conflict, 12/12 resumable**;
- new/random ID on retry: **12/12 self-conflict, 0/12 resumable**.

For repository rate-limit interruption after the first cell, durable intent + deterministic ID yielded **6/6 safe checkpoints and 6/6 resumable**. Without a durable intent, all `12/12` no-intent variants were orphaned even though checkpointing itself was safe.

Thus `intent` answers *what complete reservation was intended?* while deterministic ID answers *is the ambiguous cell write already mine?*

### Result 6 — global and staged fallbacks remain safe but centralized

The global root had `0` unsafe in the common slice, but falsely excluded **60/60** disjoint post-acquisition interactions and touched the shared authority in all 288 scenarios.

The complete staged integrator also had `0` unsafe, but discarded `156` conflicting staged candidates and serialized authority through one integration point. With an incomplete registry, the corresponding conflict slice was **78/78 unsafe**.

## Candidate repository-local state machine

A zero-hosted-coordination candidate now has this shape:

1. `intent/<reservation_id>` is immutable or CAS-monotone and records parent generation, canonical task/effect identity, full sorted cell set, status, and applied transition ID.
2. Each `cell/<id>` is an independent CAS record with holder reservation ID and monotonic fencing epoch.
3. A claimant acquires cells in sorted order. Any partial prefix is `PREPARED` only.
4. On interruption, a later invocation reconstructs from the intent and readbacks each cell; the same reservation ID makes ambiguous own writes recognizable.
5. Grant is permitted only after every expected cell is current for the same reservation and the parent generation remains current.
6. A newer parent generation may fence/reclaim old cells. Mere wall-clock expiry within the same parent generation may not.
7. External effects still require the sink to respect the reservation fence; that generic sink-side atomicity is unresolved.

## Phase-1 zero-dependency / zero-quota assessment

The tested **repository-local** ordered reservation requires no hosted runner, Codespaces, artifact/LFS/package service, cloud credit, external lock service, or manual user execution. Lightweight repository CAS is only transport/state. The design remains valid when optional monthly/trial/paid compute/storage quotas are zero, and incremental monetary cost is zero under the existing repository connection.

This does **not** close the root problem. Two unresolved children remain:

1. **same-generation abandoned reservation cleanup** — time-based steal was falsified, while permanent locks can harm liveness;
2. **arbitrary protected external sink participation** — this CLEAN role cannot force a sink/router to validate the multi-cell reservation atomically with its effect.

Neither is accepted as a residual handoff.

## Scope limits

- Three logical cells and six predicates; no multidimensional predicates yet.
- The ordered protocol assumes every conflicting effect is guarded by at least one acquired logical cell.
- Same-generation recovery assumes a future scheduled invocation can resume the same deterministic reservation ID from durable intent.
- Parent supersession is modeled as an authoritative generation fence; current-generation explicit cancellation is not yet modeled.
- Counts are mechanism counts, not rates.

## Exact continuation

Next leaf: **same-generation abandoned reservation cleanup**.

Compare:

1. deterministic same-task resume with no expiry;
2. explicit cancel epoch written by current parent authority;
3. parent-generation-only takeover;
4. wall-clock lease expiry;
5. lease expiry plus sink-time cell revalidation;
6. append-only abandonment/cancellation certificate.

Enumerate owner disappearance, scheduler interruption, duplicate task rematerialization, explicit cancellation, late old-owner return, response loss, rate-limit interruption, and external-effect ambiguity.

Primary question: **can scheduled Chat restore liveness for an abandoned current-generation reservation without manual intervention, hosted coordination, or a time-based stale-owner hole?** If not, isolate the minimum additional authority needed and keep it as an unresolved child.
