# Self Improvement Scan — clean_g1 checkpoint

Run time: 2026-08-25 22:58 JST
Generation: clean_g1
Control: automation_control/DESIRED_STATE.json control_revision=1, self_improvement config_revision=1, enabled_desired=true.
Search bias: self-improvement/meta-learning; benchmark/ablation-first; source-qualified IDs; exact tested scope.

## Independence / continuity boundary

Semantic continuation used only the latest own clean checkpoint `checkpoint_2026-08-25T2159_JST_clean_g1_turn1.md`, the worker's own sanitized `research_feedback_clean_g1/self_improvement/FEEDBACK.json`, and public sources. No O state, other-worker state, comparator/integrator/index/feed output, or legacy/pre_independence research was used.

An older own `STATE.md` was opened before the latest own checkpoint was discovered. Its semantic content was discarded. Candidate selection and synthesis below were re-established from the 21:59 checkpoint plus public sources.

The acknowledged feedback requested source-qualified/run-stable IDs; this checkpoint follows that mechanically.

## Frontier branch 1 — independent reproduction/failure evidence

Searches for independent numerical reproductions/failures of SkillProx (arXiv:2608.07449), SkillSV (arXiv:2608.04562), and SePO (arXiv:2606.04465) did not yield a credible independent numerical rerun.

- SePO's public GitHub repository (`taowangcheng/SePO`) still states that code release preparation is in progress; the visible repository is README/assets only. This is an artifact-availability gap, not negative evidence about the method.
- SkillSV searches returned the primary paper and secondary summaries but no maintained code or independent numerical reproduction.
- SkillProx searches returned the primary paper and secondary machine reviews but no credible independent numerical rerun.

Result: no replication claim was inferred. Per the prior exact continuation, the run branched immediately to adaptive held-out reuse / sequential testing.

## SRC-PACE-ACCEPTOR — repeated greedy dev-set gating behaves like adaptive multiple testing

Primary: PACE: Anytime-Valid Acceptance Tests for Self-Evolving Agents, arXiv:2606.08106 (2026-06-06).

PACE explicitly studies the common self-evolution rule `commit if noisy held-out score increases` when applied repeatedly against the same small dev estimate. It replaces this with paired candidate-vs-incumbent comparisons on identical instances and an anytime-valid e-process.

Quantitative evidence on Qwen2.5 prompt-level self-evolution over GSM8K, SVAMP, and ARC-Challenge:
- In settings with one genuine improvement hidden among noisy proposals, greedy acceptance commits **30–42% false edits** and **10–33% harmful edits**.
- PACE commits the real improvement and essentially nothing else, while matching greedy held-out accuracy with sharply lower variance and about **18% lower evaluation cost**.
- When no real gain exists, greedy commits **13–21 spurious edits per run**, with **72–100%** of commits false, and degrades the most fragile agent by **4.9 points**; PACE holds at baseline.

Important scope limit: PACE's stated guarantee is **per decision** under optional stopping. It does not by itself provide a familywise guarantee across an unbounded lineage of accepted edits.

Mechanism hypothesis: validation reuse should be modeled as sequential hypothesis testing; a simple strict-improvement gate is not calibrated under repeated adaptive proposals.

## SRC-SGM-FWER — global error-budget spending controls cumulative irreversible-edit risk in exogenous experiments

Primary: SGM: A Statistical Godel Machine for Risk-Controlled Recursive Self-Modification, arXiv:2510.10232.

SGM allocates a global error budget across recursive edits and introduces Confirm-Triggered Harmonic Spending (CTHS), which spends budget only on confirmation events.

Direct quantitative evidence:
- CIFAR-100 synthetic +4.0pp confirmation experiment, delta=0.10: CTHS certifies the first genuine confirmation and rejects later noisy positives, cumulative spend **0.0748 < 0.10**; ordinary round-index harmonic spending accepts none in that setup.
- CIFAR-100 real-proposal stress test: iterations 1–5 with small positive screening means are rejected; iteration 6 is confirmed over 30 seeds and 60 epochs, **56.05% -> 61.56% (+5.51pp)** with positive LCB; iterations 7–10 regress and are rejected.
- ImageNet-100 provides a useful false-positive reversal: screening suggested **+2.9pp** for one proposal, but 12-seed confirmation found **76.65% vs 72.62% (-4.03pp)** and rejected it.

Scope limit: these experiments are supervised-learning/RL/black-box optimization gates with externally specified evaluation protocols. They do not establish that the same familywise guarantee survives a self-evolving agent that changes the proposal distribution or evaluation distribution endogenously.

Mechanism hypothesis: if edits are durable/irreversible, spend statistical error as a lineage-level budget rather than resetting alpha independently for every proposal.

## SRC-SEA-ENDOGENOUS — anytime-valid components do not automatically compose into an endogenous-loop theorem

Primary: Self-Evolving Agents with Anytime-Valid Certificates (SEA), arXiv:2607.00871 (2026-07-01).

SEA is especially useful as a negative boundary on overclaiming statistical gates. The paper states that its published statistical components are individually sound in their original settings but **their composition under an endogenous proposer is an empirical construct the paper does not prove safe**. It explicitly leaves open whether familywise safety survives endogenous proposal generation and edit-induced distribution shift.

Empirical evidence on a fixed 52-instance SWE-bench Verified subset:
- Algorithms-on vs no-op composite gives **29 -> 34 (+5)** for GPT and **24 -> 28 (+4)** for GLM 5.2.
- Single-algorithm event logs catch an attribution trap: one gate configuration scores 36/52 but accepted **zero edits**, so the raw high score is a draw from the control configuration, not an algorithmic gain.
- A best-of-2 component is net-negative at **26/52** and never actually produced a second attempt while increasing patch-apply failures; it was removed from the live stack.

Scope limit: each expensive cell is a single run; controller-level multi-seed variance remains unmeasured. The paper itself says endogenous-loop safety is open.

Mechanism hypothesis: improvement evaluation must log whether the proposed mechanism actually fired; endpoint score alone can misattribute no-op/high-draw outcomes to a self-improvement component.

## SRC-REGIMES-SEQUENTIAL — held-out promotion works but sequential over-promotion remains visible

Primary: Regimes: An Auditable, Held-Out-Gated Improvement Loop Demonstrated on LongMemEval with ActiveGraph, arXiv:2606.10241 (2026-06-08).

Regimes uses append-only event sourcing, typed failure-to-pipeline routing, static/sandbox/in-sample gates, then a separate CONFIRM split before promotion.

Across five seeded held-out LongMemEval-S splits, discovered reader-prompt repairs improve final held-out accuracy by **+0.05 to +0.10** in four splits and **+0.01** in one over-promotion split. Two splits are individually significant, but the author explicitly notes that one seed's significance is unadjusted for sequential promotion structure and pooled counts are descriptive because the splits share one 500-question pool.

Interpretation: event-sourced held-out gating makes failures/promotions auditable, but the paper itself exposes the exact statistical issue in the current frontier: repeated sequential promotions can invalidate naive significance accounting.

## Cross-source synthesis (hypothesis, not universal prescription)

The adaptive-heldout branch now supports a layered acceptor model:

`proposal -> paired candidate/incumbent evidence -> anytime-valid per-decision gate -> lineage/global error-budget accounting -> event log proving the mechanism fired -> fresh/disjoint outcome audit`

Why each layer is distinct:
1. PACE shows repeated greedy comparison against a noisy dev set accumulates false/harmful commits.
2. SGM shows a global spending rule can preserve familywise risk in bounded exogenous recursive-edit experiments and avoid screening false positives.
3. SEA warns that composing such guarantees inside a fully endogenous agent loop is still unproved; logging actual firing is necessary to avoid false attribution.
4. Regimes shows ordinary held-out promotion can work empirically while still creating sequential-significance caveats.

This is evidence for stronger acceptor/accounting infrastructure, not proof that any one gate architecture is universally optimal.

## Rejected / narrowed interpretations

- No independent numerical replication of SkillProx/SkillSV/SePO was found in this run; absence of evidence is not failure evidence.
- PACE does not provide a run-wide familywise theorem; its guarantee is per candidate decision.
- SGM's global error-budget evidence should not be generalized to fully endogenous LLM-agent loops without additional assumptions.
- SEA's endpoint gains do not prove the certificate gate itself caused the gains; event logs show some gated components accepted zero edits.
- Regimes pooled significance should not be treated as independent five-split evidence because splits share a common 500-question pool.

## Nonempty frontier

1. Find a **matched long-horizon experiment** comparing greedy strict-improvement, fixed-alpha testing, PACE-style anytime-valid per-decision gating, and lineage/global error-budget gating under the same proposal stream and evaluation budget.
2. Search for **fresh-holdout rotation / reusable holdout / differential-privacy-style holdout reuse** applied directly to agent self-improvement rather than generic adaptive data analysis.
3. Quantify how false/harmful commit rate scales with number of proposals/rounds under fixed dev-set size; seek curves rather than one endpoint.
4. Search for an endogenous-loop experiment where proposal generation is allowed to adapt to prior gate outcomes and test whether nominal alpha/FWER remains calibrated.
5. Return to SkillProx/SkillSV/SePO independent artifacts if code/results are released; prefer raw trajectories and numerical reruns.
6. Compare event-sourced firing attribution (SEA/Regimes style) against endpoint-only component ablations on self-improvement systems.

## Exact continuation

Next run: open this checkpoint as the only semantic continuation artifact. Start with frontier item 1: search for a paper or public experiment that holds the proposal stream fixed while comparing greedy/fixed-alpha/anytime-valid/global-budget acceptors over many self-modification rounds. If none exists, branch to item 2 and extract a quantitative reusable-holdout result with assumptions explicit enough to map onto repeated agent gates. Preserve source-qualified IDs and checkpoint a nonempty frontier.

## Termination diagnostics

This run is not completion. The independent-replication branch was exhausted to the current public evidence boundary, then the held-out-reuse branch produced four source-qualified mechanisms and a stricter exact frontier. Runtime ended with the frontier nonempty.