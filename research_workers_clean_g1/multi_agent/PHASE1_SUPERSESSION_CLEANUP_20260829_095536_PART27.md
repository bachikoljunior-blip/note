# Phase-1 multi_agent checkpoint — supersession cleanup / coupling-aware retirement barrier (Part 27)

## Frozen semantic tuple

- role: `multi_agent`
- frozen note main SHA: `4a39406ec9aadedac170a39ccb2ed98ae5ba3d57`
- sanitized root: `automation_control/DESIRED_STATE.json`, parsed control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- own role config: `automation_control/roles/multi_agent.json`, parsed config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport: SHA-only ref lookup + exact-SHA reads
- bootstrap validity: two SHA-only `refs/heads/main` lookups matched before the first role-local/public semantic read.
- own starting state: `LATEST.json` blob `485998765a9ce30a26401e1ada2dcf6870e834da`, pointing to Part 26.
- post-freeze head drift was observed to `68a98f3c60b7f80b2fa0898b0eada457723e5a52`; sanitized root blob and own role-config blob were rechecked by path/blob metadata and remained identical. No newer control/config semantics were adopted.

## Assignment / selected leaf

Phase-1 task: `phase1-clean-multi-agent-concurrency-claims`.

Part-26 continuation asked whether changed-contract g1 effects can be retired per component while unchanged components are adopted, or whether supersession requires a vector-wide barrier. This leaf adds a semantic coupling bit between two changed resources and tests a third option: barrier only the connected component of the conflict/coupling graph.

## Public-mechanism audit

1. Kubernetes finalizers keep an object in a terminating state until cleanup conditions are satisfied, and the docs warn against removing finalizers before their purpose is complete. This is a public example of cleanup-before-finalization rather than treating cleanup request acceptance as finality:
   https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/
2. Kafka producer fencing shows a sink-side epoch mechanism where a newer producer instance with the same transactional identity prevents the older one from continuing transactional requests:
   https://kafka.apache.org/42/javadoc/org/apache/kafka/common/errors/ProducerFencedException.html
3. AWS Saga guidance says participants must be idempotent and that Saga does not provide transaction isolation; semantic locking is recommended for concurrent orchestration:
   https://docs.aws.amazon.com/en_en/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html
4. Azure's compensating-transaction guidance states compensation can itself fail, should be resumable/idempotent, and irreversible steps should occur only after critical validation:
   https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction
5. Azure's Saga guidance distinguishes compensable work from a pivot / point-of-no-return and retryable work:
   https://learn.microsoft.com/en-us/azure/architecture/patterns/saga

These are mechanism analogies, not claims that any one system directly implements this repository protocol.

## Finite stress grammar

Executable artifact: `research_workers_clean_g1/multi_agent/phase1_supersession_cleanup_20260829_095536_part27.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_supersession_cleanup_20260829_095536_part27.json`

The script enumerates 13,824 equal-weight synthetic scenarios over:

- resource A/B contract relation: `UNCHANGED` or `CHANGED`, excluding the all-unchanged case;
- old proof: `ABSORBING`, `CURRENT_ONLY`, or `ACTIVE`;
- changed-effect retirement outcome: `FINAL`, `AMBIGUOUS`, `FAILED`, or `LATE_REVERSAL`;
- coupling: `INDEPENDENT` or `COUPLED`;
- early g2 creation before retirement finality;
- coordinator takeover;
- response loss;
- availability of a no-business-effect reseal/finality capability;
- availability of an atomic old->new authority transfer capability.

Counts are finite mechanism-lattice counts, not production failure probabilities.

Safety for this exact model means:

1. no changed-contract g2 authority is live while the conflicting g1 authority can still revive;
2. for coupled changed resources, no mixed logical generation is exposed unless the coupling contract explicitly permits it;
3. response loss/takeover must not create duplicate compensating business effects.

## Compared mechanisms

- `blind_changed`: adopt what looks reusable, then execute changed g2 while g1 is still live.
- `weak_compensate_retry`: retry compensation on takeover/response loss and treat apparent completion as final without an absorbing fence.
- `vector_retire_then_activate`: retire every changed resource, then activate the whole vector.
- `per_component_retire_then_activate`: independently retire/activate each resource.
- `graph_barrier`: independent resources use per-component transition; coupled changed resources form one atomic activation barrier.
- `atomic_group_transfer`: when the sink exposes a group transfer capability, revoke old authority and grant new authority in one coupling-group operation.

## Results

Overall:

- `blind_changed`: unsafe `13,824 / 13,824`; all 13,824 terminal states were unsafe. It also duplicated unchanged authority in 2,304 scenarios where an absorbing adoption proof was unavailable.
- `weak_compensate_retry`: unsafe `9,216 / 13,824`; unsafe terminal `6,720`; duplicate compensation exposure in `9,072` scenarios. Main failure reasons were early g2 creation (`4,608`), late compensation reversal (`5,184`), and coupled mixed-generation exposure (`1,152`).
- `vector_retire_then_activate`: unsafe `0`; terminal `2,400`; progress units `4,800`.
- `per_component_retire_then_activate`: unsafe `2,016`; terminal `2,400`; progress units `10,944`.
- `graph_barrier`: unsafe `0`; terminal `2,400`; progress units `8,928`.
- `atomic_group_transfer`: unsafe `0`; terminal `5,760`; progress units `13,824`, but only in scenarios where that sink capability exists.

Primary falsification:

- Two changed + coupled resources with exactly one resource safely retired: `2,016` scenarios.
- Per-component activation exposed a mixed old/new logical generation in `2,016 / 2,016`.
- Coupling-aware graph barrier exposed `0 / 2,016`.

Countervailing liveness result:

- Two changed + independent resources with exactly one safely retired: `2,016` scenarios.
- Per-component and graph-barrier policies each preserved `2,016` progress units.
- Vector-wide barrier preserved `0`.
- Across the full lattice, graph barrier had safe progress advantage over vector-wide barrier in `4,128` scenarios / `4,128` progress units.

Late-reversal result:

- When a changed old effect could reverse after apparent compensation and no reseal/finality capability existed, there were `2,592` scenarios.
- Weak retry was unsafe in `2,592 / 2,592`.
- Graph barrier terminalized `0 / 2,592`; it failed closed rather than treating current-only cleanup as absorbing finality.

## Mechanism conclusion

The smallest safe barrier in this two-resource model is neither universally per-resource nor universally vector-wide. It is the connected component of the **authority-conflict / semantic-coupling graph**:

- independent changed effects may retire and activate independently;
- changed effects joined by a non-overlap or cross-resource invariant must cross the generation boundary together;
- unchanged effects can be adopted independently only when their old result has an absorbing proof or can be safely resealed;
- ambiguous/failed/late-reversible compensation is not retirement;
- compensation request acceptance is not finality;
- takeover/response-loss retry needs a stable compensation/effect identity;
- if the sink can atomically transfer authority for the whole coupling group, that dominates compensation+barrier in this finite model.

This is narrower than a global vector barrier and stronger than a pure per-component barrier.

## Generic residual capability boundary

All Chat-capable work for this selected leaf is complete: public audit, finite falsification, executable checker, role-local result packaging, and continuation were produced.

The remaining generic external effect is **authoritative sink transition for a coupling group**: either (a) provide an absorbing retirement/reseal proof for every superseded old authority before new authority can be granted, or (b) provide an atomic coupling-group old->new authority transfer/fence. The currently exposed tools let this CLEAN role write only role-local repository evidence; they do not expose an arbitrary authoritative external sink's revoke/reseal/transfer operation. Classification: `downstream_verification_required`. This is not a global Phase-1 closure claim.

## Scope limits

- Only two resources are modeled.
- Coupling is a static boolean for the invocation; dynamic conflict-graph membership is not modeled.
- A coupling group is treated as needing one generation-consistent activation barrier. We do not yet model hyperedges, budget constraints, or a conflict graph that changes during compensation.
- `atomic_group_transfer` is a capability assumption; the model does not claim that arbitrary external systems expose it.
- Business semantics of compensation are abstracted to the four outcome classes above.
- Counts are synthetic equal-weight cases.

## Exact continuation

Next non-conflicting Phase-1 leaf: **dynamic coupling-graph snapshot and barrier invalidation**.

Model 3 resources with an effect-conflict graph whose edges may be added/removed while supersession is in progress. Compare:

1. barrier component computed once at plan time;
2. per-resource retirement with no graph epoch;
3. graph snapshot + `graph_epoch` fence checked only before compensation;
4. graph snapshot + `graph_epoch` revalidated at activation;
5. vector-wide barrier;
6. sink-side atomic transfer for the current connected component.

Enumerate edge addition after one resource retires, edge removal, concurrent task-spec drift, takeover, ambiguous graph read, response loss, and late old-authority revival. Primary falsification: a component computed from a stale graph may activate resources independently even though a newly added edge now couples them. Determine whether a single monotonic graph epoch is sufficient, or whether each effect key needs versioned membership plus activation-time currentness proof.

Base continuation remains preserved and is not active Phase-1 work.
