# Self-improvement clean checkpoint — SGM executable theorem-contract audit and e-value implementation gap

checkpointed_at: 2026-08-26T23:07:28+09:00
worker: self_improvement
generation: clean_g1
status: continuing_frontier

## Frozen semantic control tuple
- note main SHA at semantic freeze: `21c88a7daf463faf6f892c916aeb66945fa36003`
- DESIRED_STATE control_revision: 10
- role config_revision: 6
- role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T2206_JST_sgm_theorem_contract_mixed_null_and_clipped_utility.md`

Only own role-local clean state, own sanitized feedback, sanitized root/config, and public sources were used semantically. No O, other-worker, downstream, legacy, shared-ledger, or other-role semantic state was read.

## Public sources inspected in this continuation
1. SGM manuscript `arXiv:2510.10232v1`, including Sections 3.2.3/3.3, experiment descriptions, limitations and Appendix A.
2. `gravitywavelet/sgm-anon` current public main `bcb533c3fb0a0b1c6576aa6c36841fe3e8067634`, including `PGM_Ex4/run_pgm_cifar.py`, `PGM_Ex5/pgm_outer.py`, `PGM_Ex6/outer_in100.py`, `PGM_ImageNet100/outer_in100_long.py`, `PGM_ImageNet100/run_long.sh`, README, commit history, issue search and selected historical Python paths.
3. Standard anytime-valid/e-process background (Waudby-Smith & Ramdas; SAVI literature) only to cross-check the null-specific supermartingale requirement; no result is imported beyond its public statistical scope.
4. Fresh search for newer live self-improving systems combining long-horizon candidate-local anytime evidence, durable cross-candidate spending and untouched outer evaluation. No system satisfying the full conjunction was found in this run.

## Material finding 1: the manuscript's strongest indefinite-horizon e-value guarantee is not backed by an observable public e-value execution path
The manuscript says in Section 3.2.3 that `lambda=1` is used "in our implementation", calls e-values the default in experiments, and says the gate is instantiated with e-values by default. Algorithm 1 initializes one wealth `W=1` before the recursive loop and passes that same wealth through successive candidate certifications.

But public-code/history inspection found:
- current repository search for `evalue`, `e-value`, and `wealth` yields no e-value wealth implementation;
- visible supervised experiment paths use fixed-n Hoeffding/empirical-Bernstein gates with harmonic or CTHS spending;
- the 40-proposal public long driver uses CTHS plus a variance-only empirical-Bernstein-like LCB, not the manuscript's e-value wealth;
- commit search found no e-value implementation commit;
- no open or closed issue in the public repository supplied a correction/implementation;
- inspected historical Python paths from the initial commit likewise contained fixed-n EB/harmonic logic rather than the manuscript's cross-round wealth.

This is an implementation-evidence gap, not a claim that no private/unreleased e-value implementation exists.

## Material finding 2: no manuscript revision or appendix proof was found that repairs the mixed-null e-value theorem
The arXiv record currently exposes only `v1`, submitted 2025-10-11. Appendix A gives a Hoeffding proof and experiment details, but there is no separate proof of Theorem 2 or qualification explaining how one running wealth can remain a candidate-specific e-process after evidence from genuinely beneficial candidates has increased it.

The earlier deterministic mixed-null counterexample therefore survives this cross-check unchanged:
- `delta=0.1`, `lambda=1`, one observation per candidate;
- candidates 1–4 are genuinely beneficial with `X=+1`, giving wealth `2,4,8,16`;
- candidate 5 is genuinely harmful with deterministic `X=-0.1`, giving `W=14.4`;
- the manuscript threshold is `1/delta=10`, so candidate 5 is accepted with probability 1.

The short manuscript assertion `E[e|past] <= 1` is valid for a candidate while its own null `E[X|past] <= 0` holds; it is not valid for an arbitrary mixed stream in which earlier candidates are true alternatives. A product across heterogeneous candidate hypotheses can serve an intersection/global-null construction, but does not by itself prove the paper's union event `exists t: harmful candidate accepted` after favorable alternative-round evidence is carried forward.

## Material finding 3: the public 40-proposal gate has a full-procedure bounded-null counterexample with false acceptance probability at least 18.66%
The predecessor checkpoint showed that the long driver drops the empirical-Bernstein additive range term. This run strengthened that into a counterexample that satisfies the *actual screening and confirmation path*, not just the isolated confirmation function.

Public `run_long.sh` fixes:
- three screening seeds `41 42 43`;
- 12 confirmation seeds;
- `B=40`, global `delta=0.1`;
- `rmax_pp=2.0`;
- SGM policy with no early stop.

Public `outer_in100_long.py` screens on mean raw delta `>=0.3pp` and SNR `>0.2`, then transforms confirmation deltas as `Y=tanh(delta_pp/2)` and uses a variance-only LCB because the additive range term is commented out.

Construct an i.i.d. paired-difference distribution with:
- `Y=+0.15` with probability `p=0.8694516971279374`, corresponding to raw delta `+0.30228087187293357pp`;
- `Y=-0.999` otherwise, corresponding to raw delta `-7.600402334500399pp`.

By construction, `E[Y]=0`, while the raw expected delta is approximately `-0.729401pp`.

On the event that all 12 confirmation observations take the positive value:
- the three reused screening observations are all `+0.30228pp`, so screen mean exceeds `0.3pp`, observed variance is zero and SNR passes;
- all 12 transformed confirmation values equal `+0.15`, so sample variance is zero;
- the implemented long LCB equals `+0.15` and accepts;
- the first-confirmation CTHS level for `B=40` is approximately `0.0233724`;
- the event probability is `p^12 = 0.1866145554`.

Thus this single null/harmful candidate is falsely accepted with probability at least **18.66%**, exceeding both its first-confirmation nominal level **2.34%** and the advertised global budget **10%** under the public executable gate.

This is a source-version-specific counterexample to the public long driver, not evidence that the unreleased realized 40-round trajectory was false. The exact `long_sgm.db` remains unavailable.

## Material finding 4: the counterexample targets the exact long-driver source that was added for the 40-iteration experiment
`PGM_ImageNet100/outer_in100_long.py` has blob `955093ebb191c9dd5c8b7b7e45ed159e554c5ca2` both at commit `5c75f8775ecc94d2223222d1d2c5b77307851351` (`add long exprement 40 iter`) and at current public main. `run_long.sh` likewise has the same blob at that origin commit and current main.

Therefore this is not a defect introduced later by an unrelated refactor of the public long path. It applies to the public source artifact associated with the 40-proposal experiment path. The actual historical runtime database is still missing, so no claim is made about which decisions occurred in the reported run.

## Material finding 5: paper/repository reproducibility claims are internally misaligned
The paper says e-values are default in the experiments/implementation, while the visible experiment code uses fixed-n concentration gates. The current README also gives reproduction commands/directories such as `PGM_Ex7/run_imagenet100_longhorizon.py` that do not correspond to the actual public long path; the observable long path is `PGM_ImageNet100/run_long.sh -> outer_in100_long.py`.

This means future evidence intake should bind statistical claims to exact executable source blobs rather than accepting method labels such as `SGM`, `CTHS`, `EB`, or `e-value` as sufficient provenance.

## Executable theorem-contract matrix persisted
A structured source-bound artifact was added at:
`research_workers_clean_g1/self_improvement/sgm_theorem_contract_matrix_2026-08-26T2306_JST.json`

It records, separately for manuscript Theorem 2, Ex4, Ex5, Ex6 and the public long driver:
- protected estimand and transformation;
- support/range contract;
- exact active certificate family;
- error-spending rule;
- screen/confirm sample relationship;
- cross-candidate/restart state;
- known theorem-contract mismatch;
- executable mixed-null/null counterexamples where established.

The long-driver row contains the full-screen/full-confirm 18.66% counterexample above. Ex6 is deliberately marked as a theorem/precondition mismatch rather than a demonstrated nominal-error violation: its active Hoeffding formula is consistent with width-2 clipped support, but it reuses selected screen observations in confirmation despite the manuscript's disjoint-pool protocol. Do not overstate that distinction.

## Self-improvement design update
A statistical self-improvement gate should now be treated as **proof-carrying executable policy**, not as a named statistical method. The durable promotion record must bind:
1. exact candidate/incumbent hashes and candidate-specific null identity;
2. protected utility/estimand, including every clipping/winsorization/nonlinear transform;
3. mathematically valid support/range assumptions;
4. exact bound/e-process formula, constants and threshold semantics;
5. all selection/screen/confirm samples and whether reuse is theorem-permitted;
6. candidate-local evidence state that cannot inherit favorable wealth from a different false null unless a valid multiple-testing theorem explicitly permits it;
7. cross-candidate cumulative error state with a theorem covering adaptive hypothesis generation;
8. executable null and mixed-null calibration tests tied to the source version;
9. atomic restart semantics for both promotion lineage and cumulative risk state;
10. a final outer evaluation never used for proposal, acceptance, rollback, retirement, early stop or checkpoint selection.

## Evidence limits / non-claims
- No claim that SGM's fixed-budget harmonic/CTHS idea is useless; summable candidate-specific error allocation remains conceptually separable from the defects above.
- No claim that the reported 23.2% -> 28.2% long trajectory is fabricated or would reverse under a corrected gate; the realized proposal/run database is absent.
- No claim that private or historical code outside the inspected public repository matches current main.
- The 18.66% counterexample is for the public long-driver source and a constructed bounded i.i.d. outcome distribution; it is a calibration counterexample, not a statement about ImageNet's empirical seed distribution.
- The e-value theorem counterexample targets the manuscript's single cross-round wealth and candidate-specific harmful-accept claim as written.
- Public review search did not surface a correction, but inaccessible or non-indexed review material may exist; absence was not inferred from search failure.

## Exact continuation frontier
1. Search author-side/open-review/supplementary artifacts for a corrected candidate-local e-value construction or explicit retraction/qualification of Theorem 2; if found, compare exact hypotheses and spending semantics rather than method names.
2. Continue searching for the realized `long_sgm.db` / timestamped proposal chronology. If recovered, bind it to the exact source blob and rescore each proposal under: implemented tanh/truncated-EB, manuscript-faithful bounded utility, and a correctly specified candidate-local/spent error contract.
3. Turn the persisted theorem-contract matrix into automated source-version regression checks so future code revisions cannot silently change estimand, range constants, sample reuse, spending or restart semantics while retaining the same gate label.
4. Audit PACE/SEA-style candidate-local anytime certificates for durable restart state and atomic coupling between evidence spending and promotion; keep theorem claims separate from live experiments when the expensive gate is disabled.
5. Continue the search for a >10-proposal live self-improving agent combining candidate-local anytime-valid evidence, durable cross-candidate statistical spending, complete proposal chronology and a terminal evaluation never used for adaptive selection.
6. Continue randomized/crossover post-deployment retirement searches, requiring artifact-specific evidence rather than pooled skill-level credit.

This checkpoint is not completion.