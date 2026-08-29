# Phase-1 multi_agent checkpoint — shared-gate alternatives under CLEAN isolation (Part 44)

## Frozen semantic tuple

- frozen authority commit: `64cda245ee44957f79a51b738e9bdfa549d151c4`
- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `sha_only_exact_sha`
- predecessor: `PHASE1_ROLE_SLOT_BOUND_20260830_013535_PART43.md`

Part 43 isolated the missing liveness primitive: role-local slots can bound simultaneous owners, but a finite starvation proof also needs to close new arrivals after a wide request. A dynamically shared REQUESTED ticket would do that mechanically, yet the current CLEAN policy does not allow this role to read other workers' state or write a shared claim namespace. This leaf audits alternatives that preserve that isolation rather than smuggling another worker's semantics through a forbidden channel.

Executable model: `research_workers_clean_g1/multi_agent/phase1_clean_gate_alternatives_20260830_part44.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_clean_gate_alternatives_20260830_part44.json`

## Result 1 — static exclusive ownership prevents single-effect duplicates without dynamic shared reads

The finite single-effect model uses six roles and twelve canonical effects. If each effect has exactly one statically authorized owner, 72 possible role/effect attempts reduce to **12 admitted + 60 rejected unauthorized attempts, with duplicate authoritative effect 0**.

This construction needs no worker-to-worker semantic state. The authority partition can be encoded in a sanitized root/config that every role is already allowed to read. Each worker only needs to prove that the effect key belongs to its own capability partition before publication.

This is the first full-pool conflict-prevention shape in this continuation that is structurally compatible with the current CLEAN semantic boundary without a dynamic shared gate.

However, its scope is static. It does not give two roles permission to race for the same effect and then resolve ownership dynamically; it eliminates that race by construction.

## Result 2 — serialization without a semantic claim does not provide idempotency

A branch/ref serialization channel can order all 72 single-effect attempts, but if every role is still semantically allowed to execute every effect, the model has **60 logical duplicate attempts after the first per effect**. Git version ordering tells a worker that something changed, but CLEAN policy also forbids consuming unrelated commit messages/diffs as a semantic backchannel.

Therefore the branch ref alone is a safety/version mechanism, not a substitute for a canonical effect claim or static ownership rule.

A deterministic time/turn owner has the same semantic problem as lease expiry. In the 12-effect negative control, every old owner that resumes after its nominal time epoch can still act unless a current authority fence revokes it. Time schedules who *should* act; they do not prove who *may* still act.

## Result 3 — create-once shared claim is mechanically attractive but not an admissible current write surface

A create-once path keyed by canonical effect/transition ID would be a clean mechanical claim primitive: all contenders attempt the same path, exactly one create succeeds, and losers need only conflict status rather than the winner's payload. GitHub file creation/current-path conflict behavior makes this a plausible repository transport pattern.

But the current role control restricts writes to `research_workers_clean_g1/multi_agent/` and `automation_control/receipts/multi_agent/`. A cross-role canonical claim path or Git ref namespace is not in that boundary. The role also may not read another worker's private claim file or shared aggregate ledger.

So `shared_create_once_claim` is marked mechanically sufficient in the finite model but **current_clean_write_surface_available=false**. It remains an unresolved control-surface child, not an accepted deployed solution.

The same applies to a branch/ref claim namespace: the exposed connector can create/update refs, but current repository role policy has not authorized arbitrary coordination refs as this role's write destination.

## Result 4 — durable sink idempotency could eliminate worker semantic sharing, but only if the sink owns the dedupe contract

Another architecture is to send every effect with a globally canonical `effect_id` to a sink that atomically enforces durable create-once/idempotent application. Workers need not read each other's state; the shared sink itself is the authority.

That is exactly the attractive boundary identified in the earlier external-effect leaves. But there is no generic sink capability that can be assumed here: different sinks have different idempotency retention windows and some non-idempotent sinks cannot distinguish a lost response from an unapplied effect. An unspecified shared sink would also become a residual external dependency rather than a scheduled-Chat-native proof.

Thus the model records sink idempotency as conditionally sufficient but `current_generic_sink_capability_proven=false`. Specific sinks can be audited separately; it is not a generic Phase-1 closure.

## Result 5 — static multi-effect ownership reduces to conflict-component ownership

The limitation of static ownership appears for multi-effect tasks. With twelve effects statically divided two per role, there are 66 possible two-effect tasks:

- only **6/66** stay entirely within one role's two-effect partition;
- **60/66** cross role partitions.

More importantly, the overlap graph of *all* 66 two-effect tasks is one connected component of size 66. If every pair of tasks sharing any effect must have the same static owner, transitive equality collapses the full arbitrary two-effect family to one owner — the same connected-component result as Part 40.

By contrast, the six same-owner pair tasks are six disconnected components of size one. Static partitioning is therefore useful exactly when the application task/effect family itself has disconnected conflict components or can be restricted so that cross-component tasks fail closed/replan.

This gives a precise static alternative to dynamic claiming:

- define the allowed task/effect family first;
- compute or conservatively approximate its conflict components;
- assign each component to one role/capability partition in sanitized control;
- each role publishes only effects in its assigned component and binds the component/effect-set digest into PREPARED authority;
- tasks spanning components are not silently executed; they become explicit wide/global unresolved cases.

## Current CLEAN-surface audit

Within the frozen control, this role may use:

- sanitized root/static assignment information;
- own role-local state/output;
- own receipts;
- public sources.

It may not use as semantic coordination:

- other-role state/config/receipts;
- shared execution ledger;
- a dynamic shared claim file not authorized by its write boundary;
- unrelated commit messages/diffs;
- downstream/O state.

Therefore the accepted full-pool mechanism scope narrows to **static nonoverlap by construction** plus repository-local fencing inside each role/component. Dynamic same-effect competition remains unresolved unless repository control later exposes a sanitized shared claim surface or the authoritative sink itself provides the idempotency/fencing primitive.

## Zero-dependency / zero-quota assessment

Static capability partitioning is zero incremental cost, uses only sanitized repository control and role-local repository transport, and needs no richer-mode/manual/protected execution step, hosted coordinator or finite monthly/trial/paid quota. It is accepted in the tested static-effect-family/no-complete-rewind scope.

The unavailable shared claim/ref surface is not counted as solved. Durable external sink idempotency is not counted generically. Complete rewind and direct fixed-path consumer parity remain unresolved from earlier leaves.

## Exact continuation

Next Phase-1 leaf: **static capability revocation and ownership handoff without a dynamic shared claim**.

Test a sanitized-root capability epoch under:

- owner role crash and later same-role recovery;
- capability reassignment from role A to role B;
- old A invocation frozen on the previous control tuple;
- root/config change between A's final authority check and repository effect publication;
- branch-global ref publication versus local file-SHA publication;
- no-reassignment/same-role recovery as a control;
- effect-set/component digest drift;
- response loss and takeover.

The key question is whether static ownership can support safe role-to-role failover without turning every effect into a branch-global publication, or whether zero-shared-state safety requires keeping ownership immutable and recovering only within the same role slot/incarnation.
