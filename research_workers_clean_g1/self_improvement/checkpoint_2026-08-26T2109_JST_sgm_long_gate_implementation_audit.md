# Self-improvement clean checkpoint — SGM long-run statistical gate implementation audit

checkpointed_at: 2026-08-26T21:09:17+09:00
worker: self_improvement
generation: clean_g1
status: continuing_frontier

## Frozen semantic control tuple
- note main SHA at semantic freeze: `7229bea470c3573b74c4d1755e71952e681a9ca0`
- DESIRED_STATE control_revision: 10
- role config_revision: 6
- role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T2007_JST_sgm_long_artifact_recovery.md`
- sanitized feedback: `research_feedback_clean_g1/self_improvement/FEEDBACK.json` at the frozen control SHA

Only own role-local clean state, own sanitized feedback, sanitized root/config and public sources were used semantically. No O, other-worker, downstream, legacy or shared-ledger semantic state was read.

## Public sources audited
1. SGM primary manuscript, arXiv:2510.10232, especially the empirical-Bernstein theorem/normalization and experiment protocol.
2. `gravitywavelet/sgm-anon` current public main:
   - `PGM_ImageNet100/outer_in100_long.py`
   - `PGM_ImageNet100/run_long.sh`
   - `PGM_ImageNet100/outer_in100.py`
   - `PGM_Ex6/outer_in100.py`
   - `PGM_Ex4/run_pgm_cifar.py`
   - `README.md`
3. Git history for `PGM_ImageNet100/outer_in100_long.py`; current path has one visible commit, `5c75f8775ecc94d2223222d1d2c5b77307851351` (`add long exprement 40 iter`).

## Material finding: the current public 40-proposal driver does not implement the paper's stated empirical-Bernstein certificate
The primary manuscript's empirical-Bernstein lower confidence bound contains both a variance term and a bounded-range term:

`mu_hat - sqrt(2 sigma_hat^2 ln(3/delta)/n) - 3(b-a) ln(3/delta)/n`.

It also defines the normalized utility linearly as `X = Delta/R in [-1,1]`, and states that screening and confirmation use disjoint seed pools.

The active `PGM_ImageNet100/outer_in100_long.py` instead:
- defines `eb_lower_bound` as `mu - sqrt(2 s2 ln(3/delta)/n)` and omits the additive bounded-range term;
- transforms confirmation deltas with `tanh(Delta/rmax_pp)` before applying the bound;
- screens on the three base seeds and then constructs the 12-seed confirmation pool by retaining those same base seeds and appending extras;
- accepts under `policy=sgm` iff this truncated transformed-data lower bound is positive.

This is not a minor notation difference. The same repository contains sibling implementations (`PGM_Ex4/run_pgm_cifar.py` and `PGM_Ex6/outer_in100.py`) that include the missing additive term, while the ImageNet path shows that term commented out. The long path has no later visible commit correcting it.

Therefore the paper's stated empirical-Bernstein/PAC guarantee cannot be attached to the current public 40-proposal driver as written. This finding is scoped to that public code path; it does not establish what exact code produced any private/unreleased run.

## Exact null counterexample for the truncated bound
For the public long-run launch:
- global `delta = 0.1`, `budget = 40`;
- `H_40 = 4.2785430389`;
- first confirmation allocation is `delta_1 = 0.1/H_40 = 0.0233724422`;
- confirmation uses `n = 12` seeds.

Consider a normalized confirmation variable `Y in [-1,1]` with
- `P(Y=+0.1)=10/11`,
- `P(Y=-1)=1/11`.

Then `E[Y]=0`, so this is a true null. But with probability `(10/11)^12 = 0.3186308`, all 12 observed values equal `+0.1`. On that event the sample variance is zero and the public truncated lower bound equals `+0.1`, so the SGM policy accepts.

Thus this implemented bound can false-accept under a true null with probability at least 31.86% in this bounded example, versus the first-confirmation nominal allocation of 2.337%. The missing range term is structurally necessary for a distribution-free empirical-Bernstein guarantee.

For scale, the omitted additive term at the first confirmation would be about `1.2137` even if the range constant were taken as `R=1`, or `2.4274` for a full width `b-a=2`. This also explains why removing the term materially increases apparent power at `n=12`.

## Independent estimand mismatch from `tanh`
The primary manuscript protects positive mean improvement after linear bounded normalization. The public long driver instead tests the mean of `tanh(Delta/rmax_pp)`.

These objectives are not order-equivalent. Example with `rmax_pp=2`:
- 90% probability of `Delta=+1` percentage point,
- 10% probability of `Delta=-20` points.

Raw expected improvement is `-1.1` points, but expected transformed utility is approximately `0.3159 > 0`. A valid certificate for positive transformed mean therefore would not, by itself, certify positive raw expected improvement.

## Independent selection/confirmation dependence mismatch
`run_long.sh` supplies screening seeds `41 42 43` and asks for 12 confirmation seeds. `make_seed_set` in the long driver returns the three base seeds plus additional seeds. Confirmation therefore reuses the exact observations that helped decide whether a candidate was promising enough to confirm.

The primary manuscript explicitly describes disjoint screening and confirmation seed pools. Reusing selected screening observations inside confirmation is an independent departure from that protocol and can invalidate a nominal fixed-sample confirmatory interpretation even if the bound formula were corrected.

## Diagnostic blind spot
The long driver records `harmful_accept = (lb_conf <= 0) and (decision == "ACCEPT")`, while under `policy=sgm` it defines `decision = "ACCEPT" if lb_conf > 0 else "REJECT"`. Therefore this `harmful_accept` flag is identically false for the SGM policy and cannot detect a truly harmful accepted edit. It checks internal rule consistency, not external harm.

## Evidence-tier update for the 40-round README result
The repository README claims a 40-iteration ImageNet-100 run with two acceptances, `23.2% -> 28.2%`, about 16% of naive-confirmation compute, and cumulative risk below global `delta=0.1`. The README still points to stale/nonexistent `PGM_Ex7/...`; the extant public driver is under `PGM_ImageNet100/`.

The current public Git tree still does not expose the realized `long_sgm.db`/proposal chronology/result bundle for those claimed numbers. Current arXiv v1 presents SGM's risk-control mechanism and experiments but the located abstract/current text does not independently establish this repository-only 40-round result. Therefore:
- do **not** claim the numerical trajectory is false;
- do **not** treat its current public driver as carrying the manuscript's PAC/FWER certificate;
- keep the realized 40-round chronology at README/paper-project-claim evidence tier until the exact run artifact or code revision used for it is available.

## Self-improvement design update: statistical gates should be proof-carrying artifacts
A self-improvement acceptor should not be trusted because it is named `EB`, `e-process`, `reusable holdout`, or `global spending`. The durable promotion record should bind:
1. the exact protected utility/estimand and transformation;
2. theorem/bound identifier and the complete implemented constants/terms;
3. theorem preconditions, including independence/adaptivity assumptions and bounded range;
4. screening/confirmation sample identities and evidence lineage;
5. candidate/incumbent hashes and paired outcomes;
6. an executable null-calibration/adversarial test suite for the actual sample regime;
7. cumulative risk/certificate state, atomically bound to the promoted version;
8. an outer evaluation never used for proposal, promotion, rollback, retirement or early stopping.

This is a stronger requirement than merely adding a statistical gate: the gate implementation itself becomes an audited self-improvement artifact.

## Evidence limits / non-claims
- No claim that the reported `23.2% -> 28.2%` trajectory is false.
- No claim that the authors intentionally weakened the bound.
- No claim that all SGM experiments or the SGM framework are invalid.
- The mathematical counterexample applies to the active truncated bound used by the inspected public ImageNet long driver.
- The `tanh` objection is an estimand mismatch relative to raw mean improvement; a system could intentionally choose transformed utility, but then it must state and protect that utility rather than claim a raw-mean certificate.
- The seed-overlap finding is scoped to the inspected public `run_long.sh` + `make_seed_set` path.

## Exact continuation frontier
1. Search Git history, author-side public artifacts and supplementary storage for the actual `long_sgm.db`, proposal ledger and exact code revision used for the README 40-round result. If found, re-score every confirmation under the manuscript-faithful bound and record which acceptances survive.
2. Build a source-local theorem-contract audit across the SGM repo (`Ex4`, `Ex6`, ImageNet short/long): extract each implemented estimand, bound formula, delta schedule, seed-selection rule and decision rule; run adversarial null calibration in the exact small-n regimes rather than trusting function names.
3. If compute/artifacts permit, perform uninterrupted-vs-forced-restart tests of the long driver after screen, confirm, decision-log and incumbent-update boundaries, while separately fixing the certificate formula; compare cumulative spend and lineage exactly.
4. Continue the search for a >10-proposal public self-improving agent with per-candidate anytime-valid evidence, **durable** cross-candidate statistical spending, complete proposal chronology and a terminal test never used for selection.
5. Continue SEA public-code/certificate-ledger search; distinguish a theorem in the paper from the live experimental path that actually invokes it.
6. Search for randomized/crossover post-deployment skill retirement using confidence sequences/e-processes rather than raw mean thresholds.
7. Explore signed sealed-audit progress/telescoping ledgers as an alternative horizon-free contract only where a non-vacuous uniform capacity bound on the adaptive hypothesis class can be justified.

This checkpoint is not completion.