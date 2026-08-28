# Open Source Phase-1: Request-operation IDs and post-effect group IDs are different capabilities

## Frozen control provenance

Frozen semantics remain `control_revision=22` / `config_revision=6`, root blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, config blob `3aeff2e6964079f0f2d607874f47422c54d8b30d`, under Phase-1 task `phase1-clean-open-source-chat-capability-patterns`. Newer note-head semantics were not adopted.

This leaf follows the GitHub/GitLab queue comparison and adds Gerrit to test whether “server operation ID” is one capability or several phase-specific capabilities.

## 1. Gerrit submits an exact reviewed patch-set revision

Current Gerrit REST docs identify the inspected server as `v3.14.2-689-g41d6d59cff` and expose:

`POST /changes/{change-id}/revisions/{revision-id}/submit`

The endpoint therefore names the exact patch-set revision being submitted. This is a strong `INTENT_HEAD_BOUND` shape: unlike a mutable `current` alias, a full revision commit ID can be checkpointed as the reviewed intent.

Primary source:
`https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html`

Gerrit also exposes submit requirements in `ChangeInfo` when requested with the `SUBMIT_REQUIREMENTS` option. Those results can be `SATISFIED`, `UNSATISFIED`, `OVERRIDDEN`, etc., and plugin-provided submit rules are part of current server submission evaluation.

Primary source:
`https://gerrit-review.googlesource.com/Documentation/config-submit-requirements.html`

As with GitHub/GitLab, a pre-submit requirement snapshot is planning evidence, not a reusable effect lease.

## 2. `submission_id` is post-effect group identity, not a pre-effect request ID

The current Gerrit `ChangeInfo` contract says `submission_id` is optional and **only set when status is `MERGED`**. It is shared across changes belonging to the same submission, and the docs explicitly warn callers not to rely on its string format.

The submit endpoint also states that one submission may merge multiple changes: topic members when whole-topic submission is enabled, dependent changes, and the closure of those sets. Gerrit directs callers to use the returned `submission_id` to query all submitted changes.

Primary sources:
- `https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html`
- `https://gerrit-review.googlesource.com/Documentation/cross-repository-changes.html`

This yields a new distinction:

- GitHub async UUID: `REQUEST_OPERATION_ID_BOUND` before final effect.
- GitLab merge-train car ID: `REQUEST_OPERATION_ID_BOUND` at queue/train admission and reused in complete train state.
- Gerrit `submission_id`: `POST_EFFECT_GROUP_ID_BOUND`; it must **not** be treated as if it were a request ID available to recover an ambiguous pre-effect submit response.

If a Gerrit submit response is ambiguous and no request-operation identifier was captured, recovery begins by reading the change/revision state. Only after a `MERGED` state is observed does `submission_id` become authoritative grouping evidence.

## 3. Group closure is its own authority axis

Gerrit's Submitted Together behavior makes another cross-provider invariant explicit. A single trigger can affect more changes than the caller named directly.

Comparable group-closure evidence is:

- GitHub: stack/member vector, especially when merge queue may split it into multiple merge groups;
- GitLab: train cars and their target-branch ordering;
- Gerrit: Submitted Together closure plus post-effect `submission_id`.

Therefore group closure cannot be reduced to “operation ID” or “final SHA.” A safe capsule retains the member set/order or dependency closure separately.

## 4. Exact final target effect still needs the destination ref

Gerrit submit type can be merge-if-necessary, fast-forward-only, rebase, merge-always, or cherry-pick. Some modes can create a destination commit whose SHA differs from the reviewed patch-set revision.

Primary source:
`https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html`

So even Gerrit's revision-addressed submit endpoint does not remove the final-effect rule:

`exact reviewed revision -> server submit -> MERGED/submission_id -> exact destination-ref evidence`

The reviewed revision is intent authority; the destination ref is final effect authority.

## 5. Taxonomy revision

Persisted:

`research_workers_clean_g1/open_source/OPERATION_EFFECT_TAXONOMY_20260829_V2.json`

V2 replaces the overly broad single operation-ID axis with:

- `INTENT_HEAD_BOUND`
- `REQUEST_OPERATION_ID_BOUND`
- `QUEUE_OR_TRAIN_ADMITTED`
- `CI_STATE_BOUND`
- `FINAL_TARGET_REF_EFFECT_EXACT`
- `POST_EFFECT_GROUP_ID_BOUND`
- `POST_EFFECT_POLICY_EXACT`

This prevents a post-effect audit identifier such as Gerrit `submission_id` from being misused as a crash-recovery request token.

## 6. Exact continuation / nonempty frontier

Fresh-bootstrap first. If Phase-1 remains active:

1. Finish the GitHub known-stacked-PR connected-surface audit. If ordinary raw PR reads cannot expose the documented `stack` object, finalize `UNKNOWN_MEMBER_VECTOR` as a strict capability boundary.
2. Wire `RULE_SUITE_DISCOVERY_20260829_V1.py` into the effect capsule and add a capture/recovery order table with ambiguous-response cases.
3. Add an executable provider-neutral classifier for the V2 axes with negative fixtures preventing:
   - post-effect group ID -> request-ID promotion;
   - CI SHA -> target-ref SHA promotion;
   - queue admission -> final effect promotion;
   - pre-effect policy pass -> effect lease promotion;
   - group trigger -> complete member closure promotion.
4. Audit Gerrit historical NoteDb `meta=SHA` snapshots as durable policy/change-state provenance and determine whether they can strengthen replay without being confused with destination-ref effect authority.
5. Preserve a nonempty Phase-1 frontier after that classifier leaf.

## Clean execution boundary

All public-system research was read-only. Writes remain confined to the authorized `research_workers_clean_g1/open_source/` and own immutable receipt namespaces. `DESIRED_STATE.json`, source repos, branches/refs, PRs/issues/releases/workflows, other-worker/downstream/O state, and the shared aggregate ledger were not mutated or consumed semantically.
