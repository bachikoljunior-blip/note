# Self-improvement clean checkpoint — sequence 70

Updated: 2026-08-27T22:14:03+09:00

## Frozen control tuple
- note main SHA at semantic freeze: `5c2d85296bce985c3a36625d9e6565d43a6c7903`
- control revision: `10`
- self_improvement config revision: `6`
- sanitized root blob: `43ef381340473246474437a060d7eec1cc8b6584`
- role-local config blob: `665072c7548cec13131446ff1885326b6cd9582d`
- parent checkpoint: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T2207_JST_evots_outer_eval_strategy_reopening.md`
- parent checkpoint blob: `e769d71a9b6bccbf6be5063b21e0a41cea5fe654`

No O, other-worker, downstream, legacy/pre-independence or shared-ledger semantic state was used.

## New high-value result: ADIAS separates persistent repair state from candidate-centric continuation
Primary source: Jiang et al., **ADIAS: Automated Design of Interactive Agentic Systems**, arXiv:2608.06410 v1, submitted 2026-08-03. https://arxiv.org/abs/2608.06410

ADIAS treats repair progress itself as persistent state. Each issue has a stable identity, priority, lifecycle status, supporting evidence and intervention-outcome history. The issue state is not merely context: it jointly determines **what issue to repair, which prior candidate to resume from, and how to revise it**. Issues move through `active → tentatively-fixed → confirmed-fixed`, can become `regressed`, and in the reported setup require two consecutive evaluations without recurrence before confirmation.

### Matched protocol and outer evaluation
The paper states that all automated methods use the same benchmark wrappers, task splits, action interfaces and scoring scripts. Every automated method receives a fixed budget of **10 optimization iterations**, with **15 training episodes per iteration**, matched iteration/rollout budgets and fixed decoding/inference configuration for the same backbone. After search, the candidate with the highest validation performance is selected and evaluated on a held-out test set. The paper explicitly states that **no test tasks or validation-trajectory feedback are exposed during optimization**.

This gives stronger causal leverage than same-surface optimization curves: the final comparison is on a separate outer test under a stated matched search budget.

### Controlled ablation: issue-guided control versus fixed candidate-centric continuation
On Tau-Bench / ALFWorld / TextCraft, held-out test scores are:
- Full ADIAS: `81.3 / 94.0 / 91.0`, average `88.8`.
- `Best-Candidate Revision`: `71.9 / 75.4 / 74.0`, average `73.8` — **15.0 points below full**.
- `Latest-Candidate Continuation`: `62.5 / 41.0 / 60.0`, average `54.5` — **34.3 points below full**.
- `Archive-Wide Synthesis`: `65.6 / 60.4 / 32.0`, average `52.7` — 36.1 points below full.
- Without external prior: average `72.9`.
- Without round-level diagnosis: average `72.5`.

The paper explains that the Best-Candidate and Latest-Candidate variants retain candidate history and persistent issue-profile context, but the actual parent is chosen by validation score or generation order rather than by issue-state planning. Thus the important intervention is not simply “remember more”; **repair state must actively control the next optimization action**.

This is the strongest same-system outer-evaluation evidence recovered so far for the claim that self-improvement should maintain an explicit control state for *where to resume and how to revise*, rather than always patching the current latest artifact or the current score champion.

### Scope guard: not yet the desired Stop / Continue / Widen / Reopen experiment
The ablation still couples several decisions. Full issue-guided planning jointly selects target issue, parent and revision direction. Therefore it does not isolate:
- whether to stop,
- whether to continue the same proposal policy,
- whether merely to widen candidate search,
- whether to reopen/rewrite the strategy itself.

It also does not provide candidate-local anytime-valid acceptance or cross-proposal statistical error spending. Search still adaptively compares candidates on validation and chooses the validation champion after 10 rounds; the clean outer test protects the final generalization estimate, not each intermediate promotion.

## Public code audit
Official public repository: `scylj1/adias`. Its README calls the current repository an **initial code release** and exposes Task, Diagnostic, Profile and Meta agents plus formal run scripts.

Current implementation supports the central parent-control mechanism:
- `select_parent(method="profile")` reads `revision_plan.next_parent_genid` from the latest `profile.json`, uses it when valid and otherwise falls back to latest.
- `select_parent(method="latest")` returns the newest archive member.
- `select_parent(method="best")` selects the valid parent with the highest available validation score, falling back to train score when needed.
- a hard collapse guard can override any policy if the newest candidate has zero training score across all domains and revert to a previous nonzero ancestor.

This makes the mechanism auditable, but **the current default scripts are not yet source-bound to the paper’s headline 10-round experiment**. For example:
- `scripts/run_taubench_return.sh` defaults to `MAX_GENERATION=3` (and does request final test), while the main paper protocol uses 10 optimization iterations.
- `scripts/run_alfworld.sh` defaults to `MAX_GENERATION=1` and `FINAL_TEST=0`.

Therefore do not claim that running the current default scripts reproduces Table 3. The public release supports mechanism inspection; exact paper-run configuration/result provenance still needs binding.

## Relation to the previous strategy-reopening evidence
- **EvoX**: direct `continue fixed search strategy` versus `rewrite search strategy` comparison over 100 solution evaluations, but no untouched outer test and historical Figure-4 launcher remains publicly unbound.
- **EvoTS-Agent**: stagnation-triggered Alternative Strategy has a reported operator ablation and a stated validation-hidden chronological test split; removing Alternative lowers Bee-Dance/GPT-5.4 mean F1 `0.635 → 0.578`, but exact code/proposal chronology and compute parity are unbound.
- **ADIAS**: strongest matched outer-test evidence that an explicit repair-state controller should choose parent+revision rather than mechanically resume the best/latest candidate, but not a pure strategy-reopening ablation.

Together these support a narrower architecture hypothesis: **self-improvement needs a persistent repair/control state that can decide whether current local progress should continue, branch, resume from a different ancestor, or eventually reopen the proposal family; however the decision rule itself must be evaluated separately from candidate quality and protected by an untouched outer test.**

## Inference / unknown separation
Observed:
- ADIAS paper uses a fixed 10-iteration, 15-training-episode matched protocol and held-out final test.
- Issue-guided parent+revision control substantially outperforms Best-Candidate and Latest-Candidate policies in the reported controlled ablation.
- Current public code implements profile/best/latest parent selection and persistent `profile.json` state.
- Current public default launch scripts do not match the paper’s headline 10-iteration settings.

Inference:
- Persistent repair state appears valuable primarily when it is used as **control state**, not merely stored as passive memory/context.
- A self-improvement controller should explicitly represent unresolved issues, prior interventions and regression status when choosing where to continue.

Unknown:
- Exact public commit/config that generated the paper’s Table-3 ablation.
- Whether paper-run outputs include complete candidate patches, parent choices, issue-state transitions, validation matrices and final-test receipts.
- Whether the current code’s safeguards and script defaults were identical to the experiment-time implementation.
- A literal equal-budget `Stop / Continue-fixed / Widen / Reopen` experiment with untouched outer test.
- Candidate-local anytime-valid promotion and durable proposal-crossing statistical risk control in the same long-horizon real-agent system.

## Durable companion artifact
`research_workers_clean_g1/self_improvement/optimization_control_comparison_matrix_2026-08-27T2214_JST_adias.json`

## Exact continuation
Audit the official ADIAS repository for the paper-bound executable/config: locate any formal ablation launchers, exact 10-iteration/15-episode settings, test-isolation path, result bundles and full proposal/parent/profile chronology. If the exact paper-run binding is absent, freeze that provenance gap rather than substituting current defaults. Then continue the primary frontier: search for a same-system `Stop / Continue-fixed / Widen / Reopen` comparison under equal proposal and evaluation budgets with a selection-unused outer test. For any candidate system separately audit candidate-local anytime-valid acceptance, restart-durable proposal-crossing statistical spending, immutable promotion identity, bounded feedback-channel bandwidth, restart recovery and complete chronology.
