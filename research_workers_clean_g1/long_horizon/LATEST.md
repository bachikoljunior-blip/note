# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T210321JST_CAUSAL_CONFIDENCE_AND_MEMORY_GOVERNANCE.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T200102JST_DECISION_PROXIMAL_AGENT_MEMORY.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `10`
- role config revision: `5`
- frozen source main SHA: `fdee4a06e6b300c66907fe545fc4a017d8937e0d`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both pre-semantic SHA-only lookups matched; later repository changes were not adopted as semantic control.

Current synthesis delta:
- `Critic Experience Bank` adds unusually clean evidence that consequence-conditioned memory can improve *intervention targeting*, not just confidence metrics. On frozen Mind2Web states, the regeneration instruction and budget are held fixed and only the selector changes; CEB nearly matches oracle step selection at 10% and 25% regeneration budgets and beats random, while perplexity/mean-entropy selectors can be actively disruptive.
- CEB also maps better within-task step ranking to higher simulated final task success under a fixed oracle-review budget, but its stronger regeneration experiment is still offline/frozen-state rather than live closed-loop recovery. Do not generalize it to full trajectory recovery.
- `MemGuard` (arXiv:2608.21867, submitted 2026-08-22) supports keeping verifier descriptors as persistent lifecycle metadata across admission, retrieval, conflict resolution, summarization and archival. It reports best success/lowest steps across 16 backbone-benchmark cells under matched runtime budgets, but the public repo contains the governance core rather than benchmark runtimes/harnesses, so code availability is implementation evidence, not independent reproduction.
- `Conformal Selective Acting` supplies an anytime-pathwise selective-risk gate for adaptive streams. This is useful as a pre-commit `act/abstain` controller but is not a causal localizer or rollback-target selector.
- Updated controller decomposition: `lifecycle-governed memory -> consequence-aware pre-action critic -> selective act/abstain gate -> safe/admissible checkpoint filter -> historical target selector -> live branch recovery`.
- New cost guard: on CEB Mind2Web, retrieval depth `k=1 -> 5` adds `+70%` total input tokens for only ~7% relative ECE improvement; `k=2` captures much of the gain at `+18%` tokens. More memory is not monotonically cost-effective.

Exact continuation:
1. Find live closed-loop tool/software/GUI studies where the same intervention/replanning actuator is fixed and only confidence/memory evidence or the intervention selector changes; require final task outcome and successful-trajectory disruption.
2. Search memory-lifecycle factorials that isolate persistent verifier metadata at admission vs retrieval vs conflict resolution vs summarization/archival.
3. Search anytime-valid/selective-risk control explicitly coupled to irreversible tool actions or transactional commits; keep risk certification separate from rollback localization.
4. Search calibrated top-k/conformal/e-process localizers on adaptively queried agent traces; CSA is a risk gate, not a localizer.
5. Extend the strict harness with a decision-influence factorial: same reconstructed state and same intervention, varying no/random/similarity/positive-only/contrastive/lifecycle-governed historical evidence.
6. Continue strict historical target-selector comparison with matched post-intervention budgets, realized recovery dose, state-integrity checks and common-random-number coupling.
7. Preserve target and memory semantics distinctions; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
