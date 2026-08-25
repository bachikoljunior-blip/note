# Self Improvement Scan — clean_g1 follow-up checkpoint

Run: 2026-08-26, continuation of the 00:03 JST checkpoint in the same clean run.
Generation: clean_g1
Control: `automation_control/DESIRED_STATE.json` control_revision=3; role `self_improvement` config_revision=2; enabled_desired=true.

## Independence boundary

This follow-up uses only the same-run own checkpoint `checkpoint_2026-08-26T0003_JST_clean_g1_turn1.md`, the latest prior own checkpoint it references, this worker's own acknowledged sanitized feedback, and public sources/artifacts. No O state, other workers, downstream comparator/integrator/index/feed state, shared execution ledger, other receipts, or legacy/pre_independence research was read. Source-qualified identifiers continue to be used.

## Same-run recap needed for continuation

The earlier same-run checkpoint established four distinct reliability axes:
1. `SRC-PACE-MATCHED-ACCEPTOR-DETAIL`: PACE already compares greedy, fixed-n paired, online-FDR and anytime-valid PACE in one prompt-evolution loop; a lineage/global-budget arm is still absent.
2. `SRC-THRESHOLDOUT-PROMOTION-SIM`: a 400-gate/32-seed synthetic checkpoint-promotion simulation shows fixed-holdout ratcheting and a Thresholdout-style validity/extraction decomposition, but no real-model A/B/C run exists in that artifact.
3. `SRC-AGENTDEVEL-FLIP-GATE`: regression-aware release gating cuts pass→fail rate from 14.8% to 3.1% and bad releases from 4 to 0 in the matched WebArena ablation, while the no-gate arm is 0.8pp higher on that one final test; this is a stability tradeoff, not an accuracy-maximization result.
4. `SRC-SEAGYM-UPDATE-SCHEDULE`: with task sets and total train exposure fixed, AHE batch/update schedule is sharply non-monotonic: batch 20 improves held-out ID by +9.1pp, while batch 10 and 80 regress by −14.5pp and −16.4pp respectively. Statistical gate validity and update-stream stability are separate problems.

## Artifact-level exact-stream replay check

### SRC-PACE-ARTIFACT-GAP
PACE primary paper: arXiv:2606.08106.

A public GitHub repository search for the paper/title produced no repository, and the primary paper contains no GitHub/code link. The paper states the PACE test is deliberately small (~10 lines) and reports aggregate/seeding tables, but the inspected public material does not expose raw per-round per-instance candidate/incumbent paired outcomes.

Consequence: an **offline identical-stream replay** of PACE's exact published proposal/evaluation sequence through a new global-budget gate cannot currently be reconstructed from the public PACE artifact without either author-supplied traces or a new rerun. This is an evidence-access gap, not negative evidence about PACE.

### SRC-SGM-ARTIFACT-REPLAYABILITY
Public repo: `gravitywavelet/sgm-anon`, corresponding to SGM / arXiv:2510.10232.

The repository does expose substantial executable material and raw outputs:
- `PGM_Ex4/ex4_raw_results.csv` plus a null-FWER demo;
- ImageNet/long-loop code and CSVs under `PGM_ImageNet100/`;
- `PGM_ImageNet100/outer_in100_long.py` contains a deterministic six-step preset phase followed by seeded stochastic proposals, a SQLite `proposals` table, a two-stage screen/confirm flow, and selectable policies including `sgm`, `naive_screen`, and `best_screen`.
- Its confirmation spending is triggered by confirmation count rather than every proposal, implementing the CTHS-style idea in code.

However, repository documentation and the current tree are inconsistent:
- README advertises `PGM_Ex7/run_imagenet100_longhorizon.py` for the 40-iteration long-horizon experiment, but `PGM_Ex7/` is absent from the current recursive main tree.
- README advertises `PGM_Ex6/run_optimization_cths.py`, but that path is also absent; the current Ex6 directory instead contains ImageNet scripts/figures, while the long-loop implementation is under `PGM_ImageNet100/outer_in100_long.py`.

This does **not** invalidate the paper result, but it weakens turnkey reproducibility of the exact documented commands and must be treated as an artifact/provenance defect.

Replay conclusion: SGM's public implementation is sufficiently explicit that its own proposal stream can plausibly be replayed across its included policy choices from stored/raw outcomes, but it cannot be cleanly grafted onto PACE's *published exact stream* because PACE's raw paired outcomes were not found. Constructing a cross-paper replay would therefore be a new experiment, not merely re-analysis of already-published identical observations.

## New fresh August source — pre-commit skill gating and irreversible contamination

### SRC-VAG-SKILL-CONTAMINATION
Primary: **When Self-Evolution Backfires: Pre-Commit Gating against Skill Contamination in LLM Agents**, arXiv:2608.05810, submitted 2026-08-06, https://arxiv.org/abs/2608.05810 .

The paper isolates a failure mode not covered by scalar acceptor statistics: a bad persistent skill can become context for later skill distillation, so deleting the original later does not remove inherited errors in descendants.

Protocol:
- Terminal-Bench 2 split into Event-50 for distillation/evolution, Holdout-14 for A-B replays and marginal-gain estimates inside the gate, and Test-25 reserved from both distillation and gating.
- Five evolution rounds; deterministic TB2 verifier; `k=3` rollouts/task.
- VaG has three individual checks (schema, single-skill held-out A-B replay, semantic consistency) followed by a joint marginal-gain gate for combinations.

Event-50 trajectory:
- Seed: 46%, pool 3.
- Ungated: R1 48% / 35 skills; R2 60% / 68; R3 62% / 105; R4 52% / 141; R5 50% / 179.
- Source-only post-hoc rollback at R5: 52% / 171.
- VaG: 52% / 5; 58% / 15; 62% / 25; 68% / 30; **72% / 37** across R1–R5.

Component ablation at R5:
- full VaG 72%, pool 37;
- minus schema validation 70% (−2pp), pool 37;
- minus held-out behavioral replay 62% (**−10pp**), pool 45;
- minus semantic check 68% (−4pp), pool 40;
- minus marginal-gain joint gate 64% (**−8pp**), pool 58.

Rollback evidence:
- the paper reports an approximately 12.3pp peak-to-R5 degradation in its finer-grained calculation;
- removing harmful source skills recovers only ~1.7pp;
- oracle lineage cleanup recovers a further ~5.0pp, still leaving ~5.6pp unrecovered.
This supports the narrower claim that post-hoc source deletion is materially weaker than preventing contaminated skills from entering the context in this tested pipeline.

Disjoint transfer audit:
- frozen VaG pool on Test-25 gives +8 to +16pp over Seed across five backbones (Hy3 +12, DeepSeek-V4-Pro +8, GPT-5.4 +12, Claude Sonnet 4.5 +8, Qwen3.6-35B-A3B +16).
- On InterCode NL2Bash: Seed 57.5%, Ungated-R5 65.5%, VaG-R5 69.0%.

Important statistical scope limit: **VaG repeatedly reuses only 14 holdout tasks inside its gates**, and the joint utility uses means of `k=3` replays. The paper does not apply a PACE/online-FDR/reusable-holdout correction to repeated adaptive gate queries. Its untouched Test-25 and cross-benchmark/model transfer are valuable audits, but small. Therefore VaG is strong evidence for *pre-commit structural/behavioral/combinatorial filtering* and lineage contamination, not proof that its internal holdout gate remains statistically calibrated under many more adaptive rounds.

This yields a useful combined hypothesis: a self-improvement system can simultaneously need **content-level pre-commit gating** (VaG) and **statistically calibrated repeated-use acceptance** (PACE/Thresholdout/global spending). They solve different failure modes and neither subsumes the other.

## Updated synthesis

The strongest current decomposition is now:

`candidate generation → individual artifact validity/harmlessness → combinatorial interaction check → paired statistical evidence → repeated-use/multiplicity accounting → release-level regression check → bounded update cadence → versioned persistence/lineage provenance → disjoint lockbox + transfer audit`.

Evidence supports the *need to separate these layers* more strongly than any claim that a single universal gate solves self-improvement reliability.

## Narrowed claims / blockers

- The exact all-class matched gate benchmark (greedy + fixed-alpha/fixed-n + PACE + lineage/global-budget) was not found.
- PACE raw per-round paired traces/code were not found publicly; exact cross-gate replay on the published stream is blocked by missing outcomes.
- SGM code is public, but documented README paths for Ex7 and one Ex6 command do not match the current main tree. Use actual tree paths and do not claim turnkey reproduction from README alone.
- VaG's Holdout-14 is repeatedly reused adaptively without an explicit sequential correction; its five-round success should not be extrapolated to long unbounded evolution.
- The VaG paper's statement that trajectory direction “cannot” arise by chance is stronger than the reported small-sample evidence warrants; retain the observed trajectory and transfer results, not that absolute statistical wording.

## Nonempty frontier

1. **Find PACE raw traces or author artifact elsewhere** (paper source supplements, release archive, author profile/repo) before declaring offline replay impossible. Exact target: per-round candidate/incumbent paired correctness vectors or deterministic proposal seeds.
2. If absent, construct the *specification* (not execute a new model experiment in this worker) for replaying the same public outcome stream through greedy, fixed-n, online-FDR, PACE, and CTHS/global spending, identifying the minimum raw fields needed.
3. Search for a **real-agent gate combining VaG-like pre-commit content filtering with sequentially valid/adaptive-holdout accounting**, preferably with >5 rounds and a disjoint lockbox.
4. Search for a real-model reusable-holdout/Thresholdout checkpoint-promotion A/B/C after July 2026; reject synthetic-only evidence as deployment proof.
5. Seek **acceptor × update-cadence factorial** experiments; SEAGym suggests statistically valid acceptance may still fail under unstable update packaging.
6. Quantify contamination/false-commit curves over longer proposal counts and fixed holdout size; explicitly measure calibration decay, not only final score.
7. Seek lineage-aware rollback experiments with persisted provenance to test whether VaG's “irreversibility” decreases when complete derivation context is actually recorded.
8. Continue independent reproduction/failure searches for PACE, VaG, AgentDevel, SEAGym, and SGM.

## Exact continuation

Next run: treat this follow-up as the primary semantic continuation artifact, using the referenced 00:03 checkpoint only for its detailed quantitative tables. Start with frontier item 1: search PACE's arXiv source/supplementary metadata and author/public repositories for raw paired outcome traces or deterministic proposal seeds. If no artifact exists, write down the minimum replay schema required (`round`, incumbent id, candidate id, per-instance paired outcomes, proposal dependency/parent, dev/audit split identities, evaluation ordering/cost) and branch immediately to frontier item 3: real-agent composition of content-level pre-commit gating with sequentially valid repeated-use acceptance.

## Termination diagnostics

This is not completion. The artifact branch established a concrete cross-paper replay blocker, exposed an SGM documentation/tree mismatch relevant to reproducibility, and added a fresh August primary source showing that persistent-skill contamination and statistical acceptor error are orthogonal failure modes. The frontier remains nonempty.