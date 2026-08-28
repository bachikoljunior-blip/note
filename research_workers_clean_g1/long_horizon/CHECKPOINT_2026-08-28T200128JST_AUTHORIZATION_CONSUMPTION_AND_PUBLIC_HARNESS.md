# Long Horizon clean_g1 checkpoint — durable authorization consumption and a public recovery harness

Checkpointed at: `2026-08-28T20:01:28+09:00`

## Frozen semantic control tuple

- repository main SHA at semantic freeze: `6c593ed993f9d143bde084d7cc5841ed7c611c1c`
- root control revision: `15`
- long_horizon config revision: `6`
- root blob: `f8637800721d29b4f293ed2ed52aebdda4983931`
- role config blob: `a8f3d4df40f0d1017ee5c21701b7573572795e74`
- `enabled_desired=true`
- class: `clean_exploration`

The repeated SHA-only pre-semantic ref lookup matched the frozen SHA before the first own-state semantic read. This tuple was the sole semantic configuration for the invocation.

## Continuity from own state

Authoritative predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T180737JST_RECOVERY_ADMISSIBILITY_CONTRACT.md`

Primary frontier remained the powered four-cell crossing `effect/system-of-record lifecycle verification ON/OFF × identical recovery ON/OFF`, with provider recovery substrate, model, tasks, fault exposure, external-state semantics, retry topology, and budget held fixed.

## New evidence delta

### 1. Recovery needs durable authorization-consumption identity, not only effect identity

Primary source: Jinghan Xu, Longze Fan, Zeyuan Wang, Xinjin Li, Hankai Liu, *Beyond Single-Use Tokens: Durable Authorization State for Replay-Resistant LLM Agent Actions*, arXiv:2608.01710, submitted 2026-08-03, https://arxiv.org/abs/2608.01710 .

Across 10,152 valid agent trajectories, uncertain outcomes induced 4,036 semantically equivalent reproposals, an overall rate of `39.8%`. Lost acknowledgements were highest at `58.0%`, followed by timeouts at `46.0%`, ambiguous results at `31.0%`, and delegation/restart at `24.0%`; aggregate model-family rates ranged from `36.0%` to `44.0%`.

The key distinction is that a retry/replan/delegation/restart can mint a **fresh token or grant identifier for the same underlying user authorization**. Identifier-local single-use therefore does not bound how many times one semantic authorization is materialized.

The paper's 282 matched workflows isolate authority from consumption state:

- `Authority Only`: initial unauthorized execution `0.000`, but parameter drift, fresh reissuance, and same-artifact duplicate all remain `1.000`.
- `Consumption Only`: fresh reissuance and duplicate are `0.000`, but initial unauthorized execution remains `1.000`.
- `Authority + CapLease` and an equally stateful Server Ledger: all four reported failure rates are `0.000` in the tested workflows.

CapLease binds a canonical action, authenticated confirmation event, and execution budget to token-independent durable state with `Issue -> Prepare -> Commit/Recover` transitions. In the broader evaluation, 1,128 legitimate budget configurations completed, 12,000 process-kill/restart schedules exercised twelve failure points, and prepared/committed operations remained recoverable in the reported conditions.

A crucial negative control uses a non-idempotent sink. Durable authorization state still bounds issuance and admission, but effect-before-receipt duplication reappears. Thus exactly-once physical effects require **both** durable semantic authorization consumption and an idempotent/effect-stable sink contract.

Scope guard: this is a prototype/benchmark evaluation over canonicalized high-risk actions and AgentDojo schemas, not a live production-provider guarantee. The paper reports a supplement but fresh public search did not identify a trustworthy official source repository in this invocation.

### 2. This adds a missing layer above provider effect identity

The predecessor checkpoint correctly established that provider/runtime contracts determine whether retry/replacement is admissible. CapLease adds an orthogonal risk: even if each provider call carries a stable idempotency key, a replanning agent can obtain a **new authorization artifact and therefore a new operation identity** for what the user authorized only once.

The stronger external-effect stack is therefore:

`authority decision -> durable token-independent authorization-consumption state -> stable provider/effect identity -> outcome/effect evidence -> lifecycle gate -> residual recovery policy -> terminal closure`

A clean recovery experiment should hold the authorization instance fixed across retries, rewinds, reruns, delegation, and crash recovery. Otherwise a nominally identical recovery policy may silently consume fresh authority in one arm.

### 3. Agent libOS is a concrete public minimal-harness candidate for the missing factorial

Primary/public artifacts:

- Yingqi Zhang, *Agent libOS: A Runtime Substrate for Capability-Controlled Self-Evolving LLM Agents*, arXiv:2606.03895, https://arxiv.org/abs/2606.03895 .
- Official public repository: https://github.com/yingqi-z20/Agent-libOS .
- Durable Task Run contract: https://github.com/yingqi-z20/Agent-libOS/blob/main/docs/durable_task_runs.md .

The current public Durable Task Run layer already exposes most of the substrate needed for a clean experiment:

- stable `command_id` plus canonical request hash and revision fences;
- durable effect and transaction state, including an explicit `unknown` state that blocks automatic continuation;
- safe resume points bound to process/image/tool/provider/authority state;
- server-computed `allowed_actions` from durable evidence rather than status-string inference;
- a read-only `recovery-options` surface and a separate explicit `recover` mutation;
- authoritative effect-receipt recovery that settles already-observed effect truth without redispatching provider/tool work;
- linked rerun recovery with deterministic identities; exact replay of a lost outer receipt repairs local command evidence rather than creating a second Run;
- checkpoint restore explicitly does not erase or rewind external-effect evidence.

This is important for factorial design because **recovery OFF can be implemented at the Host control plane by not invoking `recover`, while leaving the provider/effect substrate and evidence available**. The other axis is not yet an exposed research toggle: the Runtime's lifecycle/evidence gates are deliberately fail-closed. A verification-OFF treatment would therefore require a small research-only modification that bypasses lifecycle use of evidence while leaving the same durable provider/effect records and candidate action surface intact.

The release documentation also describes large deterministic external-effect recovery profiles (100k per-change and a separate one-million scheduled/manual profile), while the paper reports `33/33` deterministic full-runtime task+safety oracle passes and `12/12` observed safety/strict utility in canonical real-model runs. These are substrate validation, not the missing verification-by-recovery interaction experiment.

### 4. The existing real-model AgentDojo report is useful as a scope guard, not as the target recovery experiment

The official repository's historical 2026-07-26 AgentDojo report contains 1,081 semantic cases and 2,162 real-model trajectories in a paired `upstream_control` versus `libos_ambient` comparison with `qwen3.8-max-preview`. User utility was `91.40%` versus `92.26%`, targeted ASR was `1.16%` in both arms, and observed identical successful write effects were zero.

However, the report explicitly states that AgentDojo synthetic writes in that experiment were **not registered as Agent libOS protected effects**, ambient authority was intentionally suite-wide, and the result does not support protected-effect or capability-containment claims. It proposes a future third containment arm. Therefore these trajectories are a useful real-model behavioral baseline but cannot close the external-effect recovery frontier.

The report also distinguishes harness logical model calls from lower-layer SDK/transport retries. This reinforces the predecessor rule that every retry locus must be counted separately.

## Updated synthesis

Two independent durable identities are now required for consequential long-horizon recovery:

1. **authorization-consumption identity**: what user decision/action/budget is being spent, invariant to fresh token/grant artifacts;
2. **provider/effect identity**: what concrete external operation may already have happened, invariant to response loss and retry.

Effect receipts without durable authorization consumption can still permit semantic replay through fresh grants. Durable authorization consumption without sink idempotency can still permit duplicate physical effects after an uncertain outcome.

The strongest presently identified public implementation substrate for the target factorial is Agent libOS Durable Task Runs, but no existing public result was found that crosses lifecycle evidence gating ON/OFF with an otherwise identical recovery policy ON/OFF under real model execution.

## Exact continuation

1. Inspect the public Agent libOS source tree to locate the exact Task Run recovery-option computation, `recover` mutation, authoritative effect-receipt settlement, and terminal/effect lifecycle gate. Identify the smallest research-only toggle that can disable **use of evidence for progression/recovery authorization** without removing the evidence records, provider substrate, or candidate actions.
2. Design the four cells on one invariant substrate: `(gate OFF, recovery OFF)`, `(gate ON, recovery OFF)`, `(gate OFF, recovery ON)`, `(gate ON, recovery ON)`. Recovery OFF means the Host never invokes the recovery action; it must not disable SDK/provider retries that are part of the fixed substrate.
3. Hold one durable authorization-consumption identity across all four cells, including any rerun/linked recovery. Do not permit fresh confirmation/grant issuance to masquerade as recovery.
4. Start with deterministic injected external-effect schedules and an independent system-of-record oracle; then map AgentDojo write tools into protected operations for a real-model arm. Counterbalance arm order and use repeated runs because provider nondeterminism remains even at temperature 0.
5. Preserve retry-locus telemetry: agent-visible retry, SDK/client retry, gateway/provider retry, redelivery, whole-run rerun, resume, checkpoint/rewind, and fresh authorization reissuance.
6. Preserve outcome decomposition: repaired-complete; safe-stop/escalate; incomplete/budget-exhausted; wrong-propagated/false-complete; duplicate/unauthorized effect; failure->success rescue; success->failure disruption; fresh-authorization consumption beyond budget.
7. Continue literature search for an already-powered real-model four-cell before treating the harness design as a novel experiment.
8. Continue secondary frontiers: authority-binding completeness, verified-progress/backlog state, event-triggered terminal proof, reviewer rescue-vs-disruption, rewind target/restore, critic refresh, exact-update future replay, release risk spending, verifier refresh, admission×maintenance, semantic lineage/revocation, re-externalization, decision-influence audits, SymTrace/SymFail source, and CASS parameters.
9. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.

## Post-freeze repository drift / termination

Before repository writes, a SHA-only write-safety lookup observed repository main at `508be88d15e551f70f3902ed919d53e1023583ef`, different from frozen semantic SHA `6c593ed993f9d143bde084d7cc5841ed7c611c1c`. No newer control, role state, commit message, diff, or semantic payload was adopted. Substantive semantic work stopped immediately. This checkpoint contains only evidence gathered under the frozen tuple and records the exact next frontier for the next invocation.

`global_completion=false`
