# Phase-1 multi_agent checkpoint — hierarchical range-generation hotspot avoidance (Part 31)

## Frozen semantic tuple

- role: `multi_agent`
- frozen note main SHA: `68446d6322630d4ba65d734db1422c50a5782f78`
- sanitized root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport: SHA-only ref lookup + exact-SHA reads
- predecessor: Part 30 / multi-shard predicate membership and topology fencing
- post-freeze head movement was observed, but root/config blob identities remained unchanged; no newer semantics were adopted.

## Selected leaf

Part 30 left a specific question: can hierarchical range epochs preserve phantom safety while avoiding a global root's false invalidation and coordination hotspot, or does tree topology change force every claimant back through one root epoch?

This leaf compares six mechanisms over a finite grammar:

1. one global root generation;
2. immutable fixed logical partitions;
3. adaptive local tree descriptors with monotonic lineage invalidation + retained tombstones;
4. two-level global topology root + local leaf generations;
5. exact logical interval/predicate lock;
6. speculative staging + one complete fenced integrator.

The model contains `55,296` equal-weight scenarios and `331,776` strategy evaluations. Counts below are synthetic mechanism counts, not production probabilities.

## Public mechanism audit

FoundationDB exposes read/write **conflict ranges** over logical key intervals. A write anywhere in a transaction's read conflict range can cause commit conflict, which is a public precedent for keeping correctness in a stable logical range namespace rather than a client-maintained physical shard list:
- https://apple.github.io/foundationdb/api-ruby.html
- https://apple.github.io/foundationdb/special-keys.html
- https://apple.github.io/foundationdb/read-write-path.html

PostgreSQL Serializable uses predicate locking; its documentation also notes that finer-grained predicate locks may be combined into coarser page/relation locks and that coarse promotion can increase serialization failures. This is a direct public example of the safety-vs-false-conflict trade-off from coarsening:
- https://www.postgresql.org/docs/15/transaction-iso.html

TiKV documents continuous key ranges being split into and merged from Regions, so physical range topology is a real mutable implementation layer and should not automatically become the correctness namespace:
- https://tikv.org/docs/6.1/deploy/configure/region-merge/

For repository transport, GitHub's Contents API requires the current blob `sha` when updating an existing file and can return `409 Conflict`; that gives a per-path compare point, not a documented multi-path atomic compare:
- https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28

## Stress grammar

Claims cover four single logical leaves (`L0..L3`) plus two spanning predicates (`SPAN01`, `SPAN12`).

Events include:
- content write in each leaf;
- topology-only split in each leaf;
- split plus conflicting insertion in each leaf;
- topology-only merge of each adjacent pair;
- merge plus conflicting insertion of each adjacent pair.

Each event happens either before the claimant's final snapshot/check or after that check but before authority grant.

Binary controls vary:
- root visibility/currentness;
- whether topology replacement invalidates an overlapping prior descriptor;
- whether replaced descriptors remain retained as fencing tombstones;
- whether a multi-descriptor compare is atomic with grant;
- registry completeness for the staged integrator;
- durable transition/integration identity;
- response loss;
- integrator/claim takeover.

## Common strong semantic slice

A common slice fixes all strong prerequisites (`root_visible`, lineage invalidation, retained tombstones, atomic multi-compare, complete registry, durable ID) and removes response-loss/takeover so the concurrency shape can be compared directly. It contains `216` scenarios per strategy.

| mechanism | unsafe | false exclusions | blocked/serialized | grants | mean proof width | synthetic hot-authority touches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| global root | 0 | 81 | 108 | 108 | 1.00 | 216 |
| fixed logical partitions | 0 | 0 | 27 | 189 | 1.33 | 72 |
| adaptive lineage | 0 | 19 | 46 | 170 | 1.33 | 72 |
| global topology root + leaf | 0 | 65 | 92 | 124 | 2.33 | 216 |
| exact interval lock | 0 | 0 | 27 | 189 | 1.00 | 216 |
| complete staged integrator | 0 | 0 | 27 | 189 | 1.00 | 216 |

`hot-authority touches` is only a relative model metric: global mechanisms touch one shared authority object in every scenario; fixed/adaptive mechanisms touch the designated hot leaf authority only when the claim includes that leaf.

### Result 1 — a global root is not logically required

In the common strong slice, immutable fixed partitions and adaptive lineage both had `0` unsafe admissions while touching the designated hot authority `72/216` times instead of `216/216` for the global-root and root+leaf designs.

The important conditions differ:

- **fixed logical partitions** make physical split/merge irrelevant to correctness; a conflicting insertion always maps to a stable logical partition epoch;
- **adaptive lineage** permits local topology change, but the replaced logical descriptor must be monotonically invalidated and remain queryable as a fencing tombstone.

For after-check topology conflicts, adaptive lineage was safe `0/19` only when both lineage invalidation and tombstone retention were present. Dropping either condition made the same slice `19/19` unsafe.

So the root can be removed only by moving the invariant elsewhere; local topology nodes must themselves form a durable, non-ABA authority lineage.

### Result 2 — immutable logical partitions dominate topology churn in this abstraction

For `81` after-check events that are not semantic conflicts with the claimant, the global root falsely excluded `81/81`; root+leaf excluded `65/81`; adaptive lineage excluded `19/81` because an overlapping topology-only rewrite invalidates the local descriptor.

Fixed logical partitions, exact interval locking, and complete staged integration had `0/81` false exclusions in this slice.

This supports a stronger architectural preference than "use a finer tree": **keep the correctness partition stable and hide physical split/merge below it whenever possible**. A mutable correctness tree is still safer than one global root when properly fenced, but it pays avoidable topology invalidations.

### Result 3 — spanning predicates expose the next atomicity gap

Fixed logical partitions are safe for a single-cell claim because one cell epoch can be compared with grant. For spanning predicates after a conflicting write, the strong atomic multi-cell compare slice was `0/13` unsafe, while the same slice without atomic multi-cell compare was `13/13` unsafe.

Therefore per-cell CAS alone is not a complete protocol for predicates that cross authority cells. The proof must either:
- map the predicate to one stable coarser authority cell;
- atomically compare the deterministic cover with grant;
- or defer authoritative publication to a serial/fenced integration point.

GitHub Contents API's per-path `sha` compare is useful for single authority files but does not, by itself, provide the missing multi-path compare-and-grant primitive.

### Result 4 — root visibility and registry completeness remain hard gates

For topology conflicts after the final check, root+leaf was `0/19` unsafe when the topology root was current/visible and `19/19` unsafe when it was not.

For staged integration, conflicting staged candidates were safely discarded `27/27` with a complete current registry; an incomplete registry admitted `27/27` unsafely.

Thus a global root or serial integrator is not a magic escape hatch: its own currentness/completeness is part of the proof.

### Result 5 — response loss still requires durable effect identity

With all other strong prerequisites present and response loss forced, every strategy had zero duplicate-retry possibility when a durable transition/integration ID was retained. Removing that ID made every granted ambiguous case a possible duplicate retry:
- global root `108/108`;
- fixed partitions `189/189`;
- adaptive lineage `170/170`;
- root+leaf `124/124`;
- interval lock `189/189`;
- staged integrator `189/189`.

This is the same separation seen in earlier leaves: conflict fencing and crash reconciliation are different obligations.

## Phase-1 zero-dependency / zero-quota assessment

A **repository-local, single-partition claim cell** can be represented with ordinary repository state and per-file current-blob CAS. That submechanism needs no hosted runner, Codespaces, artifact/LFS/package service, external coordinator, manual user execution, paid/trial/monthly credit, or incremental monetary spend. Repository API rate limits are treated as interruption/backoff conditions, not compute.

However, this is **not global Phase-1 closure**. Two unresolved children remain:

1. **multi-partition atomicity** — simple per-path Contents CAS does not supply an atomic compare-and-grant across a spanning logical predicate;
2. **external effect participation** — this CLEAN role cannot force an arbitrary protected sink/router to apply the same fencing predicate atomically with its effect.

Those are unresolved child problems, not accepted handoffs.

## Scope limits

- Four logical leaves, two spanning predicates, and local split/merge events only.
- Adaptive lineage assumes a replacement can atomically invalidate its old descriptor before/with becoming authoritative and that tombstones are not later garbage-collected unsafely.
- `hot-authority touches` is a relative synthetic contention surface, not a throughput benchmark.
- Interval locking is treated as a semantic ideal; a hosted lock manager would violate the Phase-1 zero-dependency rule.
- Repository transport is modeled only as lightweight state transport, not as compute.

## Exact continuation

Next leaf: **static hierarchical authority-cell cover**.

Keep the correctness topology immutable and map each predicate to one canonical authority cell, or to a small deterministic cover, so physical split/merge remains outside correctness. Compare:

1. leaf-only per-cell CAS;
2. one common-ancestor authority cell;
3. deterministic multi-cell reservation in canonical order;
4. immutable reservation intent + per-cell receipts + complete certificate;
5. staged candidate + fenced serial integrator.

Enumerate predicates covering 1/2/3 cells, concurrent disjoint descendants under the same ancestor, cross-cell overlaps, partial reservation success, response loss, takeover, and repository rate-limit interruption.

Primary question: **can a static hierarchy avoid both global-root invalidation and the multi-object atomicity gap without a hosted coordinator?** Measure unsafe admission, false exclusion, proof width, recovery reads, and authority-file hotspot concentration separately.
