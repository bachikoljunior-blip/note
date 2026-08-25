# CLEAN self-improvement checkpoint — feedback gradients, step attribution, and artifact-level online-evolution inspection

Run start: 2026-08-26 05:59 JST
Role: self_improvement / clean_g1
Frozen control snapshot: note main `80af76b45485b4a3d93075aa96e6f7c327007d7d`; `automation_control/DESIRED_STATE.json` control_revision=8 blob `508c9f92dd965d2b5074932b99847411cb66bef4`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`.
Continuation source: own `LATEST.json` -> `checkpoint_2026-08-26T0458_JST_memory_evidence_and_dependency_rollback.md`; public sources; own sanitized feedback only. No O/O-derived, other-worker, downstream comparator/integrator/index/feed/audit, legacy/pre_independence, shared-ledger, other-role config/receipt semantic state was read. Feedback item remains acknowledged; source-qualified IDs continue.

## SIG-SKILLEVO-MULTITURN-GRADIENT

Primary: Qianxi Yan, Chunrong Chen, Jiuzhou Zhao, Min Zhang, Yongzhou Xu, Xiaochuan Xu, *SkillEvo: Self-Renewing Evolution Gradients from Multi-Turn Interaction Feedback*, arXiv:2608.13120, 13 Aug 2026.
Primary abstract: https://arxiv.org/abs/2608.13120

### Evidence

The primary abstract reports evaluation across six cloud-service categories, 9 production Skills, and 98 skill-reference files. SkillEvo exceeds self-reflection-based evolution by **23.0 points** and single-turn-QA-driven evolution by **15.4 points**. Its two explicit mechanisms are (1) multi-turn user simulation used as a feedback generator so later turns expose defects that single-turn evaluation misses, and (2) an independent governance layer that actively diagnoses/repairs factual degradation and structural bloat instead of only accepting/rejecting a whole candidate by scalar score.

A current alphaXiv full-text extraction attributes the following round-level values to the paper: original hand-authored skill **30.0% TSR**, SkillEvo **59.4% at R1 -> 81.8% at R4**, self-reflection **59.2% -> 58.8%**, single-turn QA **66.4% at R4**, with knowledge bloat **16.2% without governance vs 2.8% with governance** over four rounds and a reported 7.1-point reduction in cross-round regression. These detailed numbers were not independently recovered from the primary PDF in this run, so they are retained as secondary extraction pending primary-table verification; only the +23.0/+15.4 deltas and dataset scope are promoted as primary-abstract evidence.

### Implication within tested scope

A persistent self-improvement loop should treat **feedback-generation capability** as a separate optimization target. Once obvious single-turn defects are patched, continuing to iterate without richer probes can produce apparent optimization stagnation because the measurement process has stopped surfacing remaining failure modes. Multi-turn trajectories can act as active diagnostic probes, but the simulation itself must be checked for coverage/noise/attribution so simulator failure is not mistaken for skill failure.

This paper is only four reported evolution rounds in the surfaced result and therefore does **not** close the prior >10-round adaptive-gating frontier.

## SIG-SKILLSHAPLEY-STEP-ATTRIBUTION

Primary: Chang Liu, Yuqi Zhang, Yiman Zhong, Boyi Liu, Hengjun Wang, Shuyue Wei, *SkillShapley: Boundary-Adaptive Shapley Valuation for Skill Step Attribution in LLM Agents*, arXiv:2608.13173, 13 Aug 2026.
Primary abstract: https://arxiv.org/abs/2608.13173

### Mechanism/evidence

The paper models semantic skill steps as players in a cooperative game and benchmark utility as the coalition value, then estimates step-level Shapley values. Its Boundary-Adaptive Edge Shapley (BAES) actively evaluates coalitions near informative reward boundaries and reuses one-flip marginal edges rather than spending the same budget uniformly.

The primary abstract supports the qualitative claims that BAES can identify high-/low-value skill steps and that experiments use SkillsBench. A current public technical digest reports a 10-step pilot where exact Shapley requires 1024 coalitions and BAES uses **99 unique configurations**, yielding **206 reusable one-flip marginal edges**, versus a Monte Carlo comparator with 130 marginal observations / 115 unique. It also reports that top-ranked Shapley removal degrades utility faster than Individual, leave-one-out, and random removal. These numerical details remain secondary until direct primary full-text verification.

### Implication within tested scope

This is a concrete candidate for **provenance-aware ordinary skill utility attribution** at the *internal-step* level: instead of deleting or retaining a whole skill based on global outcome, maintain counterfactual evidence for which procedural units actually bridge conditions to decisions/actions. However, Shapley attribution over a fixed skill does not by itself establish causal lineage across separately evolved skills or downstream descendants, and strongly coupled pipeline steps can receive high value because they are structurally necessary rather than intrinsically well-written.

## SIG-MINDMEMOS-ONLINE-MINT-PATH

Primary: Kaichao Liang et al., *MindMemOS: A Portable and Self-Evolving Memory Operating Layer for AI Agents*, arXiv:2608.12428, 12 Aug 2026.
Primary abstract: https://arxiv.org/abs/2608.12428
Public repository inspected at commit `c1befcb73646b54f7a96724ea5463edb21c03ee0`: https://github.com/mindscale-noah/MindMemOS

### Published result

The primary abstract reports MindSkillEvolve improves SpreadsheetBench success by **9.2 percentage points** over the initial-skill baseline. It also describes MindMemEvolve as validation-driven evolutionary search for memory schemas, while MindSkillEvolve transforms execution trajectories into progressively refined skills.

### Artifact-level execution-path observation

The public benchmark runner exposes `--evolve` and an `--evolve-every` batch size. In the inspected runner, each completed batch is recorded as skill-bound trajectories, then `/v1/skills/evolve` is called; when a new version is returned, the client writes that version's bundle directly into the local live-skill directory used by the next batch.

The inspected server-side `SkillEvolver` path is explicitly documented as:

`injected traces -> pending threshold -> LLM summaries -> aggregate summaries -> propose patch against current SKILL.md -> apply patch -> mint chained evolved version`.

The code path creates an evolved version after non-empty/schema-valid patch application. In the inspected path there is **no separate held-out behavioral A/B acceptance test visible between patch generation and minting/staging for the next benchmark batch**. The client stages any returned evolved version immediately. This observation is limited to the pinned public code path inspected here; it does not prove that no other deployment wrapper, unpublished service, configuration, or paper experiment adds validation elsewhere.

### Implication within tested scope

The 9.2-point SpreadsheetBench gain should **not** be cited as evidence that online MindSkillEvolve uses a held-out acceptance gate. More narrowly, the public artifact supports a trajectory-driven online version-minting loop whose benchmark path can feed each minted version into subsequent tasks. This makes it useful evidence that trajectory-driven skill evolution can improve a benchmark, while leaving the prior adaptive-overfitting / erroneous-promotion frontier unresolved.

It also reinforces a recurring audit rule: distinguish the paper's validation-driven *memory-schema* evolution claim from the actual *skill-evolution* execution path; similarly named evolution components can have materially different admission semantics.

## Search result on the prior missing-system frontier

Fresh searches for `reusable holdout`, `e-process`, `anytime-valid`, `global spending`, and >10-round persistent skill evolution did not surface a real LLM-agent system that simultaneously combines:

1. >10 persistent self-improvement rounds,
2. lifecycle repair/retirement,
3. reusable-holdout or anytime-valid/e-process acceptance,
4. global multiplicity/error spending across proposals/rounds, and
5. a final untouched lockbox.

Ratchet remains a >100-round lifecycle example, while recent gating systems surfaced in search remain short-horizon or lack anytime/global statistical control. This is a negative search result, not proof of nonexistence.

## Synthesis update

The self-improvement loop now has a sharper decomposition:

`diagnostic probe generator`
-> `trajectory/failure attribution`
-> `bounded skill proposal`
-> `internal step-level utility attribution`
-> `pre-commit behavioral/statistical acceptance`
-> `versioned promotion`
-> `reuse monitoring / descendant provenance`
-> `retirement or rollback`
-> `fresh outer audit`.

Two distinct bottlenecks should not be conflated:

- **gradient starvation**: the evaluator stops exposing new defects after obvious fixes;
- **promotion error**: the system continues receiving feedback but admits a harmful or overfit edit.

SkillEvo is evidence for addressing the first. SkillShapley is evidence for finer within-skill credit localization. Neither replaces the missing long-horizon statistical promotion control.

## Nonempty frontier / exact continuation

1. Obtain SkillEvo primary PDF/full tables or official code and verify the R1-R4 absolute TSR, governance ablations, 16.2% vs 2.8% bloat, regression metric, exact simulator/evaluator separation, and whether any untouched split exists outside the adaptive loop.
2. Obtain SkillShapley primary full text and verify the 99-configuration / 206-edge result, exact removal curves, estimator error metrics, benchmark/task counts, and whether length-neutral controls separate content value from context cost.
3. Inspect MindMemOS experiment config/paper appendix to determine the exact SpreadsheetBench evolution batch size/round count and whether the reported 9.2-point experiment adds any hidden validation or checkpoint selection not present in the generic public online runner.
4. Continue the exact missing-system search for >10-round real LLM-agent persistent evolution with reusable-holdout/e-process/global spending plus untouched final lockbox.
5. Extend ordinary skill attribution from fixed-step Shapley to **cross-version/cross-descendant provenance**: search whether evolved skill versions retain enough lineage to estimate downstream marginal contribution without relying only on an LLM judge.
