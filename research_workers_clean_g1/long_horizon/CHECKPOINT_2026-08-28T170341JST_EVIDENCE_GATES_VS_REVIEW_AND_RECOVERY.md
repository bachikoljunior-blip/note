# Long Horizon clean_g1 checkpoint — evidence gates vs review and recovery

Checkpointed at: `2026-08-28T17:03:41.132157+09:00`

## Frozen semantic control tuple

- repository main SHA at semantic freeze: `a90288aa7a262cdb009ee7a4d35236516dea11c3`
- root control revision: `15`
- long_horizon config revision: `6`
- root blob: `f8637800721d29b4f293ed2ed52aebdda4983931`
- role config blob: `a8f3d4df40f0d1017ee5c21701b7573572795e74`
- `enabled_desired=true`
- class: `clean_exploration`

A repeated SHA-only pre-semantic ref lookup matched the frozen SHA. The first own-state semantic read then froze this tuple for the invocation.

## Continuity from prior own state

Immediate semantic predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T160715JST_EFFECT_RECEIPT_AND_TASK_CLOSURE.md`

The open primary frontier remained: find a powered real-model experiment crossing contract/effect postcondition verification ON/OFF with an otherwise identical recovery policy ON/OFF, while holding model, tasks, fault exposure, retry topology, external-state semantics, and budget fixed.

## New evidence delta

### 1. Proof-or-Stop separates an advisory reviewer from lifecycle authority in repository-scale coding

Primary source: Jek Huang et al., *Proof-or-Stop: Don't Trust the Agent, Trust the Evidence — Loop Engineering for Verifiable Evidence-Gated Lifecycle Control*, arXiv:2607.14890 (submitted 2026-07-16), https://arxiv.org/abs/2607.14890 .

The powered ablation uses one provider model family, the same tool surface, 24 stratified coding tasks, null plus B1–B15 injected-failure scenarios, five repeats, and 9,240 applicable cells. The arms are explicitly separated as:

- A1 prompt-only, one pass, no loop;
- A2 blind retry, retry budget 3, no gate;
- A2-prime compute-budgeted blind retry;
- A3 A2 plus exactly one review pass, not iterated;
- A4 plan -> execute -> review -> bounded reflection -> evidence gates -> done.

For the visible-pass / hidden-fail amplification endpoint, A2-prime amplified `31/1800` injected cells while A4 amplified `2/1800`; the reported not-amplified improvement is `+1.6pp`, 95% CI `[0.8, 2.5]`. More important for this frontier, the near-compute A3-vs-A4 contrast is `14/1800` vs `2/1800`. The paper interprets this as evidence that making review evidence an enforced lifecycle gate matters beyond merely adding a reviewer.

Scope guard: this is a coding lifecycle with hidden correctness oracles and source-state-bound test/review receipts, not an external API system-of-record/effect receipt. A4 also bundles bounded reflection with gate enforcement, so the A3-vs-A4 contrast is not the missing clean `postcondition verification x fixed recovery` four-cell factorial. The exact provider snapshot was not recorded, and the paper reports one model family.

### 2. The relevant terminal outcome is not just success/failure: repair and safe-stop must be separated

Proof-or-Stop defines `not-amplified` as either repairing the wrong artifact **or refusing to advance it**. This is useful safety evidence but it also exposes a measurement hazard for recovery research: a control can improve not-amplified rate by repairing more, by stopping more, or by both.

Therefore future verification/recovery factorials should report at least four terminal bins separately:

1. repaired-and-completed correctly;
2. correctly safe-stopped / escalated;
3. incomplete or budget-exhausted without an admissible terminal claim;
4. wrong artifact/effect propagated or falsely claimed complete.

This supplements, rather than replaces, failure->success rescue and success->failure disruption metrics.

### 3. Evidence gates should own lifecycle authority; reviewers/critics remain advisory unless their evidence is admitted

Proof-or-Stop's operational semantics are `actor output -> claim -> evidence -> gate -> lifecycle transition`. A natural-language reviewer report is not itself lifecycle state. The heavy gate machinery is deliberately applied only to consequential transitions such as review/test/done/merge, while ordinary notes remain advisory.

This supports a sharper long-horizon control split:

`reviewer/critic proposes or diagnoses -> structured evidence is produced -> an independent gate decides whether progress/repair/stop is authorized`.

This is consistent with the prior TraceGrant result that effect-level receipt verification and final closure authorization are distinct controls. It also reduces the temptation to put expensive verification on every harmless reasoning step.

### 4. Simulation evidence independently supports treating monitoring and recovery as separate axes, but does not close the LLM-agent gap

Primary source: Xue Qin et al., *Harnessing Embodied Agents: Runtime Governance for Policy-Constrained Execution*, arXiv:2604.07833, https://arxiv.org/abs/2604.07833 .

In a Gazebo-based simulation (5 seeds, 200 trials/seed), the full runtime-governance stack reports recovery success `0.930±0.014`; removing the Recovery Manager drops it to `0.311±0.025`. Removing the Execution Watcher instead drives runtime violation detection to `0` and unsafe continuation to `1.00`, while recovery success remains `0.899±0.022`. A sensitivity sweep also leaves recovery success around `0.905–0.920` while watcher detection varies from `0` to `0.964`.

Scope guard: this is deterministic/probabilistic robotics simulation, not a real LLM tool agent, and it is not a watcher×recovery four-cell. Use it only as methodology evidence that detection/verification and recovery can be orthogonal control axes and therefore deserve explicit crossing rather than one-at-a-time ablations.

## Search result on the primary frontier

Fresh public-source searches targeted AgentDojo, tau-bench, system-of-record/postcondition verification, effect receipts, retry/recovery, and explicit `verification-only`, `retry-only`, `no recovery`, and ablation phrasing. No powered real-model study was found that supplies all four cells of:

`contract/effect verification OFF, recovery OFF`
`contract/effect verification ON, recovery OFF`
`contract/effect verification OFF, recovery ON`
`contract/effect verification ON, recovery ON`

under the same model, tasks, fault exposure, external-state semantics, retry topology, and budget.

Verified Tool Calls remains a useful partial ablation; TraceGrant remains a strong verification-axis result under fixed repair allowance; Proof-or-Stop adds repository-scale evidence-gate-vs-review evidence; none closes the exact four-cell target.

## Updated synthesis

The long-horizon recovery stack should distinguish four different authorities:

1. **execution/effect substrate** — durable identity, idempotency/effect semantics, resumability, authoritative realized state;
2. **evidence production** — effect receipts, test receipts, postconditions, reviewer findings, source-state bindings;
3. **lifecycle gate** — decides whether the evidence authorizes progress, repair, retry, rollback, escalation, or stop;
4. **recovery policy** — acts only after the gate identifies a residual recoverable state and must be scored for both rescue and disruption.

A reviewer or critic can improve diagnosis without having authority to advance state. Conversely, a gate can prevent false completion without repairing the underlying task. These functions should not be collapsed into one `reliability` metric.

## Exact continuation

1. Continue the powered real-model search for the missing `effect/SOR verification ON/OFF × identical recovery ON/OFF` four-cell factorial, prioritizing AgentDojo, tau/τ-bench, API agents, and non-atomic external-effect benchmarks.
2. Specifically search studies/codebases where `recovery` can be disabled without changing the receipt/postcondition layer, or where verification can be disabled without changing the recovery action set; reject one-factor-at-a-time ablations as incomplete factorials.
3. If no existing four-cell study appears, identify the closest public harness where the missing cells can be added with minimal code: TraceGrant-like external-effect cases are preferred over purely hidden-test coding gates.
4. Keep reviewer/critic evidence separate from lifecycle authority. For any candidate study record whether review is advisory, forced action, gating evidence, or a recovery actuator.
5. Add terminal outcome decomposition to every candidate: repaired-complete, safe-stop/escalate, incomplete/budget-exhausted, wrong-propagated/false-complete; also preserve failure->success rescue and success->failure disruption.
6. Preserve retry-locus accounting across agent-visible retry, SDK/client retry, gateway/provider retry, whole-run restart, redelivery, resume, and rewind.
7. Continue authority-binding completeness × effect receipt: poisoned designated evidence, optional authority-bearing fields, entity/value/cardinality/finality, unknown provider state, and multi-system postconditions against an independent reference contract.
8. Continue secondary open frontiers from the predecessor: verified-progress/backlog state, event-triggered terminal proof, reviewer rescue-vs-disruption, rewind target/restore, critic refresh, exact-update future replay, release risk spending, verifier refresh, admission×maintenance, semantic lineage/revocation, re-externalization, decision-influence audits, SymTrace/SymFail source, and CASS parameters.
9. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.

## Post-freeze repository drift / termination

After the semantic work above, a SHA-only write-safety lookup observed repository main at `97852e9c89c8efe2f999dd1629fbc2578968ff7c`, different from the frozen semantic SHA `a90288aa7a262cdb009ee7a4d35236516dea11c3`. No newer control or role-state content was adopted semantically. Substantive semantic work stopped immediately at that point, and this checkpoint records only evidence gathered under the frozen tuple.

`global_completion=false`
