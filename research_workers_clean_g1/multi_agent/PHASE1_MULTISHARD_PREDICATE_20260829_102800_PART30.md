# Phase-1 multi_agent checkpoint — multi-shard predicate membership / topology fencing (Part 30)

## Frozen semantic tuple

- role: `multi_agent`
- frozen note main SHA: `4a39406ec9aadedac170a39ccb2ed98ae5ba3d57`
- sanitized root: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- own role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport: SHA-only ref lookup + exact-SHA reads
- predecessor: Part 29 / phantom predicate insertion
- post-freeze head drift had already been identity-checked; no newer control/config semantics were adopted.

## Selected leaf

Part 29 found that range/predicate generation, rather than per-known-key CAS, is the smallest local primitive that can fence a brand-new conflicting key. This leaf moves the phantom problem up one layer: the predicate itself is represented by a set of physical index shards, and that shard set can split, merge, or be delete/recreated while a claimant is in flight.

## Public-mechanism audit

- FoundationDB defines conflict detection over **logical key ranges**, not over a client-maintained list of physical storage shards. A read conflict range can cause the transaction to conflict with a later write anywhere in that logical range:
  https://apple.github.io/foundationdb/developer-guide.html
  https://apple.github.io/foundationdb/api-python.html
- FoundationDB's special-key documentation exposes canonical transaction conflict ranges and states that a transaction fails if a concurrent write conflict range intersects its read conflict range. This is a useful precedent for keeping the correctness namespace stable even when storage distribution changes:
  https://apple.github.io/foundationdb/special-keys.html
- TiKV publicly documents that continuous key ranges are divided into Regions and that Regions can split and merge as data size changes. This is a topology precedent only, not a claim about TiKV's transaction proof used here:
  https://tikv.org/docs/6.1/deploy/configure/region-merge/

## Finite stress grammar

Executable model: `research_workers_clean_g1/multi_agent/phase1_multishard_predicate_20260829_102800_part30.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_multishard_predicate_20260829_102800_part30.json`

The model enumerates `12,288` equal-weight synthetic scenarios over predicates initially spanning one, two, or three shards and four mutation classes:

- topology-only split/merge;
- conflicting insertion into an existing shard;
- conflicting insertion into a **new shard created by split**;
- shard delete/recreate ABA.

It also varies mutation timing before/after the last final check, whether a multi-shard descriptor vector can be compared atomically with activation, whether split/merge invalidates the parent descriptor, incarnation-sensitive shard identity, root-range generation coverage/visibility, root-certificate completeness, complete current registry, takeover, and response loss.

Safety means that a conflicting insertion or shard incarnation change after a predicate snapshot must not be authorized from a stale physical shard set.

## Compared mechanisms

1. validate only the physical shards from the initial scan;
2. re-enumerate a canonical shard vector and compare it at final activation;
3. one root range generation covering child membership/content changes;
4. per-shard intent plus root commit certificate;
5. serial logical-predicate reservation;
6. speculative staging plus a complete serial integrator.

Aggregate strategy totals mix positive and deliberately broken variants; slice claims below bind the conditions precisely.

## Results

### A shard-set phantom is real if topology can change without invalidating an observed parent

For `768` scenarios where a conflicting new child shard appears **after** the last check and the split does not invalidate any parent descriptor already in the claimant's compare set, both initial-shard validation and canonical physical-vector validation are unsafe in `768 / 768`.

This is the shard-membership analogue of Part 29's new-key phantom: the new child has no version in the old compare set.

### A root generation is sufficient, but not logically necessary under a stronger atomic descriptor contract

There are `576` conflict scenarios where the final physical-shard vector is compared atomically with authority grant, every topology change invalidates an observed parent descriptor, and shard IDs are incarnation-sensitive. Canonical vector validation is unsafe in `0 / 576`.

Conversely, if the vector check is not atomic with activation and the conflict arrives after that check, it is unsafe in `2,304 / 2,304`.

So a stable root generation is **not logically necessary** if the system can atomically compare the complete descriptor vector and every split/merge is guaranteed to invalidate a member already covered by that vector. That is a very strong multi-object primitive.

The root-generation strong slice is also `0 / 3,072` unsafe, while a missing/uncovered/lagged root is `6,912 / 6,912` unsafe on conflict scenarios. The root causes `768` topology-only false exclusions in the strong slice because any covered topology mutation invalidates the whole range snapshot.

The root therefore serves as a compact membership proof / single compare point, not magic: its safety depends on being in the same authority domain as every membership/content mutation and activation.

### Incarnation still matters at the shard layer

With an atomic descriptor vector and incarnation-sensitive shard identity, delete/recreate is `0 / 384` unsafe. With the same atomic vector but no incarnation-sensitive identity, it is `384 / 384` unsafe. A shard generation that resets on recreate is an ABA hole just like a logical effect key that resets.

### Certificate, reservation, and staged fallbacks

The fail-closed per-shard-intent + root-certificate mechanism is unsafe `0` over the full lattice, but intentionally grants only when root coverage/visibility and all certificate receipts are complete; this model records only `384` progress units and `2,688` topology-only false exclusions.

The serial logical-predicate reservation is unsafe `0` and serializes/blocks all `9,216` conflict attempts. It is the simple safety upper bound.

Staging + complete serial integration is `0` unsafe when the authoritative registry is complete, but wastes `4,608` conflicting staged computations. If the current registry can omit an authoritative shard/effect, it is `4,608 / 4,608` unsafe in the incomplete-registry conflict slice.

## Mechanism conclusion

The critical distinction is between **logical predicate authority** and **physical shard topology**.

A correct protocol has three viable shapes in this tested scope:

1. **Stable logical range conflict domain**: writers to any physical shard in the logical interval conflict with the same predicate reservation/range version. Physical split/merge is not part of the claimant's correctness proof. FoundationDB conflict ranges are the clearest public precedent for this abstraction.
2. **Atomic descriptor-vector compare**: if physical topology is exposed, compare the complete current descriptor vector atomically with authority grant, require every split/merge to invalidate an already covered parent descriptor, and use incarnation-sensitive shard IDs.
3. **Root range generation**: atomically bump one logical root on every child membership/content mutation and compare that root with activation. This compresses a wide vector proof but can create more false invalidation/hotspot pressure.

A plain vector of content generations from the initial physical scan is insufficient. A root generation is not strictly required when the stronger atomic descriptor-vector contract exists, but some stable authority over **membership of the predicate set** is required.

## Generic residual capability boundary

All Chat-capable work for this selected leaf is complete: public audit, finite model, persistence, and exact continuation.

The generic external requirement is that authority-granting writers and topology mutations participate in either a stable logical predicate-conflict domain or an atomic topology-version + authority-grant transaction. This CLEAN role can model and persist the protocol but cannot impose that atomicity on arbitrary protected external sinks/storage routers. Classification: `downstream_verification_required`; no global Phase-1 closure is claimed.

## Scope limits

- Physical topology is abstracted to 1–3 initial shards and four mutation classes.
- A split-without-parent-invalidation case is intentionally a negative control; real systems may guarantee stronger descriptor invalidation.
- Atomic descriptor-vector compare is a capability assumption and may not scale to very wide ranges.
- Logical range reservations are one-dimensional; no multidimensional/resource-budget predicates yet.
- Counts are synthetic mechanism counts.

## Exact continuation

Next non-conflicting Phase-1 leaf: **hierarchical range-generation hotspot avoidance**.

Model many disjoint predicates sharing one global/root epoch and compare global root, fixed range partitions, adaptive split-tree generations, two-level root+leaf epochs, interval/predicate locks, and staging+fenced integrator. Enumerate concurrent non-overlapping claims, range split while claims are active, parent/child generation handoff, hot-leaf contention, response loss, and takeover. Primary question: can a tree of range epochs preserve phantom safety while avoiding the global root's false invalidation, or does changing the tree topology itself require a root epoch that becomes the hotspot again? Measure unsafe phantom admission, false exclusion, serialized conflict surface, proof width, and recovery reads separately.
