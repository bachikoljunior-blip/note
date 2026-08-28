# Open Source Phase-1 Review/Policy Tri-State Verifier

## Frozen semantic tuple

- role: `open_source`
- frozen note main SHA: `40b09e47cf596eb6a9846988bc2f860b719afb8b`
- root control revision: `19`
- role config revision: `6`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v2-active-pool`
- assignment: `phase1-clean-open-source-chat-capability-patterns`
- enabled_desired: `true`
- clean semantic boundary: own role-local clean state + public sources + own sanitized feedback only

The second SHA-only head lookup matched the first before substantive semantic work. This run froze the tuple above and did not read O, other-worker/downstream state, shared aggregate ledger, other receipts/configs, or legacy/pre-independence research.

The preserved Argus/event-log continuation remains dormant restoration metadata while the Phase-1 overlay is active.

## Deliverables

1. `VERIFIER_20260829_0059_POLICY_TRI_STATE.py`
   - executable fail-closed evaluator;
   - accepts normalized evidence JSON;
   - emits per-family `PASS / BLOCKED / UNKNOWN` and overall `PROVED_READY / PROVED_BLOCKED / UNKNOWN`;
   - includes `--self-test`.
2. `POLICY_EVIDENCE_SCHEMA_20260829_0059.json`
   - JSON Schema for the normalized top-level candidate/policy-family envelope.
3. This checkpoint records the source semantics and exact continuation.

The verifier deliberately does **not** call GitHub. Collection and normalization are separate from evaluation. That separation makes missing capability explicit instead of silently converting an inaccessible endpoint into “clean”.

## Self-test result

The embedded `--self-test` suite was executed locally before persistence and all eight fixtures matched their precommitted outcomes:

| Fixture | Expected/observed |
|---|---|
| narrow generic one-approval review policy with complete evidence | `PROVED_READY` |
| required reviewer team but team-membership evidence missing | `UNKNOWN` |
| code-owner policy with 3001 changed files sourced only from REST PR-files | `UNKNOWN` |
| unattributed Copilot PR, extra-approval rule active, one configured approval + only one observed approval | `PROVED_BLOCKED` |
| stale-review dismissal with authoritative `REVIEW_REQUIRED` server review decision | `PROVED_BLOCKED` |
| another open PR sharing the same head has a blocking review | `PROVED_BLOCKED` |
| required deployment active but deployment endpoint/current-state evidence absent | `UNKNOWN` |
| merge queue required at pre-enqueue stage | `UNKNOWN` |

The useful acceptance criterion is not “green input gives READY”; it is “READY is impossible unless every requirement-dependent completeness axis is true.”

## New result 1: review-family client reconstruction has more hidden completeness axes than approval count

Current GitHub documentation makes the pull-request review family depend on combinations of:

- configured approval count;
- stale-review dismissal after diff/merge-base changes;
- code-owner approval;
- newest-reviewable-push approval by someone other than the pusher;
- review-thread resolution;
- beta required-reviewer teams with file-pattern applicability and minimum approvals;
- reviewer/team authorization;
- other open PRs that point at the same head commit and contain pending/rejected reviews;
- and, in the current public-preview rule set, an additional approval for unattributed Copilot-authored PRs when that setting applies.

Therefore a normalized review record that only carries `state=APPROVED` and `commit_id=head` is not enough for a general `PASS`.

The verifier reflects this by conditionally requiring completeness axes. For example:

- `dismiss_stale_reviews_on_push` requires an authoritative server-derived review decision (or an explicitly equivalent source) because merge-base/diff invalidation is not safely reconstructed from review rows alone;
- `require_code_owner_review` requires complete changed paths, base-branch CODEOWNERS source, and code-owner obligation resolution;
- `required_reviewers` requires changed paths, exact pattern semantics, team membership and team obligation resolution;
- `require_last_push_approval` requires the exact latest reviewable push and an independent approver;
- all review policies require complete enumeration of same-head open PR blocker state before `PASS`.

A definitive blocking row can still prove `BLOCKED` earlier; missing completeness never proves `PASS`.

## New result 2: required-reviewer pattern semantics are not safe to reimplement from one documentation surface

Two official GitHub documentation surfaces currently describe the beta required-reviewer file-pattern semantics differently:

- the ruleset prose describes the file pattern list as following standard `.gitignore`-style behavior, including negation/order semantics;
- the REST rules schema describes `file_patterns` as `fnmatch` syntax.

Until GitHub supplies one unambiguous normative matching contract or a server-derived “this team is required for this PR” result, a client should not claim a complete required-team mapping merely by picking one parser. The verifier therefore requires `required_reviewer_pattern_semantics=true`; otherwise the family is `UNKNOWN`.

This is distinct from CODEOWNERS matching. GitHub explicitly documents that CODEOWNERS syntax differs from `.gitignore`, and the CODEOWNERS file is taken from the PR **base branch**, searched in `.github/`, root, then `docs/`. Team owners must be visible and have write access. A CODEOWNERS file over 3 MB is not loaded.

## New result 3: “all pages fetched” is still not enough above the REST PR-files service cap

GitHub's REST “List pull request files” endpoint documents a maximum of **3000 files**. A connector wrapper can truthfully paginate every API page it is allowed to receive and still not have a complete changed-path set for a >3000-file PR.

Therefore:

- a `list_pr_changed_filenames`-style wrapper is a strong connected primitive for ordinary PRs;
- but `changed_paths_complete=true` must not be set above the underlying 3000-file cap unless another authoritative complete source is used;
- code-owner and file-pattern required-reviewer proofs must become `UNKNOWN` in that case.

The self-test contains this exact counterexample.

## Connected review surface observed this run

Read-only connector discovery/probes showed:

- raw REST PR reads are available and expose `mergeable_state`, but that field must not be treated as a complete replacement for the policy-family proof;
- normalized `get_pr_info` and raw REST can temporarily disagree on `mergeable` while GitHub computes mergeability, reinforcing that mergeability is asynchronous state rather than a strict evidence snapshot;
- raw REST review rows can expose `commit_id`;
- review-thread enumeration exposes resolved/outdated state and thread metadata;
- changed filenames have an all-pages wrapper;
- no connected team-membership read action was discovered;
- generic connector fetch excludes sensitive organization/user endpoint families, so required-team membership remains an exact missing surface in the inspected connector;
- generic GraphQL query access exposing PR `reviewDecision` / `mergeStateStatus` was not discovered.

GitHub GraphQL publicly defines `PullRequest.reviewDecision` as the current code-review status and `mergeStateStatus` as a detailed current merge status. If a future connected read surface exposes those fields with exact PR/head binding, they can replace several fragile client-side reconstruction steps, but they still do not by themselves prove unrelated rule families such as deployments or code scanning.

## Narrow review-family `PASS` subset in the current connector

The executable verifier intentionally permits `PASS` for a narrow simple policy when all of these are explicitly complete:

- policy inventory is complete;
- exact PR head is bound;
- review enumeration is complete;
- current reviewer authorization/permission is complete;
- same-head open PR blocker enumeration is complete and blocker absent;
- no stale-dismissal, code-owner, required-reviewer-team, last-push, thread-resolution or unknown Copilot-attribution dependency is active;
- current authorized approval count meets the configured count.

This is a **subset proof**, not a claim that every GitHub review policy is reconstructable.

## Required workflows: identity can be normalized more strongly than display name

The REST rules schema identifies required workflows using source identity including:

- `repository_id`,
- `path`,
- optional `ref`,
- optional `sha`.

Therefore the verifier requires `workflow_identity` completeness plus target-SHA/run pagination. A same-name successful run is not enough. If the required workflow is sourced from an inaccessible repository or the source identity cannot be correlated exactly, verdict remains `UNKNOWN`.

A future collector can promote required workflows to a narrow `PASS` subset when it can prove:

1. complete active workflow-rule inventory;
2. exact source `(repository_id, path, ref?, sha?)`;
3. exact candidate/merge-group target SHA;
4. complete Actions run enumeration for that target;
5. required trigger/event semantics; and
6. a completed successful run corresponding to the exact required source.

## Required deployments: public API shape is sufficient in principle, current connector is not

GitHub's public deployment API supports deployment filtering by exact SHA/ref and environment. Deployment status is a separate history; GitHub documents the most recent status as the current deployment state.

A safe deployment collector should therefore bind:

- required environment identity;
- exact candidate/merge-group SHA;
- exact deployment(s);
- authoritative current status for the relevant deployment.

It should not infer “current” merely from assumed list ordering.

The inspected connector still does not expose the deployment endpoint, so an active required-deployment rule remains `UNKNOWN` here even if every visible Check is green.

## Merge queue and async merge remain stage boundaries

The verifier is stage-aware:

- when merge queue is required and the document is `pre_enqueue`, the queue family is necessarily `UNKNOWN` because a later merge-group SHA/evidence stage has not happened;
- `post_enqueue` requires exact enqueue transaction, merge-group SHA and queue-state evidence before `PASS`.

Public `merge-async` remains a useful crash/retry benchmark:

| State | Durable evidence | Safe next action |
|---|---|---|
| `NOT_SUBMITTED` | exact PR head `H`, no accepted UUID known | submit once with `sha=H` and explicit merge action |
| `ACCEPTED_U` | 202 + UUID `U` | persist `U`, read result |
| `EXISTING_U_MATCH` | 409/existing UUID plus result proves same expected head/action | resume result read |
| `EXISTING_U_MISMATCH` | existing UUID but head/action differs | fail closed; do not reinterpret as idempotent success |
| `PENDING` | result `U` pending, expected head matches | read result again |
| `MERGED` | terminal success + merge commit OID / exact PR merged readback | commit transaction complete |
| `FAILED` | terminal failure reason | record failure; a new transaction requires a new deliberate decision |
| `EXPIRED_UNKNOWN` | result record older than retention/404 and durable PR/queue state cannot prove outcome | keep `UNKNOWN`; do not infer “never submitted” |

The result record expiry means loss of the async record is not an idempotency signal.

## Staged publication versus `updateRefs`

The previous conclusion is retained and made explicit as recovery policy:

| Mechanism | Atomic unit | Crash before commit point | Concurrent stale writer | Multi-object atomicity | Lease metadata |
|---|---|---|---|---|---|
| immutable payload(s) + one Contents pointer CAS | one pointer blob-SHA CAS | unreferenced immutable payload; readers remain on old pointer | pointer CAS rejects stale blob SHA | no, only one pointer commit point | easy to encode holder/epoch/expiry |
| GraphQL `updateRefs` | all requested refs | no partial ref update if mutation not committed | per-ref `beforeOid` rejects stale old OID | yes, within one repository/mutation | not built in |

For connected Chat workflows without generic GraphQL mutation, staged immutable publication is a practical durable pattern. For public capability benchmarking, `updateRefs` is a stronger multi-ref CAS primitive.

## Executable verdict contract

Overall result is:

- `PROVED_BLOCKED` if any applicable family has definitive blocking evidence;
- `PROVED_READY` only if every applicable family is `PASS`;
- `UNKNOWN` otherwise.

This is intentionally asymmetric: positive claims require complete evidence; negative claims can often be proven by one definitive blocker.

## Public sources

Official GitHub documentation inspected during this run:

- Rules available for rulesets:
  https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- REST rules schema:
  https://docs.github.com/en/rest/repos/rules
- About code owners:
  https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
- CODEOWNERS syntax:
  https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners#codeowners-syntax
- REST pull request files:
  https://docs.github.com/en/rest/pulls/pulls#list-pull-requests-files
- GraphQL PullRequest:
  https://docs.github.com/en/graphql/reference/objects#pullrequest
- REST deployments:
  https://docs.github.com/en/rest/deployments/deployments
- REST deployment statuses:
  https://docs.github.com/en/rest/deployments/statuses
- REST pull requests / async merge:
  https://docs.github.com/en/rest/pulls/pulls
- GraphQL Git/updateRefs:
  https://docs.github.com/en/graphql/reference/mutations#updaterefs

## Exact continuation

Fresh-bootstrap first. If the Phase-1 overlay remains active, keep preserved Argus work dormant and continue from this checkpoint.

Next nonempty frontier, in order:

1. Audit whether any **read-only connected** GitHub surface can expose authoritative `reviewDecision`, `mergeStateStatus`, effective required-reviewer obligations, or equivalent server-derived review-gate state with exact PR/head binding. Do not infer that raw REST `mergeable_state` is equivalent.
2. Find an official/public fixture for beta `required_reviewers` and test whether server behavior/documentation resolves the current `.gitignore` versus `fnmatch` description mismatch. If not resolvable, preserve `required_reviewer_pattern_semantics=false` as an explicit blocker to `PASS`.
3. Extend the executable verifier fixtures with a positive required-workflow identity case and, only if a connected deployment/current-status read becomes available, a positive required-deployment case. Keep current missing-endpoint fixture as negative control.
4. Then take the next non-conflicting Phase-1 capability leaf: audit the new public stacked-pull-request API/atomic merge workflow for Chat-capable exact-head, retry and durable-handoff semantics, comparing its server transaction boundary to `merge-async` and synchronous expected-head merge.
5. Preserve a nonempty Phase-1 frontier; do not restore the unrelated Argus base continuation merely because the current verifier leaf is complete.
