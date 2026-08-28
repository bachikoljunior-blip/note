# Primary verification — Phase-1 multi-agent parent/child generation leaf

## Frozen verification tuple

- verifier role: `primary_source_verifier`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- verifier assignment: `p1-primary-verify`
- source leaf assignment: `phase1-clean-multi-agent-concurrency-claims`
- frozen note main SHA used for semantic reads: `0ff25634a9302c4804323d1aef12e795d5b13213`
- frozen root control: revision `16`, blob `e319840755761e8aaf5c979598dd15ad6aeb79e1`
- frozen downstream control: revision `25`, blob `e14039afdb282ba5bdd0cd131eed9d65cc6216a2`
- verifier config revision: `6`
- baseline restoration blob read before semantic work: `d1b181f9f13a76578fae08038606a9a261086419`
- bootstrap two-check result: H1 = H2 = `0ff25634a9302c4804323d1aef12e795d5b13213`; `bootstrap_valid=true`

No exploration-worker state, feedback, or `DESIRED_STATE.json` was edited. The shared aggregate execution ledger was not mutated because the frozen verifier policy authorizes this role's own audit and receipt namespaces, while aggregate-ledger reconciliation is assigned elsewhere.

## Exact source/tested scope

Repository artifacts read at the frozen SHA:

1. `research_workers_clean_g1/multi_agent/LATEST.json` (blob `77a3e7fda330d9cd02bedbeaabee658ca63dac85`)
2. `research_workers_clean_g1/multi_agent/PHASE1_PARENT_CHILD_CLAIM_GENERATION_2026-08-28_220528_JST.md` (blob `5c03e2f3205ef9128c37142ac89686bf1452d8e0`)
3. `research_workers_clean_g1/multi_agent/phase1_parent_child_claim_generation_20260828_220333.py` (blob `67684a98506823e8489c01a43b5b93c1e9de7d18`)
4. `research_workers_clean_g1/multi_agent/phase1_parent_child_claim_generation_20260828_220333.json` (blob `2728febcb9c5e773db4103bda2d14cd9dafeef86`)

Public primary documentation checked:

- Kubernetes Pods / Pod generation: `https://kubernetes.io/docs/concepts/workloads/pods/`
- Kubernetes Deployment API / `observedGeneration`: `https://kubernetes.io/docs/reference/kubernetes-api/apps/deployment-v1/`
- GitHub Actions concurrency: `https://docs.github.com/en/actions/concepts/workflows-and-actions/concurrency`
- GitHub repository Contents API: `https://docs.github.com/en/rest/repos/contents`

Current Chat GitHub connector contract observed before the post-semantic head check: `update_file` replaces one UTF-8 path and requires the current blob SHA; `create_file` is create-only at a new path. This is sufficient for a single-file path-level compare-and-swap protocol, but is not a multi-file transaction or a branch-head transaction.

## Verdict

`SUPPORTED_WITH_SCOPE_CORRECTION`

The core finite-model claim is mechanically consistent with the checked script/result: each protocol has 1,184 enumerated scenarios; lease-only has 888 traces that ever terminalize, with 600 false-terminal traces and 544 duplicate-authority traces; epoch-fenced and coarse-parent protocols have zero such traces in this model. The reported lease-only ratios are arithmetically correct: `600/888 = 67.5675%` and `544/888 = 61.2613%`. The result also correctly records 816 generation rejections, 1,184 stale-epoch rejections, and 736 duplicate authoritative integration events for the enumerated grammar.

The external mechanism analogies are source-correct within their stated limits. Current Kubernetes Pod documentation says `status.observedGeneration` reflects `metadata.generation` at the point status is reported, and explicitly notes that some indirect status fields may correspond to the previous sync-loop generation. Deployment status likewise exposes the controller-observed generation. GitHub Actions documentation confirms default concurrent execution and concurrency-group restriction/queuing semantics. These are useful analogies, not proofs of the proposed multi-agent protocol.

GitHub's Contents API also supports the leaf's *single-file* canonical-manifest CAS idea: updating an existing file requires the blob `sha`, and the endpoint documents `409 Conflict`. The Chat connector exposes that same required-blob-SHA contract. This supports a one-path serialized canonical manifest. It does **not** supply atomicity across multiple files, and the worker already scopes multi-file atomicity out.

## Required scope correction: the 848 / 212 / 636 parallelism counts are pattern-level, not current-parent-generation availability counts

The checkpoint says: "Across 848 leaf traces where both children have a current completion available, only 212 satisfy both `exclusive_effect_keys disjoint` and `deterministic_merge=true`; 636 are denied..." The script does not test that generation-qualified condition.

`parallel_candidate` is computed only from whether each child's *declared completion pattern* contains the token `"current"`:

`"current" in PATTERNS[pattern_a] and "current" in PATTERNS[pattern_b]`

It does not require that those completions remain valid for the **final/current parent generation** after an inserted supersession. For example, if A completes under generation 1 and supersession to generation 2 occurs before B completes, the scenario still counts as a `parallel_candidate` even though A has no generation-2 completion available. A supersession at the end of the trace likewise leaves no generation-2 child completion, but the static candidate flag remains true whenever both patterns contain `current`.

An independent re-enumeration of the same scenario grammar, adding only the condition "both children have at least one strong completion whose generation equals the final current parent generation", gives:

- static pattern-level `parallel_candidate`: `848`
- generation-qualified both-child availability: `384`
- static pattern-level effect+merge gate admitted: `212`
- generation-qualified effect+merge gate admitted: `96`
- static pattern-level denied by overlap and/or non-deterministic merge: `636`
- generation-qualified denied by overlap and/or non-deterministic merge: `288`

The `384` generation-qualified count also matches the result artifact's `leaf_epoch_fenced.strong_terminal_at_end = 384`, which is consistent with requiring two strong current-generation canonical child slots at the end.

Therefore the correct evidence statement is: **within the enumerated declaration lattice, 848 scenarios have patterns containing a `current` completion for both children, and 212 of those also have disjoint declared effects plus deterministic merge; 636 fail at least one declaration gate.** It should not be phrased as 848 traces having two currently valid child completions for the current parent generation.

This correction does not overturn the qualitative non-substitutability claim. Epoch freshness and effect/merge declarations test different predicates. It does narrow the quantitative denominator and prevents the synthetic `636` from being interpreted as 636 observed unsafe side-effect executions: the model records structurally denied declarations, not realized merge harm.

## Additional provenance / acceptance boundary

The source leaf's own `LATEST.json` is correctly Phase-1 bound (`control_revision=16`, `config_revision=6`, correct phase/root/assignment), but it also explicitly records `chronology_valid=false` and `head_advanced_after_semantic_start=true`. Its checkpoint says newer control/config contents were not read or adopted after the leaf's semantic freeze. Those facts should remain attached to any acceptance decision; this verifier does not upgrade the leaf into a full 17-cell Phase-1 acceptance closure.

The model is a synthetic finite mechanism enumerator with a serialized integrator. It does not exercise an actual concurrent Chat run, integrator read/CAS races, crash-before-readback, cancellation acknowledgements, or multi-file atomicity. It therefore supplies protocol-counterexample evidence and implementability precedent, not an operational failure-rate estimate or an end-to-end Chat concurrency guarantee.

## Termination / exact next verification

After the above semantic work, a SHA-only postflight observation showed main had advanced to `72afe41f33496e014d4180249264fa44ccaca178`. No newer control/config content was read or adopted. Per the frozen control contract, semantic verification stops here and this checkpoint is recorded under the frozen tuple.

Exact next verification on a fresh bootstrap: do **not** repeat this static 848/212/636 leaf. If Phase-1 and `p1-primary-verify` remain active, select a different root16/config6 Phase-1 assignment-bound leaf that has actual Chat/repository execution evidence (prefer a crash/readback, cancellation, or durable-continuation case), verify its capability claim against the exact connector/repository contract, and preserve any worker-local chronology/head-drift flags instead of normalizing them away. Reopen this multi-agent leaf only if a later artifact adds generation-qualified parallel-admission counts or actual integrator CAS/crash evidence.
