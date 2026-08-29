# Phase-1 multi-agent Part 63 — topology abort cleanup

Frozen authority: DESIRED_STATE blob `481660fb6008a57cea162da38439cf115c8d7ebe` control revision 26; role config blob `f6bade5e0f774a0623e615b1fc5f924475732d5c` config revision 8; lifecycle blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; transport `sha_only_exact_sha`; frozen main `3ea5252a8a2454070e467961efb0df0f490a322d`. Phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-multi-agent-concurrency-claims`. Bootstrap valid: true.

## Bounded slice

Starting state is the Part-62 continuation only: topology G2 is PREPARED, G1 remains authoritative, one G2 child has been provisioned with an inherited floor. A finite equal-weight Boolean lattice enumerated 8 adversaries: late G2 child write, late G1 parent write, cleanup-response loss, child-name reuse with a new incarnation, stale coordinator, repository rate-limit interruption, GC, and concurrent promotion intent. This gives 256 scenarios per strategy and 1,280 strategy-scenario evaluations.

Compared strategies: (1) delete child then abort; (2) mark generation aborted then name-only child cleanup without same-compare coordinator/promotion fencing; (3) forwarding-only rollback; (4) monotonic `ABORTED` plus current coordinator/topology compare and exact child generation/incarnation cleanup; (5) fail closed.

Safety oracle for this model: abort/cleanup is destructive only when coordinator/topology authority is current and no conflicting promotion is active; PREPARED G2 is not write-authoritative; committed ABORTED is monotonic; cleanup must target the exact child generation/incarnation; ambiguous cleanup is read-before-retry; GC must not delete a live root/incarnation. Counts are mechanism-lattice counts, not production failure rates.

## Results

| strategy | unsafe scenarios / 256 | G2 resurrection | reused-child stale cleanup | duplicate cross-generation reservation | live-root deletion | stranded child | false blockage | recovery reads |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| delete-child-then-abort | 194 | 120 | 64 | 60 | 112 | 224 | 0 | 0 |
| abort-then-name-only-cleanup | 176 | 64 | 64 | 32 | 96 | 128 | 0 | 0 |
| forwarding-only rollback | 176 | 128 | 0 | 64 | 96 | 256 | 128 | 0 |
| monotonic ABORTED + exact-generation cleanup | 0 | 0 | 0 | 0 | 0 | 240 | 128 | 144 |
| fail closed | 0 | 0 | 0 | 0 | 0 | 256 | 128 | 192 |

Within this exact model, the strong strategy removes the four modeled safety failures but intentionally leaves unresolved cleanup under authority conflict, rate limit, or ambiguous response. It therefore improves over pure fail-closed on reclamation/recovery work but is not a liveness-complete protocol. Forwarding is routing/fencing assistance only: because it does not make G2 ABORTED, it leaves a resurrection surface.

The key negative control is child-name reuse. Deleting or retrying cleanup by name alone can target a later incarnation. Kubernetes' current Preconditions API documents that update/delete preconditions can include both `uid` and `resourceVersion`; this is a public analogue for exact-incarnation destructive cleanup: https://kubernetes.io/docs/reference/kubernetes-api/definitions/preconditions-v1-meta/ . The key positive atomicity requirement is the current coordinator/topology compare around the ABORT transition; etcd's transaction API is a public analogue for an atomic conjunction of key comparisons guarding a request block: https://etcd.io/docs/v3.6/learning/api/ . These are mechanism precedents only; etcd is not accepted as a Phase-1 dependency.

## Phase-1 acceptance assessment

Observation: the finite model supports the repository-local rule `PREPARED -> ABORTED` as a monotonic authority transition, fenced by current coordinator/topology identity, followed only by exact-generation/incarnation child cleanup with read-before-retry on ambiguous outcomes. Inference: a name-only cleanup or forwarding-only rollback is insufficient as an authority proof. Scope caveat: this model has one provisioned child and Boolean adversary ordering abstractions; it does not prove arbitrary multi-child cleanup, complete repository rollback safety, or external sink atomicity.

Residual richer-mode/protected/manual-user execution dependency added: none. Finite monthly/trial/paid quota dependency added: none. Incremental monetary cost: 0. External hosted coordination: not required or accepted; etcd is cited only as a public semantic precedent. Repository API rate-limit interruption is fail-closed/recoverable, not retried in this invocation.

Global Phase-1 completion claimed: false. `enabled_desired` remains true. Scheduler mutation by worker: false.

## Exact continuation

Next invocation, model post-ABORT child reclamation without starting another leaf in this invocation: root is durably `ABORTED` and carries an exact cleanup set of child generation/incarnation IDs. Compare eager exact delete, root-retained cleanup manifest plus monotonic per-child cleanup cursor, per-child tombstone, name-only GC, and fail-closed under child reuse, partial multi-child cleanup, ambiguous delete response, rate limit, stale coordinator, GC compaction, and a later topology generation reusing the same logical child name. Measure stale deletion, ABA/replay, stranded state, false blockage, recovery reads, and whether the root cleanup witness itself can be compacted without losing exact-generation fencing.