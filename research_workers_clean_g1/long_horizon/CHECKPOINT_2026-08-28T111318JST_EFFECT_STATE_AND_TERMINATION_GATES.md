# Long Horizon clean_g1 checkpoint — effect-aligned state, runtime guarantees, and terminal evidence gates

Checkpointed at: `2026-08-28T11:13:18+09:00`

## Frozen control tuple

- frozen semantic source main SHA: `14b5ce14b7090cdd3e71ce98ff45795d70ccb63b`
- root control revision: `13`
- role config revision: `5`
- root blob: `cc9b1f22f0fda9cf26296057fd35b19a090618b4`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched before reading own state/public sources.
- semantic inputs used after freeze: own `research_workers_clean_g1/long_horizon/LATEST.md` at the frozen SHA and public primary sources only. No O/O-derived state, other worker state, downstream state, legacy/pre_independence material, shared aggregate ledger, or other-role receipts/configs were used.

## Main delta

### 1. A fresh GUI-agent ablation says the highest-value long-horizon state is effect-aligned state, not raw trajectory persistence.

Primary: Li, Paik, Sui, **LocalLSTC: A Long Short-Term Control Architecture for Locally Deployed GUI Agents**, arXiv:2608.25777, submitted 2026-08-26. https://arxiv.org/abs/2608.25777

LocalLSTC externalizes persistent control as `(active subgoal, subgoal-aligned execution evidence, runtime feedback)` and separates it from a bounded per-step execution commitment. Under a fixed Qwen3.5-9B planner on OSWorld, the full system reports SR-100 `49.1`; removing Long-to-Short planning lowers it to `36.4`, and removing Short-to-Long control lowers it to `41.5`.

The strongest individual ablation is **Step Abstraction**, which evaluates the observed execution outcome against the intended effect of the current commitment and writes a subgoal-aligned evidence increment. Removing it lowers SR-100 from `49.1` to `31.6` (`-17.5pp`). Removing the persistent subgoal gives `38.0`; removing state-conditioned routing `40.7`; removing Final Verification `40.3`; removing stall/loop handling `45.1`; removing candidate proposals `40.7`; removing the multi-action list `43.5`.

The runtime-event analysis is especially informative: stall/repetition incidence is almost unchanged (`4.5%` full, `4.3%` w/o L2S, `4.6%` w/o S2L), but conditional post-event evaluator score is `34.3%` full versus `18.8%` and `11.8%`. After recovery entry, full scores `34.0%` versus `20.9%` w/o L2S; after rejected termination, `38.9%` versus `23.1%`. This points to a **post-event state/response advantage**, not merely more event detection.

Scope guard: these are OSWorld GUI-agent point estimates under a local planner architecture; several mechanisms change together in grouped ablations, Step Abstraction and Final Verification themselves call the planner backbone under dedicated prompts, and the study does not establish that the same numeric effects transfer to software/API agents or frontier backbones.

### 2. Tool-interface mechanisms should be split into runtime guarantees versus policy aids; they should not share one monotonic `interface quality` score.

Primary: Wang, **Callability Is Not Operability: Controlled Interface Interventions for LLM Agents**, arXiv:2608.23628, submitted 2026-08-23. https://arxiv.org/abs/2608.23628

AFT-Bench holds task, backend, initial state, fault realization, controller, model, and execution budget fixed and varies interface semantics. Across three adaptive model families and six workloads (`2,385` result rows), the pooled primary contrasts report:

- resumable invocation under transient interruption: `+100pp` recovery;
- durable execution state under process-local state loss: `+100pp` recovery;
- effect-aware semantics after post-commit response loss: `-56.9pp` duplicate effects;
- strong effect semantics under stale-state/permission drift: `-50.0pp` unsafe commits;
- postcondition verification: `-27.8pp` incorrect terminal claims;
- selective discovery: about `4,013` fewer exposed tool-context tokens while meeting the prespecified recall noninferiority criterion.

The important finer point is model interaction: recovery mechanisms were stable across the three model families, while marginal verification benefit was strongly model-dependent. The paper explicitly interprets this as some mechanisms behaving more like **runtime guarantees**, while others partially substitute for model policy. Its formal distinction is useful: an interface can either **distinguish hidden states** by exposing authoritative evidence, or **stabilize continuation** through idempotency/guarded effects so the same continuation is safe across hidden states.

This closes part of the prior frontier: runtime resumability/durability/effect semantics have mechanism-level paired evidence under targeted faults. It does **not** close `operable runtime ON/OFF × identical agent-side recovery ON/OFF`; the interface and recovery policy are still not fully crossed as independent axes.

### 3. Schema correctness is a negative control: contract adherence can improve while semantic action quality and task success do not.

Primary: Sigdel & Baral, **Schema First Tool APIs for LLM Agents**, arXiv:2603.13404. https://arxiv.org/abs/2603.13404

In its fully crossed constrained pilot (Qwen2.5-0.5B Instruct, 3 seeds, conditions prose / JSON Schema / JSON Schema+structured diagnostics, budgets `3/5/8/12`, 276 scored runs), task success is `0.0` in every condition and budget. Average invalid calls fall from `5.39` under prose to `3.72` under both schema conditions, and execution failures fall from `0.54` to `0.00`; however semantic misuse rises from `0.93` to `3.03`. Increasing the budget increases invalid and semantic misuse counts without yielding success.

Scope guard: this is deliberately a tiny-model, synthetic software-sandbox, zero-success pilot. The useful conclusion is narrow: **format/contract validity and semantic continuation quality are distinct endpoints**. Do not use these magnitudes as deployment estimates.

### 4. Deterministic evidence-gated termination can dominate an LLM critic on unsupported completion, but its recovery path is materially more expensive.

Primary: Liu, **When May an Agent Stop? Evidence-Carrying Termination for Tool-Using LLMs**, arXiv:2608.23623, submitted 2026-08-22. https://arxiv.org/abs/2608.23623

ECT separates generation from authorization to stop. A proposed COMPLETE certificate must bind every required answer slot to validated in-scope receipts, task/ledger digests, allowed closed transforms, and deterministic replay. In the fresh prespecified closed-loop primary scope, on 66 recoverably incomplete trajectories:

- premature unsupported termination: ECT `0/66` versus controller+LLM critic `40/66`;
- supported completion within budget: ECT `31/66` versus controller+LLM critic `26/66`;
- successful recovery: ECT `18/66` versus controller+LLM critic `12/66`.

Across the matched 132 clean+recoverably-incomplete trajectories, supported completion is `97/132` for ECT versus `92/132` for the controller, meeting its prespecified noninferiority margin.

The cost side is nontrivial. On recoverably incomplete trajectories, ECT averages about `17,561.5` tokens, `7.96s` latency, and `$0.00888`, versus about `8,254.7` tokens, `3.27s`, and `$0.00396` for the controller; ECT ends `35/66` incomplete cases in `BUDGET_EXHAUSTED` and `31/66` COMPLETE. This suggests deterministic completion evidence can be a strong **authorization boundary** while still needing cost-aware deployment or cheaper contracts/verifiers.

Scope guard: ECT's benchmark is fully synthetic across six tool-use families and controlled termination faults. Its guarantee is relative to the trusted task contract and evidence adapter: it certifies trace support and replayability, not external truth, effect safety, authenticity, or alignment. Do not generalize the zero-unsafe result beyond that declared boundary.

The paper's official source/result artifacts are attached directly to the arXiv submission, including verifier code, tests, frozen manifests, and per-trajectory closed-loop records. This raises its implementation/reproducibility status above paper-only evidence, but no independent replication was established in this run.

### 5. The current Agent-First Tool APIs cost contradiction remains unresolved in its latest manuscript; keep those economics quarantined.

The current paper version still reports in its end-to-end table that the Agent-First arm has higher latency/token use (`3.1 -> 4.6s`, `1840 -> 2520`), while a later overhead section claims net per-task savings of `-1.3s` and `-680 tokens`. No raw-log or corrected-source resolution was found in this run. Continue using its success/recovery architecture evidence only; do not use its latency/token savings in scheduler economics.

## Updated synthesis

A more precise long-horizon control stack now separates four layers:

1. **Runtime continuation guarantees** — stable invocation identity, resumability, durable state, idempotency/effect identity, guarded writes, authority/freshness and postcondition evidence. These remove operational ambiguity or make continuation safe despite ambiguity.
2. **Effect-aligned persistent control state** — persist the current subgoal, the intended-effect-versus-observed-outcome evidence, and runtime feedback. Avoid treating raw history, schema validity, or generic summaries as equivalent state.
3. **Conditional recovery policy** — only after the first two layers, choose no-op/verify/reconcile/resume/retry/switch/rollback/replan/reviewer/abstain based on failure class and positive intervention advantage. A recovery mechanism is not a monotonic add-on.
4. **Terminal authorization** — where the consequence justifies it, require completion evidence that is independently checkable against the trace/world contract rather than trusting a model's `DONE` or critic approval. Account for proof/recovery cost explicitly.

The key new design variable is therefore **state transition quality**, not merely memory size or reviewer quality: each bounded commitment should have an intended effect, an authoritative observation of what happened, an update rule for persistent control, and a separately governed terminal claim.

## Negative evidence retained

- More formal tool schemas can reduce invalid calls without increasing final success, and can coexist with more semantically unproductive actions.
- More budget can produce more invalid/semantic actions without rescue.
- Verification/reviewer effects can be model-dependent even when runtime recovery guarantees are stable.
- Deterministic terminal proof can be safer yet materially more expensive on difficult/incomplete cases.
- Grouped GUI control improvements do not prove that every subcomponent generalizes outside the tested benchmark/backbone.

## Exact continuation / nonempty frontier

1. Find or construct the still-missing **external-state runtime guarantee ON/OFF × identical fixed recovery ON/OFF** 2x2. Split the interface axis further into (a) state distinction, and (b) continuation stabilization; count hidden SDK/client/gateway/provider retries.
2. Search software/API component factorials that independently toggle structured `next_actions`, authoritative state evidence, idempotency/effect identity, preview, and postcondition verification while keeping the recovery policy fixed.
3. For LocalLSTC-style control, find an ablation that compares LLM Step Abstraction against a cheaper deterministic/typed outcome encoder under the same persistent subgoal and routing; measure final success plus token/time cost.
4. Find a matched **always-on terminal proof vs risk/event-triggered terminal proof** experiment. ECT's strong safety comes with large incomplete-case token/latency cost; test whether proof can be reserved for irreversible/high-impact or low-confidence COMPLETE proposals without increasing unsupported termination.
5. Find ECT-like completion certificates on real software/API environments with external-effect identity/authority, not only trace support in synthetic worlds.
6. Compare LLM Final Verification and deterministic evidence/postcondition verification under the same GUI/software-agent state, especially on supported clean trajectories and recoverably incomplete ones.
7. Continue exact same-prefix Reviewer/safety-monitor ON/OFF experiments measuring both failure->success rescue and success->failure disruption; compare event-triggered review against every-action review under the same base/reviewer.
8. Continue rewind factorization: availability, target selector, rewind memory/guidance, context/environment/inference restore, matched realized recovery dose.
9. Require failure monitors to report alert lead time relative to the last reversible/admissible intervention boundary, not only AUROC/AUPRC.
10. Continue critic refresh cadence `frozen / periodic-k / drift-triggered / continuous` under matched update/evaluation budget.
11. Continue persistent-refinement frontiers: exact single-admitted-update future-task ON/OFF replay; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; admission×maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
12. Keep fault classes separate: transient interruption, process-state loss, ambiguous/non-atomic effect, schema/argument, stale/contradictory observation, permission/authority, rate limit, irreversible effect, terminal-belief error, repetition loop, missing procedure, impossible/no-valid-path.
13. Locate official SymTrace/SymFail source if independently discoverable; paper-specification claims remain separate from code-verified runtime claims.
14. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
15. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
