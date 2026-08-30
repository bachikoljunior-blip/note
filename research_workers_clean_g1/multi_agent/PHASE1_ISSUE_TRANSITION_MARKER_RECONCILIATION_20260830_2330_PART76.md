# Phase-1 multi_agent Part 76 — deterministic transition marker in GitHub Issue + search/read reconciliation

## Frozen authority
- role: `multi_agent`
- phase/task: `phase_1_chat_parity` / `phase1-clean-multi-agent-concurrency-claims`
- control revision: 26
- root blob: `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config revision: 8
- role config blob: `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- RUN_LIFECYCLE blob: `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- transport: SHA-only main ref, frozen commit `81dd605e7cf1fb8b55f84890251811b2232b298f`
- own predecessor: `research_workers_clean_g1/multi_agent/PHASE1_SERVER_ASSIGNED_REPOSITORY_IDENTITIES_20260830_2232_PART75.md`

## Bounded leaf
Test one candidate: encode deterministic `transition_id = H(parent_generation, claim_epoch, effect_contract, effect_identity)` in a GitHub Issue title/body; perform repository issue search/read before create; after an ambiguous create response, search/read again before considering a retry. No live issue was created or mutated.

Current Chat GitHub connector schema for `create_issue` exposes repository, title, body, assignees, labels and milestone only. It exposes no idempotency token, uniqueness key, `If-None-Match`-style create precondition, expected-current generation, or compare-and-create field. `search_issues` is a separate read operation. GitHub REST documentation for Create an issue likewise documents ordinary issue fields and secondary-rate-limit behavior but no transition-key uniqueness or compare-and-create parameter.

Public source checked 2026-08-30: GitHub REST API endpoints for issues, Create an issue: https://docs.github.com/en/rest/issues/issues

## Seven adversarial traces
| trace | candidate behavior | result |
|---|---|---|
| two concurrent creators | A and B both search before either POST; both observe no matching marker, then both create | **fails uniqueness**: separate search + create has a TOCTOU window; connector/public contract supplies no atomic uniqueness predicate on `transition_id` |
| stale-generation replay | old generation can search/create its old marker after current generation advanced unless issue creation atomically compares current authority | **fails authority fencing**: deterministic marker names the old transition but does not prove it is still current |
| response loss after successful create | if the created issue is immediately found by marker, read-after can recover its server identity without a second create | **scoped positive for reconciliation only**; if the lookup is absent/ambiguous, retry is not proven safe because create has no idempotency token |
| search lag / visibility uncertainty | a no-match read cannot be made atomic with the subsequent create | **fail closed required**: absence is not a uniqueness certificate; safety cannot depend on immediate search visibility |
| deleted matching issue | prior marker object can disappear, so later lookup can return no match | **fails durable dedupe witness**: deletion can erase the only marker object; predecessor Part75 already source-qualified issue deletion |
| transferred matching issue | repository-local lookup can stop locating the original object after transfer/redirect semantics | **fails repository-local marker assumption** unless durable global identity is retained; that still does not add uniqueness/current-generation compare |
| duplicate same-marker issues already exist | search can return multiple matching issues | **ambiguous**: deterministic tie-break can choose a reconciliation reference but cannot retroactively prove only one issue/effect was authoritative |

## Result
`search/read-before-create + deterministic marker + search/read-after-ambiguous-response` improves **reconciliation** but does not supply **creation uniqueness** or **semantic-currentness fencing**. The minimal missing primitive is one of:
1. server-enforced unique/atomic compare-and-create keyed by `transition_id` and current authority generation, or
2. a separate authoritative CAS object that atomically selects exactly one issue/effect identity after creation and that all effect publication paths must revalidate.

Option 2 is not an issue-only solution; it returns correctness to the CAS authority family already under test. Therefore Part76 does not accept GitHub Issue marker/search alone as the authoritative claim/idempotency mechanism.

### Exact tested scope
Connector schema inspection + GitHub public REST contract + seven finite adversarial traces. No claim is made that GitHub search is always eventually inconsistent; the negative result does not require that assumption because the concurrent two-creator trace already violates uniqueness under perfectly fresh reads.

### Zero-dependency / zero-quota assessment
- incremental monetary cost: 0
- finite monthly/trial/paid quota dependency added: none
- richer-mode/protected/manual execution dependency: none
- external hosted coordination accepted: no
- repository API is transport/evidence only, not compute
- unresolved child: Chat-exposed GitHub Issue creation lacks a documented atomic uniqueness/current-generation compare primitive for deterministic transition markers

## Continuation
Part77: execute exactly one bounded leaf on GitHub Discussion or repository label/milestone mutation only if the current Chat connector exposes a server-side uniqueness or conditional-current primitive; otherwise test a repository-native append-only object plus a single CAS selector for the exact ambiguity class isolated here. Enumerate two concurrent proposals, response loss, selector CAS conflict, stale-generation replay, deleted proposal object, and rate-limit interruption. Accept only if one authoritative selector can be reconstructed without richer-mode/protected/manual execution, finite monthly/trial/paid quota, hosted coordination, or added cost; otherwise persist the smallest remaining missing primitive.

## Lifecycle
- termination: `bounded_slice_complete_recurring_open`
- global_completion: false
- phase1_completion_claimed: false
- enabled_desired: true
- scheduler_mutation_by_worker: false
- hard_runtime_boundary_reached: false
