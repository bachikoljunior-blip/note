# Open Source Phase-1: Merge-Effect Binding to Rule Suites + Authorization-Scope Epoch Gap

Frozen semantic tuple remains `note=db477c44fd7cdb98e81c35699aa0aa309f86935a`, root control `20`, open_source config `6`. This continuation does not adopt newer control semantics after authorized role-local persistence moved the note head.

This checkpoint supersedes the required-workflow conclusion in `RUN_20260829_0224_PHASE1_REQUIRED_WORKFLOW_ATTRIBUTION.md` and extends `RUN_20260829_0224B_PHASE1_RULE_SUITE_AND_ROOTS_SCOPE.md`.

## 1. Required-workflow verification splits cleanly into preflight and exact post-effect reconciliation

GitHub's current synchronous pull-request merge endpoint accepts a PR-head `sha` precondition and, on success, returns `{sha, merged, message}`. The current pull-request read contract states that after merge, `merge_commit_sha` is the actual merge commit for merge-commit merges, the squashed commit for squash, or the commit the base branch was updated to for rebase. Therefore the exact SHA `M` of the landed base-branch effect is recoverable after a successful ordinary merge and, if the immediate response is ambiguous, can still be recovered from a later authoritative PR read once the PR is known merged.

Official source:

- https://docs.github.com/en/rest/pulls/pulls?apiVersion=2026-03-10

This gives a precise Rule Suite reconciliation boundary:

- **Successful direct synchronous merge:** response `sha=M` is an exact effect identifier. A Rule Suite can decide the required-workflow family only if its `ref` is the intended base ref and `after_sha=M`, then its `rule_evaluations` contains `rule_type=workflows`, `rule_source.type=ruleset`, the exact applicable ruleset id, `enforcement=active`, and `result=pass|fail`.
- **Ambiguous synchronous response:** if a pre-read proved the PR open at expected head `H`, and a later PR read proves it merged with `merge_commit_sha=M`, then `M` is the actual landed effect. This is enough to verify the policy state of what landed, but it does **not** prove that this request/actor caused the merge or that an exact requested merge method was the cause. Causal attribution and effect identity remain separate facts.
- **Blocked synchronous merge:** status `405/403/etc.` proves the merge did not complete through that response path, but it does not document the prospective `after_sha` needed to bind a failed Rule Suite to this exact attempt. Family-specific Rule Suite attribution therefore remains `UNKNOWN` unless another authoritative binding signal exists.

The connected GitHub surface directly exposes the synchronous path as `merge_pull_request(expected_head_sha=..., merge_method=...)` and returns GitHub's `sha/merged/message` result. A safe public merged-PR read on `github/github-mcp-server#3123` demonstrated that the connected `get_pr_info` surface also returns `merged=true` and exact `merge_commit_sha=febc3293a4feb70e62399f39a26b082f78b9b176`. The corresponding public commit has one parent, consistent with a squash-style landed commit. No mutation probe was performed.

## 2. Async merge has a stronger durable intent handle, but failure and queue mapping still have proof gaps

GitHub's current asynchronous merge API accepts exact PR-head `sha`, explicit `merge_method`, and `merge_action`. A newly accepted request returns a UUID. A `409` returns an already-existing request UUID while explicitly warning that its options may differ from the caller's requested options. While pending, the result endpoint returns the UUID, merge method, merge action, and expected head SHA. On terminal success it reports the merge commit OID; on failure it reports why the PR could not be merged. Results expire 24 hours after their most recent update.

Official source:

- https://docs.github.com/en/rest/pulls/pulls?apiVersion=2026-03-10

The durable crash/retry recipe is therefore:

1. Persist intent `(repo, PR, expected head H, merge method, merge action)` before mutation.
2. On `202`, checkpoint returned UUID immediately. On `409`, treat the returned UUID as **untrusted for this intent** until a result read confirms the pending request's `expected_head_sha`, `merge_method`, and `merge_action` match the checkpointed intent.
3. Terminal success with merge OID `M` yields an exact landed-effect SHA. It can be joined to a Rule Suite only by exact `ref + after_sha=M`.
4. Terminal failure does not document an exact ref-update SHA in the public result contract, so a generic failure message cannot safely be converted into a family-specific required-workflow Rule Suite result.
5. After 24-hour result expiry, a later merged PR read can still recover the actual landed SHA `M`, but cannot by itself prove that the expired async request caused that merge.

The inspected connected Chat GitHub surface still has no async-merge/merge-queue mutation or result-poll action; it exposes only the synchronous merge wrapper and auto-merge. Thus direct ordinary merge has an executable exact-effect path today, while merge-queue/stack async remains a handoff/capability gap for this connected surface.

## 3. Queue/stack results cannot be naïvely collapsed to one Rule Suite

GitHub's current stacked-PR documentation says stacks use the async merge API, can land multiple PRs, and merge queues may split large stacks across consecutive merge groups. The resulting history also differs by merge method: one merge commit for a merged group, one squash commit per PR, or a rebased linear history.

Official sources:

- https://docs.github.com/en/pull-requests/reference/stacked-pull-requests
- https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests

Therefore one terminal async merge OID must not be assumed to cover every Rule Suite evaluation involved in queue/stack execution. A queue/stack policy verifier needs an explicit completeness proof that every relevant base/merge-group ref update and applicable rule evaluation has been mapped. Until that mapping is available, the family stays `UNKNOWN` even if the final requested PR is merged.

The executable helper `MERGE_EFFECT_RULE_SUITE_RECONCILER_20260829_0224.py` encodes this fail-closed split. Its embedded fixtures cover exact synchronous success, actual-effect recovery after ambiguous sync response, async UUID mismatch, terminal async success, queue-without-complete-suite-mapping, explicit queue coverage, and async failure without exact effect SHA.

## 4. Policy verifier v3 fixes a concrete false-positive in v2

`VERIFIER_20260829_0157_POLICY_TRI_STATE_V2.py` treated a successful exact `(target head, source repository, workflow path/ref/sha)` Workflow Run as sufficient for required-workflow `PASS`. The live scheduled reusable-workflow counterexample from the previous checkpoint shows that this can be a false positive: an ordinary run can expose the same provenance without proving that a ruleset required it.

`VERIFIER_20260829_0224_POLICY_TRI_STATE_V3.py` supersedes v2 for this family. Workflow runs are now diagnostics only. Required workflows can `PASS/BLOCKED` only from an exact effect-bound active `workflows` Rule Suite evaluation from the applicable ruleset; otherwise the family is `UNKNOWN`. Other policy-family logic remains imported from v2 to minimize the revision surface.

`REQUIRED_WORKFLOW_ATTRIBUTION_CHECKER_20260829_0224_V2.py` remains the smaller standalone rule-family contract.

## 5. Filesystem MCP is a useful implementation counterexample, but MCP Roots itself is deprecated and is not access control

The current MCP `2026-07-28` specification explicitly marks Roots deprecated, says new implementations SHOULD NOT adopt it, and recommends tool parameters, resource URIs, or server configuration instead. It also states that Roots are informational guidance, not an access-control mechanism, and that the protocol does not enforce confinement to them.

Official source:

- https://modelcontextprotocol.io/specification/2026-07-28/client/roots

The exact public `modelcontextprotocol/servers` Filesystem server at commit `40a8de87ed31a307c2a85cae21a78da9b7c1caf8` is still valuable as an **implementation-level** example because its own code independently enforces an allowed-directory set. In `src/filesystem/index.ts` it:

- installs the allowed-directory set into the validation library;
- replaces that set after client Root updates;
- handles `roots/list_changed` by fetching the new roots and replacing the set;
- performs an initial roots fetch in `oninitialized`;
- exposes `list_allowed_directories` as a read-only observation of the current set.

The tool returns only the current directory list. There is no generation number, epoch, lease token, or CAS token in that observation. Consequently `list_allowed_directories` is a freshness observation, not a capability lease. A writer can observe scope S, then have the scope changed before `write_file`; the subsequent write must still fail closed at call time.

This sharpens `CAPABILITY_FINGERPRINT_20260829_0224_V4.py`: surface freshness, resource-scope freshness, and exact operation authorization are separate dimensions. For new systems, use the pattern (server-enforced dynamic scope + explicit current-scope observation + call-time enforcement), **not** the deprecated Roots mechanism itself.

The open Filesystem issue #3204 further shows initialization readiness is separate from configured scope: a tool call may race the initial root update and get access denied even though the client has supplied an intended root. A readiness check should use an explicit server-observable state when available; fixed sleeps do not establish a lease.

## 6. Rule Suite read permission remains a target-specific proof-path constraint

Current repository Rule Suite REST requires fine-grained `Administration` repository permission (read). A safe connected read of the public `github/docs` Rule Suite list returned `403 Resource not accessible by integration`. This is exact negative authorization evidence for that operation/resource under the current connected credential; it is not global absence of Rule Suites.

Official source:

- https://docs.github.com/en/rest/repos/rule-suites?apiVersion=2026-03-10

The broader authorization lattice remains:

- repository/collaborator role read -> `RESOURCE_ROLE_PROVED`;
- server-enforced current resource scope -> `RESOURCE_SCOPE_PROVED`;
- operation-bound allow/deny -> exact operation authorization evidence;
- post-call success -> proof that that exact mutation succeeded then, not a reusable preflight permission lease.

## Exact Phase-1 continuation / nonempty frontier

Fresh-bootstrap first. If Phase-1 remains active, keep Argus dormant and continue from this checkpoint.

1. **Positive Rule Suite join:** find a safe repository/context where the connected credential can read Rule Suites (`200`) or a public source with a complete real rule-suite payload, then validate the exact `(base ref, after_sha M, ruleset id, workflows rule)` join against a real merged effect. Do not perform a noop mutation.
2. **Blocked-effect binding:** determine whether any authoritative GitHub surface exposes a prospective/ref-update SHA or rule-suite identifier on a failed synchronous/async merge. If not, formalize family-specific failure attribution as an irreducible `UNKNOWN` despite known overall merge failure.
3. **Queue/stack mapping:** map merge-group/final-base OIDs to Rule Suite refs and after-SHAs. Keep multi-group stacks fail-closed until coverage of every relevant group/update is explicit.
4. **Verifier hardening:** execute/check `VERIFIER_20260829_0224_POLICY_TRI_STATE_V3.py` and `MERGE_EFFECT_RULE_SUITE_RECONCILER_20260829_0224.py` in a clean checkout when a direct execution surface is available; add negative fixtures for `result=bypass`, evaluate-mode rule evaluations, and mismatched base refs.
5. **Authorization-scope epoch:** audit a modern (non-Roots) open-source tool server that exposes a server-enforced dynamic scope with an explicit revision/etag/epoch or operation-bound permission check. This would distinguish a genuine capability lease/CAS from the Filesystem server's observation-only model.
6. Preserve a nonempty Phase-1 frontier and do not restore unrelated/base research while the Phase-1 overlay remains active.
