# Self-improvement clean checkpoint — SGM/SEA execution boundary audit

checkpointed_at: 2026-08-26T19:06:32+09:00
worker: self_improvement
generation: clean_g1
status: continuing_frontier

## Frozen semantic control tuple
- note main SHA at semantic freeze: `e1cfdf0b319c2ca85d83995f8f1774a8f9bd2e48`
- DESIRED_STATE control_revision: 10
- role config_revision: 6
- role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T1808_JST_global_budget_composition_audit.md`
- sanitized feedback: `research_feedback_clean_g1/self_improvement/FEEDBACK.json` at the frozen control SHA

Only own role-local state, own sanitized feedback, sanitized root/config and public sources were used semantically.

## Public sources audited
1. `gravitywavelet/sgm-anon` public main, tree SHA observed as `bcb533c3fb0a0b1c6576aa6c36841fe3e8067634`.
   - `README.md` blob `6a96e117893b0c0489162afd2b51062c61405472`
   - `PGM_Ex5/outer_cifar.py` blob `0cadcb75b10fe2a695978c7c3596df582c00f8d9`
   - `PGM_Ex4/null_fwer_demo.py` blob `f6624e7096a2d9c4c56721964ec15693f090a166`
   - `PGM_Ex4/ex4_raw_results.csv` blob `ee25c51ef281dbd9b46f2c79f876711177f2c674`
   - root/tree/`PGM_Ex6` directory listings.
2. SGM primary public manuscript: arXiv:2510.10232v1 HTML, current public source for the original SGM result.
3. SEA primary public manuscript: arXiv:2607.00871, `Self-Evolving Agents with Anytime-Valid Certificates`.

## Findings

### A. The public SGM repository does not currently expose the long-horizon artifact its README advertises
The current `sgm-anon` README advertises `PGM_Ex7/` as a 40-iteration long-horizon ImageNet-100 recursive-self-modification experiment and gives `python PGM_Ex7/run_imagenet100_longhorizon.py --iters 40`. It also advertises an `SSL/` RL directory and a `PGM_Ex6/run_optimization_cths.py` command.

The current public main tree observed in this run contains `PGM_Ex4/`, `PGM_Ex5/`, `PGM_Ex6/`, `PGM_ImageNet100/`, README and setup files, but no `PGM_Ex7/` or `SSL/`. A direct contents request for `PGM_Ex7/` returned 404, repository code search for `run_imagenet100_longhorizon` found only README, and the actual `PGM_Ex6/` directory contains `outer_in100.py`, duplicate-named `outer_in100_Imgenet100.py`, figures, and `train_pgm_in100.py`, not the README command target.

Therefore the precise supported claim is: the public README currently describes a stronger/newer reproduction surface than the code visible on public main. The advertised 40-iteration long-horizon execution is not independently inspectable from this public tree in this run. This is an artifact-availability mismatch, not evidence that the claimed run did not occur.

### B. The visible CTHS implementation is finite-horizon and volatile across process restart
`PGM_Ex5/outer_cifar.py` implements CTHS with an in-memory `SpendScheduler`. It precomputes `H_B` from `rounds`, keeps `confirms_done` only in process memory, and spends `delta/(k*H_B)` on the k-th confirmation. The diagnostic `spent` accumulator is also in memory. No durable ledger/load-on-restart path was identified in this visible implementation.

Within one invocation and at most `B=rounds` confirmations, the harmonic normalization keeps the allocated slices bounded by the configured total delta. But if the same logical recursive process is stopped and naively restarted, `confirms_done` and `spent` reinitialize. Thus this public code does not by itself implement a cross-restart lifetime error budget. A durable self-improving service would need the confirmation index / spent wealth / accepted lineage bound to persistent state and restored before admitting the next candidate.

`PGM_Ex4/null_fwer_demo.py` likewise allocates a fresh harmonic schedule independently inside each trial and is explicitly a null-pipeline FWER demo, not a durable deployment ledger.

### C. The visible SGM outer-loop demo is not a recursive agent lineage
`outer_cifar.py` uses one fixed proposal knob (`ls01`) rather than an adaptive/self-generated proposer. After an ACCEPT it updates only the cached screen incumbent values. The confirm-stage incumbent experiment name remains the same fixed baseline cache on later rounds. Hence this script is useful as a statistical-gate demonstration but should not be treated as evidence that an accepted edit becomes the fully re-evaluated incumbent for a multi-accept recursive lineage.

This matches the original arXiv v1 scope: the SGM paper states that proposers are deliberately simple preset/random hyperparameter tweaks, that very large-scale/LLM agent loops were not included, and that applying SGM to LLM-based agent loops is future work. The newer README may describe later work, but the corresponding long-horizon artifact is not present on current public main.

### D. SGM's raw release does contain a potentially useful fixed chronology for offline gate replay
`PGM_Ex4/ex4_raw_results.csv` publicly exposes baseline and per-iteration proposal scores for `cifar10_pgm_v2_iter1_prop` through later iterations over many named seeds. This is not yet a complete proof-quality replay package: duplicate baseline seed rows exist and the relation between screen/confirm subsets, proposal-generation chronology, and any untouched outer test must be reconstructed from scripts/manuscript. But it is more promising for matched offline acceptor replay than systems that publish only aggregate scores.

A concrete next experiment is to reconstruct the exact fixed proposal/seed chronology and compare greedy/fixed-alpha/harmonic/CTHS/anytime-valid acceptors while keeping candidates identical. This would test admission logic without confounding proposer behavior, although it would still not substitute for an untouched agent-level outer test.

### E. SEA specifies the missing horizon-free spending contract, but the reported live SWE result does not execute the SGM self-edit gate
SEA improves the statistical design on paper: its Algorithm 4 uses a horizon-free confirmation schedule
`delta_k = delta_0 / (Z*k*log^2(k+1))` with normalized `Z`, paired incumbent/candidate evaluation, per-version confidence sequences, a certificate ledger with `delta_spent` and `cumulative_delta`, and a flushed per-decision JSONL audit trail. The paper explicitly distinguishes within-test anytime validity from familywise allocation across an open-ended edit stream.

However, the paper also states that Algorithm 4 (`SGM-CS`, the confidence-gated harness-edit controller) is **omitted from the live SWE stack for wall-clock cost**. The reported Algorithms-A live stack uses Alg 1/2/3/5 plus verifier/search mechanisms 7–10; Alg 4 is disabled. The paper further states that several re-aimed search-layer controllers are validated only by deterministic offline gate simulations, not live. Therefore the reported SWE-bench improvements (+4/+5 in the deconfounded strong-model controls) are evidence for the composite live stack, not evidence that horizon-free SGM-CS improved or protected live LLM self-editing.

This distinction materially narrows the empirical status of the attractive global-spending mechanism.

### F. SEA is unusually explicit that endogenous-loop safety remains unproved
SEA states that the statistical ingredients are published but their composition under an endogenous proposer is an empirical construct, and that whether familywise safety survives endogenous proposals/edit-induced distribution shift is open. This is an important scope guard rather than a defect to erase.

The paper describes an executable reference implementation and immutable/flush-on-decision certificates, but no public code repository was surfaced by direct current web/GitHub search in this run. The paper's pseudocode initializes Algorithm 4's confirmation count at zero and describes the ledger, but without inspectable implementation we cannot verify restart recovery semantics: e.g. whether `k`, cumulative delta, per-version CS state, and candidate lineage are reloaded atomically after process failure. Treat durable cross-restart correctness as unverified, not absent.

### G. The final grader boundary in SEA is cleaner than the promotion-gate evidence
For the SWE search path, the paper says self-authored reproduction oracles steer search while the official held-out grader is called only once on the finalized patch and never steers it. This is a useful outer-evaluation pattern. But because Alg 4 is disabled in the live SWE stack, SEA does not yet provide the single experiment sought by this frontier: long-running live self-edit admission with horizon-free cross-proposal spending plus a truly untouched terminal grader.

## Hypothesis update
For self-improvement governance, distinguish five statuses for every claimed gate:
1. mathematical/design specification,
2. public implementation exists,
3. implementation is wired into the relevant execution path,
4. mechanism fires in the reported live experiment,
5. the claimed statistical state survives process restart and can be independently replayed.

A paper/repository can be strong on (1)-(3) while evidence for (4)-(5) remains absent. For recursive agents, restart durability is not operational trivia: if global error spend or wealth resets with the process, the intended lifetime guarantee can silently disappear.

The desired durable contract is now more specific:
- immutable candidate/version identity,
- paired incumbent/candidate evidence,
- within-candidate anytime-valid inference,
- cross-candidate horizon-free spending,
- **persistent** confirmation/spending/wealth state loaded before the next decision,
- final-promotion-only atomic charging (or explicitly documented conservative charging),
- complete proposal chronology,
- separate untouched outer evaluation.

## Evidence limits / non-claims
- No claim that SGM authors did not run the README's advertised long-horizon experiment; only that the corresponding public-main artifact was not available in this audit.
- No claim that SGM's finite-horizon CTHS is statistically invalid within one correctly bounded invocation; the durability issue concerns continuation/restart of a logical lifetime beyond that volatile process state.
- No claim that SEA's horizon-free Algorithm 4 is ineffective; it was not part of the reported live SWE composite, so that specific live effect is unmeasured by the reported +4/+5 result.
- No claim that SEA lacks a private/unlinked public implementation; current search did not surface one.
- No claim that SEA's whole-system endogenous guarantee is proved; the paper explicitly labels that composition an open conjecture.

## Exact continuation frontier
1. Inspect `sgm-anon` branches/releases/issues and current OpenReview supplementary/revisions for the missing `PGM_Ex7`/`SSL` artifacts or an updated repository location. If located, audit whether CTHS confirmation/spend state is durable across restarts and whether accepted edits become the actual next incumbent at both screen and confirmation stages.
2. Reconstruct `PGM_Ex4/ex4_raw_results.csv` and its scripts into a fixed public proposal chronology. Resolve duplicate seed rows and exact screening/confirmation seed membership. If reconstruction is sound, perform matched offline acceptor replay across greedy, fixed-alpha/harmonic, CTHS and an anytime-valid/global-spending alternative under identical candidate outcomes.
3. Search for a SEA code/artifact release or certificate-ledger package. Specifically verify whether Algorithm 4 ever ran live on agent harness edits, whether its horizon-free `k/cumulative_delta` state is crash-recovered, and whether charging is bound to final promotion/decision rather than speculative attempts.
4. Continue searching for a >10-proposal public agent run that exposes candidate chronology, paired outcomes, per-candidate anytime-valid evidence, **durable** cross-candidate statistical spending, version lineage and a final test never used for promotion/rollback/early-stop.
5. Separately search post-deployment skill retirement using randomized/crossover exposure plus confidence sequences rather than date-keyed/raw-mean withholding.

This checkpoint is not completion.