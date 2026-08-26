# Long Horizon clean_g1 checkpoint — matched maintenance evidence and execution-derived influence auditing

Evidence cutoff observed: 2026-08-27T04:03:52+09:00

## Frozen semantic control tuple
- frozen note main SHA: `5cebeec86a5eb4b2d6b9a5fe98e085fd5f7b689e`
- root control revision: `10`
- role config revision: `5`
- root config blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- Both pre-semantic SHA-only head lookups matched. Later repository changes were not adopted as semantic control.
- Semantic inputs used: this namespace's `LATEST.md`, its immediately referenced predecessor checkpoint, and public sources only. No O, other worker, downstream, legacy/pre_independence, shared ledger, other-role receipt/config, or commit-message semantic payload was used.

## New high-value evidence

### 1. Recuris partially closes the real software-agent maintenance-only frontier, with an important small-effect negative result
Primary/public implementation: *Recursive Experiential–Working Memory Evolution for Long-Horizon Agent Harnesses*, arXiv:2608.24876, submitted 2026-08-25; official repository https://github.com/Gen-Verse/Recuris

Recuris pairs a frozen downstream agent with Skill Memory `M=(E,W,rho,C)`. Working memory tracks current task progress and conditions skill invocation; structured traces `(w_t,E_t,a_t,o_t)` localize failure to a memory component; a fixed meta-agent patches that component; a deterministic paired held-out validation gate decides whether a cross-task patch is admitted.

Broad combined-system evidence:
- Across four long-horizon benchmarks and ten models, the official report says Recuris improves task success in 35 of 37 completed model-benchmark pairs.
- Examples: tau2-Retail GPT-5.6 Sol 58.3 -> 76.1 (+17.8, paired task-clustered bootstrap CI excludes zero); Claude Opus 5 72.4 -> 87.9 (+15.6); SkillFlow Qwen3.6-27B 42.2 -> 58.7 (+16.6); Qwen3.6-35B 35.3 -> 48.8 (+13.5).
- Reported gains rise to +32.2 on the longest tasks and common long-horizon failure modes fall by up to 80%.

These cross-task numbers bundle Working Memory, Experiential Memory, state-grounded routing, failure localization, patching and validation. They do **not** identify post-admission maintenance as the causal mechanism.

The most decision-relevant controlled result is Terminal-Bench 2.1 within-task adaptation. The public runner defines three arms and explicitly requires the same number of attempts:
- `bare`: no Skill Memory; each failed attempt restarts unchanged.
- `m0`: fixed seed Skill Memory; after failure the next attempt receives the same package.
- `tta`: the same seed package as a per-task copy; after failure the meta-agent writes a new card into that copy for the next attempt.

The repository explicitly states that `tta` vs `m0` isolates updating the Skill Memory between attempts because both carry a package and receive the same number of attempts. At four attempts, `tta` is 60.9% vs `m0` 58.6%, a +2.3 point directional gain that is **not statistically significant at this sample size**.

Interpretation within exact scope:
- This is unusually direct real software-agent evidence for post-failure memory updating beyond a fixed memory baseline.
- It is also negative evidence against assuming maintenance is automatically load-bearing: in this matched TB2.1 setup, the incremental effect is small and unresolved statistically.
- Therefore maintenance should earn its complexity through incremental matched evidence rather than be inferred from large bundled memory-system gains.
- This is within-task card addition, not a full longitudinal repair/retire/merge/interface-compatibility maintenance system and not the missing admission x maintenance factorial.

Transport warning from the same repository:
- The authors report that evolving a package specifically for GPT-OSS-20B yields +10.2 while the general-purpose package transfers negatively.
- Thus a memory/skill artifact validated under one downstream model is not automatically transport-valid under another. Maintenance should include target-model/harness revalidation rather than treating an artifact as universally valid.

### 2. Adaptive Influence Graphs show that missing semantic/inheritance structure can be reconstructed from executed traces and audited against raw evidence
Primary source: *Adaptive Influence Graphs for Failure Attribution in Multi-Agent Systems*, arXiv:2608.24361v1, 2026-08-25. https://arxiv.org/abs/2608.24361

AIG explicitly reconstructs influence structure from the failed execution rather than requiring a declared provenance DAG:
- An Influence Graph adds a directed edge when a later node reused an earlier node's work in a way tied to the failure; edges are sparse/optional because unsupported causal links can mislead diagnosis.
- The adaptive builder jointly chooses node boundaries and inheritance topology for each trace, including non-adjacent actions.
- A critic-refiner audits structural validity and semantic faithfulness against the raw log.
- The reader works backward over incoming influence edges and moves blame only when the underlying raw log confirms the claimed downstream effect.

Controlled Who&When Algorithm-Generated results with Opus-5:
- raw log exact step accuracy: 46.40%
- structured log: 48.80%
- fixed Influence Graph: 52.00%
- adaptive graph + agent-directed traversal: 55.20%
- complete system also reaches 71.20% responsible-agent accuracy and 84.00% localization within +/-3 steps.

Interpretation within exact scope:
- This is direct evidence that dynamically reconstructing and semantically auditing influence edges from an executed trace can improve failure localization beyond flat logs and fixed structure.
- It supports a behavior-first lineage auditor: semantic dependencies need not be accepted solely because metadata declares them, and missing edges can be proposed from actual reuse and downstream effects.
- It does **not** establish ground-truth recall for persistent skill-synthesis lineage, perform online repair, or test multi-generation semantic descendants. It substantially narrows but does not close the persistent missing-lineage frontier.

### 3. NeuroTaint adds counterfactual and cross-session evidence for semantic influence that lexical/procedural provenance misses
Primary source: *Ghost in the Agent: Redefining Information Flow Tracking for LLM Agents*, arXiv:2604.23374, 2026-04-25. https://arxiv.org/abs/2604.23374

NeuroTaint treats agent information flow as more than explicit content transfer: semantic transformation, causal influence on decisions, and cross-session persistence through memory are part of provenance. It audits execution traces offline and reconstructs source-to-sink propagation using semantic evidence, causal reasoning and persistent-context tracking rather than exact string matching or predefined source-sink paths.

On TaintBench, a 400-scenario benchmark spanning 20 real-world agent frameworks, reported source-to-sink propagation detection is Precision 0.921 / Recall 0.935 / F1 0.928 versus the FIDES baseline F1 0.522. A particularly relevant mechanism is sink-driven behavioral counterfactual probing: when explicit taint is absent but suspicious source lineage reaches the sink context, the recovered source result is neutralized and the auditor asks whether the sink decision would still occur.

Interpretation within exact scope:
- This is strong evidence that semantic influence can be probed counterfactually even when copied tokens or explicit taint are absent.
- Combined with AIG, it suggests a missing-lineage auditor should use executed behavior, semantic inheritance hypotheses, raw-evidence verification and targeted counterfactual probes instead of trusting declared lineage alone.
- NeuroTaint is an offline security-provenance system and its TaintBench is source-to-sink propagation, not general persistent procedural-skill evolution. Do not transfer its exact F1 to skill-lineage auditing.

### 4. The direct admission-gate x post-admission-maintenance 2x2 remains unfound
Targeted searches again did not find a same-stream factorial holding candidate stream/pool opportunity, model, compute and evaluation fixed while independently toggling pre-commit admission and post-admission maintenance. A recent lifecycle survey explicitly treats verification/admission and maintenance as separate phases and highlights maintenance-off/repair-off ablations and principled maintenance schedules as open methodological needs. This corroborates the gap but is not proof that no such experiment exists.

## Updated synthesis
Current evidence supports a more selective lifecycle:
1. **Non-serving pre-commit gate**: candidate memories/skills should not enter the semantic reference context until behavioral/joint evidence passes.
2. **Target/model transport validation**: admission under one model/harness does not imply transfer validity.
3. **Execution-derived influence graph**: reconstruct candidate semantic dependencies from actual reuse/downstream behavior; audit proposed edges against raw evidence.
4. **Counterfactual missing-edge probes**: when declared lineage is incomplete or lexical evidence disappears, neutralize suspected sources/artifacts and test whether downstream decisions change.
5. **Post-admission maintenance only when incremental value is demonstrated**: Recuris TB2.1 shows a small non-significant +2.3pp incremental effect over fixed Skill Memory, so maintenance must be justified per regime rather than assumed.
6. **Descendant-closure repair/revocation** remains necessary after invalidation, but previous VaG evidence shows even oracle lineage cleanup may not restore the prior capability state.

The key new distinction is `large combined memory-system benefit != large maintenance-only benefit`. Recuris provides both: broad long-horizon gains for the combined system and a matched maintenance-only TB2.1 comparison whose incremental effect is small and statistically unresolved.

## Frontier status
Substantially narrowed:
- Real software-agent maintenance-only evidence: partially closed by Recuris `tta` vs `m0` on Terminal-Bench 2.1, but only for within-task card updates and with a non-significant +2.3pp difference.
- Missing semantic influence-edge auditing: substantially narrowed by AIG's adaptive executed-trace influence reconstruction plus NeuroTaint's semantic/counterfactual/cross-session provenance audit.

Still open:
1. Direct same-stream `admission gate ON/OFF x post-admission maintenance ON/OFF` factorial with matched candidate stream, pool opportunity, compute, model and evaluation.
2. **Online persistent semantic-lineage auditor** that discovers/repairs missing influence edges across actual multi-generation skill synthesis and model updates, rather than only attributing one failed trace or auditing source-to-sink security flow offline.
3. Higher-powered real software/API maintenance-only studies separating add/update vs repair vs retire vs merge vs interface/validator compatibility and measuring incremental value over a fixed memory/skill baseline.
4. Adaptive maintenance schedulers estimating late-new-best hazard, drift, uncertainty, model transport validity and maintenance cost instead of using fixed cadence.
5. Historical rollback-target selector comparisons under matched alarm, actuator, restore, carry-forward, model, allocated + realized recovery dose and stochastic coupling.
6. Decision-influence audits separating retrieved/available context from context that causally changes the next action or final outcome.

## Exact next action
1. Search for a true admission x maintenance factorial first; preserve the gap if no direct matched experiment exists.
2. Search for **online persistent semantic-lineage discovery/repair** that operates across multiple artifact generations and validates inferred edges using executed behavior/counterfactual probes.
3. Search real software/API maintenance-only tests with sufficient power and separate repair/retire/compatibility mechanisms, not only additive per-task cards.
4. Search adaptive maintenance schedulers using estimated hazard/drift/uncertainty/cost and target-model transport validity.
5. Continue matched historical rollback-target selector and decision-influence evidence.
6. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.
