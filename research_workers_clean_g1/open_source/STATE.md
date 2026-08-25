# Open Source Systems Scan — clean_g1

Generation: `clean_g1`
Worker: `open_source`
Started clean: 2026-08-25T17:01:39+09:00
Independence boundary: this run did not read legacy `research_workers/open_source/`, comparator/integrator state, or O/O-derived state. Exploration used public repositories, public benchmark artifacts, and primary/public paper pages only.

## Search bias / seed trajectory

Repo/artifact-first search for reproducible mechanisms relevant to agent improvement: public benchmark repositories, fixed experiment runners, tracked result summaries/leaderboards, and implementation contracts. Initial branches independently searched persistent-agent improvement, skill evolution/transfer, and data-centric recursive self-improvement.

## Candidate findings

### clean-os-g1-001 — Historical-best preservation decoupled from exploratory continuation

**Mechanism.** Maintain an immutable/high-watermark `best_attempt` or checkpoint ledger while allowing subsequent experiments to be non-monotone. Exploration can continue, but deployment/final selection chooses the most reliable historical checkpoint rather than the last attempt. Separate search policy from selection policy.

**Primary evidence.** RSIBench-Data (`evolvent-ai/RSIBench-Data`, arXiv:2607.25886) fixes the post-training/evaluation stack and lets agents revise only training-data strategy. Across 24 agent×benchmark settings, 14/24 (58.33%) found a later candidate better than the first valid attempt. Among 23 trajectories that continued after reaching the best observed score, 18/23 (78.26%) ended with a lower-scoring final attempt and 5/23 only recovered the same peak; none raised the frontier after the historical peak. The paper explicitly identifies preservation of strong checkpoints as a pattern in stronger runs.

The public runner implements this design directly: `runner/run_session.sh` initializes `best_attempt`, records every attempt in durable budget state, exposes `final_submit.sh <attempt_id>`, validates the selected historical attempt, and requires an official evaluation on the selected checkpoint. The generated run contract instructs the agent to inspect artifacts/evals before another attempt and to submit the best completed reliable checkpoint rather than equating the last attempt with the final result.

**Artifact grounding.** Public SWE-bench Verified baseline diagnostics for `Qwen/Qwen3.5-35B-A3B-Base`, seed 23 random 100, record raw/completed score `0.12`, 12/100 resolved, 0 Harbor errors, 43,100,492 input tokens and 4,991,056 output tokens, demonstrating a tracked executable baseline rather than README-only claims.

**Transfer hypothesis.** Any iterative agent-improvement loop should checkpoint every evaluated candidate, maintain a monotone best-so-far ledger, and make final/deployment selection a separate evidence-aware operation. This is especially valuable when later experiments are cheap enough to explore but unreliable enough to regress.

**Scope / uncertainty.** Headline 58.33% and 78.26% are descriptive across 24/23 settings, not a proof of universal behavior. The public baseline diagnostic is one 100-task SWE-bench sample and does not itself establish improvement. Treat mechanism as strong operational evidence, not universal causal proof.

**Primary sources.**
- https://github.com/evolvent-ai/RSIBench-Data
- https://github.com/evolvent-ai/RSIBench-Data/blob/main/runner/run_session.sh
- https://github.com/evolvent-ai/RSIBench-Data/blob/main/skills/rsibench-data-factory/SKILL.md
- https://github.com/evolvent-ai/RSIBench-Data/blob/main/benchmarks/swe_bench_verified/runs/qwen35base_seed23_random100/RESULT_SUMMARY.md
- https://arxiv.org/abs/2607.25886

### clean-os-g1-002 — Build procedural skills from diverse multi-model traces, not one model’s experience

**Mechanism.** Evolve reusable procedural-memory artifacts from a heterogeneous pool of execution traces produced by multiple model backbones. The diversity of failure/success modes appears to reduce over-specialization and improves cross-model transfer.

**Primary evidence.** AFTER (`DavydenkoGr/AFTER`, arXiv:2606.23127) provides 382 executable enterprise tasks across 6 roles and 22 procedural skills with controlled local, cross-task, cross-role, and cross-model transfer evaluation. The paper reports that one refinement round improves aggregate performance by 3.7–6.7 points. Skills evolved from diverse multi-model traces reach 73.1% cross-model test accuracy versus at most 59.4% for single-model trace sources (13.7-point gap to the best single-source result). The same study reports cross-role specialization can hurt transfer by as much as 7.5 points, so diversity is not a license to use one global skill indiscriminately.

**Artifact grounding.** The public repository exposes the task manifest and strict agent/oracle boundary. `tasks/manifest.json` stores task role/skills/split metadata; task instructions expose only agent-visible inputs/output contracts while generator/reference/verifier assets are oracle-side. This supports repeatable skill-evolution experiments without giving the agent verifier internals.

**Transfer hypothesis.** When distilling skills/policies from experience, sample experience across heterogeneous model/scaffold failure modes, and evaluate on held-out target models/tasks. Preserve role/domain metadata so general skills can be separated from specialized skills rather than forcing one artifact to serve every context.

**Scope / uncertainty.** AFTER is currently an arXiv preprint and the GitHub repository primarily exposes the benchmark/task artifacts rather than all paper experiment outputs. Quantitative claims come from the paper; public repo evidence confirms task/evaluation structure, not all result tables.

**Primary sources.**
- https://github.com/DavydenkoGr/AFTER
- https://github.com/DavydenkoGr/AFTER/blob/main/tasks/manifest.json
- https://arxiv.org/abs/2606.23127

### clean-os-g1-003 — Skill injection must be gated by model × scaffold × domain; blind retrieval/broadcast can catastrophically regress

**Mechanism.** Treat procedural-skill application as a conditional routing problem. Before injecting a retrieved/evolved skill, estimate compatibility with the current model, agent scaffold, and domain; allow fallback to vanilla behavior when compatibility evidence is weak. Do not assume a method that helps one scaffold/domain transfers to another.

**Primary artifact evidence.** EvoAgentBench’s public source-of-truth leaderboard (`EverMind-AI/EvoAgentBench`, `src/data/leaderboard-data.ts`) records large interaction effects across the same models/domains:

- Nanobot + Qwen3.5-27B + SWE-Bench: vanilla 45.8; Memento 9.5 (**−36.3**), ReasoningBank 53.0 (**+7.2**), GEPA 48.8 (**+3.0**).
- OpenClaw + Qwen3.5-27B + GDPVal: vanilla 43.6; GEPA 31.3 (**−12.3**), ReasoningBank 48.2 (**+4.6**).
- OpenClaw + Qwen3.5-397B + SWE-Bench: vanilla 66.7; Memento 63.7 (**−3.0**), ReasoningBank 61.3 (**−5.4**), GEPA 67.9 (**+1.2**), curator-routed diagnostic Anchor Skill 76.8 (**+10.1**).
- Nanobot + Qwen3.5-397B + SWE-Bench: vanilla 62.5; GEPA 71.4 (**+8.9**), diagnostic Anchor Skill 79.8 (**+17.3**).

The repository explicitly labels Anchor Skill as a diagnostic reference using curator-side Ability labels, not a deployable automatic method. Its large headroom relative to automatic methods suggests routing/selection quality is a major bottleneck, while the Memento collapse shows that a plausible memory mechanism can be actively harmful under a mismatched scaffold/domain.

Turn-cost artifacts also vary sharply by scaffold/model: e.g. Memento changes OpenClaw Qwen3.5-27B turns by +40.7%, while GEPA changes Nanobot Qwen3.5-27B turns by −7.2%, so quality and runtime cost should be jointly gated.

**Transfer hypothesis.** Use per-context admission: compare predicted benefit/cost to a vanilla control; route skills by learned/verified capability labels; keep a no-skill fallback; require held-out evidence before broadcast. Track negative transfer as a first-class signal.

**Scope / uncertainty.** The public leaderboard contains means and omits standard errors on the site; the repository states the values are Table 3 means. Some methods can improve strongly in other cells, so evidence supports interaction/gating, not blanket rejection of any method.

**Primary sources.**
- https://github.com/EverMind-AI/EvoAgentBench
- https://github.com/EverMind-AI/EvoAgentBench/blob/main/src/data/leaderboard-data.ts
- https://github.com/EverMind-AI/EvoAgentBench/blob/main/benchmark/README.md

### clean-os-g1-004 — Retrieval/closeout gates for persistent-state use are plausible but global gains are noisy

**Mechanism.** Insert explicit state-consultation and persistence-closeout stages into a persistent agent loop: plan-time state consultation; typed/scoped/expiry-aware rendering; procedural skill routing; retrieval-before-action gating; synchronous authoritative closeout.

**Evidence.** PAST-Bench (`Gen-Verse/PAST-Bench`, arXiv:2608.04003) exposes 26 task families / 204 episodes and matched persistence on/off controls. Hermes+ implements Plan/Render/Route/Gate/Close. Reported MiniMax-M2.7 aggregate persistence gap moves from about +0.13 to +0.15 and mechanism-evidence score from 0.64 to 0.73, while Update reaches about +0.24; however overall run variance is large enough that the aggregate +0.02 shift is not a stable global win. The stronger takeaway is diagnosis and targeted gating rather than the headline average.

**Artifact grounding.** The public repository supplies runnable paired `--compare-no-persistence` experiments, agent/model comparisons, a mechanism-ablation script, structured result outputs, and the Hermes+ source tree.

**Transfer hypothesis.** Test retrieval-before-action and synchronous closeout as independently toggleable mechanisms, and evaluate by capability rather than requiring a globally positive average.

**Scope / uncertainty.** Model/capability interactions are strong; do not treat all five mechanisms as additive or universally beneficial.

**Primary sources.**
- https://github.com/Gen-Verse/PAST-Bench
- https://github.com/Gen-Verse/PAST-Bench/tree/main/agents/hermes-plus
- https://arxiv.org/abs/2608.04003

## Rejected / downgraded leads

- `agentsynth/agentsynth`: interesting CI-gated outcome-verified trajectory packaging, but current search surfaced project claims and validation design without independent quantitative improvement evidence. Keep as tooling lead, not mechanism evidence yet.
- `BetterForAll/self-improving-agents`: illustrative self-improvement loops and machine-checkable rewards, but current evidence is demo/repository-level and lacks sufficiently controlled quantitative comparisons for promotion.
- `SIP_Bench`: useful protocol (`T0/T1/T2`, replay/adapt/heldout/drift, retention/efficiency metrics), but this pass did not yet establish a quantitative result showing a mechanism improves capability; keep as evaluation-infrastructure lead.

## Cross-candidate synthesis

Three independent public-artifact branches converge on a common operational pattern:

1. **Search can improve while being non-monotone** → preserve historical best and decouple exploration from final selection (`RSIBench-Data`).
2. **Experience diversity can improve transfer** → distill skills from heterogeneous model/scaffold trajectories, not a single source (`AFTER`).
3. **Skill effects are context-sensitive and can be severely negative** → use compatibility/admission gates and a vanilla fallback (`EvoAgentBench`).

A compact transferable design is therefore: `diverse experience pool → candidate skill/policy artifacts → held-out context-specific validation → admitted use with vanilla fallback → immutable best-so-far ledger`.

## Nonempty frontier

1. **Highest priority:** inspect EvoAgentBench’s EverOS/skill-evolution runner plus upstream Memento and ReasoningBank implementations to determine why retrieval catastrophically collapses Nanobot/Qwen3.5-27B SWE-Bench (45.8→9.5) while reasoning-strategy memory improves it (45.8→53.0). Extract concrete routing/retrieval differences, negative-transfer safeguards, and reproducible configs.
2. Inspect EvoAgentBench release/issue history and benchmark split/checksum code for leakage/contamination controls and whether leaderboard cells have public per-run variance beyond means.
3. Inspect AFTER paper/repo experiment harness availability or companion artifacts to reproduce the 73.1% multi-model-trace result and identify how trace diversity is sampled/weighted.
4. Inspect RSIBench-Data `update_budget_state.py` and `validate_final_selection.py` to extract exact best-attempt update/selection semantics and whether reliability uses score only or richer failure/cost evidence.
5. Search public repositories for explicit contextual skill-admission mechanisms (learned routers, uncertainty gates, per-domain canaries) with matched quantitative ablations.

## Termination diagnostics / continuation

No completion condition was reached. This checkpoint was written after multiple independent repo branches and after taking an additional unresolved-frontier action (inspection of EvoAgentBench’s tracked leaderboard data following the RSIBench-Data/AFTER findings). The frontier remains nonempty.

**Exact next action:** open EvoAgentBench’s skill-evolution runner / EverOS implementation and the upstream `Agent-on-the-Fly/Memento` and `google-research/reasoning-bank` code paths used for skill retrieval. Compare retrieval unit, routing key, injection placement, and fallback behavior against the two Qwen3.5-27B SWE-Bench cells, then persist a mechanism-level explanation or mark the cause unresolved if the public artifacts are insufficient.
