# Phase-1 multi-agent compensation claim collisions: stable logical undo identity, separate writer epoch

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `14da1e90bd00bd8883a4276e54a985790b3e2a7a`
- frozen DESIRED_STATE: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_EFFECT_CONTRACT_REVOCATION_20260829_085803_PART18.md`
- script: `research_workers_clean_g1/multi_agent/phase1_compensation_claim_collision_20260829_085803_part19.py`
- script SHA-256: `5028e0fb97e34e84b0a40cd4a5702cbe820e35b147804372bfe1cf48df2deca6`
- result: `research_workers_clean_g1/multi_agent/phase1_compensation_claim_collision_20260829_085803_part19.json`
- result SHA-256: `f101ca36f6732fe19b36dd51327d2c8db614ad4db3a18f39c119482bda4dc1c2`

## Objective

Stress the compensation branch when two workers race or take over. The key identity question is deliberately separated into two axes:

- **logical compensation identity**: which original irreversible effect is being undone, and by which compensation kind;
- **writer authority**: which claim epoch/worker is currently allowed to attempt that logical compensation.

The hypothesis is that logical compensation identity must be stable across takeover, while claim epoch must change across takeover. If claim epoch is embedded in the logical compensation key, takeover can create a second undo. If the key is only parent/task-scoped, different original effects alias and one required undo can suppress another.

## Public mechanism boundary

AWS Saga guidance treats compensation as an explicit local transaction and requires idempotent participants for crash/orchestrator retry. AWS transactional-outbox guidance separately warns that duplicate events can occur and recommends tracking processed messages. Those public patterns support the separation here: compensation needs a stable business/effect identity for idempotency, while concurrency control remains a separate concern.

Public sources:
- https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html
- https://docs.aws.amazon.com/en_en/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html

## Finite model

The executable model enumerates **144 equal-weight synthetic scenarios** over:

- worker relation: both target `SAME_ORIGINAL`, or target `DIFFERENT_ORIGINAL_SAME_PARENT`;
- claim/takeover timing: `NO_TAKEOVER / TAKEOVER_BEFORE_FIRST_APPLY / TAKEOVER_AFTER_FIRST_APPLY`;
- first compensation response/truth: `CONFIRMED_APPLIED / AMBIG_APPLIED / AMBIG_NOT_APPLIED`;
- sink dedupe: `VALID / EXPIRED`;
- sink recovery: `DURABLE_STATUS / NO_STATUS`;
- current writer verifier: `AVAILABLE / OUTAGE`.

One applied compensation unit corresponds to one distinct sink compensation resource/result. Required conservation is one unit per original effect: 1 unit for `SAME_ORIGINAL`, 2 for `DIFFERENT_ORIGINAL_SAME_PARENT`.

Policies:

1. compensation key = parent/task only;
2. compensation key = original effect ID, but no current-writer fencing;
3. compensation key = original effect ID + **claim epoch**, no sink fencing;
4. stable key = original effect ID + compensation kind, claim epoch checked separately at sink, fail closed on unreconcilable ambiguity;
5. same stable/fenced design, but blindly retry ambiguous compensation after status loss + dedupe expiry;
6. single fenced compensator using the same stable logical compensation identity.

## Result 1: parent/task key is too coarse

`parent_task_key_only` false-terminalizes **72/144** scenarios: 60 under-compensation and 12 over-compensation. It aliases 72 different/same logical work situations under one key.

The sharpest slice contains 54 scenarios where the workers target **different original effects under the same parent** and the sink still recognizes the shared parent/task key through durable status or valid dedupe. The parent-key policy suppresses one required undo and under-compensates **54/54**.

Therefore compensation identity cannot stop at parent/task granularity. It must bind to the specific original effect being undone.

## Result 2: original effect ID is necessary but no-fence is still unsafe

`original_effect_id_only_no_fence` reduces aliasing but still false-terminalizes 36/144 scenarios: 12 over-compensations and 24 under-compensations. It also permits 16 stale-writer effects in the same-original takeover-before-apply slice.

The under-compensation cases arise when one distinct original compensation is ambiguous-not-applied and the protocol has no safe reconciliation path before declaring the parent terminal. Stable identity alone is not completion proof.

Thus effect identity and writer fencing remain orthogonal.

## Result 3: embedding claim epoch in the compensation identity is too fine

`original_plus_claim_epoch_no_fence` creates **48 identity splits** and 36 over-compensation scenarios. In the 24-case same-original takeover-after-apply slice, the logical ID changes merely because the writer epoch changes; the policy over-compensates **16/24** scenarios, compared with 4/24 for a stable original-effect ID with no fence.

The same pattern appears when takeover happens before the first attempt: epoch-in-identity creates 24 splits and 16 over-compensations, while also allowing 16 stale-writer effects because no sink authority check exists.

So the fresh claim epoch must fence the writer, but **must not create a fresh logical compensation identity**.

## Result 4: strong candidate = stable original-effect compensation ID + separate sink-time writer fence

`stable_original_kind_fenced_failclosed` uses a stable logical ID `H(original_effect_id, compensation_kind, contract_digest)` and treats `{claim_epoch, holder}` only as authority metadata checked at the sink/effect boundary.

Across the 72 verifier-available scenarios it terminalizes 62 safely and checkpoints 10 unreconcilable ambiguities. It rejects 12 stale writers in the same-original takeover-before-apply cases, reconciles 20 ambiguities from durable sink status, uses 10 still-valid idempotent retries, and reuses the same stable compensation identity across 10 takeover-after-apply terminal cases. It has over-compensation 0, under-compensation 0 and false terminalization 0 in the modeled scope.

`single_fenced_compensator` has the same safety/liveness counts here. Serializing writers does not eliminate the need for stable effect identity or ambiguous-response reconciliation; it only removes concurrent dispatch as an additional source of races.

## Result 5: ambiguous response after dedupe/status loss remains irreducible without more sink evidence

There are 10 verifier-available scenarios where the first compensation response is ambiguous, no durable sink status exists, dedupe has expired, and the stale-before-apply case is excluded because sink fencing would reject it deterministically.

The fail-closed stable-ID policy checkpoints **10/10**. The blind-retry policy terminalizes all 10, but produces **5 duplicate compensations / 5 over-compensations** in the five cases where the ambiguous first attempt had actually applied. The other five happened not to apply, so retry happens to be correct; from the available evidence the protocol cannot distinguish the two sets.

That is the same indistinguishability structure as earlier rollback work: when the observation no longer distinguishes “effect applied” from “effect not applied,” safe progress requires durable effect status/idempotency outside the lost window or a fail-closed outcome.

## Conservation rule

The parent should not count compensation resource IDs as an unconstrained bag. Terminality must prove:

`sum(unique final compensation obligations satisfied per original_effect_id) == required compensation obligations`,

with at most one logical compensation identity per `{original_effect_id, compensation_kind, contract_digest}` unless the contract explicitly defines partial/multiple compensation segments.

A second sink resource ID for the same logical full compensation is evidence of over-compensation, not an additional success.

## Candidate protocol refinement

1. derive stable `compensation_effect_key = H(original_effect_id, compensation_kind, contract_digest)`;
2. never include claim epoch/holder in that logical effect key;
3. claim record separately carries `{compensation_effect_key, parent_generation, claim_epoch, holder}`;
4. sink validates current claim/guard epoch at compensation application;
5. sink response/status binds a durable sink resource/effect ID back to the stable compensation key;
6. takeover reuses the stable key and first reconciles existing sink status before retry;
7. ambiguous response + expired dedupe + no durable status is nonterminal/fail-closed;
8. parent terminality checks one complete compensation obligation per original effect and amount/quantity conservation, rather than counting attempts or claim epochs.

## Generic protected boundary

The residual protected requirement remains:

> The compensation sink must enforce current writer authority separately from stable logical compensation identity and must expose durable enough effect status/idempotency to reconcile ambiguous application without creating a second undo. CLEAN can derive stable keys, claims, conservation checks and staged recovery logic, but cannot install or globally validate that sink capability.

Classification: `downstream_verification_required`.

## Exact continuation

Next non-conflicting Phase-1 leaf: **partial/multi-resource compensation conservation**. Replace each original effect's one-unit undo with amounts `{100}` or split obligations `{40,60}` and allow sink responses to return one or two resource IDs, partial success, ambiguous segment success, takeover between segments, and repeated compensation kind. Compare a single full-effect stable key, segment identity derived from ordinal, segment identity derived from immutable amount/range contract, claim-epoch-derived segment identity, and a conservation ledger keyed by original effect plus immutable segment contract. Test over-refund, under-refund, segment alias/split, ambiguous partial retry, resource-ID duplication, and parent terminality. Primary falsification: ordinal-only segmentation may be unstable under replanning; immutable segment contract or a monotonic remaining-obligation ledger may be required.

Keep the Phase-1 frontier nonempty; do not restore unrelated base work while the overlay remains active.
