# Open Source Phase-1 Policy Evidence Lattice

## Frozen semantic tuple

- role: `open_source`
- frozen note main SHA: `2d54ae64052110587595e13484f464efed1bfed0`
- root control revision: `18`
- role config revision: `6`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v2-active-pool`
- assignment: `phase1-clean-open-source-chat-capability-patterns`
- enabled_desired: `true`
- clean boundary: own role-local state + public sources + own sanitized feedback only

The preserved Argus/event-log continuation remains restoration metadata and was not resumed while the Phase-1 overlay was active.

The semantic tuple froze after the root manifest, own role config, and second SHA-only head check all resolved at `2d54ae64052110587595e13484f464efed1bfed0`. After the evidence below was derived, a SHA-only head check observed `ee248ff4464d0950316452847ac5ddbafd17f966`; semantic work stopped at that barrier. No newer control semantics were read or adopted. Writes after the barrier are only role-local persistence of evidence already derived under the frozen tuple.

## Main result: final-gate proof is a policy-family lattice, not one CI boolean

A Chat-direct verifier can prove some GitHub gate families from exact objects, but several active rule families remain unavailable or only partially reconstructable through the inspected connector. Therefore final readiness must remain tri-state:

- `PROVED_READY`: complete applicable policy inventory + every active family has complete, exact, permission- and pagination-complete evidence bound to the correct candidate SHA/stage + no unresolved bypass ambiguity.
- `PROVED_BLOCKED`: a known active requirement has definitive failing/blocking evidence.
- `UNKNOWN`: any active policy family, evidence source, required identity/SHA, pagination/permission boundary, queue-stage evidence, or bypass state cannot be fully established.

Server-side GitHub enforcement remains authoritative. A green combined status or green PR-head Checks bundle is not by itself a complete final-gate proof.

## Policy/evidence coverage lattice

| Rule family | Policy object / identity | Evidence target | Connected read capability observed | PASS / BLOCKED / UNKNOWN boundary | Stage |
|---|---|---|---|---|---|
| Required status checks | ruleset `required_status_checks[]` with `(context, integration_id)` and strictness | Check runs + commit statuses on exact required SHA | Generic read-only GitHub fetch can read check-runs/check-suites/statuses. Dedicated combined-status wrapper covers classic statuses only. | PASS only after complete enumeration and exact app provenance; if same name exists as Check and status, both must pass. Any pagination/provenance/policy gap => UNKNOWN. | PR-head pre-enqueue; merge-group SHA after queue if queue required. |
| Required workflows | ruleset workflow source identity: source repository/workflow path/ref/SHA where exposed | Actions workflow run on exact candidate SHA and required event | Generic fetch of `/actions/runs?head_sha=H&per_page=100` succeeded on public `github/docs` and exposes `head_sha`, workflow path/id, event, status, conclusion. Dedicated commit-run wrapper is weaker: PR-triggered and first page only. | PASS only if ruleset workflow identity can be unambiguously correlated to a completed successful run and all pages are read. External-source workflow identity or inaccessible source => UNKNOWN. | PR-head pre-enqueue; `merge_group` run on generated merge-group SHA when queue is used. |
| Required deployments | ruleset `required_deployments` names required environments | deployment for exact candidate ref/SHA + latest deployment status for each required environment | No dedicated deployment read action discovered. Generic fetch rejected public `/deployments?...` at connector allowlist. Public REST itself supports deployments by ref/SHA/environment and deployment statuses. | Active rule is UNKNOWN in the inspected connected surface unless equivalent authoritative evidence is exposed elsewhere. A deployment for another SHA/environment is not sufficient. | Typically candidate/merge gate evidence; exact queue interaction must not be inferred without source. |
| Pull-request reviews | ruleset pull-request parameters: approval count, stale dismissal, code-owner review, last-push approval, required teams/file patterns, conversation resolution | PR review submissions, exact `commit_id`, reviewer authorization/team/code-owner applicability, latest push/diff state, review threads | Dedicated review list works but normalized result omitted `commit_id`; generic `/pulls/{n}/reviews?per_page=100` exposed exact `commit_id`. Dedicated review-thread list exposes resolved state. Collaborator-permission read exists. | BLOCKED can be proved from explicit blocking review/unresolved required thread. READY is only safe in a narrow fully enumerable configuration. Code-owner/team membership, stale-review/merge-base behavior, other PRs sharing same commit, completeness of thread pagination, or latest-push ambiguity => UNKNOWN. | Mostly PR-head/pre-enqueue, but approvals can stale as merge base changes. |
| Signed commits | `required_signatures` | every commit in the exact branch-update range; each commit's GitHub verification result | Generic exact commit REST fetch exposes `commit.verification`; normalized `fetch_commit` omitted that field in the tested public fixture. | PASS requires complete exact commit range and verified signatures under GitHub's rule semantics. Checking only the head is insufficient. Future server-generated merge/squash commit semantics can keep final proof UNKNOWN. | Pre-enqueue for known commits; server-generated final commit may be later. |
| Code scanning | ruleset `code_scanning_tools[]` with tool and severity thresholds | tool analysis + alerts for exact ref/PR | Public REST supports repository alerts/analyses filtered by tool and ref/PR with pagination and requires Code scanning alerts(read). Generic connector fetch rejected `/code-scanning/alerts`; no dedicated scanning read action discovered. | Active code-scanning rule => UNKNOWN in inspected connected surface. Public API could support a stronger verifier if exposed. | Candidate SHA/PR evidence; queue-stage exact target must be established. |
| Code quality | ruleset code-quality thresholds | code-quality analysis/findings for the candidate plus threshold semantics | Public REST has code-quality findings with Code quality(read), but generic connector fetch rejected `/code-quality/findings`; no dedicated code-quality action discovered. Current public findings docs do not expose the same exact ref/PR filter model as code scanning. | Active code-quality rule => UNKNOWN through inspected connected surface. A successful `CodeQL - Code Quality` run proves execution, not automatically a full client-side threshold proof unless GitHub documents/returns gate-equivalent state. | PR/candidate; server enforcement authoritative. |
| Code coverage (transversal newly observed family) | ruleset coverage thresholds: minimum line coverage / maximum drop | coverage result for PR branch relative to default branch | No dedicated coverage/code-quality read action discovered in inspected surface. Public docs describe the rule as preview and server-enforced. | Active coverage rule => UNKNOWN unless exact rule-bound coverage evidence becomes readable. | PR/candidate. |
| Merge queue | ruleset `merge_queue` parameters and merge action | queue-generated merge-group SHA plus Checks/workflows on that SHA | Read-only Checks/Actions can inspect a known SHA, but no queue/enqueue/async-merge mutation was discovered. Connector search for `queue` returned no action; `merge` exposed synchronous merge and auto-merge only. | PR-head green is never final READY when queue required. Queue handoff and merge-group evidence are a distinct stage; without exact enqueue capability/final merge-group proof => UNKNOWN/handoff required. | Post-enqueue/background. |

## Concrete public read probes in this run

Public fixture: `github/docs`, exact main SHA `1beae09958f6eac6a4d82e5ee902d67f28dddda6`.

1. `GET /repos/github/docs/actions/runs?head_sha=<H>&per_page=100` succeeded and returned 19 workflow runs with exact `head_sha`, workflow path/id, event, status and conclusion. This shows generic fetch is more useful for exact-SHA workflow evidence than the dedicated first-page PR-only commit-run wrapper.
2. `GET /repos/github/docs/deployments?sha=<H>&per_page=100` was rejected by the connector allowlist before GitHub execution. No dedicated deployment action was discovered.
3. `GET /repos/github/docs/code-scanning/alerts?ref=<H>&per_page=100` was rejected by the connector allowlist. No dedicated code-scanning action was discovered.
4. `GET /repos/github/docs/code-quality/findings?per_page=100` was rejected by the connector allowlist. No dedicated code-quality action was discovered.
5. Public PR `github/docs#44466` had head `8de09dde9df866b758749bf06fb4d82b6c4ae2dd`. The dedicated review wrapper returned a COMMENTED review but not its commit binding; raw public REST review enumeration exposed `commit_id=8de09dde...`. Review-thread enumeration was available and returned no threads for that fixture.
6. Raw exact-commit REST for `github/docs@1beae099...` exposed `commit.verification.verified=true`, `reason=valid`, and a verification timestamp. The normalized commit wrapper did not expose this verification field.
7. Repository ruleset `19633356` remained active for `refs/heads/main` and concretely contains pull-request review rules, merge queue (`SQUASH`, `ALLGREEN`), and app-bound required status checks. Its review rule requires one approval, stale-review dismissal and code-owner review. This is a source-shaped reminder that review readiness cannot be reduced to counting APPROVED rows.

These public probes establish API/tool shapes only. They are not claims about any user repository.

## Public GitHub semantics used for the lattice

Current GitHub documentation observed 2026-08-28/29 states:

- required deployments require successful deployment to named environments before merge;
- required signed commits verify all commits in the specified branch-update range, not only the tip;
- review rules can require approvals, code owners, newest-push approval, stale-review dismissal and conversation resolution, with merge-base changes able to stale approvals;
- required workflows support `pull_request`, `pull_request_target`, and `merge_group`; merge-queue use requires the `merge_group` trigger;
- code-scanning rules block for threshold alerts, in-progress analysis, or missing required tool;
- code-quality rules block for in-progress/failed analysis or findings at/above threshold;
- code-coverage threshold rules are currently a public-preview family;
- public deployment REST models deployments against a ref (including SHA) and environment, with separate deployment statuses;
- public code-scanning REST supports tool/ref/PR filters and pagination;
- public code-quality REST provides findings and requires Code quality(read).

## Asynchronous merge: crash/retry protocol benchmark

Public GitHub REST now documents `PUT /repos/{owner}/{repo}/pulls/{pull_number}/merge-async` plus a result endpoint. This is a useful exact-head handoff benchmark even though the inspected connector exposes no async/queue mutation.

Protocol:

1. Read PR state and freeze exact head `H`; determine intended `merge_action` from complete policy. Never omit `sha`.
2. Submit async merge with `sha=H` and explicit `merge_action` (`default`, `direct_merge`, or `merge_queue`).
3. On `202`, persist returned UUID `U` immediately.
4. On `409`, GitHub returns the UUID of an existing async request for the PR, but explicitly warns its options may differ. Treat this as ambiguous recovery, not success: read result `U` and verify its expected head SHA/method/action match the intended transaction before relying on it.
5. On `200` immediate already-merged/already-queued outcome, perform exact PR/merge readback and record resulting commit/queue state.
6. On transport ambiguity after submission, recover by reading current PR state and reissuing the same exact-head request only as a way to recover the existing UUID; then verify the returned existing request. Never blind-retry with a changed head or different action.
7. Poll `GET .../merge-async/{U}`. While pending, it reports UUID/method/expected head SHA; terminal success reports merge commit OID, terminal failure reports reason.
8. Result records expire 24 hours after their latest update. A later `404` is therefore not proof the request never existed. Reconstruct from exact PR merged state/queue state/head and preserve UNKNOWN if the old outcome cannot be established; do not create a new transaction solely because the result record expired.

The public endpoint evaluates only basic PR state at request creation; branch/ruleset policy is evaluated later in the background. Therefore `202` is acceptance of an async transaction, not proof of merge readiness or completion.

## Atomic multi-ref CAS versus connected file leases

GitHub GraphQL `updateRefs` is a stronger public benchmark for coordinated claims/publication than the connected per-object surfaces:

- multiple ref create/update/delete operations are atomic;
- each `beforeOid` can require exact old value;
- all-zero `beforeOid` asserts nonexistence;
- all-zero `afterOid` deletes a ref;
- one rejected operation leaves every ref unchanged.

Connected Contents operations instead provide per-file blob-SHA CAS. A deterministic lease file can carry holder/epoch/expiry metadata and supports inspectable stale-reclaim logic, but multiple files cannot be acquired atomically. A safer staged-publication pattern is: create immutable payload(s) first, then CAS one mutable pointer file as the commit point; a crash before pointer update leaves harmless unreferenced payload, while a successful pointer CAS gives a single exact readback target. Multi-ref `updateRefs` can atomically coordinate several claim/publication refs but has no built-in lease expiry metadata and remains one-repository GraphQL capability. Generic GraphQL mutation is not exposed by the inspected connector.

## Acceptance / counterexample fixtures added

1. Active required deployment + no deployment read surface => final verdict `UNKNOWN`, not READY from green Checks.
2. Required workflow sourced externally + run identity cannot be correlated exactly => `UNKNOWN` even if same-name Actions run passes.
3. Review wrapper says APPROVED but exact `commit_id` or reviewer authorization cannot be shown => do not count it as current-head approval.
4. Code-owner review active + changed-path-to-CODEOWNERS mapping or team membership unavailable => `UNKNOWN`.
5. Signed-commit rule active + head commit verified but an earlier commit in update range unverified => BLOCKED; head-only check is unsound.
6. Code-scanning rule active + endpoint inaccessible => `UNKNOWN`; absence of visible Alerts cannot be interpreted as clean.
7. Code-quality/coverage rule active + only a generic successful CI run visible => `UNKNOWN` unless that evidence is documented as gate-equivalent.
8. Merge queue active + PR head fully green but merge-group SHA unknown => `UNKNOWN`/enqueue handoff required.
9. Async merge returns `409` with existing UUID from a different action/head => do not treat the returned UUID as idempotent success; verify intent and fail closed on mismatch.
10. Async merge result expires after 24h and GET returns `404` => reconstruct from durable PR/merge state; never infer “not submitted”.
11. Multi-ref claim where one `beforeOid` is stale => GraphQL `updateRefs` rejects the entire group; equivalent sequential file CAS may partially commit and needs recovery evidence.
12. Staged immutable payload succeeds but pointer CAS fails => payload is garbage-but-harmless; readers remain on old exact pointer and no partial publication is visible.

## Exact continuation

Fresh-bootstrap first. If the Phase-1 overlay remains active, keep the preserved Argus base continuation dormant. Continue from this checkpoint. Next leaf: turn the lattice into an executable verifier specification with a policy-normalization schema and per-family `PASS/BLOCKED/UNKNOWN` evidence records. Prioritize the unresolved review-family proof boundary: exact pagination of reviews/threads, changed-file + CODEOWNERS mapping, required-team membership/permissions, latest-push binding and shared-commit-other-PR blockers. In parallel, inspect public deployments/status ordering semantics and required-workflow run identity to decide whether either family can be promoted from `UNKNOWN` to a narrowly `PROVABLE` subset when the generic endpoint becomes available. Then add a crash-state transition table for merge-async (`not-submitted / accepted-U / existing-U-mismatch / pending / merged / failed / expired-unknown`) and a staged-publication recovery matrix versus `updateRefs`. Preserve a nonempty frontier and do not restore Argus base work merely because this leaf completes.

## Public sources

- GitHub ruleset rule families: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- GitHub REST deployments: https://docs.github.com/en/rest/deployments/deployments
- GitHub REST deployment statuses: https://docs.github.com/en/rest/deployments/statuses
- GitHub REST code scanning: https://docs.github.com/en/rest/code-scanning/code-scanning
- GitHub REST code quality: https://docs.github.com/en/rest/code-quality/code-quality
- GitHub REST pull requests / async merge: https://docs.github.com/en/rest/pulls/pulls
- GitHub GraphQL Git / `updateRefs`: https://docs.github.com/en/graphql/reference/git
