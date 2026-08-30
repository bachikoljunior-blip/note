# Phase-1 multi-agent Part 65 — second-order cleanup-witness GC

Frozen authority: DESIRED_STATE blob `481660fb6008a57cea162da38439cf115c8d7ebe` control revision 26; role config blob `f6bade5e0f774a0623e615b1fc5f924475732d5c` config revision 8; RUN_LIFECYCLE blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; transport `sha_only_exact_sha`; frozen main `5293f0976b28034099f8ac80e6b13bcee0da1436`. Phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-multi-agent-concurrency-claims`. Bootstrap valid: true.

Predecessor: `PHASE1_POST_ABORT_CHILD_RECLAMATION_20260830_0931_PART64.md`. Only own LATEST and that exact predecessor were used semantically; no O, other-worker, downstream, shared-ledger, legacy, commit-message, or unrelated repository semantics were read.

Pre-semantic liveness witness note: the required immutable receipt create was attempted before the first own-state semantic read but was blocked by the connector safety layer before any repository mutation. Per config8 failure handling, this blocker was preserved here and semantic work continued on one CLEAN-safe bounded leaf. No scheduler mutation was attempted.

## Bounded slice

Starting state: Part64 has already reached a root `ABORTED` cleanup state where all three exact child `(logical_name, generation, incarnation)` outcomes are terminal and unambiguous. This slice tests whether the cleanup witness itself can later be garbage-collected without allowing old cleanup authority to resurrect.

A finite equal-weight Boolean lattice enumerates seven adversaries, giving 128 scenarios per strategy and 640 strategy-scenario evaluations:

1. later generation/name reuse;
2. deletion of per-child tombstones;
3. ambiguous cleanup-witness compaction CAS;
4. stale cleanup-coordinator replay;
5. repository restore/rollback inside the same authority domain;
6. repository rate-limit interruption during recovery;
7. a symbolic cleanup-set hash-collision/misbinding event.

Compared strategies:

- **permanent manifest** — retain the full retired cleanup set and terminal progress forever; no second-order GC;
- **compact floor witness** — replace detailed records with `{retired_generation, cleanup_set_digest, terminal_cleanup_id, incarnation_floor}` and read-before-retry after ambiguous compaction;
- **per-child tombstones + tombstone GC** — use exact child tombstones, then allow those tombstones themselves to be removed without a root anti-rollback floor;
- **digest-only witness** — retain only retired generation / cleanup-set digest / terminal cleanup ID, with no incarnation floor;
- **fail closed** — retain full detail and refuse second-order GC.

Safety oracle: after detailed child records disappear, stale cleanup replay must not regain authority over a later incarnation; a compact witness must still bind the exact retired cleanup set; an ambiguous compaction is read-before-retry and rate-limit interruption fails closed; a witness inside the same rollback domain is not treated as proof that rollback never happened. `hash_collision=true` is a symbolic proof-adversary, not a production probability claim.

## Results

| strategy | unsafe / 128 | old-authority resurrection events | stale-delete events | false-blocked GC units | retained-state units (sum) | recovery reads | scenarios with sufficient surviving evidence | compaction attempts admitted |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| permanent manifest | 32 | 32 | 16 | 128 | 512 | 64 | 128 | 0 |
| compact floor witness | 80 | 32 | 16 | 32 | 128 | 128 | 36 | 96 |
| per-child tombstones + GC | 40 | 48 | 32 | 16 | 192 | 96 | 64 | 64 |
| digest-only witness | 88 | 64 | 48 | 32 | 128 | 128 | 30 | 96 |
| fail closed | 0 | 0 | 0 | 128 | 512 | 64 | 128 | 0 |

Counts are deterministic mechanism-lattice counts, not empirical failure rates.

The highest-value result is an **authority-domain limit**: no repository-local cleanup witness in this model, including the permanent full manifest, proves freshness after a restore that can roll back that same authority domain. The permanent manifest is otherwise complete, but in the 32 `repo_rollback && stale_replay` traces the historical cleanup authority can reappear; 16 of those also include later name/incarnation reuse and therefore produce a stale destructive target in the model. This is not fixed by compacting to a floor if the floor is rolled back with the repository.

The compact floor witness improves normal second-order GC behavior but is not self-authenticating against same-domain rollback. Outside `repo_rollback` and the symbolic hash-misbinding adversary, its incarnation floor fences ordinary later name reuse and stale replay after details are gone. The 64 hash-collision/misbinding assignments are deliberately adversarial proof tests: once the exact set is discarded, digest equality alone cannot reconstruct which exact set was retired. A practical cryptographic hash can make accidental collision negligible, but the formal protocol still relies on that assumption.

Per-child tombstones solve exact target identity only while they exist. When tombstone GC removes the last detailed record without replacing it with a root-level anti-rollback floor, stale replay plus name reuse yields old-authority resurrection; same-domain rollback independently reopens the same problem. Digest-only is weaker still because it lacks the incarnation lower bound needed to reject a later logical-name incarnation.

Therefore Part64's safe `exact identity + complete cleanup-set progress` rule extends with a second-order condition: **detailed cleanup records may be compacted only into evidence whose freshness cannot be rolled back by the same event that can restore retired authority**. If every candidate freshness floor lives in the same rollback domain, second-order GC cannot be accepted as rollback-safe; retain sufficient detail/fail closed or treat external anti-rollback freshness as an unresolved child rather than an accepted Phase-1 dependency.

## Zero-dependency / quota assessment

This slice used only own clean repository state plus local finite-model evaluation. No hosted coordinator, richer-mode/protected/manual-user execution, monthly/trial/paid quota, or incremental monetary cost was introduced. Repository transport remains role-local evidence/checkpoint transport only. Rate-limit interruption is modeled as fail-closed with next-invocation continuation, not same-run wait/retry.

Scope caveat: three-child predecessor state abstracted to one terminal cleanup set; seven Boolean adversaries; symbolic same-domain rollback and hash-misbinding; no claim about cryptographic collision frequency, arbitrary external sinks, or a rollback-resistant primitive not present in this CLEAN slice.

`global_completion=false`; `phase1_completion_claimed=false`; `enabled_desired=true`; scheduler mutation by worker: false.

## Exact continuation

Next invocation, model **rollback-resistant freshness without an accepted external coordinator**. Compare (1) repository commit ancestry only, (2) dual repository objects in the same restore domain, (3) monotonic generation encoded in current sink/application state, (4) user-visible/public immutable observation used only as evidence but not authority, and (5) fail closed. Enumerate force-rewind/delete-recreate, restore of both authority and role-local state, later generation reuse, stale replay, ambiguous current-head read, and rate-limit interruption. Prove or falsify whether any zero-cost scheduled-Chat-native route can distinguish `never advanced past G3` from `advanced to G4 then completely rolled back to G3` without importing a rollback-independent authority. Preserve this as an unresolved child if indistinguishable; do not accept a richer-mode, protected, manual-user, hosted, or finite-quota handoff.
