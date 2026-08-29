# Phase-1 multi_agent checkpoint — rollback-domain escape without hosted coordination (Part 51)

## Frozen semantic tuple

- root: `automation_control/DESIRED_STATE.json`, control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: `automation_control/roles/multi_agent.json`, config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- preferred transport: SHA-only exact-SHA, frozen main commit `287c4c2be7c462b6b25a9ae01b073f0c794e8669`
- predecessor: `PHASE1_POLICY_REVOCATION_COMPACTION_20260830_050414_PART50.md`
- presemantic liveness witness: `automation_control/receipts/multi_agent/20260830T0536JST-presemantic-config8-dd37c4dc.json` was created and exact-read back before the first role-local semantic read.

Executable finite fixture: `research_workers_clean_g1/multi_agent/phase1_rollback_domain_escape_20260830_part51.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_rollback_domain_escape_20260830_part51.json`

## Question

Part 50 established an indistinguishability boundary when repository authority and all remembered role-local revocation state are completely rewound. Part 51 tests whether any currently CLEAN-safe, zero-cost, zero-finite-quota witness actually escapes that rollback domain without adding hosted coordination, richer-mode arbitration, protected-primary execution, or manual user action.

Candidates tested: current main, same-repository receipt chain, known later Git object by SHA, multiple same-repository refs, a genuinely independent ref domain, a monotonic floor already carried in the scheduled prompt, current branch-protection facts, an external historical-attestation oracle baseline, and fail-closed no-witness.

Adversaries include force rewind, all candidate refs rewound together, full role-local memory loss, later Git object still present or already absent, authority-name reuse, and current protection state restored after a historical gap.

## Repository/tool observations

1. The current repository exposes many refs through the read-only Git refs API, but they remain refs in the **same repository administrative/rollback domain**. Their number does not make them independent witnesses. No role-authorized separate repository/ref authority is exposed by the frozen config.
2. Read-only `GET /branches/main/protection` returned `403 Resource not accessible by integration` in this invocation. Therefore current protection details are not available to this CLEAN worker through the connected surface.
3. Read-only `GET /repos/.../rulesets` returned `403` with `Upgrade to GitHub Pro or make this repository public to enable this feature.` The current Phase-1 acceptance rules reject a paid-plan/finite-quota dependency, so this path is not an accepted escape even before historical-strength questions.
4. The connected GitHub read surfaces can fetch Git objects when a SHA is already known, but expose no operation that enumerates unreachable commits/blobs as an anti-rollback history oracle. A surviving object with a forgotten SHA is therefore not a usable witness for the full-memory-loss adversary.

## Public mechanism observations

GitHub's Git references API documents that updating a ref with `force=true` allows a non-fast-forward update; `force=false` only enforces fast-forward behavior for that update. This makes a ref a mutable pointer rather than an immutable historical witness by itself:
- https://docs.github.com/en/rest/git/refs

GitHub protected branches disable force pushes/deletion by default, but the documentation also states that force pushes can be enabled and that protections may be bypassed depending on permissions/settings. Protected branches on private repositories require GitHub Pro/Team/Enterprise-class plans:
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

Git itself explicitly distinguishes reachable from unreachable objects. `git fsck --unreachable` reports objects not reachable from refs/reflogs, and Git garbage-collection/reflog documentation permits unreachable entries/objects to expire or be pruned. Thus unreachable-object persistence is not an intrinsic permanent anti-rollback guarantee:
- https://git-scm.com/docs/git-fsck.html
- https://git-scm.com/docs/git-reflog.html
- https://git-scm.com/docs/git-gc/2.43.0

These are mechanism precedents only; no hosted Git service beyond the already-authorized lightweight repository transport is added as an accepted coordinator.

## Finite result

The fixture enumerates `1,024` rollback/loss scenario shapes and `9,216` strategy evaluations. Counts are mechanism-lattice counts, not production probabilities.

Across the full lattice:

- current main only: `512/1,024` unsafe old acceptances;
- same-repository receipt chain: `512/1,024` unsafe;
- known-SHA Git-object probe: `768/1,024` unsafe because remembered SHA and object retention are both required;
- multiple same-repository refs: `256/1,024` unsafe — useful against a *partial* ref rewind, but not a whole-repository rollback;
- genuinely independent ref witness: `768/1,024` unsafe in the generic lattice because independence plus a surviving unrewound ref are both required;
- prompt-carried monotonic floor: `512/1,024` unsafe when such a floor is absent;
- current branch-protection fact: `1,024/1,024` unsafe as historical proof because a current rule carries no monotonic head/version floor and cannot prove there was no earlier protection gap/bypass;
- external historical-attestation oracle: `512/1,024` unsafe when the oracle is absent and is not an accepted Phase-1 dependency anyway;
- fail-closed no-witness: `0/1,024` unsafe, at the cost of denying all progress when no witness survives.

The hard indistinguishable slice has 16 scenario shapes with main, receipt ref and secondary ref all rewound, role memory lost, no prompt-carried monotonic floor and no external attestation. `later_object_present`, `independent_ref_domain`, `current_protection_strict` and `authority_name_reused` vary. Every non-fail-closed candidate is `16/16` unsafe; fail-closed is `0/16` unsafe.

The important detail is the unreachable-object case: even when `later_object_present=true`, an object that cannot be named after total local-memory loss does not distinguish the two worlds through the available Chat/GitHub read surface. Its mere physical survival is not an observable anti-rollback witness.

## Acceptance / blocker

No currently exposed zero-cost, zero-finite-quota candidate is a genuine rollback-domain escape for the full adversary.

- Same-repository refs and role-local receipts are useful partial-rewind witnesses, not independent rollback domains.
- A prompt-carried dynamic monotonic floor would be outside repository rollback, but the current bootstrap prompt contains no per-artifact/policy monotonic history witness and this worker is forbidden to mutate scheduler state to add one.
- Git-object ancestry/reachability helps only while a later SHA remains nameable from surviving state/ref/prompt; full local-state loss removes that locator, and unreachable object lifetime is not a permanent guarantee.
- Current branch-protection/ruleset facts are both insufficient as historical head floors and unavailable/paid-plan-fragile on the current private-repository surface.
- An external transparency/quorum/audit service would be a stronger domain, but accepting it would violate the frozen zero-dependency rule.

Therefore the complete-authority-domain rollback boundary remains an unresolved child. The only CLEAN-safe action in that exact state is fail closed rather than resurrect old authority. This is not Phase-1 closure.

## Zero-dependency / zero-quota assessment

The fixture used scheduled-Chat reasoning, local finite computation, public documentation and role-authorized repository reads/writes only. No hosted runner, Codespaces, artifact/LFS/package service, external model/API credit, paid protection/ruleset feature, external coordinator, richer-mode arbitration, protected-primary execution or manual user action is accepted. Incremental monetary cost is zero.

## Reallocation after blocker

Per config8, this blocked leaf does not terminate the recurring objective. The next same-invocation role-safe probe is the config8 **presemantic/termination witness idempotency** leaf: determine what the new immutable lifecycle witness can and cannot prove under response loss, concurrent same-role invocations and absence of a scheduler-provided stable invocation ID. In particular, distinguish `at least one repository-reaching attempt` evidence from exactly-once invocation counting, and test random unique paths, deterministic content-addressed paths, frozen-tuple/head paths and an unavailable scheduler-ID oracle.

## Exact continuation after that probe

If the lifecycle witness can be made safe only as at-least-once attempt evidence, persist that scope explicitly and continue to the next independent multi-agent Phase-1 leaf on **overlapping same-role runs sharing one role-local LATEST CAS**: test whether immutable per-attempt checkpoints plus single-writer current-blob CAS can preserve both branches without treating a failed LATEST update as semantic loss, while remaining zero-cost and quota-independent.
