# Open Source Phase-1 Crash/Retry Transaction Protocol

## Frozen semantic control tuple

- role: `open_source`
- frozen note main SHA: `97590a1f3e99efbb80abc0bf6fcb405bba17a99f`
- root control revision: `16`
- role config revision: `6`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v2-active-pool`
- assignment: `phase1-clean-open-source-chat-capability-patterns`
- enabled_desired: `true`
- clean boundary: own role-local state + public sources + own sanitized feedback only

The first role-local/public semantic read froze the tuple above. A later SHA-only head check observed `6c22881637d6b4a75716583fb72cb0eaed62ac70`, so semantic work stopped at that barrier. The newer control/state semantics were not read or adopted. The writes below are only role-local persistence of evidence already derived under the frozen tuple.

The preserved Argus/event-log continuation remains restoration metadata only and was not resumed while the Phase-1 overlay was active.

## Main revision to the previous matrix

The previous checkpoint correctly said that a standalone Git ref update with `force=false` is not an API-level expected-old-SHA compare-and-swap: GitHub's REST update-ref call accepts the **new** SHA plus `force`, not an explicit `expected_old_sha`.

However, the lower-level Git Data surface supports a stronger **composite** direct transaction:

1. Read branch head `H0` exactly.
2. Build a new tree `T1` from `H0`'s tree.
3. Create commit `C` whose sole parent is exactly `H0`.
4. Advance the branch to `C` with non-force `update_ref`.
5. Read the branch ref back and require exact `C` (or reconcile an ambiguous response by ancestry/readback).

Under the explicit assumption that competing writers only advance history normally (no force-rewind/history rewrite between the read and update), a concurrent sibling commit `H1` from `H0` makes `C` non-descendant of current `H1`; the non-force ref update therefore fails instead of overwriting `H1`. In that bounded model, **parent-bound commit + non-force ref update acts as an effective expected-head CAS** even though `update_ref` alone is not strict CAS.

This is an inference from the Git commit DAG plus documented fast-forward semantics, not a separate GitHub atomic-CAS guarantee. It must not be generalized across force-push/history-rewrite races.

A useful stronger benchmark exists in GitHub GraphQL: `createCommitOnBranch` accepts `expectedHeadOid` and atomically appends file changes when the branch head matches. The current connected Chat surface exposes no generic GraphQL mutation and no `createCommitOnBranch` action, so this stronger primitive is **publicly available at GitHub but unavailable through the inspected connector surface**.

## Crash/retry protocol matrix

| Operation | Precondition | Effect | Exact readback | Ambiguous-response recovery / fail-closed rule |
|---|---|---|---|---|
| Exact freshness read | Known repository + branch/ref | GET exact ref object | Persist returned object SHA `H` | Read failure => `UNKNOWN`; do not mutate from a guessed/stale head. |
| Acquire reusable repository lease | Deterministic claim-file path absent, or stale reclaim completed | `create_file` with unique `claim_id`, holder, task/scope, acquire/renew time, expiry/lease duration, epoch, and optional base head | If a commit SHA is returned, `fetch_file(ref=<commit>)` must match intended bytes | If transport result is ambiguous: fetch claim path. Matching `claim_id` + body => recovered success; absent => retry create; foreign claim => collision, stop. |
| Renew lease | Claim still owned by our `claim_id`; lease not expired; current claim blob SHA `S` known | `update_file(..., sha=S)` with incremented epoch / renewed expiry | Exact bytes at returned commit SHA | Fetch current claim. Intended/newer own epoch => recovered success. Unchanged old state => retry with still-current SHA. Foreign/absent => lease lost; stop side effects. |
| Reclaim stale lease | Observed expiry is beyond configured grace **and** all participants obey no-effect-after-expiry; current blob SHA `S` known | `delete_file(..., sha=S)`, then attempt fresh create-only claim | Path absence proves delete; subsequent fresh claim exact readback proves ownership | If delete ambiguous: absent => success; unchanged same stale blob => retry; changed blob/body => abort reclaim. Concurrent reclaimers race on create-only claim; only one can own the new artifact. |
| Release lease | All intended effects are committed and exact post-effect readback succeeded; current claim is still ours | `delete_file(..., sha=current_blob_sha)` | Claim path absent | Ambiguous: absent => released; same own blob => retry delete; changed/foreign => never delete. |
| Immutable checkpoint/evidence | Unique deterministic artifact path | `create_file` | `fetch_file(ref=<returned commit SHA>)` exact bytes | Ambiguous: fetch deterministic path; exact bytes => recovered success; absent => retry; differing content => conflict, stop. |
| Mutable pointer (`LATEST`) | Exact current pointer blob SHA `S` read | `update_file(..., sha=S)` | Exact pointer bytes at returned commit SHA | If current pointer equals intended version/content => recovered success. If still old state => retry with its current SHA. Different/newer state => reconcile; never blind overwrite. |
| Multi-file branch transaction | Exact branch head `H0`; tree source pinned to `H0` | Create tree `T1`; create commit `C(parent=H0)`; non-force ref update to `C` | Exact ref should be `C` | If response ambiguous: ref=`C` => success; ref=`H0` => retry update; current descendant of `C` => our commit was incorporated then branch advanced, so either accept incorporation or fail if exact-head ownership is required; divergent/non-descendant => rebuild from new head. Never force. |
| Create PR | Deterministic head branch + base; no exactly matching open PR after search/list | Create PR | `get_pr_info` must verify exact head/base and current head SHA `H` | Timeout/422/uncertainty => search/list same head+base first; candidate counts as recovered success only after exact PR info verifies head/base/head SHA. No match => classified retry. Conflicting/moved match => fail closed. |
| Bind review to code | PR head read as exact `H` | Submit review with `commit_id=H` | Re-read PR head after review | If head moved to `H2`, review evidence is stale for exclusive handoff; restart evidence/review on `H2`. |
| Bind CI/status evidence | PR head frozen as `H` | Read `get_commit_combined_status(H)` and any exposed workflow-run evidence | Every accepted evidence record must explicitly refer to `H` | **Coverage warning:** GitHub distinguishes commit statuses from Checks; GitHub Actions generates Checks, not commit statuses. The connected surface has combined-status readback but no general Checks API action, and its workflow-run wrapper is PR-triggered/first-page scoped. Therefore do not claim complete CI coverage from these tools alone. Missing required evidence => unknown/fail closed, or rely on server-side branch protection as final authoritative gate. |
| Exclusive synchronous merge | Exact head `H` whose required evidence/review is current | `merge_pull_request(expected_head_sha=H)` | Re-read PR/base state and merge result | Head mismatch => GitHub rejects. If merge response ambiguous: re-read PR; merged => verify intended head was incorporated if available; not merged + still `H` => safe retry; head changed => stop/re-review. |
| Fresh workflow execution | Workflow exists and `workflow_dispatch` is configured | Public REST can create a dispatch event | Current GitHub.com API returns workflow-run metadata/run ID | **Not direct Chat capability on inspected connector:** discovery still exposes only workflow readback and rerun of existing runs/jobs, no fresh dispatch action. Do not substitute writing workflow YAML or calling rerun for fresh dispatch. |
| Auto-merge policy | PR exists and repository supports auto-merge | Connected `enable_auto_merge` | Wrapper returns only success | Treat as background policy, not the precise exclusive handoff primitive: wrapper has no expected-head parameter. Prefer synchronous merge with `expected_head_sha` when exact head binding is required. |

## Why file leases are preferable to ref leases on this connected surface

Public GitHub REST supports create/update/delete refs, so deterministic refs can be excellent exclusive claims in a fully exposed API. In the current connected Chat tool surface, ref create/update is exposed but **delete-ref is not**. That makes a ref claim difficult to renew/reclaim/release without leaving permanent one-shot names.

The Contents surface exposes create/update/delete of a file and requires the current file blob SHA for update/delete. Therefore a deterministic lease file is the better reusable Chat-capable claim primitive here.

The lease record can borrow Kubernetes Lease structure as a public, battle-tested model:

- `holder_identity`
- `acquire_time`
- `renew_time`
- `lease_duration_seconds` or explicit `expires_at`
- `lease_transitions` / local epoch
- task/scope identifier and optional frozen base SHA

Kubernetes Lease updates use optimistic concurrency (`resourceVersion`) so only one competing update wins. For a repository-file lease, the file blob SHA plays the analogous per-object CAS role.

### Lease safety assumptions

A timestamped lease is not automatically safe merely because it has an expiry. Safe stale reclamation requires at least:

1. every participant stops protected effects when it no longer has a valid lease;
2. renewal is completed before expiry with margin;
3. a bounded clock-skew/grace model is explicitly chosen if wall-clock expiry is used;
4. stale reclaim is performed with the exact current blob SHA so a renewed/replaced claim cannot be deleted accidentally.

If these conditions cannot be established, an expired timestamp is evidence of uncertainty, not permission to steal a claim.

## PR creation ambiguity: exact recovery sequence

GitHub's create-PR endpoint documents head/base and normal validation/conflict-style failures but no request idempotency key. The safe direct pattern is therefore deterministic identity plus read-before-retry:

1. Freeze head branch and exact head SHA `H`; freeze base branch.
2. Search/list open PRs for the same head and base before creation.
3. If none, call create PR once.
4. On clear success, call `get_pr_info` and require exact head/base and `head_sha == H`.
5. On transport uncertainty or validation ambiguity, **do not blindly create again**. Search/list same head/base.
6. If one candidate exists, verify it by exact PR info. Accept as recovered success only if exact identity/head match.
7. If no candidate exists, retry only according to the observed error class/backoff policy.
8. If a candidate exists but its head moved or base differs, treat the original attempt as unresolved/conflicting rather than silently coalescing it.

The public List Pull Requests endpoint supports explicit `head=<owner>:<branch>` and `base=<branch>` filters. The connected `search_prs` action is more generic, so exact `get_pr_info` verification remains necessary after search.

## Evidence-binding recipe for code review + CI + merge

1. `get_pr_info` -> freeze PR head `H`.
2. Read classic combined commit status for `H`; record it only as the evidence family it actually covers.
3. Read exposed workflow-run evidence for `H` when available; preserve wrapper coverage limitations.
4. If acceptance policy requires Checks not exposed through the connector, classify evidence as incomplete rather than inferring green.
5. Submit review with `commit_id=H`.
6. Re-read PR head. If it is no longer `H`, invalidate the review/evidence bundle and restart.
7. Perform synchronous merge with `expected_head_sha=H`.
8. On ambiguous merge response, read state before any retry.

Server-side branch protection remains valuable as an authoritative final gate because it can require named Checks/statuses on the latest commit even when the Chat connector cannot enumerate every evidence API. A connector-visible `combined status == success` must not be treated as proof that every required GitHub Actions Check succeeded.

## Current direct-vs-background capability boundary

### Directly executable with inspected ordinary connected surfaces

- exact ref/head read;
- create/update/delete repository files with per-file blob-SHA CAS;
- create tree + create commit(parent SHA) + non-force ref update;
- deterministic branch creation/update;
- PR search/read/create;
- review pinned by `commit_id`;
- combined status readback and limited workflow-run readback;
- synchronous merge pinned by `expected_head_sha`.

### Public GitHub capability but not exposed by inspected connector

- GraphQL `createCommitOnBranch(expectedHeadOid)` explicit branch-head CAS;
- fresh `workflow_dispatch` mutation;
- direct delete-ref action;
- general Checks API read surface.

### Background/controller-dependent

- GitHub Actions workflow execution/concurrency and auto-merge waiting;
- Argo Workflow Controller reconciliation;
- Temporal Service + Worker polling/replay.

Repository configuration can prepare these systems, but configuration alone is not execution in Chat-only mode.

## Official sources checked

GitHub:
- REST repository contents: https://docs.github.com/en/rest/repos/contents
- REST Git references: https://docs.github.com/en/rest/git/refs
- REST Git trees: https://docs.github.com/en/rest/git/trees
- REST Git commits: https://docs.github.com/en/rest/git/commits
- GraphQL `createCommitOnBranch`: https://docs.github.com/en/graphql/reference/mutations#createcommitonbranch
- REST pull requests / merge: https://docs.github.com/en/rest/pulls/pulls
- REST pull request reviews: https://docs.github.com/en/rest/pulls/reviews
- REST commit statuses: https://docs.github.com/en/rest/commits/statuses
- GitHub status-check types / protected branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- REST workflow dispatch: https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event
- Actions concurrency: https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency

Kubernetes:
- Leases: https://kubernetes.io/docs/concepts/architecture/leases/
- Lease API: https://kubernetes.io/docs/reference/kubernetes-api/cluster-resources/lease-v1/

## Acceptance/counterexample tests added

1. **Composite branch-CAS race:** read `H0`; build `C(parent=H0)`; competing writer advances to sibling `H1`; non-force ref update to `C` must fail under forward-only history. Do not count this as safe under force-rewrite races.
2. **Ambiguous ref update:** response lost after update. Read ref before retry; exact `C` means success, `H0` means retryable, descendant-of-`C` means incorporated-then-advanced, divergence means rebuild.
3. **Lease acquire ambiguity:** lost create response must recover by matching `claim_id`; a foreign claim is collision, not an error to overwrite.
4. **Lease renewal race:** renew with stale blob SHA while another renewal/replacement wins; update must fail and worker must stop if ownership cannot be re-proven.
5. **Stale reclaim race:** two reclaimers delete the same stale version / recreate; at most one create-only replacement can own the deterministic claim path.
6. **Expired-owner zombie:** former owner continues effects after lease expiry; protocol must label this unsafe because timestamp-based reclaim cannot prevent split brain unless every owner obeys no-effect-after-expiry.
7. **PR create ambiguous response:** search same head/base and exact-verify candidate before retry.
8. **Status/Checks mismatch:** classic combined commit status green while a required GitHub Actions Check is failing/missing; Chat must not claim complete CI evidence from combined status alone.
9. **Review drift:** review pinned to `H`, head moves to `H2`; merge with `expected_head_sha=H` must fail or be abandoned before re-review.
10. **Workflow-dispatch boundary:** presence of public REST endpoint does not satisfy Chat-direct capability unless the connector exposes a fresh dispatch mutation; rerun-existing-run is not equivalent.

## Scope / uncertainty labels

- The effective branch-CAS property is a protocol inference bounded to normal forward-only competing branch updates. It is not claimed across force-push/history rewrite.
- The connected GitHub tool descriptions were inspected read-only; no mutation was used for capability discovery.
- `get_commit_combined_status` is not treated as complete GitHub Actions Checks coverage because GitHub's official APIs distinguish commit statuses from Checks and Actions produces Checks.
- The lease analogy to Kubernetes is structural. GitHub file blobs do not provide Kubernetes lease semantics automatically; expiry discipline and CAS rules must be implemented by the cooperating workers.
- Fresh workflow dispatch remains an observed connector-surface negative in this invocation, not a claim that GitHub lacks the public REST endpoint.

## Frontier / exact continuation

Fresh-bootstrap first. If the Phase-1 overlay remains active, keep the Argus continuation dormant as restoration metadata. Next unresolved generic leaf: audit direct Chat-capable **server-side policy/branch-protection readback** and exact required-check verification, including whether the connected surface can read rulesets/branch protection sufficiently to prove the final merge gate without a general Checks API. Then audit GraphQL `createCommitOnBranch(expectedHeadOid)` semantics against the staged REST composite to delimit exactly where force-rewrite/background/server-policy assumptions differ. If connector capabilities change, recheck for fresh workflow dispatch, general Checks readback, and delete-ref without performing probe mutations. Preserve a nonempty crash/retry frontier and fail closed on evidence families that cannot be enumerated.
