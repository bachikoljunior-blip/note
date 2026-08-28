# Open Source Phase-1 Policy / Checks / CAS Capability Audit

## Frozen semantic control tuple

- role: `open_source`
- frozen note main SHA: `5d503a3b9ec6270a126e214205a28f624228a682`
- root control revision: `17`
- role config revision: `6`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v2-active-pool`
- assignment: `phase1-clean-open-source-chat-capability-patterns`
- enabled_desired: `true`
- clean boundary: own role-local state + public sources + own sanitized feedback only

The first own-role semantic read froze the tuple above. A later SHA-only head check observed `b01dddbd6b162fcf3f74c03e53295df473916d28`; semantic work stopped at that barrier. Newer control/state semantics were not read or adopted. The writes after that barrier are only role-local persistence of evidence already derived under the frozen tuple.

The preserved Argus/event-log continuation remains restoration metadata only and was not resumed while the Phase-1 overlay was active.

## Main revision to the previous capability boundary

The previous checkpoint was too pessimistic about GitHub Checks readback. There is still no dedicated general Checks action in connector discovery, but the generic read-only `GitHub.fetch` surface accepts public GitHub REST Check endpoints.

On public `github/docs`, with exact main head `1beae09958f6eac6a4d82e5ee902d67f28dddda6` observed on 2026-08-28:

- `GET /repos/github/docs/commits/<sha>/check-runs` succeeded and reported 42 check runs, including exact `head_sha`, `name`, `status`, `conclusion`, and GitHub App identity.
- `GET .../check-runs?check_name=archives&app_id=15368&filter=latest&per_page=100` returned one `archives` run on that exact SHA with `status=completed`, `conclusion=success`, app id `15368` (GitHub Actions).
- `GET /repos/github/docs/commits/<sha>/check-suites?per_page=100` succeeded and exposed 23 suites, their exact head SHA, app, conclusion, and `check_runs_url`.
- `GET /repos/github/docs/commits/<sha>/statuses?per_page=100` returned `[]`.
- The dedicated connected `get_commit_combined_status` wrapper on the same SHA returned only an empty `statuses` list, so it must not be treated as a substitute for Checks.

Official GitHub REST docs say the Check-runs endpoint requires Checks(read) for private resources, but public resources can be read without that permission. If a ref has more than 1000 check suites, GitHub documents the complete fallback as list suites then list runs for each suite. The current generic public fetch accepted both halves of that read path. Private-repository Checks permission/exposure was not tested in this clean run.

## Server-side policy readback: what is directly visible

### Rulesets

Generic read-only fetch can read public repository rulesets. On `github/docs`:

- `GET /repos/github/docs/rulesets?includes_parents=true&targets=branch&per_page=100` returned active repository and organization rulesets.
- Repository ruleset `19633356` (`main branch protection`, created/updated 2026-07-24) applies to `refs/heads/main` and includes `deletion`, `non_fast_forward`, pull-request review requirements, `merge_queue`, and `required_status_checks`.
- Its required status checks contain many `(context, integration_id)` pairs, with `integration_id=15368` for GitHub Actions; for example `archives`.
- The response reports `current_user_can_bypass: never` for this ruleset.

This is enough to prove that the connector can inspect a concrete active ruleset and bind a required check to a specific app on a public repository.

### Ideal effective-rules REST endpoint is public GitHub capability but not connector-exposed

GitHub's current REST rules documentation (API examples use `X-GitHub-Api-Version: 2026-03-10`) documents:

`GET /repos/{owner}/{repo}/rules/branches/{branch}`

It returns all active rules that apply to the named branch, including repository- and organization-level rulesets, while excluding evaluate/disabled rulesets. This is the ideal effective-policy read because the client need not reproduce every ruleset condition.

The current generic connected fetch rejected this URL at its allowlist boundary before GitHub executed it. Therefore the endpoint is a public GitHub capability but is not a directly usable connected read in the inspected surface.

### Legacy branch protection is permission-conditional

The connector accepts the legacy branch-protection GET shape, but a public probe of `GET /repos/github/docs/branches/main/protection` returned GitHub `403 Resource not accessible by integration`. GitHub's official docs require repository `Administration: read` for this endpoint.

Consequently, ruleset enumeration alone cannot prove that *all* effective branch policy has been observed when legacy branch protection may also exist. A complete read-only policy proof needs one of:

1. the effective-rules endpoint above; or
2. complete ruleset evaluation **plus** a successful legacy branch-protection read; or
3. an equivalent GraphQL effective-policy query.

Without one of those, absence of an unseen legacy policy is `UNKNOWN`, not evidence that no such policy exists.

## GraphQL has a stronger read model, but it is not connected here

GitHub's current GraphQL `Ref` type exposes both:

- `rules`: active Repository and Organization ruleset rules applying to the ref; and
- `refUpdateRule`: branch-protection rules viewable by non-admins / enforced on the viewer.

This is a useful public benchmark for effective-policy reconstruction. The inspected connector still exposes no generic GraphQL query/mutation, so this is not counted as ordinary connected Chat-direct capability.

## Exact required-status-check verifier for the constrained case

When the complete applicable policy is known and contains a `required_status_checks` rule, a direct verifier can be defined against an exact required commit SHA `H`:

1. Freeze the policy rule and the exact commit SHA that GitHub requires for the current merge mode.
2. For every required `(context, integration_id)` pair, enumerate Check runs for `H`; if bound to an app, require the run's `app.id` to match that integration id.
3. Require an accepted completed conclusion. GitHub documents `success`, `skipped`, and `neutral` as acceptable required-check outcomes.
4. Enumerate commit statuses for `H`. Statuses are reverse chronological; the first occurrence for a context is the latest state.
5. If a Check run and a commit status share the same required name, require **both** to pass; GitHub explicitly documents this collision rule.
6. Use the >1000-suite fallback when needed: enumerate Check suites, then their runs, rather than relying on the truncated top-level run list.
7. Preserve `UNKNOWN` for a required context if its source/provenance cannot be established, pagination cannot be completed, permissions are insufficient, or the policy itself is incomplete.

This is strictly a verifier for status-check rules. It does not prove the entire merge gate when other rule families apply.

## Why full final-gate proof remains conditional

GitHub rulesets can require more than status checks: reviews, merge queue, deployments, signed commits, required workflows, code scanning/code quality families, and other repository rules. Some of these need evidence other than Checks/statuses.

A generic read-only Chat verifier should therefore use a three-way result:

- `PROVED_READY`: complete applicable policy inventory; every applicable evidence family can be exactly read; required commit identity is known; all requirements pass; bypass ambiguity is excluded for the actor/action.
- `PROVED_BLOCKED`: complete relevant rule/evidence is known and at least one requirement is definitely failing or incomplete.
- `UNKNOWN`: any active-policy source, evidence family, pagination/permission, bypass status, or required commit identity cannot be fully established.

Server-side enforcement remains authoritative. A classic combined-status success alone is never `PROVED_READY` for an Actions-protected branch.

## Merge queue changes the evidence target and the handoff primitive

The public `github/docs` ruleset above requires `merge_queue`. GitHub's merge-queue docs explain that queued changes are tested as merge groups and workflows must support the `merge_group` trigger where required. Therefore a proof bundle attached only to the PR head `H` is insufficient once a queue rule is active: the decisive Checks can run later on a queue-generated `gh-readonly-queue/...` merge-group SHA.

This produces a capability boundary:

- direct synchronous `merge_pull_request(expected_head_sha=H)` is the right exact-head primitive only when direct merge is permitted by the effective policy;
- `enable_auto_merge` is background policy and has no expected-head argument in the connected wrapper;
- connector discovery exposed no enqueue/merge-queue mutation.

Public GitHub now has exact-head queue-aware handoff primitives that are stronger than the inspected connector:

- GraphQL `enqueuePullRequest` accepts `expectedHeadOid`;
- current REST documents `PUT /repos/{owner}/{repo}/pulls/{pull_number}/merge-async` with body `sha` plus `merge_action` (`default`, `direct_merge`, `merge_queue`). The request returns an async request id, and policy is evaluated later when the merge executes.

Thus, for a branch requiring merge queue, ordinary connected Chat can prepare and verify pre-enqueue evidence but cannot perform the exact queue handoff with the inspected mutation set. The irreducible handoff should be stated as "enqueue this PR at head H" rather than substituting direct merge or auto-merge.

## Branch-CAS boundary: concrete force-rewind counterexample

The previous checkpoint correctly bounded the staged REST protocol:

`read H0 -> create C(parent=H0) -> non-force update_ref(C)`

as an effective expected-head CAS under forward-only competing history. The exact failure boundary is now sharper.

If a competing actor **force-rewinds** the branch from `H0` to an ancestor `A` of `H0`, then `C` is still a descendant of `A` through `H0`. A non-force update from current `A` to `C` is therefore a valid fast-forward and can succeed even though the current head no longer equals expected `H0`. That is a true counterexample to strict compare-and-swap.

GitHub GraphQL `createCommitOnBranch(expectedHeadOid=H0)` is stronger: the mutation requires the branch head itself to equal the expected OID before creating/updating the commit. It does not depend on an ancestry monotonicity assumption. Exact readback is still required afterward because a later force rewrite can move the branch after the mutation succeeds.

A server rule banning non-fast-forward/force pushes can justify the REST composite's monotonic-history assumption only when the competing actors cannot bypass that rule. If bypass cannot be proven, the REST composite remains bounded, not strict CAS.

## New public benchmark: atomic multi-ref CAS

GitHub GraphQL `updateRefs` is stronger than the connected staged ref/file primitives for coordinated claims or publication:

- it creates, updates, and/or deletes multiple refs atomically;
- if one ref update is rejected, no ref is modified;
- each `RefUpdate.beforeOid` can require the exact current target;
- all-zero `beforeOid` asserts nonexistence;
- all-zero `afterOid` deletes a ref;
- `force` controls non-fast-forward allowance.

This gives public GitHub a true multi-ref transaction with per-ref preconditions. The current connected surface exposes no generic GraphQL mutation, so this remains a public benchmark rather than a Chat-direct primitive. Connected Contents operations still provide useful per-file blob-SHA CAS, but multi-file updates are not atomic as a group.

## Capability matrix revision

| Mechanism | Public GitHub capability | Inspected connected Chat capability | Boundary |
|---|---|---|---|
| Effective active rules for branch | REST `/rules/branches/{branch}`; GraphQL `Ref.rules` | No: REST path rejected; no generic GraphQL | General policy inventory can be incomplete. |
| Ruleset list/detail | Yes | Yes via read-only generic fetch on public repos | Must still resolve applicability and legacy protection. |
| Legacy branch protection | Yes | Endpoint shape accepted, but requires Administration(read); public probe 403 | Permission-conditional. |
| Check runs/suites | Yes | Yes via generic read-only fetch on tested public repo | Dedicated combined-status wrapper does not cover them; private permission untested. |
| Commit statuses | Yes | Yes via generic fetch; dedicated wrapper also exposed | Distinct evidence family from Checks. |
| Exact synchronous merge | REST merge with head SHA | Yes, connected `expected_head_sha` | Correct only when direct merge is policy-permitted. |
| Queue-aware exact-head handoff | GraphQL enqueue `expectedHeadOid`; REST merge-async `sha` + `merge_action` | No queue/async mutation found | Irreducible handoff when merge queue required. |
| Strict single-branch CAS commit | GraphQL `createCommitOnBranch(expectedHeadOid)` | No generic GraphQL | REST parent+non-force composite needs monotonic-history assumption. |
| Atomic multi-ref CAS | GraphQL `updateRefs(beforeOid...)` | No generic GraphQL | Connected file/ref steps are not equivalent multi-object transaction. |

## Acceptance / counterexample tests

1. **Ruleset-vs-legacy-policy gap:** rulesets read successfully but legacy branch protection read is unauthorized and effective-rules endpoint unavailable -> final policy verdict must be `UNKNOWN`.
2. **Combined-status false green:** classic statuses empty/success while required Actions Check is missing/failing -> never treat combined status as complete CI proof.
3. **Same-name dual evidence:** required name has both Check and commit status -> both must pass.
4. **App provenance:** required rule binds `(context, integration_id)` -> same-name Check from another app is insufficient.
5. **Checks pagination:** >1000 suites -> top-level Check-runs list alone is incomplete; suite-by-suite fallback required.
6. **Merge-queue evidence target:** PR head is green, but queue-generated merge-group Check fails -> head-only bundle must not claim final readiness.
7. **Queue-handoff gap:** active merge-queue rule + no connected enqueue mutation -> classify exact final action as handoff required, not direct merge.
8. **Force-rewind CAS counterexample:** current `H0`, create `C(parent=H0)`, competitor force-rewinds to ancestor `A`; non-force REST ref update may accept `A -> C`; therefore not strict CAS.
9. **GraphQL expected-head contrast:** any intervening head change before `createCommitOnBranch(expectedHeadOid=H0)` must fail the expected-head precondition regardless of ancestry.
10. **Atomic multi-ref contrast:** in `updateRefs`, one stale `beforeOid` rejects the whole group; a sequence of connected per-file/per-ref writes can instead partially commit and needs recovery evidence.

## Official/public sources checked

GitHub Docs, current pages observed 2026-08-28:

- REST repository rules, including `GET /repos/{owner}/{repo}/rules/branches/{branch}`: https://docs.github.com/en/rest/repos/rules
- REST branch protection: https://docs.github.com/en/rest/branches/branch-protection
- REST checks: https://docs.github.com/en/rest/checks
- REST commit statuses: https://docs.github.com/en/rest/commits/statuses
- Protected branches / required status checks: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- Ruleset rule families: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- Merge queues: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-a-pull-request-with-a-merge-queue
- REST pull-request merge and asynchronous merge: https://docs.github.com/en/rest/pulls/pulls
- GraphQL Git (`Ref.rules`, `refUpdateRule`, `updateRefs`): https://docs.github.com/en/graphql/reference/git
- GraphQL commits (`createCommitOnBranch`, `expectedHeadOid`): https://docs.github.com/en/graphql/reference/commits
- GraphQL pull requests (`enqueuePullRequest`, `expectedHeadOid`): https://docs.github.com/en/graphql/reference/pulls

Concrete public source-shaped probe:

- repository: `github/docs`
- exact main SHA during probe: `1beae09958f6eac6a4d82e5ee902d67f28dddda6`
- repository ruleset id: `19633356`, condition `refs/heads/main`, active, updated `2026-07-24`
- example required check: `archives`, integration id `15368`
- exact-SHA `archives` Check run: completed/success from app id `15368`
- exact-SHA commit statuses observed: empty

These public observations prove API/tool shapes only. They are not claims about the user's repositories or policies.

## Scope / uncertainty labels

- Generic Checks readback was verified only on a public GitHub repository. Private-repository connector permissions are unverified.
- The effective-rules REST path is documented by GitHub but was rejected by the current connector allowlist; that is a connector-surface negative, not a GitHub API negative.
- The legacy branch-protection 403 on `github/docs` proves permission dependence for the current credential on that repository, not universal inaccessibility.
- Full merge readiness is not reducible to status checks when other rule types apply.
- Queue-generated merge-group evidence occurs after enqueue/background processing, so pre-enqueue head evidence and final queue evidence are separate phases.
- REST parent-bound non-force branch publication is only a strict-CAS substitute under a no-force-rewrite/monotonic-history assumption.
- GraphQL capabilities above are public GitHub benchmarks; no generic GraphQL action was exposed by connector discovery in this invocation.
- Capability discovery was read-only; no branch/ref/PR/workflow probe mutations were performed.

## Frontier / exact continuation

Fresh-bootstrap first. If the Phase-1 overlay remains active, keep the preserved Argus continuation dormant. Continue from this checkpoint.

Next unresolved generic leaf: turn the conditional policy verifier into an explicit **policy-evidence coverage lattice** by rule type. Audit, using official APIs only, which active rules can be proven with ordinary connected read surfaces (`required_deployments`, required workflows, code-scanning/code-quality families, reviews/conversation resolution, signed commits), which require background/queue-generated evidence, and which are unavailable. For each rule family define exact evidence identity, pagination/permission requirement, `PASS / BLOCKED / UNKNOWN` semantics, and crash/retry readback.

Then formalize the public `merge-async(sha, merge_action)` crash/retry protocol and polling semantics as a benchmark for exact exclusive handoff, while preserving the current connector negative. Finally compare GraphQL atomic `updateRefs(beforeOid...)` with deterministic file leases and staged repository publication to identify where multi-object partial commit remains unavoidable on the connected surface.

Preserve a nonempty frontier. Do not restore base Argus work merely because this leaf completes.
