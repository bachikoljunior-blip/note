# Open Source Systems Scan — resume-callsite matrix + v4 canonical route fingerprint

Invocation started: 2026-08-27T00:04:50+09:00
Checkpointed: 2026-08-27T00:10:58+09:00

Frozen semantic tuple for this invocation:
- note main SHA: `dc25bd6206e3108313d3b530705595102ecb0209`
- sanitized control revision: `10`
- open_source config revision: `5`
- open_source config blob: `118f440957ba4654e804af902aa09a9224acca43`
- public Argus main: `8c5a0e356c470ad4cbdc904a7fbe4de14af366cf`

Independence: own clean state + public sources only. No O/O-derived state, other-worker state, downstream semantics, legacy/pre-independence research, shared aggregate ledger, or other-role receipt/config was used. `research_feedback_clean_g1/open_source/FEEDBACK.json` was absent at the frozen note snapshot. The note head advanced after semantic freeze; this run did not adopt later control.

## 1. The current `resume_continuous` boolean conflates several different authorities

A full public-source call-site pass shows that `start_project_daemon(..., resume_continuous=...)` is reached from materially different situations:

- `webapi/routes/daemon.py` `/daemon/start` always passes `resume_continuous=True`. This endpoint is nominally a process-start command, but `start_project_daemon()` currently interprets the flag by directly re-enabling any disabled continuous state whose `done_reason` starts with `operator ` before admission/spawn.
- The same route module's `/continuous` endpoint first calls `set_continuous(...)` and only then starts the daemon with `resume_continuous=True`. Here semantic campaign authorization already happened upstream; the daemon call only needs to launch/adopt the now-current durable state.
- `webapi/routes/manager.py` starts after Manager message/stream dispatch with `resume_continuous=bool(result.get("continuous"))`. Again the Manager result is upstream semantic authority; the process helper should not reinterpret an older disabled reason.
- `webapi/routes/workitems.py` starts after a resolved operator decision with `resume_continuous=bool(result.get("continuous"))`. In current code, `_reconcile_campaign_after_decision()` may already flip disabled continuous state back to enabled before this call, so decision acceptance and execution rearm are presently coupled twice: once in decision projection and again through the process-start resume flag.
- `plugin/service.py` starts task dispatch with the default `resume_continuous=False`; this is a useful positive control showing that ordinary task dispatch only needs process launch, not semantic campaign resurrection.
- `daemon_upgrade.py` uses `resume_continuous=True` when an upgrade target daemon is absent, and propagates saved `continuous.enabled` through immediate/scheduled restart. These are process-lifecycle paths, but the scheduled path also restores an old objective snapshot before restart, which can overrule newer semantic state.
- `daemon_lifecycle.py` propagates the same flag through daemon replacement/idle reclamation and explicit-objective session creation.

The boolean therefore mixes at least three concepts: (a) launch the process, (b) re-arm a temporary process-stop state, and (c) semantically resume/reconcile a campaign. Treating all three as one boolean is the root API-shape problem.

## 2. Existing boot logic already defines the correct process-only allowlist

`daemon/state.py` defines exactly two process-lifecycle stop reasons:
- `operator drain-stop`
- `operator stop (graceful SIGTERM/SIGINT — clock out)`

and groups only these in `RESUMABLE_STOP_REASONS`. `tests/daemon/test_continuous_resume_gate.py` verifies that resume re-arms those two while preserving `operator authority hold: new scope is not authorized` and planner-declared completion.

This means a new process/semantic distinction does not need a fresh policy taxonomy. The safe boundary can reuse the tested allowlist and remove the broader `done_reason.startswith("operator ")` pre-mutation from `start_project_daemon()`.

## 3. Refined single boot contract

A smaller design than adding multiple public resume booleans is:

1. `start_project_daemon()` never writes continuous semantic state. It may pass only a boot-time **reconcile/rearm intent**.
2. Admission/spawn happens without semantic pre-mutation.
3. Boot reads the current durable continuous state and applies one gate:
   - enabled state: adopt exactly the current generation/objective;
   - disabled + `done_reason in RESUMABLE_STOP_REASONS`: process-rearm by exact current-state CAS;
   - disabled + exact handoff-fence reason: run fresh Manager reconciliation, without first enabling;
   - operator stop/authority hold/planner completion/other disabled reason: remain disabled.
4. Upstream semantic actions (`/continuous enabled`, Manager handoff, operator decision reconciliation) must establish or request semantic authority explicitly; a process helper must never infer it from a generic `operator ` prefix.

This preserves the existing cheap crash/restart path while making process start non-authoritative over campaign meaning.

## 4. Exact handoff-fence reason

A suitable dedicated value is:

`manager handoff reconciliation required`

It is intentionally:
- not one of `RESUMABLE_STOP_REASONS`,
- not prefixed by `operator `,
- semantically specific enough for a boot gate to recognize exactly,
- not a completion statement.

The disabled fence should retain the Manager-clean execution task for the incoming objective plus open-ended semantics needed for replay. It should not itself authorize execution; it authorizes only reclassification/reconciliation.

## 5. Canonical v4 route fingerprint can reuse existing normalizers

The minimum route fields from the previous run remain appropriate, but public code now gives exact canonicalization rules:

- `vertical`: `require_vertical()` / `_strip_needed()` => trim/lowercase, strip trailing `-needed`; legacy `direct` canonicalizes to `software`; custom data-domain names must resolve at the protected state root.
- `domain`: `require_domain()` => trim/lowercase and replace `-` with `_`; absent/non-research route canonicalizes to empty string.
- `workflow_mode`: `_normalize_workflow_mode()` => only lowercase `direct` or `staged`, else empty/invalid.
- `research_target_level`: `normalize_research_target_level()` => one of `exploratory|publishable|doctoral`, else empty.
- `research_direction_mode`: `normalize_research_direction_mode()` => one of `broad|locked`, else empty.
- `target_venue`: `persist_vertical()` collapses internal whitespace, trims, and truncates to 100 characters; empty stays empty.

A deterministic v4 identity can therefore hash a canonical JSON object with these six sorted keys and compact separators. The fingerprint should be derived from the protected route state, not from model-facing workdir mirrors or current-stage progress.

`current_stage` remains intentionally excluded: stage progress is expected to change during a healthy campaign and must not invalidate cheap process restart. If stage-order/schema authority later needs fencing, it should be a separate contract digest rather than overloaded into the minimal route fingerprint.

## 6. Legacy migration should be one-way fail-closed

Current `manager-handoff.json` accepts versions 1–3 and matches objective hash + vertical + domain with `identity_generation <= current_generation`. Version 3 does not bind workflow mode, research target/direction, venue, or a protected route revision.

Safe migration:
- continue parsing v1–v3 for audit/recovery provenance;
- never let v1–v3 authorize the v4 route-aware fast path;
- one Manager reconciliation emits v4 with the canonical route fingerprint and final continuous generation;
- once v4 exists, drain/SIGTERM lifecycle increments may still use `identity_generation <= current_generation` only when objective hash and canonical route fingerprint match exactly.

Do not synthesize a missing historical fingerprint from the current route: that would bless the very drift the migration is meant to detect.

## 7. Call-site regression matrix

Add source-level/integration regressions around each semantic class:

1. `/daemon/start` against `operator authority hold` must start/attempt the process without enabling the campaign.
2. `/daemon/start` against `operator drain-stop` may re-arm through the boot gate, but only after admission/spawn reaches the boot path.
3. Admission refusal with resume intent must leave `continuous.json` byte-for-byte unchanged.
4. `/continuous enabled` followed by daemon start must not perform a second semantic transition; it should adopt the already-authorized generation.
5. Manager message/stream task dispatch with `result.continuous=true` must not broaden authority beyond the Manager-produced state.
6. Operator decision `continue` may be durably accepted even if route/generation changed, but execution rearm must go through semantic reconciliation rather than direct enable.
7. Scheduled upgrade must inspect current state at restart time and must not restore its saved objective snapshot.
8. `replace_project_daemon(... resume_continuous=True)` must use the same boot gate and preserve semantic stop/hold reasons.
9. Handoff fence + process start must trigger Manager reconciliation, never process-only rearm.
10. v4 identity must reject same-vertical `staged -> direct`, target-level, direction-mode, domain, or venue drift.
11. v4 identity must keep fast restart across ordinary stage progress with unchanged route fingerprint.
12. v1–v3 identity must force exactly one Manager reconciliation before a v4 fast path is available.

## Scope

This is source-level call-site, normalization, and failure-boundary analysis against public `lbx154/Argus` commit `8c5a0e356c470ad4cbdc904a7fbe4de14af366cf`. No live exploit, private system, or destructive action was performed. The boot gate, dedicated handoff reason, and v4 fingerprint are adaptation proposals and remain unmeasured until the regressions are implemented.

## Exact continuation

1. Trace `set_continuous`, Manager handoff, and operator-decision call paths to define a single semantic `reconcile_or_rearm` function signature and prove no remaining upstream path directly flips a stale disabled campaign to enabled.
2. Specify the two-CAS handoff-fence payload schema, including source-objective provenance versus Manager-clean execution task, and its exact generation semantics.
3. Build the v4 fingerprint helper from existing normalizers and enumerate tests for invalid/legacy route values, custom data-domain roots, venue whitespace/truncation, and stage-progress invariance.
4. Audit immediate upgrade and replacement for generation/CAS loss even after semantic pre-mutation is removed.
5. Keep external/admin `PIPELINE_STATE` writer fencing as a separate branch; do not conflate it with continuous/restart authority.
