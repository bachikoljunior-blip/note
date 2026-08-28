# Long Horizon clean_g1 checkpoint — pre/post tool-contract factorial and intervention-timing target

Observed invocation start: 2026-08-28T11:01:50+09:00
Observed checkpoint time: 2026-08-28T11:05:11.962855+09:00

## Frozen semantic control tuple
- frozen note main SHA: `568f343a3870b4add6b613f33fcc911e26bd4c7b`
- root control revision: `13`
- root control blob: `cc9b1f22f0fda9cf26296057fd35b19a090618b4`
- role: `long_horizon`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched this tuple before the first own-state/public semantic read.
- semantic inputs used: own `LATEST.md`, own latest checkpoint, own sanitized feedback, and public primary sources only. No O/O-derived state, other-worker state/output/config, downstream state, legacy/pre_independence research, shared aggregate ledger, or other-role receipts were used.

## New evidence

### 1. ToolGate supplies a real 2x2 component factorial for pre-call admissibility and post-call result verification
Primary source: *ToolGate: Contract-Grounded and Verified Tool Execution for LLMs* (arXiv:2601.04688v1, 2026-01-08).

ToolGate represents each tool with a Hoare-style contract `{P} C {Q}` over a typed symbolic state. `P` checks whether a tool call is admissible before execution; `Q` checks the returned result before it can update trusted state. The paper reports all four combinations under the same ToolGate search architecture:
- `P=0,Q=0`: ToolGate w/o Hoare;
- `P=0,Q=1`: No P check;
- `P=1,Q=0`: No Q check;
- `P=1,Q=1`: Full.

On MCP-Universe, the four-cell MCP-Avg success rates are:
- DeepSeek V3.2: `27.2 / 34.5 / 30.9 / 38.0` for `P0Q0 / P0Q1 / P1Q0 / P1Q1`;
- GPT-5.2: `37.6 / 52.5 / 46.2 / 57.0`.

The Repository Management subtask gives the same four-cell structure:
- DeepSeek V3.2: `14.5 / 21.5 / 18.2 / 24.2`;
- GPT-5.2: `26.8 / 41.5 / 33.5 / 45.5`.

This partially closes the previous component-factorial frontier: **pre-execution admissibility and post-execution commit/result verification each have independent positive value under the tested tool benchmark, and both can be crossed rather than only removed one at a time.**

The interaction is not super-additive in these cells. Difference-of-differences on MCP-Avg is approximately `-0.2pp` for DeepSeek and `-4.1pp` for GPT-5.2; on Repository Management it is `-1.0pp` and `-2.7pp`. Therefore the evidence supports complementarity in coverage, but not a general claim that stacking the two gates yields multiplicative or super-additive gains.

Scope guard: this still does **not** close the stronger `operable/authoritative external-state interface ON/OFF × identical fixed recovery ON/OFF` frontier. `Q` can trigger immediate backtracking, so the postcondition arm changes recovery behavior as well as observation/commit semantics. MCP-Universe also does not reproduce the full non-atomic external-effect/rate-limit/authority setting of production APIs. ToolGate includes symbolic state plus retrieval/reranking, and only the Hoare module is crossed here.

### 2. In the tested ToolGate setting, postcondition verification is more load-bearing than precondition filtering, but only within scope
For GPT-5.2 MCP-Avg, removing `Q` from Full changes `57.0 -> 46.2` (`-10.8pp`), while removing `P` changes `57.0 -> 52.5` (`-4.5pp`). The paper reports that the formal layer intercepts about `29.4%` of tool attempts: `17.6%` at `P` and `11.8%` at `Q`.

The error classes differ:
- `P`: value/entity hallucination `8.4%`, schema/format `5.1%`, missing state dependency `4.1%`;
- `Q`: empty/null `6.3%`, semantic mismatch `3.7%`, state-update inconsistency `1.8%`.

ToolGate also reports GPT-5.2 average tool-calling steps reduced from `6.78` to `4.21` in ToolBench. The useful architectural distinction is: **P prevents execution from entering known-invalid states; Q prevents returned evidence from corrupting trusted state and can initiate rectification.** Do not generalize the relative importance of Q>P beyond these tested benchmarks/models.

### 3. A public GitHub repository for ToolGate was not identified in this run
A read-only GitHub repository search for the exact ToolGate title returned no matching repository. This does not prove that no code exists, but implementation/reproduction status remains unverified in this checkpoint. Treat the paper table as primary-result evidence, not code-reproduced evidence.

### 4. Human-labelled “when to intervene” is itself a weak target; optimize executed intervention advantage instead
Primary source: *The Saturation Trap and the Subjectivity of Intervention Timing* (arXiv:2606.04296, 2026-06-02).

On SWE-bench-Verified debugging traces, affect-threshold triggers fire on `39–83%` of actions after state saturation. Full-trajectory LLM judges reach only F1 `0.17–0.40` at up to `90x` cost, while the small judge tested never fires. More importantly, on one 56-action trajectory, three trained human annotators show near-chance agreement on intervention location: Krippendorff alpha `+0.047`, best pairwise Cohen kappa `+0.349`; intervention-type agreement is also poor.

This makes post-hoc human `intervention-point` labels a weak primary optimization target. For reviewer/monitor cadence, prefer **executed counterfactual metrics**: failure->success rescue, success->failure disruption, intervention cost, and whether the alert arrived before the last reversible/admissible boundary. Human timing labels can remain auxiliary diagnostics rather than ground truth.

Scope guard: the timing study uses a small number of SWE-bench debugging trajectories for the human-agreement analysis. It is strong evidence that the label itself can be subjective in that setting, not proof that all intervention-timing annotation is unreliable.

## Updated synthesis
The current long-horizon recovery/controller ordering is now better separated:

`authoritative state/effect representation -> pre-call admissibility gate -> execute -> post-call semantic/state-update verification -> classify residual failure/recoverability -> estimate intervention advantage -> event/cadence decision -> reviewer/retry/resume/rollback/replan/abstain -> terminal/effect verification`

New consequence: pre- and post-tool checks should be evaluated as **distinct controls with interaction terms**, not collapsed into a single “verification” switch. Also, reviewer timing should not be trained/evaluated mainly against subjective post-hoc labels when executed rescue/disruption can be measured.

## Exact continuation
1. Find the stronger external-state `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` four-cell experiment with a true `interface-off/recovery-off` cell and full SDK/client/gateway/provider retry accounting.
2. Search software/API studies that independently toggle `state evidence / structured next-actions / idempotency+effect identity / preview / precondition / postcondition` under fixed recovery, and compute interaction rather than only single-component ablations.
3. Search ToolGate supplements, author pages, or later public releases for official code/raw logs; do not infer reproduction from the paper alone.
4. Find exact same-prefix randomized Reviewer/safety-monitor ON/OFF experiments measuring both rescue and disruption. Prefer executed branches over post-hoc human timing labels.
5. Search event-triggered vs every-action review under the same base policy/reviewer, with alerts scored relative to the last reversible/admissible intervention boundary.
6. Continue critic refresh cadence search: `frozen / periodic-k / drift-triggered / continuous` under matched update/evaluation budget.
7. Factor rewind availability, historical target selector, rewind memory/guidance, and context/environment restore with matched post-intervention budget.
8. Preserve DARC-style action-interface compatibility: diagnosis/guidance is meaningful only relative to the intervention set executable from the current state.
9. Continue persistent-refinement contamination tests; exact single-admitted-update future-task ON/OFF replay; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; admission×maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
10. Keep fault classes separate: transient interruption, process-state loss, ambiguous/non-atomic effect, schema/argument, stale/contradictory observation, permission/authority, rate limit, irreversible effect, terminal-belief error, repetition loop, missing procedure, impossible/no-valid-path.
11. Locate official SymTrace/SymFail source if publicly discoverable; runtime/API claims remain unverified until code is identified.
12. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
13. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
