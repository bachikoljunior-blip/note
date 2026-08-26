# Open Source Systems Scan — control-store fencing, capability secrecy, and durable file commit

Role: `open_source` clean exploration.
Frozen semantic control tuple: note main `b8c5a5e3b93fa70aa698d16465a8724f4785e6b3`, control revision 9, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source heads inspected: `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd` (verified current main at semantic freeze) and `untitaker/python-atomicwrites@4183999d9b7e81af85dee070d5311299bdf5164c` (archived durability precedent; not a recommended dependency).

## 1. Argus already contains most of the stale-state fencing pattern in `CampaignControlStore`

`argus_skill/manager/control_state.py` is a materially stronger file-state primitive than `.argus/PIPELINE_STATE.json`:

- cross-process Manager control mutations are serialized with `portalocker` on `.manager-control.lock`;
- every control revision is written as an immutable snapshot;
- `HEAD.json` is written last and names the sole current snapshot/revision;
- snapshot files and `HEAD.json` are temp-written, flushed, `os.fsync()`ed, then `os.replace()`d;
- authorizations are campaign/objective/epoch/revision bound;
- authorization validation rejects a non-current Manager `state_revision`, missing authorization id in the current snapshot, action outside scope, expiry, campaign mismatch, frozen-evidence drift, frozen-tree drift, and nonce mismatch;
- validator-repair capability claim is under the same lock, requires the current authorization, and records an `active_capability` in a new immutable revision;
- existing tests cover stale-wait cleanup, stale authorization after a newer Manager revision, `expected_state_revision`/wait checks at authorization issuance, one-shot consumption, frozen evidence drift, symlink/write-scope races, and capability one-shot settlement/recovery.

This means the new protected-state primitive proposed in the previous run should not reinvent revision fencing from scratch. The repository already has a tested local pattern for lock + immutable revision + HEAD-last + exact-current authorization.

### Important limitation

`CampaignControlStore` is not directly a drop-in CAS for `PIPELINE_STATE.json`:

- its state lives in a separate `campaign-control/` revision tree;
- stage/route state still has a separate `.argus/PIPELINE_STATE.json` write path;
- its ordinary `commit_revision()` serializes and increments current state but does not itself expose an external expected-prior-revision parameter for every arbitrary update (some higher-level operations do, e.g. wait/authorization checks);
- `_atomic_write_json()` fsyncs the file but does not fsync the parent directory after rename.

So simply adding a second CampaignControlStore write beside a pipeline-state write would create a two-authority/two-commit problem. Either protected pipeline keys must become authoritative inside one store, or the existing pipeline file needs one equivalent common mutation primitive.

## 2. Repair capability is interface-hidden, but the bearer is durable plaintext

The validator-repair flow deliberately gives the model only a public subset. In `_mission_execution_runtime.py`, the mission prelude exposes `authorization_id`, `capability_id`, `validator_id`, and allowed write paths, while the runtime itself fetches the authorization and passes its stored nonce to `claim_repair_capability()` and later `begin_acceptance_retry()`.

However the durable state still contains the bearer material:

- `Authorization` contains `nonce`, generated with `secrets.token_urlsafe(24)`;
- `operator-authorizations.jsonl` stores issued/claimed/closed/consumed event objects that retain the nonce;
- `RepairCapability` also contains `nonce`;
- `claim_repair_capability()` commits `active_capability=asdict(capability)` into the current control snapshot, so the current immutable revision also contains the raw nonce;
- `public_authorization()` strips the nonce only for model-facing context; it does not make the on-disk control state secret.

Therefore the capability is **prompt-hidden**, not proven model-secret across all supported runtime layouts.

## 3. Readability differs materially by sandbox/backend

`argus_skill/core/sandbox.py` establishes a write-containment invariant, not a universal read-secrecy invariant.

### Default / legacy mode

`ARGUS_SKILL_ENGINEER_SANDBOX` is OFF by default. The documented fallback is `--dangerously-bypass-approvals-and-sandbox`, so there is no filesystem secrecy guarantee for Manager state in this configuration.

### Codex `workspace-write`

The module describes `workspace-write` as confining **writes** to the project workdir plus an allowlist and protecting `~/.argus-skill`, the package, venv, and `~/.codex` from writes. It does not establish an outside-workdir read denial. Thus raw bearer secrecy should not be assumed from this mode alone.

### POSIX isolated-workdir with bubblewrap

The stronger isolation path read-only binds `/` and then overlays `/home` and `/root` (plus several credential locations) with tmpfs. This hides a default home-rooted `~/.argus-skill` from the isolated process. But a custom life/control root outside the hidden roots (for example under `/srv`) remains reachable through the read-only `/` bind unless separately hidden. So even this path provides location-dependent secrecy rather than an invariant tied to the capability itself.

### macOS `sandbox-exec`

The generated Seatbelt profile starts with `allow default`, denies writes except to the workdir/private temp/dev, and adds read denials for selected credential roots (`~/.ssh`, `~/.aws`, `~/.gnupg`, `~/.kube`, `~/.docker`, `~/.config/gh`). The ordinary `~/.argus-skill` control root is not in that explicit read-deny set. Replacing `HOME` with a private directory changes discovery, but does not itself prove the original absolute path unreadable.

### Scope

No live unauthorized capability use was executed. This is a source-level reachability/secrecy audit. The correct claim is not that every model can currently steal the nonce, but that **bearer secrecy is not an invariant guaranteed across the supported/default configurations**.

## 4. Candidate consequence: do not make correctness depend on a plaintext durable bearer

For `clean-os-g1-005`, strengthen the authority design as follows:

1. Keep semantic authority host-mediated. The model may propose a transition and receive a non-secret handle/scope summary, but should not need the bearer.
2. Bind every privileged transition to exact current protected revision/digest, transition kind, from/target state, route/evidence fingerprint, and one-shot id.
3. Validate/consume under the same protected-state lock immediately before mutation; stale/replayed/mismatched attempts make zero semantic changes.
4. Do **not** persist a reusable plaintext bearer in model-readable durable state. Prefer a stored verifier/hash plus a host-held secret, or invalidate the in-memory secret on restart and re-mint a fresh capability only after revalidating current HEAD/evidence under the still-valid operator authorization.
5. Preserve crash recovery through durable authorization + state, not by making the same bearer replayable after restart.
6. Do not add another independent lock/store around `PIPELINE_STATE` without an explicit lock order. The existing Manager pipeline lock and CampaignControlStore lock are separate.

This separates two properties that were previously conflated: restart-recoverable authorization state and secret bearer material.

## 5. A lower-complexity durability precedent exists, but not a full CAS precedent

The archived `python-atomicwrites` implementation is useful as a file-durability reference only:

- temp file is created in the destination directory;
- file contents are flushed and fsynced before commit;
- POSIX replacement uses rename and then fsyncs the parent directory so the filename update is persisted;
- macOS uses `F_FULLFSYNC` when available;
- Windows uses `MoveFileExW` with `MOVEFILE_WRITE_THROUGH` (and `MOVEFILE_REPLACE_EXISTING` for replacement).

Its own README warns that Windows atomic guarantees are weaker/less explicit, and the repository is archived. It does not provide semantic CAS. Do not adopt it as a dependency or treat it as proof of Windows crash guarantees.

The simplest candidate for Argus is therefore **not** a database migration by default: reuse the already-tested `portalocker` + revision-fence pattern, add exact expected prior revision/digest to the common protected pipeline mutation path, and use the file+directory durability sequence where the platform supports it. Database migration should be justified only if multi-object transactional coupling remains necessary after field ownership is separated.

## Refined regression matrix

Add tests that distinguish authorization, secrecy, concurrency, and durability:

- stale expected pipeline revision/digest => byte-identical protected state;
- stale/replayed/wrong-scope transition capability => byte-identical protected state;
- model-facing prelude contains no bearer and supported sandbox tests attempt direct read of the actual control root;
- default/no-sandbox mode is explicitly marked non-secret rather than silently relied upon;
- Linux bubblewrap default-home life root is unreadable, while a custom non-hidden life root is either explicitly denied or the test fails closed;
- macOS Seatbelt explicitly denies the actual control root if bearer secrecy is required;
- restart invalidates any host-memory bearer and re-mints only after exact-current authorization/evidence revalidation;
- temp file fsync failure, rename failure, and parent-directory fsync failure are injected separately;
- external math/learning setup writer using an old revision cannot overwrite a newer protected state;
- existing normal daemon outer-lock paths do not deadlock when the common mutation primitive is introduced.

## Scope limits

No current regular-daemon stage race was established. No unauthorized repair capability was exercised. `python-atomicwrites` is a durability implementation precedent, not evidence that a complete Argus-style CAS/capability design already exists. The strongest observed positive control is Argus's own `CampaignControlStore` revision/authorization machinery; the strongest newly identified limitation is that its restart-recoverable repair bearer is persisted in plaintext and is not universally hidden by all supported/default sandbox layouts.

## Exact continuation

1. Inspect all `CampaignControlStore` callers to determine whether any supported runtime truly requires reuse of the *same* repair nonce after process restart, or whether restart can safely re-mint from a still-current durable authorization; this decides whether raw bearer persistence can be removed without losing recovery.
2. Inspect `current_repair_capability()`/settlement recovery and crash tests for whether capability identity rather than bearer continuity is sufficient.
3. Build a concrete `mutate_pipeline_state(expected_revision, intent, lock_context)` migration sketch that reuses existing Manager locking without nested-lock deadlock and classify every current writer as protected mutation, descriptor/evidence write, or setup-only writer.
4. Search for a maintained cross-platform file-commit implementation with explicit directory durability semantics; if none is stronger than the archived atomicwrites precedent, keep the durability layer minimal and platform-scoped rather than claiming universal power-loss guarantees.
5. Keep the frontier open on whether protected pipeline state should become a projection of `CampaignControlStore` or remain a single JSON authority with the CampaignControlStore pattern factored into it.