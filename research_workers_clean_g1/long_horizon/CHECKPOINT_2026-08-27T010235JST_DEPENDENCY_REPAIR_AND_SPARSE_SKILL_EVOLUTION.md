# Long Horizon clean_g1 checkpoint — dependency repair and sparse skill evolution

Checkpointed at: 2026-08-27T01:02:35.956648+09:00
Invocation started at: 2026-08-27T00:57:37+09:00

## Frozen control tuple
- note main SHA at pre-semantic freeze: `91e54d08ef70f398c1232e92936e5a36086b1ad9`
- root control revision: `10`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both SHA-only pre-semantic head lookups matched.
- semantic inputs used: this role's own `LATEST.md`, its immediately referenced own checkpoint, and public sources only. No O/O-derived state, other-worker state/output/config, downstream comparator/integrator/index/feed/audit state, shared aggregate ledger, other-role receipts, or legacy/pre_independence research were used.

## New evidence 1 — correcting an ancestor without invalidating dependent descendants leaves stale reasoning alive
Primary source: `Self-Correcting Long-Horizon Search Agents via Tree-Structured Memory` (ReTree), arXiv:2608.10676, submitted 2026-08-11.
Primary URL: https://arxiv.org/abs/2608.10676

ReTree maintains search state as a dependency tree. When later evidence contradicts an earlier claim, it locates the node that introduced the claim, replaces it, regenerates that node's summary, prunes descendants that depended on the refuted state, and resumes from the repaired frontier.

The most useful control is `FlatUpdate`: it uses the same conflict detector, a matched 140-word task summary and top-5 evidence budget, but stores evidence in a flat list. It can replace the refuted fact but does not locate the introducing node, rebuild dependent summaries, or prune downstream reasoning. Across 2,149 questions spanning Bamboogle, HotpotQA, 2Wiki and FRAMES, ReTree beats FlatUpdate by 2.2–4.7 percentage points on every dataset. Natural backtracking is invoked in 9.6–17.5% of runs. The structural repair costs roughly 7–11% more model calls and 10–13% more total tokens than FlatUpdate.

This is direct evidence that an ancestor-only correction can be insufficient when stale descendants retain causal influence. It partially closes the prior semantic-descendant frontier at the level of within-run search memory: descendant invalidation itself has measurable value under a mechanism-matched control.

### Scope guard
- Descendants here are search-state nodes/summaries inside a long-horizon reasoning tree, not semantically transformed reusable skills written to a persistent cross-task library.
- Hard-pruning every descendant is conservative and can remove independent useful state. The paper itself motivates more selective claim/evidence dependency tracking.
- Therefore this does not close the stronger experiment: poison a persistent reusable skill, synthesize semantic descendants, retire the ancestor, then measure descendant retrieval and behavioral harm.

### Architectural consequence
Revocation/repair should operate over a proven dependency closure, not only the source row. A useful target is the smallest verified closure: invalidate or regenerate all descendants whose justification transitively depends on changed evidence, while preserving demonstrably independent state.

New distinction:
`ancestor corrected != dependent descendants invalidated != minimal safe invalidation closure`.

## New evidence 2 — persistent skill evolution is sparse, non-monotonic search; late rare gains can still dominate the final choice
Primary source: `Rethinking Self-Evolving Agent Skills: Feedback Dynamics over Multiple Rounds`, arXiv:2608.02636v1, 2026-07-31.
Primary URL: https://arxiv.org/abs/2608.02636

The study runs 42 ten-round feedback trajectories across 14 model–benchmark settings with GPT-5.5, Gemini 3.1 Pro and DeepSeek V4-Pro. Within each setting, parent skill, executor/optimizer configuration, revision procedure, validation rule and round budget are fixed; only feedback differs: successes+failures (`Normal`), failures only, or successes only. A candidate becomes the next skill only if validation does not decrease, while strict improvement updates the best checkpoint.

Only 55 of 388 generated candidates establish byte-distinct validation bests. Skill evolution therefore behaves more like sparse search over persistent procedures than monotonic local refinement. In the primary 14 settings, all 11 finally selected evolved skills come from feedback conditions containing failures: 9 Normal and 2 Fail-only; Success-only supplies none. Failure-containing feedback yields 44/267 new bests (16.5%) and improves 21/28 runs, versus 11/121 (9.1%) and 6/14 for Success-only. A broader SearchQA extension does contain Success-only wins for some models, so the narrow conclusion is that failure contrast is often more informative, not that positive traces are universally useless.

The time profile is especially important for maintenance scheduling: 38/55 new-best events occur in rounds 1–4, yet 6/11 final selected evolved skills first appear only in rounds 6–9. A static early cutoff catches most improvement events but misses most final selections. Rollback to the best validation checkpoint protects against regressions, but it does not make continued search monotonic or guarantee deployment improvement.

The released-test results also show why persistent procedural revision cannot always be replaced by more test-time sampling. On SpreadsheetBench, the parent skill scores 50.53, the evolved skill 85.77, oracle parallel sampling 54.80 and sequential sampling 45.20. The persistent skill change contributes a qualitatively larger gain than extra samples from the parent. Conversely, a validation-improved DeepSeek LiveMath Fail-only skill reduces released-test performance by 6.6 points, demonstrating `validation best != deployment best`.

### Scope guard
- This study does not independently cross admission gating ON/OFF with post-admission maintenance ON/OFF; it studies revision-feedback dynamics under its own validation gate.
- Benchmarks and validation panels remain finite; the released-test reversal directly warns against treating in-loop validation as universal transport evidence.
- Success-only is not globally inferior; the extended SearchQA results show model/task-dependent exceptions.

### Architectural consequence
Persistent skill maintenance should be scheduled as adaptive search with a nonzero late-improvement hazard, not as a fixed number of refinement rounds. Useful controller state includes candidate yield, time since last best, validation uncertainty, expected marginal gain, and reserved deployment/transfer checks. The controller should preserve the best known valid checkpoint while allowing rare late discoveries when their expected value exceeds compute and regression risk.

## New evidence 3 — localized maintenance can beat broad propagation, and propagation radius is itself a cost/control variable
Primary source: `Are We Ready For An Agent-Native Memory System?`, arXiv:2606.24775, 2026-06-23.
Primary URL: https://arxiv.org/abs/2606.24775

The paper evaluates representative memory systems and then changes components one at a time. On LoCoMo, MemoryOS default obtains Answer F1 23.2 / Substr EM 22.4; a Conservative-Merge maintenance policy gives 23.5 / 22.8, while Delayed-Flush falls to 20.6 / 19.5. For MemoChat, forcing a single coarse topic summary reduces 16.6 / 18.4 to 16.2 / 16.8. The authors' maintenance conclusion is that selective consolidation is preferable to unresolved backlog or aggressive coarse compression in the tested conversational-memory setting.

The systems-cost comparison also shows that maintenance propagation radius matters materially. Localized systems such as LightMem report much lower per-query cost than graph/global-reorganization systems, while the highest-quality systems can pay substantially more latency. This supports treating `how widely each write/repair propagates` as an explicit control variable rather than equating more structural maintenance with better memory.

### Scope guard
- These are primarily conversational/QA memory workloads, not reusable software/API procedural skills.
- Cross-system utility/latency numbers contain architectural differences beyond maintenance radius, so they are not a clean causal estimate of propagation cost.
- The useful evidence is the within-system component ablation plus the qualitative systems trade-off, not a universal ranking.

### Architectural consequence
Pair ReTree's dependency closure with a minimal-propagation objective: repair every proven dependent holder, but do not globally rewrite unrelated memory just because a repair occurred. `safe closure size` becomes a measurable maintenance cost.

## New evidence 4 — evaluator libraries and action skills need different lifecycle governance
Primary source: `Who Grades the Grader? Co-Evolving Evaluation Metrics and Skills for Self-Improving LLM Agents`, arXiv:2607.12790v1.
Primary URL: https://arxiv.org/abs/2607.12790

The metric loop separates anchor guards from lifecycle management. In controlled ablations, anchored evaluation has objective 0.865±0.002 and held-out 0.830±0.012. Removing anchor guards creates a vacuous always-pass collapse with objective 1.000 and training scores around 0.94–1.0. By contrast, removing the metric lifecycle does not collapse validity: objective 0.896±0.072 and held-out 0.868±0.061 in the reported setting.

The paper also gives a concrete Goodhart episode: evolved report skills exploit a rubric, an independent judge exposes the problem, one detector repair reduces erased value tags from about 30% to about 1%, and a task-aware judge's win rate rises from 0.515 to 0.770. A generic judge barely moves because it does not understand the required output contract.

The key control lesson is artifact-type specificity. A poor candidate evaluator that is never activated can be mostly harmless under strong anchored selection; a poor procedural skill retrieved into the action context can directly change behavior. Therefore an identical retire/repair policy across evaluators, memories and executable skills is not justified.

### Scope guard
- This is evaluator-pool co-evolution under the paper's anchored selection mechanism. It does not show that lifecycle is unnecessary for every evaluator architecture.
- Its evaluator results cannot be directly transferred to action-skill retirement thresholds.

### Architectural consequence
Lifecycle policy should be conditioned on the artifact's activation path and failure semantics. For action-affecting skills/memories, admission and post-admission maintenance can both be load-bearing. For candidate evaluator operations, anchor/selection validity may dominate lifecycle, with retirement serving mostly efficiency until activation risk changes.

## Updated synthesis
The prior lifecycle stack is retained but now split by dependency and artifact semantics:

`provisional candidate -> pre-commit gate -> typed low-commitment artifact -> local causal credit -> transport/shift validity -> artifact-type-specific maintenance controller -> sensor-certified retire/repair/suppress -> dependency-closed revocation/repair -> residue/influence probe -> decision-proximal retrieval/activation -> consequence-aware critic -> selective act/abstain -> safe recovery`.

Three control principles are now better supported:
1. **Repair the causal closure, not just the source.** ReTree's matched FlatUpdate control shows stale descendants materially matter.
2. **Persistent skill evolution is sparse search with rare late winners.** Fixed early stopping is unsafe; use a best-checkpoint-preserving adaptive continuation rule and separate validation from deployment/transfer evidence.
3. **Maintenance is artifact-type conditioned.** Evaluator pools whose candidates are gated by trusted anchors should not inherit the same destructive-retirement policy as action skills that are directly injected into behavior.

No reviewed study proves this full stack end-to-end.

## Search result on the direct factorial frontier
A targeted search still did not find a clean same-stream, size/compute-matched 2x2 experiment independently crossing `pre-commit admission gate ON/OFF` with `post-admission maintenance ON/OFF`. The new skill-feedback study is controlled and persistent, but its validation gate is always part of the procedure and it does not independently switch lifecycle maintenance. Keep this frontier open.

## Exact continuation
1. Keep searching for the direct admission-gate × post-admission-maintenance factorial on one persistent memory/skill stream under matched pool size and compute.
2. Continue the stronger semantic-descendant experiment: contaminate a reusable persistent skill/memory, synthesize semantically transformed descendants, retire/delete/tombstone the ancestor, and measure descendant retrieval plus behavioral harm. ReTree now covers dependent within-run reasoning descendants only.
3. Find a real software/API procedural-skill maintenance-only ablation that separates retrieval/representation/hydration from longitudinal repair/retire and contract compatibility.
4. Find adaptive maintenance stopping/scheduling policies that explicitly estimate rare late-new-best hazard, uncertainty and compute cost rather than fixed-round cutoffs; prioritize matched sequential-evidence or anytime-valid controllers.
5. Find artifact-type-specific governance factorisations that independently vary anchor/activation gating and lifecycle maintenance for evaluator versus action-skill pools.
6. Find a live closed-loop software/tool/GUI recovery experiment with fixed actuator/restore/carry-forward where only confidence/memory evidence or intervention selector changes; require final task success and disruption of originally successful trajectories.
7. Continue historical rollback-target-selector comparisons with matched alarm, candidate set, restore/carry-forward, model, allocated and realized recovery dose, stochastic coupling and abstention.
8. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
