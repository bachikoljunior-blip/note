# Phase-1 multi-agent cross-component allocation generation fencing

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `9670b94c746a4abcc5ddecc357fb79b00f6a101f`
- frozen DESIRED_STATE: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport mode: `sha_only_exact_sha`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_MULTI_RESOURCE_FINALITY_TOKENS_20260829_092530_PART24.md`
- script: `research_workers_clean_g1/multi_agent/phase1_cross_component_allocation_20260829_092530_part25.py`
- result: `research_workers_clean_g1/multi_agent/phase1_cross_component_allocation_20260829_092530_part25.json`

## Objective

Part24 showed that independently absorbing per-resource seals can safely compose when the parent invariant is a fixed conjunction of decomposable component obligations. This leaf attacks the hidden assumption: **what if the allocation contract itself changes while those individually final components are being sealed?**

The parent obligation totals 60. Generation 1 allocates `{R1:30,R2:30}`. A generation-2 reallocation may become `{20,40}`, `{40,20}`, or an ABA case with the same numeric `{30,30}` but a new authority generation. The reallocation can occur before the first resource seal, between resource seals, or after both component seals but before parent terminal publication.

This isolates cross-component allocation authority. The sink-side per-resource seal itself is assumed absorbing, as established in Part24.

## Public mechanism audit

Current FoundationDB documentation provides a useful same-authority transaction precedent: default transactions are strictly serializable, concurrent read/write conflicts cause one transaction to fail, and explicit conflict ranges can tighten which keys participate in concurrency detection: https://apple.github.io/foundationdb/developer-guide.html

The same guide/API also documents `commit_unknown_result`, where a client may not know whether commit succeeded and a blind retry can execute a transaction twice unless application logic handles that ambiguity: https://apple.github.io/foundationdb/javadoc/com/apple/foundationdb/Transaction.html

Current etcd transactions similarly allow a conjunction of version/value comparisons across keys to be tested atomically before one success block: https://etcd.io/docs/v3.6/learning/api/

These are mechanism precedents only. The result below is about a repository-defined immutable parent allocation generation and sink proofs bound to that digest; it does not claim FoundationDB/etcd governs an unrelated external effect sink.

## Finite model

The executable model enumerates **480 equal-weight synthetic scenarios** over:

- reallocation event: none, or `SWAP / SHIFT / ABA` at `BEFORE_FIRST / BETWEEN / AFTER_SECOND`;
- component sealing order: R1 first / R2 first;
- current parent-generation verifier: available/outage;
- takeover: no/yes;
- repository CAS outcome: confirmed, ambiguous-applied, ambiguous-not-applied;
- repeated recovery: no/yes.

Every component token records its local resource amount, allocation generation, and full allocation-contract digest. Terminal safety requires both component amounts to equal the **current** allocation and both tokens to belong to the current parent/allocation generation.

Policies:

1. independently final resource tokens, but only each local amount is trusted;
2. full allocation value digest is compared, but generation is omitted;
3. each token binds `{parent/allocation generation, full allocation digest}` and parent terminal CAS rechecks current generation;
4. allocation contract is frozen immutable for the parent generation before component effect work starts; reallocation must create a new parent generation rather than mutate this one;
5. one vector-level allocation/resource seal.

## Result 1: independent resource finality does not prove a mutable allocation invariant

`PER_RESOURCE_LOCAL_ONLY` terminalized 400 scenarios; **240 were unsafe**.

A focused 16-case slice reallocates `{30,30}` to `{20,40}` or `{40,20}` **between** the two resource seals. Each component is individually final for the allocation it saw, but their conjunction mixes generations. The local-only policy terminalized **16/16 unsafely**.

This is the exact boundary left open by Part24: component finality composes only relative to a stable shared contract.

## Result 2: full value equality is still ABA-unsafe without allocation generation

`VALUE_DIGEST_ONLY` reduced unsafe terminals to 40, but did not eliminate them. In a focused 8-case ABA slice, both component tokens still carry numeric allocation `{30,30}` while the parent has moved from generation 1 to generation 2 with the same values. Value-digest comparison terminalized **8/8 unsafely**.

`GENERATION_BOUND_RECHECK` terminalized **0/8** in the same slice. Numeric equality proves content equality, not authority/incarnation equality.

This is the same identity principle seen earlier for logical object reuse: a current generation/epoch is independent of the user-visible value.

## Result 3: binding resource proofs to parent generation + immutable allocation digest is safe

`GENERATION_BOUND_RECHECK` terminalized **80** scenarios, all 80 safe, with unsafe terminal 0. It intentionally fails closed if allocation generation changed after one or both component seals or if the current generation cannot be verified.

In the 16-case between-reallocation slice it terminalized **0/16**, avoiding mixed-generation composition. In 24 cases where the new generation existed **before** component work began, it resolved the new generation and terminalized **24/24 safely**.

Therefore a vector-level sink transaction is not required merely because several independently absorbing component proofs are combined. The minimum condition in this tested scope is:

`every component proof binds the same immutable {parent_generation, allocation_contract_digest} AND parent terminal publication proves that generation is still current`.

## Result 4: freezing the allocation contract is safe but stronger than necessary

`FROZEN_ALLOCATION_CONTRACT` terminalized 400/480 scenarios, all safe. In this model, once effect work for a parent generation starts, attempts to mutate that generation's allocation are rejected; legitimate reallocation must create a new generation.

This maximizes same-generation liveness but imposes a stronger coordination rule: allocation cannot be edited in place after work starts.

The generation-bound/recheck policy permits new generations but checkpoints old mixed-generation work instead. Which policy is preferable is a liveness/product decision, not a safety equivalence.

## Result 5: vector-level atomic seal is also safe but not minimal for this decomposable allocation

`VECTOR_ALLOCATION_SEAL` terminalized 400 scenarios with unsafe terminal 0. It incorporates reallocation that happened before the vector seal and rejects in-generation reallocation afterward.

This proves a stronger boundary than required. In the same synthetic scope, per-resource absorbing seals plus immutable allocation digest + parent generation fencing are sufficient. That keeps more finality work decomposable and avoids requiring one protected vector transaction across all external resources.

## Result 6: repository response-loss identity remains orthogonal

Across 160 ambiguous repository-CAS scenarios with repeated recovery, stable applied-transition identity kept maximum repository writes at 1 and duplicate repository transition at **0/160**.

FoundationDB's documented `commit_unknown_result` is a public reminder that transaction atomicity does not automatically solve client uncertainty; application-level durable transition identity/reconciliation remains useful even when the underlying transaction is atomic.

## Candidate protocol refinement

The current candidate can now avoid unnecessary vector serialization when all of these are true:

1. parent generation has an immutable allocation contract/digest;
2. each logical resource/segment proof binds that exact `{parent_generation, allocation_digest}`;
3. each component seal is independently absorbing in the sink authority domain;
4. allocation changes create a new generation rather than mutating the meaning of an existing generation;
5. parent terminal CAS rechecks current generation and rejects mixed/stale proofs;
6. repository terminal transition uses stable applied-transition identity for response-loss recovery.

If those conditions hold, per-resource parallel effect finalization remains safe even though the aggregate allocation is a cross-component invariant.

## Generic protected boundary

The protected remainder is **not** enlarged to a mandatory global vector transaction:

> The sink must still enforce each per-resource absorbing finality seal against the supplied immutable `{parent_generation, allocation_contract_digest}`. No additional vector-level sink primitive is required in the tested decomposable scope when allocation immutability/current-generation fencing is authoritative in the repository/parent domain. If the allocation contract itself is mutable only in an external authority domain that CLEAN cannot current-fence, then a vector-level atomic finalization remains required.

Classification: `downstream_verification_required`. No global Phase-1 closure is claimed.

## Exact continuation

Next non-conflicting Phase-1 leaf: **allocation-generation supersession and safe reuse of already sealed component effects**. When parent generation g1 is superseded by g2, some g1 resources may be semantically identical to g2 requirements. Compare:

1. discard every g1 seal and re-execute all effects;
2. reuse by resource name/amount only;
3. reuse by exact immutable `{original_effect_id, amount/range, effect_contract}` but without an explicit g2 adoption record;
4. g2 adoption CAS that revalidates current sink resource finality and records `adopted_from_generation=g1` under g2 allocation digest;
5. vector adoption when several component resources share a coupled allocation constraint.

Enumerate unchanged vs changed component requirements, partial g1 completion, g1 late reversal after g2 adoption, takeover, ambiguous adoption CAS, and ABA g1->g2 same visible allocation. Primary falsification: content-equivalent old seals may still lack g2 authority, while always re-executing wastes irreversible work and can duplicate external effects. Determine the minimum adoption proof that converts old finality into current-generation authority without reapplying the effect.

Keep the Phase-1 frontier nonempty; do not restore unrelated base work while the overlay remains active.
