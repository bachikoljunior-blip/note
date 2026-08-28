# Long Horizon clean_g1 checkpoint — retry topology, exactly-once substrate, and fault-exposure accounting

Checkpointed at: `2026-08-28T14:02:48+09:00`

Frozen semantic control tuple for this physical invocation:
- note main SHA: `a395bbc74c7a44ca3f27c27bb53ac6ad883cf37a`
- root control revision: `13`
- root blob: `cc9b1f22f0fda9cf26296057fd35b19a090618b4`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- role: `long_horizon`, `enabled_desired=true`, class `clean_exploration`
- repeated pre-semantic SHA-only ref lookup matched before own-state/public semantic work.
- a later SHA-only write-safety lookup observed main had advanced to `14cb17b2aa14019e28bf2285c1d40689d807285f`; per the frozen-control rule, no semantics from that newer head were adopted. Substantive research stopped and this checkpoint was written under the frozen tuple.

Clean-boundary note:
- Before the authoritative repository path was resolved, an automation-list call exposed unrelated automation metadata/prompts. That payload is quarantined. It was not used for source selection, interpretation, synthesis, candidate generation, or research direction; only non-semantic transport discovery was retained to locate the `note` repository. No O/O-derived state, other-worker state/output, downstream state, legacy/pre-independence research, shared execution ledger, or other-role receipt/config was used semantically.
- Connector capability discovery in this invocation was read-only. Repository mutations are limited to this role-local clean state and immutable own receipt namespace.

## New public artifact: an execution-layer 2×2 finally isolates liveness from duplicate-effect safety

A public August-2026 repository, `gssanjana4/idempotencybench` (`Do LLM Agents Act Exactly Once? Measuring Idempotency Violations Under Retries`, ARR under review), provides a deterministic 320-task harness with a ground-truth effect ledger. It injects `timeout_after_commit`: the external effect commits but the caller sees a timeout. It crosses retry topology with execution-side mitigations and reports both task success and semantic idempotency violation rate (IVR), where duplicates are scored by canonical action identity rather than by key equality.

For the scripted **naive** subject under the same 320 timeout-after-commit tasks, the published `results/summary.csv` contains a clean `retry ON/OFF × runtime-receipts ON/OFF` 2×2:

| fixed subject | fixed fault | retry | runtime semantic receipt | task success | IVR |
|---|---|---:|---:|---:|---:|
| naive | timeout-after-commit | OFF (`no_retry`) | OFF | `0.875` | `0.000` |
| naive | timeout-after-commit | OFF (`no_retry`) | ON | `0.875` | `0.000` |
| naive | timeout-after-commit | ON (`tool_retry`) | OFF | `1.000` | `1.000` |
| naive | timeout-after-commit | ON (`tool_retry`) | ON | `1.000` | `0.000` |

This cleanly separates two jobs:
- retry supplies **liveness/completion** in this fault: `87.5% -> 100%` success;
- the semantic receipt supplies **exactly-once safety** under retry: `100% -> 0%` IVR;
- receipts alone do not recover the interrupted multi-step episode (`87.5%` remains `87.5%` without retry);
- retry alone improves headline success while making every tested task duplicate an effect in this scripted cell (`IVR=1.0`).

So, at least in this deterministic substrate, `recovery` and `effect-safety` are not interchangeable and cannot be collapsed into one reliability score. The desired controller should track liveness and realized external-effect integrity separately.

Primary artifact:
- https://github.com/gssanjana4/idempotencybench
- `results/summary.csv`
- `src/agents.py`
- `src/world.py`

### Retry topology is a first-class state variable

The same harness distinguishes five retry locations: no retry, transport/tool retry below agent visibility, agent-visible retry, failure-conditioned whole-run restart, and unconditional at-least-once redelivery. This yields a stronger mechanism result than a generic `retry yes/no` flag.

The scripted `CarefulAgent` performs read-back after a surfaced ambiguous failure. On timeout-after-commit it can keep `IVR=0` for **agent retry** and **whole-run recovery**, because the failure is visible and the agent can inspect the effect ledger before re-execution. But it still has `IVR=1.0` under **tool/transport retry** and **at-least-once redelivery**, because those duplicate executions occur below or outside the agent's opportunity to reason. By contrast, `runtime_receipts` keep `IVR=0` across all tested retry topologies.

This sharpens the control hierarchy:

`fault/retry locus -> which controller can observe it -> which layer can safely suppress/reconcile it`.

Prompt-level reflection/recovery cannot repair a retry that happens before the model is re-entered. A durable execution substrate is required for hidden transport/orchestrator redelivery classes.

### Stable idempotency identity matters across retry boundaries

The harness also separates `idem_keys` from semantic runtime receipts. For transport retry, where the same exact key is transparently reissued, idempotency keys suppress duplicates. But the naive subject mints fresh keys at agent retry / whole-run / at-least-once boundaries, so `idem_keys` leaves `IVR=1.0` in those cells. A `StableKeyAgent` that deterministically derives the key from task identity + intended action restores `IVR=0` across those retry modes.

This directly supports a long-horizon rule: **idempotency support is not sufficient unless effect identity survives the recovery topology**. A regenerated UUID after rollback/restart is not the same authorization/effect instance merely because the model intends the same outcome. Semantic/durable effect identity should be outside model regeneration when possible.

## Small real-model 2×2: useful mechanism check, not a powered result

The same repository includes a cost-capped Claude Fable 5 pilot with one task from each of 8 templates. The model itself decides whether to retry. It crosses the base prompt vs a careful `read list_effects before retry` prompt with no mitigation vs runtime receipts, all under timeout-after-commit:

- base + no receipt: `IVR=0.125`, success `1.0`;
- base + runtime receipts: `IVR=0.0`, success `1.0`;
- careful + no receipt: `IVR=0.0`, success `1.0`;
- careful + runtime receipts: `IVR=0.0`, success `1.0`.

A published transcript for the duplicate case is especially diagnostic. Under base/no-mitigation, the model receives a timeout, explicitly says it will retry with the **same idempotency key**, executes the email a second time, then reads back two effects and reports that the recipient may have received two emails. The task goal is scored achieved while `violations=1`. Under the matched careful/no-mitigation email task, the model reads `list_effects` immediately after the timeout, sees the already-committed email, does not retry, and ends with one effect.

This confirms that headline task success can be identical while external-effect correctness differs. However `n=8` per pilot arm is far too small for a broad model-level effect claim; treat it as an auditable mechanism demonstration only. The repository README also labels the real-model leaderboard as pending.

## New benchmark-methodology evidence: ACID-Bench requires fault-exposure accounting

`ACID-Bench: Auditing Transactional Reliability in State-Changing Tool Agents` (KDD AgenticAI Evaluation workshop 2026) contributes a complementary evaluation rule. It uses 52 deterministic transactional fault scenarios across retail/airline and distinguishes partial commit, ghost-success/retry idempotency, stale-read/isolation, crash/restart durability, and consequence-level verification.

The paper explicitly separates:
- final/table validity;
- whether the configured fault was actually exposed;
- safe handoff vs fault-exposed outcome;
- transactional-integrity labels;
- low-level attempts/retries.

Across its reviewed current evidence, 688 records were table-valid, of which 554 were fault-exposed and 134 safe handoffs; invalid/non-exposure records are not valid evidence for a recovery claim. The underlying attempt logs also contained 20 failed attempts affecting 14 rows that later produced completed final rows. A final `completed` row can therefore hide material operational failure/retry history.

Its fixed-model prompt-condition validation also reports 60 final rows per arm (20-scenario subset × 3 replicates): a clarification overlay produced implemented Strict Clean Pass on `27/60`, versus `2/60` with the base Tau prompt; paired counts were 27 overlay-only, 0 base-only, 2 both, 31 neither. This is a large condition effect, but it bundles guidance with the compound agent condition and is **not** evidence that postcondition verification itself caused recovery.

Primary artifact:
- https://kdd-eval-workshop.github.io/agenticai-evaluation-kdd2026/assets/papers/58_ACID_Bench_Auditing_Transac.pdf

### Scope guard

ACID-Bench is a workshop paper over retail/airline deterministic scenarios, not a broad external-provider deployment study. Its raw local row/traces are not publicly released in the paper artifact, so the public evidence is paper-level rather than independently replayable row-level evidence. The prompt overlay is not a component-isolated verification×recovery factorial.

## Updated synthesis

The external-state reliability stack should now distinguish at least four independent dimensions:

1. **fault exposure and retry locus** — did the intended fault actually occur, and at which layer did re-execution happen?
2. **liveness/recovery** — did the system resume/continue enough to complete the intended workflow?
3. **effect identity / exactly-once integrity** — did retries, restarts, or redelivery create duplicate semantic effects?
4. **contract-complete terminal verification** — even with exactly-once execution, did the realized effect bind the correct operation/entity/fields/finality/multi-system postconditions before `done`?

The IdempotencyBench 2×2 partially closes the older `runtime guarantee × fixed recovery` frontier for one exact failure class: runtime semantic receipts and retry are complementary, with one mainly changing external-effect safety and the other liveness. It does **not** close the higher-level `contract-complete effect verification × identical recovery` frontier, because semantic receipts suppress re-execution rather than verify the full requested outcome contract.

The controller ordering should therefore be refined to:

`fault exposure/locus -> durable effect identity -> safe retry/resume substrate -> verified progress -> contract-complete effect evidence -> terminal authorization -> residual LLM recovery/reviewer`.

Critic/reviewer budget should not be expected to compensate for retries that occur below agent visibility.

## Highest-priority gap status

Two frontiers now need to be kept separate:

- **Partially closed at execution layer:** `exactly-once substrate ON/OFF × fixed retry/recovery ON/OFF` has a public deterministic 2×2 in IdempotencyBench; real-model evidence exists only as a tiny `n=8`/arm pilot.
- **Still open at outcome-contract layer:** no public controlled study found here crosses **contract-complete system-of-record verification ON/OFF × identical fixed recovery ON/OFF** while holding model, task, fault exposure, retry topology, budget, and external-state semantics fixed.

## Exact continuation / nonempty frontier

1. Find a powered real-model replication of IdempotencyBench-like `retry/recovery ON/OFF × semantic receipt/idempotency substrate ON/OFF`, preferably repository/API tasks and multiple retry loci. Measure success, omission, IVR, realized retry count, and token/time cost.
2. Find/construct the still-missing `contract-complete SOR verification ON/OFF × identical fixed recovery ON/OFF` 2×2. Hold retry topology constant and count SDK/client/gateway/provider retries.
3. Cross retry **locus** explicitly: agent-visible retry vs hidden transport retry vs orchestrator whole-run vs at-least-once redelivery vs checkpoint/rewind. Ask which controls remain causally available at each layer.
4. Compare key-local idempotency with semantic/durable effect identity under regenerated tool calls after restart/rollback; preserve operation identity outside the model where possible.
5. Adopt ACID-Bench-style denominator discipline: require deterministic fault exposure before a row supports a recovery claim; separately score safe handoff, fault-exposed recovery, transactional integrity, and attempt history.
6. Continue component ablations for contract completeness: existence/status vs operation-id/idempotency binding vs entity/field match vs duplicate/uniqueness vs finality/lifecycle vs multi-system postconditions.
7. Continue host-success vs SOR-read vs contract-complete-SOR verification under timeout-after-commit, delayed visibility, partial commit, duplicate effects, and stale/unknown provider state.
8. Continue verified-progress/backlog state, freshness/supersession audit allocation, deterministic typed outcome encoding, RefineAct components, event-triggered terminal proof, and same-prefix reviewer rescue-vs-disruption.
9. Preserve rewind-selector/restore, critic-refresh cadence, persistent-refinement contamination, exact-update future replay, release-risk spending, verifier-exposure/refresh, admission×maintenance, hidden semantic lineage, post-consolidation re-externalization, decision-influence audits, SymTrace/SymFail source, and CASS parameter frontiers.
10. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.

## Termination state for this invocation

Substantive update found. No research blocker. Semantic work stopped when the post-freeze SHA-only write-safety lookup showed repository head had advanced after the semantic-freeze barrier. The newer control/head was not semantically adopted. Next invocation must resolve a fresh SHA-only control tuple before any substantive read and resume from this checkpoint if it remains authoritative in the role-local namespace.
