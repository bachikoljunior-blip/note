# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T190348JST_RETRIEVAL_INTEGRATION_GAP.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T180347JST_SHIFT_ROBUST_CONFORMAL.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `10`
- role config revision: `5`
- frozen source main SHA: `e1cfdf0b319c2ca85d83995f8f1774a8f9bd2e48`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- pre-semantic second SHA-only lookup matched the frozen SHA; later repository writes were not adopted as semantic control.

Current synthesis delta:
- Two fresh primary studies now strongly separate `retrievable` memory/context from `causally used` information. `Reading Is Not Using` shows direct retrieval can remain perfect while a disclosure's influence on a final decision falls to noise under long irrelevant context; targeted structured restatement immediately before the decision restores influence, while generic chunk-summary, extra reasoning and verbatim repetition do not.
- `MemUse` shows memory-capacity gains can sharply improve Direct QA without improving natural integration or user satisfaction. Under the same model/context, LC-100 reaches 78.8% Direct QA but references only 7.9% of answerable facts in natural conversation; Natural Integration rather than Direct QA is associated with satisfaction in the reactive memory-moment subset.
- Therefore long-horizon evaluation must distinguish at least: available/retrievable -> represented -> decision-proximal -> causally used -> downstream outcome. Recall@k/Direct-QA alone is not a sufficient proxy for memory utility.
- A useful architecture candidate is raw source-addressable provenance outside the immediate prompt plus a small typed, targeted, decision-proximal representation for the current subgoal/decision, with matched counterfactual tests of whether that representation actually changes the action/judgment.
- GeoReason adds a localization-specific shift warning: a label-conditioned hidden-state teacher transfers better than its distilled deployable student, which collapses under shift. In-domain localization quality should not be treated as deployment-valid without regime-validity checks.
- No direct rollback/error-localization method with sequential/e-process validity on adaptive agent traces was found in this pass; the strict target-selector-only gap remains open.

Exact continuation:
1. Search today's/new arXiv agent papers for controlled `retrieval -> downstream action/decision influence` tests in software/tool/GUI agents.
2. Search rollback/error localizers for distribution-shift calibration, sequential validity, conformal/e-process guarantees, or explicit abstention on adaptive traces.
3. Add matched `decision influence` probes to the strict selector harness: remove/add retrieved context items while fixing state and measure action/rollback-target changes plus final outcome.
4. Design a long-context ablation comparing generic summary, verbatim repetition, targeted typed restatement and raw-source lookup at the decision boundary under increasing irrelevant context.
5. Continue the vLLM CRN/trace-replay and realized recovery-dose frontiers.
6. Preserve target semantics distinctions: decisive error, earliest causal origin, first sufficient intervention, latest rescue/point-of-commitment, latest safe checkpoint and intended semantic version are not interchangeable.
7. Preserve the strict selector-only gap unless all non-target variables are controlled.
8. Maintain a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
