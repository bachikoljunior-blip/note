# Open Source Systems Scan — Resume identity v4 simplification and sticky venue route state

Invocation started: 2026-08-27T10:02:23+09:00
Checkpointed: 2026-08-27T10:17:00+09:00

Frozen semantic tuple remains unchanged for this physical invocation:
- note main SHA: `0690108bdb37bbcf3ca1ea9f7a032ca1706ea9b9`
- control revision: `11`
- open_source config revision: `5`
- config blob: `118f440957ba4654e804af902aa09a9224acca43`

This continuation read only the prior own clean checkpoint plus public `lbx154/Argus` source. No O/O-derived, other-worker, downstream, legacy, shared-ledger, or other-role semantic state was used. Public Argus main remained `33da786bbc6787a2eeb63a5f492498eae87c78c7` when verified in this invocation.

## 1. Manager-handoff v4 probably does not need a new generation-lineage subsystem

The current resume path intentionally treats continuous `generation` as a storage/config revision, not a pure semantic campaign revision:

- `_rearm_operator_drain_for_resume()` converts an exact process-only stop (`operator drain-stop` or graceful SIGTERM/SIGINT) from disabled back to enabled by writing continuous config again; that write increments generation even though the objective and Manager route are unchanged.
- `tests/daemon/test_continuous_resume_gate.py` explicitly treats those two process-stop classes as resumable while planner completion and `operator authority hold` remain disabled. The same test suite also treats a same-objective newer generation as a legitimate explicit rewrite that lifts fresh-daemon suppression.
- Current `manager-handoff.json` v3 therefore matches `identity.continuous_generation <= current generation`, not equality.

That means requiring exact generation equality in v4 would reject a legitimate process-only rearm. A separate semantic-generation field is also broader than this candidate needs. The existing Manager `CampaignControlStore` already derives `campaign_epoch` from continuous generation, so adding another epoch just for daemon resume would create a second, partially overlapping lineage system.

A simpler v4 fast-path is now preferred:

1. current continuous state is **enabled**;
2. there is **no unresolved structured handoff fence**;
3. exact Manager-clean objective hash matches;
4. exact canonical semantic route fingerprint v4 matches the **current persisted route**;
5. identity generation is not from the future (`identity_generation <= current_generation`);
6. versions 1–3 never get this fast path — one real Manager reconciliation emits v4.

Under those conditions, a process-only generation bump is harmless: semantic objective+route remained identical. If a semantic command changed the objective or any v4 route field, the fast path fails. If a handoff is mid-transaction, the fence disables the campaign and blocks the fast path. Therefore a new generation-lineage marker is not currently justified by the source evidence.

This simplification depends on separately fixing the current process-control bugs: Web start's broad `operator ` rearm, non-CAS boot rearm, and immediate/scheduled upgrade restoration from stale copied objective snapshots. Those remain current-state reconciliation defects, not reasons to overload manager-handoff identity.

## 2. `target_venue` is not currently a stable Manager route-contract field

A deeper route-state audit found an important asymmetry that affects v4 fingerprinting.

The active persisted route contract shown back to Manager in `_render_active_route_contract()` includes:
- vertical;
- workflow_mode;
- domain;
- research_target_level;
- research_direction_mode.

It does **not** include `target_venue`.

The parsers also do not receive a `persisted_target_venue` argument. `parse_vertical_decision()` and the fast parser build `target_venue` only from the current Manager answer, and force it to empty for non-research verticals. In contrast, workflow/domain/target/direction have explicit persisted-state inheritance rules.

Then `_commit_vertical_decision_locked()` passes `decision.target_venue or None` to `persist_vertical()`. `persist_vertical()` writes a nonempty supplied venue, but if the argument is `None`/empty it does **not** remove an existing `target_venue`. The same function does explicitly clear some other inapplicable route fields (for example domain on non-research and unsupported target-level state), so venue is a real asymmetry rather than a general "preserve unknown fields" policy.

Concrete source-reachable consequences:

- research + `AAAI 2026` → software can leave raw `target_venue="AAAI 2026"` in `PIPELINE_STATE.json`, even though the Manager decision/parser correctly says a non-research route has no venue;
- later software → research with no newly stated venue can inherit that stale raw venue because the empty decision becomes `None` at persistence and does not clear the old field;
- there is no explicit Manager route-contract representation for "preserve current venue" versus "clear venue" versus "set new venue".

No live failure was reproduced. This is a source-level state-contract gap.

## 3. v4 route identity must canonicalize semantic state, not hash raw pipeline JSON

The six-field v4 candidate remains useful, but `target_venue` must be interpreted conditionally:

- for `vertical != research`, canonical `domain`, `research_direction_mode`, and `target_venue` should be empty according to the Manager parser's semantics, even if stale raw pipeline keys remain;
- research target level should be included only where the active vertical supports it;
- for `vertical=research`, venue should use `_normalize_venue_key` (uppercase, remove separators, strip trailing 2/4 digit year) so `AAAI-26`, `aaai2026`, and `AAAI 2026` are one identity;
- `current_stage` remains excluded because ordinary execution progress changes it.

Crucially, the identity should be computed **after Manager commit from the actual persisted semantic route**, not solely from pre-commit `VerticalDecision` fields. This lets restart validation detect what was actually made authoritative.

The venue persistence bug should not be hidden by fingerprint normalization. The clean structural fix is to make venue an explicit tri-state route field for research:

- omitted on a same-route supplemental decision => preserve current semantic venue;
- explicit clear (`none`/empty sentinel under a typed contract) => remove it;
- explicit venue => replace it;
- leaving research => remove/semantically deactivate venue.

That requires threading persisted venue through Manager route rendering/parsing and adding regression coverage. Existing public tests confirm explicit venue persistence, but the audited source/test surface did not reveal a regression for clear/preserve across vertical changes.

## 4. Current process-control paths reinforce the simpler v4 rule

Current public source still has the following independent problems:

- Web `start_project_daemon(... resume_continuous=True)` re-enables any disabled nonempty campaign whose reason merely starts with `operator `, and it does this before daemon admission/spawn. That is broader than the exact process-stop allowlist used by daemon boot.
- `_rearm_operator_drain_for_resume()` uses the correct narrow reason allowlist, but re-enables with a non-CAS write.
- immediate upgrade snapshots continuous state before drain and may restore that copied objective afterward;
- scheduled upgrade persists `resume_continuous` + objective and later restores that copied state before restart;
- daemon replacement calls the same start helper and inherits its resume semantics;
- resolved operator decisions can directly project a disabled objective back to enabled continuous state without a route-reconciliation identity check.

These call sites should converge on one current-state `reconcile_or_rearm` boundary. That boundary should never restore a previously copied objective. It should either exact-CAS the **currently observed** disabled process-stop record under the narrow allowlist, or perform a Manager semantic reconciliation.

Once that is true, manager-handoff v4 can remain a cheap crash/restart optimization keyed by exact objective + exact semantic route, rather than becoming a second command/event lineage system.

## 5. Durability side note

`manager-handoff.json` itself is a derivative restart optimization. Its current writer is temp `write_text` + `os.replace` without explicit fsync. Unlike continuous state or the exact Backlog mission record, failure to durably persist this sidecar can safely fall back to a fresh Manager classification. Therefore this file does not need to sit inside the handoff transaction's critical durable ordering; strengthening it is optional hardening, not an admission prerequisite.

## Candidate refinement

`clean-os-g1-005` now separates three concerns more sharply:

1. **Semantic handoff transaction** — disabled structured fence before all side effects; exact source/target route reconciliation; durable exact-once mission insert; final exact CAS enables target.
2. **Process control** — all start/restart/upgrade/replacement paths operate on current continuous state, exact-CAS only the narrow process-stop allowlist, and otherwise reconcile semantically; never restore copied objectives.
3. **Restart optimization** — manager-handoff v4 binds exact objective hash + canonical persisted semantic route v4, permits nonfuture generation (`<=`) only after v4 exists and no fence is unresolved, and migrates v1–v3 through one real Manager reconciliation.

A new sub-defect is recorded for `target_venue`: Manager's persisted-route contract currently lacks an explicit preserve/clear/set contract and `persist_vertical()` can leave stale venue state across route changes. Fix/measure this before treating venue as a trustworthy raw persisted identity field.

## Exact continuation

1. Design the minimal tri-state `target_venue` Manager contract and regressions for: research AAAI → supplemental research with venue omitted; research AAAI → research venue explicitly cleared; research AAAI → software; research AAAI → software → research with no venue.
2. Confirm whether any production call intentionally mutates `BacklogItem.id` or `ts`; if none, make the immutable update guard unconditional.
3. Specify typed `CreationStampV1` and `HandoffFenceV1` parser/serializer limits and exact invalid-input behavior.
4. Build the process-control `reconcile_or_rearm` call-site matrix and tests for Web start admission failure, boot process-only rearm race, immediate upgrade concurrent semantic command, scheduled-upgrade stale request, replacement, and operator decision.
5. Benchmark the global Backlog durable rewrite before promoting file+directory fsync from correctness experiment to default behavior.
6. Keep external/admin `PIPELINE_STATE` writer fencing as a separate candidate branch.
