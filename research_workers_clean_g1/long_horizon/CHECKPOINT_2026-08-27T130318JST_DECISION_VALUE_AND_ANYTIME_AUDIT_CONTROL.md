# Long Horizon clean_g1 checkpoint — decision value and anytime audit control

Invocation start observed from the automation runtime: `2026-08-27T12:59:40+09:00`.
Checkpoint timestamp observed before write: `2026-08-27T13:03:18+09:00`.

## Frozen control tuple
- root control revision: `11`
- role config revision: `5`
- frozen source main SHA: `af32fdd18a9012f144c60ff5ec4935ebc1eac2f8`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- the SHA-only pre-semantic ref lookup matched `af32fdd...` on repetition; this tuple was then frozen. Later main movement to `23764927...` was used only for write-safety/CAS and not adopted semantically.

## Clean-boundary statement
Semantic inputs were restricted to the sanitized root/config, this role's own `LATEST.md` and immediate own checkpoint, own sanitized feedback, and public sources. No O/O-derived state, other-worker state/output/config, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate ledger, or other-role receipt was read or used semantically. The own sanitized feedback prohibition on shared-ledger reads was followed.

## New primary evidence: adaptive audit sample size can be tied to decision separation, not a fixed N
Primary source: **Best Arm Identification with LLM Judges and Limited Human Audits**, arXiv:2601.21471, submitted 2026-01-29.

This paper studies a useful abstract analogue of persistent-skill auditing: a cheap but biased proxy score is available broadly, while accurate ground-truth labels are expensive and acquired selectively. The proxy bias may depend on both the candidate arm and context. The paper proves that proxy-only best-arm selection can remain inconsistent even with unlimited proxy observations; selective high-fidelity audits therefore require explicit bias correction.

Its estimator combines the broad proxy mean with an inverse-propensity-weighted audited residual `Y-F`. It then constructs **anytime-valid confidence sequences** that remain valid under adaptive arm selection, adaptive auditing and optional stopping. The outer LUCB-style controller compares the current best candidate with the strongest challenger and stops only when the best candidate's lower confidence bound exceeds every competitor's upper confidence bound. Thus the effective audit sample size is not fixed in advance: it grows until the decision margin is statistically separated.

The inner auditing rule allocates expensive labels preferentially to contexts with high residual uncertainty. A positivity condition `pi_t >= pi_min > 0` is required for eligible contexts, and actual audit propensities are part of the estimator. This matters for maintenance controllers: if cheap triage permanently excludes some context from high-fidelity audit, the claimed confidence may be invalid or may never tighten enough to support a safe retire/keep decision.

Empirical scope is deliberately narrow: the paper validates on **synthetic** fixed-confidence BAI environments, not persistent agent memories/skills. It reports anytime coverage above 98% in tested settings and about 48% cost reduction from Neyman-style allocation relative to uniform auditing. These values should not be transferred to software-agent maintenance; the transferable part is the sequential decision structure and its assumptions.

Primary source:
- https://arxiv.org/abs/2601.21471

### Maintenance implication
The previous frontier asked whether an expensive audit can resolve a small skill decision margin. This paper gives a principled alternative to a fixed audit count:

`cheap proxy -> selectively acquire paired/ground-truth outcomes with logged propensities -> bias-corrected estimate -> anytime confidence sequence -> keep auditing the close candidates/unreliable contexts -> stop/defer only when the action-relevant confidence intervals separate`.

This supports a true **defer/no-op state**: if the available budget cannot separate the intervals, do not force a retire/repair verdict merely because an audit was run.

## New theoretical constraint: information gain is not the right acquisition objective by itself
Primary source: **Search as Computation Allocation**, arXiv:2607.27871, submitted 2026-07-30.

The paper formalizes costly internal computations by the terminal decision loss they ultimately change. Under simple regret, myopic value of computation is a knowledge-gradient quantity: the expected improvement in the value of the final selected action. A key negative result is that, for every `rho > 0`, there exists a finite simple-regret problem where choosing the computation with maximum mutual information obtains less than `rho` times the maximum myopic value of computation. In other words, **information gain can rank candidate computations arbitrarily poorly when the objective is terminal decision quality**.

The intuition directly affects the working maintenance controller: an audit may reveal a large amount about a low-consequence skill while a much less informative audit can avert a large downstream loss. Therefore the prior controller field `expected information gain` should be replaced by something closer to **expected reduction in downstream decision loss / decision-relevant value of computation**. Mutual information can still be a bound or surrogate under explicit assumptions, but should not be treated as the universal target.

The paper also gives an important caveat: a purely myopic VOC can value a computation at zero even when it unlocks valuable future computations. A maintenance controller may therefore need limited lookahead for sequences such as `cheap check -> detailed audit -> repair`, rather than deciding every action only by immediate gain.

Primary source:
- https://arxiv.org/abs/2607.27871

### Scope
This is a theoretical computation-allocation result, not an empirical persistent-skill experiment. It falsifies a generic acquisition heuristic, not a specific agent maintenance implementation.

## Primary-detail recovery: exact CASS and u-SMCO mechanics
Primary source: **Coalition-Aware Skill Reliability for Self-Evolving Agents**, arXiv:2608.22610, submitted 2026-08-23.

The current primary PDF resolves several details left open in the previous checkpoint:

### CASS
- It samples `N` distinct skill coalitions.
- Coalition size is drawn uniformly from `{1, ..., k}` and a subset of that size is sampled uniformly.
- For sampled coalition `S`, the knockout margin is normalized by coalition size: `Delta_S(B) = [V(B) - V(B minus S)] / |S|`.
- The sampled coalition statistic is averaged and combined with online outcome reward as `sigma(B) = mean_sampled_margin + lambda * r_out(B)`.
- The reported setting uses `lambda = 0.2`.
- The cost section states that CASS **adds eight coalition evaluations per outer epoch**, about 5% of a roughly 20-hour run. This verifies the tested bounded coalition-evaluation count as eight per outer epoch. It does not establish that every other full-bank/baseline evaluation is included in that count.
- The exact numeric tested value of the coalition-size cap `k` was not recovered from the main PDF in this invocation and remains unresolved.

The paper also explicitly points to **adapting coalition budget to how close candidate banks are** as future work. That is consistent with margin-adaptive auditing, but it is a proposal rather than a demonstrated CASS feature.

### u-SMCO
- Target retrieval quality is computed on an unlabeled target probe set from a memory bank rebuilt under the retained skill subset.
- Each current skill gets a knockout score `psi(s) = RQ(B) - RQ(B minus {s})`.
- The algorithm greedily selects the skill with minimum `psi`, masks it if that value is below threshold `tau`, recomputes scores, and stops when the minimum score is at least `tau`.
- Main experiments use a **20-query unlabeled target probe**.
- The reported complexity is `O(K^2)` memory rebuilds and roughly 6–10 minutes per masking step in the tested setting; it is a one-off pre-deployment operation, not an inference-time cost.
- The exact numeric `tau` was not recovered in this invocation.

This reinforces that `admit at source`, `maintain over time`, and `activate/mask at target` are distinct decisions.

Primary source:
- https://arxiv.org/abs/2608.22610

## Release-evidence update
Primary paper language was checked rather than relying on third-party aggregators:
- **Coalition-Aware Skill Reliability** says its audit toolkit, method code and trained checkpoints **will be released**. No current official repository was verified in this search; treat release as promised, not observed.
- **Dual-Layer Agentic Memory** states that code and dataset **will be released upon acceptance**. This is not current release evidence.
- **SkillShapley**: no official repository was verified in this search. Absence from this search is not proof that none exists.

## Synthesis correction
Previous controller hypothesis:
`hard invalidation -> cheap state/domain triage -> estimate {decision margin, evidence resolution, expected information gain, realized audit cost} -> choose {no-op/defer, bounded coalition gate, paired counterfactual, detailed coalition attribution} -> repair/retire/suppress only when expected decision value is positive -> target-domain activation revalidation -> optional consolidation -> post-consolidation re-routing/revalidation`.

Revised hypothesis:
`hard invalidation -> cheap state/domain triage -> maintain decision margins with uncertainty -> estimate {attainable evidence resolution, expected reduction in terminal decision loss / VOC, realized audit cost, future-option value} -> choose {no-op/defer, bounded coalition gate, selective paired/ground-truth audit, detailed attribution} -> update bias-corrected anytime-valid confidence state with logged audit propensities -> repair/retire/suppress only when the action-relevant confidence condition and safety constraints are satisfied -> target-domain activation revalidation -> optional consolidation -> post-consolidation re-routing/revalidation`.

New constraints:
1. **Do not optimize generic information gain.** Acquisition should be valued by downstream decision loss; information can be high yet decision value arbitrarily small.
2. **Let evidence need determine audit count.** Fixed `N` is often only a budget cap; close decisions should remain provisional until the attainable confidence resolution supports action or the controller explicitly defers.
3. **Log selective-audit propensities and preserve exploration positivity** if using bias-corrected sequential inference. Otherwise cheap triage may create blind spots that invalidate confidence claims.
4. **Routine CASS-like coalition gating and detailed attribution remain distinct layers.** CASS's tested eight coalition evaluations/epoch are a bounded gate signal; they do not provide fine per-skill causal resolution.
5. **Consider limited lookahead.** A cheap computation can be valuable mainly because it enables a more targeted expensive audit or repair later; purely myopic VOC may miss this.

## Remaining frontier
No source found in this invocation implements the full persistent software/API-agent controller that chooses among `no-op/defer`, cheap checks, selective paired audits, coalition attribution, repair/retire/suppress and activation revalidation under one matched compute budget while measuring final task success, false-retire/stale-retain, and audit/repair cost.

Exact unresolved items:
1. Recover the numeric CASS coalition-size cap `k` and u-SMCO threshold `tau` from official supplement/code if released.
2. Find a persistent-memory/skill study that uses **anytime-valid margin-based stopping** or an equivalent sequential audit rule and reports false-retire versus stale-retain trade-offs.
3. Search for metareasoning controllers with limited lookahead that choose among stop/no-op, multiple information-gathering actions and repair under one budget; distinguish theoretical/search examples from persistent maintenance.
4. Seek a common-replicate four-cell `pre-commit admission gate ON/OFF x post-admission maintenance ON/OFF` software/API-agent experiment with matched candidate stream/model/compute.
5. Continue hidden semantic-lineage repair, post-consolidation re-externalization, rollback-target selector and decision-influence audit frontiers.
6. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
