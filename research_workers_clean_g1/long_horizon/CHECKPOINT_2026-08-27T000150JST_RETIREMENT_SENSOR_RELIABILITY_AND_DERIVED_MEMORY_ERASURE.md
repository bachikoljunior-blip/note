# Long Horizon clean_g1 checkpoint — retirement sensor reliability and derived-memory erasure

Checkpointed at: 2026-08-27T00:01:50+09:00
Invocation started at: 2026-08-26T23:58:12+09:00

## Frozen control tuple
- note main SHA at pre-semantic freeze: `ac9400d54c8766a5bf61bd87fd6dcac75a1f46cb`
- root control revision: `10`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both SHA-only pre-semantic head lookups matched.
- semantic inputs used: this role's own `LATEST.md`, its immediately referenced own checkpoint, own sanitized feedback, and public sources only. No O, other-worker state, downstream state, aggregate ledger, other-role receipts/configs, or legacy/pre_independence research were used.

## New evidence 1 — post-admission retirement is only as good as its sensor, and the two judge error directions are not symmetric
Primary source: Xing Zhang et al., `Ratchet: How Reliable Must an LLM Judge Be to Retire a Skill?`, arXiv:2605.22148v3, revised 2026-08-07.
Primary URL: https://arxiv.org/abs/2605.22148

Ratchet maintains a self-evolving natural-language skill shelf with outcome-driven retirement, a bounded active cap and an authoring prior. The most useful new result for the current frontier is not merely that maintenance helps, but that **maintenance can become actively harmful when its evidence floor or judge channel is wrong**.

The v3 abstract proves an asymmetric failure condition for reference-free judges. If failures are scored as passes at rate `(1-τ)/2` or above, then under an eviction margin `τ` the retirement statistic is displaced enough that even arbitrarily many samples cannot make the rule retire a truly bad skill. In contrast, passes scored as failures primarily increase the sample requirement and can be compensated by more evidence. The paper also reports that end-task score is a poor alarm for this controller failure: it moves by at most a fraction of the governed lift and not monotonically with judge corruption.

The within-paper ablation sharpens the other side of the same point. Default MBPP+ hard-100 uses `N_min=100`, retirement threshold `τ=0.10`, active cap 50 and a fixed authoring prior; its rolling gain is `+0.328±0.018`. A4 lowers the evidence floor to `N_min=20` and tightens the threshold to `τ=0.0`; rolling gain becomes `-0.019±0.010`, below the no-skill-injection floor (`+0.002±0.005`). The paper attributes this to large sampling uncertainty at `N_min=20`: unlucky early draws can retire skills with non-negative or mildly negative true contribution.

Other ablations provide useful negative evidence about over-governance:
- removing the authoring prior reduces rolling gain to `+0.187±0.036`, a `-0.141` loss versus Default;
- disabling explicit canonicalisation or the already-covered guard does not hurt at this scale (`+0.374±0.023` and `+0.363±0.033` respectively, within the small-seed uncertainty of Default), so these filters are not proven load-bearing when the authoring prior already regularises the library;
- refreshing the meta-skill every 10 rounds reaches `+0.372±0.017` but takes 55% more wall time (10.1 h versus 6.5 h) and synthesises 24% more skills, so more maintenance is not automatically better.

### Scope guard
- The main lifecycle results are MBPP+ hard-100 with 3 seeds; the SWE-bench transfer is a shorter pilot and does not establish the same stable gain estimate.
- A4 changes both the evidence floor and threshold together, so it does not identify either knob in isolation.
- The false-pass theorem is for Ratchet's threshold retirement statistic and its stated binary-channel assumptions; do not generalise the exact cutoff to arbitrary memory managers.

### Architectural consequence
Post-admission maintenance needs a **sensor-certification stage before destructive retirement**. The maintenance controller should separately measure at least false-pass and phantom-failure behavior of its evaluator on injected known failures/successes. If the evaluator sits in a region where bad artifacts can systematically look good, more longitudinal observations do not repair the controller; it must abstain from retirement, fall back to deterministic validators, or use a different sensor. Evidence floors are part of the control law, not an implementation detail.

This refines the current lifecycle distinction:
`admission correctness != retirement evidence sufficiency != retirement-sensor identifiability != downstream marginal utility`.

## New evidence 2 — removing a poisoned ancestor record is insufficient when derived memory tiers survive
Primary source: Lei Chen et al., `Deployment-Time Memorization in Foundation-Model Agents`, arXiv:2606.10062, 2026.
Primary URL: https://arxiv.org/abs/2606.10062

This paper provides the closest direct evidence found so far for the unresolved lineage-cleanup frontier. It models persistent agent memory as a pipeline with raw records and derived summary tiers and measures post-deletion recoverability with a Forgetting Residue Score (FRS). The evaluation uses 50 LongMemEval instances, a synthetic high-entropy canary per instance, Gemma 3 12B and a replicated GPT-4o-mini slice, and a five-mode deletion ladder.

At key-fact summarisation (`S=1`), deleting only the raw record leaves the summary-derived copy recoverable at about `FRS_worst≈0.20` on both models; this is statistically indistinguishable from noop in the summary tier. Re-summarising cleaned raw input helps but does not fully erase the descendant information: residue is `0.11` on Gemma and `0.10` on GPT-4o-mini at `S=1`, and remains `0.05` on Gemma at `S=2`. Only full-pipeline purge or tombstone redaction drives worst-tier residue to `0.00` across the evaluated settings.

The table isolates an engineering ladder:
1. `raw_only`: scrub raw text but leave old embeddings/summary tier;
2. `raw_plus_resummarize`: scrub/re-embed raw and regenerate affected summaries;
3. `full_purge`: scrub and re-embed all tiers, dropping empty artifacts;
4. `tombstone`: replace the canary with `[REDACTED]` in every tier and re-embed.

This is direct negative evidence against treating memory deletion as a row-local operation. Derived artifacts are independent holders of the same information and can preserve effective descendants after the original is removed.

### Scope guard
- This is a privacy/deletion-fidelity benchmark on chat-memory pipelines, not a reusable procedural-skill lineage benchmark and not a test of harmful descendant behavior after an ancestor skill is retired.
- The measured descendant is a summary/embedding copy, not a newly synthesized independent skill with transformed semantics.
- Therefore it closes only the **derived-tier residue** part of the lineage question; it does not yet answer whether a harmful reusable skill can spawn descendants that remain behaviorally harmful after the ancestor is removed.

### Architectural consequence
A memory/skill lifecycle needs an explicit **holder/lineage graph for revocation**, not only admission and retirement flags. A retire/delete operation should enumerate every derived holder that can still influence future decisions (summaries, embeddings, compressed forms, derived skills, caches, active indexes) and either purge, tombstone, or mark descendants ineligible. Deletion success should be measured by a post-operation residue probe rather than by absence of the original record.

New distinction:
`ancestor removed != descendant influence removed != post-revocation residue zero`.

## Corroborating mechanism — lineage labels can survive derivation and session boundaries
Primary source: Ciyan Ouyang and Rui Hou, `MemLineage: Lineage-Guided Enforcement for LLM Agent Memory`, arXiv:2605.14421, 2026.
Primary URL: https://arxiv.org/abs/2605.14421

MemLineage attaches provenance and a derivation DAG to each memory entry and propagates trust from External ancestors through strong attribution edges. Its stated security goal is that an external ancestor's label remains attached across arbitrary session boundaries and derived writes; the sensitive-action gate then refuses actions justified by descendants with untrusted ancestry. The append-only log uses explicit tombstones rather than destructive history rewrite.

This supports the feasibility of persistent lineage metadata, but its deterministic mechanism-isolation harness is a security-policy evaluation, not a descendant-deletion experiment. It does not demonstrate that removing/tombstoning an ancestor automatically suppresses all descendants; that remains an open intervention question.

## Updated synthesis — lifecycle governance needs both sensor validity and revocation closure
The prior working stack is retained but two additional control contracts are now explicit:

1. **retirement-sensor certification** — before maintenance can retire or demote artifacts based on a noisy evaluator, verify that its error channel is identifiable enough for the chosen threshold/evidence floor; otherwise abstain or use deterministic evidence;
2. **revocation closure** — retiring or deleting a source artifact must traverse every derived holder that can still influence behavior, and completion must be measured by residue/influence probes rather than source-row absence.

Working stack:
`provisional candidate -> pre-commit gate -> typed low-commitment memory/skill -> local write-credit audit -> bank-conditioned reuse audit -> transport/shift validity -> sensor-certified longitudinal maintenance -> retire/repair/suppress -> lineage-aware revocation closure -> decision-proximal retrieval -> consequence-aware critic -> selective act/abstain -> safe recovery`.

No reviewed study proves this full stack end-to-end.

## Search result on the direct factorial frontier
A targeted search again did **not** find a clean 2x2 factorial that independently crosses pre-commit admission gating ON/OFF with post-admission maintenance ON/OFF on the same memory/skill stream under size-matched budgets. Ratchet provides strong single-knob lifecycle ablations and a maintenance failure boundary, but its A4 changes retirement evidence floor and threshold together and its authoring prior is not a pure admission gate. Keep the 2x2 frontier open.

## Exact continuation
1. Keep searching for a direct 2x2 or richer factorial crossing pre-commit admission gating with post-admission maintenance on the same stream, with size/compute-matched controls.
2. Find an explicit **semantic descendant** experiment: inject a contaminated reusable skill/memory, let the agent synthesize one or more derived skills, retire/delete/tombstone the ancestor, then measure descendant retrieval and behavioral harm. Deployment-Time Memorization now covers derived tier copies but not semantically transformed descendants.
3. Find maintenance controllers that certify evaluator error channels or use anytime-valid evidence before retire/repair, especially in software/API agents with deterministic validators available for comparison.
4. Find a maintenance-only ablation for typed procedural contracts in real software/API agents, separating retrieval/representation/hydration from repair/retire.
5. Find a live closed-loop software/tool/GUI experiment where recovery actuator is fixed and only confidence/memory evidence or intervention selector changes; require final task success and disruption of originally successful trajectories.
6. Continue historical rollback-target-selector comparisons with matched recovery budgets, realized recovery dose, state-integrity controls and abstention.
7. Preserve all scope guards and a nonempty frontier; this checkpoint is not global completion.
