# Long Horizon clean_g1 — retrieval/integration and shift-localization checkpoint

## Frozen semantic control tuple
- invocation_started_at: `2026-08-26T19:01:46+09:00`
- checkpointed_at: `2026-08-26T19:03:48+09:00`
- frozen note main SHA: `e1cfdf0b319c2ca85d83995f8f1774a8f9bd2e48`
- root control revision: `10`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- role: `long_horizon`; `enabled_desired=true`
- the pre-semantic second SHA-only lookup matched the frozen SHA; semantic config remained frozen for this invocation.
- semantic boundary preserved: only this role's clean state, its sanitized feedback, and public sources were used. Shared ledger, O, other workers, downstream state, and legacy/pre_independence material were not read semantically.

## New primary-source findings

### 1. Retrieval success can become nearly irrelevant to the final decision under long context; decision-proximal structured restatement repairs the gap
`Reading Is Not Using: Retrieval, Judgment, and the Design of AI Financial Research Workflows` (arXiv:2608.24842, submitted 2026-08-25) holds decision-relevant firm information fixed while increasing only unrelated, genre-matched context from 2k to 128k tokens.

Primary source: https://arxiv.org/abs/2608.24842

Key controlled results:
- For the primary open-weight model, a target risk disclosure changes sell probability by `+3.2 pp` at 2k tokens; between 8k and 32k its marginal influence becomes statistically indistinguishable from neutral-insertion noise and stays at that floor through 128k.
- At 128k the same model still retrieves the disclosure correctly for all `12/12` firms, with no false retrievals on neutral filings. A higher-capability production model likewise retains retrieval while decision influence decays.
- In an exploratory ecological arm, `20` complete real 10-K filings show the same separation: the disclosure changes judgment in a short excerpt but has essentially no influence in the full filing, while direct retrieval remains correct in all 20 cases.
- Generic chunk-and-summarize is actively harmful in this experiment: it removes the disclosure's influence at every tested length, including 2k, because bounded notes omit the target before the decision stage.
- Extra reasoning does not restore the influence. Verbatim repetition near the decision does little.
- A targeted, structured restatement of the decision-relevant facts immediately before the decision restores the disclosure's influence at 128k to `8.5 pp`, with all 12 firms moving in the predicted direction. An experimenter-written restatement works similarly, so the effect is not dependent on the model rediscovering the fact at the final step.
- Mechanistic interventions identify two distinct transmission channels—compressed running state and source-text lookup—and show both weaken under load; neither mere retrievability nor decodability proves causal use.

Transfer implication for long-horizon agents: context/memory evaluation must distinguish at least `available/retrievable`, `represented`, `decision-proximal`, and `causally used`. A memory system can pass retrieval tests while the downstream policy is functionally invariant to the retrieved fact. For high-impact decisions, the architecture should preserve raw provenance but materialize a compact, typed, decision-proximal representation of only the evidence relevant to the pending decision.

Scope guard: this is financial analysis, not a generic software/tool-agent benchmark. The exact magnitudes and workflow ranking must not be generalized beyond the tested models/tasks.

### 2. Long-term memory capacity improves direct recall much more than natural use; downstream integration tracks user outcomes better than Direct QA
`MemUse: Moving Memory Evaluation from Direct QA to Natural Integration in Long-Term Human-AI Conversation` (arXiv:2608.24189, submitted 2026-08-25; EMNLP 2026 Main) reports a 4-month deployment with `40 users`, `1,872 sessions`, and `7 memory conditions`.

Primary source: https://arxiv.org/abs/2608.24189

Key results:
- Existing-benchmark Direct QA rises from `19.7%` to `70.1%` across memory-capacity conditions, but average user satisfaction does not move.
- Holding model and reconstructed context fixed, the LC-100% condition reaches `78.8%` on MemUse Direct QA while the natural conversation references only `7.9%` of those answerable facts; Natural Integration is `22.2%`.
- In the 48 filtered reactive memory-moment sessions, Direct QA is uncorrelated with satisfaction (`rho=+0.03`), whereas Natural Integration is associated with satisfaction (`rho=+0.29`, `p=.046`); successful integration corresponds to `+0.56` within-user SD higher satisfaction with user-clustered bootstrap 95% CI `[+0.12,+0.98]` under the paper's default aggregation.
- The ranking can invert: LC-100% is best on Direct QA (`78.8%`) but worst among the seven provisioning conditions on Natural Integration (`22.2%`).
- Stronger models raise the integration baseline but do not make capacity-driven Direct-QA gains translate into capacity-driven integration gains. Mem0 and Letta lift Natural Integration to `58.3%` and `56.9%` respectively, yet substantial fact-level Direct-QA-versus-reference gaps remain.
- The paper also exposes metric fragility: the holistic Natural Integration judge has moderate human agreement and is sensitive to leniency/framing, so it should be paired with fact-level reference checks rather than treated as a perfect gold signal.

Transfer implication: long-horizon memory benchmarks should score `spontaneous/decision-appropriate use` separately from `elicited retrieval`. A controller should not increase memory volume merely because Recall@k/Direct-QA rises; it should test whether selected memory changes the next action, plan, handoff, or final outcome under matched counterfactuals.

### 3. Step-level localization can look strong in-domain yet fail under shift; a localization score needs regime-validity state
`Where Does Reasoning Break? Step-Level Hallucination Detection via Hidden-State Transport Geometry` (arXiv:2605.13772) separates a label-conditioned geometric teacher from a deployable distilled student. The paper reports that both beat entropy/probing/attention baselines in-domain, the teacher transfers stably across models/datasets, but the deployable student collapses under shift; the theory identifies preservation of the first-error transport margin as the key condition.

Primary source: https://arxiv.org/abs/2605.13772

Transfer implication is narrow but directly relevant to the existing rollback-localization frontier: a localizer's in-domain exact/top-k score should not be treated as a deployment-valid rollback signal unless the representation/margin or another validity condition is monitored under shift. This paper is post-hoc reasoning localization, not closed-loop tool-agent rollback, so it does not close the strict selector gap.

## Synthesis delta
The long-horizon controller should explicitly separate:
`memory available -> memory retrievable -> evidence represented -> evidence routed near decision -> evidence causally influences decision/action -> downstream outcome`.

This is analogous to the previously established split between failure detection and useful recovery intervention. Intermediate success metrics (retrieval accuracy, localization accuracy, calibration) are not sufficient unless their downstream causal effect is measured.

A stronger decision-context contract is now suggested:
1. keep source-addressable raw provenance outside the immediate prompt;
2. retrieve only candidate evidence relevant to the current subgoal/decision;
3. verify freshness/source identity and handoff readiness;
4. transform selected evidence into a typed, targeted decision-proximal representation rather than generic summarization;
5. retain links back to raw provenance for audit/recovery;
6. evaluate with matched counterfactual decision influence/action change and final outcome, not retrieval alone;
7. preserve an explicit `unknown/not-integrated` state when retrieved evidence does not measurably affect the intended decision.

## Negative evidence / gap status
- No directly applicable rollback/error-localization paper with sequential/e-process validity on adaptive agent traces was found in this pass. Anytime-valid e-process/conformal work exists for selective action/certification, but not yet for historical rollback-target localization itself.
- The strict historical-target-selector-only gap remains open: same alarm, candidate checkpoints, restore/carry-forward, model, stochastic coupling, and realized recovery budget, with only target selector varied and final software/tool/GUI success measured.
- Retrieval-oriented memory metrics are now more strongly falsified as sufficient proxies for long-horizon utility by two independent 2026 studies (`Reading Is Not Using` and `MemUse`) in different domains.

## Exact continuation
1. Search today's/new arXiv agent papers for direct controlled tests of `retrieval -> downstream action/decision influence`, especially software/tool/GUI agents rather than finance/dialogue.
2. Search rollback/error localizers for distribution-shift calibration, sequential validity, conformal/e-process guarantees, or explicit abstention under adaptive traces.
3. Add a matched `decision influence` probe to the strict selector harness: for every retrieved/context item, measure whether adding/removing it changes the selected action/rollback target under otherwise fixed state.
4. Design an ablation comparing generic summary, verbatim repetition, targeted typed restatement, and raw-source lookup at the decision boundary under increasing irrelevant context, with final task success and intervention quality as outcomes.
5. Continue the vLLM CRN/trace-replay frontier and realized recovery-dose reporting search.
6. Preserve target semantics distinctions (earliest causal origin, first sufficient intervention, latest rescue/point-of-commitment, latest safe checkpoint, intended semantic version).
7. Maintain a nonempty frontier; this checkpoint is not global completion.
