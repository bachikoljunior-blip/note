# Long Horizon clean_g1 checkpoint — anytime gates, capacity accounting, and post-acceptance surveillance

Invocation start observed from the automation runtime: `2026-08-27T13:59:22+09:00`.
Checkpoint timestamp observed before write: `2026-08-27T14:01:06+09:00`.

## Frozen control tuple
- root control revision: `11`
- role config revision: `5`
- frozen source main SHA: `c721f07be3c743313f255069fed32a4d44c31f55`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched `c721f07...`; later main movement was used only for write-safety and was not adopted semantically.

## Clean-boundary statement
Semantic inputs were restricted to the sanitized root/config, this role's own `LATEST.md`, its immediate own checkpoint, own sanitized feedback, and public sources. No O/O-derived state, other-worker state/output/config, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate ledger, or other-role receipt was read or used semantically. The own sanitized feedback prohibition on shared-ledger reads was followed.

## New direct evidence: anytime-valid admission exists inside a self-evolving software-agent architecture, but gate-specific benefit is not yet isolated
Primary source: **Self-Evolving Agents with Anytime-Valid Certificates**, arXiv:2607.00871, submitted 2026-07-01.

SEA explicitly treats self-modification as a closed-loop statistical problem: the deployed policy generates the data, evaluators, components, and search space used to improve itself. It freezes the base model, confines online changes to a low-dimensional steering layer and a versioned mutable harness, and requires each accepted self-modification to pass an anytime-valid gate backed by a fixed global error budget and an auditable certificate ledger. The mutable harness includes system prompt, tools, budgets, memory, abstraction/library state, and repair primitives, so this is materially closer to persistent-agent maintenance than the previous synthetic best-arm analogue.

The paper also makes an important operational distinction: accepted edits are treated as irreversible commits for familywise risk accounting, and the gate inherits an explicit abstention / no-solution-found state. Continuous peeking is therefore part of the design rather than an afterthought.

Software-agent evidence is on a 52-instance SWE-bench Verified subset. The no-op composite control on GPT resolves 29/52, while the full suite resolves 34/52; GLM 5.2 improves 24/52 to 28/52 relative to its no-op control. However these are **composite-stack** effects. The paper's GPT single-algorithm ablation reports that the verifiable self-modification gate (Alg 4) accepted **0 edits** in that run, so its apparent score is explicitly not an algorithm effect. Therefore SEA supports the feasibility and statistical-control architecture of anytime-valid self-modification, but it does **not** yet provide a clean empirical estimate of the marginal value of the admission gate for persistent memory/skill maintenance.

The paper also states that evaluations are single-run because of cost and that run-to-run variance remains future work. This prevents strong claims about small differences.

Primary sources:
- https://arxiv.org/abs/2607.00871
- https://www.researchgate.net/publication/408341042_Self-Evolving_Agents_with_Anytime-Valid_Certificates (full-text mirror used only to recover experiment-table details)

### Maintenance implication
The previous controller can now separate two questions that were conflated:
1. **Is sequential / anytime-valid statistical admission implementable inside a real software-agent self-evolution stack?** SEA says yes.
2. **Does that gate itself improve persistent maintenance outcomes under matched candidate streams and budgets?** Still unresolved; the direct Alg-4 run accepted zero edits.

This strengthens the `defer / no solution found` state and global error-budget ledger as architectural requirements, while preserving the need for a gate-specific factorial.

## New evidence: capacity growth can counterfeit improvement unless maintenance charges the enlarged action/search class
Primary source: **Scientific CI/CD for Self-Modifying Discovery Agents: Statistical Gödel Gates, Capacity Budgets, and Domain Verifiers**, ICML 2026 workshop paper / OpenReview.

This work adds a distinct failure mode not captured by the previous VOC formulation: **capacity laundering**. A candidate may look better only because it silently receives more capacity—for example a wider retrieval window, more self-consistency samples, more code-generation attempts, a broader tool surface, or increased evaluator authority. The proposed capacity gate requires the measured benefit to exceed both statistical uncertainty and an explicit charge for the capacity delta, and rejects edits that exceed a capacity envelope.

The compact result table reports, in its tested governed setup versus baseline:
- harmful-adoption rate: `6.12% -> 0.008%`
- accepted edits per stream: `100.5 -> 49.2`
- hidden capacity-test MSE: `0.0733 -> 0.0687`
- selected polynomial capacity: degree `15.6 -> 8.7`
- harmful RNA-seq workflow edits accepted: `5/5 possible -> 0/5`

These experiments are a governance demonstration spanning synthetic/executable and dry-lab-style settings, not a production persistent software/API skill bank. The numeric deltas therefore do not transfer directly. The transferable point is that maintenance controllers should not evaluate a candidate only on task reward minus token cost: they must also account for **changes to the hypothesis/action/search capacity** that alter what can be achieved or overfit the verifier.

Primary source:
- https://openreview.net/forum?id=4ob0d33A2l
- searchable PDF mirror: https://openreview.net/pdf?id=4ob0d33A2l

## New evidence: admission and post-acceptance maintenance protect different failure timescales
The same Scientific CI/CD work explicitly separates pre-acceptance statistical/capacity/domain gates from **post-acceptance surveillance**. Its delayed-harm argument is directly relevant to memory and retrieval edits: a memory update can bias future retrievals, a workflow change can alter future data collection, and an objective edit can redirect exploration in ways that retrospective acceptance tests do not expose.

Its lifecycle therefore requires accepted edits to carry:
- immutable incumbent/candidate snapshot hashes and a revert command,
- shadow/prospective audit obligations,
- surveillance boundaries for calibration, invariants, and protected utility,
- automatic quarantine + rollback when a harm alarm crosses the boundary.

It also identifies **verifier memorization** as a longitudinal failure mode: a hidden acceptance set that repeatedly returns feedback gradually becomes training signal. The proposed verifier lifecycle is `commit -> seal -> score -> coarse report -> retire -> refresh`, with retired verifiers kept for forensic audit but not continued promotion. This implies that audit evidence itself has a lifecycle and a contamination budget; a controller that adaptively optimizes against one static holdout can invalidate its own future confidence.

### Maintenance implication
`pre-commit admission gate` and `post-admission maintenance` are not redundant. They address distinct time horizons:
- admission rejects immediately unsupported or capacity-laundered edits;
- surveillance catches delayed harm that only appears under prospective deployment;
- verifier renewal prevents the gate itself from becoming a learned target.

This is stronger than the earlier generic two-timescale hypothesis because it identifies a concrete third state variable: **verifier freshness / exposure history**.

## Synthesis correction
Previous controller hypothesis:
`hard invalidation -> cheap state/domain triage -> maintain decision margins with uncertainty -> estimate {attainable evidence resolution, expected reduction in terminal decision loss / VOC, realized audit cost, future-option value} -> choose {no-op/defer, bounded coalition gate, selective paired/ground-truth audit, detailed attribution} -> update bias-corrected anytime-valid confidence state with logged audit propensities -> act only when confidence/safety conditions support it -> target activation revalidation -> optional consolidation -> post-consolidation revalidation`.

Revised hypothesis:
`hard invalidation -> verifier freshness/authority check -> cheap state/domain triage -> capacity-delta accounting -> maintain decision margins with uncertainty -> estimate {attainable evidence resolution, decision-relevant VOC, capacity-adjusted gain, realized audit cost, future-option value} -> choose {no-op/defer, bounded coalition gate, selective paired/ground-truth audit, detailed attribution} -> anytime-valid admission with global risk spending -> staged/shadow activation when delayed harm is plausible -> post-acceptance surveillance -> rollback/quarantine on harm -> verifier retire/refresh when exposure contaminates acceptance signal -> target activation revalidation -> optional consolidation -> post-consolidation revalidation`.

New constraints:
1. **Capacity changes are part of the treatment.** More tools, attempts, retrieval width, memory, or evaluator authority cannot be credited as a pure skill improvement without a capacity charge or matched-capacity control.
2. **Verifier freshness is state.** Repeated exposure to acceptance feedback can invalidate the holdout's role as independent evidence; maintenance must budget and renew evaluators, not only skills.
3. **Anytime-valid admission does not replace post-acceptance surveillance.** Delayed harm can remain invisible at promotion time.
4. **A no-op/defer output is a first-class safe action.** SEA's abstention semantics and sequential confidence logic reinforce the previous best-arm result.
5. **Composite self-evolution improvements cannot be used to infer the contribution of a gate that accepted zero edits.** Mechanism firing and final-score lift must be distinguished from component-specific causal benefit.

## Remaining frontier
No source found in this invocation implements the full persistent software/API-agent controller that jointly chooses `no-op/defer`, cheap checks, selective paired audits, coalition attribution, repair/retire/suppress, capacity changes, evaluator renewal, staged activation and rollback under one matched compute/capacity budget while reporting final task success, false-retire, stale-retain, delayed-harm escapes, and audit/repair cost.

Exact unresolved items:
1. Find a common-replicate software/API-agent experiment that isolates anytime-valid admission gate benefit from the rest of the self-evolution stack and includes nonzero accepted edits.
2. Search for persistent-memory/skill work that tracks **verifier exposure / holdout retirement** and reports how performance changes when the same hidden evaluator is repeatedly queried.
3. Search for maintenance controllers that charge explicit **capacity deltas** (tool count, retrieval width, attempts, memory budget, evaluator authority) rather than only token/runtime cost.
4. Continue the prior search for a common-replicate four-cell `pre-commit admission gate ON/OFF x post-admission maintenance ON/OFF` experiment with matched candidate stream/model/compute.
5. Recover numeric CASS coalition-size cap `k` and u-SMCO threshold `tau` from official supplement/code if released.
6. Continue hidden semantic-lineage repair, post-consolidation re-externalization, rollback-target selector and decision-influence audit frontiers.
7. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
