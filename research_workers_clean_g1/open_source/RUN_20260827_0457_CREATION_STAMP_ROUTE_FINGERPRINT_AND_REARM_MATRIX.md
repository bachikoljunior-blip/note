# Open Source Systems Scan — immutable creation stamp + source-exact route fingerprint + rearm matrix

Invocation started: 2026-08-27T04:57:17+09:00
Checkpointed: 2026-08-27T05:02:38+09:00

Frozen semantic tuple for this invocation:
- note main SHA: `00217016a980e18d7c93fd8603ec0c3dce34b30d`
- sanitized control revision: `10`
- open_source config revision: `5`
- open_source config blob: `118f440957ba4654e804af902aa09a9224acca43`

Independence: own clean state + public sources only. No O/O-derived state, other-worker state/config, downstream semantics, legacy/pre-independence research, aggregate execution ledger, or other-role receipts/configs were used. The selected control/config tuple was frozen before the first role-local/public-source semantic read.

Public source head verified during this run:
- `lbx154/Argus` public `main`: `33da786bbc6787a2eeb63a5f492498eae87c78c7`.
- This head is 4 commits ahead of the prior audited `0904e8de645a6e4988e49815c9d9e2c3b511c467`; the changed files are CLI/launcher/release/frontend bundle surfaces, not the continuous/backlog/Manager handoff files audited below. Prior source-level findings therefore still apply to current public main unless explicitly narrowed here.

## 1. New correction: `ensure_item_exact` must compare a dedicated immutable creation stamp, not recompute identity from the current backlog row

The previous checkpoint correctly rejected a digest of the full `BacklogItem`, but it still left open the idea that recovery could recompute an identity from a subset of apparently immutable semantic fields.

Current Argus source shows that is not robust enough:

- `Backlog.update(item_id, **fields)` performs generic `setattr` for any dataclass field present on the row.
- `backlog_guard.ensure_manager_decision()` may legitimately update an already-routed row's `manager_decision`, and may also replace `objective`, when the previously routed vertical becomes unavailable and the item is re-routed through Manager.
- Therefore a row can remain the same persisted mission identity while some route/execution fields legitimately change after creation.

Consequently, a recovery primitive that recomputes its creation identity from the row's *current* objective/Manager-decision fields can falsely conflict with a legitimate already-persisted mission. Conversely, omitting those fields entirely can accept a deliberately pre-seeded conflicting row with the same target id.

The narrow fix is to persist an explicit immutable creation stamp on first insert. `ensure_item_exact` should compare that stamp, not mutable live fields.

### Required immutability property

A new optional field such as `creation_identity`/`creation_stamp` must not become just another field mutable through generic `Backlog.update`. Either:

1. `Backlog.update` explicitly refuses changes to a non-empty creation stamp; or
2. the stamp is held in a separate append-once/indexed structure updated atomically under the same backlog lock.

The first option is lighter for the current JSONL design. Legacy rows may keep an empty stamp; the new handoff-fence path should require a non-empty stamp for exact recovery instead of silently treating an unstamped legacy row as equivalent.

## 2. Source-exact creation stamp v1 for the current continuous Manager path

`manager/dispatch.py::_persist_operator_priority_item()` currently creates the continuous operator-priority row with these semantic creation inputs:

- `item_id = root_task_id`;
- `objective = execution_body`;
- `original_objective = execution_body`;
- priority frozen as `min(head_priority - 1, -1)` from the pending queue at first creation;
- ordered tags exactly: `manager`, `operator`, `operator_priority`, `scope:bounded`, `review:required`, `stage_transition:skip`;
- `iterate = false`;
- `iteration_max_cycles = 1`;
- `context_refs = _merge_context_refs(context_refs)`;
- `manager_decision = decision_evidence(division) or {"routed": true}`;
- unprovided `work_kind` currently normalizes to `scope` via `DEFAULT_WORK_KIND` / `parse_work_kind`.

`_merge_context_refs` already provides a source-level canonicalization seam: it converts nonblank keys/values to strings, requires a nonblank `ref`, deduplicates by `(kind, ref, attachment_id, why)`, preserves first occurrence order, and preserves the normalized ref dict that survives the dedupe.

Recommended creation-stamp schema v1:

```text
schema_version = 1
target_item_id
manager_intent_id
execution_task_sha256        # SHA256(execution_body.strip(), UTF-8)
original_objective_sha256    # same today, retained so future divergence fails visibly
frozen_priority
tags                         # exact ordered creation list
iterate = false
iteration_max_cycles = 1
work_kind = "scope"
context_refs_sha256          # canonical JSON of _merge_context_refs output; object keys sorted, list order preserved
manager_decision_sha256      # canonical JSON of the creation-time decision_evidence snapshot
protected_route_fingerprint  # separate route authority binding, defined below
```

Do **not** include:

- `ts` or display `title` (volatile/display-only creation output);
- `status`, started/finished timestamps, running owner, attempts/retries, outcomes, notes, or other runtime-mutable fields;
- the current post-creation `objective` or `manager_decision` as a substitute for the stored stamp.

The fence should persist the stamp before any route/backlog side effect. The new row should persist the same stamp atomically with the row. Recovery semantics then become:

- target id absent -> append row + stamp once;
- target id present with equal stored stamp -> success, regardless of legitimate later runtime-field changes;
- target id present with different/missing stamp -> fail closed while the handoff remains disabled.

## 3. `manager_decision` alone is provably too weak to bind the protected route

`life/supervisor/backlog_guard.py::decision_evidence()` persists only:

- vertical;
- stage;
- workflow_mode;
- research_target_level;
- learned_vertical_status;
- optional `require_independent_review`;
- `routed=true`.

It does **not** carry research `domain`, `research_direction_mode`, or `target_venue`.

Therefore even a perfectly stable creation-time `manager_decision` digest cannot distinguish all same-vertical route changes. The dedicated protected-route fingerprint is not redundant; it is necessary to bind the mission to the Manager-owned route that authorized its creation.

## 4. Source-exact protected-route fingerprint v4

Current public Argus exposes the required canonicalizers:

- **vertical**: `skills/vertical_select.py::_strip_needed` -> trim + lowercase, remove trailing `-needed`, legacy `direct` maps to `software`; final validity should still pass the current known/data-domain resolver.
- **domain**: Manager `_sluggify_name` -> trim/lowercase, `-` and spaces become `_`, other non-`[a-z0-9_]` runs become `_`, trim outer `_`.
- **workflow_mode**: trim/lowercase; only `direct|staged` are valid.
- **research_target_level**: `normalize_research_target_level` -> trim/lowercase and require `exploratory|publishable|doctoral`, else empty/not-applicable according to the committed route.
- **research_direction_mode**: `normalize_research_direction_mode` -> trim/lowercase and require `broad|locked`, else empty/not-applicable.
- **target_venue**: current Manager parser uses whitespace collapse (`" ".join(value.strip().split())`) and truncation to 100 characters; it does **not** lowercase. A source-exact v4 helper should preserve that behavior rather than invent a casefold unless a separate venue-identity normalizer is proven equivalent.

Recommended fingerprint input:

```json
{
  "schema_version": 4,
  "vertical": "<canonical>",
  "domain": "<canonical-or-empty>",
  "workflow_mode": "<canonical>",
  "research_target_level": "<canonical-or-empty>",
  "research_direction_mode": "<canonical-or-empty>",
  "target_venue": "<whitespace-normalized-or-empty>"
}
```

Hash canonical UTF-8 JSON with sorted keys and compact separators. `current_stage` remains excluded because valid progress changes it without changing the campaign route.

Current `manager-handoff.json` remains v3 and binds only objective hash + vertical + domain + a generation inequality (`identity_generation <= current_generation`) + intent id. It still cannot detect same-vertical route drift such as `staged -> direct`, research target/direction change, or target venue change. Legacy v1-v3 identities should therefore cause one fresh Manager reconciliation before a v4 identity is emitted; treating them as v4-equivalent would preserve the missing-authority gap.

## 5. Exact-state reconcile/rearm matrix is now source-mapped

Current public main still contains multiple process-control paths that restore a copied objective instead of CASing the current disabled record:

### Web start

`webapi/daemon_lifecycle.py::start_project_daemon(... resume_continuous=True)` reads continuous state and, before daemon admission/spawn, directly re-enables any disabled nonempty objective whose `done_reason.lower().startswith("operator ")`. This is broader than the daemon's exact process-stop allowlist and occurs before admission, so a rejected daemon start can still leave durable campaign state re-enabled.

### Daemon boot

`daemon/_life_worker_identity.py::_rearm_operator_drain_for_resume` correctly restricts semantic eligibility to `RESUMABLE_STOP_REASONS` (drain-stop and graceful SIGTERM/SIGINT), which is a strong positive control, but then re-enables through non-CAS `write_continuous_config` using the previously read state.

### Immediate upgrade

`webapi/daemon_upgrade.py::upgrade_project_daemon` snapshots `continuous` before the drain. After a successful stop it writes `enabled=true, objective=<pre-drain snapshot>` and then starts the daemon. A concurrent semantic stop/replacement can therefore be overwritten by the stale pre-drain snapshot.

### Scheduled upgrade

The durable upgrade request stores `resume_continuous` plus a copied objective. `_complete_scheduled_daemon_upgrade` later uses those request-time values to call non-CAS `write_continuous_config(enabled=true, objective=copied_objective)` before restart. It does not bind the request to the current continuous generation/route.

### Replacement

`replace_project_daemon` delegates the target start to `start_project_daemon(... resume_continuous=...)`, so it inherits Web-start rearm semantics rather than establishing a separate exact-state authority.

These paths can converge on one rule:

> Process-control code must never restore a caller-copied objective. It may pass a resume *intent*, but the sole `reconcile_or_rearm` boundary must lock/read the **current** continuous record and either (a) exact-CAS a disabled state whose reason is in the narrow process-stop allowlist, or (b) require semantic Manager reconciliation against the current protected-route fingerprint. Stop/hold/completion states remain disabled.

Scheduled/immediate upgrade should store process identity/request metadata, not an authoritative objective snapshot to resurrect later.

## 6. Candidate refinement

`clean-os-g1-005` is now best stated as:

> Keep Argus's existing Manager pipeline lock and deterministic evidence gates. Before a continuous replacement performs any external side effect, exact-CAS the standing campaign into a disabled handoff fence that freezes a dedicated immutable mission creation stamp and the v4 protected-route fingerprint. Persist the target backlog mission with an atomic exact-insert that compares the stored immutable stamp (not mutable live row fields). Only after route/backlog reconciliation exact-CAS the target objective enabled. All daemon start/upgrade/replacement resume paths must consume the currently observed disabled state through one exact-state reconcile/rearm boundary, never restore a copied objective snapshot.

This remains an unimplemented adaptation proposal, not a measured improvement.

## Scope and uncertainty

- No live exploit/crash was executed and no upstream Argus repository was mutated.
- Findings are source-level transaction/recovery analysis at public main `33da786bbc6787a2eeb63a5f492498eae87c78c7`.
- The source proves the relevant mutation/rearm shapes; it does not prove these failures have occurred in production.
- The proposed creation-stamp field, immutability enforcement, route-fingerprint helper, fence schema and unified reconcile/rearm boundary are not implemented or benchmarked.

## Exact continuation

1. Trace every legitimate post-creation mutation of continuous Manager backlog rows and design the narrowest `creation_stamp` immutability rule/regression suite, including a legitimate Manager re-route after creation and a pre-seeded conflicting target id.
2. Locate the best code home for a shared `protected_route_fingerprint_v4()` that reuses current normalizers rather than duplicating them; specify v1-v3 migration/readback tests and case-only venue behavior explicitly.
3. Enumerate every caller of `start_project_daemon`, `_rearm_operator_drain_for_resume`, immediate/scheduled upgrade and replacement to design one `reconcile_or_rearm` API contract without changing correct drain/SIGTERM behavior.
4. Keep external/admin `PIPELINE_STATE` writer fencing as a separate branch; do not conflate it with continuous/restart authority.
