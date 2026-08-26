# Open Source Systems Scan — duplicate-ID invariant + venue-identity correction

Invocation started: 2026-08-27T06:00:11+09:00
Checkpointed: 2026-08-27T06:04:02+09:00

Frozen semantic tuple:
- note main SHA: `4b05024dd6a2d98b5092a10a6703dfcf76ad6f32`
- sanitized control revision: `11`
- open_source config revision: `5`
- open_source config blob: `118f440957ba4654e804af902aa09a9224acca43`

Independence: own clean state + public sources only. No O/O-derived state, other-worker state/config, downstream semantics, legacy/pre-independence research, aggregate ledger, or other-role receipts/configs were used. The control/config tuple was frozen before the first role-local/public-source semantic read.

Public source head verified:
- `lbx154/Argus` public `main`: `33da786bbc6787a2eeb63a5f492498eae87c78c7` (unchanged from the prior open_source checkpoint).

## 1. New invariant: backlog IDs should be globally unique, but recovery needs exact-idempotent insert

Current `argus_skill/life/memory.py` has an asymmetry:

- `Backlog.add(item)` appends without checking whether `item.id` already exists.
- `Backlog.add_many(...)` rejects duplicate IDs both within the batch and against existing rows.
- plan-revision replacement paths also reject reused IDs.
- `Backlog.update(item_id, ...)` stops at the first matching row.

Therefore a duplicate ID created through the single-row `add()` path is not merely cosmetic: later update/settlement by ID becomes ambiguous because only the first matching row is mutated, while dependency maps and other scans may see a different duplicate ordering.

For `clean-os-g1-005`, the narrow recovery primitive should therefore not be implemented as another plain `add()` call. Recommended split:

1. Strengthen ordinary `Backlog.add()` to reject an already-existing ID, matching `add_many` / plan-revision invariants.
2. Add a dedicated `ensure_item_exact(item, creation_stamp)` under the same backlog lock for crash recovery:
   - ID absent -> append exactly once;
   - ID present + equal immutable creation stamp -> idempotent success, no second row;
   - ID present + missing/different stamp -> fail closed.

This preserves global ID uniqueness while still making a partially completed continuous handoff recoverable.

## 2. Narrowing: normal Manager-message continuous dispatch already has a pre-side-effect stable target ID

The Web/TUI Manager turn path allocates `root_task_id = BacklogItem.new_id()` during classification and threads that ID into `enqueue_mission(...)`. The continuous persistence callback creates the operator-priority row with `item_id=root_task_id`.

So for the normal Manager-message path, the target mission ID does **not** need to be generated inside the post-route persistence callback; a stable ID already exists before `manager_continuous_handoff` performs its side effects. The handoff fence can freeze this existing ID before route/backlog mutation.

By contrast, the project CRUD `set_continuous(... enabled=true)` wrapper calls Manager continuous handoff without a root task ID, but that path does not provide the backlog `persist` callback and therefore does not create the operator-priority backlog row. The exact-insert requirement should be conditional on a persistent target mission actually being part of the handoff.

This narrows the fence contract: `target_item_id` is mandatory when `persist` is present; it is not an invented backlog identity for control-only continuous enablement.

## 3. Correction: route fingerprint must use semantic venue identity, not case-preserving display normalization

The prior checkpoint proposed preserving Manager's `target_venue` whitespace/case form in the v4 protected-route fingerprint because the Manager parser currently preserves case.

Public research-vertical source shows that is too strict for *identity*:

- `venue_profiles._normalize_venue_key(key)` uppercases, removes non-alphanumeric separators, and strips a trailing 2- or 4-digit year.
- Venue research compares a researched profile key and selected target through this normalizer.
- Thus strings such as `AAAI-26`, `aaai2026`, and `AAAI 2026` are intentionally the same venue identity.

A route fingerprint that hashes the raw/case-preserved target would cause false route drift and unnecessary Manager reconciliation for semantically identical venue spellings.

Corrected v4 rule:

```text
vertical                 -> existing vertical canonicalizer
domain                   -> Manager domain slug normalizer
workflow_mode            -> current direct|staged normalizer
research_target_level    -> current research target normalizer
research_direction_mode  -> current direction normalizer
target_venue             -> venue_profiles._normalize_venue_key when nonempty
```

The fingerprint should still exclude `current_stage`, because valid progress changes stage without changing route identity.

Required regression cases:
- `AAAI-26` == `aaai2026` == `AAAI 2026`;
- separator/case-only changes do not force a fresh Manager handoff;
- genuinely different venue keys do;
- dynamic profile key and selected target compare through the same venue normalizer before admission.

## 4. Creation stamp immutability remains a distinct requirement

`Backlog.update()` performs generic `setattr` for any existing dataclass field. Legitimate post-creation paths do mutate status/runtime fields and, via backlog guard rerouting, may replace `manager_decision` and `objective`.

Therefore the creation stamp cannot be reconstructed from current mutable fields and cannot be left writable through the generic update API. If stored on `BacklogItem`, `Backlog.update()` must reject changing a nonempty stamp. Normal status/objective/manager-decision evolution remains allowed and recovery compares only the stored immutable creation stamp.

## Candidate refinement

`clean-os-g1-005` is now:

> Keep existing Manager pipeline locking and deterministic evidence gates. Before continuous replacement side effects, exact-CAS the standing campaign into a disabled handoff fence carrying the already-reserved target mission ID (when a backlog persist is part of the handoff), an immutable creation stamp, and a semantically normalized protected-route fingerprint. Enforce globally unique backlog IDs; recover with an exact-idempotent insert rather than a duplicate append. Canonicalize venue identity with the research vertical's existing `_normalize_venue_key`, not raw display spelling. Finish by exact-CAS enabling the target objective. Process resume/upgrade/replacement must consume current disabled state through one exact-state reconcile-or-rearm boundary rather than restore copied objectives.

This remains an unimplemented adaptation proposal, not a measured performance improvement.

## Scope / uncertainty

- No upstream repository mutation or live exploit/crash was performed.
- Findings are source-level transaction/identity analysis at public Argus main `33da786bbc6787a2eeb63a5f492498eae87c78c7`.
- The proposed global duplicate guard, creation stamp, handoff fence, route fingerprint v4, and unified reconcile/rearm boundary are not implemented or benchmarked.

## Exact continuation

1. Finish a field-by-field audit of every legitimate `Backlog.update` caller for a continuous Manager-created row; classify fields as creation-immutable vs runtime-mutable and specify regression coverage for reroute/status/settlement/operator-decision paths.
2. Design the smallest `ensure_item_exact` API and tests using the real `Backlog`: duplicate ordinary `add` must fail; exact recovery must be idempotent after legitimate mutable-field changes; same ID with different/missing stamp must fail closed.
3. Locate a shared public helper home for `protected_route_fingerprint_v4` that imports/reuses current vertical/domain/research/venue normalizers without cyclic dependencies; specify legacy v1-v3 handoff migration.
4. Complete the start/boot/immediate-upgrade/scheduled-upgrade/replacement caller map into one exact-state `reconcile_or_rearm` contract. Keep external/admin `PIPELINE_STATE` writer fencing separate.
