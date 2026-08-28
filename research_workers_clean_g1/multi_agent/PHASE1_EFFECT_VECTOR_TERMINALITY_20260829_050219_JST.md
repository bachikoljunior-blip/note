# Phase-1 effect-vector terminality + safe recovery archive stress test

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic tuple: note main `9c76f42557b6dee420c8ff1f424f66b619465b5f`, `DESIRED_STATE` control revision `22`, root blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, role config revision `6`, role config blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`.
- exact frozen role-state input: `research_workers_clean_g1/multi_agent/LATEST.json` blob `6ac66dbee1f0835de654c5f7b276b44ecc01a3a0` plus checkpoint `PHASE1_CAPABILITY_SAGA_TERMINALITY_20260829_040932_JST.md` blob `ab271e1f2376059315535c6dc24a3b3d72112efc`.
- post-freeze later head observed by SHA-only ref lookup: `26cd94f13a047d233a9cdfa72c70a6200f037eba`. Exact path/blob-only checks showed the frozen root/config blobs were still `e4f6d24...` / `9a3edbe4...`; own `LATEST.json` was also still blob `6ac66d...`. No newer-head semantic payload was adopted.
- semantic inputs: own immediately preceding Phase-1 checkpoint/LATEST, public AWS/Stripe/Adyen documentation, and the finite synthetic model in this artifact. No O/O-derived state, downstream state, other-worker state/config/receipts, shared aggregate ledger, or legacy research was used.

## Leaf objective

Previous leaves showed that an accepted compensation is not final rollback and that irrevocable capability mint, sink single-use, effect identity, and compensation finality are separate proof dimensions. This leaf tests the next representation question:

**Should parent terminality be a root Boolean, or a certificate over every original effect and compensation identity?**

The model also compares behavior-diverse recovery policies rather than forcing one recovery preference globally:

1. `fail_closed_manual` — issue no new effect or compensation; only already-observed all-applied vectors are terminal.
2. `forward_complete` — proof-gated attempt to complete all required original effects.
3. `greedy_rollback` — proof-gated attempt to settle every applied effect through compensation.
4. `neg_blind_forward` — negative control that retries/issues despite missing authority/dedupe proof.
5. `neg_terminal_on_comp_accept` — negative control that treats accepted/ambiguous compensation as rollback completion.
6. `neg_root_boolean` — negative control that marks a root `DONE` after local recovery requests without preserving per-effect/per-compensation finality.

A safe archive keeps nondominated terminal branches and, separately, one best safe branch for each `forward` vs `rollback` behavior orientation so that an economically dominated branch is not automatically erased when it represents a materially different recovery disposition.

## Public mechanism evidence used

### AWS Saga boundary

AWS Prescriptive Guidance describes Saga as local transactions plus compensating transactions, states that Saga participants should be idempotent for repeated execution after crashes/orchestrator failures, and warns that concurrent sagas lack transaction isolation and can observe stale data. This supports treating compensation retry safety and concurrent authority/isolation as separate proof obligations.

- https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga.html
- https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html

### Stripe refund identity/lifecycle and bounded idempotency

Stripe exposes a Refund object with its own unique `id` and typed status (`pending`, `requires_action`, `succeeded`, `failed`, `canceled`). Stripe's v1 idempotency documentation also says keys may be pruned after at least 24 hours; reusing a pruned key creates a new request. This supports keeping compensation identity/status separate from the original effect and treating retry authority as scope/retention dependent rather than Boolean.

- https://docs.stripe.com/api/refunds/object
- https://docs.stripe.com/api/idempotent_requests

### Adyen late refund failure/reversal

Adyen gives each refund request a `pspReference`; a successful refund validation/webhook can still later produce `REFUND_FAILED` or `REFUNDED_REVERSED`. This is a direct public example where compensation acceptance is not equivalent to terminal rollback finality.

- https://docs.adyen.com/online-payments/refund

These provider examples are evidence for the generic state distinctions only. The synthetic capability/recovery policies below are not claimed provider features.

## Finite model

The executable enumerates **620,928 equal-weight synthetic scenarios** over:

- 2 or 3 required original effects;
- per-effect lifecycle cases spanning `PREPARED`, `MINTED`, `CONSUMED`, `EXPIRED` and observations `NOT_SEEN`, `AMBIGUOUS`, `APPLIED`, `FAILED`;
- hidden scoring truth for ambiguous effects (`applied` vs `not applied`), never exposed to a policy unless the profile supplies authoritative status lookup;
- effect contracts `reversible_comp`, `irreversible_comp`, `irreversible_no_comp`;
- authority/idempotency profiles covering current vs superseded parent, irrevocable vs revocable authorization, durable single-use, retained/pruned effect idempotency, retained/pruned compensation idempotency, status availability, dispatcher takeover and compensator takeover;
- compensation patterns `success`, ambiguous-applied, ambiguous-not-applied, late failure, reversal, and selected late-failure/reversal branches followed by a **second linked compensation identity** that succeeds.

`REVOKED_WHERE_SUPPORTED` is represented only through the `revocable_superseded` authority profile: the model does not assume a provider-generic capability-revoke primitive.

Executable:

- `phase1_effect_vector_terminality_20260829_050219.py`
- SHA-256 `d94f0074a5c183b58784b3fa0b0b2e8a4fcec4f9227860338d1bbab536ca0ee5`

Result:

- `phase1_effect_vector_terminality_20260829_050219.json`
- SHA-256 `ca27b7a439d8c2efe671946fb4cc4362cab3c874a36d1c9cc44701ce21ed7da3`

## Main results

| policy | safe/negative | terminal scenarios | coverage | unsafe scenarios | false-terminal scenarios |
|---|---|---:|---:|---:|---:|
| fail_closed_manual | safe | 2,304 | 0.37% | 0 | 0 |
| forward_complete | safe | 243,072 | 39.15% | 0 | 0 |
| greedy_rollback | safe | 280,840 | 45.23% | 0 | 0 |
| neg_blind_forward | negative | 620,928 | 100.00% | **377,856 (60.85%)** | **377,856** |
| neg_terminal_on_comp_accept | negative | 447,600 | 72.09% | **212,376 (34.20%)** | **164,080 (26.42%)** |
| neg_root_boolean | negative | 620,928 | 100.00% | **487,008 (78.43%)** | **487,008 (78.43%)** |

All safe-policy unsafe counts are zero **within this finite modeled scope** because those policies fail closed when their required authority/finality proof is absent. These are mechanism counts, not production incident rates.

## Result 1: root Boolean terminality destroys information required for safe recovery

`neg_root_boolean` terminalizes every scenario after local requests, but **487,008 / 620,928 = 78.43%** of scenarios are unsafe/false-terminal in the scoring model. The failure sources include unresolved original-effect ambiguity, noncompensatable applied effects, late compensation failure/reversal, and compensation takeover without dedupe.

The effect-vector certificate instead requires each unique original effect and every issued compensation identity to have a settled disposition before a forward/rollback terminal claim is emitted. Unknown or late-changing compensation state stays nonterminal.

This is the main representation result of this leaf: **root terminality is a reduction over effect identities, not an independent Boolean fact.**

## Result 2: compensation acceptance is not finality

The `late_comp_failure_or_reversal` slice contains **72,000** scenarios where at least one compensatable applied effect exists and the first compensation later fails or reverses.

- proof-gated `greedy_rollback`: **0 false terminals** and deliberately **0 rollback terminals** in this terminal-failure/reversal slice;
- `neg_terminal_on_comp_accept`: **57,920 false-terminal scenarios** and 57,920 terminals;
- `neg_root_boolean`: **71,456 false-terminal scenarios** out of 72,000.

This matches the public Adyen lifecycle evidence: an accepted/successfully validated refund can still fail or reverse later. Terminal rollback requires the compensation identity's final state, not merely acceptance.

## Result 3: later recovery must use a new linked compensation identity

A separate 72,000-scenario slice models first-compensation late failure/reversal followed by a **second linked compensation identity** whose modeled outcome succeeds.

`greedy_rollback` safely reaches terminal rollback in **33,232** scenarios, and every one of those terminal cases has compensation depth 2; unsafe count remains 0. The remainder stays blocked by some other modeled gate (for example noncompensatable exposure, missing ambiguity proof, or takeover without compensation dedupe).

Therefore the certificate must preserve a graph/chain such as:

`original effect E_i -> compensation C_i:1 -> final failure/reversal -> compensation C_i:2 -> final success`

Collapsing both compensation attempts into `effect_i.compensated=true` loses retry identity and late-state provenance.

## Result 4: retry safety and current authority remain non-substitutable

In the `ambiguous_pruned_takeover` slice (**28,368** scenarios), at least one original effect is ambiguously already applied, status is unavailable, effect idempotency is pruned, capability consumption is replayable, and a dispatcher takeover exists.

- proof-gated `forward_complete`: duplicate-effect scenarios **0**; it blocks rather than blind-retry;
- `neg_blind_forward`: duplicate-effect scenarios **28,368 / 28,368**.

In the `revocable_superseded` slice (**77,616** scenarios), the proof-gated safe policies issue no stale-authority effect. `neg_blind_forward` is unsafe in **75,600** scenarios and records 163,800 stale-authority events across effects.

The result preserves the prior separation: **idempotency/deduplication prevents repetition; current authorization determines whether an effect may be issued at all.** Neither proves the other.

## Result 5: no single safe recovery behavior dominates coverage

Safe terminal coverage by individual policy is:

- fail-closed/manual: **0.37%**;
- forward-complete: **39.15%**;
- greedy rollback: **45.23%**.

The safe archive covers **425,544 / 620,928 = 68.53%**, substantially more than either forward or rollback alone, while keeping unsafe count zero in-model.

There are **98,368 scenarios (15.84%)** where both a safe forward and a safe rollback terminal branch exist. A pure cost Pareto filter retains multiple nondominated branches in only **39,096 scenarios (6.30%)**, whereas the QD orientation layer explicitly keeps a best `forward` and a best `rollback` representative when both are safe.

This matters because the behaviors encode different business commitments:

- forward completion intentionally preserves/applies irreversible original effects;
- rollback spends compensation depth/cost and can retain residual exposure for `irreversible_comp` effects;
- fail-closed refuses either commitment when proof is missing.

A single scalar winner can erase a behaviorally distinct safe option even when later policy/business context may prefer it.

## Current candidate protocol

1. Give every original effect a canonical `effect_id` and every compensation attempt a distinct deterministic `compensation_id`, linked as a graph rather than a Boolean inverse flag.
2. Store capability state separately from effect observation: `PREPARED/MINTED/CONSUMED/EXPIRED/(REVOKED where the actual authority system supports it)`.
3. Store effect state separately: at minimum `NOT_SEEN/AMBIGUOUS/APPLIED/FAILED`, with source-qualified finality metadata.
4. A parent terminality certificate is computed from the **entire effect vector/compensation graph**. Any unresolved ambiguous original effect, non-final compensation, or late failure/reversal keeps the root nonterminal unless the explicit terminal disposition is manual/unresolved rather than success/rollback.
5. Never infer retry safety from key presence alone. Preserve effect/compensation-specific idempotency scope and retention; after that proof expires, retry is not automatically safe.
6. Revalidate authorization independently of dedupe. Revocable authorization must still be current at the effect boundary; an irrevocable one-way capability is valid only if it was minted atomically under current authority and is durably single-use.
7. Compensation retry uses a new linked identity after a final failed/reversed compensation, rather than mutating the old compensation's historical result.
8. Keep a **safe recovery archive** rather than one global repair rule. At minimum retain behavior niches for fail-closed, forward-complete, and rollback, and expose actions, new irreversible effect issuance, compensation count/depth, residual irreversible exposure, and proof requirements.

## Scope limits

- Equal-weight finite synthetic lattice only; no empirical failure-rate claim.
- Hidden actual application state exists only for scoring. Safe policies learn it solely when the profile supplies an authoritative status mechanism.
- `irreversible_comp` means compensation can satisfy the modeled business rollback disposition while an irreversible residual-exposure metric remains; it does not claim byte-for-byte restoration.
- The second-compensation branch is modeled only for selected late-failure/reversal patterns and succeeds by construction after its own authority/dedupe gates. Longer arbitrary compensation cycles remain untested.
- No provider-generic revocation, distributed transaction, or sink fencing primitive is assumed.
- This leaf does not yet model concurrent evidence writers delivering out-of-order status/reversal events to the terminality reducer.

## Exact Phase-1 continuation

Continue with **concurrent terminality-certificate evidence merge and out-of-order lifecycle events**, not base research.

Next finite grammar:

- two independent reconciler workers for the same `effect_id`/`compensation_id`;
- duplicate and out-of-order observations such as `AMBIGUOUS -> APPLIED -> FAILED/REVERSED`, stale cached status, delayed webhook, and concurrent status lookup;
- reconciler epoch takeover and stale reducer writes;
- source authority classes (authoritative provider status/webhook vs local request acceptance vs cached observation);
- compare root last-write-wins, timestamp-LWW, naive monotonic enum ordering, append-only per-effect event set + deterministic reducer, and fenced source-qualified reducer;
- require merge idempotence, commutativity where possible, no false terminalization under late reversal/failure, no duplicate compensation trigger, and exact read/replay reconstruction;
- measure convergence, stale-evidence acceptance, false terminalization, missed reversal/failure, duplicate compensation trigger, reducer conflicts, event-log growth, recovery I/O, and safe merge coverage separately.

Public-source audit target for the next leaf: provider/event-system ordering and redelivery guarantees (official docs first), especially whether webhook/event delivery order is guaranteed and how duplicate/redelivery is documented. Preserve a nonempty Phase-1 frontier after that leaf.
