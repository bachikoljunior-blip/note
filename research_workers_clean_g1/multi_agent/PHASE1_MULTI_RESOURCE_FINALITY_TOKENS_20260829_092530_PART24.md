# Phase-1 multi-agent multi-resource finality-token composition

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `9670b94c746a4abcc5ddecc357fb79b00f6a101f`
- frozen DESIRED_STATE: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport mode: `sha_only_exact_sha`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_STATUS_COMMIT_TOCTOU_20260829_092530_PART23.md`
- script: `research_workers_clean_g1/multi_agent/phase1_multi_resource_finality_tokens_20260829_092530_part24.py`
- result: `research_workers_clean_g1/multi_agent/phase1_multi_resource_finality_tokens_20260829_092530_part24.json`

## Objective

Part23 reduced single-resource terminal safety to an absorbing sink-side finality proof or compare-and-seal. This leaf asks whether several independently versioned resource proofs can simply be collected and conjoined.

The modeled vector has two 30-unit resources (`R1`, `R2`) plus an already-stable 40-unit component. Each required 30-unit resource can begin settled or failed. A failed resource needs one stable-identity 30-unit replacement. Tokens/resources may flip, expire, or be revoked between collecting the first and second proof and again after the final recheck but before repository publication.

## Public mechanism audit

Current etcd documentation provides a useful vector-level conditional-mutation precedent: a transaction can atomically evaluate a conjunction of comparisons over multiple keys and apply the success block as one transaction/revision. This is stronger than sequential independent current reads: https://etcd.io/docs/v3.6/learning/api/ and https://etcd.io/docs/v3.7/learning/api/

Revocation is a separate semantic dimension. OAuth 2.0 Token Revocation (RFC 7009) specifies that revocation invalidates a token and notes that propagation delay can exist across servers: https://datatracker.ietf.org/doc/rfc7009/

These are mechanism analogies only. An etcd transaction does not make an unrelated external effect sink transactional, and an OAuth token is not a compensation-finality certificate. The modeled distinction is simply **revocable current proof vs absorbing finality proof**.

## Finite model

The executable model enumerates **18,816 equal-weight synthetic scenarios** over:

- `R1` initial status: settled/failed;
- `R2` initial status: settled/failed;
- mid event after first proof but before second: none, resource flip, token revoke, or token expiry on either resource;
- post event after last check: same event set;
- proof acquisition order: R1 first / R2 first;
- independently absorbing token availability: yes/no;
- current-writer verifier: available/outage;
- takeover: no/yes;
- repository CAS outcome: confirmed, ambiguous-applied, ambiguous-not-applied;
- repeated recovery: no/yes.

A terminal is labeled unsafe if either the final amount vector is not exactly `{R1:30,R2:30}` **or** a component authority token used by the certificate has become stale/revoked/expired. Repository CAS itself uses a stable applied-transition ID, so this leaf isolates vector proof composition.

Policies:

1. sequential revocable/current tokens;
2. sequential tokens plus one authoritative recheck of all components immediately before repository CAS;
3. per-resource compare-and-seal, each component becomes independently absorbing when sealed;
4. one vector-level atomic compare-and-seal over both required resources;
5. independently absorbing per-resource tokens, but only when that sink capability is available.

## Result 1: sequential current tokens do not compose into a current vector

`SEQUENTIAL_REVOCABLE_TOKENS` terminalized 9,800 scenarios; **9,000 were unsafe** and only 800 were safe terminals in this deliberately adversarial balanced lattice.

A focused 64-case slice starts with both resources settled and revokes/expires the **first** token before the second token is collected. Sequential collection terminalized **64/64 unsafely**. Rechecking all components later refreshed that token and was safe 64/64, showing that the first token was a point-in-time capability rather than an immutable component proof.

The 9,000/9,800 ratio is not a production risk estimate. The lattice intentionally gives token invalidation/resource transition mechanisms equal synthetic weight.

## Result 2: rechecking the whole vector simply moves the TOCTOU boundary

`RECHECK_ALL_THEN_REPO` terminalized 8,960 scenarios but **7,680 were unsafe**. It fixes events that happened before the recheck but cannot protect against events after it.

In 128 focused cases, both resources were initially settled and a token was revoked/expired **after** the last recheck. The policy terminalized **128/128 unsafely**. In another 32 focused cases, a resource flipped after the last recheck; it terminalized **32/32 unsafely**.

Thus repeated current reads improve freshness but do not convert revocable proofs into an atomic vector commitment.

## Result 3: independently absorbing per-resource seals safely compose for this decomposable invariant

`PER_RESOURCE_COMPARE_AND_SEAL` terminalized **9,800** scenarios with **0 unsafe terminals**, duplicate replacements 0, and duplicate repository transitions 0.

The first sealed resource remains absorbing while the worker processes the second. A mid-event targeting the unsealed second resource is handled when the second resource is sealed; a mid/post event targeting an already sealed resource is rejected by the modeled sink semantics.

This gives an important refinement to Part23: **vector-level atomicity is not always required**. If each component finality proof is independently absorbing and the parent invariant is decomposable as a conjunction of per-resource exact obligations, sequentially collected component seals can compose safely.

## Result 4: vector atomic seal is also safe, but coarser

`VECTOR_ATOMIC_SEAL` also terminalized **9,800** scenarios with unsafe terminal 0. It used one protected vector operation per terminal (9,800 modeled protected operations), whereas per-resource sealing used two per terminal (19,600 modeled protected operations).

The trade-off is not simply “fewer calls is better.” A 2-case liveness micro-control makes one required component temporarily hot/unsealable. Per-resource sealing durably finalized the unaffected component in **2/2** cases; the coarse vector seal made durable component progress in **0/2** until the whole vector could seal. This is a mechanism illustration, not a production contention rate.

For decomposable obligations, per-resource absorbing seals preserve more partial progress/parallelism; for cross-component invariants, a vector-level seal may still be necessary.

## Result 5: token semantics, not token existence, decide safety

`ABSORBING_PER_RESOURCE_TOKENS` is deliberately enabled in only half the lattice. It terminalized 4,900 scenarios, all safe, and failed closed elsewhere. In the subset with absorbing-token capability plus confirmed repository CAS it produced **1,960 safe terminals / 0 unsafe**.

A signed/current token that can later expire or revoke is not equivalent. The certificate must know whether the token is:

- merely current at issuance;
- revocable/expiring;
- or absorbing for the finality claim being persisted.

## Result 6: repository response loss remains an independent solved layer

There are 6,272 ambiguous repository-CAS scenarios with repeated recovery. Stable applied-transition identity keeps the maximum repository terminal write at **1** and duplicate repository transition at **0/6,272**.

Again, local idempotency cannot compensate for an invalid component finality token; the two proof obligations are orthogonal.

## Candidate protocol refinement

For a parent effect-vector, annotate each component finality proof with explicit semantics:

- resource/effect ID and original-effect binding;
- exact amount/range segment;
- status version;
- proof type: `CURRENT_ONLY / REVOCABLE / EXPIRING / ABSORBING`;
- revocation/expiry authority if applicable;
- replacement lineage;
- claim epoch only as writer authority, never logical effect identity.

Composition rule:

1. if every required component carries independently **absorbing** finality and the invariant is a decomposable conjunction, sequential per-resource sealing is safe;
2. if any component proof is revocable/current-only, the vector is nonterminal unless the sink offers a vector-level atomic seal/currentness mechanism covering all such components;
3. cross-component conservation constraints that cannot be decomposed require a vector-level authority boundary even when individual status observations are current;
4. repository CAS then persists only the already-final vector proof and uses stable transition identity for response-loss reconciliation.

## Generic protected boundary

The generic protected remainder is narrower than “must have one global transaction”:

> The sink/status authority must provide either independently absorbing per-resource finality/seal semantics for every component of a decomposable effect-vector, or a vector-level atomic compare-and-seal for components whose validity can otherwise change. Revocable/expiring current tokens cannot be upgraded to immutable vector finality by repository logic alone.

Classification: `downstream_verification_required`. No global Phase-1 closure is claimed.

## Exact continuation

Next non-conflicting Phase-1 leaf: **cross-component invariant coupling**. Keep two 30-unit components but add a shared global constraint such as `exact total=60 and exactly one active replacement lineage per original obligation`, then allow transfer/reallocation between components while per-resource seals are individually valid. Compare:

1. independently absorbing per-resource seals;
2. per-resource seals plus immutable allocation contract fixed before any seal;
3. vector-level compare-and-seal over allocation + resources;
4. escrow-style disjoint capacity tokens whose sum is conserved;
5. fail-closed when allocation changes after the first component seal.

Primary falsification: independent finality of each component does not automatically prove a cross-component invariant if the allocation contract itself can change between seals. Measure false terminality, unused/overcommitted capacity, safe partial progress and how much vector serialization is actually necessary. Preserve stable replacement/effect identity and the existing sink-side authority boundary.

Keep the Phase-1 frontier nonempty; do not restore unrelated base work while the overlay remains active.
