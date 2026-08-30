# Phase-1 multi_agent Part 75 — server-assigned repository identities

## Authority / scope

- Role: `multi_agent`; task: `phase1-clean-multi-agent-concurrency-claims`.
- Frozen semantic authority: `automation_control/DESIRED_STATE.json` blob `481660fb6008a57cea162da38439cf115c8d7ebe` control revision 26; `automation_control/roles/multi_agent.json` blob `f6bade5e0f774a0623e615b1fc5f924475732d5c` config revision 8; main ref observed as `de0165308d48efa0e34e5e4ca39c8bf49341cc34`; transport `exact_sha_main_ref`.
- Presemantic liveness witness: `automation_control/receipts/multi_agent/receipt_2026-08-30T2232_JST_presemantic_witness_seq001.json`, exact-read back before the first own-state/public semantic read.
- Predecessor state: `LATEST.json` blob `e930c78747affc04d58223d00feaa1837ad5cf82`, whose exact continuation selected this Part 75 leaf.
- Bounded leaf only: inspect GitHub Issue server-assigned identities as a possible anti-rollback / claim-fencing anchor outside branch/path state. No issue was created, modified, transferred, or deleted because this CLEAN role's repository write boundary is limited to its own state and receipt namespaces.

## Public / connector observations

1. Current Chat GitHub connector capability discovery exposes `create_issue`, `fetch_issue`, `update_issue`, issue search, comments and related issue operations. `create_issue` takes repository, title/body, assignees, labels and milestone, with no exposed idempotency token or expected-current precondition. The issue-scoped connector discovery did not expose an issue-delete action.
2. GitHub REST `Create an issue` documents a `201 Created` response containing server-assigned `id`, `node_id`, and repository-scoped `number`; it also documents `503 Service unavailable` and secondary rate limiting. Source: https://docs.github.com/en/rest/issues/issues
3. GitHub REST `Get an issue` documents `301 Moved Permanently` after transfer and `410 Gone` when a readable issue was deleted. Same source: https://docs.github.com/en/rest/issues/issues
4. GitHub documents that repository admins/owners can permanently delete issues. Source: https://docs.github.com/en/issues/tracking-your-work-with-issues/administering-issues/deleting-an-issue
5. GitHub GraphQL exposes `createIssue`, `transferIssue`, and `deleteIssue`. `transferIssue` consumes an Issue node ID and returns the transferred `Issue`; `deleteIssue` deletes the Issue object. Source: https://docs.github.com/en/graphql/reference/issues
6. GitHub's global-node-ID migration guidance says the new global IDs are unique and may be relied on directly as references; the global-node-ID guide recommends persisting them across API versions. These statements establish identity/reference uniqueness, not semantic-generation order, non-deletability, or a compare-and-swap on a current tail. Sources: https://docs.github.com/en/graphql/guides/migrating-graphql-global-node-ids and https://docs.github.com/en/graphql/guides/using-global-node-ids
7. GitHub documents issue transfer as retaining the issue's comments/assignees and redirecting the old URL to the new issue URL. Source: https://docs.github.com/en/issues/tracking-your-work-with-issues/administering-issues/transferring-an-issue-to-another-repository

## Bounded adversarial mechanism test

Four candidate uses were checked against six trace families (24 mechanism-traces):

- `issue_number_floor`: treat server issue number / creation order as freshness.
- `global_node_id_tail`: treat the newest remembered global node ID as current authority.
- `immutable_issue_chain`: each new issue body names predecessor node ID and semantic generation.
- `issue_plus_branch_pointer`: issue is immutable evidence while a repository file/ref stores the canonical tail.

Trace families: normal g3->g4 creation; stale g3 worker creates after g4; ambiguous create response then retry; permanent deletion of the current issue; issue transfer; repository path/ref rollback while the issue object survives.

### Results

- `issue_number_floor`: fails semantic fencing in the stale-worker trace even under the *stronger* hypothetical assumption that numbers are strictly increasing. A stale g3 worker that creates after g4 would receive a later server creation identity, so server creation order is not semantic authority order. It therefore cannot encode parent generation/currentness by itself.
- `global_node_id_tail`: global uniqueness is useful as an incarnation/effect identity, but the documented contract is not an ordering relation. Two unique node IDs do not tell a stateless worker which semantic generation is authoritative. Permanent deletion can also make a once-current node unresolvable (`410 Gone`).
- `immutable_issue_chain`: a stale writer can create a fork from an older predecessor because `createIssue` has no documented compare against a canonical tail. Unique child IDs distinguish forks but do not choose one. The ambiguous-response trace also has no connector-exposed idempotency token or server uniqueness constraint on a deterministic transition ID, so a retry cannot be proven at-most-once from the documented surface.
- `issue_plus_branch_pointer`: the issue ID improves durable identity/reconciliation, but canonical freshness returns to the branch/path pointer. Part 74 already scoped that same-domain delete/recreate/force rollback remains unresolved; an immutable issue does not make a rolled-back pointer current.
- Issue transfer is compatible with the idea that a node ID is a cross-API object reference, but it does not add generation ordering or a tail compare. Repository-scoped URL/number addressing is additionally redirected on transfer, so it is weaker than node identity as an incarnation handle.

Mechanism outcome count within this finite 24-trace audit: **0/4 candidates establish a documented anti-rollback authority primitive**. This is not a universal impossibility theorem. A scoped positive remains: **global node IDs are documented unique references and can serve as durable effect/incarnation identities**, including reconciliation metadata, provided canonical generation/freshness is fenced elsewhere.

## Acceptance / zero-dependency assessment

- Accepted anti-rollback anchor from this leaf: **none**.
- Exact unresolved child: a server-assigned unique repository object identity lacks a documented semantic-generation order and lacks a create-time compare against the current authority tail; deletion can remove the object. Therefore it cannot replace the missing non-rollback freshness authority by itself.
- Residual richer-mode / protected / manual execution dependency added: **false**. No external execution handoff was accepted.
- Finite monthly/trial/paid quota dependency added: **false**. Only current lightweight GitHub repository/API transport and public documentation were inspected; no quota-bearing compute/storage feature was consumed.
- Incremental monetary cost: **0**.
- Scope guard: public contract + connector capability audit + finite adversarial mechanism reasoning only. No destructive live test; absence of a documented guarantee is treated as fail-closed, not as proof GitHub internally reuses IDs or necessarily duplicates every retry.
- Global Phase-1 completion: **false**; recurring objective remains open.

## Exact continuation

**Part 76:** test a stronger Chat-exposed issue-based idempotency construction rather than raw server IDs: deterministic `transition_id` embedded in issue title/body + search/read-before-create + search/read-after-ambiguous-response. Enumerate two concurrent creators, stale-generation replay, response loss after successful create, search lag/visibility, deleted matching issue, transferred issue, and duplicate same-marker issues. Accept only if the current connector/public server contract provides a uniqueness or atomic compare that prevents two same-marker authoritative issues; otherwise preserve the smallest missing primitive and then move to another non-conflicting Phase-1 coordination leaf on the next invocation.
