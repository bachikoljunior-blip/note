# Long Horizon clean_g1 checkpoint — Phase-1 multi-run continuation guard

## Frozen control / provenance

- role: `long_horizon`
- class: `clean_exploration`
- `enabled_desired=true`
- transport mode: `exact_blob_two_pass`
- sanitized root: `automation_control/DESIRED_STATE.json`, parsed `control_revision=25`, Git blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`; two path reads matched exactly before semantic work and late recheck still matched.
- own role config: `automation_control/roles/long_horizon.json`, parsed `control_revision=16`, `config_revision=7`, Git blob `41984ccfed213f739f005db5a772baef4a8c711f`; two path reads matched exactly before semantic work and late recheck still matched.
- current Phase-1 overlay from the frozen sanitized root: `phase_id=phase_1_chat_parity`, `root_problem_id=o-chat-parity-root-v5-irreducible-handoff-aligned`, `task_id=phase1-clean-long-horizon-overrun-recovery`.
- own prior `LATEST.md` Git blob consumed: `44042bbf008feb09d35c4dc301debbf3257fdd4e`; late conflict recheck matched the same blob.
- own prior checkpoint consumed: `CHECKPOINT_2026-08-29T070703JST_SHADOW_RECOVERY_ADMISSIBILITY.md`, Git blob `895deeb2f875ddd7b10af2381fc8072a1e9c1fc8`.
- own sanitized feedback consumed: Git blob `9836c7853800e6245493d1fd74f90d768290fc21`; its artifact-access warning was applied. No shared ledger or other-role receipt/config/state was read.
- one main-ref lookup was used only to obtain a transport SHA for a role-local branch. That response also surfaced unrelated commit-message metadata, which is forbidden semantic input; it was quarantined and not used for source selection, interpretation, synthesis, or candidate generation. Only the ref SHA was used as transport metadata.
- semantic inputs used: frozen sanitized root, own role config, own role-local clean state, own sanitized feedback, and public sources below.
- forbidden O / other-worker / downstream / legacy semantics were not used.
- `bootstrap_valid=true`.

## Current Phase-1 assignment

Test multi-run planning, checkpoint reconstruction, forecast-overrun switching, stale/duplicate defenses and rate-limit recovery in recurring Chat. Existing/public mechanisms were audited first, then the smallest direct Chat-capable mechanism probe was executed before further decomposition.

## Existing/public solution audit

The useful pieces are distributed across existing workflow systems rather than appearing as one scheduled-Chat continuation contract:

1. **Temporal durable replay / Continue-As-New / version pinning.** Temporal persists event history for replay after crashes; long-running workflows can Continue-As-New with the same Workflow Id and a fresh Run Id/history, and Temporal documentation warns clients not to target an old Run Id after Continue-As-New. Worker Versioning can pin a run to a worker version and upgrade at Continue-As-New boundaries. This supports durable reconstruction and explicit run-generation boundaries. Public references:
   - https://github.com/temporalio/documentation/blob/main/docs/encyclopedia/event-history/java.mdx
   - https://github.com/temporalio/documentation/blob/main/docs/guides/entity-pattern-loyalty-points.mdx
   - https://github.com/temporalio/documentation/blob/main/docs/production-deployment/worker-deployments/worker-versioning.mdx
2. **LangGraph checkpoints / threads / forks.** LangGraph persists state checkpoints per thread, can restart from a prior successful step, and time-travel from an old checkpoint creates a fork. Its interrupt documentation also notes that a resumed node starts again from that node's beginning, so pre-interrupt side effects require care. This supports explicit checkpoint identity and shows why checkpoint pointer alone is not an effect-deduplication contract. Public references:
   - https://docs.langchain.com/oss/python/langgraph/persistence
   - https://docs.langchain.com/oss/python/langgraph/interrupts
   - https://docs.langchain.com/langsmith/human-in-the-loop-time-travel
3. **Kubernetes lease/resource-version fencing.** Coordinated leader election uses Lease expiry and optimistic concurrency through `resourceVersion`, so only one concurrent update wins. This is a close public analogue for rejecting stale continuation writers rather than merely checking elapsed time. Public reference: https://kubernetes.io/docs/concepts/cluster-administration/coordinated-leader-election/
4. **AWS Step Functions retry/timeout/fallback policy.** Step Functions exposes task timeouts/heartbeats plus bounded retry policy (`MaxAttempts`, `BackoffRate`, `MaxDelaySeconds`, optional jitter) and Catch fallback states. This supports durable retry budgets and an explicit alternative path rather than unbounded repetition. Public references:
   - https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html
   - https://docs.aws.amazon.com/step-functions/latest/dg/sfn-best-practices.html
5. **HTTP rate-limit `Retry-After`.** A 429 response may include `Retry-After`; the header specifies a minimum delay before a follow-up request. This motivates persisting a server-derived `not_before` boundary across invocations rather than rediscovering it in a retry loop. Public references:
   - https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/429
   - https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After

No audited source by itself supplied the tested combination of exact checkpoint-head reconstruction, independent resume-consumption identity, forecast-overrun plan-generation switching, and rate-limit-aware defer/switch policy for recurring Chat.

## Direct mechanism probe

A deterministic standard-library Python probe was implemented at:

- `research_workers_clean_g1/long_horizon/phase1/phase1_continuation_guard.py`
- local SHA-256 before repository write: `596acbee0647d1cf0132d13c145d2757c8a84e1fbdb6943b4ad165a54f74f36d`

The probe separates four pieces of state:

1. **Checkpoint integrity / reconstruction.** The checkpoint payload is canonically serialized and SHA-256 sealed. A payload/hash mismatch is rejected before continuation policy runs.
2. **Exact-head freshness.** A candidate may continue only when its checkpoint hash equals the authoritative head. A switch creates a new checkpoint with the old hash as predecessor and increments `plan_generation`, making the old candidate stale.
3. **Duplicate resume consumption.** Resume identity is `H(task_id, checkpoint_hash, plan_generation, invocation_id)` and is consumed in a ledger independent of checkpoint identity. Repeating the exact same invocation against the same head is rejected even though the head itself did not change.
4. **Overrun/rate-limit switching.** Before work authorization, the guard compares `forecast_p90_remaining + retry_reserve` against remaining budget. A forecast overrun switches to a predeclared alternative plan and increments generation. When a persisted `rate_limit_not_before` is present, it additionally includes the required wait in that slack calculation: a feasible wait returns durable `DEFER_RATE_LIMIT` until eligible; an infeasible wait switches immediately; no alternative produces durable `DEFER_NO_ALTERNATIVE` rather than a spin loop.

The suite deliberately launches separate child Python processes for continuation steps, so reconstruction and the duplicate ledger cross an OS-process boundary rather than sharing in-memory objects.

## Probe results

Full result artifact:
`research_workers_clean_g1/long_horizon/phase1/phase1_continuation_guard_result.json`

Local result SHA-256 before repository write: `e8c5229131898bdb989f65b8343c5aa9b70a4b61daa3d6d8c5873bccbe9f17a6`.

All 11 expected controls passed:

- valid current continuation -> `CONTINUE`
- exact duplicate of the same resume identity -> `REJECT_DUPLICATE_RESUME`
- structurally valid but non-head checkpoint -> `REJECT_STALE_CHECKPOINT`
- tampered payload retaining the old hash -> `REJECT_INTEGRITY`
- p90 forecast plus reserve beyond remaining budget -> `SWITCH_PLAN`
- replay of the pre-switch checkpoint -> `REJECT_STALE_CHECKPOINT`
- rate limit whose wait still fits budget -> `DEFER_RATE_LIMIT` before `not_before`
- same rate-limited state at `not_before` -> `CONTINUE`
- rate-limit wait that consumes slack -> `SWITCH_PLAN`
- replay of the pre-switch rate-limited checkpoint -> `REJECT_STALE_CHECKPOINT`
- rate-limit overrun with no alternative -> `DEFER_NO_ALTERNATIVE`

`passed=true`, `process_boundary=true`.

## Live repository CAS probe

The currently exposed GitHub write path was also tested on the isolated role-local branch `clean-long-horizon-phase1-20260829-1102`, never on `main`:

1. Created `research_workers_clean_g1/long_horizon/phase1/CAS_PROBE.txt` version 1; returned blob `6e4d8c681df9937ff1e9b3c599664d2834636378` after readback.
2. Replaced it with version 2 using that exact blob as the update precondition; the write succeeded and returned content blob `fe99ae6444795c5eb995ced93eb9b9ac9a359f80`.
3. Attempted a second replacement using the now-stale version-1 blob. GitHub rejected it with HTTP 409 and message that the current file did not match the stale SHA.
4. Readback still showed version 2 and blob `fe99ae6444795c5eb995ced93eb9b9ac9a359f80`.

Within this tested repository-path scope, CAS is therefore an actually exposed Chat-capable stale-writer defense, not an assumed unavailable capability.

## Switching criteria persisted

For this prototype the control rule is:

- **Continue:** exact checkpoint head; resume id unconsumed; no active rate-limit wait; `forecast_p90_remaining + retry_reserve <= budget_remaining`.
- **Reject stale:** candidate checkpoint hash != authoritative head hash, or candidate plan generation != current generation.
- **Reject duplicate:** exact resume identity already exists in the independent consumption ledger.
- **Defer rate limit:** server-derived/persisted `not_before > now` and `wait + forecast_p90_remaining + retry_reserve <= budget_remaining`, with retry budget still available. Do not consume a work claim while merely waiting.
- **Switch plan:** forecast slack is negative, or the persisted rate-limit wait would make slack negative / retry budget is exhausted, and an alternative plan is predeclared. Switch atomically advances checkpoint predecessor/sequence and increments `plan_generation`.
- **Defer without alternative:** the same overrun condition holds but there is no safe predeclared alternative. Persist the blocker instead of blind retry.

The exact numeric p90 forecast is an input to this control rule, not estimated by the prototype.

## Tested scope / negative evidence

- This is a deterministic mechanism test plus one live GitHub CAS probe; it is not a powered task-success evaluation.
- The process-boundary tests are separate OS processes inside one Chat invocation, not yet separate scheduled automation invocations.
- The forecast value is supplied, not calibrated; this run tests switching logic, not forecast quality.
- The rate-limit cases inject a durable `not_before`; they do not intentionally exhaust a real production service quota.
- The independent resume-consumption ledger is local-file durable in the probe but is not transactionally coupled to external non-idempotent effects. Exactly-once external-effect safety is outside this leaf's tested scope.
- Existing workflow products support several component mechanisms, but no public evidence found in this run establishes that this exact compound guard improves real scheduled-Chat success rates.
- The current selected leaf is therefore a mechanism/provenance result, not `global_completion`.

## Conflict / write-boundary check

- Own `LATEST.md` blob was stable at `44042bbf008feb09d35c4dc301debbf3257fdd4e` from semantic read through the pre-write conflict check.
- Frozen root/config blobs were unchanged at late recheck.
- All repository mutations in this run are confined to `research_workers_clean_g1/long_horizon/` and `automation_control/receipts/long_horizon/` on a dedicated role-local branch.
- No direct merge to `main`, protected authority mutation, primary lease/fence mutation, shared ledger write, or cross-role write was performed.

## Generic residual capability boundary

The remaining effect required to make this checkpoint the authoritative `main` role-local state is **merge the prepared role-local PR/branch into the primary branch**. The frozen CLEAN policy forbids this role from directly merging `main`; the branch/PR preparation itself is Chat-capable and is performed in this run. The residual merge is recorded only as `downstream_verification_required`; this CLEAN role does not claim that the remainder is globally irreducible or globally accepted.

## Exact continuation / nonempty Phase-1 frontier

1. On the next invocation, resolve fresh root/config authority before semantic work. Resolve own state from `main` if the role-local PR has landed; otherwise inspect only this role's source-qualified branch/PR checkpoint rather than unrelated state.
2. Execute the **actual invocation-boundary reconstruction leaf**: persist a head checkpoint plus resume-consumption ledger in role-local repository state, then on a later recurring Chat invocation reconstruct it and exercise one accepted continuation plus a duplicate/stale replay. Preserve exact CAS preconditions/readback.
3. Add an ABA control: advance A->B->A-like semantic payloads while checkpoint sequence/generation remains monotonic; verify old resume ids and predecessor hashes cannot regain authority just because semantic payload fields happen to match.
4. Calibrate the overrun trigger separately. Compare point-estimate versus p90/slack-triggered switching on a deterministic duration trace and measure unnecessary switches versus missed overruns; do not broaden the current fixed-forecast result.
5. Add rate-limit sequences with repeated 429/`Retry-After`, missing `Retry-After`, and a persisted capped backoff chosen once per checkpoint. Verify restart does not resample/retry early and that exhausted retry budget routes to alternative/defer.
6. Preserve a nonempty Phase-1 frontier and exact scope; `global_completion=false`.
