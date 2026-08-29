# Phase-1 multi_agent checkpoint — coordination-free algebraic redesign (Part 46)

## Frozen semantic tuple

- frozen authority commit: `302327074272033f246c5d8f555df61004e3802f`
- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `sha_only_exact_sha`
- predecessor: `PHASE1_CLEAN_ISOLATION_COORDINATION_20260830_043701_PART45.md`

Part 45 isolated the current CLEAN boundary for generic non-commutative failover: without a cross-role fence or authoritative sink-side epoch check, finite failover and stale-writer safety trade against one another. Part 46 asks how much of that problem can disappear by changing the effect algebra instead of adding a coordinator.

Executable model: `research_workers_clean_g1/multi_agent/phase1_algebraic_redesign_20260830_part46.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_algebraic_redesign_20260830_part46.json`

The finite lattice contains `1,440` scenarios and `10,080` strategy evaluations over effect algebra (`G-set`, content-addressed contribution, max register, escrow rights, non-commutative update), duplicate replay, two distinct payloads under one semantic key, owner crash/slow-late, generation supersession, whether a global reduction or all-role completeness proof is required, and repository interruption before or after the role-local write.

## Result 1 — CRDT-style additivity removes update conflict, but not necessarily the final reducer

For true grow-only-set semantics, `own_gset_contribution` is duplicate-safe and concurrency-safe in **288/288** supported scenarios. Each role can write its own additive fact inside its own namespace without reading another worker.

That does **not** mean 288 terminal outcomes. Only **24/288** are already terminal under the modeled current CLEAN boundary. Those 24 require all of the following:

- the role-local contribution itself is the useful terminal outcome;
- no global union/materialized reduction is required;
- no proof that all roles have contributed is required;
- no newer generation needs old contributions filtered out;
- the contribution owner did not crash before producing it.

The remaining 252 supported G-set cases require a cross-role reducer or current-generation/completeness filter.

Inria's SyncFree work is a useful mechanism precedent: CRDTs permit unsynchronised concurrent updates while preserving a consistency model. That supports the algebraic **update** claim, not the stronger claim that a CLEAN worker can materialize a final cross-role answer without reading other workers:
- https://radar.inria.fr/report/2013/regal/uid92.html

## Result 2 — content addressing is identity, not semantic conflict resolution

`own_content_addressed_contribution` deduplicates the same bytes/identity in all 288 supported content-addressed scenarios. But when two distinct payloads claim the same semantic key, **144/144** such cases still need a semantic reducer and are not concurrency-safe as a single-valued current result.

Two valid hashes answer “which bytes?” They do not answer “which of these conflicting values is authoritative?”

Only **12/288** supported content-addressed cases are already terminal in the model: no semantic-key conflict, no global reduction/completeness/current-generation filtering, and no crashed owner.

Thus content addressing is a strong retry/provenance primitive, but not a general multi-agent authority primitive.

## Result 3 — max/register candidates move conflict into reduction

A max/join register is algebraically friendly: local candidates can be replayed or concurrently generated without corrupting the candidate set. But `own_max_candidate` has **288/288** supported cases requiring a reducer and **0/288** terminal current-CLEAN outcomes in this model.

The reason is not safety of the candidate files. The useful effect is the **global/current maximum**, and materializing that value requires observing candidates from more than one role or delegating the join to a shared sink. The current CLEAN policy allows neither other-worker semantic reads nor an arbitrary shared reducer.

This is the central Part-46 distinction: algebraic convergence can turn a conflict into a deterministic merge rule, but somebody or something must still execute that merge if the merged value is the useful outcome.

## Result 4 — static escrow can preserve a global numeric invariant without hot-path coordination, by refusing failover transfer

`static_escrow_disjoint_rights` pre-partitions a bounded resource into disjoint local rights. Each role can spend only its own rights with role-local idempotency. In all **288/288** escrow scenarios the concurrent invariant is safe in the model.

This matches the bounded-counter/escrow CRDT mechanism described in the CRDT literature: the allowed decrements/rights are split among replicas so local decrements preserve the invariant while rights remain available:
- https://asc.di.fct.unl.pt/~nmp/pubs/tr-arxiv-crdt-2018.pdf

However the no-coordination variant deliberately does **not** reallocate rights after failure. In **96/96** owner-crash escrow scenarios, safety is preserved by stranding the crashed owner's rights, so terminal progress is blocked for the assigned operation. Only **48/288** supported escrow scenarios are already terminal without a global aggregate/completeness step.

A rights-transfer protocol would reintroduce exactly the authority/fencing question from Part 45: the old owner must be prevented from spending rights after they are transferred.

The current frozen root/config also does not define arbitrary cross-role escrow allocations, so this remains generic mechanism evidence, not an installed current route.

## Result 5 — deterministic single owner remains a liveness/freshness trade

For a non-commutative effect, deterministic single ownership avoids simultaneous writers without a shared runtime coordinator. But a crashed owner blocks progress, and all **48/48** slow-late plus generation-supersession cases retain stale-generation risk without an effect-time fence.

Only **36/288** supported single-owner cases are terminal in the model after excluding crash, stale generation and any required global reduction/completeness step.

Algebraic redesign helps where the operation itself can be made commutative/idempotent or pre-partitioned. It does not turn an arbitrary non-commutative current-authority mutation into a coordination-free effect.

## Result 6 — a shared CRDT sink and a fenced sink are useful positive controls, but they are not current CLEAN routes

A shared CRDT sink can execute the join so workers do not read one another. It supports the G-set/max/content-addressed classes in this model and materializes 480 terminal cases, but it is still a cross-role authoritative service. A fully fenced sink is the strongest positive control and is safe/terminal in **1,440/1,440** finite scenarios.

Neither is accepted as a Phase-1 dependency. The frozen root forbids adding hosted coordination/compute/quota-bearing infrastructure, and current CLEAN semantics do not expose an authorized arbitrary shared reducer/sink.

These controls are useful because they show what the local contribution files are missing: not “more hashing,” but **an authorized place that performs the join/current-generation/fencing rule**.

## Largest current-CLEAN-compatible terminal subclass found so far

The largest mechanism class that survives all current gates is narrower than “CRDT”:

> **An independently terminal role-local effect whose rights/state are already disjoint, whose operation is monotonic/idempotent for its own namespace, and whose useful outcome requires no cross-role aggregate, all-role completeness proof, revocation, current-generation filter, or failover transfer.**

This includes some local evidence publication and statically partitioned effects. It does not cover a global max, a current single-valued shared register, a reassignable escrow right, or a consolidated multi-role answer.

The final-reducer requirement is therefore a separate unresolved child, not a detail that can be hidden inside “eventual convergence.”

## Zero-dependency / zero-quota assessment

All accepted restricted cases use only role-local repository transport and local deterministic logic. No GitHub Actions, Codespaces, artifact/LFS/package storage, cloud compute, external model/API credit, richer-mode arbitration, protected-primary execution or manual user action is required. Incremental monetary cost is zero.

Public CRDT/escrow sources are mechanism evidence only. No external CRDT service or database is added to the route.

## Exact continuation

Next leaf: **can Git repository structure itself be an opaque, zero-compute Merkle accumulator/finalizer without semantic cross-role reads?**

Compare:

1. branch commit/tree SHA used only as an opaque snapshot certificate;
2. deterministic per-role content-addressed paths;
3. a finite expected-path set encoded only in sanitized root/config;
4. server-maintained Git tree composition from concurrent disjoint role-local writes;
5. a semantic reducer baseline.

Required adversaries: missing role contribution, duplicate same content in different role namespaces, stale generation, role add/remove, branch response loss, concurrent disjoint writes, and a malicious/conflicting payload hidden behind a valid blob hash.

Measure exactly what an opaque tree/root hash can certify without reading another worker's semantics: snapshot identity and perhaps inclusion if a sanctioned proof is available. Separately measure what it cannot certify: semantic correctness, required-role completeness when membership is dynamic, or a cross-role aggregate value. Treat reading other-role tree entries, path lists or contents as forbidden semantic input unless the frozen control explicitly authorizes a sanitized metadata surface; treat any server-side custom reducer as an unresolved external capability.
