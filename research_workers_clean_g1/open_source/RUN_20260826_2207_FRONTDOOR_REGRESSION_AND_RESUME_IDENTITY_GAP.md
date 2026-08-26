# Open Source Systems Scan — front-door regression + restart identity gap

Invocation started: 2026-08-26T21:59:42+09:00
Checkpointed: 2026-08-26T22:07:51+09:00

Frozen semantic tuple for this invocation:
- note main SHA: `5885e238e2c57f48264bf462356ae7ef5639f53e`
- sanitized control revision: `10`
- open_source config revision: `5`
- open_source config blob: `118f440957ba4654e804af902aa09a9224acca43`
- public Argus main: `8c5a0e356c470ad4cbdc904a7fbe4de14af366cf`

Independence: own clean state + public sources only. No O/O-derived state, other-worker state, downstream semantics, legacy research, shared ledger, or other-role receipt/config was used.

## 1. The generic I/O primitive already proves the split-commit shape

`tests/daemon/test_state_portable.py::test_replace_failure_after_callback_surfaces_instead_of_false` already injects exactly the low-level failure needed for the front-door case: `before_write` commits a side effect, `os.replace(...continuous.json...)` then fails, the CAS raises `ContinuousConfigCommitError`, the callback side effect remains, and `continuous.json` stays at its prior state.

So the remaining gap is not hypothetical behavior of the storage primitive. It is the absence of an integration regression proving that the *Manager front door* must not leave an enabled old objective on a newly committed route after that already-tested failure mode.

## 2. Minimal front-door regression

`tests/manager/test_pipeline_yield.py` currently covers successful replacement and additive-authority handoffs, but not a post-precommit `continuous.json` replace failure.

A minimal failing regression can reuse that fixture shape:

1. Seed `continuous.json` with enabled objective A.
2. Seed protected pipeline state with `vertical=software`, `workflow_mode=staged`.
3. Use a fake `Prepared.commit()` that persists the *same vertical/domain* but changes `workflow_mode=direct` (or another protected route field) and returns the corresponding Division.
4. Monkeypatch `daemon_state.os.replace` to raise `EIO` only when the destination is `continuous.json`; allow route-state replacements.
5. Call `front_door.manager_continuous_handoff()` and expect `ManagerHandoffError` wrapping the storage commit failure.
6. Assert the safety invariant, not one particular implementation: after failure it must be impossible for `(continuous.enabled == true && continuous.objective == A && protected_route == B)` to hold. A fix may satisfy this by route rollback or, preferably, by a disabled handoff-fence state.
7. Also assert the pipeline-yield marker is cleared, so the regression isolates semantic coherence rather than a stale-yield wedge.

Current code fails the semantic invariant: `_commit()` runs inside `before_write`, route B is durable, the later continuous replace can fail, `prepared.failed()` records failure, and `finally` clears the yield with no route compensation.

## 3. Future restart can preserve the mismatch when vertical/domain are unchanged

This is stronger than the immediate split-brain finding.

Manager handoff identity v3 stores only:
- objective SHA256,
- vertical,
- domain,
- continuous generation,
- intent id,
- optional source-objective metadata.

It does **not** bind `workflow_mode`, `research_target_level`, `research_direction_mode`, `target_venue`, current stage, or a protected route/state revision/digest. Legacy event recovery also canonicalizes a completed event back down to objective + vertical + domain + generation + intent.

`_manager_handoff_identity_matches()` accepts an identity when objective/vertical/domain match and `identity.continuous_generation <= current_generation`.

But `persist_vertical()` writes protected route fields including `workflow_mode`, research target/direction, target venue, and stage state. Therefore a front-door failure that changes only one of those fields while keeping vertical/domain unchanged can leave:

- continuous A still enabled at generation g,
- protected route mutated to B,
- prior handoff identity for A still matching objective + vertical + domain at generation <= g.

On a later explicit `--resume-continuous`, `_resume_matches_manager_handoff()` can therefore return true and skip Manager re-division even though the protected route is not the route that identity actually certified. The daemon-boot failure path's process-local suppression does not repair this later restart case because this mismatch originated in the live front door and the durable identity matcher is blind to the changed route fields.

A second compact regression should construct exactly this same-vertical case: write identity for A under `software/staged`, mutate only persisted `workflow_mode` to `direct` without changing continuous A, then assert resume identity matching is false. Current v3 matching returns true.

## 4. Refined fail-closed protocol

The smallest robust protocol now looks like:

1. CAS A-enabled -> **disabled handoff-fence** before any protected route mutation.
2. Commit route B under the existing Manager pipeline lock.
3. CAS the exact fence generation -> B-enabled.
4. Only after step 3 succeeds, publish the completed-event / manager-handoff identity.
5. Bind identity to one protected `route_revision` or canonical route fingerprint rather than enumerating only vertical/domain. The fingerprint should cover every Manager-owned field that changes execution semantics.
6. The handoff-fence reason must never be in `RESUMABLE_STOP_REASONS`; restart must reconcile it through Manager rather than process-resume it.

If step 2 or 3 fails, the durable state can be route-old or route-new, but continuous execution remains disabled, so an old objective is never executed under a new route. Existing continuous generation CAS and exact process-resume allowlisting remain useful positive controls; this proposal extends them across the route/continuous boundary rather than replacing them.

A route fingerprint also lets process-only drain/SIGTERM resumes keep the existing `identity_generation <= current_generation` convenience without trusting stale semantic routes: generation may advance for process lifecycle reasons, but the protected route fingerprint must remain exact.

## Scope

This is source-level reachability and regression design against public Argus `8c5a0e...`; no live exploit or state-corrupting run was executed. The finding is limited to the observed front-door precommit/replace ordering plus the observed v3 resume-identity fields.

## Exact continuation

1. Trace `PreparedManagerHandoff.failed()` plus operator-message/event durability to decide what exact objective payload a disabled handoff-fence must preserve for automatic reconciliation after crash.
2. Enumerate all `_manager_handoff_identity_matches()` consumers and migration tests; design a backward-compatible v4 route-fingerprint identity and the same-vertical/workflow-mode mismatch regression.
3. Verify every semantic rearm path treats the new fence as non-resumable and routes it through Manager reconciliation; keep process-only drain/SIGTERM rearm unchanged.
4. Define the minimum protected route fingerprint fields from `PIPELINE_STATE` and test canonicalization so descriptor-only evidence changes do not spuriously invalidate identity.
5. Keep external/admin `PIPELINE_STATE` writer fencing as a separate branch; do not conflate it with this front-door cross-file commit defect.
