# Phase-1 multi-sink guard vector and per-effect terminality certificate

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `14da1e90bd00bd8883a4276e54a985790b3e2a7a`
- frozen DESIRED_STATE: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_GUARD_EPOCH_CLAIM_FENCING_20260829_085803_PART16.md`
- script: `research_workers_clean_g1/multi_agent/phase1_multi_sink_guard_vector_20260829_085803_part17.py`
- script SHA-256: `c85e2d79b29fa5e2cc0adcc3f7696ffc245f05b58332773426931a0a6b0d2310`
- result: `research_workers_clean_g1/multi_agent/phase1_multi_sink_guard_vector_20260829_085803_part17.json`
- result SHA-256: `b6c2c9c7e8748cb906c2efa07d557da4a81060d312879087b15a4c5c4ad53265`

## Objective

Extend the single-sink guard-epoch result to a parent that requires two authoritative effects whose sinks can advance authority asynchronously. Test whether a scalar parent epoch is enough for terminality, or whether terminality needs a per-effect certificate containing the authority proof that was current **at each effect's application time**, plus durable effect identity for ambiguous-response recovery.

This distinction matters because a sink may legitimately accept an effect under `e1` and only later advance to `e2`. A parent that demands every historical receipt equal the latest scalar `e2` loses valid history; a parent that accepts arbitrary historical receipts without sink validation accepts stale effects that happened after a sink had already advanced.

## Public mechanism boundary

AWS's Saga guidance treats cross-service work as a sequence of local transactions rather than one implicit global ACID transaction. It explicitly notes eventual consistency, requires idempotent participants for retry after crashes/orchestrator failure, and warns that Saga lacks transaction isolation so concurrent orchestration can observe stale data. AWS's transactional-outbox guidance separately warns that duplicate messages can occur and recommends idempotent consumers that track processed messages. These are public precedents for treating per-participant completion, concurrency/freshness and duplicate suppression as separate obligations rather than collapsing them into one parent status bit.

Public sources:
- https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html
- https://docs.aws.amazon.com/en_en/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html

The synthetic `sink atomic authority receipt` below is stronger than Saga itself: it assumes each effect sink can atomically validate the presented guard epoch with effect application and return/recover a durable effect identity. This is a protocol requirement, not a claim that AWS or GitHub natively provides this exact object.

## Finite model

The executable model enumerates **288 equal-weight synthetic scenarios** over:

- sink A transition timing: `STABLE_E1 / E2_BEFORE_APPLY / E2_AFTER_APPLY`;
- sink B transition timing: same three states;
- A response: `CONFIRMED / AMBIG_APPLIED`;
- B response: `CONFIRMED / AMBIG_APPLIED`;
- B dedupe: `VALID / EXPIRED`;
- current authority verifier: `AVAILABLE / OUTAGE`;
- staged computation contract: `MATCH / MISMATCH`.

Sink A is modeled with recoverable durable effect identity. Sink B is intentionally weaker in one policy and relies only on an expiring dedupe contract.

Policies:

1. `scalar_current_epoch_atomic` — each sink validates authority at apply, but parent terminality requires both effect receipts to equal one latest scalar parent epoch;
2. `scalar_any_historical_no_sink_check` — terminalize from historical e1 receipts without per-sink apply-time authority proof;
3. `vector_claim_only_no_sink_check` — label receipts with a sink vector but never have the sink validate it;
4. `vector_atomic_ephemeral_b_dedupe` — per-sink apply-time authority check, but B only has expiring dedupe;
5. `vector_atomic_durable_effect_ids` — per-sink apply-time authority check and durable effect identities/status for both sinks;
6. `vector_atomic_exact_reuse_durable` — same strong receipt plus exact contract gating for staged computation reuse after takeover;
7. `serial_fail_closed` — refuse to terminalize when B's ambiguous-applied effect cannot be safely reconciled after dedupe expiry.

There are 144 verifier-available and 144 verifier-outage scenarios. Outage is a checkpoint/liveness cost for policies that require authoritative sink verification.

## Result 1: one latest scalar epoch is too coarse for asynchronously transitioning sinks

`scalar_current_epoch_atomic` is authority-safe in the modeled scope because each effect itself is sink-validated, but among 144 verifier-available scenarios it terminalizes only **32** and false-blocks **112**.

The most direct slice is the 64 scenarios where the two sinks' final epochs differ. The scalar policy false-blocks **64/64**, while the per-sink durable receipt policy terminalizes **64/64**. The scalar cannot express “sink A validly applied under e1, sink B required e2” without either replaying valid work or rejecting completion.

A second decisive slice has both sinks advance to e2 **after** their e1 effects were already validly applied. There are 16 such verifier-available scenarios. The scalar latest-e2 rule false-blocks **16/16**, whereas the per-effect durable receipt policy terminalizes **16/16**. Later authority advancement does not retroactively make a previously authorized irreversible effect stale.

Therefore parent terminality should not require every receipt's authority epoch to equal one current scalar epoch. It needs the stronger historical fact: **was each required effect atomically authorized at its own application time, for the correct parent/task/effect contract?**

## Result 2: a vector label without sink validation is as unsafe as an unlabeled historical receipt

`scalar_any_historical_no_sink_check` and `vector_claim_only_no_sink_check` have the same aggregate safety outcome: both terminalize all 288 scenarios, accept **192 stale effects**, and false-terminalize **160** scenarios. They also create 72 duplicate effects under B's ambiguous-response/expired-dedupe cases.

In the 80 verifier-available scenarios where at least one sink had advanced to e2 **before** the old e1 attempt reached effect application, vector-label-only terminalizes **80/80**, with 96 stale-effect acceptances and 80 false parent terminalizations.

Thus converting a scalar into a vector is not sufficient by itself. The vector becomes evidence only when each component is bound to a sink-time authoritative check.

## Result 3: per-effect apply-time certificates preserve safety without retroactive over-fencing

`vector_atomic_durable_effect_ids` terminalizes all **144/144** verifier-available scenarios and checkpoints all 144 verifier outages. It has stale-effect acceptance 0, false terminalization 0 and duplicate effect 0 in the modeled scope.

Its parent certificate is conceptually a set/vector of required effect records:

`{effect_key, task/input/effect_contract_digest, sink_authority_epoch_validated_at_apply, durable_effect_id, terminal_status}`.

The parent may terminalize only when every required effect has such a valid receipt. The receipt does not have to match the sink's later current epoch if the sink proves the effect was authorized when applied. Conversely, an old receipt is invalid if no sink-time proof shows that its epoch was current at application.

This is a historical authorization certificate, not merely a snapshot of current sink epochs.

## Result 4: authority-vector correctness does not solve ambiguous retry duplication

`vector_atomic_ephemeral_b_dedupe` has no stale-authority or false-terminal failure, but still produces **24 duplicate effects**. Those 24 are exactly the verifier-available slice where B's old effect was authorized, the response was `AMBIG_APPLIED`, and B's dedupe had expired. In the targeted 24-case slice it duplicates **24/24**.

The durable-effect-ID policy reconciles those same 24 scenarios without duplicate effect. This matches the public transactional-outbox/Saga guidance that participants need idempotency/replay handling independently of cross-service orchestration.

Therefore the parent terminality certificate needs both dimensions: per-effect authority proof **and** durable effect identity/status sufficient to reconcile response loss.

## Result 5: computation reuse remains separable from authority

`vector_atomic_exact_reuse_durable` is as safe as the durable certificate policy. For sink transitions that occur before the old attempt can apply, it records **48 safe staged-result reuses** when the immutable staged contract exactly matches the fresh claim, and **48 rejected-reuse/recompute cases** when it does not.

The stage is a compute artifact only. Fresh authority comes from the new sink check, and the durable effect identity comes from the effect application path.

## Candidate protocol refinement

For a parent with heterogeneous authoritative sinks:

1. retain the parent generation/task contract as common identity, but do not collapse sink authority into one scalar current epoch;
2. each required sink effect receives a stable `effect_key` and durable logical effect identity;
3. the sink atomically validates its presented authority/guard epoch and current claim/effect contract when applying the effect;
4. the resulting receipt records the epoch that was valid **at apply**, the durable sink effect ID/status, and the exact contract digest;
5. parent terminality is a completeness predicate over the required receipt set/vector, not `all receipt epochs == latest scalar epoch`;
6. a later sink authority transition does not invalidate a previously authorized irreversible effect unless the effect contract itself defines such revocation semantics;
7. an old staged computation may be reused under a fresh claim only after exact contract revalidation;
8. verifier outage or ambiguous effect without durable reconciliation remains nonterminal/fail-closed.

## Generic protected boundary

The minimum remaining protected capability is unchanged in kind but becomes per-sink in scope:

> Each authoritative effect sink must provide an atomic current-authority check (or equivalent server invariant) at effect application and enough durable effect identity/status to reconcile ambiguous application. CLEAN can construct claims, vectors, immutable stages and parent completeness certificates, but cannot install or globally validate those protected sink invariants.

Classification: `downstream_verification_required`.

## Exact continuation

Next non-conflicting Phase-1 leaf: **certificate revocation semantics and irreversible-vs-revocable effects**. Introduce effect contracts `IRREVERSIBLE_ONCE_AUTHORIZED / REVOCABLE_UNTIL_PARENT_TERMINAL / COMPENSATABLE`, then advance a sink or parent epoch after a valid apply-time receipt but before parent terminality. Compare historical apply-time certificate, current-epoch-only certificate, explicit revocation tombstone, compensation receipt, and fail-closed. Test whether “later epoch does not invalidate old receipt” is safe only for irreversible authorization semantics, and derive a terminality predicate that carries effect revocability/compensation state rather than assuming one rule for all sinks. Include ambiguous compensation response and durable effect identity.

Keep the Phase-1 frontier nonempty; do not restore unrelated base work while the overlay remains active.
