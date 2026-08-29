# Phase-1 same-repository rollback indistinguishability and minimum protected boundary

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- transport_mode: `sha_only_exact_sha`
- frozen semantic main SHA: `14da1e90bd00bd8883a4276e54a985790b3e2a7a`
- frozen DESIRED_STATE: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_ANTI_ROLLBACK_KEY_ROTATION_MULTIPATH_20260829_080052_JST.md`
- script: `research_workers_clean_g1/multi_agent/phase1_same_repo_rollback_indistinguishability_20260829_085803.py`
- script SHA-256: `0d9e2d3bc747aaace0a0738187e5f96be4ddb2cdc7ef2d9efd809fddbc36e4ed`
- result: `research_workers_clean_g1/multi_agent/phase1_same_repo_rollback_indistinguishability_20260829_085803.json`
- result SHA-256: `32672dbeaed6d92a67a141d490e90f0fcc74143c075e19bd5912be3f707278e4`

## Why this leaf changed under control 25

The predecessor under control 24 treated any remaining protected/richer capability as a leaf failure. Control 25 instead requires CLEAN to execute all safely available Chat-capable predecessors, then record the **minimum generic protected-authority-only remainder** as `downstream_verification_required`. This leaf therefore does not try to manufacture a same-domain anti-rollback proof after the information has been erased. It tests whether such a proof is possible, completes the current Chat-capable model/public audit, and narrows the residual capability boundary.

## Public mechanism audit

GitHub documents Git references as rewritable pointers. Its REST ref update accepts a target SHA and a `force` boolean; `force=false` only requires a fast-forward update, while `force=true` can rewrite the ref. This makes a ref a useful publication pointer, but not by itself a permanent anti-rollback witness.

GitHub branch protections/rulesets can block force pushes, restrict updates, and restrict deletions on targeted branches/tags. Rulesets can also have bypass actors. Creating or updating a repository ruleset requires repository **Administration (write)** permission. In the currently exposed scheduled-Chat capability surface, ruleset/protection access is read-only; no ruleset mutation action is exposed. Separately, this CLEAN role is forbidden from acquiring or mutating protected authority. Therefore installing or changing such a guard is not a safely Chat-capable role-local effect in this run.

Git's own reflog/object model is also not a permanent same-domain witness: reflog entries can expire and unreachable objects can be pruned. A hidden commit SHA may help recovery while retained and known, but the model must not equate “Git object once existed” with a durable monotonic freshness floor after all current pointers and remembered SHAs are rewound/lost.

Public sources:
- https://docs.github.com/en/rest/git/refs
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository
- https://docs.github.com/en/rest/repos/rules
- https://git-scm.com/docs/git-reflog
- https://git-scm.com/docs/git-prune

## Finite model

The executable model enumerates **3,456 equal-weight synthetic scenarios** over:

- transition history: `NEVER_V4 / V4_CONFIRMED_THEN_ROLLBACK / V4_AMBIG_APPLIED_THEN_ROLLBACK / V4_AMBIG_NOT_APPLIED`;
- authority ref: `CURRENT / FORCE_REWOUND / DELETE_RECREATE / DIVERGENT_SIBLING`;
- immutable version surface: `V4_VISIBLE / V4_OBJECT_HIDDEN / V4_LOST`;
- `LATEST`: `CURRENT / STALE / MISSING`;
- v4 SHA witness: `PRESERVED_IN_CURRENT_REPO / LOST_WITH_ROLLBACK`;
- same-repository alternate ref: `V4_PINNED / REWOUND_V3 / MISSING`;
- dedupe: `VALID / EXPIRED`;
- repository transport: `AVAILABLE / RATE_LIMITED`.

There are 1,728 available-transport and 1,728 rate-limited scenarios. Counts are mechanism counts, not production probabilities.

Policies compared:

1. `current_pointer_only`;
2. `same_branch_append_only`;
3. `same_domain_sha_chain`;
4. `same_repo_alt_ref`;
5. `combined_same_repo` (accept the maximum surviving witness among current branch/version/SHA/alternate ref);
6. `same_object_tombstone` (a permanent marker that is nevertheless stored in the same rewound authority object);
7. `fail_closed_without_monotonic_proof`;
8. `protected_monotonic_floor` as a semantic baseline whose freshness witness is outside the rollback domain.

## Aggregate result

For available transport, `current_pointer_only` accepts stale g3 in **648** true-floor-v4 scenarios and creates **324** duplicate external effects when dedupe has expired. A same-branch append-only file, same-domain SHA chain, or separate same-repository ref each reduce unsafe acceptance to **432**, but do not eliminate it. Combining all surviving same-repository surfaces reduces unsafe acceptance further to **216** and duplicate external effects to **108**.

The remaining 216 are decisive: they are the **full same-domain erasure** slice in which main now shows g3, no v4 file is visible, no v4 SHA remains in current repository state, and no alternate ref still pins v4. Every same-domain strategy—including `combined_same_repo` and a tombstone stored in the rewound authority object—accepts g3 in **216/216** and is unsafe. A tombstone does not become anti-rollback merely by being called permanent if the storage domain containing it can be rolled back.

`fail_closed_without_monotonic_proof` has unsafe acceptance 0, but it blocks **864/864** legitimate true-floor-g3 available scenarios. The protected monotonic-floor baseline has unsafe acceptance 0 and false block 0 in the modeled scope, but its authority is intentionally outside the worker-controlled rollback domain.

All 1,728 rate-limited scenarios checkpoint instead of weakening authority.

## Indistinguishability result

The model maps each scenario to the observation available to a stateless recovery worker: current main generation, whether a visible v4 artifact exists, whether a v4 SHA is currently known, whether an alternate ref currently pins v4, current `LATEST` generation, dedupe state, and transport state.

Across 192 distinct observation classes, **12 classes contain both true-floor-3 and true-floor-4 histories**, covering **2,160 scenario members**. In the full-erasure slice, 216 rolled-back true-floor-v4 scenarios collapse into just six observation classes that also exist in the never-v4 world.

Therefore any deterministic recovery rule restricted to those same-domain observations must make the same decision for the paired histories. If it accepts g3, it preserves liveness in the never-v4 history but is unsafe after v4 was erased. If it rejects g3, it is safe after rollback but falsely blocks the indistinguishable never-v4 history. This is an information-loss result, not a weakness of a particular CAS syntax.

## What same-repository anchors can and cannot do

A same-repository alternate ref/tag is useful against **partial** rollback when it survives independently of the rewritten main ref. The model demonstrates that explicitly: preserving any one of the v4 version file, known v4 SHA, or v4-pinned alternate ref removes many unsafe cases. But a second ref is not a proof against a rollback operation capable of rewriting/deleting both refs, and a commit SHA stored only in files that are themselves rolled back is not an outside-domain witness.

A protected branch/tag ruleset can change the problem from recovery-after-rollback to prevention-of-rollback for its exact protected ref scope. GitHub publicly supports blocking force pushes and restricting updates/deletions. However the protection policy and its bypass/removal authority are a separate authority domain. This CLEAN role neither has an exposed ruleset mutation capability nor authorization under its role policy to mutate protected authority.

## Minimum generic remaining capability boundary

All safely Chat-capable predecessors selected for this leaf are complete: source audit, finite counterexample model, same-domain alternatives, rate-limit behavior, executable evidence, and durable continuation.

The smallest remaining capability is therefore recorded as:

> **Provide a monotonic authority/freshness witness outside the rollback domain, OR prevent rewind/delete/recreate of the authority ref with protected policy whose bypass/removal authority is itself outside the worker-controlled rollback domain.**

Classification: `downstream_verification_required`.

This is deliberately generic. CLEAN does not decide whether a particular protected ruleset, organization/enterprise policy, platform audit witness, or other protected surface is truly irreducible or sufficient globally. It also does not claim Phase-1 global closure.

## Exact scope limits

The positive `protected_monotonic_floor` baseline is synthetic: it assumes its floor cannot be rolled back with the repository authority. The public GitHub ruleset discussion only proves that GitHub has mechanisms capable of blocking ref force pushes/updates/deletions; it does not prove that the current repository has the required rule, has no bypass path, or is protected against all repository-level restore/delete scenarios.

The model also does not claim that GitHub retains unreachable objects forever. Hidden-object recovery is treated as opportunistic unless a current, source-qualified witness still identifies the object.

## Next Phase-1 leaf

Continue with **protected-boundary minimization by threat scope**, without reading protected repository semantics: distinguish `(A)` target-ref force/update/delete only, `(B)` ruleset mutation/bypass, `(C)` whole-repository delete/recreate or restore, and `(D)` platform/account rollback. Compare the weakest generic authority surface that is sufficient for each scope and test whether a one-time protected guard plus ordinary role-local CAS thereafter is enough, or whether every publication requires a protected freshness read. Include bypass-list changes, ruleset disable/reenable, alternate-ref protection, repository identity reincarnation, fail-closed verification outage, and two concurrent old-path retries. Preserve the current result as the lower-bound impossibility proof for all mechanisms whose entire persistent state is rewound together.

Keep the Phase-1 frontier nonempty; do not resume unrelated base work while the overlay remains active.
