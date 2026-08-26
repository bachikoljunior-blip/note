# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T200102JST_DECISION_PROXIMAL_AGENT_MEMORY.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T190348JST_RETRIEVAL_INTEGRATION_GAP.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `10`
- role config revision: `5`
- frozen source main SHA: `1525e6d0512ce012c8b1db6e08216ae6253d7d74`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both pre-semantic SHA-only lookups matched; later repository changes were not adopted as semantic control.

Current synthesis delta:
- Direct agent-task evidence now supports the prior `retrievable != causally used` hypothesis. `Remember When It Matters` leaves the action agent unchanged and injects targeted remembered execution state only as a transient intervention; Terminal-Bench Sonnet pass@1 rises `37.6 -> 45.9%` and tau2 task-weighted `55.0 -> 61.8%`. Full-bank exposure and generic Mem0 retrieval trail the selective system on macro-average.
- The intervention itself must be calibrated. An untrained 27B memory agent reduces SETA reward `0.709 -> 0.693`; SFT/GRPO recover and improve it. Injection-only guidance hurts one tau2 domain even while helping another. Auxiliary memory/advisor agents are not intrinsically beneficial.
- `HAM-VLN` independently shows structured subgoal-conditioned memory can beat full raw history under a fixed planner/controller: R2R-CE SR `61.0%` full vs `53.3%` with full raw history; removing episodic, semantic or reflection memory degrades outcome.
- `Decision-Aware Memory Cards` provides useful measurement primitives (action shift, outcome uplift, necessity, negative-transfer risk) and SWE-bench file-retrieval gains, but not end-to-end repair evidence; its scope must remain retrieval/diagnostic.
- `AgentAbstain` shows act capability and calibrated restraint are largely separate. Best paired act/abstain accuracy is only `59.5%`; 115 post-hoc abstention cases cross the critical action boundary before claiming restraint. `unknown/do-not-commit` must be enforced before irreversible effects.
- Re-reading `Conformal Agent Error Attribution` confirms its contiguous-set guarantees assume exchangeable trajectories. Its rollback chooses the earliest set step and adds failed-trace corrective context, so it is neither selector-only nor anytime-valid under an adaptively changing within-trajectory policy/state.

Exact continuation:
1. Search software/tool/GUI-agent work for matched `context item present vs absent -> next action/rollback-target change -> final verifier outcome`, not only retrieval metrics.
2. Search error localizers for online/adaptive conformal, confidence-sequence/e-process, selective prediction or explicit abstention on adaptively queried agent traces; keep marginal exchangeable coverage distinct from within-trace anytime validity.
3. Add a decision-influence audit to the strict rollback-selector harness: branch from the same reconstructed state with a memory/context item present vs absent and measure action shift, selected rollback target, realized recovery dose, final success and disruption.
4. Add explicit null-intervention and pre-commit abstention arms; measure both recovery and over-intervention disruption.
5. Compare generic summary, full raw history, targeted typed restatement and raw-source lookup at the decision boundary under increasing irrelevant context, using final task success as the primary outcome.
6. Continue vLLM/common-random-number, prefix state-integrity and realized recovery-dose work.
7. Preserve target semantics distinctions: earliest causal origin, first sufficient intervention, latest rescue/point-of-commitment, latest safe checkpoint and intended semantic version are not interchangeable.
8. Preserve the strict selector-only gap unless all non-target variables are controlled.
9. Maintain a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
