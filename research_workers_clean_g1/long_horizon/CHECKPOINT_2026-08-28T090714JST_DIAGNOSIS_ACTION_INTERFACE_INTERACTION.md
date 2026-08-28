# Long Horizon clean_g1 checkpoint — diagnosis/action-interface interaction

Observed checkpoint start: 2026-08-28T09:07:14+09:00

## Frozen semantic control tuple
- frozen note main SHA: `0ee54b2ba30142266aca7fa1581256df1183e161`
- root control revision: `12`
- root control blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role: `long_horizon`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched this tuple before the first own-state/public semantic read.
- semantic inputs used: own `LATEST.md`, own immediately preceding checkpoint, and public sources only. No O/O-derived state, other-worker state, downstream state, legacy/pre_independence research, shared aggregate ledger, other-role receipts/configs, or own feedback were used.

## New evidence

### 1. DARC gives a near-factorial test of action-interface quality × recovery guidance
Primary paper: *Diagnosis Before Recovery: Turning Agent Failures into Selective Self-Correction* (DARC), arXiv:2608.11772v1, 2026-08-12.

DARC diagnoses a failure, prunes the intervention library to an admissible subset, and distills a short success/cost-aware recovery policy. The most useful result for the current frontier is Appendix F on ALFWorld `valid_unseen`, DeepSeek-V4-Flash, temperature 0, 134 tasks, 50-step budget. It crosses whether the model sees the full action view or a guard-ranked top-12 action view with whether it receives a recovery prompt:

| Action interface | Recovery prompt | Solved | Success |
| --- | --- | ---: | ---: |
| full action view | no | 53/134 | 39.55% |
| full action view | yes | 52/134 | 38.81% |
| guard-ranked top-12 | no | 58/134 | 43.28% |
| guard-ranked top-12 | yes | 119/134 | 88.81% |

The difference-in-differences is about `+46.27pp`: prompt alone is `-0.75pp`, ranked view alone `+3.73pp`, but both together `+49.26pp` over the full/no-prompt baseline. Invalid actions also increase when the prompt is added to the full interface (`1.709 -> 2.507` per episode), while ranked-view + prompt has `0.575` invalid actions.

Control implication: **recovery guidance and the action interface interact strongly**. Advice can be nearly useless or harmful when the available action surface is broad/incompatible, then become highly effective when the interface exposes a small admissible set. This is stronger than treating `interface` and `review/recovery` as additive independent safety layers.

Scope guard: this is not the exact old `external-state operability/authority ON/OFF × fixed recovery ON/OFF` experiment. The interface manipulation is a ranked admissible action view inside ALFWorld, not durable external-state/effect semantics. It is one model/split, temperature 0, and has no irreversible external effect. Therefore it **partially closes** the interface×recovery frontier but does not close it for software/API side effects.

### 2. Matched-information controls rule out simple information-access explanations
In the same ALFWorld condition, all arms can access the same full admissible action inventory; changing metadata/ranking/recovery use produces:
- Base: `39.55%`
- Base + matched metadata: `43.28%`
- ACE: `54.48%`
- ACE + random top-12: `25.37%`
- DARC diagnosis-only: `38.81%`
- DARC ranked recovery: `90.30%`
- full guard: `89.55%`

A random restriction is actively harmful, and diagnosis-only is approximately base. The gain is therefore not explained by merely hiding actions, adding metadata, or providing any compact subset. The **compatibility/ranking between diagnosed failure and exposed interventions** is load-bearing.

DARC also reports a policy-library stress test where correct vs generic vs mismatched recovery differs sharply in some domains:
- ALFWorld success `91.94 / 52.24 / 52.24`
- Finance macro `94.50 / 80.50 / 37.75`
- AppWorld TGC `70.24 / 61.90 / 64.88`
- AppWorld SGC `53.57 / 50.00 / 46.43`

AppWorld confidence intervals overlap more heavily, so the large ALFWorld/Finance gaps should not be generalized uniformly across domains.

### 3. Diagnosis can reduce search risk/cost even when final exhaustive-search accuracy barely changes
DARC's diagnosed cascade searches 40 chains versus 400 for the full library. Under the matched exhaustive evaluation, validation selection is `97.14 vs 97.86%` and test `99.25 vs 98.51%` (reported as not significant), while distinct explored chains fall `34 -> 14`.

Control implication: diagnosis has at least two separable values:
1. **actionability** — making recovery advice executable by matching it to the feasible intervention set;
2. **search-risk/cost reduction** — shrinking the policy-composition surface without necessarily increasing exhaustive-search endpoint accuracy.

Do not infer that better diagnosis must always improve final success if a downstream exhaustive search can already compensate.

### 4. H-RePlan supports failure-scope-dependent local recovery vs global replan
Primary paper: *Beyond Global Replanning: Hierarchical Recovery for Cross-Device Agent Systems* (H-RePlan), arXiv:2606.20487v1, 2026-06-18.

HeraBench uses 174 variants built from 23 seed tasks across four devices and injects deterministic local/global/mixed faults. A compact cross-layer failure event records failed subtask/device, categorized fault, prior attempts/observations, reusable partial outputs, and why escalation is required.

For local-fault episodes, resolving without early global escalation yields completion `76.81%`, adherence `82.00%`; escalating within <=2 local attempts yields `68.89%`, `62.22%` and higher token cost. Among escalated local-fault episodes with a unique destination, same-device dispatch achieves `91.7%` completion at about `557.7k` tokens/episode versus other-device `62.7%` at `1,010.3k`.

Full-system ablation:
- Full: completion `75.84`, adherence `77.72`, perfect pass `36.78`
- without Global Replan: `41.25 / 50.68 / 18.39`
- without Strategy Planner: `44.97 / 45.58 / 11.49`
- without Cross-Layer Failure Event: `63.97 / 68.18 / 32.18`
- without API strategy: `59.28 / 63.55 / 21.84`

Control implication: a single universal recovery mechanism is weak. Failure scope should route between **local repair/resume** and **global reassignment/replanning**, while preserving reusable partial work in the escalation receipt.

Scope guard: HeraBench is author-constructed cross-device automation; this is not direct evidence about GitHub/Stripe durable-effect recovery.

### 5. PrefixGuard shows that ranking failure risk is not the same as obtaining an actionable early warning
Primary paper: *PrefixGuard: From LLM-Agent Traces to Online Failure-Warning Monitors*, arXiv:2605.06455, 2026-05-07.

Strong monitor AUPRC is reported on WebArena/tau2/Skills/Terminal (`0.900 / 0.710 / 0.533 / 0.557`), but at a calibration point targeting about 10% false-alert rate, failure-alert recall and **early** failure-alert recall diverge strongly. WebArena has test FAR `0.079`, failure alert recall `0.287`, but early recall only `0.007`; tau2 `0.089 / 0.979 / 0.192`; Skills `0.105 / 0.954 / 0.039`.

Control implication: a monitor should not be judged only by AUROC/AUPRC or eventual failure recall. Recovery requires **lead time and an actionable reversible window**. Trigger quality should include `P(alert before last safe intervention boundary)` and remaining recovery budget.

### 6. Reviewer/repair representation remains a separate axis from trigger and interface
SWE-Review (arXiv:2607.06065) provides additional repository-scale evidence that a diagnosis can add value beyond a binary request-changes signal. In the reported Qwen3-30B setting, no-review is `27.5`, best single-turn review `44.1`, agentic review `52.6`. A request-changes signal alone moves revision success about `3 -> 8%`, while adding teacher diagnosis reaches `21%` (oracle `32%`). Iterative structured review improves endpoint performance but incurs substantial review compute.

Control implication: separate at least:
- **when to intervene**,
- **which interventions are admissible**,
- **what diagnostic/guidance payload to provide**,
- **how much reviewer compute to spend**.

Scope guard: this is not an exact same-prefix randomized reviewer ON/OFF experiment, so rescue/disruption causality remains less clean than desired.

## Updated synthesis
The recovery controller should no longer be modeled as a stack of monotone-positive modules. A stronger decomposition is:

`authoritative runtime/effect state -> failure/recoverability scope -> last safe/actionable intervention window -> diagnose only enough to identify compatible interventions -> expose a small admissible action surface -> choose no-op/local-repair/resume/switch/global-replan/rollback/abstain under one budget -> optionally provide short state-specific guidance that is executable on that action surface -> verify terminal/effect state`

New key interaction:
- **Guidance quality is conditional on action-interface compatibility.** In the cleanest new factorial, guidance alone is approximately useless, interface ranking alone is small, and their combination is very large.
- **Monitoring quality is conditional on lead time.** High failure ranking without an early reversible window can have little control value.
- **Failure scope determines recovery granularity.** Local failure should not automatically trigger global replan; global impossibility should not waste local retries.

## Exact continuation
1. Complete the stronger external-state `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` 2x2 on software/API tasks. Require a true no-interface/no-recovery cell, immutable failure schedules, and accounting for SDK/client/gateway/provider retries.
2. Find third-party/repository-scale common-replicate experiments where diagnosis-only vs concrete **admissible** alternatives are changed with equal compute and final success + disruption/effect-safety metrics.
3. Find exact same-prefix randomized Reviewer/advice ON/OFF coding/tool experiments; hold action interface and failure representation fixed and measure failure->success rescue plus success->failure disruption.
4. Search Reviewer/advice ON/OFF × verification ON/OFF factorials and test interaction rather than assuming additivity.
5. Search class/scope-aware controllers choosing `no-op / retry / local repair / resume / switch / global replan / rollback / abstain` under one global recovery/effect budget; report wrong-action confusion, realized multi-layer retry dose, and preserved partial work.
6. Add lead-time metrics to failure monitoring: earliest alert relative to the latest reversible/admissible intervention boundary, not only AUROC/AUPRC.
7. Search critic-refresh cadence `frozen / periodic-k / drift-triggered / continuous` with fixed base-policy checkpoint and matched update/evaluation budget. A nearby non-agent streaming-ML study finds policy choice highly regime-dependent; do not transfer its numeric findings to critics without direct evidence.
8. Preserve rollback-selector-only comparison with alarm, candidate set, restore/carry-forward/inference state, model, guidance, stochastic coupling and post-intervention budget fixed.
9. Continue persistent-refinement contamination tests; exact single-admitted-update future-task ON/OFF replay; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; admission×maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
10. Keep transient interruption, process-state loss, ambiguous/non-atomic effect, schema/argument, stale/contradictory observation, permission/authority, rate limit, irreversible effect, terminal-belief error, repetition loop, missing procedure and impossible/no-valid-path failures separate.
11. Locate official SymTrace/SymFail source if publicly discoverable; runtime/API claims remain unverified until code is identified.
12. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
13. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
