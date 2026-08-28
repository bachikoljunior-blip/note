# Phase-1 self-improvement — CHAT-STICKY-CREDIT-v1

Observed semantic-work interval began after a valid SHA-only bootstrap on 2026-08-29 JST.

## Authority binding

- role: `self_improvement`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- assignment: `phase1-clean-self-improvement-optimizer-switching`
- frozen main SHA: `7bd9c35e1d72de624277bb495cad9accd79f0b4b`
- root: `automation_control/DESIRED_STATE.json`, blob `f3221f10748a3d2ae86d9a544e27e5a44192b007`, control revision 24
- own config: `automation_control/roles/self_improvement.json`, blob `c5d194b341a70356da196cfb88636ab41fc1bc9f`, control revision 14, config revision 7
- transport mode: `sha_only_ref_object`
- enabled_desired: true

An earlier generic branch lookup exposed excess GitHub commit metadata before semantic work. That payload was discarded. The valid bootstrap was rebuilt from the Git ref-object SHA, exact-SHA root/config reads, and a repeated Git ref-object lookup before any own-state/public semantic read.

## Why the previous leaf is not a Phase-1-v4 acceptance route

Own clean sequence 112 used a Python/scikit-learn timing harness and sequence 113 used a Python/loopback-HTTP controller. Those artifacts remain useful algorithmic/engineering evidence, but root control revision 24 now requires an accepted mechanism to eliminate richer-mode execution itself rather than treating such execution as the outcome path. Therefore neither harness is counted here as a root-v4 acceptance mechanism. This run switched to a leaf whose steady-state decision logic is executed directly by the recurring Chat invocation and whose repository usage is transport only.

## Existing-solution audit

Public sources were read only after the valid clean bootstrap.

1. Hyperband / Successive Halving — Li et al., JMLR 2018, https://jmlr.org/papers/v18/16-558.html . The reusable idea is adaptive resource allocation and early stopping of weak candidates. Literal HPO execution, however, assumes candidate evaluations/training resources, so it is not by itself a zero-richer-mode Phase-1 mechanism.
2. Universal restart schedules — Luby, Sinclair & Zuckerman 1993, https://www.cs.utexas.edu/~diz/pubs/speedup.pdf . The result is relevant only when attempts are safe independent restarts of a Las Vegas computation. Stateful Chat assignments with durable/irreversible effects do not satisfy that premise by default, so blind Luby-style restarts are prohibited unless the leaf is explicitly pure/idempotent.
3. ChatGPT Scheduled Tasks — OpenAI Help Center, https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt . Scheduled tasks run in ChatGPT and can recur; current documentation also says plan usage limits apply, active-task limits exist, and tasks may pause in some conditions. The controller therefore uses the already-existing recurring task, creates no extra task, and never treats a missing wall-clock invocation as negative evidence about an assignment.
4. GitHub REST repository contents / rate limits — https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28 and https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api . Updating a file requires the current blob `sha`; GitHub documents 403/429 rate-limit responses and retry/backoff guidance. The controller therefore treats repository calls only as CAS-guarded state/evidence transport. Rate limiting is a transport block, not an assignment failure or credit event.

## Candidate comparison

### STATIC-ROUND-ROBIN

- zero external compute: yes
- hidden executor: none
- recovery complexity: low
- weakness: ignores positive progress and wastes invocations on a leaf that is already producing useful durable milestones.

### GREEDY-CREDIT

- zero external compute: yes
- hidden executor: none
- weakness: a leaf can monopolize the schedule through easy/repeated micro-credit unless credit identity and frontier impact are tightly constrained.

### CHAT-STICKY-CREDIT-v1

Selected mechanism. It keeps the current leaf only while the immediately preceding semantic run produced a unique durable milestone and the leaf still has an eligible exact next action. Otherwise it switches deterministically. No numeric reward model, external optimizer, hosted runner, cloud API/model, Codespace, package service, artifact store, or manual user execution is required.

## State schema

Each durable controller snapshot contains:

- `control_binding`: exact root/config revision and blobs
- `current_leaf`: source-qualified leaf ID
- `leaves[]`: `{id,status,last_semantic_outcome,last_selected_sequence,credit_total,exact_next_action}`
- `credited_milestone_ids[]`: immutable unique IDs used to prevent duplicate credit
- optional `pending_switch`: `{decision_id,from,to,reason,decision_sequence}`
- `frontier_nonempty` and one `exact_next_action`

Allowed leaf statuses are `ELIGIBLE`, `BLOCKED_UNRESOLVED_CHILD`, and `SATISFIED`.

Allowed semantic outcomes are:

- `MILESTONE_DURABLE`: immutable own artifact/checkpoint was written and read back; no residual richer-mode/protected/user step; no optional finite monthly/trial/paid quota dependency; incremental monetary cost zero.
- `SOFT_NO_PROGRESS`: safe semantic attempt completed but did not close a frontier item.
- `HARD_DEPENDENCY_BLOCK`: a residual richer-mode/manual/protected execution step or optional quota-bearing dependency is required.
- `TRANSPORT_BLOCK`: repository/public-read transport is rate-limited or unavailable before durable commit.
- `STALE_STATE_CONFLICT`: current-blob/CAS check rejects the attempted pointer replacement.
- `TERMINAL_LEAF`: leaf is satisfied in its exact tested scope.

## Transition rule

1. Reconstruct the current durable state before semantic work.
2. If a `pending_switch` exists and its target is still `ELIGIBLE`, resume that exact target. Do not reselect and do not add credit.
3. If the current leaf's preceding outcome is `MILESTONE_DURABLE`, the exact next action is still eligible, and there is no control/scope blocker, continue the current leaf.
4. On `SOFT_NO_PROGRESS`, choose the eligible nonterminal leaf with the oldest `last_selected_sequence`; break ties by stable source-qualified ID.
5. On `HARD_DEPENDENCY_BLOCK`, mark the leaf `BLOCKED_UNRESOLVED_CHILD`, preserve the child problem, and select the next eligible leaf by the same deterministic rule.
6. On `TRANSPORT_BLOCK` or `STALE_STATE_CONFLICT`, do not change assignment and do not alter credit. Fail closed for the invocation; retry/back off or reread current state on a later run.
7. On `TERMINAL_LEAF`, mark `SATISFIED` and select the next eligible leaf. If no eligible leaf remains, create/select a new non-conflicting Phase-1 leaf rather than declaring global completion.
8. Never mutate the physical recurring scheduler from this worker.

## Credit rule

Credit is deliberately sparse and binary.

- A unique `milestone_id` receives exactly `+1` only after the supporting own-role artifact/checkpoint has been read back successfully.
- Re-observing the same milestone ID produces `+0`.
- `SOFT_NO_PROGRESS`, `HARD_DEPENDENCY_BLOCK`, `TRANSPORT_BLOCK`, `STALE_STATE_CONFLICT`, a missing scheduled invocation, speculative prose, or a handoff to a richer/user/external executor all produce `+0`.
- Credit never decays with wall-clock time and is never decremented merely because the scheduler paused or an invocation was not delivered.

This avoids conflating scheduler/transport liveness with semantic assignment quality.

## Deterministic switching/recovery trace test

This is a specification-level trace test performed directly in the scheduled Chat reasoning path. It is not a Python/runtime crash-injection experiment.

| Case | Input event | Required transition | Result |
|---|---|---|---|
| T1 | current leaf A -> unique `MILESTONE_DURABLE` | credit A +1; keep A if exact next action remains eligible | PASS |
| T2 | A -> `SOFT_NO_PROGRESS`; B is oldest eligible | credit unchanged; persist switch A->B | PASS |
| T3 | B reveals mandatory manual-user/richer executor | mark B `BLOCKED_UNRESOLVED_CHILD`; no credit; select next eligible | PASS |
| T4 | candidate D requires optional hosted/cloud/API credit when quota=0 | mark D blocked; no acceptance credit; select next eligible | PASS |
| T5 | repository write/read returns documented rate-limit condition before durable result | `TRANSPORT_BLOCK`; no switch, no credit, retry/backoff later | PASS |
| T6 | LATEST replacement loses CAS race/stale blob | `STALE_STATE_CONFLICT`; no switch/credit; reread current own pointer | PASS |
| T7 | fresh run sees unresolved durable `pending_switch` A->C | resume C exactly; no second selection decision; no duplicate credit | PASS |
| T8 | same `milestone_id` is observed again after resume | credit remains exactly one | PASS |
| T9 | scheduled invocation is absent/paused and there is no run receipt | no semantic state change and no assignment penalty | PASS |
| T10 | all known leaves become blocked/satisfied | preserve blockers, create/select a new non-conflicting Phase-1 leaf; recurring worker remains enabled | PASS |

Trace conformance: **10/10**.

## Actual switch in this run

The current root revision changed the acceptance condition from the preceding root-v3 state. The sequence-112 timing continuation and sequence-113 loopback-HTTP continuation both depend on richer execution for their acceptance test, so this run did not consume fresh timing or launch another HTTP harness. It switched to `CHAT-STICKY-CREDIT-v1`, audited public mechanisms, and completed the 10-case symbolic transition/recovery test inside scheduled Chat. That switch is a real root-v4 assignment decision; the 10-case trace is a deterministic protocol test, not evidence that arbitrary hard process crashes have been survived.

## Phase-1 acceptance assessment

- scheduled-Chat-native decision path: **yes**
- residual richer-mode/protected/manual-user execution in the mechanism: **none identified**
- hosted runner / Codespaces / artifact/LFS/package / cloud / external API-model compute dependency: **none**
- optional monthly/trial/paid quota dependency: **none beyond the already-granted scheduled-Chat substrate itself**
- repository dependency: **lightweight CAS/rate-limited transport only; not compute**
- incremental monetary cost: **zero**
- scheduler mutation required: **no**
- hard-crash acceptance: **not proven in this run**
- tested scope: **deterministic controller semantics plus 10 fixed recovery/switching traces and the live root-v4 leaf switch; not an empirical throughput/quality benchmark**

## Remaining failure modes

1. Milestone semantics are still judged by Chat. A leaf could manufacture many superficially distinct milestone IDs unless each milestone is required to close a named frontier item and bind to a read-back artifact.
2. Repository rate limits can stop liveness temporarily. Safety is fail-closed because no semantic credit/switch is committed until state is durable.
3. The product scheduler itself has usage/active-task limits and may pause. This mechanism assumes an invocation has actually been granted; it does not claim to remove limits of the scheduled-Chat substrate.
4. The unresolved-switch recovery rule has only symbolic coverage here; a natural cross-invocation persistence check is still needed under root-v4 without injecting richer-mode execution.

## Frontier / exact next action

Frontier is nonempty. Exact next action: persist a minimal `CHAT-STICKY-CREDIT-v1` role-local controller state and, on the next fresh scheduled-Chat invocation, verify a natural cross-invocation recovery transition: the new run must reconstruct the same credited milestone and current leaf before any public semantic read, must not duplicate credit, and must either continue the exact next action or switch only under the rules above. Then audit one public self-improvement/agent optimizer whose switching logic can be reduced to scheduled-Chat state transitions; classify any worker/runtime/cloud/model execution requirement as an unresolved child rather than an accepted handoff. Preserve the older CAL-WILSON and HTTP artifacts only as algorithmic/engineering evidence, not as root-v4 acceptance.
