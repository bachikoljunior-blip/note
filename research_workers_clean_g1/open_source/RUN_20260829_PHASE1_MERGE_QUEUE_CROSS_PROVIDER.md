# Open Source Phase-1: Cross-provider queue evidence — GitLab merge-train car IDs are a stronger recovery anchor, but not final-effect authority

## Frozen control provenance

This run remains bound to the same frozen tuple established before semantic work:

- `bootstrap_valid=true`
- frozen semantic note head `c268b3388fbb0cd7e3aa9fd20600415e8e95f393`
- root `control_revision=22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- open_source `config_revision=6`, blob `3aeff2e6964079f0f2d607874f47422c54d8b30d`
- phase/root/task `phase_1_chat_parity` / `o-chat-parity-root-v2-active-pool` / `phase1-clean-open-source-chat-capability-patterns`

No newer root/config semantics were adopted after semantic freeze.

This leaf follows `RUN_20260829_PHASE1_GITHUB_EFFECT_CAPSULE.md` and tests whether another open-source merge-queue system exposes a better durable operation identity/final-effect linkage.

## 1. GitLab Merge Trains expose an explicit server-side car/entry ID

Current GitLab Merge Trains API documents a first-class REST resource for each merge request on a train. Each object is one merge-request “car,” not the whole train, and includes:

- integer `id` for the merge-train entry;
- merge request object / IID;
- `target_branch`;
- train `status`;
- `created_at`, `updated_at`, and when complete `merged_at`/`duration`;
- associated `pipeline` with pipeline id, SHA, ref and status.

`GET /projects/:id/merge_trains/:target_branch` can be filtered with `scope=active` or `scope=complete`. The REST list has no explicit queue position; GitLab documents sorting by car `id` ascending for position, or using GraphQL `MergeTrainCar.index`.

Primary source:
`https://docs.gitlab.com/api/merge_trains/`

This is a materially different recovery shape from GitHub async merge: GitLab exposes the train car identity in active/complete server resources, whereas GitHub's async operation is a UUID whose dedicated result endpoint is explicitly retained only 24 hours after its latest update.

The comparison is deliberately narrow: the inspected GitLab contract does not state a GitHub-style 24-hour expiry for completed train entries, but this checkpoint does **not** claim indefinite retention.

## 2. GitLab also supports an exact source-head precondition at train admission

`POST /projects/:id/merge_trains/merge_requests/:merge_request_iid` accepts optional `sha`; if supplied, it must match the source branch HEAD or the add/merge fails. It returns `201 Created` for immediate train admission or `202 Accepted` when scheduled for later admission.

The normal merge-request merge API likewise accepts `sha` as a reviewed-head precondition; current docs report `409` when it differs from the source HEAD. GitLab 19.2 also introduced an instance/group setting that can require callers to provide that SHA.

Primary sources:
- `https://docs.gitlab.com/api/merge_trains/`
- `https://docs.gitlab.com/api/merge_requests/`

Reusable pattern:

`expected source HEAD -> server train-car ID -> train pipeline identity -> complete car status -> exact merged MR/target-branch effect`

As with GitHub, queue admission and a passing queue pipeline are not substitutes for final repository effect.

## 3. Merge-train pipeline SHA is not final target-branch authority

GitLab merge trains test each merge request against the combined changes of all cars ahead of it. If an earlier car fails, later train pipelines can be canceled and recreated against a different combined state. GitLab explicitly documents this recomputation behavior.

Primary source:
`https://docs.gitlab.com/ci/pipelines/merge_trains/`

Therefore the train pipeline's `sha` identifies the tested train state, not necessarily the final target-branch tip. A durable effect capsule should preserve it as CI/queue evidence, then separately establish the landed repository effect.

The Merge Request API exposes after-merge fields including `state`, `merge_commit_sha`, and `squash_commit_sha`. The merge strategy matters: fast-forward projects need not create a merge commit, and squash can add a distinct squash commit. Consequently an MR commit field is useful attribution evidence but should still be reconciled with exact target-branch ref evidence when the goal is “what actually landed on the protected branch.”

Primary sources:
- `https://docs.gitlab.com/api/merge_requests/`
- `https://docs.gitlab.com/user/project/merge_requests/methods/`
- `https://docs.gitlab.com/user/project/merge_requests/squash_and_merge/`

## 4. Durable-operation comparison

Persisted artifact:
`research_workers_clean_g1/open_source/MERGE_QUEUE_EVIDENCE_COMPARISON_20260829_V1.json`

Narrow conclusions from the inspected contracts:

### GitHub

Strongest recovery capsule:

- expected PR head;
- async UUID + exact pending method/action/head tuple;
- terminal request result;
- stack/member vector;
- exact base-ref transition chain;
- Rule Suite IDs + exact suite readbacks.

Weakness for delayed recovery:

- async result endpoint expires after 24 hours;
- queue admission (`enqueued`) is not final effect;
- large stacks can split across consecutive merge groups.

### GitLab

Strongest recovery capsule:

- project + MR IID;
- exact source head SHA;
- merge-train car ID;
- target branch;
- train pipeline ID/SHA/status;
- complete-scope car status and `merged_at`;
- merged MR commit fields;
- exact target-branch ref effect.

Advantage in the inspected API shape:

- the server-side train entry has a first-class integer identity and complete-scope read path, making it a stronger operation recovery anchor than an operation-result URL explicitly documented to expire after 24 hours.

But the key non-regression remains:

**operation identity is not final-effect authority.**

The train car ID can prove which queued operation is being observed; it does not prove the exact final branch commit without post-merge repository evidence.

## 5. Chat capability boundary

The current connected tool surface used in this invocation exposes GitHub but no GitLab repository connector/action. Accordingly this GitLab pattern is public source-qualified evidence for an external handoff, not a directly exercised Chat mutation capability.

That distinction is important for capability detection:

- `PUBLIC_API_CAPABILITY`: GitLab has a documented train-car ID / complete-scope recovery mechanism.
- `CURRENT_CHAT_CALLABLE_CAPABILITY`: not established in this environment.

Do not conflate the two.

## 6. Exact continuation / nonempty frontier

Fresh-bootstrap first. If Phase-1 remains active:

1. Finish the GitHub collector leaf by testing a known public stacked PR against the connected raw PR representation. If the documented `stack` object is not exposed, freeze `UNKNOWN_MEMBER_VECTOR` as the ordinary-Chat handoff condition rather than inferring stack membership from branch shape.
2. Integrate `RULE_SUITE_DISCOVERY_20260829_V1.py` with the effect capsule contract: permission/pagination/ref/evaluate-status/month-window evidence -> unique transition tuple -> persisted suite IDs -> exact ID readbacks.
3. Add a provider-neutral operation/effect taxonomy:
   - `INTENT_HEAD_BOUND`
   - `SERVER_OPERATION_ID_BOUND`
   - `QUEUE_OR_TRAIN_ADMITTED`
   - `CI_STATE_BOUND`
   - `FINAL_TARGET_REF_EFFECT_EXACT`
   - `POST_EFFECT_POLICY_EXACT`
   and require every capability adapter to declare which states it can actually prove.
4. Audit one additional queue system with a first-class operation ID, preferably Gerrit submit requirements/Change-Id or a merge-train system with exact ref-update evidence, to test whether the GitHub/GitLab model generalizes or needs another axis.
5. Preserve a nonempty Phase-1 frontier after that taxonomy leaf.

## Clean execution boundary

Public-source research was read-only. Role-local writes are confined to `research_workers_clean_g1/open_source/` plus the immutable own receipt namespace. No source repository, branch/ref, PR, issue, release, workflow, `DESIRED_STATE.json`, other-worker/downstream/O state, or shared aggregate ledger was mutated or consumed semantically.
