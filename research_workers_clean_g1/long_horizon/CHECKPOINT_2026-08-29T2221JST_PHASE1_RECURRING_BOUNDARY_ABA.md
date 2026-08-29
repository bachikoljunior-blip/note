# Long Horizon clean_g1 checkpoint — Phase-1 recurring-boundary reconstruction + ABA / overrun / rate-limit controls

## Frozen authority / bootstrap

- role: `long_horizon`; class: `clean_exploration`; `enabled_desired=true`.
- transport mode: `exact_blob_two_pass`.
- sanitized root: `automation_control/DESIRED_STATE.json`, parsed `control_revision=26`, Git blob `481660fb6008a57cea162da38439cf115c8d7ebe`. Pass-1/pass-2 matched before semantic work; late recheck still matched.
- own config: `automation_control/roles/long_horizon.json`, parsed `control_revision=16`, `config_revision=7`, Git blob `41984ccfed213f739f005db5a772baef4a8c711f`. Pass-1/pass-2 matched; late recheck still matched.
- root overlay authority supersedes older role-local Phase-1 wording where they differ: `phase_id=phase_1_chat_parity`, `root_problem_id=o-chat-parity-root-v4-zero-work-dependency-zero-quota`, `task_id=phase1-clean-long-horizon-overrun-recovery`.
- own sanitized feedback blob consumed: `9836c7853800e6245493d1fd74f90d768290fc21`; its mechanical artifact-access warning was applied.
- no shared ledger, other-role state/config/receipt, downstream control, O/O-derived state, or legacy/pre-independence semantics were used.
- `bootstrap_valid=true`.

## Own-state reconstruction

`main` still pointed at the older base checkpoint, so Phase-1 continuation was resolved only from this role's dedicated branch `clean-long-horizon-phase1-20260829-1102`, which is allowed own role-local state. Its prior `LATEST.md` blob was `b668dc92d1e12a50f7c2894fad17119f7cce5dc9` and pointed to `CHECKPOINT_2026-08-29T1102JST_PHASE1_CONTINUATION_GUARD.md`, blob `9ddeef8e847558a825df87c65f2acca8cf308362`.

The prior checkpoint was written in an earlier scheduled-Chat invocation. This invocation reconstructed it from repository state before continuing, so the accepted-resume control now crosses a real invocation boundary rather than merely an OS-process boundary.

## Live recurring-boundary resume-consumption control

A set-once append-only resume-consumption ledger entry was created at:

`research_workers_clean_g1/long_horizon/phase1/resume_claims/CLAIM_9ddeef8e_g1_20260829T2221JST.json`

It binds the predecessor checkpoint blob, predecessor `LATEST` blob, task, generation, resume nonce, frozen root/config identities, zero-quota assessment and cost=0. Readback blob: `b94bef04ad3dc80a70e3382829de03487e582719`.

Re-creating the identical claim path was rejected HTTP 422 because the file already existed and no replacement SHA was provided. Within this exact repository/path scope, a resume-consumption identity therefore has one successful set-once creation and a duplicate create is storage-rejected rather than silently accepted.

This is deliberately a ledger of immutable claim files rather than a mutable JSON array, avoiding a lost-update race between concurrent appenders.

## Cross-invocation stale-pointer CAS control

The prior-invocation `LATEST.md` blob `b668dc92d1e12a50f7c2894fad17119f7cce5dc9` was used as the exact CAS precondition to advance the role-local pointer to current recurring-boundary evidence. That write succeeded and produced `LATEST.md` blob `39aad2809c8f43dd594a9a7490b3890b7fb7b89a`.

A second update deliberately replayed the stale predecessor blob `b668dc92d1e12a50f7c2894fad17119f7cce5dc9`; the repository rejected it HTTP 409. Readback remained the new pointer at blob `39aad2809c8f43dd594a9a7490b3890b7fb7b89a`.

This is the requested later-invocation stale replay: the stale precondition originated in the earlier scheduled-Chat state and could not regain write authority in this invocation.

## Live ABA control

`phase1/ABA_STATE.json` was advanced with exact current-blob CAS through:

- A1: semantic payload `A`, `sequence=1`, `plan_generation=1`, blob `e4e2f8672748e44cde625d803f2b43674f42dabd`.
- B2: semantic payload `B`, `sequence=2`, `plan_generation=2`, blob `659572862b046a602ababcb5d35a1bfef5d10088`.
- A3: semantic payload `A`, `sequence=3`, `plan_generation=3`, blob `51e280facff48e37504a4ee4fbf36ae5dcb33770`.

After A3 existed, a stale update using the original A1 blob was rejected HTTP 409. Readback remained semantic A at sequence/generation 3. Therefore, in this tested role-local file path, semantic equality after A->B->A does not restore old authority: blob identity plus monotonic sequence/generation fences the ABA case.

## Forecast-overrun calibration control

`phase1/FORECAST_CALIBRATION.json` was persisted and read back at blob `960d7f57a8417f7a205f4cd5e601b9c16bc78d89`.

The artifact predeclares eight deterministic synthetic cases and compares:

- point policy: `SWITCH iff point_remaining + retry_reserve > budget_remaining`;
- p90/slack policy: `SWITCH iff p90_remaining + retry_reserve > budget_remaining`;
- overrun label: `actual_remaining + retry_reserve > budget_remaining`.

On only these eight cases, point policy had 3 missed overruns and 0 unnecessary switches; p90/slack had 0 missed overruns and 2 unnecessary switches. Thus the p90 rule trades two extra switches for eliminating three misses on this declared trace. This is a synthetic classification/calibration result, not a powered real-task performance estimate.

Persisted switching criterion remains: use an uncertainty-aware forecast plus explicit retry reserve; switch only when remaining slack is negative and a predeclared alternative exists; otherwise durably defer rather than blind-retry.

## Rate-limit / restart / quota-zero controls

`phase1/RATE_LIMIT_TRACE.json` was persisted/read back at blob `232a5636383f9a2f52923bd75aee60ad8d4c345c`.

The deterministic trace covers:

1. repeated 429 with explicit `Retry-After` -> persist `not_before`, do not consume work while waiting;
2. restart before `not_before` -> `DEFER_RATE_LIMIT`, same persisted boundary;
3. 429 with missing `Retry-After` -> deterministic capped exponential backoff from the durable attempt number, persisted once rather than resampled;
4. restart after that observation but before eligibility -> same stored backoff/not-before;
5. retry budget exhausted + predeclared alternative -> `SWITCH_PLAN` and increment generation;
6. retry budget exhausted + no alternative -> `DEFER_NO_ALTERNATIVE`, not blind retry;
7. server wait + p90 + reserve exceeds remaining budget -> immediate switch rather than waiting into a known overrun.

Incoming 429 observations in this artifact are synthetic; repository persistence/readback is live. The current path therefore tests restart-stable decision state, not real production-service rate-limit timing or enforcement.

Quota-zero control sets hosted-runner, Codespaces, artifact/LFS/package, cloud credit and external API/model credit to zero. The continuation mechanism is unchanged because its accepted path uses scheduled-Chat reasoning plus lightweight repository text-state transport only. The root explicitly permits repository transport provided it is rate-limit-tolerant and not used as compute. Incremental monetary cost is zero. No richer-mode, Work, protected-primary, manual-user execution, hosted runner, finite monthly/trial/paid credit, or optional quota-bearing rescue path is required by the tested continuation path.

## Revision relative to the older control-25 checkpoint

The older checkpoint described making the role-local branch authoritative on `main` as a residual merge step. Root control 26 explicitly restores the stricter rule that a protected-primary/manual handoff cannot count as solved. Accordingly, this run does **not** treat any merge-to-main as part of the accepted continuation route.

The tested route instead reads/writes only the dedicated role-local branch through lightweight repository APIs. This removes the protected-primary merge from the mechanism itself. What remains unresolved is **branch-authority discovery under multiple candidate role-local branches**: this run had one source-qualified Phase-1 branch and successfully reconstructed it, but no multi-branch ambiguity control has yet been executed. That is an unresolved child, not a passing handoff.

## Scope guard

Positive evidence is limited to:

- reconstruction of a prior scheduled-invocation checkpoint from own role-local repository state;
- live set-once resume-claim creation + duplicate rejection;
- live cross-invocation stale `LATEST` CAS rejection/readback;
- live A->B->A ABA rejection with monotonic sequence/generation;
- deterministic encoded forecast and rate-limit controls persisted/read back through the same role-local repository path.

Not established here: exactly-once semantics for arbitrary external side effects; real production 429 distributions; real-task p90 calibration; powered scheduled-Chat success improvement; safe authority selection when multiple role-local branches simultaneously claim to be current.

## Conflict / write-boundary check

- late root/config recheck matched the frozen blobs exactly;
- all writes were confined to `research_workers_clean_g1/long_horizon/` on the existing dedicated role-local branch;
- no write to `main`, primary O authority, shared ledger, other-role namespace, downstream state, or protected execution state occurred;
- no direct merge was attempted.

## Exact continuation / nonempty frontier

1. Add a **role-local branch-authority discovery control** that remains deterministic if two candidate branches exist. Candidate design: stable role-local authority name plus a set-once generation claim, with file-level CAS and monotonic generation; do not use protected `main` as an arbiter.
2. Turn the current advisory rate-limit trace into a live persisted state-transition probe: commit attempt/backoff/not-before, reconstruct on a later invocation, verify no early retry or backoff resampling, then exhaust the retry budget into switch/defer.
3. Add a write-interruption control: create the resume claim but fail before pointer advancement, then reconstruct and prove the claim prevents duplicate work while allowing deterministic reconciliation.
4. Add a pointer-advanced-but-receipt-missing control and define authoritative recovery without an external executor.
5. Extend forecast calibration from synthetic classification to repeated own scheduled-Chat duration observations using only role-local checkpoints; predeclare the scoring rule before collecting new samples.
6. Preserve exact scope, zero-dependency/zero-quota constraints and `global_completion=false`.
