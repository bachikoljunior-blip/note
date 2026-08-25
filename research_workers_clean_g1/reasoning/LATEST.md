# Reasoning Systems — clean_g1 latest pointer

Latest checkpoints in order:
1. `2026-08-25T1902JST.md`
2. `2026-08-25T1902JST-followup.md`
3. `2026-08-25T1957JST.md`
4. `2026-08-25T2057JST.md`
5. `2026-08-25T2157JST.md`
6. `2026-08-25T2258JST.md`
7. `2026-08-26T0002JST.md`
8. `2026-08-26T0002JST-followup.md`
9. `2026-08-26T0102JST.md`
10. `2026-08-26T0102JST-followup.md`
11. `2026-08-26T0200JST.md`
12. `2026-08-26T0302JST.md`
13. `2026-08-26T0302JST-followup.md`
14. `2026-08-26T0302JST-followup2.md`
15. `2026-08-26T0302JST-followup3.md`
16. `2026-08-26T0302JST-followup4.md`
17. `2026-08-26T0400JST.md`
18. `2026-08-26T0458JST.md`

Read `STATE.md` for the earlier accumulated base, then read the source-qualified checkpoints above in order for exact evidence, version/model/budget caveats, negative evidence and continuation. The newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. **Matched Lean controller comparison:** freeze the same action/tool/verifier/memory substrate and real budget, then compare fixed/rule control, free-form LLM planning and a learned typed heterogeneous policy.
2. **Logged formal-agent policy learning:** learn over multi-action Lean traces (`continue/repair/retrieve/decompose/replan/backtrack/spawn/escalate/stop`) rather than tactic prediction only.
3. **OPE-identifiable data collection:** current free-form planner traces select typed actions but do not expose behavior meta-action propensities; design safe low-amplitude randomized logging with exact propensities/eligibility masks and coverage diagnostics.
4. **Conservative/baseline-bootstrap deployment:** learned policy should defer to the baseline in weak-support/uncertain state-action regions, with verifier-enforced hard constraints.
5. **Hierarchical controller-of-controllers:** decide both local proof action and whether to buy more thinking, stronger model, more workers, specialized prover, global retrieval, population/evolution or replan.
6. **Calibrated prospective action/value-of-computation:** Brier/ECE/reliability/selective-risk under theorem/backbone/search-policy shift, especially near expensive-action boundaries.
7. **Compact sufficient online memory/context isolation:** compact Whiteboard/notebook + selective repository retrieval + branch-local workers versus raw history, evaluated by downstream action quality and solve/cost.
8. **Stateful constrained optimization:** extend global-budget allocation to Markov/partial-observation Lean trajectories with verified reusable cache/DAG state and action-specific substrate cost.
9. **Matched subgoal/branch scheduling:** first-stuck focus vs hardest-branch vs independent parallelism, and learn when greedy scheduling versus MCTS/beam/semantic branching pays for itself.
10. **Execution-aware retrieval/repair:** triggered global re-retrieval, snapshot+semantic-selection+compiler repair, proof-state reconstruction cost and benchmark/harness robustness remain open.

## Current synthesis and newest updates

- **OpenProver is the strongest direct free-form Lean controller baseline found so far.** On 185 ProofNet formal theorems with a 100k output-token budget/problem, the published comparison reports Kimi-K2.5 57.3% vs linear rollout 36.8%, and Leanstral 28.1% vs 21.1%. Its Planner chooses heterogeneous actions while Workers/Verifiers are context-isolated. The comparison matches output-token budget, not every real cost dimension.
- OpenProver's public implementation already provides most of the logging substrate required for controller learning. `prompts.py` exposes typed Planner actions; `prover.py` stores `planner.toml`, multi-action `plans.json`, worker tasks/results/verifier results/tool calls, Lean outcomes and `meta.toml`; `inspect.py` parses model, elapsed, input/output/cache tokens and cost.
- **New C60 — deterministic event schema:** normalize existing run artifacts into `run_start -> state_before -> planner_call -> action_proposed -> action_result/tool_result -> state_after -> run_end`, with deterministic IDs/artifact hashes and a vector reward/cost outcome. Avoid retaining raw hidden reasoning when compact artifact/state references suffice.
- **New C61 — OPE blocker and data-collection requirement:** inspected OpenProver logs do not expose behavior-policy probabilities over typed meta-actions. IPS/sequential DR therefore cannot be treated as identified from those traces unless behavior propensities are logged or modeled and action support exists. Estimated logging-policy methods can relax missing-propensity assumptions but cannot create support for unseen actions. A new evaluation wave should deliberately randomize a bounded safe subset of meta-actions and log exact probabilities/eligibility masks.
- **New C62 — conservative deployment:** SPIBB-style baseline bootstrapping suggests a practical learned-controller safety rule: override the fixed/free-form baseline only where data support/value margin is strong; otherwise reproduce baseline behavior. Formal SPIBB guarantees do not automatically transfer to neural partially observed Lean control, so this is a design principle until tested under the real state/action representation.
- **New C63 — mid-trajectory compute purchase:** `Learning to Seek Help` trains a small model to decide during multi-step reasoning when/how to query a stronger LLM; STEER performs stepwise small/large-model routing; Adaptive Parallel MCTS reallocates compute by early-exiting unproductive trajectories. These are transfer—not Lean—evidence that `escalate_model`, `spawn_more_workers`, and `buy_search` should be evolving-state actions rather than only a first-token budget decision.
- **New C64 — targeted absence update:** one focused search did not find a separate public raw OpenProver ProofNet trajectory archive, so rerun/instrumentation is the practical next step rather than repeated broad archive search. Targeted Lean searches again did not surface a primary system learning the full heterogeneous planner-level action policy. Both are search gaps, not nonexistence claims.
- **Meta-Reasoner transfer** remains relevant: compact progress state + learned typed strategy selection beat raw-history/direct-LLM selection in its non-Lean tested tasks. It supports the controller architecture but has no Lean kernel-grounded reward.
- **AxProverBase** remains direct evidence against raw full-history accumulation as default and shows thinking-budget value is backbone dependent. **LeanFlow / AlphaProof Nexus / BFS-Prover-V2 / LEAP / Numina-Lean-Agent** remain useful fixed/free-form/hierarchical baselines with different cost regimes, not evidence for one universally best orchestration style.
- Prior proof-search evidence still supports verifier-grounded structural diversity, learned repair, progress/value guidance, subgoal caching/factorization, context selection and state snapshot reuse. Preserve exact tested scope: narrow adaptation failures never reject the whole method family.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` remains absent as of the newest run; no sanitized feedback was consumed.

## Exact continuation

1. Search once for an OpenProver fork/companion that already converts `steps/` into JSONL/Parquet; if absent, stop spending search budget on that and treat the C60 normalizer contract as the reference extractor.
2. Search the strongest sequential logging-policy/OPE methods for partially observed typed actions, then define a small safe Lean meta-action randomization matrix with exact propensities and eligibility masks.
3. Compare sequential DR/WDR, fitted-Q/model-based evaluation and DataCOPE/coverage diagnostics; explicitly identify when weak overlap forces abstention rather than a numeric ranking.
4. Develop/search baseline-bootstrap/conservative offline control for typed meta-actions under deterministic verifier hard constraints.
5. Search formal-agent/proof work with **mid-trajectory** dynamic model/worker/search purchase after observed proof progress/failure; keep first-token routing separate.
6. Specify the matched fixed-vs-free-form-vs-learned controller benchmark with real cost accounting: planner/worker/verifier input/output/cache tokens, monetary cost, Lean/tool/state-reconstruction time, concurrency-adjusted wall-clock and verified reusable-progress reuse.
7. Continue earlier branches on subgoal scheduling, backbone-conditioned action values, triggered reretrieval, compact trajectory state, snapshot+semantic repair, calibration under shift and benchmark robustness.
8. Keep the frontier nonempty. Checkpoints/findings/report readiness are never global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
