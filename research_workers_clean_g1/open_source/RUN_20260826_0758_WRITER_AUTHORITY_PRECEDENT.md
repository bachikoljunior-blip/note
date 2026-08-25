# Open Source clean_g1 — RUN_20260826_0758_WRITER_AUTHORITY_PRECEDENT

Frozen semantic control tuple for this physical invocation: note main `ab5d9ae732b8d590a8de659411584db9f7722230`, sanitized control revision 9, `open_source` config revision 5, config blob `118f440957ba4654e804af902aa09a9224acca43`. The tuple was rechecked with SHA-only Git-ref transport before the first role-local/public semantic read and then frozen. Only this worker's own clean state plus public sources were used. No O/O-derived state, other-worker state/config/output, downstream semantics, aggregate ledger, other-role receipts, or legacy/pre-independence research was read.

## Scope

Continue the exact prior frontier against fresh public `lbx154/Argus@962cb06554daaede17b786c495e13ee3b6530e6e` (verified current `main` this run): enumerate direct `PIPELINE_STATE` writers, classify their lock/authority boundary, identify a second concrete external writer, and search for a public implementation that combines one-shot authorization with exact-state freshness checks.

No unauthorized mutation, secret read, exploit, or live race was executed. Findings are source/call-path analysis only.

## Finding A — classification diagnostics are direct writers but are serialized in the Manager path

`argus_skill/manager/classification_contract.py` directly performs read/modify/write on `.argus/PIPELINE_STATE.json` through `write_pipeline_state()` for both failure-streak increment and reset.

However, the current production caller in `manager/_vertical_ops.py::decide_vertical()` wraps both `record_contract_failure()` and `reset_contract_failures()` in `with self.pipeline_lock():`. Therefore this writer does not add a second lock-bypassing production path under the checked in-repository Manager flow.

Scope limit: this does not prove that a third-party Python consumer cannot import these helpers directly. It only classifies the current in-repository production caller.

## Finding B — verification policy is a latent direct writer, but no current in-repository production caller was found

`core/verification_policy.py::set_policy()` reads the full pipeline payload, mutates `verification_profile` / `exploration_posture`, and calls `write_pipeline_state()` without an internal pipeline lock or expected prior revision/digest.

Repository code search at the pinned commit found `set_policy(` only in its defining module and tests. Therefore it is a callable public/library mutation surface but not a second concrete current product writer based on in-repository reachability.

This distinction matters: the architectural invariant should cover exported mutators, but current operational risk should not be overstated as if the product already invokes this path concurrently.

## Finding C — a second concrete supported external writer exists: math objective CLI

`verticals/math/objective_mode.py::set_objective()` is a direct full-object read/modify/write of `.argus/PIPELINE_STATE.json` and is exposed through the supported module CLI:

`python -m argus_skill.verticals.math.objective_mode set ...`

The source itself explicitly documents the concurrency property: the temp-file + `os.replace()` write prevents torn reads, but read/modify/write is **not atomic against concurrent `persist_vertical()`** and an interleaving can lose one side's edit. The comment says this race is intentionally left alone because the objective command is assumed to run once at setup while `persist_vertical` runs on Manager routing and they are not expected to overlap in normal operation.

This is materially stronger than a hypothetical external embedding. Together with the previously established supported `argus learn --base <workdir>` path, current Argus has at least **two explicit operator/admin entrypoints** that can write the same whole pipeline object outside the Manager pipeline lock if intentionally pointed at a live workdir:

1. `argus learn` -> `persist_vertical(...)`;
2. math objective CLI -> `set_objective(...)` -> `write_pipeline_state(...)`.

The source does not claim these are safe under concurrent same-workdir use; for the math objective path it explicitly acknowledges the lost-update race and relies on lifecycle separation instead.

## Candidate refinement — `clean-os-g1-005`

The candidate is now narrower and better supported:

**Every semantic writer of shared durable pipeline state should either (a) be proven lifecycle-exclusive, or (b) pass through the same mutation primitive requiring both scoped authority and exact expected prior state. Atomic replace alone is insufficient.**

The matched falsification target should no longer be only `learn` vs Manager. Add the objective CLI as an independent external-writer case:

- Manager changes route/stage after the CLI's stale read;
- stale objective write must be rejected with byte-identical state;
- fresh objective write on inactive/setup state must succeed;
- legitimate objective semantics must be preserved;
- no weakening of existing completion/evidence gates.

This directly tests whether a shared CAS-aware mutation boundary prevents a currently documented lost-update class without breaking normal bootstrap use.

## Finding D — a strong near-precedent combines one-shot preview authority with revision checks, but not in one atomic durable transaction

Fresh public source `Wh1isper/mcp-email-server@8b3c0026ffa7c3f6df6b415d317f62795a6c0ecd` (verified current `main`) contains a useful concrete pattern in `LegacyImportService`:

- preview creates a random `secrets.token_urlsafe(32)` token;
- stored previews have a 600-second TTL and bounded registry;
- `apply()` removes the token with `_previews.pop(preview_token, None)` under a lock, so the preview token is one-shot at the service layer;
- apply rejects a missing/expired/reused token;
- apply requires caller `expected_revision == plan.target_revision`;
- it rechecks selected target, source fingerprint/snapshot, catalog revision, per-account revisions, and policy revision before/through mutations;
- final automatic cutover calls `guarded_import_cutover(...)`, whose local backend holds the bootstrap file lock and then the catalog import writer guard while rechecking expected bootstrap/catalog/account/source state before changing selection.

This is substantially closer to the desired primitive than the earlier Step Functions-token + Kubernetes-resourceVersion composition because one public application deliberately combines a one-time authorization handle and stale-revision rejection in the same workflow.

Important scope limit: token consumption (`pop`) and the whole multi-store import/cutover are **not one atomic durable transaction**. The token is consumed before later validation/mutations, and the workflow spans multiple guarded steps. Therefore it is a strong near-precedent, not proof of an implementation that atomically co-consumes a capability and CASes the exact target object in one storage transaction.

The design implication remains: keep one-shot authority and expected-state freshness as separate checks, but implement their acceptance at the same low-level pipeline mutation boundary if possible. If host restart or storage failure can occur between capability consumption and state mutation, recovery semantics must be explicit.

## Updated regression matrix

1. current Manager classification diagnostics remain serialized under pipeline lock;
2. exported `set_policy()` without a current production caller is classified as latent/public API, not active race evidence;
3. stale `argus learn` whole-object write after Manager mutation is rejected, state unchanged;
4. stale math-objective CLI write after Manager mutation is rejected, state unchanged;
5. fresh bootstrap `learn` and fresh objective setup succeed;
6. stage mutator without valid host capability fails with byte-identical state;
7. exact transition-kind/from/target/revision capability succeeds once;
8. replayed capability fails;
9. capability minted before route/stage change becomes stale and fails;
10. crash/restart between capability claim and mutation has explicit recovery semantics and cannot replay authority;
11. deterministic completion/evidence validators still execute after authority/freshness admission;
12. read-side revalidation continues to reject old/corrupt authority records.

## Tested scope / uncertainty

- Argus exact public commit audited: `962cb06554daaede17b786c495e13ee3b6530e6e`, verified current `main` in this run.
- mcp-email-server exact public commit audited: `8b3c0026ffa7c3f6df6b415d317f62795a6c0ecd`, verified current `main` in this run.
- No concurrent Argus write was executed; lost-update claims are source-level concurrency implications and, for math objective mode, explicitly acknowledged by source comments.
- `set_policy()` has no current in-repository production caller found; third-party import reachability is not equivalent to active product use.
- mcp-email-server is an independent application precedent, not an Argus or agent-system benchmark and not evidence of AGI performance improvement.
- The near-precedent does not atomically co-commit token consumption and target mutation in one durable transaction.

## Nonempty frontier

1. Search Argus tests/history/issues for explicit live-daemon contracts around both `argus learn` and the math objective CLI; determine whether same-workdir refusal is intended/backward-compatible or whether live admin mutation must remain supported.
2. Finish direct writer enumeration for `write_pipeline_state`: classify stage-machine writers, any vertical-specific objective/policy writers, and whether their production callers are lock-bound, lifecycle-exclusive, or externally callable.
3. Trace `adopt_operator_objective` from the Manager route path to verify exactly which outer lock protects its normal runtime write; keep the standalone CLI classified separately.
4. Search for a public storage-backed implementation where a one-shot authorization row/token is consumed and an exact target version is CASed in the **same DB transaction**. If none is found, retain mcp-email-server as near-precedent and the proposed Argus primitive as a composition of separately demonstrated invariants.
5. Inspect custom `--life-dir` state-root handling further only if it changes whether raw authority material can be hidden from model-readable files; do not conflate filesystem secrecy with mutation authority.
6. Keep the unresolved Memento control-operator provenance branch dormant unless a new paper-era artifact appears.

## Exact continuation

Start by tracing the normal `adopt_operator_objective` call from Manager routing through the outer daemon/pipeline-lock boundary and separate that safe normal path from the standalone objective CLI. Then enumerate remaining direct `write_pipeline_state` production callers, especially stage-machine/vertical-specific writers, and classify each by lock/lifecycle/external reachability. Finally search public source for a transactional pattern that atomically marks a one-shot authorization consumed and CAS-updates the target object's expected revision in one storage transaction; if only multi-step near-precedents exist, preserve that limitation explicitly.
