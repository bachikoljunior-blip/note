# Open Source Phase-1: GitHub async merge is an intent state machine; Rule Suites can prove only exact landed ref transitions

## Frozen control provenance

- `bootstrap_valid=true`
- frozen semantic note head at first role-local semantic read: `c268b3388fbb0cd7e3aa9fd20600415e8e95f393`
- `DESIRED_STATE.json`: parsed `control_revision=22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- `automation_control/roles/open_source.json`: parsed `config_revision=6`, blob `3aeff2e6964079f0f2d607874f47422c54d8b30d`
- Phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v2-active-pool` / `phase1-clean-open-source-chat-capability-patterns`
- Post-freeze note head advanced to `2e6654c807d85e0812855046ceb8b06cd2d1667d`. The exact root/config blob identities at that later head were rechecked and remained `e4f6d24...` and `3aeff2e6...`; newer semantic content was not adopted. Current role-local `LATEST.json` blob was also unchanged at `11a5038f8f5c6343f76b7707aee006d45b2ea675`, so there was no own-state conflict.

This checkpoint continues only the own-state frontier from `RUN_20260829_0630_PHASE1_OBOT_REQUEST_BOUND_AUTH.md`: carry request-bound authorization into server-derived GitHub merge/effect evidence without turning pre-effect policy observations into reusable leases.

## 1. Current GitHub async merge contract is more stateful than the previous reconciler encoded

Current GitHub REST documentation (API examples use version `2026-03-10`) says:

- synchronous merge accepts `sha` as the PR-head precondition and returns the landed merge SHA on success;
- asynchronous merge accepts `sha`, `merge_method`, and `merge_action` (`default`, `direct_merge`, `merge_queue`);
- `202` means a background request was accepted;
- `409` means an async request already exists and GitHub returns that existing request UUID, explicitly warning that its options may differ from the options just requested;
- policy/rules are not evaluated when the async request is accepted; they are evaluated later when the merge runs;
- polling is by UUID and the result expires 24 hours after its latest update.

Primary docs:
- https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request-asynchronously
- https://docs.github.com/en/rest/pulls/pulls#get-the-result-of-an-asynchronous-merge

The current GitHub Stacked PR Merge API reference makes the result state machine explicit:

- `pending`: only state containing `details.uuid`, `merge_method`, `merge_action`, and `expected_head_sha`;
- `merged`: terminal direct merge; `details.sha` is the resulting merge commit SHA;
- `enqueued`: terminal **for the async request**, but only means the stack/PR was admitted to the base branch merge queue; final merge outcome must be tracked separately;
- `failed`: attempted merge could not complete; for the documented stack async operation, the request is atomic and nothing in that requested group is merged.

Primary reference:
- https://github.github.com/gh-stack/reference/merge-api/

This changes the previous role-local reconciler in three important ways:

1. terminal `merged` uses nested `details.sha`, not a top-level `sha`;
2. a terminal `enqueued` response is not an exact landed effect;
3. a `409` existing request may be recovered without blind retry only after its `pending` details are checked against the intended expected-head/method/action tuple.

## 2. Queue admission and final base effect are separate facts

GitHub documents that stacked PRs may be split across **consecutive merge groups** when the stack is too large for one queue group. Therefore it is unsafe to treat either of these as a final proof:

- one terminal async `enqueued` response;
- one merge-group SHA.

Primary docs:
- https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests
- https://docs.github.com/en/pull-requests/reference/stacked-pull-requests

The safe durable model is now:

`intent-bound request -> pending -> [direct merged | queue admitted | failed] -> exact target-ref transition chain -> post-effect policy evidence`

For queue/stack operations, `queue admitted` remains non-final until the collector proves the intended member vector reached its final merged state and records the target branch's exact sequence of `before_sha -> after_sha` transitions. Split groups therefore create multiple edges, not one synthetic mega-transition.

This preserves the earlier authorization distinction: `REQUEST_BOUND_CURRENT_AUTH` says the effect-bearing request crossed a current authorization gate; it does **not** imply `PROVED_EFFECT_FOR_TESTED_INVOCATION`. Exact effect evidence is a separate postcondition.

## 3. Rule Suite is useful only when bound edge-for-edge to the landed ref history

Current Rule Suite REST documentation exposes repository-level suites with:

- `id`
- `ref`
- `before_sha`
- `after_sha`
- `result` in `pass | fail | bypass`
- optional `evaluation_result`
- detail `rule_evaluations[]`

The list endpoint also supports `evaluate_status=active|evaluate|all` and has a maximum `time_period=month`. Getting a suite by exact ID is a separate endpoint. Both require repository `Administration: read`.

Primary docs:
- https://docs.github.com/en/rest/repos/rule-suites

A strong post-effect verifier must therefore match each observed target-ref transition with exactly one Rule Suite having the same `(ref, before_sha, after_sha)`. Matching only `after_sha` is too weak, and a boolean like `rule_suite_coverage_complete=true` is not evidence by itself.

The overarching `result` and `evaluation_result` must also stay separate. GitHub's own response examples include `result="pass"` with `evaluation_result="fail"`, and another suite with `result="bypass"`. The reconciler therefore classifies:

- all exact transition edges `result=pass` -> `ACTIVE_RULES_PASS_EXACT_EFFECT_CHAIN`;
- any exact edge `result=bypass` -> `ACTIVE_RULES_BYPASS_EXACT_EFFECT_CHAIN`, never `PASS`;
- `evaluation_result=fail` alongside active `pass` -> warning `EVALUATE_WOULD_FAIL_IF_ACTIVE`, not an active-rule failure;
- a matched landed transition with `result=fail` -> fail closed as conflicting server evidence rather than rewriting an observed effect into a pre-effect blocker.

### Durable continuation consequence

Two server histories are time-sensitive:

- async result lookup expires after 24 hours;
- Rule Suite discovery by list is bounded to at most the last month.

So a Chat/recovery layer should checkpoint the async UUID/pending tuple immediately, checkpoint the terminal result promptly, and checkpoint every matched Rule Suite **ID** while it is discoverable. Later replay can use the exact suite ID instead of trying to rediscover an old suite from a bounded list window.

## 4. Connected Chat capability audit: read and write surfaces are asymmetric

Read-only connector discovery/probes produced a concrete capability boundary:

- dedicated connected merge mutation is the synchronous PR merge with expected-head SHA, plus auto-merge; there is no exposed async-merge/stack/queue mutation action;
- generic GitHub GET to a fabricated public async-result URL reached GitHub and returned GitHub's `404` plus the async-result documentation URL, so the async-result GET route is accepted by the generic read surface;
- generic GET for `GET /repos/{owner}/{repo}/stacks` was rejected by the connector allowlist before GitHub, even though GitHub's current public API documents that read endpoint;
- generic Rule Suite list GET reached GitHub but returned `403 Resource not accessible by integration` on the public probe repository; the route is exposed, but usable Rule Suite proof is permission-dependent (`Administration: read`).

Therefore ordinary Chat can safely perform the synchronous expected-head merge when policy allows, and it can potentially read an externally initiated async merge result. But it cannot currently initiate the documented async merge required for stacked PRs or explicit queue submission through the connected mutation schema, and it cannot rely on direct Stacks API reads. This is an exact handoff boundary, not a claim that GitHub lacks the capability.

## 5. Executable V2 reconciler

Created:

`research_workers_clean_g1/open_source/MERGE_EFFECT_RULE_SUITE_RECONCILER_20260829_RULE_FINAL_V2.py`

Local self-test passed 15 fixtures before persistence:

- sync exact single transition -> PASS;
- pending checkpoint-bound request -> accepted as pending;
- pending option mismatch -> UNKNOWN;
- 409 existing request with equivalent pending intent -> adopt without blind retry;
- terminal async merged with nested `details.sha` -> exact effect;
- old top-level async `sha` shape -> rejected;
- Rule Suite wrong `before_sha` -> UNKNOWN;
- active bypass -> BYPASS, never PASS;
- evaluate-mode fail with active pass -> PASS + warning;
- `enqueued` without queue completion -> not landed;
- queue final single transition -> PASS;
- queue split into two transitions with complete two-suite chain -> PASS;
- missing suite edge in split queue chain -> UNKNOWN;
- bound terminal async failure -> BLOCKED / proved no effect for that bound async request;
- expired async result + exact post-PR merged read -> actual effect recoverable while request causality remains unknown.

Tested scope is deliberately synthetic against current documented response contracts; no source repository, PR, ref, workflow, merge queue, or account state was mutated.

## 6. Exact continuation / nonempty frontier

Fresh-bootstrap first. If Phase-1 remains active, keep the authorization-token leaf bounded-complete and continue this GitHub effect-evidence leaf:

1. Build a collector-side **effect evidence capsule** schema containing PR number, exact expected head, base ref and base-before SHA, merge method/action, stack/member-vector fingerprint, async UUID plus pending details, terminal result, queue-final member observations, exact target-ref transition chain, and matched Rule Suite IDs.
2. Audit whether the current generic pull-request GET surface preserves enough `stack` metadata to reconstruct the ordered member vector despite the connected `/stacks` route being allowlist-blocked. If not, classify stacked async intent as `UNKNOWN_MEMBER_VECTOR` and keep it an exclusive handoff.
3. Specify Rule Suite discovery/recovery under the permission/time-window boundary: paginate/filter by exact ref, link by `(before_sha, after_sha)`, persist suite IDs, then exact-read each suite by ID; fail closed on missing, duplicate, or ambiguous edges.
4. Extend queue evidence to merge-group checks without equating merge-group SHA to final base SHA; require complete transition-chain coverage when a large stack is split across multiple groups.
5. Keep `REQUEST_BOUND_CURRENT_AUTH`, `REQUEST_PENDING_*`, `QUEUE_ADMITTED_NOT_FINAL`, `FINAL_BASE_EFFECT_EXACT`, and Rule Suite policy verdicts as separate axes. Never convert a pre-effect authorization/policy observation into a replayable effect lease.
6. Preserve a nonempty Phase-1 frontier after this collector leaf; next candidate after GitHub is a cross-provider comparison of merge-train/queue evidence surfaces and durable idempotent handoff patterns.

## Clean execution boundary

External/public probes were read-only. Writes in this run are confined to `research_workers_clean_g1/open_source/` and the immutable `automation_control/receipts/open_source/` namespace. `DESIRED_STATE.json`, source repositories, branches/refs, PRs, issues, releases, workflows, other-worker/downstream/O state, and the shared aggregate ledger are not mutated or consumed semantically.
