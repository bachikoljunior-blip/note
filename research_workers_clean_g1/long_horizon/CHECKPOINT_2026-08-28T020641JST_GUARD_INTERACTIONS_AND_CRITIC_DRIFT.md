# Long Horizon clean_g1 checkpoint — guard interactions and critic drift

Checkpointed from an invocation whose semantic control tuple was frozen before any role-local/public-source semantic read.

## Frozen control tuple
- invocation_started_at: `2026-08-28T02:02:28+09:00`
- checkpointed_at: `2026-08-28T02:06:41+09:00`
- root control revision: `12`
- role config revision: `5`
- frozen semantic source note main SHA: `36ea6b38d1d493cc80e913f073ea8a0f24b79972`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched the same main SHA.
- later repository movement was used only for write safety and was not adopted semantically.

Clean semantic inputs in this invocation were limited to this role's own LATEST/minimum predecessor state plus public sources. No O/O-derived state, other-worker state, downstream state, legacy research, shared aggregate ledger, other-role receipt/config, or commit-message/diff payload was used semantically.

## New primary evidence

### 1. Mutation-gated safeguards interact non-monotonically; complete factorials matter

Primary paper: Alejandro Cuadron, Pengfei Yu, Yang Liu, Arpit Gupta, *SABER: Small Actions, Big Errors — Safeguarding Mutating Steps in LLM Agents*, arXiv:2512.07850.

The paper finds mutating environment-changing actions are only about 14–18% of trajectory steps yet carry disproportionate failure risk. In the Qwen3-Thinking-235B ablation on tau-Bench Verified, block-based context cleaning is held on with at most 16 blocks while reflection and mutation-gated verification are crossed:

- Airline: No-SABER `58.0%`; +Reflection `68.0%`; +Verification `68.7%`; both/full `78.7%`.
- Retail: No-SABER `66.9%`; +Reflection `80.8%`; +Verification `80.5%`; both/full `77.7%`.

Airline exhibits strong positive complementarity, but Retail exhibits a negative interaction: either single safeguard beats their combination by about 3 points. Therefore `more safeguards` is not a monotone control rule even when each safeguard alone helps. A controller should preserve the null/single/combined cells and estimate domain-conditional interaction rather than stack reviewer/verification/reflection mechanisms by default.

Scope guard: this is reflection x simulated-user verification conditional on context cleaning, not the unresolved operable-interface x fixed-recovery factorial. Verification relies on a user simulator, and the paper itself notes benchmark/user-simulation limitations. The Retail difference is a point estimate; do not generalize it to all mutating actions or all domains without replication/power analysis.

### 2. A deterministic public tool benchmark exposes a practical host for crossed recovery policies, but not yet the target interface factorial

Public repository inspected read-only: `akgitrepos/toolmisusebench`.

The released baselines make treatment mechanics explicit:
- `HeuristicAgent` attempts tools once with schema defaults and has no error-repair branch.
- `SchemaRepairAgent` uses the last tool error to repair arguments and reissues the same tool.
- `PolicyAwareAgent` layers authorization/safety blocking and a safe read-only fallback on top of schema repair.

The associated ToolMisuseBench study reports deterministic fault injection over 6,800 tasks; schema-aware/policy-aware recovery reaches roughly 0.50 on timeout/schema-drift classes while authorization and rate-limit classes remain 0. This reinforces explicit recoverability/action classes and provides an inspectable harness in which recovery-policy arms can be crossed without relying on opaque hosted trajectories.

However, the current public baselines vary policy semantics and do not themselves supply `operable/authoritative interface ON/OFF x identical fixed recovery ON/OFF`. Treat this as an experimental host candidate, not as evidence that the missing factorial is already solved.

### 3. Reviewer/critic quality is policy-relative and can become stale as the agent improves

Primary paper: Boyang Liu et al., *CAFE: Self-Improving Search Agents Need Co-Evolving Feedback*, arXiv:2608.24794, submitted 2026-08-25.

CAFE explicitly treats feedback as an intervention whose usefulness changes with the agent's failure distribution. Its matched five-iteration component table shows the strongest RDPO row when both comparative feedback estimation and feedback-aware advantage shaping are active (`52.5 EM / 60.7 F1` average), compared with `50.2/58.5` with neither, `51.3/59.4` with comparative feedback alone, and `51.1/59.5` with shaping alone. The paper's feedback analysis also reports that dominant correction content shifts from retrieval/grounding errors early toward verification and then planning/redundancy errors later; average hallucination falls from `17.63%` under outcome-reward GRPO to `12.60%` under CAFE.

This supports a lifecycle constraint for long-running reviewer systems: a critic calibrated to yesterday's failure distribution can become the wrong intervention policy after the base agent changes. Critic/reviewer evaluation should therefore be version-bound to the controlled agent state, and fixed-critic versus refreshed/co-evolved-critic should be an explicit factor.

Scope guard: CAFE is training-time co-evolution for search agents, not a randomized deployment-time reviewer ON/OFF experiment on software/API trajectories. It does not establish that continually retraining every critic is optimal or safe under persistent external effects.

## Updated synthesis

The recovery controller should now preserve two different interaction layers rather than independently maximizing every safeguard:

1. **Pre-action/runtime layer:** interface state distinguishability, authority/effect identity, postcondition evidence, mutation/consequence class.
2. **Intervention layer:** no-op/defer, verification, reflection/advice, retry/resume/replan/rollback/reviewer, including their pairwise/combined interactions.

A useful intervention can become harmful after another ambiguity-reducing safeguard is active (Verified Tool Calls) or after another reasoning safeguard is active (SABER Retail). Likewise, a reviewer can become stale as the controlled policy's error distribution shifts (CAFE). Thus optimize the *joint controller under the current domain/policy state*, not a bag of individually positive components.

## Exact continuation

1. Find a complete common-replicate `operable/authoritative interface ON/OFF x identical fixed recovery ON/OFF` 2x2; measure success, duplicate/unsafe effects, disruption and cost.
2. Use deterministic/open harnesses such as ToolMisuseBench only as experimental hosts unless the crossed treatment semantics are explicitly matched; inspect configuration/pipeline read-only for a treatment-preserving implementation path.
3. Search deployment-time same-prefix `reviewer/reflection/advice ON/OFF x verification ON/OFF` factorials with both initially failed and initially successful/benign prefixes; measure rescue and pass-to-fail disruption. SABER makes interaction sign a first-class endpoint.
4. Search fixed-critic versus refreshed/co-evolved-critic under the same evolving base-policy checkpoints and matched evaluation budget; separate critic drift from base-agent improvement.
5. Preserve rollback-selector-only comparison under identical alarm/candidates/restore/carry-forward/inference state/model/guidance/stochastic coupling/post-intervention budget.
6. Keep recoverability/action classes explicit: transient interruption, process state loss, non-atomic ambiguous effect, schema drift, authority denial, rate limit/external unavailability, irreversible effect, and terminal-belief mismatch must not be pooled.
7. Continue exact single-admitted-update future-task ON/OFF frozen replay; randomized/propensity-logged reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; common-replicate admission x maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
8. Locate official SymTrace/SymFail source if publicly discoverable; do not infer runtime behavior from release claims.
9. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
10. Preserve exact tested scope and a nonempty frontier; this checkpoint is not completion.
