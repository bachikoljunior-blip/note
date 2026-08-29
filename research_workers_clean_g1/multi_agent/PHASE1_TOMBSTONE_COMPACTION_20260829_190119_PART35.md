# Phase-1 multi_agent checkpoint — cancellation tombstone compaction + complete-rewind boundary (Part 35)

## Frozen semantic tuple

- role: `multi_agent`
- frozen note main SHA: `68446d6322630d4ba65d734db1422c50a5782f78`
- sanitized root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- transport: SHA-only ref lookup + exact-SHA reads
- predecessor: Part 34 / reservation-level CANCELLED tombstone + lazy cell release
- post-freeze main movement was rechecked; authority blobs stayed unchanged.

## Selected leaf

Part 34 showed that a current reservation-level `CANCELLED` witness can safely decouple logical revocation from best-effort cell cleanup, but deleting that witness merely because cells look clean is unsafe under stale-cell restore. This leaf tests compact witnesses and makes the complete repository-rewind case explicit.

## Public mechanism audit

GitHub protected branches can disable branch deletion and force pushes, and administrators can optionally configure stronger non-bypass behavior. GitHub also documents that protected branches for **private** repositories are available with GitHub Pro/Team/Enterprise offerings, rather than being an unconditional zero-cost property of every private repository:
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

That means branch protection can be a useful deployment assumption, but it is **not accepted here as the generic Phase-1 anti-rollback solution**: the current control forbids counting a protected/admin execution step or paid-plan dependency as solved.

Kubernetes' distinction between reusable Name and lifetime-unique UID remains the public precedent for scoping any compact retirement watermark to an incarnation rather than a logical key name that may be reused:
- https://kubernetes.io/docs/concepts/overview/working-with-objects/names/

## Finite compaction lattice

Executable model: `research_workers_clean_g1/multi_agent/phase1_tombstone_compaction_20260829_190119_part35.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_tombstone_compaction_20260829_190119_part35.json`

The model has `576` scenario shapes and `3,456` strategy evaluations. A cancelled reservation spans one to three stable logical cells. It varies:

- no/partial/full retired-holder floor propagation;
- stale cell restore after tombstone compaction;
- cell delete/recreate;
- cell incarnation-sensitive identity;
- task/effect key reuse;
- task/effect key incarnation-sensitive identity;
- whether tombstone GC is attempted.

Compared strategies:

1. permanent per-reservation tombstone;
2. delete tombstone after current cleanup with no retirement floor;
3. monotonic retired-holder floor on every stable logical cell;
4. append-only terminal reservation index;
5. monotonic retired-generation watermark per canonical task/effect-key incarnation;
6. fail-closed no-GC.

A separate explicit history-pair proof covers complete same-domain repository rewind.

Counts are finite mechanism counts, not production probabilities.

## Strong incarnation slice

With both stable cell incarnation and task/effect-key incarnation fixed, each strategy has `144` scenarios:

| strategy | unsafe | false block | tombstone-GC completions | state shape |
| --- | ---: | ---: | ---: | --- |
| permanent tombstone | 0 | 0 | 0 | O(cancelled reservations) |
| cleanup-only GC | 36 | 0 | 72 | compact but unsafe |
| per-cell retired floor | 0 | 0 | 32 | O(stable logical cells) |
| terminal index | 0 | 0 | 72 | O(terminal reservations) unless separately compacted |
| **generation watermark** | **0** | **0** | **72** | **O(task/effect-key incarnations)** |
| fail-closed no-GC | 0 | 0 | 0 | O(cancelled reservations) |

### Result 1 — current cleanliness is not a retirement proof

In the strong-incarnation slice, deleting the reservation tombstone without first creating any monotonic retirement witness was **36/36 unsafe** when a stale holder cell was later restored.

This is the same authority/evidence distinction seen throughout the run: cleanup removes present references; it does not prove that an old identity can never reappear.

### Result 2 — a full per-cell retired floor is safe but wide

A monotonic `retired_reservation_generation >= g` floor on every stable logical cell allowed **32/32** tested GC completions with unsafe `0`. The tombstone was retained whenever the full required cell set had not yet durably advanced its floor.

If a cell can be delete/recreated and its floor resets while identity is not incarnation-sensitive, the full-floor strategy becomes **12/12 unsafe** in that recreate slice. A floor therefore belongs to the stable logical-cell incarnation, not merely its reusable name.

### Result 3 — one generation watermark per canonical task/effect-key incarnation is the smallest tested scoped witness

Under the explicit assumption that the repository authority itself is not completely rewound, a monotonic retirement watermark per canonical task/effect-key incarnation was **0/144 unsafe** in the strong slice and completed all `72/72` requested tombstone-GC operations.

The intended representation is conceptually:

`retired_through_generation[key_incarnation] = max(old_value, cancelled_reservation_generation)`

Every claimant/effect path rejects an old reservation generation at or below the watermark. A stale cell holder can therefore point to an already-compacted reservation record and still be rejected by the smaller key-level witness.

The watermark must be incarnation-scoped. With logical key reuse but no key-incarnation identity, it falsely blocked **72/72** new-history cases. The append-only terminal index had the same `72/72` false-block failure when keyed only by reusable logical name. Kubernetes' UID semantics are the public analogue for this history separation. citeturn171253search0

This is a scoped compression result, not a claim that one watermark solves arbitrary cross-key reservations or external sink authority.

## Complete same-domain rewind: explicit indistinguishability pair

Now consider two histories:

- **World A**: the repository legitimately never advanced beyond byte state `S = GRANTED(g1)`;
- **World B**: the repository advanced to `CANCELLED(g1)`, then every allowed repository witness — tombstone, watermark, cells, terminal index, own role-local state — was completely rewound/restored to the exact same bytes `S = GRANTED(g1)`.

A stateless deterministic scheduled invocation restricted to current same-domain repository state observes **the same bytes `S` in both worlds**.

Therefore it must make the same decision in both:

- admit `g1` -> preserves liveness in World A, but re-admits cancelled stale authority in World B;
- reject `g1` -> preserves World B safety, but false-blocks the legitimate World A history.

No rearrangement of witnesses that are all erased by the same complete rewind can distinguish the pair. Some non-rewound monotonic assumption/witness is necessary.

This is narrower than ordinary force-push risk. GitHub branch protection can prohibit force pushes/deletion when configured, but that is protected/admin configuration and GitHub documents plan-dependent availability for private repositories. It therefore cannot be introduced as the generic accepted Phase-1 route under the fixed zero-protected-step/zero-paid-dependency requirements. citeturn867474search0

## Phase-1 zero-dependency / zero-quota assessment

Within the tested **no-complete-authority-rewind** scope, the generation-watermark compaction is repository-local and Chat-capable: lightweight current-blob CAS/readback only, no hosted runner, Codespaces, artifact/LFS/package service, external coordinator, manual user execution, paid/trial/monthly credit, or incremental monetary cost.

Global Phase-1 closure is not claimed. Remaining unresolved children are:

1. **complete repository-authority rewind/restore with no surviving admissible anti-rollback state**;
2. **arbitrary protected external effect after `AUTHORIZED`** where compatible sink-side status/idempotency/fencing is unavailable.

The first is now an explicit observation-indistinguishability boundary rather than a vague rollback concern.

## Scope limits

- One cancelled reservation at a time over one to three stable logical cells.
- Generation watermark is abstracted as one monotonic authority field per canonical task/effect-key incarnation.
- All authority paths are assumed to consult the compact watermark after tombstone GC.
- Full rewind is modeled as exact byte restoration of every allowed repository witness.
- Protected branch/ruleset configuration is public mechanism evidence only, not an accepted dependency.

## Exact continuation

Next leaf: **anti-rollback redesign without protected/admin settings or paid/quota-bearing infrastructure**.

Audit whether any scheduled-Chat-visible, zero-cost, non-rewound state exists outside the repository authority bytes while staying inside CLEAN semantic-input rules — for example:

- immutable connector response identity that remains discoverable after rewind without a remembered SHA;
- Git object ancestry/history that remains current-discoverable after force rewind;
- automation-native durable state that is admissible as own state and not part of repository rewind.

Falsify each candidate against a complete branch rewind where all current repository bytes and own role-local files revert. If no admissible surviving state exists, persist the complete-rewind case as an unresolved capability boundary and move to the next non-conflicting concurrency leaf: **crash-safe effect-status reconciliation for repository-local `AUTHORIZED` transitions**.
