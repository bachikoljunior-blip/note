# Phase-1 atomic-objective precommit versus compensation/manual recovery

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `9aecbfd72ebddea92de34792a4587f81e58a744c`
- frozen DESIRED_STATE: control revision `22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- post-freeze observed main SHA: `2fc82034b76ce3fa753993434b38902f10c3c437`
- post-freeze authoritative identity verified: `true` (same root/config blob identities; newer semantic bodies were not used)
- semantic inputs: own role-local latest/checkpoint, finite synthetic mechanism model, and public primary documentation only.

## Leaf objective

Test the unresolved case from the previous reservation-lifetime leaf: after fragment A has validly become externally effective, B can be blocked by authority/proof drift or integrator takeover. Compare four safe candidates:

1. per-fragment fencing;
2. whole-plan atomic precommit when a real shared transaction domain exists;
3. compensation after partial application;
4. fail-closed/manual recovery.

Two negative controls are included: blind retry of an ambiguous compensation and falsely treating a partial state as objective completion.

The key distinction is between **authorization safety** and **business-objective atomicity**. A per-fragment fence can prevent stale B while still leaving an undesirable A-only state. Only a transaction that actually encloses both effects can prevent that partial state by construction; compensation is a separate eventually-consistent recovery path.

## Public mechanism scope

- Amazon DynamoDB `TransactWriteItems` is a concrete bounded example of a shared atomic domain: up to 100 actions in the same account/Region complete atomically, all succeed or all fail. `ClientRequestToken` provides request idempotency only for a 10-minute window. Source: https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html
- PostgreSQL two-phase transactions (`PREPARE TRANSACTION`, `COMMIT PREPARED`, `ROLLBACK PREPARED`) are intended for external transaction managers coordinating transactional resources; prepared transactions remain inspectable and should normally be resolved promptly. Source: https://www.postgresql.org/docs/current/two-phase.html and https://www.postgresql.org/docs/16/sql-prepare-transaction.html
- Azure's Compensating Transaction pattern explicitly treats compensation as eventual consistency: compensation can fail, progress must be recorded so it can resume, retryable undo steps should be idempotent, and some cases require human intervention. Source: https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction

These sources support mechanism boundaries only. The finite counts below are synthetic and are not production incident rates.

## Finite model

The script enumerates **2,112 equal-weight synthetic scenarios** after collapsing irrelevant dimension combinations. Dimensions include:

- objective contract: atomic all-or-nothing / forward-only / mixed / manual-allowed;
- fragment A/B reversibility;
- bounded whole-plan atomic capability absent/present;
- clear vs ambiguous precommit response, with/without authoritative status and possible actual application;
- compensation absent/present;
- compensation finality success / failed / ambiguous;
- compensation idempotent retry and authoritative status availability;
- possible actual compensation application under ambiguity;
- integrator takeover and authority drift between fragments.

### Aggregate comparison

| policy | unsafe | objective-resolved | autonomous terminal | residual partial | irreversible residual | manual |
|---|---:|---:|---:|---:|---:|---:|
| per-fragment fence | 0 | 924 | 528 | 1,584 | 288 | 396 |
| atomic precommit | 0 | 968 | 1,056 | 0 | 0 | 88 |
| disciplined compensation | 0 | **1,068** | **1,104** | 1,008 | 288 | 252 |
| fail-closed/manual | 0 | 924 | 528 | 1,584 | 288 | 1,584 |
| blind ambiguous-comp retry (negative) | **192** | 1,044 | 1,392 | 720 | 288 | 180 |
| partial-as-done (negative) | **1,584** | 528 | 2,112 | 1,584 | 288 | 0 |

## Result 1: per-fragment fencing does not provide atomic-objective semantics

In the 396 atomic-objective scenarios with drift/takeover between A and B, the `partial_as_done` negative control falsely terminalizes **396/396**. The safe per-fragment policy instead leaves the partial state pending.

For the narrower 72-scenario atomic slice where A is irreversible and drift/takeover occurs:

- per-fragment fence: irreversible residual **72/72**, objective resolved 0;
- disciplined compensation: irreversible residual **72/72**, objective resolved 0;
- fail-closed/manual: irreversible residual **72/72**, objective resolved 0;
- atomic-precommit policy: irreversible residual **0/72**, objective resolved **36/72**.

The remaining atomic-precommit cases are fail-closed/ambiguous or lack the bounded capability; they do not create A-only exposure.

**Conclusion:** if the business contract truly requires all-or-nothing and A cannot be undone, fragment-level authority proofs are insufficient. Either the effects must fit a real shared atomic transaction/capability before A is exposed, or the protocol must admit that the objective cannot be autonomously guaranteed.

## Result 2: final compensation can repair reversible partial state, but it is a new proof branch

In the 36 atomic-objective cases with drift/takeover, reversible A, available compensation, and final successful compensation:

- per-fragment fence resolves 0/36 and leaves residual 36/36;
- disciplined compensation resolves **36/36** and leaves residual 0;
- atomic precommit resolves 18/36 and leaves residual 0.

Compensation therefore expands safe autonomous recovery exactly where undo capability and finality are present. It is not equivalent to rollback inside the original transaction: it is an additional external effect with its own finality/retry contract.

## Result 3: ambiguous compensation must fail closed unless retry authority is source-qualified

A targeted 96-scenario slice has:

- A reversible;
- compensation available;
- the first compensation request may already have applied;
- response is ambiguous;
- integrator takeover occurs;
- no authoritative compensation status;
- no idempotent retry contract.

Blind takeover retry duplicates compensation in **96/96** and is unsafe. The disciplined policy has unsafe 0/96 and leaves those cases pending/manual rather than inventing retry authority.

This matches the Azure guidance that compensation can itself fail/retry and should be idempotent when repeatable. A generic `has_key=true` or takeover does not establish a safe retry contract.

## Result 4: a behavior-indexed safe archive dominates any single fixed policy on coverage

Across the four safe policies, the union archive has:

- safe objective coverage: **1,596 / 2,112 = 75.57%**;
- safe autonomous terminal coverage: **1,608 / 2,112 = 76.14%**;
- safe terminal/explicit-manual coverage: **2,112 / 2,112 = 100%**.

The best single fixed policy on objective coverage is disciplined compensation at **1,068 / 2,112 = 50.57%**.

Per-objective archive objective coverage is:

- atomic: 402/528;
- forward: 264/528;
- mixed: 402/528;
- manual-allowed: 528/528.

The archive is not claiming every niche is equally desirable. It preserves materially different safe recovery semantics (`commit`, `rollback`, `manual`, `pending`) so a later authority/objective contract can choose without collapsing these behaviors into one scalar policy prematurely.

## Candidate protocol

1. Classify the business objective before executing any fragment: `ATOMIC_REQUIRED`, `FORWARD_ONLY`, `MIXED`, or `MANUAL_ALLOWED`.
2. If `ATOMIC_REQUIRED` and any first-visible effect is irreversible, require a real shared transaction/atomic capability that covers **all** authoritative effects before exposing any fragment. Do not relabel per-fragment fencing as atomicity.
3. Keep per-fragment currentness/epoch/reservation fencing even when objective atomicity is not required.
4. After a valid partial state, compensation is a new effect identity with independent availability, idempotency scope, status/finality, and takeover rules.
5. Ambiguous compensation without authoritative status or a still-valid idempotent retry contract stays pending/manual; takeover is not retry authority.
6. `MANUAL_REQUIRED` is an explicit safe disposition, not a success claim.
7. Preserve a behavior-indexed safe archive across commit/rollback/manual/pending outcomes when the objective contract is not yet fixed.

## Exact scope limits

- Synthetic finite lattice; equal weighting is not an empirical incident distribution.
- The atomic-precommit candidate assumes a genuine all-effects transaction domain. DynamoDB's 100-action same-account/Region scope and PostgreSQL/XA-style transactional-resource scope are examples, not general external-API guarantees.
- Compensation success/failure/status is abstracted as an oracle in the lattice; provider-specific retry windows and irreversible business semantics remain outside this leaf.
- No worker can bypass the authoritative integrator in this model.
- Manual terminality means the agent stops autonomously with an explicit unresolved disposition; it does not mean the business objective was achieved.

## Exact Phase-1 continuation

Continue with **atomic-capability scope mismatch and mixed-sink objective partitioning**.

Next finite grammar:

- effect set partitioned across one atomic domain plus one or more non-transactional external sinks;
- objective requires global atomicity vs permits staged/compensating subsets;
- transaction commit clear/ambiguous;
- external sink idempotency/status available or absent;
- parent/integrator takeover between atomic-domain commit and external sink effect;
- compensation available for transactional and non-transactional subsets;
- compare `pretend-global-atomic`, `atomic-core + fenced external tail`, `saga partition`, `manual after atomic-core`, and a behavior-indexed safe archive;
- measure false global-atomic claim, cross-domain residual exposure, duplicate tail effect/compensation, lock/prepared-state burden, manual burden, and safe objective coverage.

Keep a nonempty Phase-1 frontier afterward; do not restore unrelated base research while the Phase-1 overlay remains active.
