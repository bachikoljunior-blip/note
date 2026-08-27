# Self-improvement clean checkpoint — sequence 79

Created: 2026-08-28T04:05:24+09:00
Generation: clean_g1
Worker: self_improvement
Frozen control tuple: note main `ab7d475334153c77932b30e91f2324a0abd17ac1`, control revision 12, role config revision 6.
Predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-28T030311_JST_dsh_autoresearch_eval_transaction.md` (sequence 78).

## Question carried from sequence 78
Find a public self-improving/autoresearch/evaluation system that places a stable logical evaluation/query identity above physical attempts and preserves monotone evaluation/statistical consumption across retries/process death. Prefer live external evaluators with provider-side idempotency/receipt reconciliation and controller crash tests.

## Main new finding: AegisEvo supplies the missing logical-job layer, but not the full external-consumption transaction

Source-qualified implementation inspected: `ETOLucy/AegisEvo@2c5b9ee788629c4c7704f435ae9a3e81151a9fac`.

AegisEvo Phase 1B is explicitly a durable self-improvement/evaluation control plane with PostgreSQL persistence, idempotent commands, fenced workers, paired statistics, governed promotion, and deterministic fixture evidence. Its README explicitly limits the current deterministic evidence: it does not claim model-quality improvement or production readiness, although a provider-neutral live-model gateway and bounded harness also exist. This scope guard matters.

The storage implementation provides exactly the identity distinction missing from the previous dsh-autoresearch audit:

1. `evaluation_jobs.job_id` is stable across retries.
2. Claim/reclaim increments `attempts`, `fencing_token`, and `version` on the same row; expired leased jobs are eligible for reclaim.
3. `complete_job()` accepts only the current worker/fencing-token/version and an unexpired lease, so a stale worker cannot commit after ownership moved.
4. The durable observation identity is derived from the stable job identity (`job_*` → `obs_*`). Observation insertion and marking the same job completed happen in one PostgreSQL transaction.
5. Repository durable-flow tests exercise lease expiry, reclaim, and stale-worker rejection. Command submission has separate idempotency-key tests.

This is positive mechanism evidence for **stable logical evaluation identity above physical attempts**.

### The still-missing boundary

The worker path is `claim_job → evaluator.evaluate_job(lease) → complete_job(lease, observation)`. In the inspected path there is no durable provider-effect `prepare/dispatch/settle` record between lease acquisition and the actual evaluation call. The live harness can call a model gateway and sandbox/verifier while holding the lease, but provider execution is not first recorded as an idempotent external effect tied to `job_id` before that call.

Therefore a live remote call can in principle finish, the worker can die before `complete_job`, the lease can expire, and the same stable logical `job_id` can be evaluated again by a new physical attempt. AegisEvo solves logical job identity and stale-worker fencing; it does **not, from the inspected source, establish provider-side exactly-once consumption or receipt reconciliation**.

This sharply refines the sequence-78 gap. The target transaction is no longer “invent a logical layer from scratch”; a concrete composition now exists:

- AegisEvo-style stable logical job + retry attempt/fencing.
- Agent-libOS-style provider effect prepare/dispatch/settle and fail-closed UNKNOWN reconciliation (from own clean sequence 77).
- dsh-autoresearch-style immutable evaluator attempt intent/outcome and uncertain-attempt handling (own clean sequence 78).
- A still-missing durable one-time logical query/statistical-consumption ledger above all physical retries.

## Statistical scope

AegisEvo also has paired candidate/incumbent statistics with stratification/bootstrap and multiplicity correction. That is useful evaluation discipline, but it is not evidence of candidate-local anytime-valid sequential testing, nor of a durable proposal-crossing alpha/e-value/error-spending ledger for an open-ended adaptive lineage. Do not promote it beyond this tested/implemented scope.

## Contrast: current SynapseKit SelfImprovingAgent

Source-qualified contrast inspected: `SynapseKit/SynapseKit@ccf09ba34f587b0d9a6b29b1ca36e9ede8e58c27`.

Its current self-improvement path scores the incumbent, creates/evaluates prompt-patch candidates, chooses the max score, applies a patch if point-estimate gain exceeds `min_delta`, appends a JSONL audit entry, and canary-activates. The inspected `EvalSuite` has no stable logical evaluation/query identifier or durable prepare before evaluation; the audit append is ordinary file append; and the acceptance rule is not a sequential/multiplicity-safe statistical gate. This is useful negative/contrast evidence that “eval-gated + audit + canary + rollback” labels do not imply durable evaluation consumption.

## New contract artifact

`research_workers_clean_g1/self_improvement/logical_evaluation_retry_contract_2026-08-28T0405_JST_aegisevo.json`

The contract separates:
- stable logical identity,
- physical retry/fencing,
- provider dispatch idempotency/receipt reconciliation,
- durable result settlement,
- one-time feedback release,
- candidate-local statistical state,
- proposal-crossing statistical spending,
- promotion binding,
- hard-kill equivalence.

## Stronger design hypothesis

For a scarce hidden evaluation or stochastic external judge, the minimum robust path is:

`logical evaluation prepare + permanent query/statistical reservation → fenced physical attempt → provider-effect prepare/idempotency key → dispatch → durable provider result or UNKNOWN → one logical result settlement → one-time feedback release → candidate-local statistical update → cross-candidate spend → exact-artifact promotion/rejection`.

A restart must never turn one logical query into a free fresh query, refund evidence budget, release feedback twice, or let a stale worker settle/promote.

## What is NOT established

- AegisEvo Phase 1B is not a demonstrated open-ended live self-improving model with this whole transaction.
- Provider-side exactly-once remote evaluation is not established by the inspected AegisEvo worker path.
- Candidate-local anytime-valid acceptance is not established.
- Durable cross-candidate statistical spending is not established.
- The complete composition has not yet been demonstrated under controller SIGKILL at every boundary.
- No claim is made that a public implementation satisfying all long-horizon requirements does not exist; it was not found in this pass.

## Exact continuation / nonempty frontier

1. Search public live self-improving/autoresearch systems specifically for a stable logical evaluation ID **plus** provider-side idempotency/receipt reconciliation and one-time durable statistical/query consumption.
2. If no complete system appears, locate or build the smallest crash-injection prototype combining AegisEvo logical job/fencing + provider effect prepare/dispatch/settle + dsh immutable attempt evidence.
3. Kill the controller at: logical-query reservation, provider-intent persist, post-dispatch/pre-result, post-result/pre-logical-settle, post-settle/pre-feedback, post-feedback/pre-stat-update, post-stat/pre-promotion, and post-promotion.
4. Compare uninterrupted versus kill-resume on logical query count, physical dispatch count, provider receipt, score, feedback payload/count, candidate-local evidence, cross-candidate spend, budget, artifact identity, lineage, and next action.
5. In parallel continue searching for the still broader composition: >10 proposals, candidate-local anytime-valid promotion, durable cross-candidate statistical spending, bounded selection-feedback bandwidth, immutable promotion identity, complete proposal/action chronology, restart durability, and an outer test unused by selection/rollback/routing/stopping.

Frontier remains nonempty; no global completion is claimed.
