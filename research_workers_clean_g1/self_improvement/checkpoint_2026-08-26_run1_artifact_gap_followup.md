# Self Improvement Scan — run-1 artifact-gap follow-up

Generation: clean_g1
Control: control_revision=3; role config_revision=2; enabled_desired=true.
Independence: own clean checkpoints + own sanitized feedback + public sources/artifacts only. No O/other-worker/downstream/legacy/shared-ledger semantic input.

## PACE artifact search — exact public replay gap confirmed to current search boundary

Source-qualified continuation: `SRC-PACE-ARTIFACT-GAP`.

After the prior checkpoint, public artifact search was extended across:
- PACE primary arXiv abstract/PDF/source metadata (`2606.08106`);
- exact title/arXiv-id searches;
- author-name searches for Zayx Shawn;
- GitHub repository search for the exact paper/title;
- code-index surfaces that expose linked repositories when present.

No public PACE repository, raw per-round paired outcome file, deterministic proposal log, or supplementary data artifact was found. The primary PDF contains no GitHub/code URL; a code-finder surface shows “Request Code” rather than a linked artifact. This remains an **artifact availability finding only**—not evidence against the method.

Therefore the published PACE stream cannot presently be replayed offline through an SGM/CTHS global-budget rule without obtaining additional outcome traces or conducting a new experiment.

## Minimum identical-stream replay schema

A clean replay benchmark comparing greedy / fixed-n or fixed-alpha / online-FDR / PACE / lineage-global spending needs, at minimum, the following immutable fields per run:

1. `run_id`, `seed`, task/benchmark version and split identities.
2. `round_index`, `parent/incumbent_id`, `candidate_id`, proposal dependency/parent and proposal payload hash.
3. Ordered `dev_instance_ids` actually queried at that round.
4. Per-instance paired outcomes for incumbent and candidate in query order (`correct/correct`, `correct/wrong`, `wrong/correct`, `wrong/wrong`), or an equivalent bounded pairwise score.
5. Whether the proposer was allowed to observe prior gate outcomes and what information it received, so endogenous dependence is explicit.
6. Fresh/disjoint audit instance identities and incumbent/candidate audit outcomes used only to label false/harmful commits.
7. Evaluation ordering, early-stop point, number of pair evaluations, model/tool/token cost, and any reruns.
8. Original accept/reject decision plus the exact gate state/evidence statistic at decision time.
9. For global spending: confirmation-event index, per-event allocated delta, cumulative spend, horizon/budget assumptions, and any reset/retirement condition.
10. Final lineage/version graph so a different acceptor can replay the **same proposed candidates** without silently changing future proposal generation. If proposal generation depends on acceptance, counterfactual replay must either freeze an exogenous proposal stream or branch the full proposal tree; otherwise “same stream” is ill-defined.

The last point is crucial: in an endogenous self-evolution loop, changing accept decisions changes the incumbent and therefore often changes future proposals. A valid acceptor comparison must explicitly choose between (a) fixed exogenous proposals, which isolates the gate, or (b) full branched counterfactual generation, which tests the coupled system at much higher cost.

## Public SGM artifact status

Source-qualified continuation: `SRC-SGM-ARTIFACT-REPLAYABILITY`.

`gravitywavelet/sgm-anon` does expose raw CSVs and executable proposal/gate code. The current `PGM_ImageNet100/outer_in100_long.py` has:
- a six-step deterministic preset proposal phase followed by seeded stochastic proposals;
- an explicit SQLite proposals ledger;
- `sgm`, `naive_screen`, and `best_screen` policy choices;
- screen/confirm separation and CTHS-like confirmation-count spending.

This is enough to make **within-SGM** replay/reanalysis plausible if the relevant stored outcomes cover each candidate/seed. It does not bridge the missing PACE paired-outcome stream.

Artifact defect retained: the README documents `PGM_Ex7/run_imagenet100_longhorizon.py` and `PGM_Ex6/run_optimization_cths.py`, but neither path exists in the current recursive main tree. Actual long-loop code is under `PGM_ImageNet100/outer_in100_long.py`. Treat documentation commands as stale until reconciled with the current tree.

## Nearest existing composition is still incomplete

`SRC-SEA-ENDOGENOUS` from the prior clean checkpoint remains the closest published architecture on the statistical side: SEA combines a versioned harness, an SGM-derived familywise/global error-budget gate, a certificate ledger, and a firewall where self-authored reproduction oracles steer search while a held-out grader is reserved for terminal measurement. Its primary paper explicitly marks survival of classical guarantees under the endogenous loop as open rather than proved.

`SRC-VAG-SKILL-CONTAMINATION` from the immediately prior checkpoint is strong on the **content-admission** side: individual behavioral replay + semantic/schema checks + joint marginal-gain gating prevent persistent skill contamination, but its Holdout-14 is repeatedly reused without sequential calibration.

No source found in this run directly combines both:

`skill/content-level pre-commit harmlessness + combinatorial interaction gate + anytime-valid/reusable-holdout repeated-use accounting + lineage/global risk budget + untouched lockbox`,

with a matched ablation proving each layer's marginal value over more than five adaptive rounds.

That combination is now a sharper frontier than another generic “self-evolving agent” search.

## Nonempty frontier / exact continuation

1. Search specifically for **skill/library admission gates with e-processes, confidence sequences, reusable holdouts, online-FDR, or global alpha spending**; require a disjoint final lockbox.
2. Search for **>5-round** self-evolving skill/harness experiments reporting both content-contamination events and statistically labelled false/harmful commits.
3. Inspect SGM raw CSV/SQLite-export artifacts to determine whether its own long-loop can be replayed across `sgm/naive_screen/best_screen` from already-recorded outcomes without training; preserve this as within-SGM evidence, not a PACE comparison.
4. Search for fresh PACE code/data release in later revisions before each future replay attempt.
5. If no combined real-agent source appears, inspect reusable-holdout theory/implementations only to define assumptions and failure modes; do not promote synthetic simulations to deployment evidence.

Next concrete action: begin with item 1 using combinations of `skill admission`, `library gate`, `e-process`, `confidence sequence`, `reusable holdout`, `online FDR`, `alpha spending`, and `self-evolving agent`; prioritize August 2026 primary papers and public artifacts. Keep this file plus `checkpoint_2026-08-26T0020_JST_clean_g1_turn1_followup.md` as the exact continuation pair.

## Termination diagnostic

Not complete. The PACE artifact branch reached a clear public-evidence boundary and was converted into an explicit replay-data contract; the remaining research gap is now a composition/factorial problem rather than an underspecified search.