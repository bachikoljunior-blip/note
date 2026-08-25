# Open Source clean_g1 — RUN_20260826_0657_EXTERNAL_WRITER_ISOLATION

Frozen semantic control tuple for this physical invocation: note main `bef75c9992d531894760890e0a092f1e7eb0da0e`, sanitized control revision 9, `open_source` config revision 5, config blob `118f440957ba4654e804af902aa09a9224acca43`. The tuple was rechecked with the SHA-only Git-ref transport before the first role-local/public semantic read and then frozen. Only this worker's own clean state, absent own feedback, sanitized root/role control, and public sources were used. No O/O-derived state, other-worker state/config/output, downstream semantics, aggregate ledger, other-role receipts, or legacy/pre-independence research was read.

## Scope

Continue the exact prior frontier against fresh public source `lbx154/Argus@962cb06554daaede17b786c495e13ee3b6530e6e`: (1) finish non-daemon `_SkillLoopRunner.execute()` reachability, (2) inspect direct CLI `persist_vertical` behavior, (3) finish the Manager-state readability matrix for isolated workdirs, and (4) look for independent public precedents for state-bound callback authority and stale-state rejection.

No unauthorized mutation, secret read, exploit, or live race was executed. Findings below are source/call-path analysis and documented external-system behavior only.

## Finding A — the current non-daemon teammate embedding is deliberately non-authoritative

Repository-wide code search at the pinned Argus commit found the only clear production source outside the runtime/supervisor internals that directly constructs `_SkillLoopRunner` and calls `runner.execute()` in `argus_skill/team/teammate_entry.py`.

That entrypoint is explicitly documented as having **no cockpit, no daemon lock, and no planner**. This initially looks like the exact non-daemon bypass sought by the prior frontier. However, the call passes `holds_stage_authority=False`.

The runtime guard in `apps/_runtime_helpers.py::_should_run_stage_transition()` checks `holds_stage_authority` first and unconditionally returns `False` when it is absent. `apps/_runtime_execute.py` also marks the stage transition as skipped when `not holds_stage_authority`.

Therefore this concrete current non-daemon embedding does **not** reach the Manager stage writer despite executing from the shared project root without the outer daemon lock. This is strong evidence that the known fan-out embedding already closes the obvious direct-runner stage-write path.

Scope limit: repository code search cannot prove the absence of dynamic third-party embeddings, aliases, or external Python consumers. It supports only that no additional in-repository production `_SkillLoopRunner` instantiation outside the known runtime/teammate paths was found at this commit.

## Finding B — a different current supported external writer exists: `argus learn`

The direct CLI branch is more important than the teammate path.

Public parser/source behavior:

- `argus learn` is a supported subcommand with `--base` defaulting to the current working directory.
- `_cmd_learn()` ingests material, writes its manifest, then directly calls `persist_vertical(base, "learning")`.
- The function then prints instructions to start a daemon in that workdir, showing that the intended use is bootstrap-before-daemon.
- `_cmd_learn()` does **not** resolve/acquire `Manager.pipeline_lock()`, inspect a live daemon for the same base, or require a state revision/digest precondition before calling `persist_vertical`.

`skills/vertical_select.py::persist_vertical()` performs a full-object read/modify/write:

1. reads the current pipeline payload;
2. unconditionally assigns `payload["vertical"] = vert`;
3. intentionally preserves any existing `current_stage` (it only seeds a stage if none exists);
4. calls `write_pipeline_state(project_root, payload)`.

`core/pipeline_state.py::write_pipeline_state()` writes a temp file and `os.replace()`s it into place. This prevents torn JSON, but it is **not** compare-and-swap: there is no expected old digest/revision and no inter-process lock around the read/modify/write transaction.

### Concrete concurrency implication

If an operator runs `argus learn --base <currently-active-workdir>` while a daemon/Manager is concurrently mutating the same `.argus/PIPELINE_STATE.json`, both writers can read the same old payload and later atomically replace the whole object. Whichever replacement lands last can discard fields written by the other from its newer snapshot. The CLI can also change `vertical` while intentionally retaining the pre-existing stage.

This is a **current supported external-writer path**, unlike the previously hypothetical arbitrary embedding. It is narrow: it requires an explicit `learn` invocation targeting the same live workdir, and the command is clearly intended as pre-daemon bootstrap. No evidence was found that this race is common or has caused a reported incident. GitHub issue search for `persist_vertical` in the public repository returned no open/closed issue hits at this run.

Nevertheless it materially strengthens the architecture case: normal daemon serialization alone cannot make the durable primitive safe when another supported process can write the same object outside that lock.

## Finding C — exact-revision rejection should cover route writers, not only stage writers

`clean-os-g1-005` should now be scoped to **all semantic pipeline-state mutations** rather than only stage advance/rollback/complete.

Minimum justified contract:

1. keep the existing Manager pipeline lock for normal in-process orchestration;
2. retain deterministic evidence/completion validators;
3. make each semantic mutation identify its transition kind and exact expected prior state (revision or digest);
4. reject stale expected state before replacing the durable object;
5. require a host-authorized capability for mutation paths that are intended to be Manager/supervisor-only;
6. for bootstrap/admin CLI paths such as `learn`, either refuse a same-workdir live session or route through a lock/CAS-aware administrative mutation path;
7. preserve byte-for-byte state on rejected stale/unauthorized calls;
8. keep read-side authority/completion revalidation for old or externally corrupted durable state.

Atomic replacement and CAS solve different problems: `os.replace()` avoids torn files; expected-state CAS avoids lost updates from stale whole-object writers.

## Finding D — isolated-workdir secrecy is OS/layout dependent, not a universal property

The previous run left `isolate_workdir=True` unresolved. Fresh source allows a sharper matrix.

### Default safe-mode OFF

`_apply_sandbox_policy()` forces `sandbox_mode=None`, `isolate_workdir=False`, and the dangerous bypass. No filesystem read isolation is established. Manager-state bearer material must be treated as readable by the model process.

### Codex safe-mode `workspace-write`

The command builder explicitly describes this mode as **write confinement** to `-C` plus an allowlist. It protects gate/package state from writes but does not establish a general read deny. Therefore Manager-state plaintext cannot be treated as secret merely because `workspace-write` is enabled.

### POSIX `isolate_workdir` with bubblewrap

`core/sandbox.py::isolated_workdir_command()` starts with a read-only bind of `/`, then overlays `/root`, `/home`, and several credential/service roots with tmpfs. It selectively re-exposes only needed executables/config/cache/git/workdir material. Under the normal default global root (`~/.argus-skill`), this hides Manager state because the enclosing `/home` or `/root` is replaced.

Important limitation: `/` is otherwise still read-only bound. A custom `--life-dir` located outside the hidden roots (for example under `/srv/...`) may remain readable unless separately hidden. Thus even the Linux bubblewrap path does not prove secrecy for every supported state-root layout.

### macOS `sandbox-exec` isolated-workdir path

The macOS profile starts from `(allow default)`, denies writes outside the approved workdir/tmp/dev set, and adds explicit read denies only for selected sensitive directories (`~/.ssh`, `~/.aws`, `~/.gnupg`, `~/.kube`, `~/.docker`, `~/.config/gh`). It also remaps `HOME` to a private directory.

`~/.argus-skill` is not in the explicit file-read deny list. Remapping `HOME` changes normal lookup but does not by itself deny an absolute path to the original home. Therefore the current macOS isolation source does **not** justify treating the original Manager state as unreadable.

### Consequence for capability storage

A raw bearer nonce should not rely on ordinary Manager-state filesystem secrecy across supported layouts. Stronger options are:

- keep the raw one-shot secret only in a host process / privileged helper and persist only a hash + consumed/expired metadata;
- invalidate outstanding capabilities across host restart and re-mint only after revalidating current state/evidence; or
- use a cryptographically authenticated scoped token whose signing key is outside model-readable state, still with server-side one-shot consumption and exact-state rejection.

This is a refinement of the existing `RepairCapability` precedent, not evidence that the present validator-repair flow is exploitable. The repair host currently claims the capability before invoking the Engineer, so later filesystem readability of an already-consumed nonce does not automatically recreate authority.

## Finding E — independent production precedents support the two halves separately

No single public agent runtime with both an opaque one-shot mutation capability and exact object-revision CAS at the same primitive was established in this run. Two mature systems independently demonstrate the two contracts:

1. **AWS Step Functions callback task tokens.** Step Functions generates a task token for the current task. `SendTaskSuccess` requires that token; invalid tokens are rejected, and a token whose task expired or was already closed returns `TaskTimedOut`. The callback documentation says a timeout causes a new random token to be generated. This is a strong state-bound/one-current-task callback-capability precedent.
2. **Kubernetes API `resourceVersion`.** An update supplies the object's previously read `resourceVersion`; when it is stale the API server rejects the update with HTTP 409 Conflict. Kubernetes authorization is evaluated separately before mutation. This is a mature precedent for separating *who may request the operation* from *whether the state is still exactly fresh enough to update*.

These do not by themselves prove the proposed Argus design improves AGI performance or benchmark results. They support the systems invariant that authority and freshness should be independent gates.

Public references checked this run:

- https://docs.aws.amazon.com/step-functions/latest/apireference/API_SendTaskSuccess.html
- https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html
- https://kubernetes.io/docs/reference/using-api/api-concepts/
- https://kubernetes.io/docs/reference/access-authn-authz/authorization/

## Candidate refinement — `clean-os-g1-005`

Current formulation:

**Primitive-bound semantic authority + exact-state rejection for every durable pipeline writer.**

The strongest current evidence is no longer a conjectured daemon race. It is the coexistence of:

- well-serialized normal daemon paths;
- a safe non-daemon teammate runner explicitly stripped of stage authority;
- low-level mutators without caller capability/revision CAS;
- and a supported explicit CLI route writer (`argus learn`) that performs whole-object pipeline read/modify/replace outside the Manager lock.

A targeted matched test should therefore include a deliberately interleaved `learn`/Manager write and require stale write rejection with no lost fields, plus stage capability tests. This is narrower and more falsifiable than claiming general concurrent corruption.

Suggested regression matrix:

1. teammate direct runner with `holds_stage_authority=False` cannot mutate stage;
2. stale `learn` route write after a Manager state change is rejected, state unchanged;
3. fresh bootstrap `learn` on inactive/new state succeeds;
4. stage mutator without valid host capability fails with byte-identical state;
5. exact from/target/revision capability succeeds once;
6. replayed capability fails;
7. capability authorized before route/stage change becomes stale and fails;
8. legitimate supervisor dynamic rollback receives only rollback-scoped authority and succeeds;
9. current deterministic completion validators still run after authorization/freshness checks;
10. raw bearer secret is absent from model-readable state under default, custom-life-dir, Linux isolated, and macOS isolated layouts.

## Tested scope / uncertainty

- Exact Argus public commit audited: `962cb06554daaede17b786c495e13ee3b6530e6e`.
- Source/call-path analysis only; no race or unauthorized mutation was executed.
- The `argus learn` concurrency risk requires explicit same-workdir invocation while a live writer exists. Intended pre-daemon usage is safe from that specific interleaving.
- Atomic `os.replace` is present and prevents partial-file writes; the issue is stale whole-object lost update / authority, not torn JSON.
- The POSIX bubblewrap secrecy conclusion applies to default home-root state; custom `--life-dir` outside hidden roots remains a separate layout risk.
- The macOS conclusion is based on the checked-in sandbox profile semantics; no live macOS filesystem probe was run.
- AWS Step Functions and Kubernetes are independent systems precedents, not matched Argus experiments.

## Nonempty frontier

1. Search tests/history/PRs for an intended live-session contract around `argus learn`; determine whether refusing an active same-workdir daemon is backward-compatible or whether route mutation must be supported live.
2. Trace other direct non-Manager callers of `persist_vertical`, `write_pipeline_state`, `reset_stage_for_replacement_intent`, `rollback_stage`, and `complete_final_stage`; classify explicit operator/admin paths separately from model/daemon paths.
3. Inspect custom `--life-dir` propagation into Linux/macOS isolation to enumerate exactly which state-root layouts expose Manager authorization files.
4. Find or build from public precedents a minimal implementation pattern that combines one-shot scoped authority with exact prior-state CAS in one mutation transaction; keep Step Functions token semantics and Kubernetes resourceVersion semantics separate until such a combined implementation is actually verified.
5. Monitor fresh Argus upstream for a route/stage capability or state-revision migration; if upstream fixes the external-writer path, compare rather than duplicate it.
6. Keep the unresolved Memento Table-4 control-operator provenance branch dormant unless a new paper-era artifact appears.

## Exact continuation

Start by enumerating every production caller of `write_pipeline_state` and `persist_vertical` at the pinned/freshest Argus main, classify whether each runs under the Manager pipeline lock, a live-daemon refusal, or neither, and identify any second concrete external writer. Then inspect `--life-dir`/state-root propagation through `isolated_workdir_command` for custom POSIX and macOS layouts. Finally search for a public implementation that atomically consumes a scoped one-shot authorization *and* rejects a stale expected state revision at the same mutation boundary; if none is found, keep the candidate as a composition of separately demonstrated invariants rather than claiming an existing combined precedent.
