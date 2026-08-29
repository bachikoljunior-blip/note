# Phase-1 multi_agent checkpoint — complete-rewind audit + repository-local effect reconciliation (Parts 36–37)

## Frozen semantic tuple

- role: `multi_agent`
- authority commit from SHA-only main-ref bootstrap: `64cda245ee44957f79a51b738e9bdfa549d151c4`
- sanitized root: `automation_control/DESIRED_STATE.json`, control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role config: `automation_control/roles/multi_agent.json`, config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `sha_only_exact_sha`
- predecessor own checkpoint resolved through `LATEST.json`: `PHASE1_TOMBSTONE_COMPACTION_20260829_190119_PART35.md`
- presemantic config8 liveness witness was written and exact-read back before reading own state or public sources.

The recurring Phase-1 objective remains open. No scheduler mutation was performed.

## Part 36 — anti-rollback candidate audit after a complete same-domain rewind

Part 35 left an explicit indistinguishability pair: a legitimate repository that never advanced beyond `GRANTED(g1)` and a repository that reached `CANCELLED(g1)` and was then completely restored to the exact same repository/own-state bytes. This leaf audits candidate surviving witnesses under the current CLEAN and zero-dependency/zero-quota rules.

Executable model: `research_workers_clean_g1/multi_agent/phase1_anti_rollback_20260830_part36.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_anti_rollback_20260830_part36.json`

Ten candidate classes were checked against two histories (`20` candidate-world evaluations). A candidate had to: survive the modeled complete rewind, remain discoverable without a remembered rewound identifier, be a CLEAN-admissible semantic input, have a durable contract, distinguish the two histories, require no protected/admin step, and remain valid with optional finite quotas at zero.

**Accepted candidates: 0/10.** Rejection counts by candidate were: CLEAN-admissibility `4`, rewind survival `3`, inability to distinguish the histories `3`, discoverability without remembered state `2`, durability contract `2`, zero-quota acceptance `2`, protected/admin dependency `1`.

Key cases:

- Current repository bytes and any SHA stored only in role-local repository state are erased by the modeled rewind and therefore cannot distinguish the histories.
- A dangling Git object can be addressed if its SHA is already known, but that does not solve stateless rediscovery after every remembered SHA is rewound. GitHub's troubleshooting guidance says that after a branch is deleted or force-pushed, recovery may require a collaborator that still has the commit to push it again; this is not a current-state discovery guarantee for a stateless scheduled Chat invocation.
- GitHub's repository activity view can display force-push events, but it is outside this role's CLEAN semantic-input/write contract and the public page is not a permanent anti-rollback-retention guarantee.
- Connector response URIs are not an accepted witness: the exposed interface requires a known prior response URI and provides no role-local durable enumeration contract after a stateless restart; it is also outside the configured semantic-input namespace.
- Automation runtime metadata is not in the current role's semantic-input whitelist and, even if observed, does not encode whether a particular old claim was cancelled before the rewind.
- An independent repository ref remains in the same unprotected rollback domain and can itself be moved/deleted.
- Protected branch/ruleset prevention remains disallowed as the generic Phase-1 answer because the fixed root rejects protected/admin execution dependencies and private-repository branch protection is not an unconditional zero-paid-plan property.
- An external monotonic store would distinguish histories but violates the current no-external-hosted-coordination / zero-finite-quota acceptance boundary.
- A trusted wall clock survives, but the two histories can be observed at the same time and therefore clock value alone does not prove that cancellation occurred.

Public mechanism references used in this audit:

- GitHub activity view and force-push visibility: https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/using-the-activity-view-to-see-changes-to-a-repository
- GitHub troubleshooting for commits after branch deletion/force push: https://docs.github.com/en/enterprise-server@3.17/pull-requests/how-tos/commit-changes/troubleshooting-commits
- Protected branch force-push behavior: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

### Part 36 conclusion

Within the current CLEAN input contract, **complete same-domain rewind remains an unresolved capability boundary**. The proof is information-theoretic at the tested boundary: if all admissible distinguishing state is restored to identical bytes, a deterministic stateless policy has identical observations in both histories. No rearrangement of those same rewound bytes can recover the erased fact.

This does not invalidate repository-local generation/tombstone/watermark mechanisms under the explicit no-complete-rewind assumption; it limits their scope.

## Part 37 — crash-safe repository-local `AUTHORIZED` effect reconciliation

After preserving Part 36 as an unresolved child, this invocation immediately reallocated to the next non-conflicting Phase-1 leaf as required by config8.

Executable model: `research_workers_clean_g1/multi_agent/phase1_repo_effect_reconciliation_20260830_part37.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_repo_effect_reconciliation_20260830_part37.json`

The finite lattice contains `96` scenario shapes and `528` supported strategy evaluations over:

- single canonical object vs multi-path repository effect;
- no authority change vs cancel vs supersede after an earlier read;
- unrelated branch advance;
- success-response loss;
- a later descendant commit after successful publication;
- whether an old target marker remains observable.

Compared strategies:

1. separate authority precheck + target write + blind retry;
2. separate authority precheck + target transition marker + fail closed if the marker is missing;
3. co-located single-object CAS with `applied_transition_id` / monotonic applied-through state;
4. multi-path Git tree/commit publication + `update_ref(force=false)` + ancestry reconciliation;
5. the same Git-ref publication but exact-SHA-only response-loss reconciliation followed by retry;
6. fail closed on every ambiguous response.

### Result 1 — a separate precheck is not a publication fence

In all `64` scenarios where cancellation or supersession occurs after the authority read but before the separate target write, both separate-file strategies produce **64/64 stale-authority publications**, even when the target contains a transition marker. The marker helps identify what happened after a crash; it does not make the authority check and effect publication atomic.

The blind-retry variant also creates `16` duplicate logical publication attempts in response-loss/current-authority scenarios.

### Result 2 — co-locate single-key repository authority and canonical effect when possible

For the `48` single-object scenarios, one current-blob CAS that changes `AUTHORIZED(t)` to `APPLIED(t,payload)` has **0 stale publications and 0 duplicates**. Cancel/supersede changes the same blob first, so the old blob SHA no longer matches and the stale transition remains pending rather than publishing. All `8` supported response-loss cases with unchanged authority are reconciled by reading the current transition identity / applied-through field.

GitHub's Contents API requires the current blob `sha` when updating a file, returns `409 Conflict` on conflicts, and documents that conflicting contents operations should be serialized:
https://docs.github.com/en/rest/repos/contents

This positive result is scoped to a canonical effect that can be represented in the same authority object. It is not a claim of arbitrary cross-file atomicity.

### Result 3 — multi-path publication can use one branch-ref publication boundary, but it is coarse

For multi-path repository effects, the exposed GitHub connector has `create_tree`, `create_commit`, `update_ref(force=false)` and commit comparison support. GitHub documents that a created tree must be committed and the branch ref updated before it becomes branch state; `force=false` requires a fast-forward update and can return `409 Conflict`:

- https://docs.github.com/en/rest/git/trees
- https://docs.github.com/en/rest/git/refs
- https://docs.github.com/en/rest/commits/commits#compare-two-commits

In the model, `git_ref_fast_forward_with_ancestry` has **0 stale publications and 0 duplicate integrations across all 96 scenarios**. Any cancel/supersede commit based on the same branch makes the old proposal a sibling, so its non-force ref update fails rather than overwriting current authority.

The cost is coarse invalidation: `16` unrelated-advance scenarios conflict even though authority itself did not change. They are retry/revalidation work, not unsafe writes.

### Result 4 — exact ref equality is insufficient after response loss

If proposal commit `P` was published, the response was lost, and a later legitimate commit becomes a descendant of `P`, current ref equality (`HEAD == P`) is false even though `P` did apply. The exact-SHA-only retry strategy created `4` duplicate logical integrations in that slice. An ancestry/compare check or a persistent transition identity is therefore required before retry.

This result inherits Part 36's limit: complete same-domain force rewind can erase the current ancestry path and is not solved by this leaf.

## Phase-1 acceptance / dependency assessment

Accepted within tested scopes:

- **Single canonical repository effect:** co-located authority/effect current-blob CAS + durable transition identity. No richer-mode/manual/protected step, no hosted coordinator, no optional monthly/trial/paid quota, zero incremental monetary cost. Repository API rate limits are treated as checkpoint/backoff interruptions, not compute.
- **Multi-path same-branch repository publication under no-complete-rewind/cooperative non-force writers:** tree + commit + `update_ref(force=false)` + ancestry/transition reconciliation. Same zero-dependency / zero-finite-quota / zero-incremental-cost assessment.

Still unresolved:

1. complete same-domain repository/own-state rewind with no surviving admissible monotonic witness;
2. arbitrary external/protected sink effects that cannot atomically validate repository authority or provide durable idempotent status;
3. branch-wide false conflicts for multi-path Git-ref publication under a busy full recurring-Chat pool.

Global Phase-1 closure is not claimed.

## Exact continuation

Next Phase-1 leaf: **immutable staging + manifest-gated publication to reduce branch-wide false conflicts without losing multi-path atomic visibility**.

Test, in a finite lattice:

- unique immutable stage writes before authority publication;
- one current-blob manifest CAS per conflict domain carrying parent generation, claim/integrator epoch, effect-set digest and `applied_transition_id`;
- crash before/after manifest CAS and lost responses;
- concurrent disjoint vs overlapping effects;
- stale takeover/cancel between stage and manifest publication;
- unreferenced-stage GC;
- direct fixed-path readers that bypass the manifest as a required negative control;
- comparison against global Git-ref publication and fail-closed serialization.

The main question is whether manifest-gated staging preserves the strong single-object fencing proof while avoiding unrelated branch-ref conflicts. If legacy/direct readers cannot be made manifest-aware, preserve that as a separate unresolved consumer-contract child rather than claiming parity.
