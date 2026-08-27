# Primary verification — Argus continuous-state unknown-field / fence semantics

Verified at: 2026-08-27T15:47:04+09:00

## Frozen bootstrap tuple

- note main SHA: `e369842ab9090cce3925e29cbb4619eaa8f8b29b`
- `automation_control/DESIRED_STATE.json` blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- control revision: `11`
- `automation_control/DOWNSTREAM_STATE.json` blob: `3006c9416c64a704f4ad9e3071b7ee8edc7bf178`
- role: `primary_source_verifier`, config revision: `5`
- bootstrap_valid: `true`

## Clean source claim inspected

Source-qualified clean artifacts at the frozen note SHA:

- `research_workers_clean_g1/open_source/RUN_20260827_1505_FENCE_REGRESSIONS_BACKLOG_IMMUTABILITY.md`, blob `fda7cb48505837abd80a5c76a5aecccedeb6c832`
- predecessor `research_workers_clean_g1/open_source/RUN_20260827_1401_FENCE_CALLSITE_MATRIX.md`, blob `6585c0b502c22c9f9d4327fe5fdaed1804c1cacf`

Public primary source pinned to `lbx154/Argus@33da786bbc6787a2eeb63a5f492498eae87c78c7`.

## Verdict

### 1. CONFIRMED — an unmodeled `handoff_fence` JSON key would not survive current state semantics

At the pinned Argus commit, `ContinuousConfigState` models only `enabled`, `objective`, `open_ended`, `done_reason`, `done_at`, and `generation`.

`_read_continuous_state_unlocked()` parses a JSON object by selecting only those known keys. Unknown keys are not retained in the returned state. `_continuous_state_reserve_text()` likewise serializes only modeled fields. `_write_continuous_config_unlocked()` constructs a fresh replacement dictionary containing only the modeled fields. Therefore an extra physical JSON key such as `handoff_fence` would be ignored on read and erased by the next successful ordinary write/CAS/disable rewrite unless the schema/parser/serializer are changed to model it explicitly.

This is stronger than a compatibility-style concern: `compare_and_swap_continuous_config()` reads through the same lossy parser and `_same_continuous_state()` compares only the six modeled fields. A change to an unknown physical field with all modeled fields unchanged is invisible to CAS equality. A successful CAS may then overwrite the file and erase the unmodeled field.

**Scope:** source-level behavior at the exact pinned commit. No live daemon race or production incident was induced.

### 2. CONFIRMED SOURCE-REACHABLE — malformed/invalid continuous JSON collapses to the permissive default state

`_read_continuous_state_unlocked()` returns `ContinuousConfigState()` on JSON decode, type, value, or I/O errors. Thus corrupt/unparseable physical state is represented to callers as the default disabled/empty/open-ended/generation-0 state rather than as an explicit corruption/unknown state.

The read alone does not rewrite the bad file. However a later ordinary write, or a CAS whose expected value is the parsed default, can replace the physical file with a fresh modeled-state object. This is a storage-layer **corruption-to-default fail-open/reset path** for authority metadata.

This must not be conflated with the separate Manager semantic “replacement reset” behavior. The latter remains the next verification target.

**Scope:** source-reachable storage semantics. This audit did not prove that a current production caller actually encounters corrupt JSON and then performs an expected-default CAS.

### 3. CONFIRMED — current durability primitives are substantial, but only for the modeled state

The pinned implementation has:

- an inter-process continuous-config lock;
- temp-file write plus flush and file `fsync`;
- atomic `os.replace`;
- parent-directory `fsync` after replacement;
- modeled-state generation/CAS;
- quota reserve handling;
- distinct exceptions for ambiguous post-replace durability and callback-before-replace split outcomes.

The existing `tests/daemon/test_state_portable.py` exercises failed replace preservation, lock behavior, quota reserve/retry, delayed quota failure, post-replace ambiguity, callback-before-replace failure, and reader/writer locking.

Those guarantees do **not** automatically extend to a future authority field that is absent from the model/equality contract.

### 4. NOT CURRENT IMPLEMENTATION — first-class fence, creation stamp, strict Manager reconcile receipt

Repository searches at the pinned Argus commit returned no implementation hits for `handoff_fence`, `creation_stamp`, or `ReconcileReceipt`. The clean worker’s proposed first-class fence, immutable creation stamp, and strict Manager-reconciliation receipt are therefore adaptation/design requirements, not existing Argus guarantees.

The worker’s specific requirement that a fence participate in dataclass parsing, serialization, reserve text, CAS equality, and every writer is supported by this source audit. Merely adding an extra JSON field without those changes is unsafe.

## Existing-test gap

The inspected state portability tests do not cover:

1. preservation/rejection semantics for unknown critical JSON fields;
2. unknown-field participation in CAS equality;
3. malformed JSON failing closed instead of collapsing to default;
4. first-class handoff-fence serialization/equality/finalization.

These are proposed regression targets, not tests claimed to exist today.

## Exact scope and non-claims

- No Argus source was mutated.
- No production daemon or live failure was injected.
- No claim is made about incident frequency.
- No claim is made that the proposed `ManagerReconcileReceipt` already exists or has measured benefit.
- The continuous-storage corruption/default behavior is distinct from Manager route/vertical/stage replacement-reset semantics.

## Exact next verification

Audit the actual Manager replacement-reset path at `lbx154/Argus@33da786bbc6787a2eeb63a5f492498eae87c78c7`: determine whether missing/corrupt project-local or custom-domain state can silently fall back to built-in `research` (or another permissive route), and whether any current postcondition binds the reset to the exact intended route/vertical/stage/domain. Test the worker’s “replacement reset is fail-open” claim separately for built-in research, same-first-stage replacement, and project-local custom-domain cases. Keep any proposed strict `ManagerReconcileReceipt` distinct from current implementation evidence.