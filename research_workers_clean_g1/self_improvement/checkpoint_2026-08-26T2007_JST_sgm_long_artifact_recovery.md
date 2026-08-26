# Self-improvement clean checkpoint — SGM long-run artifact recovery and replay boundary

checkpointed_at: 2026-08-26T20:07:39+09:00
worker: self_improvement
generation: clean_g1
status: continuing_frontier

## Frozen semantic control tuple
- note main SHA at semantic freeze: `2a3aa1187560a6aa18ee55f25791e953477801d8`
- DESIRED_STATE control_revision: 10
- role config_revision: 6
- role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T1906_JST_sgm_sea_execution_boundary.md`
- sanitized feedback: `research_feedback_clean_g1/self_improvement/FEEDBACK.json` at the frozen control SHA

Only own role-local clean state, own sanitized feedback, sanitized root/config and public sources were used semantically. The note main advanced after semantic freeze; no newer control or cross-role semantic state was adopted.

## Public sources audited
1. `gravitywavelet/sgm-anon` current public main and Git history.
   - current main: `bcb533c3fb0a0b1c6576aa6c36841fe3e8067634`
   - commit `5c75f8775ecc94d2223222d1d2c5b77307851351`, message `add long exprement 40 iter`
   - current `PGM_ImageNet100/outer_in100_long.py`, blob `955093ebb191c9dd5c8b7b7e45ed159e554c5ca2`
   - current `PGM_ImageNet100/run_long.sh`, blob `9f47e92057f322de0001e13258ea58261944a2ea`
   - current `README.md`, blob `6a96e117893b0c0489162afd2b51062c61405472`
   - current branches API: only `main`; releases API: none; issue list: one unrelated issue.
2. `PGM_Ex4/run_pgm_cifar.py`, blob `8bd61b34beaeba8f47e1376abed29258c8fed10d`.
3. `PGM_Ex4/ex4_raw_results.csv`, blob `ee25c51ef281dbd9b46f2c79f876711177f2c674`.
4. SGM arXiv public page `2510.10232v1` and current web/GitHub search for later public artifacts.
5. SEA arXiv `2607.00871v1` plus current web search for a public code/certificate-ledger release.

## Findings

### A. Correction: the 40-proposal SGM execution code is public on current main, but under a different path than the README advertises
The prior checkpoint said the advertised `PGM_Ex7/` long-horizon artifact was not independently inspectable from current public main. That was too strong.

Current Git history shows commit `5c75f877...` with message `add long exprement 40 iter`. That commit added `PGM_ImageNet100/outer_in100_long.py` and `PGM_ImageNet100/run_long.sh`; both still exist on current main. `run_long.sh` sets:
- `BUDGET=40`,
- screen seeds `41 42 43`,
- `CONFIRM_N_SEEDS=12`,
- `--policy sgm`,
- `--no_early_stop`,
then invokes `outer_in100_long.py`.

So there is a concrete public 40-proposal driver. The README reproduction table is stale/misaligned: it points to non-existent `PGM_Ex7/run_imagenet100_longhorizon.py --iters 40`, whereas the extant executable path is `PGM_ImageNet100/run_long.sh` / `outer_in100_long.py --budget 40 --no_early_stop`.

### B. The long driver is a genuine recursive incumbent lineage, not the fixed-incumbent limitation seen in the earlier Ex4 demo
In `outer_in100_long.py`, an accepted candidate executes `inc_cfg = prop_cfg`, then recomputes screen performance under a new incumbent experiment name derived from the accepted config hash. Subsequent proposals are generated from that updated `inc_cfg`. Therefore accepted edits really do become the next incumbent in this long-driver path.

This narrows the earlier negative observation: `PGM_Ex4/run_pgm_cifar.py` is insufficient evidence for a fully recursive multi-accept lineage, but the later `PGM_ImageNet100/outer_in100_long.py` does implement one.

### C. CTHS state is not explicitly durable, but restart semantics are subtler than a simple reset
The long driver initializes `confirm_count=0` and `delta_used_total=0` in memory and does not load a dedicated certificate/risk ledger. On its face that is not explicit crash-durable spending state.

However, a fresh process also restarts the outer loop at iteration 1 and reuses cached run outcomes from SQLite by experiment/config hash. If all previously completed run rows remain stable, replaying iterations 1..k can deterministically re-trigger the same confirmations and acceptances, implicitly reconstructing `confirm_count`, cumulative spend and incumbent lineage before reaching new work.

Therefore the precise status is **implicit replay recovery, not explicit durable-ledger recovery**. It may preserve the intended schedule in the ideal stable-cache case, but the lifetime guarantee remains unverified under crashes because:
- `torch.backends.cudnn.deterministic = False`,
- incomplete seed runs can be rerun after restart and may yield different outcomes,
- the driver does not atomically bind confirmation index/spend to an accepted version,
- proposal rows can be duplicated by replay,
- recovery correctness depends on cached experiment identities and database integrity rather than a loaded risk certificate.

A restart test must deliberately crash at screen, post-confirm/pre-log, and post-accept/pre-next-iteration boundaries and verify that the reconstructed lineage and cumulative delta exactly match uninterrupted execution.

### D. The README's long-horizon numerical result remains artifact-level unverified
The current README claims 40 iterations, two acceptances, 23.2%→28.2%, ~2136 vs ~12960 minutes, and cumulative risk below δ=0.1 across 120 decisions. The public Git tree contains the long driver and launch script, but current repository search found no committed `long_sgm.db`, long-run JSON/CSV proposal ledger, trajectory, or result bundle matching those numbers. The only current hit for `long_sgm` is the launch script; `23.2/28.2` likewise resolves to README text.

Commit history is also informative: the long-run code was added in `5c75f877...`, followed by a README update and requirement-file change, with no visible result-artifact commit. Thus the long-run *execution path* is now inspectable, but the reported 40-round *realized chronology and outcomes* are still not independently replayable from public artifacts located in this run.

### E. Exact offline replay of Ex4 acceptors is blocked by the released CSV format, not merely by missing analysis code
`run_pgm_cifar.py` resolves incumbent/candidate outcomes with `ORDER BY ts DESC LIMIT 1` for each `(exp_name, seed)`. The released `ex4_raw_results.csv` summary drops those timestamps and does not dump the proposals table/config lineage.

The visible CSV has duplicate baseline rows for multiple seeds (e.g. seed 17 appears three times; 23/37/41/53 also repeat) but no timestamp in the summary section to identify which row `fetch_acc` would have selected. It also exposes only 12 rows for `cifar10_pgm_v2_iter10_prop` while iterations 1–9 expose the full 36-seed panel. The exact incumbent/proposal config lineage and original accept/reject chronology are not present in this CSV.

Therefore a proof-quality matched replay across greedy / fixed-alpha / harmonic / CTHS / anytime-valid alternatives cannot be reconstructed from `ex4_raw_results.csv` alone. Required missing artifacts are at minimum the original SQLite `runs` + `proposals` tables or a timestamped export containing every candidate config, parent/incumbent identity, paired outcome and decision. A lossy replay using arbitrary duplicate-row resolution would manufacture chronology and is rejected.

### F. SEA public-code status remains unchanged in this search pass
Current web search surfaced the primary SEA manuscript and secondary summaries but no inspectable official repository/certificate-ledger release tied to arXiv:2607.00871. The paper remains explicit that Algorithm 4 / SGM-CS is omitted from the reported live SWE stack for wall-clock cost. No new evidence was found that the horizon-free self-edit gate ran live or that its `k/cumulative_delta` state has crash-recovery semantics in a public implementation.

## Hypothesis update
For long-running self-improvement, separate **replay-reconstructible state** from **explicitly durable state**.

A system can sometimes recover a risk counter by replaying immutable prior evidence from iteration 1. That is stronger than a blind reset, but weaker than an atomic certificate ledger because recovery depends on deterministic/stable evidence and exact re-execution of every prior decision. A robust deployment contract should record at each final decision:
- candidate/version hash,
- parent/incumbent hash,
- paired evidence identity,
- confirmation index,
- allocated delta/e-value wealth before and after,
- accept/reject/HOLD result,
- durable cumulative spend,
- transaction/commit identity,
and restore this state directly before the next proposal.

For research reproducibility, a README command/path mismatch is not just documentation friction when the central claim is a long adaptive chronology. The publishable unit should include the actual driver, exact invocation, proposal/decision ledger and result bundle used for the reported run.

## Evidence limits / non-claims
- No claim that the README's 40-round numbers are false; only that their realized chronology/result bundle was not located publicly in this audit.
- No claim that replay-based recovery must fail; only that crash-equivalent lifetime risk control has not been demonstrated by the inspected implementation.
- No claim that Ex4 cannot support any descriptive reanalysis; only that exact matched acceptor replay is not justified from the lossy CSV alone.
- No claim that SEA lacks private or newly unindexed code; current public search did not surface an official release.

## Exact continuation frontier
1. Inspect `PGM_ImageNet100/outer_in100_long.py` history and any unindexed repository artifacts for a committed/generated `long_sgm.db`, logs, figures, notebook cells, or export matching the README 40-round chronology. If unavailable, treat the numerical long-run result as paper/README-level evidence while preserving the now-verified execution path.
2. Design a crash-recovery audit for the long driver: uninterrupted vs forced restart after (a) screen cache completion, (b) confirmation completion before proposal-log commit, (c) proposal-log commit before incumbent recomputation, and (d) accepted incumbent recomputation. Compare recovered `confirm_count`, cumulative delta, version/config lineage and decisions exactly.
3. Search author forks/archived commits/supplementary storage for the original Ex4 SQLite DB or timestamped proposals export. Do not perform matched acceptor replay unless duplicate baseline selection and complete iter10/lineage can be resolved without fabrication.
4. Continue searching for SEA code/certificate artifacts and for a >10-proposal public agent with per-candidate anytime-valid evidence, **durable** cross-candidate spending, complete proposal chronology and a terminal test never used for promotion/rollback/early-stop.
5. Separately search randomized/crossover post-deployment skill retirement with confidence sequences or e-processes rather than raw date-keyed mean comparisons.

This checkpoint is not completion.