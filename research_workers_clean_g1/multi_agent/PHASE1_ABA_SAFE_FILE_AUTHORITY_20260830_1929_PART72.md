# Phase-1 multi_agent Part72 — ABA-safe file authority without ref CAS/protected policy

Authority freeze: `DESIRED_STATE.json` control_revision 26, blob `481660fb6008a57cea162da38439cf115c8d7ebe`; `roles/multi_agent.json` config_revision 8, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`; `RUN_LIFECYCLE.json` blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; transport `sha_only_exact_sha`; frozen main `4bfed4b77c6344da5e59313f0e95b7125129c674`.

## Bounded question
Can create-only path conflict plus sink-time durable `applied_transition_id` prevent duplicate/conflicting authoritative effects when the coordination record itself can be deleted/recreated, or does a positive result require an explicit non-deletion/independent anti-rollback assumption?

## Public mechanism evidence
GitHub REST repository-contents documentation says create/update and delete are separate contents operations; updating requires the blob `sha` being replaced, deleting requires the blob `sha` being deleted, and concurrent create/update versus delete operations can conflict and should be serialized. Source: https://docs.github.com/en/rest/repos/contents (retrieved 2026-08-30). This supplies ordinary blob-CAS/conflict behavior but no server-maintained path-incarnation token or non-deletion guarantee.

## Finite truth-table probe
64 equal-weight Boolean traces were considered per mechanism over `{coordination_record_deleted_or_exact_old_bytes_recreated, stale_old_generation_writer, create_response_ambiguous, effect_already_applied, durable_sink_effect_id_available, durable_sink_generation_floor_available}`. Counts are mechanism-counterexample counts, not production rates.

Safety predicates were separated: (A) duplicate replay of the same logical transition and (B) stale/conflicting authority from an old generation that has not necessarily been applied before.

| mechanism | unsafe /64 | duplicate-effect traces /64 | bounded interpretation |
|---|---:|---:|---|
| deterministic create-only witness keyed by `{parent_generation,next_generation,transition_id}` | 40 | 16 | Path conflict dedupes only the same transition while its record exists. A stale generation can use a distinct transition path, so create-only is idempotency, not freshness. Deletion also reopens same-transition replay. |
| mutable current pointer + explicit incarnation nonce + blob-SHA CAS | 24 | 16 | Ordinary stale writers are fenced while the current pointer remains present and changed. Delete/recreate of exact old bytes recreates the same blob SHA/nonce state and reopens the ABA trace. |
| content-addressed transition chain + mutable/deletable current head | 24 | 16 | Content hashes authenticate bytes/links but do not prove that an old head was not restored after deletion; same bounded ABA surface as the pointer. |
| create-only winner + sink-time durable `applied_transition_id` | 36 | 8 | Durable sink id halves the replay-duplicate slice when available, but a never-before-applied stale transition still has a fresh id and is accepted without a freshness floor. |
| create-only winner + sink durable `applied_transition_id` + sink monotonic minimum-generation floor | 22 | 8 | Mixed-capability lattice still has failures when either sink capability is absent. In the supported sub-slice where both sink properties exist, all 16/16 traces are safe, including coordination-record deletion/recreation. |

Derivation highlights: create-only stale-authority failures occur for all 32 traces with `stale_old_generation_writer=1`; mutable-pointer/chain stale failures require both stale writer and coordination ABA (16). Same-transition duplicates require deletion plus prior application (16) unless a durable sink id is actually available/used (8). The final mechanism's supported `sink_effect_id=1 && sink_generation_floor=1` sub-slice is 16/16 safe because freshness and replay identity are checked independently at the effect sink.

## Result
`applied_transition_id` alone is not an anti-rollback primitive. It answers “has this transition already been consumed?” but not “is this transition still authorized now?”. A deterministic create-only witness likewise arbitrates only writers targeting the same path/transition identity; different old/new generation transitions need a freshness authority.

Therefore coordination-record deletion is tolerable only when an independent authority domain at the effect sink durably enforces both (1) a monotonic accepted-generation lower bound and (2) single-consumption/idempotent effect identity. If that sink contract is unavailable, the tested repository-only positive requires an explicit non-deletion assumption for the authoritative current/retirement witness; blob-SHA CAS, a nonce stored only in the deletable file, or content-addressing alone does not discharge ABA.

This is a scoped falsification, not a universal impossibility theorem: another repository primitive with a non-deletable server-maintained incarnation/version or an atomic sink freshness predicate could change the result. No destructive repository test was performed.

## Phase-1 constraints
Residual richer-mode/protected/manual execution dependency: none added. Finite monthly/trial/paid quota dependency: none added. Incremental monetary cost: 0. Repository API is transport/evidence only, not compute. Accepted external hosted coordination: none. Conditional sink-floor positive is capability-scoped evidence, not a generic accepted handoff.

## Observation vs inference
Observation: current public Contents contract uses blob SHA for update/delete and allows delete; current Chat connector exposes create/update/delete file operations. Inference from the finite model: path create conflict and durable effect-id alone cannot jointly prove freshness after deletion/recreation; independent monotonic freshness or a non-deletion threat assumption is required.

## Exact continuation
Part73: execute one bounded leaf on repository-only monotonic freshness without protected branch policy: compare (a) append-only per-generation quorum-of-path witnesses, (b) deterministic hash-chain checkpoints replicated across independent role-local paths, (c) two-file cross-check with one file deletion/recreation, and (d) sink-side generation floor when the sink is only the repository itself. Include single-path deletion, two-path coordinated deletion, stale read followed by create, ambiguous response, and exact-byte recreation. Determine whether replication changes only fault threshold or can create a true anti-rollback property without an undeletable/server-monotonic primitive. Keep Phase 1 open and do not start another leaf in this invocation.
