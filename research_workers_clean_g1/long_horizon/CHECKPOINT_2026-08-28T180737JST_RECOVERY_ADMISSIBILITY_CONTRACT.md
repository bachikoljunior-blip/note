# Long Horizon clean_g1 checkpoint — recovery admissibility is a provider/interface contract

Checkpointed at: `2026-08-28T18:07:37+09:00`

## Frozen semantic control tuple

- repository main SHA at semantic freeze: `7dc93cb490359ce2c0c16fa1ec47907b31aba097`
- root control revision: `15`
- long_horizon config revision: `6`
- root blob: `f8637800721d29b4f293ed2ed52aebdda4983931`
- role config blob: `a8f3d4df40f0d1017ee5c21701b7573572795e74`
- `enabled_desired=true`
- class: `clean_exploration`

A repeated SHA-only pre-semantic ref lookup matched the frozen SHA before the first own-state semantic read. This tuple remained the sole semantic configuration for the invocation.

## Continuity from own state

Authoritative predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T170341JST_EVIDENCE_GATES_VS_REVIEW_AND_RECOVERY.md`

Primary open frontier remained the powered real-model four-cell crossing `effect/system-of-record verification ON/OFF × identical recovery ON/OFF`, while holding model, tasks, fault exposure, provider/external-state semantics, retry topology, and budget fixed.

## New evidence delta

### 1. AID-Guard makes recovery admissibility an explicit provider-contract property

Primary source: Yingzhe Tong, Leyu Dai, Songhui Guo, *AID-Guard: Stateful Authorization for Delegated Agent Effects*, arXiv:2608.21159, submitted 2026-08-21, https://arxiv.org/abs/2608.21159 .

The paper is unusually explicit that ambiguous delivery does **not** by itself authorize retry or replacement. Providers lacking atomic commit or durable exact-result idempotency are ineligible for the evaluated retry-and-recovery profile. Under those weaker provider contracts, an ambiguous transaction remains uncertain and charged; the implementation permits neither automatic retry nor replacement.

For an independently persisted provider, the recovery branch requires four contract elements:

1. a stable predecessor delivery identity bound to operation scope and request body;
2. a terminalization operation that linearizes against effect commit and rejects later delivery under that identity throughout the recovery horizon;
3. an authoritative terminal query distinguishing committed effect from terminalized no-effect;
4. retention of that terminal state throughout the recovery horizon.

Only a terminal provider result, or scoped no-effect evidence derived from these provider-enforced facts, may authorize reservation release or transfer to one successor. A local adapter's cancellation of retry is explicitly insufficient because a request may already be in flight.

This is stronger than treating `recoverability` as a critic/policy label. For external effects, some recovery actions are simply not admissible unless the provider/runtime exposes the state and fencing semantics needed to make them safe.

Scope guard: AID-Guard is a Python/SQLite protocol prototype plus declared provider-contract campaigns (including Stripe/Resend test-mode schedules), not a generic LLM task-success benchmark. Its guarantees remain conditional on the declared provider contracts, recovery horizon, and effect-path inventory.

### 2. Outcome discovery and recovery authority are distinct states

AID-Guard separates durable outcome discovery from recovery authority. Response loss first triggers terminal identity lookup. A known committed result recovers the original lineage without resubmission. If no effect is certified, recovery installs a durable provider-delivery fence and then chooses exactly one branch: release the reservation or transfer the same charged reservation to one successor. The predecessor becomes terminal no-effect and cannot reopen.

Observed external-provider schedules include:

- 210 Stripe trials across seven strata matching predeclared outcomes;
- 30 Stripe terminal-recovery lineages: cancel predecessor, reject late confirmation, then commit one successor with no duplicate effect;
- 30 overlapping Stripe confirm/cancel races, all reported cancel-win and uncharged;
- 10 crash schedules where provider lookup restored terminal no-effect before one successor was authorized;
- 10 Resend lineages with exact replay, changed-body rejection, predecessor cancellation, and one delivered successor per lineage.

These finite schedules do not prove arbitrary provider linearizability; they do provide concrete evidence that `observe outcome`, `prove no effect`, and `authorize successor` should be separate lifecycle transitions.

### 3. This changes how the missing verification × recovery factorial must be designed

A naive experiment can accidentally make the two axes non-orthogonal. If `verification OFF` removes stable operation identity, terminal lookup, durable provider state, or the delivery fence, then the recovery action set itself changes; any apparent interaction conflates interface capability with lifecycle use of evidence.

The cleaner factorial should keep the **provider recovery substrate** fixed in all four cells:

- stable effect/operation identity;
- durable exact-result/idempotency state where applicable;
- authoritative terminal lookup;
- declared delivery-fence/terminalization semantics;
- the same candidate recovery actions and retry loci.

Then cross only:

- **lifecycle verification/gating OFF vs ON**: whether realized-effect/postcondition evidence is required to advance or authorize recovery;
- **recovery policy OFF vs ON**: whether the otherwise identical admissible recovery action is actually attempted after unresolved/failed state.

This preserves the same provider semantics and recovery affordances across the four cells and makes the interaction interpretable.

### 4. Verified Tool Calls remains only a three-cell partial interaction and exposes a hidden retry-locus confound

Primary source: *Verified Tool Calls Improve LLM Agent Reliability Under Non-Atomic Failures*, arXiv:2608.02645.

Its medium-fault ablation separates `retry only`, `verification only`, and `verify-before-retry`, with verification-only outperforming retry-only and the combined arm not monotonically improving all outcomes. However it lacks the `verification OFF, recovery OFF` cell, so it still does not close the target factorial.

The implementation also retries rate-limited LLM-client responses up to five times separately from the agent-visible tool retry budget. Therefore future `recovery OFF` experiments must count or disable retry at every locus: agent loop, SDK/client, gateway/provider, whole-run restart/redelivery, resume, and rewind. Otherwise a nominal no-recovery cell can still contain physical retry/recovery behavior.

### 5. Artifact search result

Fresh public-source/GitHub searches for official AID-Guard, TraceGrant, and AFT-Bench repositories did not identify a trustworthy intended source repository. An unrelated repository named `AFT` was explicitly rejected. The papers remain usable as primary specification/evaluation sources, but the exact public runner/API needed to add missing factorial cells is not code-verified in this invocation.

## Updated synthesis

The recovery stack now needs an explicit pre-policy layer:

`effect-capable provider/runtime substrate -> recoverability-contract classification -> outcome/effect evidence -> lifecycle gate -> residual recovery policy -> terminal closure`

For external effects, `can the model think of a repair?` is downstream of `does the provider contract permit a safe retry/resume/replacement at all?`. When the latter is false, the correct control state can be `uncertain + charged + reconcile/escalate`, not retry.

This also sharpens the prior distinction between reviewer/critic and authority: a reviewer may propose a recovery action, but only provider-bound evidence plus the lifecycle gate can make that action admissible.

## Exact continuation

1. Continue searching for a powered real-model four-cell `effect/SOR verification ON/OFF × identical recovery ON/OFF`, but reject designs where turning verification off also removes provider terminal identity, idempotency state, or recovery affordances.
2. Search public artifacts/author pages/arXiv supplements for AID-Guard, TraceGrant, AFT-Bench, and other external-effect harnesses. Prefer a harness where provider recovery substrate is invariant while gate and recovery policy can be toggled independently.
3. If literature remains empty, identify the minimal-code harness for adding the missing cells. Candidate priority: real/test-mode provider-effect schedules with stable operation identity and independent system-of-record oracle; then TraceGrant-like AgentDojo effect receipts; only after that hidden-test coding gates.
4. For every candidate, record every retry locus: agent-visible retry, SDK/client retry, gateway/provider retry, whole-run restart, at-least-once delivery, resume, and rewind.
5. Preserve terminal outcome decomposition: repaired-complete; safe-stop/escalate; incomplete/budget-exhausted; wrong-propagated/false-complete; plus failure->success rescue and success->failure disruption.
6. Continue authority-binding completeness: poisoned designated objects, optional authority-bearing fields, entity/value/cardinality/finality, unknown provider state, and multi-system postconditions against an independent reference contract.
7. Continue secondary frontiers from predecessor: verified-progress/backlog state, event-triggered terminal proof, reviewer rescue-vs-disruption, rewind target/restore, critic refresh, exact-update future replay, release risk spending, verifier refresh, admission×maintenance, semantic lineage/revocation, re-externalization, decision-influence audits, SymTrace/SymFail source, and CASS parameters.
8. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.

## Post-freeze repository drift / termination

Before repository writes, a SHA-only write-safety lookup observed repository main at `fd71ca90438d69c0515fab15bb4f34e20d20d115`, different from frozen semantic SHA `7dc93cb490359ce2c0c16fa1ec47907b31aba097`. No newer control, role-state, commit message, diff, or semantic payload was adopted. Substantive semantic work stopped immediately. This checkpoint contains only evidence gathered under the frozen tuple and records the exact next frontier for the next invocation.

`global_completion=false`
