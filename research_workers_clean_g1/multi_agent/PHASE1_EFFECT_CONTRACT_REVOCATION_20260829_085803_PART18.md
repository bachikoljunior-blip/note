# Phase-1 effect-contract revocation semantics: epoch change is not semantic revocation

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `14da1e90bd00bd8883a4276e54a985790b3e2a7a`
- frozen DESIRED_STATE: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_MULTI_SINK_GUARD_VECTOR_20260829_085803_PART17.md`
- script: `research_workers_clean_g1/multi_agent/phase1_effect_contract_revocation_20260829_085803_part18.py`
- script SHA-256: `c05f0e16eb166fa82552f461551151504f5289863aba0119c072f9c0aadce82d`
- result: `research_workers_clean_g1/multi_agent/phase1_effect_contract_revocation_20260829_085803_part18.json`
- result SHA-256: `ea57726811e302fd4357890c2dbd61c974c7970eab218c95c973d9a5f056abdc`

## Objective

The previous leaf showed that a parent can use a historical per-effect apply-time authority receipt even if the sink later advances epochs. This leaf tests the boundary of that statement by making effect semantics explicit. It separates:

- `IRREVERSIBLE_ONCE_AUTHORIZED` — later authority movement cannot undo the already-authorized effect;
- `REVOCABLE_UNTIL_PARENT_TERMINAL` — an explicit revocation may invalidate the effect before parent terminality;
- `COMPENSATABLE` — an explicit revocation does not erase the original effect, but requires a separate compensating effect before the rollback/compensated branch can terminalize.

The central question is whether an epoch/takeover event should itself count as semantic revocation. The model says no: authority freshness and business/effect revocation are distinct state machines.

## Public mechanism boundary

AWS Saga guidance treats compensation as an explicit follow-on local transaction and notes that Saga participants must be idempotent for retries; it also warns that Saga lacks transaction isolation. That public pattern is consistent with the protocol separation here: an original effect receipt, a revocation decision, and a compensation result are separate pieces of state. A compensation request is not evidence that the compensation effect actually reached its final result.

Public source:
- https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html

The contracts below are synthetic protocol semantics; this is not a claim that AWS defines these exact three contract labels.

## Finite model

The executable model enumerates **576 equal-weight synthetic scenarios** over:

- effect contract: `IRREVERSIBLE_ONCE_AUTHORIZED / REVOCABLE_UNTIL_PARENT_TERMINAL / COMPENSATABLE`;
- event after a valid original apply-time receipt: `NONE / TAKEOVER_ONLY / EXPLICIT_REVOKE`;
- revocation tombstone: `PRESENT / MISSING`;
- compensation outcome: `CONFIRMED / AMBIG_APPLIED / FAILED / NOT_SENT`;
- compensation effect identity: `DURABLE / NONE`;
- compensation dedupe: `VALID / EXPIRED`;
- current verifier: `AVAILABLE / OUTAGE`.

There are 288 verifier-available and 288 verifier-outage scenarios.

Compared policies:

1. always terminalize `SUCCESS` from the historical original receipt;
2. current-epoch-only: any later epoch/change makes the old receipt nonterminal;
3. contract-aware proof: interpret takeover/revocation according to the effect contract, require a revocation tombstone for revocable cancellation, and require compensation finality/proof for compensatable rollback;
4. same contract-aware policy but blind-retry ambiguous compensation after dedupe expiry;
5. terminalize compensation when a compensation request/attempt merely exists;
6. treat any epoch/takeover change as semantic revocation;
7. fail closed on every authority change.

## Result 1: takeover is not revocation

For the 64 verifier-available `IRREVERSIBLE_ONCE_AUTHORIZED` scenarios with a later takeover or explicit revoke request, the historical apply-time receipt remains `SUCCESS` terminal evidence in **64/64**. `current_epoch_only` false-blocks **64/64**.

For the 32 verifier-available `REVOCABLE_UNTIL_PARENT_TERMINAL + TAKEOVER_ONLY` scenarios, the correct disposition is still `SUCCESS` in **32/32** because the model contains no semantic revocation event. The `epoch_change_means_revoke` negative control turns 16 into an incorrect `CANCELLED` terminal result and false-blocks the other 16. Thus **authority epoch change is not a semantic revocation token**.

This matters for multi-agent takeover: a fresh worker epoch should fence future stale writes, but it should not retroactively erase an irreversible or still-valid effect that a previous worker applied while authorized.

## Result 2: historical receipt alone is insufficient after explicit semantic revocation

In the 32 verifier-available `REVOCABLE_UNTIL_PARENT_TERMINAL + EXPLICIT_REVOKE` scenarios, a tombstone exists in 16 and is missing in 16. The contract-aware policy produces `CANCELLED` terminal in the 16 tombstoned cases and remains nonterminal in the 16 missing-proof cases.

The `historical_receipt_always_success` negative control marks all **32/32** as `SUCCESS` and is wrong in all 32. Conversely, current-epoch-only remains nonterminal for all 32 and therefore false-blocks the 16 cases where explicit revocation proof is already complete.

So the parent certificate needs effect semantics plus explicit revocation state. Neither “old receipt always wins” nor “latest epoch always wins” is sufficient.

## Result 3: compensation request is not compensation finality

In the 8 verifier-available cases where a compensatable effect was explicitly revoked and the compensation attempt **FAILED**, `comp_request_is_terminal` reports `COMPENSATED` in **8/8** and is unsafe/wrong in all 8. The contract-aware proof remains nonterminal in all 8.

Across the full 576-scenario lattice, request-as-terminal produces 10 unsafe terminal dispositions. This is the same structural distinction as the prior Saga leaf: issuing/accepting a compensating command is not the same as observing a final compensation effect.

## Result 4: ambiguous compensation needs durable identity or still-valid idempotency

The sharpest ambiguity slice has 2 verifier-available scenarios: compensation was `AMBIG_APPLIED`, no durable compensation effect ID exists, and dedupe has expired. The safe contract-aware policy remains nonterminal in **2/2**. The blind-retry policy retries, produces **2 duplicate compensations**, and terminalizes incorrectly in **2/2**.

When the ambiguous compensation has a durable effect identity, the contract-aware policy can reconcile it; when no durable identity exists but dedupe is still valid, it can safely retry. These are different recovery mechanisms but both are stronger than guessing that the ambiguous attempt succeeded.

## Aggregate comparison

- `historical_receipt_always_success`: 128 unsafe/wrong terminal dispositions;
- `current_epoch_only`: 316 false blocks;
- `contract_aware_proof`: unsafe terminal 0 in the modeled verifier-available scope; 254 terminal results, 34 deliberately nonterminal, and 288 verifier-outage checkpoints;
- `contract_aware_blind_retry`: 2 duplicate compensations and 2 unsafe terminals;
- `comp_request_is_terminal`: 10 unsafe terminals;
- `epoch_change_means_revoke`: 30 unsafe terminals plus 34 false blocks.

Counts are finite mechanism counts, not production rates.

## Candidate terminality certificate refinement

Each required effect record should carry at least:

`{effect_key, contract_kind, task/effect_contract_digest, apply_time_authority_proof, durable_effect_id/status, semantic_revocation_state, compensation_effect_id/status}`.

Terminality is contract-dependent:

- irreversible: a valid apply-time receipt is enough; later takeover does not invalidate it;
- revocable: a valid original receipt is success unless an explicit revocation transition occurs; then terminal cancellation requires a durable revocation tombstone/proof;
- compensatable: explicit revocation moves to a compensation branch; parent cannot terminalize that branch until the compensation effect has a final/reconcilable identity/status;
- authority epoch movement alone fences future writers but is not semantic revocation.

## Generic protected boundary

The remaining protected capability now has two orthogonal parts:

> The authoritative sink must atomically validate apply-time authority, and the semantic owner of a revocable/compensatable effect must expose a durable revocation/compensation state transition whose finality cannot be fabricated from claim epochs alone. CLEAN can model and carry these states but cannot install or globally validate the protected authority/revocation mechanism.

Classification: `downstream_verification_required`.

## Exact continuation

Next non-conflicting Phase-1 leaf: **multi-agent compensation claim collisions**. Two workers may race to compensate the same original effect after explicit revoke; enumerate compensation task-key identity, original-effect-ID binding, compensation claim epochs, ambiguous first response, dedupe expiry, worker takeover, multiple compensation resource IDs and amount/quantity conservation. Compare compensation keyed only by parent/task, compensation keyed by original effect ID, original-effect+compensation-kind+claim epoch, durable sink compensation ID/status, and single fenced compensator. Primary falsification: prove that a fresh claim epoch fences stale compensation writers but must not create a second logical compensation identity for the same original effect. Measure duplicate undo, over-compensation, orphan ambiguous compensation, false terminality and safe reuse.

Keep the Phase-1 frontier nonempty; do not restore unrelated base work while the overlay remains active.
