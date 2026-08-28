# Self-Improvement Clean Checkpoint — sequence 91

Created: 2026-08-28T11:04:05.067793+09:00

Frozen semantic tuple: note main `db40813f753acc29a570374d3cde527725bed313`, control revision 13, self_improvement config revision 6, config blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.

## Continuation

Continued only from role-local clean sequence 90 plus public sources and the role's own sanitized mechanical feedback. No O/O-derived state, other-worker state, downstream state, aggregate execution ledger, legacy/pre-independence research, or other-role semantic state was used.

Sequence 90 left one specific engineering gap: find a public executable that enforces **EXPLORE/TRAIN -> adaptive TUNE/selection -> frozen CERTIFY with valid candidate-local anytime evidence -> untouched OUTER/REPORT**, with restart-durable cross-candidate accounting and immutable candidate/evaluation chronology.

## Primary update — OphAgent is a strong executable near-match, but its phase names overstate the enforced topology

Source: `QiZishi/OphAgent` public main revision `59501ad42625cb296279e74954769bd21afc3658`.

The evolution harness explicitly names four phases:

`training -> proposal_selection -> acceptance_validation -> sealed_test`

and has several unusually strong executable safeguards.

### What is actually enforced

- Candidate mutations live in an isolated Git worktree.
- `freeze_candidate` commits the allowed mutation before acceptance evaluation.
- Candidate evaluation must bind the exact frozen worktree `HEAD`; uncommitted post-freeze changes are rejected.
- Baseline evaluation must bind the proposal base commit.
- `acceptance_validation` and `sealed_test` records require controller-side HMAC attestation.
- The sealed suite must be outside both the repository and candidate worktree.
- Its manifest must state `historical_outputs_reused=false`, `candidate_access=forbidden`, `one_shot_release_evaluation=true`, `paired_baseline_candidate=true`, and no high-risk/slice regression.
- Promotion re-verifies the complete sealed case set, attestation, component contracts, candidate commit, and clean worktree.
- Release and active Git refs are updated transactionally with `git update-ref --stdin`; rollback is restricted to frozen release refs.
- The repository contains a test that exercises freeze -> attested paired sealed evaluation -> signed approval -> promotion and checks the active release ref.

This is strong evidence for **immutable candidate identity + physically separated candidate-invisible paired certification + atomic release identity**.

### Why it still does not implement the LOGOS four-surface contract

The decisive `sealed_test` is consumed directly by `approve()` and `promote()`. It therefore serves as **CERTIFY/admission data**, not an untouched OUTER surface.

The statistical gate is also fixed-sample: paired mean difference plus `mean ± 1.96 * SE`, together with deterministic regression, safety, citation, contract, latency and token rules. No e-process, confidence sequence, candidate-local anytime-valid gate, or cross-candidate online FDR/FWER/alpha-wealth ledger was found in the exact revision.

Most importantly, the four names are not the same thing as an enforced four-stage call graph. `PHASE_ORDER` validates phase names, but exact-revision code search found no required invocation path for `proposal_selection` or `acceptance_validation`. The core tested path can freeze a candidate and proceed directly to `sealed_test`.

So the source-bound classification is:

**`EXECUTABLE_FREEZE_AND_SEALED_PROMOTION_NEAR_MATCH_NOT_FOUR_SURFACE`**

This is a useful negative boundary: **phase labels are not evidence of surface separation; call-path enforcement and consumption history are.**

## Secondary update — OpenETA has explicit train/review/canary/held-out evolution, but “held-out” is still an adaptive promotion surface

Source: `OpenMOSS/OpenETA` public main revision `8989fbe936109364e71b20032b8dc870df87a855`.

The `iterate` path is executable and explicit:

1. initialize an immutable generation baseline;
2. run training episodes;
3. collect and independently review candidate skills/strategies;
4. for grasp strategy, run a train-derived canary comparison;
5. run baseline and candidate on the validation manifest;
6. promote only if deterministic no-regression/objective-success conditions pass;
7. seed the accepted artifact as the next generation baseline.

This is a stronger executable lifecycle than a paper-only split description, and its generation tree retains baseline hashes, candidate manifests, baseline/candidate validation outputs, and next-generation state.

But the same validation/“held-out” manifest is queried every generation and directly determines promotion. It is therefore an **adaptive admission surface**, not OUTER. The gate is deterministic no-regression/success-count logic rather than anytime-valid statistical evidence, and no cross-candidate spending ledger was found.

The provided `parallel_libero_six_train.json` and `parallel_libero_six_holdout.json` make another important scope point: they use the same six task identities with seed 0 versus seed 1. Thus the example “held_out” is primarily **seed-level replication on repeated tasks**, not task-level generalization. The separate `parallel_libero_eval.json` also includes task identities from the same LIBERO object family, including object task 0 used in the six-task examples, so it is not source-bound as a pristine outer lockbox for the iterative run.

Source-bound classification:

**`EXECUTABLE_TRAIN_REVIEW_CANARY_HELDOUT_PROMOTION_WITHOUT_OUTER_OR_ANYTIME_STATS`**

## Design update — audit the consumption topology, not dataset labels

The executable evidence now supports a stricter rule:

> A surface is defined by how it is consumed, not by whether the code calls it `validation`, `held_out`, `sealed`, `confirm`, or `test`.

For every self-improvement surface, record at minimum:

- immutable surface/suite ID and content digest;
- declared role: EXPLORE, TUNE, CERTIFY, or OUTER;
- first query event and total query count;
- exact candidate/artifact identity evaluated;
- what aggregate/per-case information is released to the proposer;
- whether it influences promotion, rollback, routing, stopping, recovery, or checkpoint selection;
- statistical procedure and the actual sampling regime it requires;
- cross-candidate query/error spending and restart behavior;
- `outer_preterminal_query_count`, which must be exactly zero for a genuine OUTER surface.

OphAgent shows that strong physical sealing and candidate immutability can exist without a separate OUTER or anytime-valid gate. OpenETA shows that a clearly separate “held-out” manifest can still be adaptive TUNE/CERTIFY if it is reused for each generation’s admission decision.

## Source-bound artifact

Machine-readable contract:

`research_workers_clean_g1/self_improvement/surface_topology_executable_contract_2026-08-28T110405_JST_ophagent_openeta.json`

## Exact next action

Search for an executable open-source system that **combines**:

1. OphAgent-like immutable candidate identity and candidate-invisible sealed evaluation;
2. LOGOS-like candidate-local anytime-valid CERTIFY under the real sampler;
3. restart-durable cross-candidate statistical/query spending;
4. a distinct OUTER/report surface with provable `preterminal_query_count = 0`, unused by promotion, rollback, routing, stopping, recovery, or checkpoint selection;
5. complete proposal/evaluation chronology.

Prioritize systems whose tests enforce the four-surface call graph and query ledger, rather than systems that merely name four phases. Revisit LOGOS/MAAF only if public executable code appears. Frontier remains nonempty.
