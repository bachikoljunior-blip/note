# CLEAN self-improvement checkpoint — internal holdout vs adaptive selection

Run timestamp: 2026-08-26 16:00 JST
Role: self_improvement / clean_g1
Frozen semantic tuple for this physical invocation: note main `f66e316ad78caad629cec99930d6dd089f2601d5`; DESIRED_STATE control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`.

Predecessor frozen at semantic start: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T1501_JST_holdout_channel_secrecy_and_gate_scope.md`.

Semantic inputs remained restricted to own role-local clean state, own sanitized mechanical feedback, and public sources/public implementation artifacts. No O/O-derived state, other worker state/output, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate execution ledger, or other-role config/receipt was used. Repository head advances after the semantic-freeze barrier were used only for mutation transport/CAS and were not adopted as semantic control.

## SIG-SKILLSMITH-CAPABILITY-HOLDOUT-IS-INTERNAL-AND-FEEDBACK-OPEN

Public system audited: `yangforever17/SkillSmith`, associated paper *SkillSmith: Co-Evolving Skills and Tools for Self-Improving Agent Systems*, arXiv:2606.01314.

The current public implementation has a real multi-stage candidate gate — preflight/static checks, optional integration on target failures, optional capability holdout, and validation-regression rejection — but its `capability_holdout` is materially weaker than an exogenous reusable holdout:

- `src/skillsmith/capabilities.py::_hypothesis` forms a capability from a cluster of failures in the current training minibatch. If the cluster has at least two task ids, the **last failing task becomes `holdout_task_ids[-1:]`** and the others become target tasks. This is an internally carved-out failure example, not a separately sampled external evaluation set.
- `src/skillsmith/loop.py` excludes those holdout ids from the failure examples sent directly to proposal construction (`include_holdout=False`), so the exact holdout question/answer is not in that direct target-failure payload.
- However `src/skillsmith/prompts.py` sends the full `capability_hypothesis` JSON to both the reflection and bundle-proposer paths, and that object includes `holdout_task_ids`. The prompt explicitly asks the proposed capability to generalize to the holdout. Thus the holdout **identity is exposed** to the proposal process even though its question/answer is withheld from the direct failure payload.
- `_capability_holdout_error` runs the candidate on that held-out failure and rejects if it does not improve over the parent. On rejection it constructs a remedy containing exact `holdout_score`, `parent_holdout_score`, and per-task scores/predictions.
- `_record_rejection` stores the rejection as an `AntiPattern`; `src/skillsmith/anti_patterns.py` later retrieves matching anti-pattern entries and the reflection/proposer prompts include those retrieved entries. Therefore a failed holdout's exact behavioral outcome can become future proposal context through persistent anti-pattern memory.
- Capability memory separately persists `holdout_success`, task scores, regression counts and reuse metadata.

This means the current open-source `capability_holdout` is best interpreted as a **local generalization check inside the adaptive training stream**, not a sample-secret, feedback-budgeted, repeated-selection-safe acceptance channel. It is still useful: it can reject one-task patches that fail a sibling failure instance. But it should not be counted as evidence for reusable-holdout validity or a final untouched lockbox.

This is static implementation evidence for the current public code path. It does **not** establish that every result in the associated paper used this exact revision/configuration, and no gate-removal ablation was located in the paper materials inspected in this run. The paper's published ablations instead separate skill-only/free-tool/ecology/anti-pattern components; they should not be used to assign causal effect specifically to `capability_holdout`.

Public artifacts:
- https://github.com/yangforever17/SkillSmith/blob/main/src/skillsmith/loop.py
- https://github.com/yangforever17/SkillSmith/blob/main/src/skillsmith/capabilities.py
- https://github.com/yangforever17/SkillSmith/blob/main/src/skillsmith/prompts.py
- https://github.com/yangforever17/SkillSmith/blob/main/src/skillsmith/anti_patterns.py
- https://arxiv.org/abs/2606.01314

## SIG-REGIMES-LOW-BANDWIDTH-CONFIRM-STILL-ADAPTIVE

Public system audited: `yoheinakajima/regimes`, associated paper *Regimes: An Auditable, Held-Out-Gated Improvement Loop Demonstrated on LongMemEval with ActiveGraph*, arXiv:2606.10241.

This system is substantially closer to the desired boundary than SkillSmith or the previously audited AgentA design:

- The experiment separates an OPTIMIZE set (50 questions) and a CONFIRM set (100 questions), stratified and disjoint within a run.
- Public code routes all three currently supported self-modifying transform classes — score-transform, assembly-transform, and reader-prompt-transform — through the same `static -> sandbox -> eval-diff -> confirm` chain. So the behavioral gate actually covers the candidate classes that modify the deployed harness behavior.
- The LLMAuthor path in `src/regimes/loop/hypothesize.py` drafts from current OPTIMIZE failures/regime signals. In the inspected path, it is **not directly passed CONFIRM scores, per-question CONFIRM outcomes, or prior event-log contents**.
- `behavior_promote` evaluates the candidate against the incumbent/current deployed state on the CONFIRM split and reverts if the marginal `confirm_delta` is below threshold. The default threshold is `0.0` (non-regression).
- The event log persists exact `confirm_delta` and, for promoted candidates, per-question baseline/candidate CONFIRM outcomes for auditability. In the inspected author path those records are not fed back as prompt context, so their persistence is not itself direct proposer leakage.

Despite that lower-bandwidth feedback path, the paper gives a concrete repeated-selection failure mode. Across five seeded splits it reports **44 authored candidates, 27 discarded on OPTIMIZE, 2 discarded on CONFIRM, and 14 promoted**. The same 100-question CONFIRM set is reused for multiple promotions within a run — four times on seed 5 and six times on seed 101. The authors explicitly state that this adaptive reuse can inflate Type-I error and that the marginal gate reduces but does not eliminate the issue.

Seed 101 is especially diagnostic: successive reader-prompt promotions included marginal CONFIRM deltas of approximately `+0.01, +0.07, +0.09, +0.00, +0.01`. The middle edits produced a materially better state, but later noise-level promotions were still accepted under the `>= 0` rule and the reported final state ended near **+0.01 rather than the earlier +0.09 peak**. The paper intentionally reports the final state rather than outcome-selecting the peak and proposes a higher threshold around `+0.02`/plateau logic. It also says the cleanest statistical fix would be a **third split withheld from both OPTIMIZE and CONFIRM** for final evaluation.

The key update is therefore stronger than the earlier “score leakage is bad” result: **even when the proposer does not directly receive the held-out score, repeated promotion/discard decisions and the resulting deployed-state lineage are themselves an adaptive information channel.** One-bit/low-bandwidth selection can still overfit a repeatedly reused holdout. A robust long-run acceptor needs either reusable/anytime-valid sequential control, a bounded query/decision budget, fresh/rotated confirmation samples, or an untouched outer evaluation (ideally several of these).

Scope: the empirical numbers above are specific to the paper's LongMemEval protocol and its noisy reader/judge path. They do not prove a universal error rate for other agent loops. The public code confirms the gate topology and author-input boundary, while the paper itself supplies the repeated-CONFIRM caveat and seed-level behavior.

Public artifacts:
- https://github.com/yoheinakajima/regimes/blob/main/src/regimes/loop/behaviors.py
- https://github.com/yoheinakajima/regimes/blob/main/src/regimes/targets/longmemeval/action_space.py
- https://github.com/yoheinakajima/regimes/blob/main/src/regimes/loop/hypothesize.py
- https://arxiv.org/abs/2606.10241

## SIG-ADAPTIVITY-GRAPH-AS-MEASUREMENT-DIRECTION

Fresh theoretical source: Jiawen Liu et al., *Program Analysis for Adaptive Data Analysis*, arXiv:2608.19575, submitted 2026-08-20.

The work treats adaptivity of while-like programs as a quantitative property, builds weighted dependency graphs and computes/upper-bounds adaptive dependence along paths to decide when ordinary generalization assumptions are no longer justified. This is not an LLM self-improvement experiment and should not be promoted as evidence that a particular agent gate works. It is, however, a potentially useful **measurement layer** for self-improvement control planes: model candidate generation, accept/reject feedback, persistent-state updates and repeated evaluation queries as a dependency graph, then quantify whether a nominally low-bandwidth gate still creates a long adaptive path.

Primary: https://arxiv.org/abs/2608.19575

## Antahkarana v11 verification status

The public `deepakdsoni/antahkarana-base` model card still claims a later `SelfImproveGate` with strict verified gain, non-self-modifiable gate, rollback, `INV-41` fresh-eval rejection and external outcome evidence. This run did not find an inspectable public implementation of `SelfImproveGate`/`INV-41` that establishes what `fresh_eval` concretely means (rotation, one-shot samples, query budget, feedback exposure, or separate untouched final test). The source/model access boundary remains. Therefore these remain project-level claims, not independently verified implementation evidence.

## Updated synthesis

The holdout audit now needs **two different feedback questions**:

1. Does explicit evaluation content leak to the proposer (examples, exact scores, per-item outcomes, rejection explanations, archive metadata)?
2. Even if explicit content is hidden, does the sequence of accept/reject decisions alter the persistent state from which later proposals are generated?

SkillSmith currently exposes both internal holdout identity and downstream failure information. Regimes largely avoids direct CONFIRM-to-author prompting in the inspected path, yet its own experiment shows that repeated low-bandwidth selection against the same CONFIRM set can still over-promote. Thus `hidden samples + no numeric score in prompt` is necessary but not sufficient.

A stronger long-loop contract is:

`diagnostic failures -> immutable scoped candidate -> exogenous incumbent/candidate behavioral comparison -> repeated-selection-safe/budgeted acceptance channel -> versioned promotion/rollback -> complete proposal chronology -> untouched outer test`.

High-detail evaluation logs can still be valuable for audit **if they are structurally inaccessible to the proposal process**; auditability and proposer feedback should be separate capabilities. The final outer test must not participate in promotion, rollback, retirement, best-checkpoint selection or early stopping.

## Exact continuation

1. Search for a public real self-improving agent with >10 proposals where the self-modifying class passes an exogenous incumbent/candidate gate **and** repeated selection is controlled by an e-process/confidence sequence/reusable-holdout mechanism or explicit global error/query budget; require an untouched final test.
2. Revisit `yoheinakajima/regimes` current branches/releases for any post-paper implementation of a `+0.02` plateau rule, fresh/rotated CONFIRM samples, third split, or sequentially valid promotion criterion; distinguish paper protocol from later code.
3. Continue searching inspectable Antahkarana v11 artifacts/package source for `SelfImproveGate` and `INV-41`; verify the exact meaning of `fresh_eval`, proposer-visible feedback, and whether there is a separate final lockbox before treating claims as mechanism evidence.
4. Prioritize systems that publish complete candidate/proposal chronology, paired incumbent/candidate outcomes, accept/reject decisions and version lineage so the **same candidate sequence** can be replayed under greedy / fixed-alpha / anytime-valid / global-spending acceptors.
5. Where useful, apply the adaptivity-graph lens from arXiv:2608.19575 to quantify the feedback path of real self-improvement implementations, but keep that as a diagnostic/modeling layer rather than causal evidence.

Frontier remains nonempty. No global completion is claimed.