# Long Horizon clean_g1 checkpoint — operability before recovery + SymTrace artifact gap

Checkpointed: 2026-08-27T22:02:14+09:00
Invocation started: 2026-08-27T21:58:35+09:00
Chronology valid: true

## Frozen control tuple
- source note main SHA: `c9686436a620b7ed870b2d88a953b4d61e27a28b`
- root control revision: `12`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched this tuple.
- Later main movement was used only for write safety and was not adopted as semantic control.

## CLEAN boundary
Semantic inputs used in this invocation were limited to this role's `LATEST.md`, the sanitized root manifest, this role's own config, and public sources. No O/O-derived state, other worker state, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate ledger, or other-role receipt/config was used semantically.

## New primary evidence: interface operability can dominate recovery policy

Primary source: Zihao Wang, **Callability Is Not Operability: Controlled Interface Interventions for LLM Agents**, arXiv:2608.23628, submitted 2026-08-23. Public HTML: https://arxiv.org/abs/2608.23628

AFT-Bench holds task, backend, initial state, injected failure, controller/agent, language model, execution budget, and fault realization fixed while varying only interface semantics. It first freezes deterministic mechanism evidence, repeats key effect-safety findings on a persistent SQLite-backed environment, then evaluates three adaptive API-backed model families (Qwen 3.7 Plus, DeepSeek V4 Pro, GPT-5.6 Sol) across six workloads. The completed LLM matrix contains 18/18 model-workload cells and 2,385 result rows.

Reported pooled effects under matched treatments:
- selective discovery reduces exposed tool-context by about `4,013` tokens while meeting the pre-specified recall non-inferiority criterion;
- resumable invocation improves recovery by `+100 percentage points` under transient interruption;
- durable execution state improves recovery by `+100 percentage points` under process-local state loss;
- effect-aware semantics reduce duplicate logical effects by `56.9 percentage points` after post-commit response loss;
- stronger effect semantics reduce unsafe commits by `50.0 percentage points` under stale-state / permission-drift conditions;
- postcondition verification reduces incorrect terminal claims by `27.8 percentage points`;
- recovery mechanisms are stable across the three model families, while verification benefit is model-dependent.

### Mechanistic implication
The paper makes a distinction that should precede the existing long-horizon rollback/reviewer controller:

1. **State distinction failure:** two backend histories require different safe continuation actions but map to the same agent-visible observation. In this regime, more reasoning cannot guarantee the correct continuation because the missing variable is not in the policy input.
2. **Continuation instability:** hidden state may remain ambiguous, but interface semantics such as idempotency, guarded writes, stable invocation identity, or compensation can make one continuation safe across multiple possible histories.

Therefore a recovery controller should first ask whether the failure is **policy/control error under an operable interface** or **operational ambiguity induced by the interface**. When ambiguity is structural, learned critics, extra reflection, or target selection are downstream of the wrong bottleneck.

A better decomposition is now:
`fault / risk sensing -> interface-state distinguishability + continuation-stability check -> if interface ambiguity, verify/reconcile/resume/use guarded semantics or abstain -> only then intervention-advantage estimation -> safe cut -> admissible checkpoint selection -> rollback target -> guidance/application -> restore -> external-effect settlement -> commit verification`.

This does **not** imply every agent failure is an interface problem. AFT-Bench intentionally tests interface-specific workloads; its `+100pp` recovery results are tied to the matched interruption/state-loss treatments and must not be generalized to arbitrary long-horizon failures.

## Important negative evidence / scope guard
- Stronger models cannot guarantee safe continuation when histories requiring different actions are observationally identical through the interface. This is an information/semantics limitation, not evidence that model improvements never help.
- Postcondition verification is not a universal runtime guarantee: its marginal benefit varies materially by model, unlike resume/durable-state mechanisms in the tested matrix.
- Structured output by itself is only a carrier; the paper explicitly does not treat machine-readable formatting as an independent safety guarantee.
- The AFT-Bench public code/repository was not located through targeted web and GitHub repository searches in this invocation. This is a reproducibility-artifact gap, not evidence that code does not exist.

## SymTrace artifact follow-up
Primary source rechecked: Zhongwen Luan et al., **Repair or Resample? Rethinking Failure Debugging in LLM Multi-Agent Systems**, arXiv:2608.25920, submitted 2026-08-26. Public HTML: https://arxiv.org/abs/2608.25920

The paper still states that SymTrace and SymFail are released and specifies selective replay as strict request/result matching plus content-hash validation of the reconstructed prefix, then live resume from the designated target. Targeted web searches and GitHub repository searches for `SymTrace`, `SymFail`, the exact paper title, and author/title combinations did not locate the intended public source repository in this invocation. An unrelated Rust project named `symtrace` was explicitly rejected as a name collision. Therefore the previous implementation claim remains **paper-specification verified but public-code-path unverified**.

This means the proposed target-selection x guidance factorial remains experimentally plausible from the paper's specification, but the exact public runner/API path and whether an empty/no-op guidance object is accepted remain unverified.

## Reviewer / intervention search status
A fresh search for software/tool-agent studies randomizing reviewer/no-review from the same replayed failure prefix did not locate a study that cleanly fixes prefix, target set, model, recovery budget, and actuator while randomizing reviewer application. Nearby work continues to confound diagnosis, target selection, guidance content, or actuation. The same-prefix reviewer/no-review factorial remains an open experimental gap.

## Updated synthesis
The strongest new design change is to put **operability diagnosis before recovery optimization**. Current long-horizon recovery research has spent substantial effort on better alarms, causal localization, rollback target selection, guidance, and repair stopping. AFT-Bench shows a class of failures where those controls are secondary because the interface suppresses the distinction needed for any policy to choose safely. This suggests two families of interventions should be evaluated separately:
- **interface hardening:** expose authoritative lifecycle/postcondition evidence or stabilize continuation via idempotency/guarded semantics;
- **policy recovery:** critic/reviewer/rollback/replan once the interface is sufficiently operable.

A valuable future factorial is therefore `legacy vs operable interface` x `no recovery vs fixed recovery policy`, with the same task/fault/model/budget. This can measure whether a sophisticated recovery policy adds value after interface ambiguity is removed, or merely compensates for weak tool semantics.

## Exact continuation
1. Locate the official SymTrace/SymFail artifact through author profiles, institutional pages, paper revisions, Hugging Face / Zenodo / GitHub links, or an accessible release mirror. Verify the actual replay API, target/guidance plumbing, prefix/hash assertions, RQ3 runner, and empty/no-op guidance behavior. Read-only discovery only.
2. Search for an existing `interface treatment x recovery policy` factorial in stateful software/tool agents. Preserve as unexecuted if no matched study exists.
3. Search specifically for same-prefix randomized `reviewer/no reviewer` or `advice/no advice` experiments on replayable source failures, including benign/successful prefixes for pass->fail disruption.
4. Preserve the strict rollback-selector-only design: identical alarm, candidate checkpoints, restore/carry-forward, inference state, model, guidance, stochastic coupling, realized recovery dose, and budget; only target selector varies.
5. Continue exact single-admitted-update future-task ON/OFF frozen replay, randomized/propensity-logged reviewer routing, persistent-release FWER-vs-FDR/LORD, verifier exposure/refresh, admission x maintenance common-replicate factorial, hidden semantic lineage, post-consolidation re-externalization, and decision-influence audits.
6. Recover official numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
7. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
