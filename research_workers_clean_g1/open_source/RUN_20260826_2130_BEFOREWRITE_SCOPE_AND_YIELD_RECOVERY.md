# Open Source Systems Scan — `before_write` scope refinement and pipeline-yield recovery

Frozen clean tuple remains note main `31face47d7ee4b9b686ee3ae55fb9dbdeb877284`, control 10, open_source config 5 (`118f440957ba4654e804af902aa09a9224acca43`). Public Argus source remains `8c5a0e356c470ad4cbdc904a7fbe4de14af366cf`.

## Scope refinement

Repository-wide `before_write=` search finds only two production continuous-CAS call sites: Manager front-door continuous handoff and daemon-boot Manager handoff.

The **live front-door path remains the strong split-brain case** from the prior checkpoint: route B commits in the callback, a later `continuous.json` replace failure leaves continuous A intact, the front-door exception path only emits failure, and the pipeline-yield token is cleared in `finally`. There is no route compensation after the callback has returned successfully.

The **daemon-boot path has an additional local fail-closed guard** and should not be generalized identically. It also commits the Manager route in `before_write`, but if the CAS/replace raises and continuous generation is still the expected generation, boot sets `init_continuous=False`, clears `init_objective`, and records the old enabled generation in a suppression structure before constructing the supervisor. Thus the just-starting process does not immediately execute old continuous A under newly committed route B. The durable route/continuous files can still be out of sync until a later Manager reconciliation, but the current boot process explicitly suppresses that old generation.

This makes the priority patch target the active front-door handoff first; boot needs a durability/coherence cleanup but already has a runtime safety backstop.

## Pipeline-yield crash behavior

`manager/_session_ops.py` gives `.manager_pipeline_yield.json` a token, requesting PID, and timestamp. `manager_pipeline_yield_requested()` self-clears the file if:

- token/PID is invalid;
- requesting PID no longer exists / cannot be signaled; or
- request age exceeds pipeline-lock timeout + 60 seconds.

So a requester crash does not create an unbounded permanent yield wedge. This is a positive control. It does **not** fix the live front-door I/O failure case: the exception is caught in-process and `finally` explicitly clears the yield immediately while the route side effect remains.

## Existing continuous CAS semantics confirmed

Although `ContinuousConfigState.generation` is declared `compare=False` for dataclass equality, the actual `_same_continuous_state()` used by CAS explicitly compares generation in addition to enabled/objective/open-ended/done fields. Therefore the proposed stale-write fencing genuinely includes generation; generic dataclass `==` in some tests should not be mistaken for the CAS predicate.

## Updated exact continuation

1. Inspect tests/front-door fault injection coverage for the active-handoff post-precommit replace failure; formulate a minimal failing regression without live state mutation.
2. Inspect handoff identity publication/readback after successful commit and determine the exact coherent state tuple for a disabled handoff-fence protocol.
3. Inspect boot suppression lifecycle to ensure a future restart after durable route/continuous mismatch always forces Manager reconciliation rather than trusting old handoff identity.
4. Continue decision-lineage and lifecycle-resurrection fixes in parallel; do not broaden the boot finding beyond its observed runtime guard.
5. Keep external/admin PIPELINE_STATE writer fencing as a separate branch.
