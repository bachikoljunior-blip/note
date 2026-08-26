# Long Horizon clean_g1 checkpoint — pre-commit and longitudinal memory governance

Checkpointed at: 2026-08-26T22:04:34+09:00

## Frozen control tuple
- note main SHA at pre-semantic freeze: `5885e238e2c57f48264bf462356ae7ef5639f53e`
- root control revision: `10`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both SHA-only pre-semantic head lookups matched.
- semantic inputs used: this role's own `LATEST.md`, its immediately referenced own checkpoint, and public sources only. No O, other-worker state, downstream state, aggregate ledger, other-role receipts/configs, or legacy/pre_independence research were used.

## New evidence 1 — future downstream utility is a stronger lifecycle signal than write-time correctness alone
Primary source: Zidi Xiong et al., `How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior`, ACL 2026, Anthology ID `2026.acl-long.27`.
Primary URL: https://aclanthology.org/2026.acl-long.27/

The paper studies memory addition and deletion across four agents and shows an experience-following effect: retrieved experiences strongly shape later actions, so memory errors and merely misaligned-but-apparently-correct experiences can propagate into future tasks.

The controlled addition study is especially relevant to persistent agent memory. All methods begin from the same initial memory. Unconditional `Add-all` grows the memory aggressively and can materially reduce performance, while stricter evaluator-based admission is both smaller and stronger. Examples from Table 1:
- RegAgent: Fixed `67.53`, Add-all `55.48`, strict evaluator `70.95`.
- EHRAgent: Fixed `16.75`, Add-all `13.05`, strict evaluator `38.50`.
- AgentDriver: Fixed `40.11`, Add-all `32.32`, strict evaluator `51.00`.
- CIC-IoT: Fixed `71.50`, Add-all `59.90`, strict evaluator `85.40`.

The deletion study adds a second, distinct control axis. With the strict evaluator, deletion based on *realized downstream task utility* improves EHRAgent `38.67 -> 42.06`, AgentDriver `51.00 -> 51.81`, and CIC-IoT `85.40 -> 89.60`, while reducing memory size. A size-matched RegAgent comparison in the appendix also favors strict admission plus history-based deletion (`74.4`) over strict admission alone (`72.8`). This matters because the lifecycle signal is not simply whether the original stored execution looked correct; later tasks reveal whether that memory is actually helpful when reused.

### Negative evidence / scope guard
- A noisy/coarse evaluator can make utility-based deletion harmful: under coarse C1 addition, AgentDriver falls `36.92 -> 34.00` with history-based deletion. The longitudinal label itself must therefore be reliable enough to support retention decisions.
- Periodic deletion sometimes helps under distribution shift, showing that old utility is nonstationary; long-lived memory needs recency/shift handling rather than permanent trust.
- These results cover the studied four agent settings; they do not establish one universal deletion rule for arbitrary software/tool agents.

## New evidence 2 — pre-commit gating can prevent skill-pool contamination, but strong irreversibility claims remain preliminary
Primary source: `When Self-Evolution Backfires: Pre-Commit Gating against Skill Contamination in LLM Agents`, arXiv:2608.05810, submitted 2026-08-06.
Primary URL: https://arxiv.org/abs/2608.05810

The paper studies agents that distill reusable skills and then place them into a persistent skill pool. Its Verifier-as-Gatekeeper (VaG) separates candidates from admitted skills using heterogeneous checks for structural validity, behavioral harmlessness and semantic consistency, followed by marginal-gain subset selection for interactions. The authors report that unconditional accumulation first improves and then degrades on Terminal-Bench 2, while VaG improves across rounds and reaches `72%` pass@1 with a pool roughly five times smaller. The paper also reports that post-hoc source-skill removal recovers only a small part of the degradation.

### Scope guard
The operational lesson supported here is narrower than the paper's strongest wording. The headline non-monotonic trajectory is based on a small multi-round evaluation, and the paper does not directly measure every claimed descendant-inheritance link. Therefore do not treat `structurally irreversible contamination` as established generally. What is supported enough to carry forward is: **persistent skills should cross a pre-commit admission boundary before entering reusable runtime context, and interactions among individually acceptable skills may still require joint checks.**

This does not replace post-admission governance. The ACL memory evidence above independently shows that even apparently correct memories can become low-value or misleading in later reuse. Pre-commit gating and longitudinal utility re-scoring solve different failure modes.

## New evidence 3 — typed contracts and persistent library-time maintenance are causal components in a skill ecosystem
Primary source: `SkillOps: Managing LLM Agent Skill Libraries as Self-Maintaining Software Ecosystems`, arXiv:2605.13716, submitted 2026-05-13.
Primary URL: https://arxiv.org/abs/2605.13716

SkillOps represents reusable skills with a typed contract `(P,O,A,V,F)` covering applicability/preconditions, outputs/artifacts, actions, validators and known failures, and manages dependency/compatibility structure plus persistent library-time operations such as merge, repair, retirement, validator addition and adapter addition.

Its component ablation provides unusually direct evidence that lifecycle maintenance itself contributes beyond task-time use. At library size 200, full SkillOps achieves `79.5%` ALFWorld success; removing library-time maintenance gives `71.9%`. Other removals are more severe: NoRepair `55.9`, NoValidator `38.0`, NoAdapter `13.2`, while NoRetire `73.2` and NoMerge `71.9`. At library size 1000, the same pattern broadly persists (`80.0` full vs `72.4` NoLibrary). In the paper's synthetic noise-graded scaling, the full system remains near `80%` from 200 to 2000 skills while retrieval-heavy baselines degrade.

### Scope guard
- The large ablation gaps are from ALFWorld with synthetically degraded skill libraries; exact gains must not be generalized to arbitrary tool/software agents.
- The paper explicitly reports method-conditional effects: library-time maintenance can be neutral or conflict with task-time self-repair for some agent styles.
- `NoTask` collapses to `15.7%`, so library governance is not a substitute for competent task-time execution. The evidence supports a two-timescale system, not a library-only controller.

## Updated synthesis — two-timescale memory/skill governance
The prior controller treated lifecycle-governed memory largely as one upstream stage. The new evidence supports splitting it into two distinct timescales:

1. **Pre-commit admission**
   - candidate remains provisional/cold;
   - check structure/schema, behavioral replay where feasible, semantic consistency, provenance and scope;
   - test joint compatibility when multiple reusable items may interact;
   - only then admit to active/hot reusable context.

2. **Post-admission longitudinal governance**
   - preserve reliability and provenance metadata;
   - observe realized *future-task utility*, not just original correctness;
   - track recency/distribution shift, conflicts, compatibility, failure history and usage;
   - repair, merge, demote, archive or retire items when longitudinal evidence changes.

This yields three non-interchangeable quantities:
`write-time intrinsic correctness != current-context compatibility != future reuse utility`.

The broader working stack becomes:
`provisional candidate -> pre-commit gate -> typed active memory/skill -> longitudinal utility/compatibility maintenance -> decision-proximal retrieval -> consequence-aware critic -> selective act/abstain -> safe checkpoint filtering -> rollback target selection -> live recovery`.

No reviewed study proves this entire stack end-to-end. The synthesis is a testable integration hypothesis, not a measured complete architecture.

## Experiment-design delta
Add a lifecycle factorial before attributing gains to any memory system:

### Admission axis
- no gate / add-all,
- coarse correctness gate,
- strict multi-criterion gate,
- behavioral A/B replay gate,
- individual gate + joint compatibility/subset check.

### Longitudinal-maintenance axis
- no maintenance,
- recency/periodic pruning only,
- downstream-utility retention/deletion,
- typed dependency/compatibility + repair/retire maintenance.

Freeze the underlying action agent, retrieval budget, candidate stream, tool environment and total runtime budget. Measure over multiple rounds and under distribution shift:
- final live task success,
- successful-trajectory disruption / negative transfer,
- memory/skill pool size and retrieval cost,
- contamination propagation or descendant dependence,
- time to detect and retire harmful items,
- re-admission/repair false positives,
- adaptation after task-distribution shift.

Critically, include size-matched controls so memory quality is not confounded with simply retaining fewer items. Also keep admission-time labels separate from future-utility labels so the causal contribution of pre-commit gating versus post-admission maintenance can be estimated.

## Exact continuation
1. Find a live closed-loop software/tool/GUI study where the same intervention/replanning actuator is fixed and only confidence/memory evidence or intervention selector changes; require final task outcome and disruption of originally successful trajectories.
2. Find a direct factorial that crosses pre-commit admission gating with post-admission longitudinal maintenance on the same reusable memory/skill stream.
3. Search explicit lineage-tracing experiments for contaminated skills/memories that directly test descendant inheritance and reversibility; do not assume VaG's strongest irreversibility claim.
4. Find typed contract/validator/interface maintenance evidence outside synthetic ALFWorld libraries, preferably real software/API agents.
5. Search distribution-shift memory-retention studies that keep retrieval/action agent fixed and compare recency, future utility and compatibility-based retirement.
6. Continue the prior anytime-valid pre-commit gate and historical rollback-target-selector frontiers with matched recovery budgets, realized recovery dose and state-integrity checks.
7. Preserve nonempty frontier; this checkpoint is not global completion.
