# Phase-1 proposal proof drift, reservation lifetime, and fragment fencing

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic tuple remains note main `9c76f42557b6dee420c8ff1f424f66b619465b5f`, root control revision `22`, root blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, role config revision `6`, role blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`.
- semantic inputs: own immediately preceding Phase-1 objective/archive checkpoint plus this finite synthetic stress model only. CLEAN boundary preserved.

## Leaf objective

The objective-first archive leaf made parallel recovery conditional on current proposal proofs and an exclusive-effect reservation. This leaf tests how long those proofs/reservations remain authoritative while two fragments execute.

The core trace is:

`proposal V1 -> reserve -> execute A -> parent/objective/proof/reservation/integrator changes -> execute B`

A reservation or proof check before A is not automatically authority for B. Conversely, rechecking at every irreversible boundary can safely block B after A was validly issued, but that leaves a partial-effect state that must be represented rather than falsely calling the plan atomic.

## Finite model

The executed model enumerates **1,152 equal-weight synthetic scenarios** over:

- parent/objective version change: none / before reservation / after reservation before A / between A and B;
- proof-digest change on the same schedule;
- reservation expiry: never / before A / between A and B;
- integrator takeover: none / before A / between A and B;
- reservation reacquisition capability absent/present;
- fragment A reversible vs irreversible;
- late old fragment absent/present after takeover.

Compared protocols:

1. `precheck_once` — one currentness check before reservation; A/B do not recheck proof, reservation, or integrator epoch.
2. `reserve_then_final_revalidate` — reserve first, revalidate proof/reservation once before A, then let B inherit that authority.
3. `per_fragment_fence` — every fragment checks current parent/proof, reservation validity, and worker/integrator epoch before its effect.
4. `immutable_stage_current_integrator` — workers only stage immutable fragment outputs; the current integrator revalidates before each publication and may reacquire an expired reservation when the parent/proof remain current.

## Main results

| protocol | safe complete coverage | unsafe scenarios | duplicate effects | notable recovery/exposure |
|---|---:|---:|---:|---|
| precheck once | 8 / 1,152 = **0.69%** | **640 = 55.56%** | 216 | stale proposal effects 576; stale worker effects 432 |
| reserve + one final recheck | 8 = **0.69%** | **184 = 15.97%** | 64 | reservation leaks 456 |
| per-fragment fence | 8 = **0.69%** | **0** | 0 | 60 partial irreversible exposures |
| immutable stage + current integrator | **48 = 4.17%** | **0** | 0 | 72 safe reacquisitions; 216 late old stages ignored; 96 partial irreversible exposures |

Counts are finite equal-weight mechanism counts, not production incident rates.

## Result 1: proof/currentness is a boundary condition, not a plan-wide lease

The `version_or_proof_changes_between_fragments` slice has **504** scenarios.

- precheck once: **360 unsafe**;
- reserve + one final recheck: **144 unsafe**;
- per-fragment fence: **0**;
- immutable-stage/current-integrator: **0**.

The proposal's proof digest and parent/objective version must therefore be checked at each authoritative effect boundary unless a stronger transaction/capability explicitly covers the whole multi-effect interval.

## Result 2: reservation validity must be checked at each effect boundary

In the **384-scenario** `reservation_expires_between_fragments` slice, precheck-once is unsafe in 216 and one-final-recheck is unsafe in 96. Both can issue B after the reservation no longer exists.

Per-fragment fencing blocks B safely. Immutable staging can additionally recover **12** safe-complete cases in this slice by reacquiring authority only when the parent/proof are still current.

A reservation ID in proposal metadata is therefore not itself an authority proof; the effect boundary needs the current reservation incarnation/epoch or an atomic all-effects capability.

## Result 3: integrator takeover invalidates old fragment authority even if its content is correct

The `integrator_takeover_between_fragments` slice has 384 scenarios:

- precheck once unsafe 216;
- one-final-recheck unsafe 64;
- per-fragment fence unsafe 0;
- immutable staging/current integrator unsafe 0 and safely completes 16.

For the explicit late-old-fragment slice the same unsafe counts recur. Immutable staging records/ignores **216** late old stages rather than letting the old worker directly publish an effect.

This preserves the earlier claim protocol: result correctness and current authority are independent.

## Result 4: safe fencing can still leave partial irreversible exposure

Per-fragment fencing has unsafe count 0 but records **60** scenarios where fragment A was validly issued, A is irreversible, and B is later blocked by changed proof/authority/reservation. Immutable staging/current-integrator records 96 such partial exposures because it safely reaches A in more cases before later invalidation.

This is not a stale-write failure. It is a planning/finality fact: if an objective requires true all-or-nothing semantics, per-effect fencing alone is insufficient once A is irreversible. The plan needs a stronger pre-commit capability, compensating objective, or an explicit partial/manual terminal state.

## Current candidate protocol

1. Proposal metadata binds exact parent/objective version and every proof digest, but those bindings are not assumed current forever.
2. Reservation acquisition happens only for a currently valid proposal; the reservation has its own identity/epoch/expiry.
3. Before each authoritative fragment effect, revalidate `{parent/objective version, proof digest, current integrator/worker epoch, reservation}`.
4. A stale worker may write only immutable stage output. Current integrator publication is the authoritative boundary.
5. If reservation expired, reacquire only after current parent/proof validation; a new reservation is a new authority incarnation.
6. Preserve partial-effect state explicitly. `A applied, B blocked` is not plan success and may require compensation/manual recovery depending on the business objective.
7. For atomic all-or-nothing objectives with irreversible A, require a stronger capability than independent per-fragment reservations before issuing A.

## Scope limits

- Finite synthetic lattice only.
- Reservation reacquisition is modeled as conflict-free when enabled; contention/conflict is outside this leaf.
- The immutable-integrator policy assumes leaf workers cannot bypass the integrator to the external sink.
- Partial irreversible exposure is measured separately from unsafe stale authority; a valid earlier effect can still become an undesirable partial result after later state change.

## Exact Phase-1 continuation

Continue with **atomic-objective precommit versus compensating/manual recovery after partial irreversible parallel completion**.

Next finite grammar:

- objective atomic-all-or-nothing vs forward/mixed/manual;
- fragment A irreversible/reversible and B reversible/irreversible;
- whole-plan precommit capability available/unavailable;
- compensation availability/finality for A and B;
- reservation/precommit response ambiguity and integrator takeover;
- partial A-applied/B-blocked state;
- compare per-fragment fence, whole-plan irrevocable authorization point, compensation-after-partial, fail-closed/manual, and behavior-indexed safe archive;
- measure objective violation, false atomic terminality, duplicate effect/compensation, irreversible residual exposure, manual burden, and safe objective coverage.

Keep a nonempty Phase-1 frontier afterward.
