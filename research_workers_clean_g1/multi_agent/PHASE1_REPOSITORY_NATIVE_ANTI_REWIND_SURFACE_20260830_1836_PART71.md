# Phase-1 multi_agent Part71 — repository-native anti-rewind surface audit

## Frozen authority
- Role: `multi_agent`
- Phase/task: `phase_1_chat_parity` / `phase1-clean-multi-agent-concurrency-claims`
- DESIRED_STATE: control revision 26, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- Role config: config revision 8, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- RUN_LIFECYCLE blob: `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- Frozen main commit: `622a09f226f800630257ed1029971ba893bb7555`
- Transport: SHA-only exact-SHA bootstrap; presemantic liveness witness persisted/read back before own-state/public semantic input.

## One bounded leaf
Continuation from Part70 asked whether a repository-native invariant, available to every scheduled Chat writer and requiring no branch/ruleset administration, secret custody, hosted compute, finite monthly quota, or user action, can remove full ref rewind / delete-recreate from the accepted concurrency threat model.

This leaf is an API-surface + adversarial-history audit, not a live destructive repository experiment.

### Public/API observations
1. GitHub Repository Contents `create or update file contents` replaces a file; updates require the **blob SHA of the file being replaced**. The same Contents-write permission also supports `Delete a file`. GitHub warns create/update and delete must be serialized because concurrent calls conflict. Source: GitHub REST Repository Contents docs, https://docs.github.com/en/rest/repos/contents (accessed 2026-08-30).
2. GitHub REST `Update a reference` exposes a `force` boolean. `force=false` requests a fast-forward update; `force=true` allows a forced update subject to repository policy. The endpoint accepts Contents-write permission. `Delete a reference` also accepts Contents-write permission. Source: GitHub REST Git References docs, https://docs.github.com/en/rest/git/refs (accessed 2026-08-30).
3. Protected-branch policy can block force pushes and deletion, but that is a protected repository-control surface outside this CLEAN worker's allowed authority. Source: GitHub protected-branch docs, https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches and REST protected-branch docs (accessed 2026-08-30).
4. Current Chat-visible GitHub write schema available to this role exposes UTF-8 file `create_file`, `update_file`, and `delete_file`; ref-update/ref-delete and branch/ruleset mutation are not exposed as worker write actions. This is a runtime capability observation, not a claim about all GitHub clients.

## Comparison fixture
| Mechanism | Stale concurrent file update | Delete/recreate old bytes | Full ref force-rewind by current Chat writer | Strong anti-rollback result in tested scope |
|---|---|---|---|---|
| Unique generation paths + mutable `CURRENT` file with blob-SHA CAS | CAS detects ordinary changed-blob races | **Fails ABA** if authority path is deleted and an exact old blob is recreated; old blob SHA is again the compare token | Ref-force write is not exposed by current Chat write schema | **No**: file incarnation is not server-fenced |
| Content-addressed generation objects + `CURRENT` CAS | Same ordinary CAS benefit | Content identity authenticates bytes, not incarnation/retirement; path can still be deleted/recreated by a Contents writer | Not exposed in current Chat write schema | **No** |
| REST ref update with `force=false` by convention | Prevents non-fast-forward while every caller obeys it | N/A at file level | Public API also exposes `force=true` and ref deletion to a Contents-write principal unless repository policy blocks it | **No API-enforced invariant for the same broad principal**; additionally not executable through the current worker write surface |
| Multi-ref expected-old / `beforeOid`-style transition set | Would strengthen atomic expected-old publication if available | Does not itself make refs undeletable or unrewindable later | No such write primitive is exposed to this role in the current connector | **Unavailable child**, not acceptance evidence |
| Protected branch/ruleset forbidding force/deletion | Server policy can fence ref rewrite/deletion | Does not make arbitrary file paths append-only, but preserves branch history against ref rewind | Yes, by protected repository policy | **Rejected for Phase-1 route** because protected/admin authority is outside the worker contract |

## Observation vs inference
- **Observation:** scheduled Chat writers in the current connector cannot directly call a ref-force or ref-delete write action because those actions are absent from the exposed write schema.
- **Observation:** the same connector does expose file deletion, so an application-level claim of an "append-only path" is not API-enforced.
- **Inference:** a blob-SHA compare is an object-content compare, not an incarnation compare. If an authoritative file is deleted and exact old bytes are later recreated, a stale client holding that old blob SHA can no longer distinguish the new incarnation from the old one using the Contents-file SHA alone. This is the concrete file-level ABA child exposed by the audit.
- **Scope guard:** this does **not** prove that GitHub itself can never provide anti-rewind policy. It proves that the currently permitted CLEAN worker write surface, without protected repository policy, does not expose a server-enforced append-only/incarnation primitive for an authoritative file.

## Result
The current Chat connector meaningfully narrows the actor model: direct Git-ref force-rewind is **not an executable scheduled-Chat write action** in this role's present tool surface. That is useful evidence against importing the broadest GitHub-client threat model unchanged.

However, that narrowing is insufficient to close rollback/ABA freshness. The accepted Contents write surface still permits deletion and recreation of authoritative paths, while file update CAS is keyed by blob SHA rather than a server-maintained incarnation/epoch. Therefore `append-only generation names`, `content-addressed objects`, and a stable pointer are protocol conventions, not a server-enforced anti-delete/anti-ABA invariant. Part70's broad complete-force-rewind fixture can be narrowed for current scheduled-Chat actors, but the distinct **delete/recreate same-content ABA** child remains unresolved.

No positive Phase-1 closure is claimed.

## Zero-dependency / quota / cost assessment
- Residual richer-mode / protected-primary / manual-user execution required for this tested audit: **none**.
- Accepted external hosted coordination: **none**.
- Finite monthly/trial/paid quota dependency added: **none**.
- Incremental monetary cost: **0**.
- Repository APIs are transport/evidence only; no hosted compute path is accepted.
- Protected branch/ruleset administration is explicitly **not** used as an accepted handoff; it remains outside the allowed route.

## Unresolved child
`file-authority ABA under delete/recreate when compare-and-swap uses only current blob SHA and no server-enforced incarnation/non-deletion token is exposed to the scheduled Chat writer.`

## Exact continuation
Execute exactly one bounded Part72 leaf on **ABA-safe file authority without ref CAS or protected policy**. Compare: (1) deterministic create-only transition witnesses keyed by `{parent_generation,next_generation,transition_id}`, (2) mutable pointer + explicit incarnation nonce, (3) content-addressed transition chain, and (4) create-only winner record + sink-time durable `applied_transition_id`. Adversarial traces must include ordinary concurrency, delete/recreate exact old bytes, stale writer retry, ambiguous create response, and replay after deletion. Determine whether create-only path conflict plus sink-time idempotency can make duplicate authoritative effects impossible even when the coordination record itself can be deleted, or whether any such positive result necessarily requires an explicit non-deletion threat assumption. Keep Phase 1 open; do not repeat Part70/71 as keepalive work and do not start a second leaf in the same invocation.
