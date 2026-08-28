# Phase-1 parent/child claim-generation stress test

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- first explicit local-clock observation: `2026-08-28T21:58:17+09:00`
- checkpointed_at_observed: `2026-08-28T22:05:28+09:00`
- chronology_valid: `false` because bootstrap/control reads began before the first explicit local-clock observation; no earlier timestamp is fabricated.
- frozen note main SHA: `97590a1f3e99efbb80abc0bf6fcb405bba17a99f`
- frozen root control revision: `16`
- frozen role config revision: `6`
- frozen role config blob: `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- control_change_after_semantic_start: `true`
- newer observed note main SHA after semantic start: `6c22881637d6b4a75716583fb72cb0eaed62ac70`
- newer control/config contents were not read or adopted after the semantic freeze barrier.
- semantic inputs used: own `LATEST.json`, own prior Phase-1 checkpoint, sanitized root/own role config, and the public sources listed below. No O, downstream, other-worker state/config/receipts, shared aggregate ledger, or legacy research was used.

## Result

The previous leaf established that a lease is not stale-writer fencing. This continuation tested the next parent/child layer: parent generation supersession, child completion before/after supersession, leaf takeover, overlapping exclusive-effect declarations, deterministic versus non-deterministic merge declarations, and one serialized CAS-style canonical integrator.

The companion enumerator `phase1_parent_child_claim_generation_20260828_220333.py` exhaustively generates 1,184 finite scenarios per protocol. The grammar has two required children (`A`,`B`), four per-child completion patterns (`current_only`, `stale_then_current`, `current_then_stale`, `stale_only`), every interleaving that preserves each child's local completion order, no supersession or a generation-1 -> generation-2 supersession at every event boundary, balanced effect-key overlap, and balanced deterministic/non-deterministic merge declarations. The canonical integrator is serialized, so lost-update races are deliberately outside this model.

### Exact mechanism counts

| protocol | scenarios | traces that ever terminalize | traces with false parent terminalization | traces with duplicate authoritative child integration | safe parallel admissions |
|---|---:|---:|---:|---:|---:|
| coarse parent claim | 1,184 | 616 | 0 | 0 | 0 |
| leaf lease-only | 1,184 | 888 | 600 | 544 | 212 |
| leaf epoch-fenced | 1,184 | 616 | 0 | 0 | 212 |

For the lease-only leaf protocol, 600/888 terminalizing traces (67.57%) contain at least one parent terminalization that used a child result whose claim was no longer current, and 544/888 (61.26%) contain at least one duplicate authoritative integration of the same child slot. There are 736 duplicate authoritative integration events in total. These equal-enumeration fractions are mechanism-test ratios only, not real-world incidence estimates.

The generation+epoch-fenced leaf protocol rejects 816 generation-mismatched results and 1,184 stale-epoch results in this grammar, while producing zero false terminalization traces and zero duplicate authoritative integration traces. The coarse parent claim is also safe in this finite model, but it exposes no leaf parallelism.

A second independent proof obligation appears at decomposition time. Across 848 leaf traces where both children have a current completion available, only 212 satisfy both `exclusive_effect_keys disjoint` and `deterministic_merge=true`; 636 are denied by at least one of those gates. A negative control that keeps epoch fencing but admits every parallel candidate would therefore admit all 636 structurally conflicting cases. This means stale-writer fencing and parallel-decomposition safety are non-substitutable: current epochs do not make overlapping effects or non-deterministic merges safe.

Result artifact: `phase1_parent_child_claim_generation_20260828_220333.json`.

## Mechanism interpretation

### 1. Parent generation must be a terminality watermark

A parent terminal state should be generation-qualified. Required child results must carry the parent generation/task hash they were computed for, and terminalization must validate those fields against the current parent immediately before the canonical CAS. Superseded child results can remain immutable evidence, but they are not automatically current results.

This has a close public analogue in Kubernetes generation tracking. Current Kubernetes Pod documentation states that `status.observedGeneration` reflects the object's `metadata.generation` at the point the status is reported, and also distinguishes status that may still reflect a prior generation while an indirect process is in progress. Deployment/StatefulSet status APIs likewise expose `observedGeneration`. Sources: https://kubernetes.io/docs/concepts/workloads/pods/ and https://kubernetes.io/docs/reference/kubernetes-api/apps/deployment-v1/

Observation: generation-qualified status is a public mechanism for distinguishing current desired state from potentially lagging observations. Inference for this assignment: parent integration should use the same kind of generation pin; the Kubernetes fields are not themselves a multi-agent claim protocol.

### 2. Single-CAS serialization does not replace leaf fencing

The model intentionally gives every protocol a serialized canonical integrator, eliminating lost updates. Lease-only still produces 544 duplicate-authority traces because sequential CAS operations can each be individually valid at the storage layer while the second writer is semantically stale. Therefore CAS solves concurrent overwrite, but current-owner/current-epoch validation solves stale authority; both are required.

### 3. Coarse exclusivity and fine-grained fencing trade utilization, not the same safety mechanism

A coarse parent claim can stay safe by serializing all required child work behind one authority domain, but it forfeits independent leaf parallelism. Fine-grained leaf claims recover parallelism only when each leaf is independently fenced and decomposition proves non-overlapping exclusive effects plus deterministic/serialized merge.

GitHub Actions publicly documents that workflows/jobs can run concurrently by default and that concurrency groups can restrict that execution, cancel pending runs, or queue them. Source: https://docs.github.com/en/actions/concepts/workflows-and-actions/concurrency . Observation: coarse concurrency grouping is an available exclusion mechanism. Inference: a group limit alone does not encode parent generation, child task hash, or leaf claim epoch, so those still need explicit result/integration metadata in a repository-native protocol.

## Updated protocol obligations

- **P1 parent-generation coherence:** a terminal parent must be based only on required child dispositions whose `parent_generation` and `task_hash` equal the current parent objective.
- **P2 leaf stale-writer exclusion:** authoritative child integration requires the current claim epoch/fencing token; lease validity/TTL alone is not sufficient.
- **P3 immutable staging:** stale/superseded child work may be retained at a unique immutable path, but cannot overwrite a current canonical child slot automatically.
- **P4 serialized canonical authority:** one integrator performs the parent/child manifest update through CAS and reconciles on conflict.
- **P5 decomposition independence:** parallel admission requires disjoint exclusive-effect keys and a deterministic merge rule; otherwise merge the leaves into one claim or execute sequentially.
- **P6 parent completeness:** terminalization requires every required child to have a generation-valid accepted result or explicit skip/block disposition.
- **P7 no hidden-progress assumption:** elapsed time, cancellation request, or claim expiry is never completion evidence; only durable staged/integrated state is.

## Failure tests added

1. Child A completes under parent generation 1, parent supersedes to generation 2, child B completes under generation 2: generation-1 A must not satisfy generation-2 parent completeness automatically.
2. Child B's epoch-1 worker completes after epoch-2 takeover: immutable staging may succeed; canonical integration must reject epoch 1.
3. Epoch-1 stale B integrates first and epoch-2 B integrates later: lease-only protocol must be flagged for false terminalization/duplicate authority even though both CAS writes serialize cleanly.
4. Epoch-2 current B integrates first and epoch-1 B wakes later: stale overwrite must be rejected rather than treated as a later valid CAS update.
5. Two ready leaves declare the same exclusive effect key: parallel route must be denied regardless of valid claim epochs.
6. Two ready leaves have disjoint effects but no deterministic merge rule: parallel route must be denied or an explicit serialized resolver supplied.
7. Parent supersedes after a generation-1 terminal state: generation-1 result remains historical evidence, while generation-2 completeness resets rather than inheriting old children implicitly.
8. No other worker actually runs: the protocol remains correct and progresses sequentially; it must not infer child completion from the existence of claims.

## Scope limits

- The enumerator models a single serialized canonical integrator and therefore does not test integrator read/CAS races, crash-before-readback, or multi-file atomicity.
- It treats a stale claim result as non-authoritative even if its bytes happen to equal the current worker's result; the safety claim is about authority/provenance, not content equivalence.
- Effect overlap and deterministic merge are declared booleans here; no automatic static analysis for discovering effect-key overlap or semantic commutativity is claimed.
- The terminal/duplicate percentages are balanced synthetic mechanism counts, not operational failure probabilities.
- Cancellation acknowledgements and cancellation-vs-already-emitted side effects are not modeled in this leaf.

## Base continuation preserved, not resumed

The pre-overlay base continuation remains preserved exactly as fallback metadata and was not resumed while the Phase-1 overlay is active:

`Resolve/freeze latest sanitized control. Continue from FOLLOWUP_2026-08-28_200940_JST.md. Extend compensation repair from one ambiguous writer to multiple refund resource IDs and amount conservation over unique capture/refund/reversal identities; model accepted-but-no-resource-ID timeout; add late failure/reversal to newly issued compensation; expand to two captures and multi-irreversible branching DAG; compare independent repair proposals against early cross-critique on safe Pareto/QD coverage. Retry JudgmentBench only after source-qualified byte-stable transfer plus local publisher-hash verification; retry only source-qualified SymFail item artifact discovery.`

## Exact next Phase-1 action

Resolve/freeze the newest sanitized control first. If the Phase-1 overlay still assigns `phase1-clean-multi-agent-concurrency-claims`, extend this same transition grammar with an explicit parent/integrator claim epoch and crash/cancellation boundaries: `integrator_read -> parent_supersede/cancel -> integrator_CAS -> crash-before-readback -> resume/reconcile`, plus old-child completion during/after cancellation. Compare `{CAS-only, cancel-only, generation+leaf-epoch fenced}` for false parent terminalization, duplicate canonical integration, orphan accepted child results, and recoverability. Add one revalidation branch where a superseded child may be adopted only after exact `task_hash + input_digest + effect_contract` equivalence is proved; automatic adoption remains forbidden. If that leaf is exhausted, continue to the next unresolved generic Phase-1 concurrency candidate rather than restoring base work.
