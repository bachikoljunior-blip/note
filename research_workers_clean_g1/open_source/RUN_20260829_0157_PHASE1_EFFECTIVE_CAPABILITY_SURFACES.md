# Open Source Phase-1: Effective Capability Surfaces and Fail-Closed Evidence

## Frozen semantic tuple

- note semantic base SHA: `91fdb502f413a8d9c660d339d04525aca5ce5100`
- root control revision: `20`
- open_source config revision: `6`
- phase: `phase_1_chat_parity`
- root: `o-chat-parity-root-v2-active-pool`
- assignment: `phase1-clean-open-source-chat-capability-patterns`

Only this role's clean state, the sanitized root/own config, public sources, and read-only connector capability discovery were used. No O/O-derived, other-worker, downstream, legacy, shared-ledger, or other-receipt semantics were read.

## 1. Verifier v2: raw policy keys and exact workflow identity

Persisted:

- `VERIFIER_20260829_0157_POLICY_TRI_STATE_V2.py`
- `POLICY_EVIDENCE_SCHEMA_20260829_0157.json`

The verifier remains fail-closed: incomplete evidence is `UNKNOWN`; `PROVED_READY` requires every supplied applicable policy family to pass.

### Review-policy revisions

The current public `github/docs` rulesets expose the raw pull-request parameter `require_extra_approval_for_unattributed_changes=true`. Verifier v2 consumes that raw key directly. If it is enabled and the PR is classified as `copilot_unattributed`, one additional authorized approval is required.

Current GitHub documentation says required-reviewer file patterns follow standard `.gitignore`-style ordered matching, including `!` negation. Therefore a collector that only claims ordinary `fnmatch` cannot prove required-reviewer path obligations when `file_patterns` are configured. Verifier v2 requires the evidence marker `required_reviewer_pattern_engine=ordered_gitignore_negation`; otherwise the family is `UNKNOWN`.

The embedded acceptance oracle is intentionally narrow rather than a production parser: `*.sql` matches `prod/query.sql`, while later `!test/*.sql` excludes `test/query.sql`.

Official/public evidence:

- https://github.blog/changelog/2026-02-17-required-reviewer-rule-is-now-generally-available/
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- `GET https://api.github.com/repos/github/docs/rulesets/880450`
- `GET https://api.github.com/repos/github/docs/rulesets/1072968`

### Required-workflow identity boundary

A required-workflow rule identifies a source workflow by `repository_id`, `path`, and optional `ref`/`sha`. Verifier v2 therefore does not accept same-name or same-path success alone. A successful run must be bound to the exact target head SHA and the exact required source tuple.

The connected read surface can enumerate ordinary Actions runs at an exact target `head_sha` and exposes run fields including target `head_sha`, run `path`, `workflow_id`, status and conclusion. In this run, a public `github/docs` exact-head query at `6e9b187def89fe6bac93dbc4eeeb2e53bce33004` returned such run evidence. However, no live public required-workflow execution was found whose response proves the central required-workflow **source repository** tuple from the ruleset. Thus the synthetic exact-identity positive fixture is valid as a verifier contract, but live connected readiness for this family remains `UNKNOWN` until source identity is demonstrated.

Official evidence:

- https://docs.github.com/en/rest/repos/rules
- https://docs.github.com/en/rest/actions/workflow-runs

### Verifier v2 self-tests

All precommitted fixtures passed locally before persistence:

- raw Copilot key + one approval -> `PROVED_BLOCKED`
- bare-fnmatch required-reviewer collector -> `UNKNOWN`
- ordered-negation collector with complete narrow evidence -> `PROVED_READY`
- exact required-workflow source identity + exact target SHA + success -> `PROVED_READY`
- same path but wrong source repository -> `PROVED_BLOCKED`

## 2. Stacked-PR intent state machine

Persisted `STACK_INTENT_MACHINE_20260829_0157.py`, continuing the earlier durable stack-intent schema.

GitHub's public stacked-PR API is currently public preview. The stack merge API is asynchronous and mandatory for stacks; legacy synchronous merge cannot substitute. The async request's `sha` binds the requested PR head, but does not provide an expected-head vector for every lower stack member. Therefore the client must persist and re-read the full ordered member/head/direct-base snapshot separately from the requested top SHA.

The state machine fails closed across:

- exact stack snapshot -> `READY_TO_SUBMIT`
- lower-member head drift while top head is unchanged -> `CONFLICT`
- ambiguous submit with matching recoverable request identity -> `RESUME`
- mismatching recovered request -> `CONFLICT`
- queued large stack represented by multiple ordered merge groups -> accepted only when flattened membership exactly equals the intended contiguous bottom-through-requested group
- result missing after the documented retention window -> `EXPIRED_UNKNOWN`; 404 is not evidence that no request existed

All six embedded self-tests passed locally before persistence.

Official evidence:

- https://docs.github.com/en/pull-requests/reference/stacked-pull-requests-apis-and-webhooks
- https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests
- https://docs.github.com/en/rest/pulls/stacks

The current stack REST examples explicitly send `X-GitHub-Api-Version: 2026-03-10`. Connected discovery in this run found no stack-specific action, no async-merge action, and no API-version-selection action; generic GitHub fetch exposes only a URL argument and cannot set that version header. Therefore public GitHub has the stack capability, while the inspected connected Chat surface still lacks the exact operation/version surface needed to claim parity.

## 3. New cross-system capability-detection pattern: effective enumeration beats declared configuration

### GitHub MCP Server

At public commit `febc3293a4feb70e62399f39a26b082f78b9b176`, GitHub MCP Server documents several precedence layers:

- explicitly excluded tools are removed from an enabled toolset;
- read-only mode disables non-read-only tools even if requested;
- lockdown is only a best-effort content filter and explicitly **not** an authorization boundary.

Its scope-filtering documentation adds a more important caveat: classic PATs can hide tools at startup using `X-OAuth-Scopes`, but fine-grained PATs, GitHub App tokens and server-to-server tokens show tools and let the GitHub API enforce permissions. If scope discovery itself fails, the server logs a warning and continues **without filtering**. Therefore tool visibility is not equivalent to authorization in all authentication modes.

Official repository evidence:

- https://github.com/github/github-mcp-server/blob/febc3293a4feb70e62399f39a26b082f78b9b176/docs/server-configuration.md
- https://github.com/github/github-mcp-server/blob/febc3293a4feb70e62399f39a26b082f78b9b176/docs/scope-filtering.md

Safe generic rule: capability detection must use the **effective runtime tool enumeration after configuration precedence**, while separately classifying whether visibility is authoritative for the active authentication mode. A visible tool may still fail authorization; an absent tool may reflect mode/filter/scope rather than platform absence.

### Kubernetes MCP Server

At public commit `4568a4fa6668e9af9df0d5fd8366f3859a7961e5`, Kubernetes MCP Server makes the same distinction explicit in another implementation:

- `read_only=true` exposes only tools annotated `readOnlyHint=true`;
- `disable_destructive=true` removes tools annotated `destructiveHint=true`, but is subordinate to read-only mode;
- `enabled_tools` is an allowlist and `disabled_tools` is applied afterward;
- experimental target-compatibility filtering can hide tools when required cluster APIs are absent.

It also supports SIGHUP configuration reload that rebuilds the toolset registry. Separately, `stateless=true` disables tool and prompt change notifications. The combination creates a concrete stale-capability hazard: configuration may change the effective tool registry while a stateless client receives no tool-change notification. A safe Chat executor must therefore re-enumerate effective tools at an appropriate pre-action boundary rather than assuming a startup capability snapshot is durable.

Official repository evidence:

- https://github.com/containers/kubernetes-mcp-server/blob/4568a4fa6668e9af9df0d5fd8366f3859a7961e5/docs/configuration.md

This is exact to these documented modes; it is not a claim that every MCP server dynamically reloads configuration or filters capabilities in the same way.

## 4. Connected review aggregate boundary remains

Public GitHub GraphQL exposes `PullRequest.reviewDecision` and `mergeStateStatus`, but connected discovery still exposes only normalized PR/review/thread actions rather than a generic GraphQL query or a dedicated aggregate action. The inspected `get_pr_info` result does not include either aggregate. Therefore client-side reconstruction remains necessary where possible, and server aggregate evidence stays an exact missing surface rather than being silently inferred.

## Exact continuation / nonempty Phase-1 frontier

1. Find a public live required-workflow ruleset + execution where the source workflow tuple can be bound end-to-end to target-head run evidence; if the public API response does not expose that provenance, record the precise missing endpoint/field and keep the family `UNKNOWN`.
2. Turn the GitHub-MCP/Kubernetes-MCP observations into a small reusable capability-fingerprint contract: effective `tools/list`, active safety mode, auth-mode visibility semantics, change-notification availability, and an explicit `authorization_unproven` state.
3. Test the stale-capability counterexample: dynamic registry change + absent tool-change notification must force pre-mutation re-enumeration rather than trusting a cached tool list.
4. Revisit GitHub stack parity only if a connected stack/async-merge/API-version surface becomes discoverable; do not count synchronous merge or auto-merge as substitutes.
5. Preserve the unrelated Argus continuation dormant while the Phase-1 overlay remains active.
