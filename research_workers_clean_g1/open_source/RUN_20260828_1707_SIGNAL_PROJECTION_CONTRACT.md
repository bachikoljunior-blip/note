# Open Source follow-up — default signal logging breaks the durable Mission View input contract

- role: `open_source`
- observed_at: `2026-08-28T17:07:05.986481+09:00`
- frozen semantic control tuple: note `a90288aa7a262cdb009ee7a4d35236516dea11c3`, control `15`, config `6`
- post-freeze note head used only for authorized write coordination: `9ffc88c7a49c8c1da276ba6f66efdf22d0d3096f`
- public Argus main observed: `2894b434affaff3a28c1fbbcd5c39f2e7a832236`
- public Portalocker develop observed: `c86f80c2505de8e44fb9d2493eb94ab96201fef6`
- clean scope unchanged: own state + public sources only; no O, other-worker, downstream, legacy, or shared-ledger semantics

## Candidate013 — signal persistence and durable Mission View disagree on their event contract

Argus main advanced by seven public commits from the previous observed Argus head, but the canonical event sink, Mission View state/dispatch, planner-verdict outbox, and dependency floor files inspected here still retain the previously identified locking/recovery shapes. The new finding is independent of those races and exists even in a single process with no rotation.

`JsonlEventSink.handle_event()` applies the default `signal` persistence filter before `_append()`. Mission View projection is executed only inside `_append()`, after the canonical JSONL write. Therefore an event filtered from the canonical log is also filtered from the persistent Mission View. This is the right ordering for replayability in principle, but the declared projected event set is not a subset of the events guaranteed to survive the default signal policy.

The exact static mismatch among current `_PROJECTED_EVENT_TYPES` is narrow:

1. `round.review.started` is projected by Mission View but is not in `SIGNAL_EVENT_TYPES`, its type contains no error/fail/escalation marker, and its production emitter supplies only `round_index`, `round_max`, and `session_id`. Under the default signal policy it is therefore deterministically skipped before `_append()` and can never set the persisted reviewer role to `active / Reviewing benchmark evidence`.
2. `engineer.progress` is also projected but is not guaranteed durable under signal. Only payloads whose text carries an error/win marker survive the signal filter. Ordinary progress/action rows therefore update downstream live observers but do not update the persistent Mission View.

This is more than a cold-rebuild defect: the live persistent read model itself never receives those filtered events. A later schema/cursor reconciliation cannot recover an event that the canonical log never contained.

## Web snapshot consequence, scoped carefully

`role_activity()` is itself reconstructed from the persistent event-log tail. It recognizes `round.review.started`, `agent.io.start`, and `engineer.progress` as active-role evidence. The WebAPI `build_snapshot()` derives its `roles` payload from that log-backed `role_activity()` and then overlays those roles into `snapshot_mission_view()`.

Because the default daemon runtime constructs `JsonlEventSink` without overriding verbosity, it runs in signal mode. For the reviewer-start transition, both paths used by the periodic Web snapshot are therefore missing the same durable evidence: persistent Mission View never projected `round.review.started`, and `role_activity()` cannot read it from JSONL. Downstream in-process/live sinks still receive the event, so this finding does **not** claim every real-time frontend stream is blind; it is specifically a durable/periodic-snapshot consistency defect.

## Minimal remediation boundary

Do not fix this by projecting events that were deliberately omitted from the canonical log: that would make `mission-view.json` impossible to reproduce from its stated ground truth. Instead make the persistent read-model contract explicit.

A low-churn split is:

- Promote the low-volume lifecycle transition `round.review.started` into the default signal set. It is the missing coarse reviewer-active state transition analogous to already-durable `life.manager.intent.started`, `life.planner.start`, and `round.start`.
- Treat high-frequency `engineer.progress` as ephemeral/live UI state unless Argus deliberately chooses to persist all such rows. Remove it from the *durable* Mission View input contract or introduce a separate live-only overlay; do not let payload-dependent signal markers decide whether a supposedly event-sourced durable projection sees an event.
- Add an invariant test over the durable Mission View event set: every durable projected type must be unconditionally persisted by default signal policy. Keep payload-conditional/noisy events out of that set.
- Add an end-to-end regression using the actual default `JsonlEventSink`: emit `round.start -> round.review.started` and assert both `events.jsonl` and a periodic `build_snapshot()` can show Reviewer active before the verdict arrives. A second test should prove an ordinary `engineer.progress` remains absent from the clean canonical log and therefore is not required for durable reconstruction.

This contract split should land before schema-7 cursor reconciliation. Otherwise the new cursor could make replay exact only with respect to an already incomplete canonical input set.

## Event-authority continuation remains unchanged, with one commit-boundary guard

The prior Portalocker conclusion remains supported: Argus advertises `portalocker>=3`, while the inspected Windows low-level raw-fd surface first excludes the upstream-known position/fallback/OVERLAPPED correctness defects at `>=4.2`. Portalocker 4.2 accepts raw descriptors, normalizes Windows lock position to byte zero, maps nonblocking contention to `AlreadyLocked`, and leaves other failures as `LockException`.

For canonical event authority, retain `os.open(..., 0600)` plus low-level `LOCK_EX|LOCK_NB`, retry only `AlreadyLocked`, and propagate permanent acquisition failures. All sidecar cleanup after the canonical data append—including unlock and fd close—must be prevented from converting an already-committed event into an apparent append failure that a caller could retry.

## Exact continuation

First settle candidate013 as a durable-vs-live projection contract: promote `round.review.started` to signal, split payload-conditional `engineer.progress` out of durable Mission View semantics, and add the default-sink + Web snapshot invariant/regression. Then implement/source-map the candidate009/011 shared event-authority primitive with `portalocker>=4.2`, pre-rotation one-byte delimiter isolation, and byte-based stable physical-row iteration. POSIX readers may pin handles/end offsets under shared `flock`; Windows correctness scans hold exclusive event authority. Next enforce `events.lock -> mission-view.lock`, then finish Planner verdict `FOUND / ABSENT / UNKNOWN` and explicit `iter_call_events` corruption behavior. Keep candidate008 power-loss fsync durability and candidate005 transition provenance separate.

No repository mutation outside the authorized open_source state/receipt namespaces was performed in this invocation.
