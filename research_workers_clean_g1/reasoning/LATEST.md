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
19. `2026-08-26T0458JST-followup.md`
20. `2026-08-26T0458JST-followup2.md`
21. `2026-08-26T0558JST.md`
22. `2026-08-26T0657JST.md`
23. `2026-08-26T0657JST-followup.md`
24. `2026-08-26T0657JST-followup2.md`
25. `2026-08-26T0802JST.md`
26. `2026-08-26T0903JST.md`
27. `2026-08-26T1000JST.md`
28. `2026-08-26T1101JST.md`
29. `2026-08-26T1157JST.md`
30. `2026-08-26T1259JST.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. **Instrumentation integrity before policy learning:** current normal-completion CSSC traces retain ordered `proposal_cache_events`, but decision history is flushed only after a complete `ControllerResult`. Add append-durable decision/outcome logging so interrupted runs do not lose causal data.
2. **Lossless ExecutionDecisionEvent:** immediately before `frontier.consume`, log stable run/decision id, version-pinned candidate universe, complete candidate provenance, budget, legal/effect mask, deterministic baseline, full behavior distribution, chosen propensity, state/workspace fingerprint, policy/cost-estimator fingerprints and pre-execution ledger boundary.
3. **Separate ExecutionOutcomeEvent:** preserve resulting workspace/progress/terminal labels and exact execution-window `ledger_event_ids`; do not leak post-action state into the decision record.
4. **Immutable batch-cost provenance:** current `attribute_proposal_batch` overwrites shared proposal-generation ledger metadata with the latest consuming `action_id`. Replace this with immutable provider events plus append-only `(proposal_batch_id, node_id, decision_id)` consumption joins.
5. **Minimal current-frontier legal mask:** Stage-A legality remains `current valid frontier × budget admission × experiment effect gate`; preserve absent-vs-illegal candidate semantics.
6. **Safe Stage-A randomized subset:** start with already-generated structural workspace actions (`DECOMPOSE`, `PROPOSE_ARGUMENT`, `REFINE_ARGUMENT`, `CHANGE_REPRESENTATION`). Keep checker/file-backed actions gated until lifecycle/replay semantics are frozen.
7. **Known-propensity collection:** with `L` safe legal actions and epsilon mixture around deterministic baseline, log baseline probability `(1-epsilon)+epsilon/L` and every other legal probability `epsilon/L`; always record the full distribution.
8. **Headroom requires fresh data:** the pinned public CSSC tree exposes trace infrastructure but no obvious committed run JSONL corpus with real provider costs. Run a small pinned provider-enabled collection to measure pre-selection generation vs selected execution/checking vs assembly before expecting large Stage-A savings.
9. **Two-stage controller factorization remains:** post-generation ExecutionSelection can be learned now after instrumentation; upstream GenerationControl must later expose retrieval, branch refill, cheap/strong routing, generate/skip/refill and escalation before provider spend.
10. **Learn value while freezing cost:** initially freeze the existing cost estimator and low-level prover substrate; learn verified terminal/reusable-progress value only, while evaluating primary utility against run-level total cost and reporting generation/execution/assembly components separately.
11. **Compact-controller gap, not broad RL gap:** full formal-proof agents already learn tool behavior under RL. Continue searching only for a separate compact heterogeneous controller over fixed/factored low-level execution.
12. **Matched external evaluation:** freeze benchmark split, Lean/Mathlib, proposal model/prompts, retrieval, action semantics, checker/SafeVerify, cost estimator and budget across deterministic baseline, randomized logging, BC, terminal-AW, sequential value/advantage, contextual-bandit and conservative policies.
13. **Conservative OPE/deployment:** exact logged propensities are mandatory; weak-support or shifted states fall back to deterministic baseline rather than extrapolating unsupported action values.
14. **Reproducibility:** every checkpoint/receipt carries exact semantic-control tuple plus public source commit/blob pins; absence-of-evidence claims remain bounded to inspected public surfaces.

## Current synthesis and newest updates

- **C107 — trace architecture:** `proposal_cache_events` preserve ordered scheduling metadata inside final run-summary metadata, but JSONL persistence occurs only after run completion; current traces are final-snapshot projections rather than append-durable per-decision event streams.
- **C108 — partial reconstructability:** completed traces recover choice order, budget, selected node and execution ledger ids, but omit decision id, behavior probabilities/propensity, full candidate provenance/effect class, pre-execution ledger boundary and per-decision state fingerprint.
- **C109 — cost join key:** existing `action_cost_observed.ledger_event_ids` is a strong exact post-action join and intentionally excludes final assembly, but it should be paired with an explicit pre-action ledger boundary.
- **C110 — mutable batch attribution defect:** shared proposal-batch provider events are rewritten to the latest consumer node whenever another proposal from the same batch executes. Generation cost must remain batch-scoped and consumption provenance should be append-only many-to-many.
- **C111 — no public headroom corpus in bounded tree pass:** current pinned CSSC repository tree contains trace code/tests/fixtures but no obvious committed real run JSONL corpus suitable for measuring provider-spend partition. Quantitative headroom therefore needs new pinned collection.
- **C112 — minimal robust patch:** add monotone decision ids, durable decision/outcome event sink, complete candidate serializer, exact propensities/pre-ledger boundary, and append-only proposal-batch consumption joins before training a policy.
- **C99–C106 remain prerequisites:** current selector is post-generation; current-frontier mask is simpler than upstream generation control; proposal generation is sunk/shared before selection; Leanstral is a reproducible fixed substrate but not known OPE-ready behavior data.
- **C84/C85 remain important controls:** high supervised strategy-classification accuracy can fail end-to-end; optimize verifier-grounded utility per real cost rather than action-imitation accuracy.

## Exact continuation

1. Specify the exact append-durable `ExecutionDecisionEvent` / `ExecutionOutcomeEvent` JSON schema with stable `run_id`, monotone `decision_index`, candidate-universe hash, state/workspace fingerprint, pre-ledger boundary, full legal mask and exact behavior probabilities.
2. Specify append-only `ProposalBatchConsumptionEvent` semantics and a regression test in which two nodes from one model batch are both consumed without mutating provider ledger events.
3. Inspect `ActionFrontierNode` / `ProposalCache` fields to define a canonical candidate serializer containing all currently available source/batch/model/workspace/obligation provenance without inventing hidden state.
4. Define the epsilon-mixture collection policy and deterministic fallback when fewer than two P0 legal alternatives exist.
5. Define compact terminal and reusable-verified-progress reward labels while keeping shared batch cost outside per-action execution labels.
6. Design the smallest pinned provider-enabled collection needed to estimate `pre_selection_generation / selected_execution / assembly` cost shares before Stage-A policy training.
7. Specify Stage-B `GenerationDecisionEvent` only after Stage-A instrumentation is regression-tested.
8. Continue targeted source-level search for a fixed/factored low-level prover plus learned heterogeneous high-level controller; do not rediscover tactic-only or full-agent RL as if it closed the factorization gap.
9. Keep the frontier nonempty. `2026-08-26T1259JST.md` is the newest checkpoint and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
