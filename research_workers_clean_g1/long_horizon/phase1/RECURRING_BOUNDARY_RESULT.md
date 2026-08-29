# Phase-1 recurring-boundary execution evidence

This role-local artifact records the live repository transport probes executed under frozen sanitized authority `DESIRED_STATE control_revision=26 / blob 481660fb6008a57cea162da38439cf115c8d7ebe` and `long_horizon control_revision=16, config_revision=7 / blob 41984ccfed213f739f005db5a772baef4a8c711f`, transport mode `exact_blob_two_pass`.

## Prior-invocation reconstruction

The later scheduled-Chat invocation reconstructed the prior role-local checkpoint `CHECKPOINT_2026-08-29T1102JST_PHASE1_CONTINUATION_GUARD.md` from the dedicated role branch. The predecessor checkpoint blob was `9ddeef8e847558a825df87c65f2acca8cf308362`; predecessor `LATEST.md` blob was `b668dc92d1e12a50f7c2894fad17119f7cce5dc9`.

A set-once resume-consumption claim was created at `phase1/resume_claims/CLAIM_9ddeef8e_g1_20260829T2221JST.json` and read back at blob `b94bef04ad3dc80a70e3382829de03487e582719`. Re-creating the identical claim path was rejected by the repository Contents API with HTTP 422 because the path already existed and no replacement SHA was supplied. Within this exact repository-path scope, the claim path therefore acts as an append-only consumption ledger entry: one successful creation, then duplicate creation rejection.

## Live ABA control

`phase1/ABA_STATE.json` was advanced by current-blob CAS through semantic payloads `A(seq=1,g=1) -> B(seq=2,g=2) -> A(seq=3,g=3)`. The first A blob was `e4e2f8672748e44cde625d803f2b43674f42dabd`; B was `659572862b046a602ababcb5d35a1bfef5d10088`; final A3 is `51e280facff48e37504a4ee4fbf36ae5dcb33770`. A stale attempt using the original A1 blob after A3 existed was rejected HTTP 409. Readback remained semantic payload A with monotonic `sequence=3`, `plan_generation=3`. Therefore equal semantic payload does not restore stale write authority in the tested path.

## Forecast-overrun calibration

`phase1/FORECAST_CALIBRATION.json` is a predeclared eight-case synthetic deterministic trace, read back at blob `960d7f57a8417f7a205f4cd5e601b9c16bc78d89`. Relative to `point_remaining + reserve > budget`, `p90_remaining + reserve > budget` reduced missed overruns from 3 to 0 on these eight cases while increasing unnecessary switches from 0 to 2. This is only a classification-tradeoff control for the declared cases, not a powered task-success estimate.

## Rate-limit and quota-zero trace

`phase1/RATE_LIMIT_TRACE.json` was persisted/read back at blob `232a5636383f9a2f52923bd75aee60ad8d4c345c`. It covers repeated 429, explicit `Retry-After`, missing `Retry-After`, restart before `not_before`, deterministic capped exponential backoff chosen from durable attempt number, retry-budget exhaustion with an alternative (`SWITCH_PLAN`), exhaustion without an alternative (`DEFER_NO_ALTERNATIVE`), and a wait that consumes forecast slack. The incoming 429 observations are synthetic; the persistence/readback is live.

The quota-zero control sets hosted-runner, Codespaces, artifact/LFS/package, cloud-credit and external API/model-credit allowances to zero. The continuation decision is unchanged because the tested route uses only scheduled-Chat reasoning plus lightweight repository state transport. No optional quota-bearing execution path or manual/richer-mode rescue is in this tested route; incremental monetary cost is zero. Repository transport can still be rate-limited, so the persisted `not_before`/bounded-backoff policy remains mandatory.

## Scope

Positive evidence is limited to scheduled-Chat reconstruction of an earlier role-local checkpoint, live role-local repository create/read/update CAS behavior, and deterministic encoded forecast/rate-limit traces. It does not establish exactly-once safety for arbitrary external side effects, real production 429 timing, calibrated real-task p90 forecasts, or global task-success improvement.

The next repository probe is to CAS-advance the role-local `LATEST.md` using the predecessor blob from the prior invocation, then deliberately replay that stale predecessor SHA and confirm rejection/readback. After that, checkpoint the whole result and continue to rate-limit state enforcement versus merely advisory policy, plus multiple-branch authority/discovery hardening without any protected-primary merge dependency.
