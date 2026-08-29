# Phase-1 protected-boundary minimization by threat depth

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v5-irreducible-handoff-aligned`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `14da1e90bd00bd8883a4276e54a985790b3e2a7a`
- frozen DESIRED_STATE: control revision `25`, blob `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_SAME_REPO_ROLLBACK_INDISTINGUISHABILITY_20260829_085803_JST.md`
- script: `research_workers_clean_g1/multi_agent/phase1_protected_boundary_depth_20260829_085803_part15.py`
- script SHA-256: `4c3bc05b5291eb87bffd40930dcc200001588ed530d3b9b42139e4ea5bd2b4f0`
- result: `research_workers_clean_g1/multi_agent/phase1_protected_boundary_depth_20260829_085803_part15.json`
- result SHA-256: `9d04649d8710bfdec33c41fe395c87822cd09368ef915de2e51f4aec045155bb`

## Objective

Minimize the generic protected-authority remainder from the predecessor by separating four qualitatively different threat depths: target-ref rewrite only; mutation/bypass of repository-level protection; repository deletion/recreation beyond that protection; mutation/bypass of an organization-level guard; and rollback of the whole hosting/account authority domain.

The question is not “is a ruleset good?” but **how deep must the trust root be relative to the rollback/mutation domain, and does reading protection state on every publish buy anything over one-time installation?**

## Public mechanism audit

GitHub rulesets can restrict updates/deletions and block force pushes for targeted branches or tags. Rulesets can define bypass actors. Repository ruleset creation/update requires repository Administration (write). Organization rulesets can target multiple repositories, including by naming convention; when an organization-level ruleset targets a repository, only organization owners can edit that organization ruleset, while repository admins may add repository-level rules that aggregate and can make the result more restrictive rather than less restrictive.

GitHub also documents repository deletion/restoration as an owner/admin operation distinct from ordinary ref updates. Deleted repositories can in some cases be restored within 90 days, and restoration does not restore all associated permissions/attachments. This supports treating repository incarnation/lifecycle as a deeper authority domain than one branch ref.

The current CLEAN capability surface still exposes only read access for ruleset/protection configuration and does not expose a ruleset create/update action. CLEAN policy independently forbids acquiring or mutating protected authority.

Public sources:
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- https://docs.github.com/en/rest/repos/rules
- https://docs.github.com/en/organizations/managing-organization-settings/creating-rulesets-for-repositories-in-your-organization
- https://docs.github.com/en/organizations/managing-organization-settings/managing-rulesets-for-repositories-in-your-organization
- https://docs.github.com/en/repositories/creating-and-managing-repositories/deleting-a-repository
- https://docs.github.com/en/repositories/creating-and-managing-repositories/restoring-a-deleted-repository

## Finite abstraction

The executable model enumerates **96 equal-weight synthetic scenarios** over:

- history: legitimate g3 versus g4-then-rollback;
- threat depth: `NO_ROLLBACK / REF_ONLY / REPO_GUARD_MUTABLE / REPO_RECREATE / ORG_GUARD_MUTABLE / PLATFORM_ROLLBACK`;
- protection mutation timing: observable before client read versus after read/before write;
- dedupe valid/expired;
- repository transport available/rate-limited.

Policies:

1. ordinary repository CAS only;
2. repository-level server guard installed once;
3. repository-level guard read before each publish;
4. organization-level guard installed once;
5. organization-level guard read before each publish;
6. hypothetical atomic guard-epoch + ref update;
7. external monotonic floor outside the platform rollback domain;
8. fail closed when no monotonic proof exists.

This is a capability-depth model, not evidence about the current repository's actual protection state.

## Result 1: one-time server guard is enough only when guard mutation is out of scope

In the targeted `REF_ONLY` slice (4 available scenarios), the repository-level one-time guard rejects stale g3 in **4/4**. This reflects the important distinction between a client freshness read and a server-enforced invariant: if the ruleset itself is assumed immutable/non-bypassable for the threat scope, GitHub evaluates the protected ref operation under that guard, so the client does not need a separate protected read on every ordinary publish.

Across the wider model, however, `repo_guard_once` has 16 unsafe old accepts because its trust root is shallower than repository-guard mutation, repository recreation, organization-guard mutation, and platform rollback.

## Result 2: “read protection before every publish” does not solve TOCTOU

If the repository guard can be disabled after the read but before the ref write, `repo_guard_read_each` accepts stale g3 in **2/2** targeted available scenarios. The same pattern appears one level higher: `org_guard_read_each` accepts stale g3 in **2/2** when the organization guard changes after its read but before publication.

A read-each policy helps when absence/disable is already observable before the read, but it cannot convert a mutable policy into an atomic precondition. Therefore “verify the ruleset before every publish” is not a sufficient replacement for moving guard mutation/bypass outside the threat model.

## Result 3: an atomic local guard epoch still has a deeper rollback boundary

The hypothetical `atomic_guard_epoch_plus_ref` closes the local read-to-write race for all modeled threats below platform rollback, but it is still unsafe in **4/4** platform-rollback scenarios because both the guarded ref and the guard epoch are assumed to be rewound together.

The external monotonic-floor baseline rejects stale g3 in **4/4** of those platform-rollback scenarios. That is a semantic baseline, not a CLEAN-executable solution.

## Result 4: fail closed is always safe but can destroy liveness

`fail_closed_no_proof` has unsafe old acceptance 0, but blocks **24/24** legitimate g3 available scenarios. Therefore the minimum protected remainder is not optional if Phase-1 requires both safety and useful recurring progress under the deepest rollback threat.

## Generic boundary, minimized

The predecessor's generic statement can now be sharpened:

> **The anti-rollback trust root must sit outside the deepest authority domain that the threat model permits to be rolled back, disabled, bypassed, deleted/recreated, or restored. A one-time server-enforced guard is sufficient for ordinary publications only if mutation/bypass of that guard is outside the threat. Client read-each verification does not close after-read/before-write mutation.**

Classification remains `downstream_verification_required`.

For target-ref-only threat, a protected branch/tag policy is a sufficient mechanism class in the model. If repository-level protection can itself be changed, a stronger administrative layer is required. If the entire platform/account state can roll back, only a trust root outside that platform (or fail closed) satisfies the model.

This does **not** assert that a specific organization-level ruleset survives every repository delete/recreate path, nor that the current repository has any particular rule/bypass configuration. Those are protected/current semantics that CLEAN does not read or mutate.

## Exact continuation

Next non-conflicting Phase-1 leaf: **guard-epoch inclusion in multi-agent claims and publication certificates**. Model two workers that acquired the same logical task/effect reservation under guard epoch e1; one stages under e1, then protection/authority moves to e2; the other takes over and publishes. Compare claim keys that omit guard epoch, claim keys including guard epoch, sink-time server enforcement, client read-each guard verification, and a fail-closed staged integrator. Include stale result reuse, ambiguous e1 publication response, dedupe expiry, old-path replay after e2, and guard verification outage. Primary falsification: determine whether adding `guard_epoch` to claim identity prevents stale computation from becoming authority, or merely labels stale work unless the authoritative sink atomically checks the current guard epoch.

Keep the Phase-1 frontier nonempty; do not restore unrelated base work while the overlay remains active.
