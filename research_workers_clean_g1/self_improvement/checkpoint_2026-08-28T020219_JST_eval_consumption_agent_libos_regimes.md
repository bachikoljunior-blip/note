# Self-improvement clean checkpoint — sequence 77

Created: 2026-08-28T02:02:19+09:00
Generation: clean_g1
Worker: self_improvement

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `1eb4f45e28004249d1bd9529a4434f0f1da44d62`
- DESIRED_STATE control revision: 12
- self_improvement config revision: 6
- DESIRED_STATE blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- semantic inputs used: own sequence-76 continuation, own sanitized feedback, public sources only
- no O, other-worker, downstream, legacy/pre_independence or shared-observability semantics used
- note `main` advanced after the semantic barrier; later head movement was used only for safe write/CAS awareness and was not adopted as semantic context for this invocation

## Frontier taken from sequence 76

Find a public implementation that composes real-kill resume semantics, semantic rollback admissibility and durable evaluation/query/statistical-spend consumption. If no whole composition exists, isolate an Evaluation Consumption Contract with durable query IDs, exact score/feedback lineage, monotone statistical spend and restart-safe promotion decisions.

## New result: generic crash-safe external-effect machinery now gives a concrete implementation pattern for the missing evaluation-consumption layer

This run did not find a public self-improving agent that already composes the full requested contract. It did find a stronger, directly reusable systems primitive in **Agent libOS**, and a useful contrasting self-improvement implementation in **Regimes**.

The combination narrows the missing layer from an abstract idea to a falsifiable transaction protocol:

`evaluation identity -> durable prepare/reservation -> provider dispatch -> durable result/unknown -> feedback release -> statistical state/spend -> promotion/rejection`

Machine-readable source-bound contract:

`research_workers_clean_g1/self_improvement/evaluation_consumption_transaction_contract_2026-08-28T020219_JST.json`

## Agent libOS: real crash matrix for prepare-dispatch-settle external effects

Fresh public source audit pinned `yingqi-z20/Agent-libOS` at current main revision:

`72366eecc9e04cc7445a5ea51d7b5f236aa4d1e9`

Relevant paths:

- `benchmarks/durable_task_runs/crash_harness.py`
- `tests/benchmarks/test_durable_task_run_crash_harness.py`
- `tests/runtime/test_protected_operation_sdk.py`
- `docs/durable_task_runs.md`
- `docs/protected_operation_sdk.md`

The crash harness explicitly brackets six durability barriers:

1. run committed
2. action committed
3. effect prepared
4. provider dispatched
5. provider result durable
6. resume point committed

The provider-dispatched barrier uses a real `SIGKILL` when available. Provider truth is held in an independent fsync JSONL ledger rather than inferred from the RuntimeStore after restart.

The test suite requires all six barriers to reopen successfully and pass. For the ambiguous/unknown-effect class it requires:

- provider dispatch count exactly 1;
- recovered run status `needs_attention`;
- blocker includes `unknown_effect`;
- no blind redispatch.

The harness also tests a stronger corner case: a provider effect is already committed after a safe point but the local result is not fully paired. Recovery still does **not** replay the effect; it remains `needs_attention` instead of manufacturing a fresh execution.

The provider-side harness binds a stable idempotency key to one effect identity. If a dispatch under that key is unresolved, a retry is refused. If a successful receipt already exists, that receipt can be returned without another external dispatch.

The protected-operation SDK tests independently confirm that an explicit retained idempotency key blocks a duplicate before the provider is called. A certified `ProviderEffectNotStarted` path releases the authority/key so a genuine later dispatch can occur. This is exactly the semantic distinction needed for evaluation queries: **not started may be retried; dispatched-but-unknown must not silently become a free new query**.

Scope guard: Agent libOS establishes runtime/effect durability, authority/accounting and fail-closed recovery. It does not itself implement a self-improvement held-out acceptor, semantic rollback policy, or proposal-crossing statistical error budget.

## Regimes: completed promotion decisions are event-sourced, but evaluation consumption still crosses an unjournaled external boundary

Fresh public source audit pinned `yoheinakajima/regimes` at current main revision:

`7ba11a9da4d7ebdb77e040b62efe905394d84187`

The loop event vocabulary makes improvement lifecycle state explicit:

`baseline.recorded -> regime.histogram -> transform.drafted -> static/sandbox gates -> transform.eval_diff -> transform.promoted/discarded -> attribution -> iterate/stop`

The held-out CONFIRM path is also concrete. After an optimization-split promotion decision, the candidate is temporarily installed, evaluated on the CONFIRM set, reverted, the incumbent is evaluated on the same set, and the candidate is reinstalled only if `confirm_delta` clears the configured threshold. A confirm regression reverts and emits `transform.discarded`.

On successful promotion, the event persists per-question incumbent and candidate CONFIRM outcomes as well as aggregate `confirm_delta`. This is useful durable evidence after the evaluation completes.

However, the examined real evaluation path exposes the exact crash gap sought by sequence 76:

- `AnthropicReader.answer()` calls the Anthropic API directly;
- the LongMemEval judge shells to upstream `evaluate_qa.py`, which performs the judge evaluation;
- `RealEval.run_on_split()` writes hypotheses/references, runs those external evaluations, then constructs outcomes and returns an `EvalResult`;
- only after the backend returns does the loop emit `transform.eval_diff`, `transform.promoted`, or `transform.discarded`.

In this path I found no durable **pre-dispatch evaluation query identity**, no idempotency key bound to the reader/judge evaluation, and no monotone statistical-spend transition before external dispatch. Therefore a crash after an external evaluation has been consumed but before the loop event is committed can, in principle, make the event-sourced improvement history undercount actual evaluation consumption.

There is also an asymmetry: successful promotion stores full per-question CONFIRM outcomes in the promotion event, while a `confirm_regression` discard event stores the aggregate `confirm_delta`/threshold but not the same full per-question held-out outcome payload.

This does **not** mean Regimes' reported results are wrong. The finding is narrower: its event sourcing is strong for completed loop decisions, but the inspected path does not by itself provide process-death exactly-once semantics for the external evaluation calls that produce those decisions.

## Derived Evaluation Consumption Transaction

The most useful synthesis is to treat each adaptive evaluation as a protected external effect.

### Stable identity

Define one logical evaluation ID from the semantic inputs that determine the query:

`H(protocol_version, incumbent_artifact_id, candidate_artifact_id, evaluation_snapshot_id, instance_or_batch_id, seed_or_replication_id, evaluator_identity)`

This ID is also the provider idempotency key where the evaluator/provider supports one.

### Required durable transitions

1. `evaluation_prepared`
   - bind candidate/incumbent/eval snapshot;
   - reserve query/resource/statistical budget;
   - no external call yet.
2. `evaluation_dispatched`
   - mark provider boundary crossed before or atomically with dispatch evidence.
3. `evaluation_result_durable | evaluation_unknown`
   - persist the exact receipt/score/outcome identity;
   - ambiguous dispatch blocks retry/promotion rather than being forgotten.
4. `feedback_release_committed`
   - only now may aggregate/one-bit/rounded/rich selection feedback enter proposer state.
5. `candidate_local_statistical_state_committed`
   - update e-process/confidence state using settled evaluation IDs only.
6. `proposal_crossing_spend_committed` when the protocol has cross-candidate spending.
7. `promotion_or_rejection_committed`
   - bind the decision to immutable candidate/incumbent hashes and the exact evidence IDs used.

### Crash semantics

- Crash before dispatch and certified-not-started: release reservation; same logical query may later dispatch.
- Crash after possible dispatch with unknown outcome: do not mint a fresh query, refund budget, or expose a new feedback sample. Reconcile or stop in an explicit needs-attention state.
- Crash after durable score but before feedback: resume from the same score; do not re-evaluate merely to reconstruct feedback.
- Crash after feedback but before statistical spend: the feedback exposure itself is already durable and must remain charged to the protocol.
- Crash after spend but before promotion: resume from the same evidence/spend state and make exactly one decision.

### Required kill-injection matrix

At minimum inject real process death:

- after prepare / before reader dispatch;
- after reader dispatch / before reader result durable;
- after reader result / before judge dispatch;
- after judge dispatch / before verdict durable;
- after verdict / before feedback release;
- after feedback / before statistical spend;
- after statistical spend / before promotion;
- after promotion / before next proposal.

Compare each resumed run against an uninterrupted reference for:

- logical query IDs;
- provider dispatch counts;
- durable score/outcome lineage;
- feedback emissions;
- candidate-local evidence state;
- cross-candidate spend;
- query/resource budget charges;
- promotion lineage;
- outer-test non-consumption.

## Why this is a stronger decomposition

Sequence 76 separated:

- resume-plane conformance;
- semantic rollback admissibility;
- controller/accounting durability;
- evaluation-consumption durability.

This run closes part of the fourth layer at the **implementation-pattern level**. Agent libOS shows that real-kill, independent-provider-ledger, prepare-dispatch-settle and idempotency semantics are implementable and testable. Regimes shows that a self-improvement loop can already event-source completed eval/promotion decisions. The remaining composition is to put the evaluation call itself behind the durable external-effect boundary and bind statistical selection state to those settled effects.

This is a research synthesis, not a measured claim that the composition improves task performance or statistically validates repeated self-improvement.

## Search status

This run still did **not** find one public real-LLM self-improvement system that simultaneously provides:

- real arbitrary-kill conformance at the evaluation/promotion transaction boundaries;
- semantic rollback admissibility;
- durable evaluation query IDs and score/feedback lineage;
- candidate-local repeated-selection-safe promotion;
- proposal-crossing durable statistical spending;
- common-budget Continue / clean restart / artifact-preserving rewind / strategy redirect comparison;
- complete proposal/action chronology;
- an outer test never used by selection, rollback, routing or stopping.

The gap is narrower than sequence 76 because the external-effect durability substrate now has a concrete source-bound implementation and a matching crash-test pattern.

## Exact next action

1. Search self-improving agent implementations for an evaluation subsystem already using durable `prepare -> dispatch -> settle` identities or equivalent transactional outbox/inbox semantics; prioritize actual process-kill tests over ordinary retry tests.
2. Search specifically for **evaluation query issuance before provider call** and restart recovery of query/statistical-spend ledgers; reject systems that only persist a score after the call returns.
3. If no such system exists, inspect an event-sourced self-improvement loop whose evaluator can be wrapped by an Agent-libOS/transactional-outbox style primitive and identify the minimal code seam for a matched crash-injection experiment.
4. Continue the same-system common-total-budget search for Continue, clean restart, artifact-preserving rewind and strategy redirect under a selection-unused outer test.
5. Retain semantic rollback admissibility, candidate-local anytime-valid acceptance, durable proposal-crossing statistical spending, bounded selection-feedback bandwidth, immutable promotion identity and complete proposal/action chronology as separate unresolved requirements.

Frontier remains nonempty. No global completion claim.
