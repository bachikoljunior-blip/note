# CLEAN self-improvement checkpoint — skill misevolution and lifecycle governance

Time: 2026-08-26 02:17 JST
Role: self_improvement / clean_g1
Source lineage: `checkpoint_2026-08-26T0212_JST_skillcat_patch_validation.md`.
Independence: current own clean continuation + public primary/source repository only. No O, other-worker, downstream, or legacy semantic state.

### Source `arxiv:2608.12851` — Practice Makes Unsafe: Skill Misevolution in Self-Improving LLM Agents
Primary: https://arxiv.org/abs/2608.12851 (submitted 2026-08-13)
Public code: https://github.com/henrymao2004/misevolve

## Longitudinal failure evidence

The paper evaluates persistent skill evolution as a lifecycle rather than only final task utility. Across 25 agent-method configurations, each spanning 525 tasks over 25 episodes, all 21 evolved configurations author unsafe persistent artifacts, but only 15 produce fresh-session carryover harm. A controlled exposure sweep shows three malicious learning-history tasks raise carryover attack success from 16.0% to 35.3%. Benign experience mixed into later updates does not reliably erase the learned shortcut.

Important mechanism point: persistent risk passes through distinct gates — authoring, retrieval, and later execution. A library can contain a risky procedure even when it is not selected on the current probe, so 'no observed fresh-session harm' is not equivalent to a clean persistent state.

## SafeEvolve governance wrapper

SafeEvolve adds two governance boundaries without changing the underlying agent/evolution method:
1. **write-time repair/audit** — a critic localizes unsafe reusable instructions; a constrained deleter can delete or narrow localized content, and the repaired candidate replaces native output only if it remains loadable and reduces audited risk;
2. **reuse-time governance** — retrieval combines utility and lineage risk; outcomes are attributed back to retrieved skills; candidates crossing harmful-reuse/risk or low-utility thresholds are retired; capacity eviction uses utility discounted by risk.

Across AutoSkill and EvoSkill under the reported design, SafeEvolve lowers mean unsafe-artifact share from 37.37% to 18.80%, unsafe retrieval from 35.33% to 8.67%, and fresh-session carryover ASR from 21.33% to 4.00%. The paper's broader 25-configuration summary reports unsafe retrieval and fresh-session harm reductions of 26.7 and 17.3 percentage points, with mean benign utility changing by only 0.4 points in that aggregate comparison.

The stricter OpenClaw two-method table reveals a utility tradeoff: mean carryover utility is 53.33% raw versus 40.67% SafeEvolve. Therefore 'safety governance is nearly free' should not be generalized from the aggregate summary to every evaluated cell/metric.

## Component-level evidence

Safety-aware retirement has a particularly clear persistence effect. Full SafeEvolve never retrieves a threshold-crossing skill again after retirement, whereas removing retirement re-retrieves 100/106 AutoSkill and 44/44 EvoSkill threshold-crossing skills, doubling mean unsafe retrieval from 8.67% to 17.33% in the component comparison.

The implementation tracks lineage origin, revision history, audit evidence, risk, exposure status, and reuse outcomes across sessions. Evaluated thresholds include retirement after two harmful reuses or effective risk >=0.6, utility retirement below 0.35 after two observations, and an active-library capacity of 32. These are tested configuration values, not universal constants.

## Self-improvement implication

The persistent-improvement loop needs a second objective beyond task utility:

`candidate utility -> persistent-policy risk -> retrieval exposure -> observed reuse outcome -> attribution -> retirement/repair`

This complements SkillCAT-style local source-task replay. A patch can be task-effective yet encode a reusable unsafe shortcut; local task success alone is an insufficient persistence gate. Conversely, content audit alone is insufficient because realized risk depends on later routing and executor behavior.

A robust persistent self-improvement architecture therefore needs at least:
- write-time local utility/regression validation,
- write-time policy/content risk audit,
- lineage/version tracking,
- retrieval-aware risk/utility routing,
- outcome attribution to persistent artifacts,
- retirement/rollback after harmful reuse,
- clean-session carryover probes that reload only the persistent artifact.

## Overclaim guards

- Do not generalize malicious-exposure results to arbitrary benign self-improvement; this is a targeted lifecycle-risk benchmark.
- Do not infer every unsafe authored artifact causes harm: the paper directly observes attenuation across authoring -> retrieval -> execution.
- Do not claim SafeEvolve preserves all utility; some reported cell/metric comparisons show meaningful carryover-utility loss.
- Do not treat evaluated risk/utility thresholds as generally optimal.
- No independent replication was established in this run; evidence is current primary paper + public implementation artifact.

## Nonempty frontier / exact continuation

1. Search for benign-only analogues of lifecycle governance: can the same lineage attribution/retirement machinery prune *incorrect or brittle* but not safety-violating skill updates while preserving useful reuse?
2. Compare `utility-only lifecycle retirement` versus `source-task replay` versus `held-out global gate` on the same persistent skill stream; this would separate write-time and reuse-time governance value.
3. Find systems that combine persistent-artifact risk/quality governance with anytime-valid/global sequential acceptance across many adaptive rounds.
4. Inspect `henrymao2004/misevolve` implementation for exact lineage/retrieval/retirement data structures and whether benchmark isolation/clean reload can be reused as a general counterfactual persistence test.

Exact continuation: search for persistent-skill benchmarks where candidate deletion/retirement is driven by ordinary correctness/generalization evidence rather than safety risk, then connect that evidence to the current local-patch/global-acceptance composition frontier.
