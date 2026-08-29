# Phase-1 multi_agent checkpoint — phantom conflict / predicate insertion (Part 29)

## Frozen semantic tuple

- role: `multi_agent`
- frozen note main SHA: `4a39406ec9aadedac170a39ccb2ed98ae5ba3d57`
- sanitized root: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- own role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport: SHA-only ref lookup + exact-SHA reads
- predecessor: Part 28 / dynamic coupling graph
- main moved repeatedly after semantic freeze. A first unique-path create returned `409` because the branch advanced. A SHA-only ref recheck observed `562a09affa55b1d4b3c4d1c3dab5e43e6a19ac70`; exact root/config blob checks remained `347c...` / `9a3e...`, so the unique-path write was retried under the same frozen semantics and succeeded. No new control/config semantics were adopted.

## Selected leaf

Part 28 proved that activation-time versioning must cover the actual coupling authority. This leaf tests a stronger counterexample: a claimant validates every **known** effect key, but a concurrent worker inserts a new overlapping effect key that was absent from the read set. That is a phantom conflict rather than a stale version of a known key.

## Public-mechanism audit

- FoundationDB strict serializability tracks read/write **key ranges**, and explicitly supports read conflict ranges so a concurrent write to a key inside the range can make a transaction conflict even if that exact key was not individually read:
  https://apple.github.io/foundationdb/developer-guide.html
  https://apple.github.io/foundationdb/api-python.html
- PostgreSQL Serializable isolation rejects executions that cannot be serialized; PostgreSQL documentation describes predicate/SIREAD locking as the mechanism for detecting writes that would have changed an earlier query result:
  https://www.postgresql.org/docs/14/transaction-iso.html
  https://www.postgresql.org/docs/18/sql-set-transaction.html
- CockroachDB has publicly described interval/range tracking for scans specifically so a later write to a key that was absent during the scan is still recognized as a read/write conflict:
  https://www.cockroachlabs.com/blog/serializable-lockless-distributed-isolation-cockroachdb/

These are mechanism precedents only; they do not define this repository protocol.

## Finite stress grammar

Executable model: `research_workers_clean_g1/multi_agent/phase1_phantom_conflict_20260829_101520_part29.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_phantom_conflict_20260829_101520_part29.json`

The model enumerates `8,192` equal-weight synthetic scenarios over:

- insertion type: brand-new key or delete/recreate of a logical name;
- whether the inserted effect overlaps the claimant's predicate;
- indexed publication path vs bypass path;
- global coupling epoch visibility;
- range-index epoch visibility and shard completeness;
- append-only conflict-generation visibility and incarnation awareness;
- known-key incarnation-sensitive versioning;
- current registry completeness for a serial integrator;
- takeover, response loss, and ambiguous reservation commit.

Safety in this exact model means: a new overlapping effect key must not gain conflicting authority after a claimant validated a snapshot that omitted it.

## Compared mechanisms

1. per-known-key CAS/version checks;
2. global coupling-authority epoch;
3. range/prefix index epoch;
4. append-only conflict-index generation;
5. serial predicate reservation;
6. speculative staging + fenced integrator/current re-enumeration.

The aggregate strategy totals mix strong and deliberately broken coverage variants. The discriminating slices below are the positive/negative claims.

## Results

### Perfect known-key CAS does not detect a new phantom

For `2,048` overlapping **NEW_KEY** scenarios, per-known-key CAS is unsafe in `2,048 / 2,048`. The inserted key simply has no version in the claimant's read set. The weak baseline also exposes duplicate transition attempts in `1,792 / 2,048` of these takeover/response-loss/ambiguous-retry combinations.

By contrast, delete/recreate of a key that *was* known can be fenced by incarnation-sensitive identity: `0 / 1,024` unsafe in that strong slice. This separates ABA protection from phantom protection.

### Global coupling epoch is sufficient only inside one authority domain

When the insertion path is indexed and the current global epoch update is visible, global epoch revalidation is `0 / 2,048` unsafe. But it invalidates `1,024` non-overlapping indexed scenarios too, because any covered insertion changes the global snapshot.

When an authority-granting writer bypasses that epoch domain, global epoch is unsafe in `2,048 / 4,096` bypass scenarios—the unsafe half is exactly the overlapping half. A global integer is not a fence unless every conflict-relevant insertion is forced to advance it before authority can be granted.

### Range-local epoch is the smallest local positive primitive in this model

For overlapping indexed insertions where the relevant range epoch is visible **and every shard covering the predicate is updated**, range epoch revalidation is `0 / 512` unsafe.

If the range update is missing or only a partial shard is visible, it is unsafe in `1,536 / 1,536`. The locality benefit is real: in the `1,024` indexed+visible non-overlap cases where a global epoch causes false exclusion, the range epoch causes `0` false exclusions.

Thus the local optimization is not "version each known key"; it is "version the predicate/range namespace in which a phantom could appear."

### Append-only generation must be incarnation-aware

A complete visible append-generation slice is `0 / 1,536` unsafe but incurs `768` non-overlap false exclusions because the modeled generation is global. Delete/recreate without incarnation-aware records is `256 / 256` unsafe: an append log keyed only by logical name can collapse ABA semantics.

### Serial predicate reservation and staged integration

The authoritative serial predicate reservation baseline is unsafe `0 / 8,192`; it serializes/blocks the `4,096` truly overlapping attempts. It is the simple safety upper bound, not the concurrency optimum.

Staging + fenced integrator is `0 / 4,096` unsafe when the integrator's current registry is complete, while `2,048` conflicting staged computations are discarded/wasted. If the registry can omit an authoritative effect, the same mechanism is unsafe in `2,048 / 2,048` overlapping incomplete-registry scenarios.

## Mechanism conclusion

A claim protocol must distinguish **point conflicts** from **predicate conflicts**:

- deterministic per-effect keys and incarnation-sensitive CAS solve duplicate/ABA problems for effects that are already in the read set;
- they cannot prove absence of a conflicting key that did not exist when the read set was built;
- preventing such phantoms requires an authority object covering the *set/predicate* itself: a global coupling epoch, a localized range/prefix epoch, or a serial predicate reservation;
- a localized range epoch dominates a global epoch on the tested non-overlap liveness slice, but only if every insertion that could satisfy the predicate atomically updates every relevant range shard;
- an append-only global generation is another safe snapshot invalidator when complete and incarnation-aware, but is coarser;
- staging is safe only when the final integrator re-enumerates a complete authoritative registry.

The minimal positive repository-side shape from this finite model is therefore **predicate/range-generation fencing plus stable transition identity**, not per-known-key CAS alone.

## Generic residual capability boundary

All selected-leaf Chat-capable predecessors are complete: public audit, executable finite falsification, artifact persistence, conflict recovery, and exact continuation.

The remaining generic authority condition is that **every external authority-granting insertion capable of satisfying an overlapping predicate must participate atomically in the same predicate/range-generation or reservation domain that the claimant validates at activation**. Repository-local state can represent such an index, but this CLEAN role cannot force an arbitrary external sink/bypass writer to obey it or manufacture a protected sink-side predicate lock. Classification: `downstream_verification_required`. No global Phase-1 closure is claimed.

## Scope limits

- One claimant predicate and one concurrent insertion per scenario.
- Range overlap is boolean; no interval geometry or hyperrectangles.
- The range-index strong slice assumes all relevant shards are atomically/currently visible.
- The serial predicate reservation baseline assumes every authority-granting writer participates.
- The staged-integrator positive slice assumes a complete registry.
- Counts are synthetic equal-weight mechanism cases, not production failure rates.

## Exact continuation

Next non-conflicting Phase-1 leaf: **multi-shard predicate generation and boundary-crossing overlap**.

Model interval predicates that span 1–3 index shards, concurrent insertions at shard boundaries, split/merge of index shards, and range-generation propagation. Compare:

1. validate only shards observed by the initial scan;
2. canonical range decomposition + all-shard generation vector;
3. one root generation that atomically covers all child shards;
4. per-shard intent + root commit certificate;
5. serial predicate reservation;
6. staging + complete fenced integrator.

Enumerate shard split after snapshot, boundary-key insertion, partial generation update, root/shard response loss, takeover, and delete/recreate of a shard ID. Primary falsification: a range may acquire a **new shard** after the claimant snapshots the old shard set, recreating the phantom problem one level above the effect keys. Determine whether a stable root range-generation is necessary to validate the membership of the shard set itself.
