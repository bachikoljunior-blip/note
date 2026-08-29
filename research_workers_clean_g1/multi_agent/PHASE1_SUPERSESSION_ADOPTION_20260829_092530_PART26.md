# Phase-1 multi-agent generation supersession and safe effect adoption

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `9670b94c746a4abcc5ddecc357fb79b00f6a101f`
- frozen DESIRED_STATE: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport mode: `sha_only_exact_sha`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_CROSS_COMPONENT_ALLOCATION_20260829_092530_PART25.md`
- script: `research_workers_clean_g1/multi_agent/phase1_supersession_adoption_20260829_092530_part26.py`
- result: `research_workers_clean_g1/multi_agent/phase1_supersession_adoption_20260829_092530_part26.json`

## Objective

Part25 requires every component proof to bind the current parent generation and immutable allocation digest. That raises a practical supersession problem: when `g1` becomes `g2`, an already-sealed external effect may be **exactly the effect g2 still needs**. Re-executing it can duplicate an irreversible effect, but silently treating old authority as current also violates the generation fence.

This leaf models reuse as an explicit authority transition—**adoption**—instead of either a cache hit or unconditional replay.

## Public mechanism audit

Kubernetes provides a useful public ownership/adoption analogy:

- a valid `OwnerReference` carries the owner's `uid`, not just its visible name: https://kubernetes.io/docs/reference/kubernetes-api/definitions/owner-reference-v1-meta/
- Kubernetes documents that ownership differs from selector/label matching and that owner references help controllers avoid interfering with objects they do not control: https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/
- ReplicaSet documentation explicitly says a matching Pod without a controlling OwnerReference can be acquired, after which the Pod carries the ReplicaSet's identifying owner information: https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/

This is a mechanism analogy, not a claim that Kubernetes adoption is an external-effect exactly-once protocol. The relevant pattern is that **matching content/selector and current ownership are separate facts**, and adoption establishes current ownership explicitly.

## Finite model

The executable model enumerates **20,736 equal-weight synthetic scenarios** over two g2 component requirements:

- relation of each g1 resource to g2: `EXACT / CONTRACT_CHANGED / AMOUNT_CHANGED`;
- g1 resource: sealed or missing;
- g1 proof per resource: absorbing or current-only;
- late invalidation of neither/R1/R2;
- current g2-generation verifier: available/outage;
- no-effect reseal/finality operation: available/unavailable;
- adoption/repository CAS result: confirmed, ambiguous-applied, ambiguous-not-applied;
- repeated recovery: no/yes;
- takeover: no/yes.

`CONTRACT_CHANGED` deliberately preserves the same visible resource name and amount while changing immutable effect semantics. The model treats changed-contract old effects as outside the current g2 requirement; cleanup/compensation of those old effects is a separate future branch.

Policies:

1. discard all g1 work and re-execute every g2 effect;
2. adopt by visible resource name/amount;
3. reuse exact immutable effect contract but **without a g2 adoption record**;
4. per-resource g2 adoption: exact contract + current g2 generation/allocation + absorbing old proof or successful no-effect reseal + stable g2 adoption CAS;
5. vector g2 adoption with the same proof rules but all-or-nothing preflight.

## Result 1: always re-executing old exact effects is not a safe fallback

`DISCARD_REEXECUTE` terminalized 8,640 scenarios; **2,240 were unsafe**, and **2,688 scenarios created duplicate external effects** at execution time.

A focused 8-case slice has both g1 resources already sealed, exact for g2, with absorbing finality and current generation verifier available. Discard/re-execute terminalized **8/8 unsafely** and duplicated both already-satisfied logical effects.

This eliminates “just redo it under g2” as a generic supersession fallback for irreversible effects.

## Result 2: exact content reuse still needs a current-generation adoption record

`EXACT_CONTRACT_REUSE_NO_ADOPTION` terminalized 8,880 scenarios and false/unsafe-terminalized **2,880**. In the same focused exact/absorbing 8-case slice, it terminalized **8/8 unsafely** despite creating no duplicate effect.

The external truth is correct, but the current g2 authority proof is missing. In this model, that distinction is deliberate: terminality requires not just “a matching effect exists” but “g2 has explicitly accepted that effect as satisfying its current immutable obligation.”

This is the adoption analogue of Kubernetes owner UID vs selector/name matching.

## Result 3: name/amount adoption is too weak for effect semantics

`NAME_AMOUNT_ADOPT` terminalized 9,600 scenarios with **3,840 unsafe terminals**.

A focused 16-case slice gives R1 the same visible name/amount but changes its immutable effect contract. Name/amount adoption terminalized **16/16 unsafely**. Strong adoption instead executed the changed g2 effect and terminalized **16/16 safely**.

Therefore adoption equivalence must include the immutable original-effect/segment/effect-contract identity, not only display identity or amount.

## Result 4: strong g2 adoption is safe in the tested lattice

`G2_PER_RESOURCE_ADOPTION` terminalized **7,950** scenarios, all 7,950 safe, with duplicate external effects 0 and duplicate adoption records 0.

For an exact g1 resource it requires:

1. exact immutable `{original_effect_id, amount/range, effect_contract}` match;
2. current g2 `parent_generation + allocation_contract_digest`;
3. old sink resource finality that is already absorbing, **or** a protected no-effect reseal that converts current-only finality into an absorbing proof without replaying the business effect;
4. stable g2 adoption identity, for example `H(g2_generation, old_resource_id, old_final_version, allocation_digest)`;
5. adoption record `adopted_from_generation=g1` persisted under g2;
6. current g2 generation rechecked at parent terminal publication.

The record is authority lineage, not a second external effect.

## Result 5: current-only old proof cannot be adopted from a point-in-time read alone

A focused 4-case slice gives R1 an exact g1 resource whose proof is only current-at-read, then invalidates it after weak adoption. Name/amount adoption terminalized **4/4 unsafely**.

When no no-effect reseal exists, the strong policy terminalized **0/4** and failed closed. When reseal is available, another 4-case slice safely resealed/adopted and terminalized **4/4**.

This reuses Part23's TOCTOU result rather than adding another read loop: current-only old finality must become absorbing before g2 adopts it.

## Result 6: per-resource adoption preserves partial progress better than vector adoption

Both strong policies have identical terminal safety counts here: 7,950 safe terminals / unsafe 0. Their liveness differs.

In a focused 12-case slice, R1 is exact + absorbing while R2 is exact + current-only and cannot be resealed. Per-resource adoption durably adopts the safe R1 component in **12/12** before checkpointing on R2; vector adoption makes **0/12** component adoption progress because preflight fails the whole vector.

Across the full lattice, per-resource strong adoption has 426 nonterminal scenarios with some durable adoption progress vs 390 for vector adoption; those aggregate counts also include CAS/recovery shapes, so the focused slice is the clearer mechanism comparison.

When allocation invariants are already frozen by Part25, per-resource adoption remains the smaller safe unit.

## Result 7: ambiguous adoption/repository CAS is reconciled by stable IDs

There are 6,912 ambiguous-CAS scenarios with repeated recovery. Stable adoption/terminal identities produce duplicate adoption record **0/6,912** and at most one repository terminal write.

Takeover changes writer authority but not adoption identity. A new claim epoch therefore resumes/reconciles the same logical `g1 resource -> g2 obligation` adoption instead of minting another adoption record.

## Candidate protocol refinement

Supersession handling now has three disjoint branches per component:

1. **exact + absorbing old proof** → adopt into current g2 with stable adoption CAS, no external effect replay;
2. **exact + current-only old proof** → no-effect reseal/finalize, then adopt; if reseal unavailable or ambiguous beyond recovery, fail closed;
3. **changed/missing old proof** → execute the new g2 effect under the normal current-writer/current-generation sink fence.

Never use “re-execute everything” as a generic fallback for exact irreversible effects, and never treat exact-content equality itself as g2 authority.

## Generic protected boundary

The protected remainder narrows again:

> The sink/status domain must expose either an already-absorbing old resource proof or a no-business-effect reseal/finality operation that can make a CURRENT_ONLY old resource safe for adoption. The repository/CLEAN side can perform all exact-contract equivalence checks, current-g2 generation/allocation checks, stable adoption IDs, `adopted_from_generation` lineage, per-resource partial adoption, and parent CAS reconciliation. It cannot manufacture absorbing sink finality for an old resource.

Classification: `downstream_verification_required`. No global Phase-1 closure is claimed.

## Exact continuation

Next non-conflicting Phase-1 leaf: **adoption invalidation and compensation cleanup for changed old effects**. The current model treats changed-contract g1 effects as outside g2 requirements. Extend it so supersession may require compensating or retiring those old effects while simultaneously adopting unchanged components.

Compare:

1. adopt unchanged + blindly execute changed g2 effects, leaving g1 changed effects live;
2. compensate every superseded g1 effect before any g2 progress;
3. per-component transition state `OLD_ACTIVE -> COMPENSATING -> RETIRED`, then adopt/execute g2 only after that component's old authority is final;
4. vector-wide retire-then-activate barrier;
5. escrow/capability transfer where old and new effect cannot be simultaneously authoritative.

Enumerate ambiguous old-effect compensation, late compensation failure/reversal, current-only vs absorbing old proof, partial adoption of unaffected components, takeover, response loss, and a g2 effect created before g1 retirement becomes final. Primary falsification: exact adoption solves unchanged effects, but changed-effect supersession still needs a non-overlap transition so old and new conflicting external authorities are not simultaneously live. Determine whether that transition can remain per-component or requires a coupled vector barrier.

Keep the Phase-1 frontier nonempty; do not restore unrelated base work while the overlay remains active.
