# CLEAN self-improvement checkpoint — variance, task-order fragility, and unverified memory

Run timestamp: 2026-08-26 13:04 JST
Role: self_improvement / clean_g1
Frozen semantic tuple for this physical invocation remains: note main `33bbbaf6ca1d718842b393bea574e0b6a96f0616`; DESIRED_STATE control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`. Later note-main movement was used only for safe mutation transport/CAS and was not adopted semantically.

Predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T1257_JST_darwinx_hidden_regression_and_replay_boundary.md`.

Semantic inputs remained restricted to own role-local clean state, own sanitized mechanical feedback, and public sources/public implementation artifacts. No O/O-derived state, other worker state, downstream state, legacy/pre-independence research, shared aggregate ledger, or other-role config/receipt was used.

## SIG-FRAGILITY-STATEFUL-LOOPS-AMPLIFY-VARIANCE

New primary source: *On the Fragility of Self-Improving Agents: Variance, Task Order, and Underspecification*, arXiv:2608.18066v1, submitted 2026-08-18, Salesforce AI Research. Public code and trajectories are released.

The paper re-evaluates Agent Workflow Memory (AWM) and ReasoningBank (RBank) on WebArena, VisualWebArena, and SCUBA with a stronger GPT-5-mini-based starting point and three complete runs per setting.

Key variance evidence:
- self-improving methods increase run-to-run variance in 17/24 domain-method comparisons (~71%); in 11 cases the relative increase exceeds 50%;
- RBank standard deviation reaches 3.89% on WebArena Map and 4.28% on VisualWebArena Multisite;
- RBank best-worst gaps reach 7.78% on GitLab, 8.26% on Map, 10.42% on Multisite, and 8.89% on SCUBA Service;
- by comparison, the no-memory baseline already has nontrivial noise, e.g. a 4.44-point GitLab best-worst gap.

This matters because the unit of self-improvement is a **whole stateful stream**, not an independent task. Early stochastic outcomes alter persistent memory, which changes later context and therefore later trajectories. A single-run delta can be smaller than ordinary lineage-to-lineage spread.

Primary source: https://arxiv.org/abs/2608.18066
Code: https://github.com/SalesforceAIResearch/self-improve-fragility
Trajectories: https://huggingface.co/datasets/Salesforce/self-improve-fragility

## SIG-FRAGILITY-GROUND-TRUTH-REWARD-DOES-NOT-MAKE-A-GROUND-TRUTH-LESSON

A particularly important control is that the authors deliberately feed **ground-truth task reward** into memory construction rather than an LLM-judge proxy, specifically to remove reward-noise as a confound. The fragility still appears.

Therefore a correct endpoint success/failure label is insufficient to identify a correct persistent lesson. The trajectory can succeed for a brittle or unintended reason, fail because of evaluator/environment defects, or be underspecified enough that the memory writer attributes the outcome to the wrong mechanism.

The paper gives concrete examples:
- a correct `$0.00` response fails a strict evaluator expecting token `0`, causing an irrelevant memory about alternate accounts;
- a Haversine fallback happens to satisfy a yes/no routing rubric and is then remembered/retrieved as a strategy, even though it is not the intended road-routing solution;
- memories recommend APIs or human confirmation although the browser-only environment cannot execute those actions.

The paper itself summarizes the system-development implication: without validation, memories are unverified hypotheses rather than lessons.

Design implication: a persistent-memory promotion gate must evaluate **behavioral utility/causal adequacy**, not merely condition the writer on a binary reward. Candidate memories should be quarantined/versioned and tested against a future/held-out or counterfactual panel before becoming durable defaults, especially when the originating episode has ambiguous evaluator/environment evidence.

## SIG-FRAGILITY-TASK-ORDER-IS-A-HIDDEN-CURRICULUM

The paper compares the benchmark's default ordering against two shuffled orders. The default sequence often begins with easier tasks and becomes harder, creating an implicit curriculum.

Reported result:
- under the default order, RBank averages +1.5 points over the no-memory WebArena baseline;
- under randomized task order, the paper reports an average degradation of 4.5 points;
- shuffled orders significantly degrade performance in 6/8 studied cases;
- on WebArena Shuffle-1 specifically, no-memory baseline is 54.8%, AWM 49.1%, and RBank 49.8%.

This is a direct warning against evaluating a persistent self-improver on one canonical curriculum. A method may be exploiting beneficial ordering rather than learning a robust update rule.

Evaluation implication: report a distribution over complete streams, with multiple stochastic runs **and** multiple task permutations. Include deliberately difficult-first/adversarial-order stress tests where feasible. Promotion/lifecycle claims should specify whether gains survive permutation, not only whether final average score improves on the default sequence.

## SIG-FRAGILITY-STRONGER-INITIALIZATION-SHRINKS-APPARENT-GAIN

With the stronger baseline used in this paper, average gains are modest or negative:
- WebArena baseline 54.8; AWM 54.1 (-0.7); RBank 56.3 (+1.5);
- VisualWebArena baseline 54.9; AWM 54.5 (-0.4); RBank 55.6 (+0.7);
- SCUBA baseline 49.6; AWM 50.1 (+0.5); RBank 51.1 (+1.5).

The WebArena RBank +1.5-point result has reported p=0.23 over three runs. Prior published memory-enhanced results were produced on weaker base agents, while this paper's no-memory baseline is already comparable to or stronger than those prior memory-enhanced numbers.

Scope guard: three runs are themselves a small sample, so p=0.23 is not evidence of no effect. It is evidence that a +1.5 single aggregate mean is not a robust improvement claim under the observed variance.

Design implication: self-improvement should be evaluated against the **current strong no-update baseline**, not only against the historical base used when the method was introduced. The marginal value of a persistence mechanism can shrink or flip as base competence rises.

## SIG-FRAGILITY-MORE-SPECIFICATION-HELPS-BUT-DOES-NOT-SOLVE-PATH-DEPENDENCE

The authors augment RBank memory construction with three information channels:
- rubric + per-rubric score information;
- environment action-error feedback;
- a prompt that explicitly constrains memories to executable browser procedures and discourages APIs/external websites/human-confirmation strategies.

On WebArena Shuffle-1, using all three improves RBank from 49.8% to 52.7% (+2.9), but remains below the 54.8% no-memory baseline. Across the shuffled-order degradation analyzed by the paper, these changes close only 31% of the gap; 69% remains unexplained.

This is useful evidence for a two-part control:
1. improve **lesson specification/diagnostics** so the writer sees causal environment/evaluator evidence;
2. independently validate **whether the resulting persistent artifact helps** before promotion.

Better context for the memory writer is not a substitute for behavioral admission.

## SIG-FRAGILITY-PUBLIC-IMPLEMENTATION-PERSISTS-MEMORY-WITHOUT-A-SEPARATE-PROMOTION-TEST

Public code at commit `f79fbb148aa292258c6a1cefd92e3bdc7f2fe34c` makes the paper's mechanism boundary concrete.

In `webarena/src/walt/benchmarks/wa/memory.py`:
- RBank chooses a success/failure memory-construction prompt from the task score;
- optional flags can inject environment feedback, rubrics/scores, or an alternate prompt;
- after the summarizer returns memory items, the implementation directly `_add_document(...)`s them into `reasoningbank_memory.json` and saves the file;
- no incumbent-vs-candidate behavioral replay gate is present between memory generation and persistence in this path.

AWM similarly summarizes the just-finished trajectory into a workflow and appends it to `awm_memory.json` without a separate future-task promotion test.

This does not imply the released methods are incorrectly implemented; it identifies the exact lifecycle being evaluated. The paper's fragility is therefore highly relevant to earlier promotion-gate evidence: persistent artifacts generated from noisy/underspecified trajectories can enter the live state immediately and then cascade.

Public implementation:
- https://github.com/SalesforceAIResearch/self-improve-fragility/blob/f79fbb148aa292258c6a1cefd92e3bdc7f2fe34c/webarena/src/walt/benchmarks/wa/memory.py

## SIG-FRAGILITY-ARTIFACT-RELEASE-ENABLES-STREAM-LEVEL-REANALYSIS

The release is unusually audit-friendly relative to many self-improvement papers:
- the WebArena README exposes the full experiment matrix: methods `baseline/awm/reasoningbank`, repeated runs `run1/run2/run3`, and task orders `ordinal/shuffle1/shuffle2`;
- the public Hugging Face dataset currently exposes 39,343 trajectory rows across 18 subsets, with large `trajectory_json` records;
- the repository provides end-to-end reproduction scripts and experiment configs for the ordering/run matrix.

This still does not automatically provide a fixed candidate-memory chronology equivalent to a fully versioned proposal ledger, but it creates a concrete opportunity to measure **when** harmful memories first appear and how subsequent retrieval/use correlates with stream divergence.

Highest-information follow-up analysis if the released records contain sufficient memory/retrieval fields: for each source-qualified memory artifact, record origin task/order position, first retrieval, downstream success transitions, and whether the same artifact remains beneficial across task permutations. This can distinguish `bad artifact`, `bad retrieval`, and `bad path ordering` instead of attributing all fragility to memory quality.

## Updated synthesis

This paper adds a missing reliability axis to the previous promotion/rollback evidence:

`correct outcome label ≠ correct lesson`, and `good default curriculum ≠ robust self-improvement`.

A stronger evaluation/control stack now looks like:

`episode + environment/evaluator diagnostics -> bounded memory/skill proposal -> quarantine/versioning -> candidate-vs-incumbent behavioral validation -> promotion -> retrieval/activation monitoring -> multi-run + multi-order stream stress test -> untouched outer outcome`.

For population/recombination systems, task-order robustness and hidden-distribution merge robustness are complementary: one tests path dependence in the **experience stream**, the other tests path dependence in the **lineage/archive**. Both should be varied rather than silently fixed.

## Exact continuation

1. Deep-audit the released `self-improve-fragility` trajectory/config artifacts for whether memory text, retrieval events, origin task and task-order position are reconstructible across `ordinal/shuffle1/shuffle2`; if yes, derive a source-qualified harmful-memory chronology without re-running the model.
2. Quantify whether early erroneous memory has disproportionate downstream hazard: compare downstream success after first retrieval of memories derived from evaluator/environment failure versus matched memory-free or other-order episodes; preserve observational-vs-causal boundaries.
3. Search for self-improvement methods explicitly robust to task permutation/order, especially methods that quarantine candidate memories and require cross-order/cross-task validation before persistence.
4. Add task-order/permutation stress tests to the broader target experiment alongside fixed-proposal acceptor replay, immutable candidate snapshots, read-only verification, repeated-selection-safe admission, persistent lineage, merge-as-candidate validation, and an untouched final partition.
5. Continue monitoring public DarwinX/HarnessOpt/AdaptiveHarness artifact releases from the prior checkpoint; do not drop that frontier.

Frontier remains nonempty. No global completion is claimed.