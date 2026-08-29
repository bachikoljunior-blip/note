# Phase-1 multi-agent status-read to terminal-commit TOCTOU

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `9670b94c746a4abcc5ddecc357fb79b00f6a101f`
- frozen DESIRED_STATE: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport mode: `sha_only_exact_sha`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_STATUS_VERSION_ORDER_20260829_092530_PART22.md`
- script: `research_workers_clean_g1/multi_agent/phase1_status_commit_toctou_20260829_092530_part23.py`
- result: `research_workers_clean_g1/multi_agent/phase1_status_commit_toctou_20260829_092530_part23.json`

## Objective

Part22 showed that a terminal effect-vector certificate needs a proof of current resource status, not merely the highest observed event/version. This leaf asks the next question: **what happens after a genuinely authoritative current read but before repository terminal publication?**

The race is:

`authoritative sink read(v3) -> optional replacement/current check -> sink v4 transition -> repository terminal CAS`.

The core falsification target is that even a correct v3 read becomes stale if the external sink remains free to invalidate that state before a separate repository CAS.

## Public mechanism audit

Two current public mechanisms establish the boundary precisely:

- HTTP `If-Match` makes the target mutation conditional on the target resource's current strong ETag; if it no longer matches, the mutation fails with `412 Precondition Failed`. MDN describes this as optimistic locking / lost-update prevention: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/If-Match and https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Conditional_requests
- Kubernetes updates carry the target object's `resourceVersion`; a stale update is rejected with `409 Conflict`, and the documentation recommends conditional update for lost-update detection: https://kubernetes.io/docs/reference/using-api/api-concepts/

These are positive precedents for **same-authority-domain** conditional mutation. They do not imply that a conditional read/compare against an external sink can atomically guard a later mutation in a separate repository authority domain. That cross-domain gap is exactly what the finite model tests.

## Finite model

The executable model enumerates **1,152 equal-weight synthetic scenarios** over:

- v3 resource status: `SETTLED / FAILED`;
- later transition: same status, status flip, or `REVERSED`;
- transition point: none, before re-read, between re-read and sink check, or after sink check but before repository CAS;
- absorbing finality token available: yes/no;
- current-writer verifier: available/outage;
- takeover: no/yes;
- repository CAS response/truth: confirmed applied, ambiguous applied, ambiguous not-applied;
- repeated recovery: no/yes.

Original effect B is fixed exactly satisfied at 40; A requires 60. A `FAILED/REVERSED` old resource needs one 60-unit replacement. If the old resource later becomes `SETTLED` after replacement, A is over-compensated; if a previously settled resource later fails/reverses without replacement, A is under-compensated.

Every policy uses a stable repository `applied_transition_id`, so repository response-loss retry is already at-most-once. This isolates the external-status-to-repository-publication boundary.

Policies:

1. authoritative read v3, then repository terminal CAS;
2. persist a durable v3 witness, then repository terminal CAS;
3. authoritative re-read immediately before repository CAS;
4. conditional compare in the sink, then repository CAS, but the compare **does not seal** future sink transitions;
5. sink compare-and-seal: current status is checked and the exact resource/replacement vector is atomically made non-invalidatable before repository publication;
6. repository publication only after receiving an already-absorbing finality token; if no such token exists, fail closed.

Counts are synthetic mechanism counts, not production failure rates.

## Result 1: durable witness records a point in time; it does not freeze the source

`READ_THEN_REPO_CAS` terminalized 720 scenarios and false-terminalized **300**. `DURABLE_V3_WITNESS_REPO_CAS` has exactly the same 720 / **300** result.

Across 288 scenarios with some sink transition and a confirmed repository CAS, the one-read policy terminalized 216 and false-terminalized **120**. Persisting the v3 witness also terminalized 216 and false-terminalized **120**.

A durable witness is essential provenance, but unless its semantics are absorbing it proves only what was true at v3.

## Result 2: re-read closes only races that happened before that re-read

A focused 16-case slice starts with `SETTLED`, invalidates to failed/reversed **before** the re-read, has verifier available, and uses a confirmed repository CAS. The original one-read protocol false-terminalized **16/16**. The re-read saw the invalidation, created the required replacement, and was exact **16/16**.

Globally, `REREAD_THEN_REPO_CAS` improved to 700 terminals with **200 false terminals**, down from 300, but did not eliminate the TOCTOU.

## Result 3: even an authoritative sink compare is insufficient if it does not seal future transitions

The sharpest slice contains 32 scenarios where v3 is settled and the invalidating transition occurs **after the last sink check but before repository CAS**. Both a re-read and a sink-local conditional compare terminalized **32/32 falsely**.

`SINK_COMPARE_ONLY_THEN_REPO_CAS` has 680 terminals / **100 false terminals** overall. This matters because a correct `If-Match` or `resourceVersion` compare protects the mutation that is conditional on it; it does not magically guard a later mutation in another system.

The mirror race is v3 `FAILED`: the worker creates a replacement, then the old resource flips to `SETTLED` after the check. In the focused 8-case slice the compare-only policy false-terminalized **8/8** by over-compensating A.

## Result 4: compare-and-seal removes the modeled cross-authority TOCTOU

`SINK_COMPARE_AND_SEAL` terminalized **680** scenarios, all 680 exact, with **0 false terminals**. In the 32-case post-check invalidation slice it was exact **32/32**; in the 8-case failed-then-old-settles slice it was exact **8/8**.

The modeled primitive is stronger than a read or ordinary compare: in the authoritative sink domain it atomically validates current resource status and then makes the specific finality/replacement vector non-invalidatable before returning. The repository may persist that finality result later because the sink-side state has been sealed against the transition that would invalidate it.

This is a candidate proof shape, not a claim that the currently available external effect system exposes such an operation.

## Result 5: an already-absorbing finality token is the other safe shape

`ABSORBING_FINALITY_TOKEN` terminalized **360** scenarios with false terminalization 0. It terminalizes only the half of the lattice where such a token exists; the other half fails closed.

In the 32-case post-check invalidation slice, 16 scenarios had a token and were exact; the 16 without one remained nonterminal. The important property is not token syntax or signing by itself. The token's semantics must guarantee that the represented final status cannot later be invalidated (or that invalidating transitions are conditioned on/revoke the same authority object before repository terminality can accept it).

## Result 6: repository CAS/idempotency is orthogonal and already solved locally

There are 384 scenarios with ambiguous repository CAS plus repeated recovery. The stable `applied_transition_id` keeps the maximum actual repository terminal write at **1**, with duplicate repository transition **0/384**.

That does not repair stale external truth: a perfectly idempotent repository CAS can still persist the wrong terminal decision. Storage idempotency and external semantic finality remain distinct proof obligations.

## Candidate protocol refinement

The Part19-Part22 identity/conservation rules remain, plus one new rule:

1. derive stable logical effect/segment/replacement identities independent of claim epoch;
2. maintain exact per-original resource-vector conservation over unique authoritative resource IDs;
3. require current status/version proof rather than delivery order/highest observed status;
4. **before repository terminal publication, convert that current point-in-time fact into an absorbing sink-side finality proof**;
5. that proof is either an already-absorbing finality token or a protected conditional seal/finalization operation in the same authoritative sink domain;
6. repository terminal CAS persists the token/vector with stable `applied_transition_id`; CAS response loss is reconciled locally without re-executing the external effect;
7. if the sink cannot provide absorbing finality/seal semantics, fail closed rather than treating re-read frequency as atomicity.

## Generic protected boundary

The minimal generic protected remainder is now:

> The external authoritative sink/status domain must either expose absorbing finality semantics for each effect resource or perform a conditional seal/finalization of the exact current effect-vector version before repository terminal publication. A CLEAN repository writer can perform all reads, version checks, stable-ID construction, conservation verification, checkpoints and repository CAS work, but cannot synthesize cross-authority atomicity from a prior read, ETag/resourceVersion compare, or durable witness if the sink remains free to invalidate the result afterward.

Classification: `downstream_verification_required`. This is not a global Phase-1 pass claim.

## Exact continuation

Next non-conflicting Phase-1 leaf: **multi-resource finality-token composition**. Replace the single A resource with two independently versioned resources plus B, and compare:

1. seal/token each resource independently, then repository terminal CAS;
2. acquire tokens sequentially while an earlier token may expire/revoke;
3. one vector-level atomic seal over all required resources;
4. independently absorbing per-resource tokens whose conjunction is immutable;
5. fail-closed vector certificate when even one component token is missing/stale.

Enumerate token expiry/revocation, status-version advance while sealing another resource, takeover, replacement lineage, response loss, and repository CAS retry. Primary falsification: individually current tokens collected at different times are not necessarily a current vector unless each token is independently absorbing for the entire decision interval or the sink offers vector-level atomic finalization. Measure false terminality, over/under-compensation, token churn/recovery cost and parallelism lost to coarse vector sealing.

Keep the Phase-1 frontier nonempty; do not restore unrelated base work while the overlay remains active.
