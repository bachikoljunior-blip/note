# Phase-1 multi_agent checkpoint — membership epoch and phantom-role admission (Part 44)

## Frozen semantic tuple

- frozen authority commit: `302327074272033f246c5d8f555df61004e3802f`
- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `sha_only_exact_sha`
- predecessor: `PHASE1_ZERO_WRITE_INFLIGHT_20260830_043701_PART43.md`
- post-freeze check: main later reached `2f57efb50d7b17d19dfa6dc6ac1caf61460e05f6`; frozen root and role-config blob identities were unchanged, so no new semantics were adopted.

Part 43 established a finite authoritative-inflight **count** without a global write per local admission: every role has one incarnation-sensitive current admission slot, and only its slot head may be authoritative PREPARED. The missing condition was a finite, stable definition of the current role-slot membership set. Part 44 tests role add/remove/re-add, rename, namespace migration and control advance as phantom-membership races.

Executable model: `research_workers_clean_g1/multi_agent/phase1_membership_phantom_20260830_part44.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_membership_phantom_20260830_part44.json`

The finite lattice contains `5,184` scenarios and `25,920` strategy evaluations. Dimensions are base role count 1/3/11, membership operation `none/add/remove/readd/rename/migrate`, mutation timing before REQUESTED / after REQUESTED before scan / after scan before publish, same-role overlap, stale slot, membership-response loss, slot-creation-response loss, rate-limit interruption at membership write or slot creation, and a control/membership authority advance after the invocation's semantic freeze. Counts are mechanism counts, not deployment probabilities.

## Result 1 — a fixed slot snapshot has a membership-phantom problem

A wide owner can enumerate a finite set of current role slots and still be wrong if membership can change after the snapshot. The `fixed_slot_snapshot_no_membership_epoch` negative control has **768/768 phantom-role unsafe** cases in the post-REQUESTED `JOIN / READD / RENAME / MIGRATE` slice where both membership and slot transport are available.

Across the whole lattice it has 768 phantom-role unsafe cases, 3,552 stale-membership publications and 576 stale-slot false exclusions. Membership response loss is ambiguous in 1,440 cases and slot creation response loss in 1,152.

The important distinction is the same one as the earlier predicate/range phantom result: enumerating known members does not fence creation of a new member outside the captured set.

## Result 2 — append-only role history is not a current membership fence

`append_registry_snapshot` improves provenance but does not solve the predicate race. If a new role-incarnation appears after the registry scan and before wide publication, **384/384** such cases are phantom-role unsafe in the model.

An append-only record can tell us that a role existed or a transition was requested. It does not by itself prove that the set of ACTIVE role-incarnations has not changed since a wide operation chose its finite bound.

Therefore the finite slot count needs a **current membership authority epoch**, not just an auditable history.

## Result 3 — a separate membership epoch restores safety but not finite liveness under arbitrary churn

`separate_membership_epoch_recheck` re-reads the current membership epoch immediately before wide publication. Any membership/control transition after REQUESTED makes the wide operation abort and retry. This produces **0 modeled phantom-role unsafe** and **0 stale-membership publication** in all 5,184 scenarios.

However 2,688 scenarios require a membership retry. In the finite lattice 2,496 scenarios happen to terminalize without a retry condition, but no finite progress theorem follows under unbounded membership churn: a JOIN/LEAVE sequence can always invalidate the next retry.

So a membership epoch can be a safety fence while still leaving wide-operation starvation open.

## Result 4 — co-locating membership and wide-ticket state closes the phantom window in the finite model

The strongest generic candidate stores in one current CAS object:

`membership_epoch + finite ACTIVE role-incarnation set + wide_ticket_state + ticket_transition_id`

The protocol shape is:

1. **JOIN** initializes/reconciles the role's incarnation-sensitive slot first; only after a successful slot readback does it CAS the shared membership object to ACTIVE. If rate-limited or response-ambiguous, membership stays non-ACTIVE/fail-closed until reconciliation.
2. **LEAVE** CASes membership to retiring/removed; a stale old slot then stops contributing to the current ACTIVE bound.
3. **WIDE** CASes the same object to `REQUESTED`, capturing the exact current ACTIVE role-incarnation set and membership epoch.
4. While REQUESTED, membership mutation conflicts or fails closed. A newly scheduled local invocation only **reads** the shared ticket and then writes its own local role slot; it does not write the shared membership root for ordinary local admission.
5. Final wide publication binds the captured membership/ticket transition identity and the Part-42 recovery epoch.

`co_located_membership_ticket` has **0 phantom-role unsafe, 0 stale-membership publication and 0 false stale-slot exclusion in 5,184/5,184** modeled scenarios. It performs 6,144 membership/ticket root writes across the lattice, versus the `global_root_every_admission` baseline's 46,944 global-hotspot touches.

This retains the desired locality property in the abstract protocol: shared writes happen for membership changes and wide-ticket acquisition/release, not for every local operation.

GitHub's Contents API current-blob SHA update behavior can provide a single-file CAS primitive if such a shared semantic object is authorized:
- https://docs.github.com/en/rest/repos/contents

Rate-limit interruption must be treated as checkpoint/readback rather than an assumed membership transition:
- https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api

## Result 5 — control/config freshness and membership activation are separate authority domains unless explicitly coupled

The invocation itself remains bound to the frozen control/config tuple. A later control revision is not adopted mid-run. But a future role activation caused by a newer control can still become a membership phantom unless activation is required to transition the same current membership authority before the new role may publish authoritative work.

In the finite model the membership-epoch candidates fence 2,592 control-advance cases; the snapshot/registry controls do not.

This is not permission to read a newer control after the semantic barrier. It is a protocol requirement on the **future activation path**: membership activation must be represented in the current membership authority domain before it can add authoritative in-flight capacity.

## Critical CLEAN-boundary result — the strongest generic candidate is not currently deployable by this role

The current `multi_agent` CLEAN policy authorizes semantic reads from:

- own role-local clean state;
- public sources;
- own sanitized feedback;
- sanitized root manifest;
- own role config.

It authorizes writes only to the role's own state namespace and immutable own receipts. It forbids other-worker state and the shared aggregate execution ledger.

The co-located membership/ticket object above is a **cross-role semantic coordination object**. For it to work, all roles must read it and membership/wide coordinators must write it. No such cross-role shared coordination manifest is currently exposed as an authorized CLEAN semantic surface in the frozen root/config.

Therefore Part 44 does **not** count this generic mechanism as current Phase-1 acceptance. Treating an unavailable shared manifest or an optimizer/user/protected handoff as “the implementation step” would violate the root's zero-residual-dependency rule. This is an exact unresolved child.

This also means Part 43's per-role slot bound is a protocol mechanism result, not yet a cross-role deployment proof under current CLEAN isolation. Each role may own its local slot, but a wide coordinator cannot simply inspect other workers' role-local state under the present boundary.

## Zero-dependency / zero-quota assessment

The finite mechanisms themselves require only lightweight repository CAS/readback and add no GitHub Actions, Codespaces, artifact/LFS/package storage, cloud compute, external model/API credit, manual user action, richer-mode arbitration or protected-primary execution. Incremental monetary cost is zero; rate limits are interruption/checkpoint events.

However the generic shared membership/ticket candidate fails a different acceptance gate: **current repository authorization / CLEAN semantic boundary**. A capability that is not authorized is an unresolved child, not a zero-dependency success.

## Exact accepted and unresolved scope

Accepted as generic mechanism evidence only:

- a changing finite role-slot set needs a current membership authority epoch;
- snapshot/history-only membership admits post-snapshot phantom roles;
- final epoch recheck is safe but can starve under unbounded membership churn;
- co-locating membership epoch/set with the wide REQUESTED ticket eliminates the modeled phantom window while avoiding a shared write on ordinary local admission.

Not accepted as a current deployable Phase-1 route:

- any protocol requiring CLEAN workers to read other-worker role-local state;
- any protocol requiring this worker to write the shared aggregate ledger;
- a cross-role membership/ticket manifest that is not explicitly authorized by the current sanitized control;
- any manual, protected or richer-mode step to install such a surface.

Other unresolved boundaries remain complete repository rewind, noncooperative publication paths, direct fixed-path consumers and arbitrary external sinks.

## Exact continuation

Next leaf: **CLEAN-boundary-compatible cross-role coordination without shared worker-state reads**.

Compare only designs legal under the frozen CLEAN boundary:

1. deterministic effect identities with an authoritative sink providing durable idempotency/fencing;
2. root-sanitized immutable membership metadata plus one own-local slot per role, but no shared runtime ticket;
3. branch-conflict-only wide publication without pre-ticket cross-role reads;
4. an explicitly sanitized shared coordination manifest only as an unresolved capability test unless/ until the root itself authorizes it.

Required adversarial cases: same/different effect IDs, two roles choosing conflicting effects, late retry after newer generation, wide publication under an endless stream of local commits, rate-limit interruption, response loss, role add after wide proposal, and a worker unable to observe another role's local state.

Target: determine whether safety **and finite wide-operation liveness** can be obtained under current CLEAN isolation with no shared semantic coordinator. If not, isolate the minimal cross-role-readable authority primitive as an exact unresolved child rather than disguising it as a handoff.
