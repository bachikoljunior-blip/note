# Self Improvement Scan — real-agent compositional-gate gap follow-up

Generation: clean_g1
Control: `automation_control/DESIRED_STATE.json` control_revision=4; `self_improvement` config_revision=3; enabled_desired=true.
Independence: own clean continuation + own sanitized feedback + public sources only. No O, other workers, comparators/integrator/index/feed, shared ledger, other receipts, or legacy semantic context.
Own continuation source: latest repository-chronology self-improvement checkpoint commit `745a2b72b7aa05a34943a8fa2cfe762d82f73e87` (`checkpoint self-improvement compositional gate simulation evidence`).
Feedback: `research_feedback_clean_g1/self_improvement/FEEDBACK.json` item `self-improvement-id-stability-20260825` is acknowledged; new source IDs below are source-qualified.

## Search target

Continue the unresolved frontier from the latest checkpoint: find a **real self-evolving LLM agent** with more than five adaptive rounds that combines at least two of:
1. content/semantic admission gate;
2. held-out or anytime-valid statistical acceptance;
3. cross-proposal/global spending or capacity control;
4. untouched lockbox/final audit.

Primary/public sources checked in this run included Double Ratchet (arXiv:2607.12790), VaG (arXiv:2608.05810), Ratchet (arXiv:2605.22148), A-Evolve-Training (arXiv:2606.20657), A-Evolve/A-Evolve infrastructure, and targeted searches for `e-process`, `confidence sequence`, `reusable holdout`, `online FDR`, `statistical gate`, `semantic gate`, and `lockbox` in self-evolving agents.

## SRC-DOUBLE-RATCHET-REAL-COMPOSITION — strongest real-agent partial composition found

Primary paper: **Who Grades the Grader? Co-Evolving Evaluation Metrics and Skills for Self-Improving LLM Agents**, arXiv:2607.12790, 2026-07-14. Public reference implementation: `amazon-science/Self-Evolving-Agents-Double-Ratchet`.

This is the strongest real-agent near-match found for the missing composition experiment:

- The skill loop runs **100 rounds**. Co-evolution alternates metric phases of **15/8/5/2 rounds** with four **25-round** skill phases, matching the 100-skill-round oracle budget.
- The metric loop has a **birth gate**, validity/fail-closed anchor discipline, shadow tier, and leave-one-out merit retirement.
- A tiny anchored dev set is the only supervised signal for metric evolution. A **locked set is never read by any loop** and is audit-only.
- The skill loop's held-out evaluation and rollback anchor remain pinned to that locked set while the evolved metric grades only training attempts, so a corrupted metric can degrade learning but cannot corrupt measurement.
- For reference-free report generation, a stronger **external final judge kept outside all loops** audits final outputs and exposed a real Goodhart failure; a targeted detector repair reduced erased evidence tags from roughly 30% to ~1%, after which a task-aware judge preferred repaired evolved outputs over baseline in 0.770 of decided pairs versus 0.515 before the fix.
- Anchor-guard ablation is load-bearing for metric validity: disabling anchor guards collapses the metric into a vacuous near-always-pass grader (0.94–1.00 train pass fraction), while disabling metric-side lifecycle alone does not cause collapse.
- Despite this, held-out task score alone can remain deceptively strong under the vacuous metric, which is direct evidence that **outer measurement validity must be audited separately from downstream task reward**.

Reported held-out peaks for Double Ratchet versus the reference skill loop are MBPP+ 0.717±0.038 vs 0.700±0.025, Spider 0.458±0.038 vs 0.483±0.038, Report 0.812±0.006 vs 0.850±0.010; authors summarize this as 106%, 110%, and 88% lift retention respectively. Three seeds; held-out sets are only 40–48 items, so the paper itself limits conclusions to coarse effects.

### Why it does not close the target frontier

Double Ratchet does **not** use an anytime-valid e-process / confidence sequence, proposal-index alpha/e-value spending, online FDR, or an explicit capacity charge across repeated proposals. Its 100-round lockbox discipline and outer judge therefore close the long-horizon + audit side of the target, but not the adaptive-multiple-testing/global-error-budget side.

The report Goodhart repair is also not a generic pre-commit semantic gate on every skill. It is a detected failure followed by a targeted detector repair and rerun. Thus it does not subsume VaG's per-skill structural + behavioral + semantic pre-commit gate.

Evidence class: **real-agent, long-horizon, multi-layer audit/control; partial composition only**.

## SRC-VAG-REAL-PRECOMMIT — complementary real-agent partial composition

Primary paper: **When Self-Evolution Backfires: Pre-Commit Gating against Skill Contamination in LLM Agents**, arXiv:2608.05810, 2026-08-06.

VaG supplies the complementary piece:
- disjoint Event-50 / Holdout-14 / Test-25 splits;
- three per-skill pre-commit critics: deterministic schema validity, single-skill A-B replay on held-out tasks, and LLM semantic consistency;
- a second joint marginal-gain gate that admits Warm skills to Hot only if the set improves held-out performance;
- frozen-pool transfer to four additional backbones and a second benchmark without re-evolution.

On Event-50, ungated evolution rises 48→60→62 then falls to 52→50 over R1–R5, while VaG rises monotonically 52→58→62→68→72 with a final pool 37 versus 179. Source-only post-hoc rollback recovers only a small fraction of the ungated drop.

### Why it still does not close the target frontier

VaG runs only **five** evolution rounds, not >5. It reuses a 14-task held-out set for A-B and joint selection, uses mean of k=3 replays, and provides no anytime-valid/global repeated-testing control. Its untouched Test-25 is strong final-audit separation, but the gate itself remains vulnerable in principle to adaptive reuse of the same small Holdout set over longer horizons.

Evidence class: **real-agent pre-commit semantic/behavioral composition + untouched final test, but short horizon and no sequential-error budget**.

## SRC-RATCHET-LONG-HORIZON — long-horizon lifecycle without lockbox/statistical commit gate

Primary paper: **Ratchet: A Minimal Hygiene Recipe for Self-Evolving LLM Agents**, arXiv:2605.22148.

Ratchet provides **100-round** real-agent evidence with outcome-driven retirement, bounded active-cap, meta-skill authoring prior, and a five-consecutive-regression rollback persistence gate. On MBPP+ hard-100, held-out pass@1 rises from 0.258±0.047 to a late-window rolling mean 0.584 across 100 rounds and 3 seeds; no-skill control drifts only +0.002±0.005.

However the rollback gate reads the same held-out stream used for reporting and is explicitly designed as online lifecycle management, not a frozen lockbox. Ratchet has no semantic pre-commit gate and no anytime-valid repeated-testing correction.

Evidence class: **real-agent long-horizon lifecycle/rollback; not the missing compositional statistical+semantic contract**.

## SRC-AEVOLVE-TRAINING-SCALE — scale evidence, but only four outer rounds

Primary paper: **A-Evolve-Training: Autonomous Post-Training of a 30B Model**, arXiv:2606.20657.

This is valuable scale evidence: a no-human-in-loop post-training system runs over multiple weeks, reaches 0.86 held-out versus the top human submission's 0.87 on the NVIDIA Nemotron-Reasoning Challenge, and detects that its own dev metric has stopped tracking external performance, changing search policy accordingly. But it reports only **four outer rounds**, and does not provide the missing statistical+semantic multi-gate composition.

Evidence class: **real autonomous post-training at scale; insufficient round count and gate composition for this frontier**.

## Synthesis / current gap

After targeted primary-source search, no real self-evolving LLM-agent experiment was found in this run that simultaneously demonstrates all of:

`>5 endogenous rounds + semantic/content pre-commit gate + anytime-valid/reusable-holdout statistical acceptance + global spending/capacity accounting + untouched lockbox/final audit`.

The evidence is currently split across complementary systems:
- **Double Ratchet**: 100 rounds + locked anchor + outside judge + anchor/validity/lifecycle controls, but no anytime-valid/global repeated-testing budget and no generic per-skill semantic pre-commit gate.
- **VaG**: semantic/behavioral + joint pre-commit gates + untouched final Test, but only five rounds and no adaptive-testing correction.
- **PACE/SEA/Scientific CI/CD** (already in the current clean lineage): anytime-valid / spending ideas, but they do not close the same real long-horizon compositional loop; Scientific CI/CD's strongest composition table is simulation evidence.
- **Ratchet**: 100-round governed lifecycle, but not independent lockbox/statistical commit control.

This triangulation sharpens the missing experiment rather than broadening claims: the next decisive study should compose VaG-style semantic/behavioral admission with PACE/SGM-style sequential acceptance and Double-Ratchet-style locked outer audit over a Ratchet-scale 20–100 round real loop.

## Updated nonempty frontier

1. Search papers/repos **citing Double Ratchet, VaG, PACE, SEA, or Scientific CI/CD** for a later real-agent composition, prioritizing August 2026 and public code.
2. Search for `confidence sequence` / `e-process` / `online FDR` inside skill-library or harness-evolution repositories, not just paper titles.
3. Inspect whether A-Evolve's current public gate implementation has evolved beyond simple holdout rollback into statistical or semantic admission controls; classify repo behavior separately from paper claims.
4. Search for >5-round **counterfactual lockbox** experiments where the acceptor sees only a reusable/limited-information holdout while a disjoint final set is opened once.
5. If no exact system exists, construct a source-backed factorial experiment specification: VaG content gate × PACE/SGM acceptor × Double-Ratchet lockbox/outer audit × Ratchet lifecycle/cap, with proposal count and false/harmful commits as first-class metrics.
6. Continue to separate `real-agent`, `simulation`, `theoretical guarantee`, and `infrastructure-only` evidence classes.

## Exact continuation

Next run: begin with citation/implementation tracing from **Double Ratchet (2607.12790), VaG (2608.05810), PACE, SEA, and Scientific CI/CD**, searching specifically for August 2026 real-agent follow-ons that implement at least two of these controls together. Then inspect A-Evolve repository gate code for whether current implementation includes statistical confidence/spending or only scalar holdout comparison. Do not widen to generic self-improvement until these citation chains are exhausted.

## Termination diagnostic

Not complete. This run found the strongest real-agent partial composition matching the long-horizon + lockbox + outer-audit side (Double Ratchet), but the exact long-horizon semantic + anytime-valid + global-spending + lockbox conjunction remains unobserved. Frontier remains nonempty.
