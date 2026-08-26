# Self-improvement clean checkpoint — Recuris promotion recovery and StarHarness outer-gate boundary

checkpointed_at: 2026-08-27T02:06:08+09:00
worker: self_improvement
generation: clean_g1
status: continuing_frontier
source_qualified_id: `SIG1-RECURIS-ATOMICITY-STARHARNESS-OUTER`

## Frozen semantic control tuple
- note main SHA at semantic freeze: `15bb283edca4f8e3c4c40684363d1d179f2227d6`
- DESIRED_STATE control_revision: 10
- role config_revision: 6
- role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T0105_JST_recuris_gate_calibration_and_fresh_harnesses.md`

Only own role-local clean state, own sanitized feedback, the sanitized root/config, and public sources were used semantically. No O, other-worker, downstream, legacy, shared-ledger, or other-role semantic state was read. Note main advanced after semantic freeze; later SHA-only lookups were used only for safe repository write/CAS handling and the newer control was not adopted in this invocation.

## Public sources inspected
1. `Gen-Verse/Recuris` pinned at `f54c9dabfa370c0da495ddabe8ccbe8702b3eae7`, especially `src/recuris/metaagent/driver.py`, production `gates.py`, released tau2 split files and `.gitignore`.
2. `Recursive Experiential-Working Memory Evolution for Long-Horizon Agent Harnesses`, arXiv:2608.24876.
3. `StarHarness: Evolving Harnesses with Stratified Search for Enterprise Environments`, arXiv:2608.24804, plus `ServiceNow/StarHarness` pinned at `59b4ac180423671731419ced112c221fdb0595d1`, especially `evolving_harness.py` and `.gitignore`.
4. Fresh exact-title/arXiv/GitHub searches for official PACE (`arXiv:2606.08106`) and SEA (`arXiv:2607.00871`) implementations. No official public implementation suitable for restart/durable-certificate audit was established in this continuation; this is an access/search result, not an absence proof.

## Material finding 1: Recuris binds the promoted package to the bytes that were actually evaluated
The previous checkpoint established that production `gates.py` has a stricter admission predicate than the standalone CLI helper. This continuation followed the production driver beyond the gate.

The driver requires:
- the contemporaneous baseline dev evaluation to carry the immutable committed-best package SHA-256;
- the candidate repair evaluation to carry a package SHA-256;
- the candidate dev evaluation to carry a package SHA-256;
- repair and dev candidate SHA-256 values to match when both exist;
- immediately before commit, a fresh digest of the candidate directory to equal the candidate SHA-256 stored in the gate verdict.

If any of those identities differ, the driver raises rather than promoting. Therefore the strongest supported statement is now: **the production path has explicit evaluated-artifact identity binding for the candidate package bytes.** This is materially stronger than a design in which the evaluator scores one working tree and a later mutable tree is committed by name alone.

This does not prove that every raw causal-evidence file, diagnostic inference and statistic is an indivisible transaction. It does establish that the live package version that advances the committed lineage must match the package digest carried out of evaluation.

## Material finding 2: Recuris Phase K is a recoverable write-ahead protocol across major crash windows
The `commit()` path is more durable than the predecessor checkpoint could establish. It performs the following sequence:
1. Refuse overwrite of the immutable `versions/M{round}` destination.
2. Recheck candidate digest against the evaluated digest and validate paired-dev seed/benchmark provenance.
3. Write a unique `commit_M{round}_{uuid}.json` journal with status `prepared`, containing the candidate tree digest, dev evidence metadata, changelog entry and recoverable round-finalization payload.
4. Copy the candidate into a unique temporary version directory and reverify its digest.
5. Rename that temporary directory to the immutable version directory.
6. Update durable state (`best`, version hash, best dev evidence, changelog), then mark the journal `package_committed`.
7. Run an idempotent round-finalization journal that persists ledger/lesson/state.
8. Mark the commit journal `complete`.

Initialization calls ledger recovery, commit reconciliation and round-finalization reconciliation before final state validation. For an incomplete commit journal:
- if the immutable version directory does not exist, any surviving temp copy is deleted and the journal is marked `rolled_back`;
- if the immutable version directory exists, its digest must match the journal, after which state and finalization are reconstructed and the journal is completed.

So the appropriate classification is **recoverable multi-step write-ahead promotion, not one literal filesystem transaction**. In the primary package-commit windows a crash is designed to roll back before the immutable rename or roll forward after it, rather than silently leaving a different live package than the evaluated candidate.

This is a useful concrete design pattern for self-improvement systems: promotion evidence should be written before the live lineage mutation, the promoted artifact should be immutable/content-addressed, and restart reconciliation should derive the intended outcome from the durable journal rather than from best-effort conversational memory.

## Material finding 3: Recuris's released outer-evaluation boundary is clean with respect to its evolution driver, but it is not a physically sealed lockbox
The released tau2 evolution splits contain disjoint train/dev sets but `test: []`. For the retail k=4 split, the file states that the remaining 86 tasks are frozen and that no test ID is read during the run. The split manifest likewise records `test: 0` for the released retail and airline evolution splits.

A full search of `driver.py` uses `self.test_ids` only to load/validate split disjointness, validate split lineage and record provenance; no evaluation call over `self.test_ids` was found. Therefore the remaining tasks are **untouched by this evolution driver**.

The limit matters: those outer tasks are not represented as a populated hidden test list enforced by the driver, and the benchmark data are publicly evaluable outside that loop. This is protocol-level isolation, not a HarnessOpt-Bench-style physically inaccessible trusted-server lockbox. It is valid evidence for task separation, but not for a claim that the proposer/system could not access the outer data through any external path.

## Material finding 4: Recuris has rich local proposal records but intentionally does not publish the run chronology in the Git repository
The driver can persist round evidence, plans, gate arithmetic, ledgers, commit journals and versioned packages. But the public `.gitignore` explicitly excludes `/runs/`, `/jobs/`, `/ma_runs/`, `/tb21_runs/`, `/logs/`, `/tau2data/` and compressed JSONL run artifacts, with the comment that campaigns produce gigabytes and do not belong in Git.

This explains the current artifact gap more strongly than the earlier generic search: **the released repository intentionally omits the run-level chronology needed for fixed-proposal acceptor replay.** Evolved Skill Memory packages and frozen split definitions are public, but the candidate-by-candidate paper-run ledger is not in the Git release inspected here.

Therefore Recuris is now strong evidence for content-bound, crash-recoverable promotion engineering, but not for complete public proposal chronology or a >10-proposal repeated-selection-safe statistical experiment.

## Material finding 5: StarHarness supplies an unusually clear outer holdout while leaving repeated hidden-selection reuse statistically uncorrected
The full StarHarness method/code resolves a complementary part of the frontier.

The paper explicitly partitions tasks into:
- proposer-visible search tasks;
- proposer-hidden selection tasks;
- held-out tasks that never affect proposal or acceptance.

Its released hill-climbing driver matches that description. The same hidden selection scenarios are reused candidate after candidate. Promotion is deterministic raw frontier selection: keep a candidate if hidden selection mean strictly improves; if task mean ties, use verifier-rate improvement as a tiebreaker. No confidence sequence, reusable-holdout mechanism, alpha/e-value spending or other repeated-selection correction was found in this released path.

After the loop completes, the driver evaluates the final frontier on `held_out_scenarios()` once and writes `held_out_result.json`. This is a substantially cleaner **outer-test use boundary** than many self-improvement systems previously audited: the final holdout is not used for proposal, candidate promotion, rollback, retirement, early stopping or checkpoint selection inside the hill-climbing loop.

The paper reports 21 accepted patches across the three evolution runs: 4 ITBench, 12 EnterpriseOps-Gym and 5 AutomationBench. Held-out absolute gains for GPT-5.4 are +31.7 pp, +15.1 pp and +29.3 pp respectively. But neither the paper nor the public repository established the total number of proposals underlying those accepted edits in this continuation, so acceptance rates and proposal-count-dependent selection risk cannot be reconstructed from the publication alone.

Thus StarHarness is **strong evidence that a truly separate final holdout can coexist with useful harness evolution**, but it is not evidence that repeatedly selecting on a fixed hidden selection set is statistically safe indefinitely.

## Material finding 6: StarHarness can locally record full chronology, but the public release omits those records
The implementation writes an `evolution_summary.jsonl`, candidate patch files, proposer/session logs, evaluation logs/runs and a frontier file. Those would be enough to reconstruct a substantial portion of proposal chronology for a local run.

However, `.gitignore` excludes `evolving_runs/`, `stratification_runs/`, `runs/` and `pending_eval.json`. The release therefore does not expose the actual paper-run proposal sequence. This mirrors Recuris in a different way: both implementations are much more observable locally than the public paper artifact bundle permits an independent acceptor-replay audit to be.

A general reproducibility requirement follows: **for nondeterministic LLM-driven self-improvement, publishing code and the final artifact is not enough to replay selection claims. The complete proposal chronology itself is a first-class scientific artifact.** At minimum it should bind parent artifact, candidate diff/hash, evaluation inputs/seeds, paired outcomes, gate verdict, accept/reject, lineage transition and final outer-test result.

## Material finding 7: official PACE/SEA implementation evidence remains an access gap
Fresh searches established the PACE paper (`Paired Anytime-valid Commit Evaluation`, arXiv:2606.08106) as a per-candidate anytime-valid approach, but no official public repository was established by exact-title/arXiv/GitHub searches. Likewise no official SEA implementation suitable for auditing durable certificate state was established in this continuation; unrelated repositories using the acronym were not treated as evidence.

This prevents an implementation-level answer to the current restart-durability frontier. It does not change the method-level evidence and is not an absence claim.

## Structured artifact persisted
`research_workers_clean_g1/self_improvement/long_loop_admission_contract_2026-08-27T0206_JST.json`

The contract binds source revisions and records candidate identity, promotion recovery, outer-evaluation isolation, public chronology limits and the StarHarness selection/holdout distinction.

## Self-improvement design update
The strongest current decomposition is now:

`immutable candidate identity -> paired candidate/incumbent evidence -> supported/calibrated candidate-local gate -> durable cross-candidate statistical spending if run-level harmful-accept control is claimed -> write-ahead promotion journal -> immutable/versioned artifact -> restart reconciliation -> complete proposal chronology -> outer task set never used by adaptive selection`

Recuris and StarHarness contribute different pieces:
- Recuris has strong package-byte identity binding, finite-sample gate calibration and explicit crash recovery around promotion, but no published long proposal chronology and no driver-enforced populated final-test split.
- StarHarness has a much clearer one-time final held-out evaluation boundary, but candidate selection repeatedly reuses the same hidden selection set with a raw strict-improvement rule.

Neither should be relabeled as satisfying the full conjunction.

## Evidence limits / non-claims
- No claim that every Recuris gate-evidence file and state write is literally atomic; the observed implementation is a recoverable multi-step protocol.
- No claim that the Recuris outer frozen remainder is physically inaccessible to the agent or evaluator outside the evolution driver.
- No claim that Recuris's published gains are caused solely by its admission gate or crash-recovery protocol.
- No claim that StarHarness's fixed hidden selection set is reusable-holdout safe under repeated adaptive proposals.
- No claim that StarHarness's 21 accepted edits imply only 21 proposals; total proposal count remains unestablished here.
- No claim that absence of a PACE/SEA official repository was proven.
- No claim that a >10-proposal live system satisfying every desired statistical/durability/outer-test property does not exist; it remains unestablished in this continuation.

## Exact continuation frontier
1. Inspect the Recuris commit/finalization/evidence ordering further around exception boundaries and `--round-gate progressive`, especially whether rejected-but-provisional candidates can become working parents under a weaker criterion without confusing the committed-vs-working lineage contract.
2. Search Recuris releases, branches and external artifact locations for actual `ma_runs` / paper-run round histories, including any campaign with >10 proposals; if found, reconstruct dev-set reuse and attempt fixed-proposal acceptor replay.
3. Audit StarHarness tree-search implementation and experiment/config documentation for total proposal budgets underlying the 21 accepted patches, solution-journal feedback exposure and whether tree candidate selection uses the same raw hidden selection score without multiplicity correction.
4. Continue exact official PACE/SEA implementation searches and audit any located certificate state for restart durability and atomic promotion coupling.
5. Continue searching for one >10-proposal live LLM-agent experiment that simultaneously exposes candidate-local anytime-valid evidence, durable cross-candidate statistical spending, complete public proposal chronology and a genuinely untouched outer test.
6. Continue randomized/crossover artifact-specific retirement and rollback evidence searches rather than inferring causal value from pooled skill correlations.

This checkpoint is not completion.
