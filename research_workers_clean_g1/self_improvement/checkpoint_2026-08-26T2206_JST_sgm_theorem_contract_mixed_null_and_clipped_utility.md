# Self-improvement clean checkpoint — SGM theorem-contract audit: mixed-null e-value failure and clipped-utility mismatch

checkpointed_at: 2026-08-26T22:06:32+09:00
worker: self_improvement
generation: clean_g1
status: continuing_frontier

## Frozen semantic control tuple
- note main SHA at semantic freeze: `7dbada70beba2d8c93f786f7140c26e197255ec3`
- DESIRED_STATE control_revision: 10
- role config_revision: 6
- role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T2109_JST_sgm_long_gate_implementation_audit.md`
- sanitized feedback: `research_feedback_clean_g1/self_improvement/FEEDBACK.json` at the frozen control SHA

Only own role-local clean state, own sanitized feedback, sanitized root/config and public sources were used semantically. No O, other-worker, downstream, legacy or shared-ledger semantic state was read. The repository head advanced after the semantic-freeze barrier; no newer control semantics were adopted in this invocation.

## Public sources audited
1. SGM primary manuscript, arXiv:2510.10232v1, especially Sections 3.1–3.3 and supervised-learning experiments.
2. `gravitywavelet/sgm-anon` public main `bcb533c3fb0a0b1c6576aa6c36841fe3e8067634`, especially:
   - `PGM_Ex4/run_pgm_cifar.py`
   - `PGM_Ex5/pgm_outer.py`
   - `PGM_Ex6/outer_in100.py`
   - `PGM_ImageNet100/outer_in100_long.py`
   - `PGM_ImageNet100/run_long.sh`
   - `.gitignore`
   - public branch/release/commit metadata.
3. SEA primary manuscript, arXiv:2607.00871v1, as a comparison point for per-edit anytime-valid certification and summable cross-edit spending. No SEA implementation claim is upgraded beyond what the primary manuscript exposes.

## Artifact search update: realized 40-round SGM chronology is still unavailable publicly
The exact `long_sgm.db`/proposal chronology behind the repository's 40-proposal ImageNet claim was not found.

Observed public artifact facts:
- the repository exposes only branch `main`;
- the GitHub releases endpoint is empty;
- the visible history for `PGM_ImageNet100/outer_in100_long.py` contains one commit, `5c75f8775ecc94d2223222d1d2c5b77307851351` (`add long exprement 40 iter`);
- `.gitignore` explicitly excludes `*.db`, `logs/`, and `runs/`;
- the long launch script points to `$RUNS_DIR/long_sgm.db`, but that realized database is not tracked;
- the `PGM_ImageNet100/results.csv` present at the long-driver commit contains only seven generic `seed,lr,epochs,acc` rows and is not a 40-proposal decision ledger.

Therefore the exact realized acceptance sequence still cannot be replayed or rescored from public artifacts. This is an artifact-access limitation, not evidence that the reported trajectory is false.

## Material finding 1: the bounded-utility contract in the paper and the public supervised code are not the same estimand
The SGM manuscript states that tests operate on bounded paired differences `Delta_i in [a,b]`, with `R=max(|a|,|b|)`, and interprets positive mean normalized improvement as improvement of the underlying performance difference.

But the manuscript's own supervised settings show that the configured `r_max` cannot be a literal support bound on the reported raw percentage-point differences:
- CIFAR-100 reports `r_max=1.0` while the accepted proposal has raw mean improvement `+5.51pp`;
- ImageNet-100 reports `r_max=0.5` while the confirmation result at iteration 6 has raw mean improvement `-4.03pp`.

If every raw paired difference were actually bounded by `|Delta_i| <= r_max`, the sample mean could not exceed that bound in magnitude. Thus the reported raw differences themselves establish that these `r_max` values are not literal support bounds for raw accuracy deltas.

The current public supervised code resolves this by changing the tested variable:
- `PGM_Ex4/run_pgm_cifar.py` divides each raw delta by `rmax_pp` and clips to `[-1,1]` before certification;
- `PGM_Ex5/pgm_outer.py` does the same for screen and confirmation;
- `PGM_Ex6/outer_in100.py` does the same, with default `rmax_pp=0.5` matching the paper's ImageNet setting.

That is a valid *definition of a winsorized utility* if stated explicitly, but a confidence certificate for `E[clip(Delta/rmax,-1,1)] > 0` is not in general a certificate for `E[Delta] > 0`.

A concrete sign-reversal example under the ImageNet setting `rmax=0.5pp`:
- with probability 0.9, raw improvement is `+0.25pp`;
- with probability 0.1, raw improvement is `-5pp`.

Then raw expected improvement is `-0.275pp`, while the clipped normalized mean is `0.9*(+0.5)+0.1*(-1)=+0.35`. A perfectly valid statistical certificate on the clipped variable could therefore approve a proposal whose raw expected accuracy change is negative.

This does not show that any reported SGM acceptance has this distribution. It shows that the theorem contract must bind the *actual protected utility*. If the intended utility is winsorized, claims should be about winsorized utility or separately prove that clipping cannot reverse the decision-relevant ordering.

## Material finding 2: empirical-Bernstein range constants differ across public SGM paths
The manuscript's empirical-Bernstein LCB contains the additive term `3(b-a) ln(3/delta)/n`. For a normalized variable in `[-1,1]`, the range width is `b-a=2`.

Public paths are inconsistent:
- `PGM_Ex4/run_pgm_cifar.py` uses a full additive range term with default `R=2.0`, matching a width-2 normalized support, while still testing a clipped rather than raw utility;
- `PGM_Ex5/pgm_outer.py` documents `y in [-1,1]` but calls the empirical-Bernstein bound with `R=1.0`, so its additive term is half the width-2 term stated in the manuscript;
- `PGM_Ex6/outer_in100.py` defines an empirical-Bernstein helper with `R=1.0`, but its active final confirmation path uses a Hoeffding bound on the clipped variable; the Hoeffding radius implemented there is consistent with width 2 for `[-1,1]`, so the main remaining theorem-contract issue for that final gate is the clipped estimand and sample-selection protocol, not the same missing EB term;
- `PGM_ImageNet100/outer_in100_long.py` omits the empirical-Bernstein additive range term entirely, as established in the predecessor checkpoint.

Therefore function names such as `eb_lower_bound` are not enough to identify a common certificate across the repository. Each executable path needs a source-bound theorem contract.

## Material finding 3: the manuscript's cross-round e-value theorem is invalid for a mixed sequence of true and false per-edit nulls as written
The primary manuscript defines, across self-modification rounds,
- `e_{t,i}=1+lambda_{t,i} X_{t,i}`;
- `E_t=product_i e_{t,i}`;
- `W_t=W_{t-1} E_t`, `W_0=1`;
- acceptance when `W_t >= 1/delta`;
- and claims `Pr(exists t: accept at round t when mu_t <= 0) <= delta`.

The supermartingale argument only holds for a product of factors whose conditional expectations are <=1 under the null being tested. For a *beneficial* candidate (`mu_t>0`), `E[e_{t,i}|past]` can exceed 1. Once such alternative-round evidence is multiplied into the same wealth process, that wealth is no longer an e-process for a later candidate-specific harmful-edit null.

A deterministic counterexample uses the manuscript's own update rule with `delta=0.1`, `lambda=1`, and one normalized observation per candidate:
1. rounds 1–4 are genuinely beneficial with `X=+1`; wealth is `2,4,8,16`; round 4 is beneficial and crosses the threshold `1/delta=10`;
2. the algorithm does not reset `W` after accepting and continues recursive modification;
3. round 5 is genuinely harmful with deterministic `X=-0.1`, hence `mu_5=-0.1`;
4. wealth becomes `16*0.9=14.4`, still above 10, so the stated acceptance rule accepts the harmful round-5 edit with probability 1.

This directly contradicts a familywise claim bounded by `delta=0.1` over arbitrary mixed beneficial/harmful edit sequences.

The statistical reason is structural: multiplying per-edit e-values across different hypotheses gives an e-process for an *intersection/global null* only when every contributing factor satisfies its null expectation condition. It does not by itself control the union event "some later candidate-specific null is true" after evidence from false nulls/real improvements has increased wealth.

Resetting wealth after every successful edit would avoid this exact carry-over counterexample but still would not yield a global 0.1 FWER across an unbounded number of independently retested edits. A cumulative guarantee needs null-specific evidence plus a valid cross-hypothesis mechanism, e.g. summable per-edit alpha/e-value budgets or a multiple-testing construction whose theorem actually covers the adaptive hypothesis sequence.

This finding is about Theorem 2 / the across-round wealth construction as written in arXiv:2510.10232v1. It is logically independent of the public-code empirical-Bernstein defects. The repository text search in this run did not locate an obvious e-value implementation, so no claim is made here about an unobserved/private implementation.

## Sample-selection contract remains inconsistent with the paper's stated supervised protocol
The manuscript explicitly says screening and confirmation use disjoint seed pools for supervised learning. Public `make_seed_set(...)` in both the Ex5 and Ex6/ImageNet-style code returns the screening seeds plus extra seeds, so confirmation reuses the selected screening observations. The long driver does the same.

Thus even a corrected fixed-n bound needs an execution path that uses genuinely disjoint confirmatory evidence after screening, or a theorem that explicitly permits the selection/reuse mechanism.

## Comparison point: what SEA gets structurally closer to, and what it still does not establish
SEA (arXiv:2607.00871v1) explicitly treats the self-evolving agent as an adaptive system and specifies a candidate-specific anytime-valid self-edit gate plus a summable horizon-free per-edit error schedule rather than carrying favorable evidence from one edit directly into a later edit's null test. That is structurally closer to the required cross-hypothesis contract.

But SEA itself limits the claim: its composition under an endogenous proposer is not established as a complete safety theorem, and the manuscript says the expensive self-edit certification algorithm is disabled in the reported live SWE-bench stack. Therefore SEA is useful here as a design direction, not as empirical validation that the full long-horizon contract already works in live self-improving agents.

## Self-improvement design update: a proof-carrying gate needs a hypothesis identity, not just a theorem name
The durable admission record for an irreversible self-improvement should bind at least:
1. candidate and incumbent hashes plus the exact per-edit null being tested;
2. the protected utility/estimand, including any clipping, winsorization, saturation or nonlinear transformation;
3. a mathematically valid support/range bound for that utility, not a merely "plausible" gain scale;
4. the exact bound/e-process formula, constants and threshold semantics;
5. all selection, screening and confirmation sample identities and whether reuse is theorem-permitted;
6. candidate-local evidence state that cannot inherit favorable wealth from a different false null unless a valid multiple-testing theorem explicitly permits it;
7. cross-candidate cumulative error state with a theorem covering adaptive hypothesis generation;
8. executable null and mixed-null calibration tests, including adversarial sign-reversal distributions;
9. atomic persistence/restart semantics for both promotion lineage and cumulative risk state;
10. an outer evaluation never used for proposal, acceptance, rollback, retirement, early stopping or best-checkpoint selection.

This strengthens the prior "proof-carrying statistical gate" requirement: the theorem must be bound not only to code and constants but also to the *identity of the null hypothesis whose evidence is being accumulated*.

## Evidence limits / non-claims
- No claim that the SGM framework has no useful risk-control ideas; its fixed-budget union-bound/CTHS direction remains conceptually separable from the defects identified here.
- No claim that the published CIFAR or ImageNet decisions would reverse under a corrected raw-utility analysis without the unreleased per-seed chronology.
- No claim that the README 40-round `23.2% -> 28.2%` trajectory is false.
- No claim that every private or historical SGM implementation matches current public main.
- The e-value counterexample targets the manuscript's single cross-round wealth process and its claimed mixed-sequence harmful-accept guarantee as written.
- The clipping examples are counterexamples to equivalence of estimands, not claims about the empirical distributions in the reported experiments.
- The public-code range-width findings are path-specific and version-specific.

## Exact continuation frontier
1. Search author-side artifacts, Git history, forks, supplementary storage and archived assets for the exact `long_sgm.db`, proposal ledger and code revision behind the 40-round claim. If found, replay every candidate using the manuscript-faithful raw utility and separately the actually implemented transformed utility.
2. Turn the SGM source-local theorem-contract audit into a compact executable matrix for Ex4/Ex5/Ex6/long: estimand, clipping/transformation, support width, bound formula, spending index, screening/confirmation overlap, accept threshold, restart state. Add null and mixed-null adversarial tests for each active gate.
3. Inspect the manuscript appendix/review history for any qualification or correction of the across-round e-value theorem. Search public code/history for an e-value implementation; if one appears, check whether wealth is candidate-local, reset, spent, or globally multiplied across alternatives.
4. Locate SEA's public/reference implementation if available; audit whether its per-edit spending/certificate ledger is durable across restart and atomically bound to candidate promotion. Keep live-result evidence separate because the manuscript's expensive self-edit gate was disabled in that experiment.
5. Continue searching for a >10-proposal public self-improving agent with candidate-local anytime-valid evidence, durable cross-candidate statistical spending, full proposal chronology and a terminal test never used for selection.
6. Continue randomized/crossover post-deployment skill-retirement searches using confidence sequences/e-processes, and require that retirement evidence also be candidate/artifact-specific rather than pooled across heterogeneous skills.
7. Explore signed sealed-audit/telescoping progress ledgers only where a non-vacuous uniform capacity bound on the adaptive hypothesis class can be justified; do not treat a hidden evaluator alone as a statistical guarantee.

This checkpoint is not completion.