# Phase-1 guard-epoch inclusion in claims is not sink fencing

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `14da1e90bd00bd8883a4276e54a985790b3e2a7a`
- frozen DESIRED_STATE: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_PROTECTED_BOUNDARY_DEPTH_20260829_085803_PART15.md`
- script: `research_workers_clean_g1/multi_agent/phase1_guard_epoch_claim_fencing_20260829_085803_part16.py`
- script SHA-256: `35224afe0ab63150873c39de2ff8b5a0669733f89c612abc11872e7ecee6e36c`
- result: `research_workers_clean_g1/multi_agent/phase1_guard_epoch_claim_fencing_20260829_085803_part16.json`
- result SHA-256: `f1745b17fec9fbcddf4def649eea86f89201d95f1b18aa6cb57fd94b7e06465e`

## Objective

Test whether carrying a protected-authority `guard_epoch` inside a multi-agent task/effect claim is itself sufficient to fence stale authority after the guard moves from `e1` to `e2`, or whether the epoch is only descriptive metadata until the authoritative sink compares it against current authority at effect application.

This leaf keeps the previous protected-boundary result fixed: CLEAN does not install or mutate the protected guard. It only models how ordinary role-local claims, immutable staging and publication should bind to a guard epoch if such an epoch exists.

## Finite model

The executable model enumerates **72 equal-weight synthetic scenarios** over:

- authority timing: `STABLE_E1 / E2_BEFORE_CLIENT_READ / E2_AFTER_CLIENT_READ_BEFORE_EFFECT`;
- old e1 publication response: `CONFIRMED / AMBIG_APPLIED / AMBIG_NOT_APPLIED`;
- immutable staged-result contract: exact `MATCH / MISMATCH` under the fresh e2 claim;
- sink dedupe: `VALID / EXPIRED`;
- current guard verifier: `AVAILABLE / OUTAGE`.

Compared policies:

1. claim identity omits guard epoch and the sink never checks it;
2. claim identity includes guard epoch but the sink never checks it;
3. claim includes guard epoch and the client reads current guard before publication;
4. authoritative sink atomically checks current guard epoch at effect application;
5. fresh e2 claim plus exact staged-result revalidation plus sink-time atomic epoch check;
6. fail closed whenever guard proof is unavailable.

The model treats `guard_epoch` as application/protocol metadata. It does **not** claim GitHub natively provides such an epoch field. The closest public mechanism precedent remains server-side protected-ref enforcement: a server-enforced invariant can reject a forbidden ref update at the effect boundary, whereas a client observation before the write is only an observation.

## Result 1: adding guard epoch to the claim key alone changes no authoritative safety outcome

`claim_no_guard_epoch_no_sink_check` and `claim_guard_epoch_no_sink_check` are behaviorally identical across all **72/72** scenarios. Each accepts the old e1 effect in all 72 scenarios, produces **48 unsafe stale effects** after authority has moved to e2, and creates **24 old-plus-new duplicate effects** when dedupe has expired. Each also has 12 ambiguous-response retry duplicates.

In the targeted transition-before-client-read slice, the guard-epoch key-only policy accepts stale e1 authority in **24/24** scenarios. Therefore the epoch is merely a label unless some authoritative component compares it against current authority.

This is the same separation seen earlier between lease metadata and a fencing token: identity can distinguish work, but it cannot cause an external authority sink to reject a stale holder by itself.

## Result 2: client read-each verification still has the same TOCTOU hole

`claim_guard_epoch_client_read` rejects old e1 work when e2 is already visible before the read, but in the `E2_AFTER_CLIENT_READ_BEFORE_EFFECT` targeted slice it still records **12 unsafe stale effects** among the 24 scenarios; the other 12 checkpoint because the verifier is unavailable.

Across the full model the client-read policy has 12 unsafe stale effects, 6 old-plus-new duplicates and 4 ambiguous retry duplicates. A successful client freshness read therefore does not become an atomic publication precondition.

## Result 3: sink-time epoch comparison eliminates stale-authority effects in the modeled scope

`claim_guard_epoch_sink_atomic` records **0 unsafe stale effects** and **0 old-plus-new duplicate effects**. In the targeted after-read/before-effect transition slice, every verifier-available old e1 attempt is rejected and the fresh e2 path publishes; verifier outage checkpoints rather than weakening the fence.

This result is deliberately narrow: the synthetic sink is assumed to compare the presented epoch to current guard authority atomically with effect application. If that atomicity is absent, the result does not transfer.

## Result 4: fencing and idempotency remain separate obligations

Even the sink-atomic policy still has **2 ambiguous retry duplicates**. Those occur while e1 remains current: the first effect was actually applied, its response was ambiguous, the dedupe window expired, and the retry is therefore duplicate despite perfect authority freshness.

So `guard_epoch` solves stale-writer authority only when checked by the sink; it does not solve response-loss/idempotency. A durable logical effect identity or sink-specific idempotency contract remains separately necessary.

## Result 5: stale computation may be reusable without reusing stale authority

The `reclaim_e2_exact_contract_sink_atomic` policy rejects all old e1 authority after transition. Where the immutable staged result's contract exactly matches the fresh e2 claim, it records **12 safe reuses** in the full model; where the contract mismatches, it records **12 rejected reuses**. In the targeted e2-before-read slice with verifier available there are 6 safe reuses and 6 mismatch rejections.

The key design rule is: computation/data reuse can cross an authority epoch only after exact revalidation, but the old claim/lease/epoch itself never crosses the boundary.

## Candidate protocol refinement

For ordinary Chat-capable work under a pre-existing guard epoch:

1. include `{guard_epoch, parent_generation, task_key, effect_keys, claim_epoch}` in reservation identity and immutable staging provenance;
2. do not treat that metadata as publication authority;
3. at authoritative integration/effect time, atomically compare the presented guard epoch (plus current claim/parent epoch) against the current authoritative sink/server invariant;
4. on verifier outage or inability to establish current epoch, checkpoint/fail closed;
5. if authority advances, issue a new claim under the new epoch; allow prior staged computation only after exact task/input/effect-contract digest revalidation;
6. independently carry durable effect identity/idempotency for ambiguous-response retry safety.

## Generic protected boundary

This leaf does not remove the protected remainder identified previously. It sharpens what ordinary CLEAN-side claims can do **after** a guard exists:

> `guard_epoch` in the claim is useful provenance and stale-work classification, but stale-authority safety requires a server/sink invariant that checks the current protected epoch at the effect boundary (or an equivalent atomic protected precondition). Installing, changing or globally validating that protected invariant remains outside this CLEAN role's executable authority.

Classification: `downstream_verification_required`.

## Exact continuation

Next non-conflicting Phase-1 leaf: **guard-epoch vector across multiple authoritative effect sinks**. Model a parent requiring two effects whose sinks can observe guard epochs asynchronously (`e1/e1`, `e2/e1`, `e2/e2`), one sink with durable idempotency and one with expiring dedupe, plus worker takeover and ambiguous response. Compare scalar parent guard epoch, per-sink epoch vector, sink-time atomic checks with a parent terminality certificate, and fail-closed serial integration. Test false parent terminalization, stale effect acceptance, duplicate effect, recoverability and staged-result reuse. Primary falsification: determine whether parent terminality may rely on a scalar epoch when sinks transition asynchronously, or must carry a vector/certificate proving each required effect under its own current authority and durable effect identity.

Keep the Phase-1 frontier nonempty; do not restore unrelated base work while the overlay remains active.
