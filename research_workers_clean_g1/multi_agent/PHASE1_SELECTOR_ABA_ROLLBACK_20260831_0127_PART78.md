# Phase-1 multi-agent Part78 — selector-object ABA / rollback

## Frozen authority
- DESIRED_STATE: `automation_control/DESIRED_STATE.json`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`, control revision 26.
- Role config: `automation_control/roles/multi_agent.json`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`, config revision 8.
- RUN_LIFECYCLE blob: `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`.
- INSTRUCTION_CONTROL_MANIFEST blob: `f33de8209ada96ea0e2e1f3237b21a3cc555a242`.
- Transport: preferred SHA-only exact-main freeze at `15d898233a1d14f21561f762bc6d3f003ce55289` before the first role-local semantic read.
- Bootstrap valid: true. Phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-multi-agent-concurrency-claims`.

## Lifecycle witness diagnostic
The required presemantic immutable receipt write was attempted before the first own-state/public semantic read, but the connector call was blocked by the platform safety layer. No same-run retry was attempted. The semantic tuple above was then frozen and the role-local `LATEST.json` was read once, selecting its exact Part78 continuation. This checkpoint records that write-surface blocker without claiming the presemantic witness succeeded.

## Bounded finite grammar
Exactly one bounded leaf was executed. A 64-trace equal-weight finite grammar crossed:
- restore mode: `delete_recreate_identical`, `ref_rewind_old_commit`, `selective_restore_old_selector`, `no_restore`;
- selector response: `ack`, `ambiguous`;
- proposal identity: `deterministic_reused`, `unique_per_attempt`;
- writer: `stale_pre_restore`, `fresh_post_restore`;
- prior external effect: `applied`, `not_applied`.

Five mechanisms were evaluated mechanically:
1. selector Contents-CAS keyed only by the current selector blob SHA;
2. a monotonic epoch embedded only in the selector / same rollback domain;
3. a create-only deterministic marker stored in the same rollback domain;
4. Git-ref publication with `force=false` / fast-forward fencing;
5. an ideal independent non-rollback witness, used only as a falsification control because it introduces an authority domain that is not available under the current zero-external-coordinator acceptance rule.

Metrics count only this finite grammar and are not production failure rates. `stale_aba` means a stale pre-restore writer is admitted again after rollback/recreation. `duplicate` is the narrower ambiguous-response + prior-effect-applied subset where that stale admission can replay a logical effect. `false_block` counts fresh post-restore, no-prior-effect traces rejected by the independent-witness fail-closed control.

| mechanism | accepted / 64 | stale_aba / 64 | duplicate / 64 | false_block / 64 |
| --- | ---: | ---: | ---: | ---: |
| blob SHA only | 56 | 24 | 6 | 0 |
| same-domain embedded epoch | 56 | 24 | 6 | 0 |
| same-domain deterministic marker | 56 | 24 | 6 | 0 |
| ref fast-forward fence | 48 | 16 | 4 | 0 |
| independent non-rollback witness control | 8 | 0 | 0 | 12 |

## Result
The Part77 open falsification is confirmed in the modeled scope: **content identity and same-domain monotonic metadata do not provide anti-rollback identity when the authority domain itself can be restored to an older state.** Delete+recreate of identical selector content and exact ref rewind both make the old selector state current again, so a stale writer holding the pre-restore identity can satisfy the same compare. Embedding an epoch or deterministic transition marker in that same rollback domain does not help when the restore also reinstates the old epoch/marker state.

A non-force Git ref update is strictly stronger than file-blob comparison for a selective old-file restore under an otherwise newer branch head: the stale proposal is not a fast-forward of that newer head in this model. It still does **not** fence an exact branch rewind to the stale writer's old base; after that rewind the stale proposal can again be a valid fast-forward. Therefore branch-head fast-forward is an optimistic concurrency primitive, not a history-nonreusability proof across authorized/possible ref rollback.

The only zero-`stale_aba` control in this grammar is a witness that survives selector/ref rollback and cannot be reset to the old value. Under the current Phase-1 acceptance contract, treating a separate hosted coordinator or manual/protected branch-control step as that witness is not acceptable. This leaves a precise unresolved child rather than a handoff: **find a scheduled-Chat-native, zero-cost, zero-finite-quota, non-reusable incarnation witness that is not rolled back with the selector and requires no richer-mode/protected/manual execution.**

## Public-source qualification
- GitHub REST Git references documentation, retrieved 2026-08-31: `force=false` on update-reference is documented to require a fast-forward update and the endpoint documents `409 Conflict`. Source: https://docs.github.com/en/rest/git/refs
- The immediately preceding own Part77 checkpoint already qualified GitHub Contents update semantics: updating a file uses the current file `sha`, and conflicting contents operations can conflict. Source retained from role-local clean state: https://docs.github.com/en/rest/repos/contents

These public API facts support only the mechanism boundaries above; the ABA counts come from the finite grammar, not from GitHub production telemetry.

## Scope / acceptance guards
- Observation: same-domain state restored to an old value can make a previously valid compare value current again in the finite model.
- Inference: no state variable wholly contained in the same fully rollbackable authority domain can distinguish `old state was always current` from `newer state existed and was then fully restored` after all external memory of the newer state is removed. This is an indistinguishability claim for the modeled state boundary, not a universal impossibility theorem for systems with independent durable witnesses.
- Residual richer-mode / protected-primary / manual-user execution dependency on the tested repository-only mechanisms: none added.
- Finite monthly/trial/paid quota dependency added: none. Lightweight repository/public-doc access only; no hosted runner, Codespaces, artifact/LFS/package, cloud compute, paid API/model credit, or external coordinator was consumed.
- Incremental monetary cost: 0.
- External hosted coordination accepted: no.
- Rate-limit behavior: fail closed and checkpoint for a later scheduled invocation; no same-run waiting/backoff/retry.
- Global completion: false. Phase-1 completion claimed: false. `enabled_desired`: true. Scheduler mutation by worker: false.

## Nonempty frontier and exact continuation
**Part79:** execute exactly one bounded leaf on rollback-domain separation without accepting an external coordinator. Compare (a) selector plus second Git ref in the same repository, (b) selector plus immutable commit/tag object reachable only by stored SHA, (c) repository issue/release-style monotonic IDs as a *forbidden-dependency diagnostic control only*, and (d) fail-closed generation reset with deterministic re-derivation from irreversible effect IDs. Enumerate full-main rewind, selective selector restore, ref/tag deletion+recreate, loss of the only stored witness SHA, and stateless next-invocation reconstruction. Falsify any candidate whose witness disappears or can be reused under full repository rollback; separately record whether the only surviving candidate violates the no-external-hosted-coordinator / no-manual-protected-execution acceptance gate. Do not start this leaf in the current invocation.

Termination for this invocation remains `bounded_slice_complete_recurring_open`; this checkpoint is not semantic completion.
