# Long Horizon clean_g1 checkpoint — interface/recovery decomposition + periodic critic grounding

Observed checkpoint time: 2026-08-28T04:02:09+09:00

## Frozen semantic control tuple
- frozen note main SHA: `a4c48b00398181c120612ebc1521572760f6101e`
- root control revision: `12`
- root control blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role: `long_horizon`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched this tuple.
- semantic inputs used: own `LATEST.md` at the frozen SHA plus public sources only. No O/O-derived state, other-worker state, downstream state, legacy research, shared ledger, or other-role receipts/configs were used.
- repository movement after the semantic barrier was used only for write-safety/CAS and was not adopted semantically.

## New evidence

### 1. Periodic critic grounding independently prevents stale-critic plateau, but cadence remains unmeasured
Primary source: TEMPO, arXiv:2604.19295, submitted 2026-04-21, https://arxiv.org/abs/2604.19295

TEMPO alternates policy refinement on unlabeled test questions with critic recalibration on labeled data. Its direct frozen-critic ablation reports that the frozen critic initially tracks the full system but plateaus after roughly 100 iterations as the policy evolves, while the alternating system continues to improve. This independently supports the prior ECHO result that critic validity is policy-relative rather than permanent.

Scope guard: TEMPO is test-time training for math/STEM/puzzle reasoning, not a tool/GUI/software agent recovery loop. It compares full alternating recalibration against a frozen critic; it does **not** sweep periodic interval, event-triggered refresh, or matched critic-update budgets. The paper explicitly leaves the trade-off between calibration frequency and compute efficiency for future work. Therefore it strengthens `frozen vs refreshed`, but does not solve critic-cadence selection.

### 2. AFT-Bench makes recovery-class separation more explicit and preserves the missing interface × recovery factorial
Primary source: Callability Is Not Operability, arXiv:2608.23628, submitted 2026-08-23, https://arxiv.org/abs/2608.23628

AFT-Bench holds task, backend, initial state, injected failure, controller, model and execution budget fixed while changing one interface mechanism. In pooled three-model results, removing resumable invocation under transient interruption changes recovery by the full `1.0000`, and removing durable state under process-local state loss also changes recovery by `1.0000`. Effect-aware semantics reduce duplicate effects by `0.5694`, strong effect semantics reduce unsafe commits by `0.5000`, while terminal verification reduces incorrect terminal claims by `0.2778` and is more model-dependent.

The important control implication is not that every workload needs every mechanism. The paper explicitly separates resumability, durable state, effect semantics and verification because they solve different ambiguity classes. This reinforces a recovery controller that first classifies the failure/ambiguity class, then exposes only the continuation semantics required for that class.

Open gap preserved: AFT-Bench changes interface semantics while holding controller fixed; it does not cross `weak/legacy interface vs operable interface` with `identical fixed recovery OFF vs ON` as a common-replicate 2×2. Thus it still cannot answer how much sophisticated recovery remains valuable after interface ambiguity is removed.

### 3. Verify-before-retry still lacks the fourth cell, and retry can be harmful once verification exists
Primary source: Verified Tool Calls Improve LLM Agent Reliability Under Non-Atomic Failures, arXiv:2608.02645, submitted 2026-07-31, https://arxiv.org/abs/2608.02645

The paper's medium-fault ablation compares three conditions on `activate_customer`:
- retry-only baseline: about `58%` task success, `42%` duplicate actions;
- verification-only: about `80%` task success, `20%` duplicates;
- verify-before-retry: about `72%` task success, `28%` duplicates.

Thus, in this controlled run, adding retry **after** postcondition verification makes both success and duplicates worse than verification-only. This supports treating retry as a competing action (`no-op / verify / wait / reconcile / resume / retry / rollback`) rather than an automatic second layer.

However the ablation has no `verification OFF + retry OFF` cell. Therefore it cannot estimate the full verification×retry interaction or distinguish whether verification-only beats a passive/no-recovery controller. The desired complete 2×2 remains missing.

### 4. GUI evidence shows verifier, loop-recovery and search are distinct load-bearing components, but not interaction-isolated
Primary project source: VLAA-GUI official project page, https://ucsc-vlaa.github.io/VLAA-GUI/ ; arXiv:2604.21375.

On WindowsAgentArena with Gemini 3 Flash at a 50-step budget, the official ablation reports:
- full VLAA-GUI: `60.4%`;
- minus Completeness Verifier: `51.3%`;
- minus Loop Breaker: `52.6%`;
- minus Search Agent: `49.4%`.

The project also reports that the Loop Breaker reduces wasted steps for Gemini 3 Flash from `4.9%` to `2.8%`. This is useful independent GUI-agent evidence that terminal verification, recovery from loops, and external procedural search address different failure modes.

Scope guard: these are one-component-at-a-time ablations, not a complete factorial. They do not isolate reviewer/reflection × verifier interaction on identical prefixes, nor rescue vs disruption on an explicit benign/success cohort.

## Current synthesis delta
- The upstream ordering is now more strongly supported as: `interface-state distinguishability / safe continuation semantics -> failure-class identification -> choose among no-op/verify/reconcile/resume/retry/replan/rollback/reviewer -> terminal evidence`.
- Runtime-like mechanisms (resume/durable state) can dominate specific operational failures and appear model-invariant in the tested AFT-Bench cells; policy-like mechanisms (verification/critic) show more model dependence.
- Critic/reviewer freshness remains a separate longitudinal variable. ECHO gives direct agentic stale-critic harm; TEMPO independently shows frozen-critic plateau under evolving reasoning policy. Neither gives the matched cadence sweep needed to choose refresh timing.
- Reliability modules are not safely assumed additive. Verified Tool Calls directly shows verify+retry worse than verify-only in one controlled setting; prior guard-interaction evidence remains compatible with this.

## Exact continuation
1. Find or construct from a published benchmark a common-replicate `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` 2×2, including the true no-recovery/no-verification cell. Measure task success, duplicate/unsafe effects, rescue, disruption and compute/tool-call cost.
2. Search critic-refresh cadence experiments that hold a base policy checkpoint and total critic-update/evaluation budget fixed while comparing `frozen / periodic-k / drift-triggered / continuous`; prioritize software/tool/GUI agents, then reasoning TTT only as auxiliary evidence.
3. Search same-prefix `reviewer/reflection/advice ON/OFF × verification ON/OFF` factorials with both failed prefixes and benign/success prefixes, so failure→success rescue and success→failure disruption are both observed.
4. Inspect public implementations of Verified Tool Calls / VLAA-GUI only read-only to determine whether missing factorial cells can be run without changing semantics; do not treat runnable possibility as existing evidence.
5. Preserve rollback-selector-only comparison with alarm, candidate checkpoints, restore/carry-forward/inference state, model, guidance, stochastic coupling and post-intervention budget fixed.
6. Keep recoverability/action classes separate: transient interruption, process-local state loss, ambiguous effect, schema error, authority/permission drift, rate limit, irreversible effect, terminal-belief error, repetitive loop and missing procedural knowledge should not be pooled into one generic `failure`.
7. Continue exact single-admitted-update future-task ON/OFF frozen replay; randomized reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; admission × maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
8. Locate official SymTrace/SymFail source if publicly discoverable; paper methodology remains usable evidence but runtime/API claims stay unverified until code is identified.
9. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
10. Preserve exact tested scope and nonempty frontier; this checkpoint is not global completion.
