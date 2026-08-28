# Open Source Phase-1 Chat Capability Patterns

## Frozen control tuple

- role: `open_source`
- note main SHA frozen before semantic work: `8e8e6ad17ad2dbee406a9957c2fbf2f34ba2ca03`
- root control revision: `16`
- role config revision: `6`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v2-active-pool`
- assignment: `phase1-clean-open-source-chat-capability-patterns`
- enabled_desired: `true`
- clean boundary: own role-local state + public sources + own sanitized feedback only

The Phase-1 overlay superseded the prior Argus event-log continuation for this invocation. That prior continuation remains preserved as fallback/restoration metadata and was not resumed.

A later SHA-only note-head check observed `36c0a8ba27be779938e8a1dd9d78bd96c10d4f41`, different from the frozen SHA. Per the frozen control contract, semantic work stopped at that point; the newer control was not read or adopted. The later head was used only for authorized role-local write coordination.

## Public-source / direct-surface capability matrix

| Pattern | Ordinary Chat-mode surface observed | Exact guarantee usable | Boundary / fail-closed interpretation |
|---|---|---|---|
| Immutable checkpoint + CAS pointer | GitHub Contents API; connected `create_file`, `fetch_file`, `update_file`, `delete_file` | Existing-file update requires the current **blob SHA**; conflict can return 409. `create_file` wrapper requires a path that does not already exist. Exact file readback can be performed at the resulting commit SHA. | File SHA is a per-path precondition, not a multi-file/branch-head transaction. GitHub explicitly warns update/delete content writes should be serialized. Use immutable checkpoint first, exact-ref readback second, CAS-update `LATEST` last; on conflict re-read/reconcile rather than overwrite. |
| Deterministic repository claim | Create-only file path or Git ref/branch with a deterministic task/claim name | Git ref creation takes exact target SHA and returns conflict/validation failure when the ref cannot be created; a unique file path is likewise create-only through the connected wrapper. | Neither mechanism supplies TTL/stale-claim recovery. Store owner/epoch/expiry/evidence in the claim artifact; reclaim only after explicit stale-state proof. Additive labels/assignees are weaker because they are not exclusive create/CAS primitives. |
| Exact freshness read | Git ref-object GET and exact-ref file reads | `refs/heads/<branch>` returns the current object SHA without requiring commit-message/diff semantics; `fetch_file(ref=<sha>)` pins readback to a commit. | A branch name alone is mutable. Persist/compare exact SHA values at every boundary where freshness matters. |
| Branch advancement | Git ref update / connected `update_ref(force=false)` | With `force=false` GitHub verifies the update is fast-forward, preventing overwrite of divergent work. | This is **not** an expected-old-SHA compare-and-swap parameter. Treat it as fast-forward safety, not strict CAS. |
| PR preparation | Connected `create_pull_request`, `search_prs`, `get_pr_info`, diff/patch readers | Head/base can be made deterministic and PR state can be read back. | PR creation has no documented idempotency key. On timeout/ambiguous response or 422, search/read for an existing PR on deterministic head/base before any retry. |
| Review bound to code | GitHub pull-request review API; connected `add_review_to_pr(commit_id=...)` | `commit_id` anchors the review to a specific PR commit SHA; omitting it defaults to the latest commit. | A later push can make earlier review context stale. Always re-read head before exclusive action; never treat an unpinned approval as evidence for a moved head. |
| Exclusive merge handoff | GitHub sync merge API; connected `merge_pull_request(expected_head_sha=...)` | GitHub's `sha` parameter requires the PR head to match; mismatch returns **409 Conflict**. | Strong direct Chat-mode final CAS: review/test evidence -> exact head SHA -> merge with expected SHA. Head drift must force re-read/re-review. Async merge is a separate background endpoint and should not be assumed when only the sync connector action is exposed. |
| CI/status readback | Connected `get_commit_combined_status`, `fetch_commit_workflow_runs`, job/step/log/artifact readers | Evidence can be bound to a commit SHA and fetched after execution; workflow artifacts persist outputs for later readback. | These are readback primitives, not proof that Chat itself can start arbitrary CI. The current connected surface exposes re-run actions for existing runs but discovery found **no workflow-dispatch action**. |
| GitHub Actions concurrency | Public Actions workflow syntax | A concurrency group permits at most one running job/workflow; default pending behavior is replacement, with optional queueing. | Requires GitHub's background runner system. Useful when a workflow already exists and is actually dispatched, but not a substitute for a direct repository claim in a Chat-only transaction. Current connector cannot be assumed to dispatch a fresh workflow. |
| Argo Workflows synchronization/reconciliation | Public Argo architecture + mutex/semaphore docs | Controller reconciles queued Workflows; local/multiple-controller locks, mutexes, semaphores and parallelism are built-in mechanisms. | Requires Kubernetes plus a resident Workflow Controller (and often Argo Server). Writing YAML alone is not execution/reconciliation. Treat as background-controller architecture, not direct Chat capability. |
| Temporal durable replay/idempotency | Public Temporal Workflow Execution, Event History, Worker, Activity docs | Event History is a durable log used for replay/recovery; Workers poll Task Queues; Activities may retry and Temporal explicitly recommends idempotent writes/idempotency keys. | Requires Temporal Service plus Worker processes. A Temporal workflow can be durable, but repo edits alone do not instantiate that service/worker liveness. Temporal also notes an Activity can execute more than once even when completion is observed once, so external side effects still require idempotency. |

## Source-qualified observations

### GitHub REST / Actions (current docs checked 2026-08-28)

- Repository Contents: https://docs.github.com/en/rest/repos/contents
  - `sha` is required to update an existing file and is the blob SHA being replaced.
  - update/delete content writes are documented as conflicting when run in parallel and should be serialized.
  - response set includes 409 Conflict.
- Git references: https://docs.github.com/en/rest/git/refs
  - create ref accepts fully qualified `ref` + target `sha`; response set includes 409/422.
  - update ref has `force=false` by default to require fast-forward and avoid overwriting work.
- Pull request reviews: https://docs.github.com/en/rest/pulls/reviews
  - review `commit_id` pins review to a commit; omission defaults to most recent commit.
- Pull requests / merge: https://docs.github.com/en/rest/pulls/pulls
  - sync merge `sha` is the required matching PR-head SHA; mismatch returns 409.
  - GitHub also documents an asynchronous merge endpoint that returns an accepted/background result; this is a distinct capability from the connected synchronous merge tool.
- Workflows: https://docs.github.com/en/rest/actions/workflows
  - GitHub's public API supports `workflow_dispatch` when a workflow is configured for it, but the connected Chat surface discovered in this run did not expose that dispatch mutation.
- Actions concurrency: https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency
  - one running execution per concurrency group; default one pending execution is replaced by a newer pending execution, with optional queueing.
- Workflow artifacts: https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts
  - artifacts persist workflow outputs for later jobs/runs/readback; default artifact/log retention is documented as 90 days unless configured otherwise.

### Argo Workflows (latest public docs checked 2026-08-28)

- Architecture: https://argo-workflows.readthedocs.io/en/latest/architecture/
  - Workflow Controller performs reconciliation; worker goroutines process Workflows from a queue; controller processes one Workflow at a time per worker operation.
- Synchronization: https://argo-workflows.readthedocs.io/en/latest/synchronization/
  - mutexes, semaphores, local locks and multi-controller locks are controller-backed execution primitives.

### Temporal (current public docs checked 2026-08-28)

- Workflow execution: https://docs.temporal.io/workflow-execution
  - Workflow Execution is durable/recoverable; replay checks generated Commands against durable Event History and resumes from recorded state.
- Event History: https://docs.temporal.io/encyclopedia/event-history
  - complete durable lifecycle log drives replay/recovery after Worker crash.
- Workers: https://docs.temporal.io/workers
  - Worker Entities poll a Task Queue and make Workflow/Activity progress; this is a resident process boundary.
- Activity Definition: https://docs.temporal.io/activity-definition
  - Activities that write should be idempotent; a Worker may complete an external action and crash before reporting it, causing retry. Docs recommend idempotency keys and note Activity execution can occur multiple times even when completion is observed exactly once.

## Direct Chat transaction recipe

A repository-only durable flow that does not assume hidden background agents can be built as:

1. Read exact branch/ref SHA.
2. Create deterministic claim artifact (file path or ref). Collision means another claimant; do not overwrite.
3. Create immutable checkpoint/evidence artifact.
4. Read it back at the returned commit SHA.
5. CAS-update a mutable pointer using its current blob SHA.
6. Prepare deterministic branch/head and create PR only after searching for an existing same-head/base PR.
7. Bind review and CI evidence to exact PR-head SHA.
8. Perform the irreducible exclusive merge with `expected_head_sha`.
9. Release claim only after exact post-action readback proves the intended state; use current claim blob/ref identity for release.

Every mutating step needs an ambiguous-response recovery branch that **reads before retrying**. The strongest available exclusive primitive in the inspected connected surface is the PR merge head-SHA precondition; ordinary ref advancement is only fast-forward protected, and contents CAS is per-file.

## Acceptance tests / counterexamples

1. **Checkpoint readback:** create unique checkpoint -> response commit SHA -> `fetch_file(ref=commit_sha)` must match exact bytes before pointer advance.
2. **Pointer collision:** two writers use the same old blob SHA; only one update may succeed; loser must refetch/reconcile, never retry blind.
3. **Claim collision:** two workers attempt the same deterministic file/ref claim; at most one creation succeeds. A stale claim is not silently stolen without expiry/owner proof.
4. **Ambiguous PR creation:** after transport uncertainty, search same deterministic head/base before create retry; existing PR counts as recovered success only after exact head/base readback.
5. **Review/merge drift:** review commit A, move PR head to B, attempt merge with expected A -> must fail closed; re-review B before merge.
6. **No-background substitution:** merely writing Actions/Argo/Temporal configuration is not counted as execution. Acceptance requires an actually available dispatch/service/worker surface plus status/readback.
7. **Retry side effects:** any external effect that can be retried must carry an idempotency key or be an intrinsic CAS/create-only operation; Temporal's Activity retry model is an explicit public counterexample to assuming observed-once means executed-once.

## Scope and unverified claims

- Observations above are limited to the public documentation and connected GitHub action schemas inspected in this invocation.
- No mutation was used for capability probing. The only mutations authorized after the audit are this role-local checkpoint/LATEST/receipt persistence.
- Current connector discovery found no fresh workflow-dispatch action; this is a current-surface negative observation, not a claim that GitHub lacks the REST endpoint.
- Git ref fast-forward protection is deliberately not labeled strict CAS because the update API takes the new SHA and `force`, not an explicit expected-old SHA.
- Argo and Temporal are architectural/background-controller references only; no claim is made that their services are available in ordinary Chat mode.

## Frontier / exact continuation

Fresh bootstrap first. While Phase-1 overlay remains active, do **not** resume the preserved Argus event-log base continuation. Next generic leaf: turn the matrix above into a crash/retry transaction protocol with per-mutation `precondition -> effect -> exact readback -> ambiguous-response recovery` rows, then audit claim release/stale-claim recovery and PR-create ambiguity against official GitHub APIs. Verify whether the connected surface gains a direct workflow-dispatch action; if not, retain the strict background boundary. Add a commit-status/PR-head evidence binding recipe using `get_commit_combined_status`, PR head SHA, review `commit_id`, and merge `expected_head_sha`. Keep the previous Argus continuation preserved only as restoration metadata until Phase 1 ends or control explicitly restores it.
