# Open Source Systems Scan — operator decision acceptance vs execution re-arm authority

Role: `open_source` clean exploration.
Frozen semantic control tuple: note main `31face47d7ee4b9b686ee3ae55fb9dbdeb877284`, control revision 10, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source: `lbx154/Argus@8c5a0e356c470ad4cbdc904a7fbe4de14af366cf`, public main verified unchanged in this invocation.
Invocation started: `2026-08-26T21:02:51+09:00`.
Checkpointed: `2026-08-26T21:17:00+09:00`.

## New finding

Changing `_reconcile_campaign_after_decision()` from unconditional write to a simple CAS is necessary but **not sufficient**.

Argus deliberately treats an operator decision card as valid even if the continuous campaign generation changed while the question was pending. `tests/webapi/test_operator_decision.py::test_campaign_generation_change_does_not_block_pending_decision` explicitly writes a newer standing objective after the card was created and then requires the old pending decision to be accepted and resolved. This is reasonable for the human decision itself: a later continuous generation should not erase the fact that the operator answered a question.

But the same implementation currently conflates **decision acceptance** with **permission to resume whatever campaign state is current at projection time**:

- a non-stop decision is durably resolved and continuation work is created;
- `_reconcile_campaign_after_decision(stopped=False)` then reads the *current* continuous state;
- if that current state has any nonempty objective and is disabled, it unconditionally writes `enabled=true`, without checking why it was disabled, whether it is the campaign generation that created the question, or whether protected route authority changed.

Therefore a sequence is source-reachable:

1. campaign A creates a pending operator decision;
2. some newer authority action advances continuous generation and disables current work for a semantic reason (operator stop/authority hold/new-scope hold, etc.);
3. the operator later answers the old decision with a continue-like option;
4. decision acceptance is intentionally allowed;
5. current reconciliation sees a disabled objective and re-enables it, even though the old card was not authority to reverse the newer semantic disable.

A CAS against the state read in step 5 would still succeed if no concurrent write occurs after that read. So this is **stale authority**, not merely TOCTOU.

No live state was mutated; this is source-level reachability.

## Existing idempotency makes a safer separation feasible

The code already has most of the needed structure:

- resolved decision cards are durable and exact replays return `application_status=already_applied`;
- `manager_resolve_operator_decision()` calls `_reconcile_campaign_after_decision()` again on an exact replay, so projection is already treated as retryable separately from the decision receipt;
- stop-decision replay is tested not to advance continuous generation twice;
- front-door Manager continuous handoff has a mature stale-generation pattern: CAS expected state, distinguish persistence failure from a newer generation, and raise `ManagerHandoffSupersededError` instead of overwriting newer authority.

Thus a fix need not invalidate old human decisions. It can preserve the card as accepted while making execution projection conditional.

## Refined decision projection contract

At card creation or first semantic binding, persist enough authority context to distinguish the question's execution lineage from later state, for example:

- continuous generation / objective identity at the time the decision became pending;
- protected route revision/digest (separate Fence B);
- optionally the disable/wait contract id that the answer is allowed to release.

On answer:

1. **accept the human decision** if the card is still pending, even if newer generation exists (preserve current product behavior);
2. **project execution only if** the current semantic state is still the same releasable wait/decision lineage, or a current Manager reconciliation explicitly authorizes the old answer under the newer route;
3. if lineage changed, keep the resolved decision and continuation receipt but mark semantic projection as `superseded/reconcile_required`, never force-enable current disabled state;
4. exact replay can retry the projection because the existing replay path already calls reconciliation;
5. all actual continuous writes then use full-state CAS so a writer arriving after reconciliation also wins safely.

This cleanly separates:

- **human-decision validity** (durable, should survive unrelated generation changes),
- **continuous-state write freshness** (existing CAS), and
- **execution-authority lineage** (route/wait revision binding).

## Regression cases

Add tests that preserve the existing generation-change acceptance contract while preventing stale execution:

- pending card from generation N; generation N+1 remains enabled with a newer objective; old decision is accepted but does not rewrite N+1 (current behavior already effectively does this);
- pending card from N; N+1 is disabled with `operator authority hold`; old continue decision is accepted/resolved but must not enable N+1;
- pending card from N; N+1 is `operator chose to stop the campaign`; old continue decision must not resurrect it;
- pending card from N; only its own expected wait/paused projection is disabled and no route revision changed; continue decision may CAS-enable exactly that lineage;
- first projection loses CAS to N+1; exact decision replay remains idempotent and retries/reconciles without duplicating continuation;
- protected route revision changed while continuous generation did not; old card remains resolved but semantic projection requires Manager re-reconciliation.

## Exact continuation

1. Trace where operator decision cards are created from Planner wait/review paths and identify a stable existing wait/authorization id that can bind projection without adding broad new schema.
2. Inspect `manager/front_door.py` continuous handoff's supersession path as the internal reference for `decision accepted, execution superseded` semantics.
3. Audit all semantic disable reason producers to classify which are releasable by the originating decision vs authoritative stop/hold/completion reasons that old decisions must never override.
4. Keep process lifecycle CAS and protected route revision as orthogonal fences.
5. Continue external/admin `PIPELINE_STATE` writer fencing separately.
