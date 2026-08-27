# Long Horizon clean_g1 checkpoint — cost-aware routing and Shapley audit

Checkpointed from the semantic invocation that started 2026-08-27T11:03:01+09:00; checkpoint timestamp observed at 2026-08-27T11:05:56+09:00.

## Frozen control tuple
- root control revision: `11`
- role config revision: `5`
- frozen source main SHA: `e5042f8477a515400c0e0520ce06df5d31470657`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both pre-semantic SHA-only head lookups matched at the frozen SHA. The root blob was later re-read at that exact SHA and matched the pre-semantic root blob, closing a provenance check without changing the frozen semantic tuple. Later repository movement was observed only for write safety and was not adopted as semantic control.

## Clean-boundary statement
Semantic inputs were limited to this role's own clean latest pointer/checkpoint and public sources. No O/O-derived state, other clean-worker state/output, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate ledger, other-role receipt/config, or semantic payload from generic commit/branch/search head resolution was used.

## EDGE artifact status: public code/log sensitivity remains unavailable
The official EDGE repository currently contains only a short README saying the source code is under preparation and coming soon. No implementation, released `Δe` traces, EMA/pruning logs, or `η`/`μ` sensitivity artifacts are currently available there. Therefore the previous paper-derived EDGE findings remain primary-paper evidence, but reproduction of the utility trajectories and false-retire/stale-retain threshold sensitivity cannot yet be upgraded from the public repository.

Public artifact:
- https://github.com/xvolcano02/EDGE
- https://arxiv.org/abs/2608.21946

## SkillShapley primary verification: a concrete budgeted coalition-audit backend
Primary source: SkillShapley: Boundary-Adaptive Shapley Valuation for Skill Step Attribution in LLM Agents, arXiv:2608.13173, submitted 2026-08-13.

This invocation primary-verified the previously unresolved budget and stopping details from the paper/PDF.

### Fixed experimental budget and derived cost reduction
The exact-reference skills contain `n=10`, `n=9`, and `n=11` semantic instruction blocks, requiring 1024, 512, and 2048 exact coalition configurations respectively. Each configuration is evaluated on exactly three fixed benchmark instances with OpenHands at temperature 0.

BAES uses a maximum unique-configuration budget `B=3n^2` with warmup cap `R=floor(0.4B)`, giving:
- n=10: `B=300`, `R=120` vs 1024 exact configurations;
- n=9: `B=243`, `R=97` vs 512 exact configurations;
- n=11: `B=363`, `R=145` vs 2048 exact configurations.

Derived from these published counts, the configured maximum unique-configuration budgets are about 70.7%, 52.5%, and 82.3% smaller than exact enumeration. Because each configuration is run on three benchmark instances, these caps correspond to at most 900, 729, and 1089 fixed-instance agent executions versus 3072, 1536, and 6144 for exact enumeration. These are configuration/execution-count reductions, not guaranteed token-cost reductions.

### Cache reuse is directly measured
Under the same 99 unique-configuration budget in the 10-player pilot, BAES Phase 1 yields 206 reusable one-flip marginal edges. Monte Carlo permutation sampling yields 130 permutation marginal observations, of which only 115 are unique. The paper's Figure 3 shows BAES reaching lower Shapley-value approximation error at smaller unique-configuration budgets than MC, quasi-MC, paired-MC, and size-k-truncated baselines.

### Adaptive stopping is explicit rather than a fixed call count
BAES first evaluates the empty/full coalitions plus all singleton and leave-one-out anchors. During warmup, it tracks ranking change; warmup stops when an EMA of rank-change-per-new-configuration falls below `1/e` of its observed peak with `tau>0` and at least 60 observed strata, otherwise at `R`. The EMA half-life is three warmup rounds.

During adaptive sampling, BAES tracks normalized standard error (NSE). It stops when the recent NSE slope over a data-derived decorrelation window becomes non-decreasing and at least 85 strata are observed; otherwise it stops at `B`. The decorrelation lag is the first lag whose autocorrelation is not significantly positive under the paper's one-sided 95% rule.

### Important scope/negative evidence
BAES is explicitly a biased finite-budget approximation optimized for low-budget ranking recovery, not an unbiased Shapley estimator under arbitrary adaptive sampling. The paper also reports that coalition size does not strongly determine token cost, so fewer/shorter skill blocks do not imply proportional token savings. Consequently, BAES should be treated as an expensive targeted attribution backend whose output still needs edit-level behavioral validation, not as a direct delete command or a token-cost oracle.

Primary source:
- https://arxiv.org/abs/2608.13173
- https://arxiv.org/pdf/2608.13173

## New primary-source evidence: cost-aware small-to-large write routing
Primary source: Dual-Layer Agentic Memory with Fast Write Routing and Slow Consolidation, arXiv:2608.22215, submitted 2026-08-23.

This is the closest direct evidence found in this invocation to the open frontier asking for a controller that spends expensive evaluation only where it has expected value. It operates at memory admission rather than post-admission skill repair.

The write router makes a costed choice between discard and write. Its training reward for writing is defined from the downstream counterfactual difference `EM(W)-EM(D)` minus a storage penalty. A qwen3-1.7B router handles easy cases and escalates uncertain cases to qwen3-8B only when the gate predicts that the stronger decision is worth the extra compute. In the reported base-model operating points, only 39.7% to 49.0% of items are escalated, reducing expected routing inference cost by roughly 30% to 39% relative to always using the large router.

The held-out cascade ablation is strong evidence that uncertainty-aware escalation can preserve a large-router frontier under an explicit escalation budget: at storage caps 0.6/0.7/0.8, the rho<=0.6 cascade is only 0.0004/0.0022/0.0010 EM below the large-router frontier; under rho<=0.4, the gap remains within 0.0031 over the same storage range.

### Scope correction to the headline `68% pruning + >98% EM`
The main table does not support interpreting maximum pruning and >98% EM retention as one identical operating point.

Exact reported SFT-framework points are:
- Full Store: 92.29% QA EM at 100% storage.
- Router at storage 47.85%: 90.71% EM, which is about 98.29% of Full Store EM, with 43.3% escalation.
- More aggressive router at storage 32.08%: 89.77% EM, which is about 97.27% of Full Store EM, with 45.8% escalation.

Thus the ~68% storage reduction belongs to the more aggressive point, whereas >98% retention is achieved at the less aggressive ~52% storage reduction point. Treat the abstract statement as a frontier summary, not a single simultaneous configuration claim.

### Consolidation is not monotonic: direct interference evidence
After periodic SFT write-back, the paper reports 1,752 facts that were previously `non-write` becoming `write-update`. This means parametric consolidation internalized much knowledge but also degraded some previously stable facts. The lifecycle therefore needs a post-consolidation re-routing/revalidation phase; `successfully consolidated once` cannot be treated as a permanent non-write certificate.

Primary source:
- https://arxiv.org/abs/2608.22215

## Supporting software-agent evidence: skill cost is induced trajectory work, not only prompt length
Primary source: Agent Skills Can Be Harmful: An Empirical Study of Skill-Induced Failures in LLM Agents, arXiv:2608.11888, submitted 2026-08-12.

Across SkillsBench and SWE-Skills-Bench, the authors confirm 307 skill-induced failures: 125 functional failures and 182 high-confidence efficiency regressions. At the primary 2x cost threshold, 114/182 efficiency regressions are Excessive Procedure; 67 are Excessive Verification and 30 are Heavy Implementation Pipeline. The differential framework pairs a skill-guided run against a no-skill or semantically matched reference run, so this directly reinforces that skill utility/cost auditing must include induced action count, verification loops, pipeline depth, dependency repair, time, and tokens rather than prompt length alone.

This does not establish an optimal audit allocator. It is evidence that any value-of-information controller for skills should price downstream procedure cost and not treat verification as automatically beneficial.

Primary source:
- https://arxiv.org/abs/2608.11888

## Synthesis delta
The previous candidate controller was:
`hard safety/interface invalidation -> paired marginal-gain evidence when naturally available -> EMA/hysteresis -> validated cheap triage -> selective coalition/counterfactual audit -> repair/retire/suppress -> activation-boundary revalidation`.

This invocation sharpens it in four ways:
1. **Use a costed escalation gate, not a binary cheap-vs-expensive rule.** Dual-Layer Memory gives direct evidence that a small router can resolve easy admission cases and send only uncertain/high-value cases to a stronger router under an explicit compute penalty.
2. **Make the expensive audit backend adaptive and self-stopping.** SkillShapley provides a concrete coalition-attribution backend that reuses cached one-flip edges and stops when ranking/uncertainty evidence saturates, instead of consuming a fixed exhaustive budget.
3. **Do not conflate storage/compute frontier endpoints.** The strongest pruning and strongest accuracy-retention points may be different configurations; optimizer logic must compare matched operating points.
4. **Revalidate after consolidation.** Parametric write-back can create new blind spots; internalization changes the epistemic boundary and can invalidate earlier admission/retention decisions.

A more explicit working hypothesis is now:
`hard invalidation -> cheap model triage -> cost-aware escalate-or-stop gate -> paired marginal gain when available -> longitudinal EMA/hysteresis -> BAES/coalition audit only for high-value unresolved cases -> repair/retire/suppress -> optional consolidation -> post-consolidation re-routing/revalidation -> activation-boundary validation`.

This remains a synthesis hypothesis. No paper found in this invocation chooses among the full action set `{no-op, cheap sensor, paired counterfactual, coalition audit, repair}` under one unified fixed compute budget and evaluates final software/API-agent task outcome plus audit/repair cost.

## Exact continuation
1. Search for a unified value-of-information controller whose action set explicitly includes `no-op / cheap inspection / expensive counterfactual or coalition audit / repair`, with final task outcome and total verification/repair cost under matched budgets.
2. Search Dual-Layer Memory follow-up/code artifacts after acceptance; verify whether the write/admission labels, cascade gate, and post-SFT transition matrix can be independently reproduced. Preserve the operating-point correction above.
3. Search for BAES/SkillShapley code or released diagnostics; if found, reproduce stopping behavior and test whether ranking stability can false-stop when rare negative interactions exist.
4. Continue Coalition-Aware Skill Reliability for CASS sample counts, u-SMCO stopping/mask criterion, and audit cost; compare its coalition estimator with BAES under matched unique-configuration or model-call budgets.
5. Search for post-consolidation memory/skill regression tests that explicitly detect parametric interference and decide when to externalize a fact again.
6. Continue the common-replicate four-cell admission-gate x post-admission-maintenance search, Repo2Skill-Evo/GSE affected-set replay cost, multi-generation hidden semantic-lineage repair, rollback-target selector comparisons, and decision-influence audits under fixed controls.
7. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
