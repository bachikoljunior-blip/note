# Long Horizon clean_g1 — PACE nonzero anytime gate and run-level boundary

Observed invocation start: `2026-08-27T15:03:15+09:00`.
Semantic-freeze control tuple: note main `a957e5211f2f9c16ea5ac955b89c3a3fa86c06b0`, root control revision `11`, role config revision `5`, root blob `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`, role config blob `268523da20c78ce3091344c492ad3d51f6f9e667`. Repeated pre-semantic SHA-only ref lookup matched. Later main movement was used only for write safety and was not adopted semantically.

## New primary-source evidence

### PACE gives a clean nonzero anytime-valid acceptance example
Primary source: Zayx Shawn, **PACE: Anytime-Valid Acceptance Tests for Self-Evolving Agents**, arXiv:2606.08106v1, submitted 2026-06-06. https://arxiv.org/abs/2606.08106

PACE isolates the **acceptor** in an open-ended self-evolution loop. Each candidate prompt is evaluated against the incumbent on the same examples; ties are discarded; discordant outcomes update a testing-by-betting e-process. A candidate commits as soon as the e-process crosses `1/alpha`. The paper uses `alpha=0.05`, `lambda=0.5`. Its theorem is explicitly **per candidate under optional stopping**, not a run-level familywise guarantee.

The controlled regime is the useful missing case for this frontier: the proposer has one known genuinely beneficial edit hidden among noisy edits. On Qwen2.5-1.5B and 3B, across 5 seeds, PACE commits exactly `1.0` change per run, with `0%` audit-labelled false and `0%` harmful commits, while preserving the genuine gain. Greedy commits `3.4±1.2` / `3.0±2.6` changes, with `42% / 30%` false and `33% / 10%` harmful commits. At 1.5B, PACE and greedy both reach about `+0.57` held-out gain; at 3B PACE reaches `+0.74±0.04` versus greedy `+0.54±0.30`. PACE also uses about `18%` fewer dev evaluations in the reported 1.5B example (`1712` vs `2080` paired problems) because it stops early.

A milder-handicap run gives a useful power boundary: with a smaller true gain of about `+0.18`, PACE captures `+0.14` at `0%` false while greedy captures `+0.18` but with `17%` false and `17%` harmful commits. This is direct evidence that anytime-valid gating can preserve **nonzero accepted improvements**, but it may trade recall for false-commit control when gains are marginal.

The stochastic no-real-gain regime confirms the complementary failure mode: greedy commits roughly `13.3–20.7` changes/run with `72–100%` audit-labelled false commits, while statistical gates commit fewer than one change/run and largely hold baseline quality.

## Scope and negative evidence

- This closes the statistical sub-frontier **“can an anytime-valid gate admit a real nonzero improvement instead of only blocking?”** for prompt-level self-evolution.
- It does **not** close the requested software/API-agent frontier. The experiment is prompt evolution on GSM8K/SVAMP/ARC-Challenge with frozen Qwen2.5 models, not a stateful software/tool agent with side effects.
- The guarantee is **per candidate**, not run-level familywise control. The paper explicitly treats loop-level adaptivity empirically. A long-lived persistent controller still needs a global risk-spending / verifier-lifecycle story if repeated accepted edits are to be certified jointly.
- The fresh audit pool is used for measurement only. Repeated reuse/exposure of the operational dev/evaluator signal across very long deployments remains a separate contamination/freshness problem.
- The paper argues interface generality to skills/code/workflows because the gate consumes paired outcomes, but system-level generality is explicitly argued rather than demonstrated.

## Related skill-reliability continuation

Fresh public review of arXiv:2608.22610 (`Coalition-Aware Skill Reliability for Self-Evolving Agents`, submitted 2026-08-23) re-confirms that coalition-conditioned skill value and outcome-only admission are structurally different. The current public HTML specifies CASS sampling coalition sizes uniformly from `{1,...,k}` and a bounded number `N` of coalitions, but the numeric `k` and the u-SMCO masking threshold remain unresolved from the accessible primary text in this invocation. Do not fabricate them.

## Revised synthesis

A long-lived self-modification controller should distinguish at least:
1. **candidate-local evidence**: paired sequential gate with explicit power/cost trade-off;
2. **run-level risk accounting**: cumulative error spending across repeated candidate decisions;
3. **verifier freshness/exposure**: whether the evidence source remains valid after repeated adaptive reuse;
4. **post-acceptance surveillance**: delayed harms not visible at admission time;
5. **capacity accounting**: improvements caused by extra tools/retrieval/attempts/memory/evaluator authority must not be credited as skill quality;
6. **maintenance/revocation**: accepted artifacts can later become stale, harmful, or coalition-negative.

PACE supplies unusually clean evidence for layer 1 with a real accepted gain. It does not establish layers 2–6.

## Exact continuation

1. Find a **stateful software/API-agent** experiment using anytime-valid or sequential commit gating with nonzero accepted edits and matched incumbent/candidate executions.
2. Find run-level/global-risk procedures for open-ended self-modification that preserve power after many accepted/rejected candidates, ideally with actual agent experiments rather than only theorem-level proposals.
3. Search persistent memory/skill systems that directly measure verifier exposure, holdout retirement/refresh, and longitudinal leakage from repeated acceptance feedback.
4. Search maintenance controllers charging explicit capacity deltas: tool count, retrieval width, attempt budget, memory budget, evaluator authority.
5. Search common-replicate four-cell `admission gate ON/OFF × post-admission maintenance ON/OFF` evidence with matched candidate stream/model/compute.
6. Recover numeric CASS coalition cap `k` and u-SMCO threshold `tau` only from official supplement/code if it appears.
7. Continue hidden semantic-lineage repair, post-consolidation re-externalization, rollback-target selector, and decision-influence audit frontiers.
8. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
