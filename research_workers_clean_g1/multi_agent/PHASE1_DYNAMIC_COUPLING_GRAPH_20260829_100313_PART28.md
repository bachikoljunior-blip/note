# Phase-1 multi_agent checkpoint — dynamic coupling graph / activation-time fencing (Part 28)

## Frozen semantic tuple

- role: `multi_agent`
- note main SHA frozen before semantic work: `4a39406ec9aadedac170a39ccb2ed98ae5ba3d57`
- sanitized root: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- own role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport: SHA-only ref lookup + exact-SHA reads
- predecessor own state: Part 27, `LATEST.json` blob `7da9eface7f44bfab11b4443d0138c6bd101608b`
- post-freeze main drift continued, but root/config path/blob metadata remained identical at observed head `885ecccf17feabcbfd0a133a1a8bd55fcea18d2a`. No second semantic config was adopted.

## Selected leaf

Part 27 showed that the minimal safe supersession barrier is the connected component of a static authority-conflict / semantic-coupling graph. This leaf asks whether that component may be computed once, or whether graph membership itself must be fenced at activation time.

## Public-mechanism audit

- etcd transactions atomically guard requests with conjunctions of value/version/revision comparisons; multi-key mutations in one transaction share one store revision:
  https://etcd.io/docs/v3.6/learning/api/
- etcd's revision is a monotonically increasing logical clock over the key-value store, and one transaction that mutates multiple keys receives one revision:
  https://etcd.io/docs/v3.3/learning/api_guarantees/
- ZooKeeper reads expose znode versions and writes are atomic; version checks and multi-operation transactions are public precedents for version-fenced coordination:
  https://zookeeper.apache.org/doc/r3.9.4/zookeeperOver.html
  https://zookeeper.apache.org/doc/r3.8.6/apidocs/zookeeper-server/org/apache/zookeeper/Op.html
- Kubernetes documents optimistic-lock failure for read-then-write replacement when a resource changes between read and write:
  https://v1-34.docs.kubernetes.io/docs/reference/generated/kubernetes-api/v1.25/

These are mechanism precedents only.

## Finite stress grammar

Executable artifact: `research_workers_clean_g1/multi_agent/phase1_dynamic_coupling_graph_20260829_100313_part28.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_dynamic_coupling_graph_20260829_100313_part28.json`

The model enumerates `14,560` equal-weight synthetic scenarios over three resources A/B/C and possible coupling edges AB/BC. It varies:

- plan-time graph: none, AB, BC, or AB+BC;
- one post-plan edge addition/removal or no mutation;
- mutation origin: explicit graph write or task/effect-contract drift;
- whether a global graph epoch update is visible;
- whether that epoch authority covers contract drift;
- per-effect membership-version visibility: both endpoints, left only, right only, or none;
- which subset of resources has absorbing old-authority retirement;
- takeover and response loss;
- availability of sink-side atomic current-component transfer.

Safety for this model means: no **current** coupling edge may connect one resource already activated for g2 to another resource not yet activated for g2.

## Compared mechanisms

1. stale plan-time connected component;
2. per-resource activation with no graph epoch;
3. graph epoch checked only before compensation;
4. global graph epoch revalidated immediately before activation;
5. per-effect membership versions revalidated at activation;
6. vector-wide barrier;
7. sink-side atomic transfer over the **current** connected component.

Weak plan/per-resource mechanisms intentionally lack stable activation identity so takeover/response-loss duplicate exposure is visible.

## Results

Whole lattice:

- stale plan component: unsafe `4,096`, duplicate activation exposure `7,020`.
- per-resource/no epoch: unsafe `7,280`, duplicate activation exposure `10,920`.
- precheck-only epoch: identical to stale plan in this grammar — unsafe `4,096`, duplicate `7,020`.
- global activation-time epoch recheck across all strong and weak epoch variants: unsafe `2,560`.
- per-effect version recheck across all strong and partial/missing version variants: unsafe `2,816`.
- vector barrier: unsafe `0`.
- sink atomic current-component transfer: unsafe `0`.

The aggregate global/per-effect totals deliberately mix valid and invalid epoch implementations; the discriminating slices are below.

### Stale-component falsification

There are `4,096` edge-addition scenarios in which the plan-time component would cross a newly added current coupling edge. Stale plan activation is unsafe in `4,096 / 4,096`. Vector barrier and atomic current-component transfer are `0 / 4,096` unsafe.

### When one global epoch is sufficient

In `5,600` scenarios where the activation-time global epoch is an authoritative mutation witness — no mutation, or the mutation is covered and the changed epoch is visible — activation-time epoch recheck is unsafe in `0 / 5,600`.

So a single monotonic graph epoch **is sufficient for this model only if every coupling-relevant mutation is atomically in its authority domain and the activation compares the current epoch immediately before granting new authority.**

Two negative controls define that condition:

- explicit graph write occurred but epoch visibility lagged: `1,024 / 3,584` unsafe;
- coupling changed because task/effect contract drift was outside the graph epoch authority: `1,024 / 3,584` unsafe.

A graph-file version that can lag the actual edge set, or that excludes task/effect inputs from which edges are derived, is not a fence.

### Per-effect versions

When both endpoints of every changed edge receive their membership/version update atomically, per-effect activation recheck is unsafe in `0 / 3,808`.

When endpoint versions are partial or missing, it is unsafe in `2,816 / 10,752`. In particular, a newly coupled endpoint whose version did not change lets its old plan component activate across a current edge.

Thus per-effect versions are not intrinsically stronger than a truly authoritative global epoch; their safety also depends on atomic coverage of every affected endpoint.

### Liveness under safe graph shrink

A strong global epoch invalidates the entire plan on any graph mutation. On edge-removal scenarios with a visible authoritative epoch, it preserved `0` progress units across `2,688` cases.

Endpoint-local strong versions preserved `512` progress units across `1,792` edge-removal cases because an unaffected component could proceed.

Sink-side current-component transfer preserved `5,120` progress units across `3,584` transfer-capable edge-removal cases.

So per-effect versions/local current-component checks are useful primarily as a **locality/liveness optimization** over an already-safe global fence.

## Mechanism conclusion

The safe hierarchy for this tested scope is:

1. A static component snapshot is insufficient.
2. A pre-compensation graph check is insufficient; the graph can change after it.
3. A single global `coupling_authority_epoch` is sufficient **only** when:
   - every edge addition/removal and every task/effect-contract change that can alter coupling is atomically reflected in the same epoch authority;
   - the epoch is revalidated at activation, not just at planning or compensation start;
   - activation itself uses a stable idempotent identity.
4. Per-effect membership versions can narrow invalidation and improve progress, but must atomically cover every affected endpoint; partial endpoint versioning recreates stale-component failures.
5. If neither global epoch nor endpoint membership can be made authoritative over the actual sink coupling, a sink-side atomic transfer over the current connected component is the cleanest positive primitive; otherwise fail closed.

A useful design name for the global object is **coupling authority epoch**, not merely graph epoch, because its scope must include the semantic inputs from which conflicts are derived.

## Generic residual capability boundary

Chat-capable work for this selected leaf is complete: public audit, finite model, executable checker, result packaging, safety/liveness discrimination, and continuation.

The generic remaining effect is an authoritative activation gate that can atomically compare either:

- one coupling-authority epoch covering all coupling-relevant inputs, or
- current versioned membership for every affected effect key,

and then grant/transfer external authority without a race. Repository evidence can describe and precompute this, but the exposed CLEAN tool surface cannot manufacture an arbitrary external sink's atomic compare-and-grant operation. Classification: `downstream_verification_required`; no global Phase-1 closure is claimed.

## Scope limits

- Three resources; graph only has AB/BC edges.
- No hyperedges or range/predicate conflicts.
- Edge mutation is modeled as one toggle.
- Per-effect versioning assumes explicit endpoint membership records; insertion of a brand-new conflicting key not present in the plan (a phantom) is not yet modeled.
- Atomic current-component transfer is a capability assumption.
- Counts are synthetic mechanism counts.

## Exact continuation

Next Phase-1 leaf: **phantom conflict / predicate insertion during claim acquisition**.

Model a worker that snapshots known effect keys, then a concurrent worker inserts a new effect key whose predicate/range overlaps the first worker without changing any key the first worker read. Compare:

1. per-known-key CAS/version checks;
2. global coupling-authority epoch;
3. range/prefix index epoch;
4. append-only conflict-index generation;
5. serial reservation index / predicate lock;
6. speculative staging + fenced integrator.

Enumerate new-key insertion, delete/recreate name reuse, sharded index lag, takeover, response loss, and ambiguous reservation commit. Primary falsification: even perfect per-key versions cannot detect a **phantom conflicting key** that was absent from the read set. Determine the minimal authority object that prevents this without falling back to a global reservation lock.
