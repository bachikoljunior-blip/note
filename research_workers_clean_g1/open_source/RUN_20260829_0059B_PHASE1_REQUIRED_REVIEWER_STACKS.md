# Open Source Phase-1 Amendment: Required-Reviewer Semantics + Stacked-PR Transaction Boundary

## Frozen semantic tuple

This amendment continues under the already-frozen clean tuple from the same run:

- note semantic base SHA: `40b09e47cf596eb6a9846988bc2f860b719afb8b`
- control revision: `19`
- open_source config revision: `6`
- assignment: `phase1-clean-open-source-chat-capability-patterns`

Only public sources and the role's own clean state were used. Note head changes after the semantic barrier were caused by this role's authorized checkpoint/verifier persistence; no newer control semantics were read or adopted.

## Revision 1: the required-reviewer pattern discrepancy is now classified as REST-schema lag/underspecification, not an unresolved 50/50 contract

The first checkpoint recorded a conflict:

- current ruleset prose says required-reviewer file patterns use standard `.gitignore`-style behavior with ordered matching and `!` negation;
- current REST rules schema labels `file_patterns` as `fnmatch` syntax.

A fresh official GitHub changelog entry dated 2026-02-17 resolves the intended user-facing evolution: the required-reviewer rule became generally available and specifically added `!` negation “just like `.gitignore`”. The live ruleset prose also documents ordered negation. Therefore the stronger interpretation is:

1. ordered `.gitignore`-style negation is an intentional current feature of required reviewers;
2. the REST schema's bare `fnmatch` label is stale or incomplete as a normative matching description;
3. a client that implements only ordinary fnmatch cannot claim `required_reviewer_pattern_semantics=true`;
4. the verifier should accept the completeness axis only when the collector implements the documented ordered-negation behavior or receives server-derived required-team obligations.

This remains different from CODEOWNERS syntax, whose own documented parser semantics must be handled separately.

Official evidence:

- https://github.blog/changelog/2026-02-17-required-reviewer-rule-is-now-generally-available/
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- https://docs.github.com/en/rest/repos/rules

## Revision 2: the exact raw ruleset key for Copilot unattributed changes is observable

A read-only public ruleset probe on `github/docs` ruleset `19633356` returned a `pull_request` rule with:

- `required_approving_review_count: 1`
- `dismiss_stale_reviews_on_push: true`
- `required_reviewers: []`
- `require_code_owner_review: true`
- `require_extra_approval_for_unattributed_changes: true`

The public ruleset prose says “Require an additional approval for unattributed Copilot pull requests” is in public preview and enabled by default for new and existing rulesets.

Therefore the first verifier's normalized `copilot_extra_approval_may_apply` concept has an exact raw-policy source: `require_extra_approval_for_unattributed_changes`. A future verifier revision should normalize the raw key directly rather than leaving it as a vague capability flag. The existing negative fixture remains semantically correct: if the raw setting is true and the PR is an unattributed Copilot PR, one additional approval is required.

Public fixture read:

- `GET https://api.github.com/repos/github/docs/rulesets/19633356`

## New capability leaf: stacked pull requests expose a strong server transaction, but the current connected Chat surface does not expose the required operations

GitHub's stacked pull requests are in public preview. Current official documentation exposes:

- REST list/get/create/add/remove stack endpoints;
- a `stack` object on pull request resources;
- read-only GraphQL stack membership;
- webhook stack membership;
- and an asynchronous merge endpoint that is **mandatory** for stacks.

A stack merge request is server-atomic at the group level: when requesting a PR in the stack, all unmerged PRs below it through the requested PR are merged, or all are added to the merge queue, or none of the group is. Branch protection and repository rules are evaluated later during the asynchronous transaction, not fully at request acceptance.

Official sources:

- https://docs.github.com/en/pull-requests/reference/stacked-pull-requests-apis-and-webhooks
- https://docs.github.com/en/rest/pulls/stacks
- https://docs.github.com/en/rest/pulls/pulls
- https://docs.github.com/en/pull-requests/reference/stacked-pull-requests

## Stack-construction transaction semantics

### Create

`POST /repos/{owner}/{repo}/stacks` takes an ordered array of PR numbers from bottom to top. Each PR's base ref must match the prior PR's head ref. Documented statuses are `201`, `404`, and `422`; there is no documented idempotency key or expected-stack-version precondition.

### Add/remove

Adding PRs to the top and removing unmerged PRs are separate mutations. Add/remove document `409` when another request is modifying the stack, but still do not expose an expected old stack version analogous to a CAS token.

Therefore safe ambiguous-response recovery is read-after-write, not blind retry:

1. persist intended ordered PR vector and exact per-member heads before the mutation;
2. on timeout/ambiguous response, list/get the stack or read stack membership from the PRs;
3. accept success only if one exact stack contains the intended membership/order and expected heads/base linkage;
4. if a different stack or partial mutation is observed, classify `UNKNOWN`/conflict rather than retrying into a second topology.

This is weaker than GraphQL `updateRefs` CAS because the public stack mutation has neither an idempotency key nor an expected-head vector.

## Stack merge: `sha` is a requested-PR precondition, not a full-stack member vector

The asynchronous merge endpoint accepts:

- `sha`: the requested PR head that must match;
- `merge_method`;
- `merge_action` (`default`, `direct_merge`, `merge_queue`).

If `sha` is omitted, GitHub snapshots the current requested-PR head and cancels if that PR is pushed between request and execution. Pending result readback exposes `uuid`, `merge_method`, `merge_action`, and `expected_head_sha`.

For a stack, however, the request/result does **not** carry a vector of expected head SHAs for every lower stack member. That matters for exact-intent protocols: a lower branch can change while the requested top PR head remains unchanged. Server rule evaluation and linear-history checks may reject many such races, but the top `sha` alone does not prove that every reviewed layer boundary stayed identical to the client's preflight snapshot.

A durable stack-merge intent capsule should therefore store at least:

```text
stack_id / stack_number
stack_base_ref + observed stack_base_sha
ordered_members = [
  {pr_number, head_sha, direct_base_ref, direct_base_sha}, ...
]
requested_pr_number
requested_head_sha
merge_method
merge_action
async_uuid (once known)
```

`requested_head_sha` is the API precondition. The member vector is a recovery/audit precondition that must be re-read before submission and reconciled after ambiguous outcomes.

## Stacked async-merge crash/retry table

| State | Evidence | Safe recovery |
|---|---|---|
| `STACK_SNAPSHOT` | exact stack id/number, ordered member/head vector, requested top `H` | re-read stack + members; proceed only if identical |
| `SUBMIT_UNKNOWN` | request may have reached GitHub; no durable UUID | inspect PR/stack merge state and any recoverable async request before retry; blind retry is not proof-safe |
| `ACCEPTED_U` | 202 + UUID `U` | persist `U` immediately; poll result |
| `EXISTING_U_MATCH` | 409 + existing UUID; pending result matches `expected_head_sha=H`, method and action | resume `U`; still keep member-vector audit snapshot |
| `EXISTING_U_MISMATCH` | existing request has different expected head/method/action | fail closed; this is another transaction |
| `ALREADY_200` | endpoint says already merged or already queued | exact stack/member/queue readback required; 200 alone does not prove this caller's intended stack snapshot |
| `PENDING` | result retains UUID/method/action/expected top head | continue polling; policy evaluation is still in progress |
| `MERGED` | terminal result + merge commit OID | verify all intended stack members reached expected terminal merged state and resulting stack/base state is consistent |
| `QUEUED` | stack added to merge queue | switch to merge-group evidence; stack may be split across consecutive merge groups if too large |
| `FAILED` | terminal rule/merge failure | record failure; do not mutate/retry under the old intent capsule without a new snapshot |
| `EXPIRED_UNKNOWN` | async result aged out after 24h and durable repository state cannot reconstruct outcome | remain `UNKNOWN`; 404 is not evidence that no request was made |

The public docs explicitly state that async merge result records expire 24 hours after their most recent update.

## Merge queue nuance for stacks

GitHub may allow a stack's merge group to exceed configured maximum size by up to 50% to keep the stack together. If the stack is too large for that buffer, it is split across consecutive merge groups. Therefore a verifier must not assume “one stack = one merge-group SHA”. Queue-stage evidence must permit an ordered sequence of merge groups while preserving bottom-up stack order.

## Connected Chat capability boundary observed

Read-only connector discovery found no stack-specific action and no async-merge action. The connected generic GitHub fetch rejected a public `GET /repos/github/docs/stacks?...` request as outside its allowlist. The generic pull-request fetch is usable, but in an observed `github/gh-stack` PR created with the stacks CLI it did not expose a `stack` object through the connected response; the new API examples use `X-GitHub-Api-Version: 2026-03-10`, while generic connected fetch does not expose a caller-controlled API-version header.

Consequences:

- public GitHub **has** stack read/write and atomic async stack merge capability;
- the inspected ordinary connected Chat surface **does not currently expose** stack create/add/remove or async merge;
- connected synchronous `merge_pull_request(expected_head_sha=...)` cannot substitute, because GitHub explicitly says stacks cannot be merged with legacy synchronous merge endpoints or mutations;
- connected `enable_auto_merge` cannot substitute either, because GitHub explicitly says auto-merge is not supported for stacked PRs;
- a Chat workflow can still create ordinary chained PR branches, but that is not equivalent to server-linked stack membership and does not obtain the stack atomic-merge semantics.

This is a clean example of Phase-1's core distinction: **public platform capability exists; connected Chat capability is missing; claimed/adjacent operations must not be counted as equivalents.**

## Exact continuation

Fresh-bootstrap first. If Phase-1 remains active:

1. Revise the executable verifier normalization so the raw ruleset key `require_extra_approval_for_unattributed_changes` maps directly to the Copilot extra-approval logic; retain the existing negative fixture.
2. Treat required-reviewer matching as documented ordered `.gitignore`-style negation despite the stale REST-schema `fnmatch` label; add a fixture where `*.sql` is required but `!test/*.sql` excludes a path.
3. Audit whether any connected GitHub action permits selecting API version `2026-03-10`; if not, preserve new-stack API visibility as a connector-version/allowlist gap rather than a generic GitHub absence.
4. Add a stack intent-capsule fixture/state-machine artifact distinguishing requested-top `sha` from the ordered member-head snapshot and allowing multiple merge-group SHAs for large queued stacks.
5. Then return to the positive required-workflow identity fixture and server-derived review-decision surface. Preserve a nonempty Phase-1 frontier and keep the unrelated Argus continuation dormant.
