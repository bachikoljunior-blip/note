# Phase-1 multi_agent checkpoint — Git Merkle accumulator/finalizer (Part 47)

## Frozen semantic tuple

- frozen authority commit: `302327074272033f246c5d8f555df61004e3802f`
- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `sha_only_exact_sha`
- predecessor: `PHASE1_ALGEBRAIC_REDESIGN_20260830_043701_PART46.md`

Part 46 found that role-local CRDT/content-addressed/escrow contributions can make some updates coordination-free, but most useful cross-role outcomes still need a reducer or completeness/current-generation proof. Part 47 asks whether Git's own content-addressed tree/commit structure can supply that finalization without a CLEAN worker reading another role's semantic state.

Executable model: `research_workers_clean_g1/multi_agent/phase1_git_merkle_accumulator_20260830_part47.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_git_merkle_accumulator_20260830_part47.json`

The finite lattice has `384` scenario shapes and `2,688` strategy evaluations over missing contribution, duplicate same content in different role namespaces, stale generation, role add/remove, publication-response loss, concurrent disjoint branch write, malicious/conflicting payload hidden behind a valid content hash, and dynamic output whose bytes are not known before execution.

## Result 1 — an opaque commit/tree SHA proves snapshot identity, not terminal semantics

Git is a content-addressable filesystem: tree objects record filenames plus blob/subtree object IDs, and commits point to a tree snapshot. That makes a commit/tree SHA a strong identity for a particular snapshot:
- https://git-scm.com/book/en/v2/Git-Internals-Git-Objects.html

But a worker that is only allowed to treat that SHA opaquely cannot derive which required roles are present, whether contributions are current-generation, whether a payload is semantically valid, or what a cross-role aggregate value is.

The required negative control, `opaque_tree_hash_as_terminal_negative`, marks the existence of an opaque tree hash as terminal. It is **false-terminal in 376/384** finite scenarios. Only eight scenario shapes have none of the modeled adverse conditions.

Therefore “the repository has a new Merkle root” is provenance/snapshot evidence, not by itself a Phase-1 completeness/semantic proof.

## Result 2 — precommitting the exact expected tree can eliminate reads only when the useful bytes are known in advance

A different mechanism can compare the final tree hash with an exact expected root hash that was sanitized/precommitted before execution. If the expected tree is exact, equality can prove those exact bytes without enumerating another role's current tree entries.

That is safe but extremely narrow. `precommitted_exact_tree_hash` terminalizes only **2/384** scenarios and false-excludes **382/384**. All **192/192** dynamic-output scenarios are unsupported because the output bytes, and therefore the final root hash, are not knowable before the run.

Whole-tree equality is also brittle to unrelated legitimate concurrent writes. It is useful for a fixed fixture or predetermined artifact, not as a generic accumulator for novel role outputs.

## Result 3 — tree inspection would answer metadata questions, but is forbidden cross-role observability here

GitHub's Trees API exposes each tree entry's path, type and object SHA:
- https://docs.github.com/en/rest/git/trees

A verifier could enumerate expected role paths and inspect their blob identities. In the model, `expected_path_tree_scan` obtains inclusion/completeness/current-generation predicates for selected cases, but **384/384** scenarios require other-role metadata reads.

The frozen `multi_agent` policy forbids other-worker state or output reads. A pathname and blob SHA for another role are still that role's output metadata for this purpose; CLEAN isolation does not become irrelevant merely because Git exposes them as a tree.

So tree scanning is not a current role-authorized way around the reducer boundary.

## Result 4 — a hypothetical sanitized Merkle proof would be a new capability, and inclusion still is not semantics

One could imagine a root-authorized endpoint returning a sanitized proof such as “all currently required role-incarnations have one contribution under generation g” without exposing raw role entries. That would be closer to a cross-role proof surface than a semantic reducer.

The current GitHub Trees documentation used here exposes tree entries, not a custom role-aware inclusion/completeness proof endpoint, and the frozen repository control does not authorize such a shared proof surface. Therefore this remains an unavailable capability, not an accepted handoff.

Even granting a perfect inclusion proof does not solve semantic correctness for unknown dynamic output. In all **192/192** dynamic-output cases, the hypothetical proof strategy still cannot certify the payload's semantics from an unknown hash alone. A content hash binds bytes; it does not prove that those bytes satisfy an application predicate unless the expected hash or a self-contained proof of that predicate is known.

## Result 5 — a semantic reducer solves more, but explicitly crosses the CLEAN boundary

`semantic_reducer_baseline` reads role paths and contents, checks missing/stale/malformed contributions, and computes a cross-role result. Unsurprisingly it can produce more terminal outcomes than an opaque hash.

But all **384/384** model scenarios require other-role metadata *and* content reads. Under the frozen role config that is a forbidden semantic input. Replacing a reducer with “a tool that does the reducer” would still introduce the unavailable shared/external executor forbidden by Phase-1.

This is the same distinction Part 46 exposed: algebraic convergence or Merkle commitment can reduce the amount of coordination needed, but a useful predicate still needs to be proved somewhere.

## Result 6 — current snapshot SHA alone does not settle lost-response history after later branch movement

In the `publication response lost + concurrent disjoint write` slice, `snapshot_commit_sha_only` leaves **96/96** cases unreconciled. If the branch has advanced past the proposed commit, simply reading the current head/tree SHA does not say whether the earlier publication was once applied.

This is the same response-loss boundary from earlier publication leaves: recovery needs a durable transition/integration identity or ancestry proof. Merkle identity of the *current* snapshot is not automatically a proof of past application history.

## What Git's Merkle structure can and cannot certify under current CLEAN isolation

Without reading other-role entries, the current worker can safely use a commit/tree SHA for:

- immutable snapshot identity;
- provenance binding to a known commit/tree;
- exact equality against a precommitted expected root when every expected byte/path was known beforehand.

It cannot generically certify:

- required-role completeness for a dynamic membership set;
- current-generation status of role-local outputs;
- semantic correctness of unknown dynamic payloads;
- a cross-role union/max/aggregate value;
- whether a lost earlier publication occurred when the branch later moved.

The current CLEAN-compatible fallback remains role-local terminal artifacts with no cross-role completion claim.

## Zero-dependency / zero-quota assessment

The tested mechanisms use repository Git object/ref APIs as transport only. No Actions, Codespaces, artifact/LFS/package storage, cloud compute, external model/API credit, richer-mode arbitration, protected-primary execution or manual user action is added. Incremental monetary cost is zero.

A custom sanitized Merkle-proof service or semantic reducer is **not** counted as solved: it is an unavailable cross-role capability and remains an unresolved child.

## Exact continuation

Next Phase-1 leaf: **self-local proof-carrying result contracts**.

Test whether each role can make its own useful output independently verifiable and terminal without any cross-role reader by comparing:

1. plain content hash negative control;
2. schema + content hash + frozen root/control tuple binding;
3. deterministic local predicate proof with explicit evidence fields;
4. a self-contained proof-carrying artifact whose verifier needs only the artifact and sanitized root/config;
5. a cross-role all-certificates verifier baseline.

Required adversaries: valid hash with wrong semantics, stale control tuple, omitted required evidence field, duplicate replay, role add, response loss, and a task whose useful outcome explicitly requires all-role completeness.

Target the largest self-certifying outcome class that is actually terminal under current CLEAN isolation. If a final verifier must enumerate other-role certificates or call an external proof service, preserve that as a new unresolved child rather than treating certificate emission as Phase-1 completion.
