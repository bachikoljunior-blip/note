# Phase-1 authority-domain atomicity and recovery stress test

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- invocation start observed: `2026-08-29T00:02:29+09:00`
- checkpoint packaging clock observation: `2026-08-29T00:09:15+09:00`
- chronology_valid: `true`
- frozen note main SHA: `ee248ff4464d0950316452847ac5ddbafd17f966`
- frozen root control revision: `18`
- frozen role config revision: `6`
- frozen role config blob: `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- control_change_after_semantic_start: `true`
- newer observed note main SHA after semantic start: `cb36dd38845ea8483934d2503287abd90bc45b76`
- newer control/config contents were not read or adopted after the semantic freeze barrier.
- semantic inputs used: own `LATEST.json`, own previous Phase-1 checkpoint, frozen sanitized root/own role config, GitHub connector capability discovery, and the public GitHub documentation listed below. No O, downstream, other-worker state/config/receipts, shared aggregate ledger, or legacy research was used.

## Result

The previous leaf showed that parent generation, leaf epoch, integrator epoch, storage CAS, and crash reconciliation identity are separate proof obligations. This continuation tested the next boundary: whether the parent-generation authority and canonical integration authority can safely live in different repository objects.

The companion enumerator exhaustively evaluates `147,456` equal-weight synthetic scenarios over:

- pre-transaction authority transition: `none / integrator takeover / cancel`,
- write order: `parent -> manifest` or `manifest -> parent`,
- each repository request outcome: `ok / fail / ambiguous-applied / ambiguous-not-applied`,
- optional read-before-retry after an ambiguous response,
- interruption/authority transition after the first data write and after the data pair: `none / crash / takeover / cancel`,
- optional final commit-event outcome for the journal protocol, and
- a later `none / takeover / cancel` after finalization.

The counts are finite mechanism counts, not operational failure probabilities. The model preserves the prior fencing assumptions: a takeover invalidates an in-progress old integrator but does not retroactively invalidate a transaction already fully committed before takeover; cancel advances the current parent lifecycle/generation; deterministic transaction IDs plus read-before-retry are used by the strong candidates.

### Three authority-domain candidates

1. **`split_two_cas_pair_checked`** — parent generation/lifecycle and canonical manifest remain in two files. Each path uses its own CAS and deterministic transaction ID. Current terminality is accepted only after reading both files and observing a matching transaction. A single file is never sufficient authority.
2. **`co_located_single_object_cas`** — parent generation/lifecycle, integrator epoch, child acceptance digests, canonical manifest, terminal disposition, and `applied_integration_id` are co-located in one CAS-protected object. Every authority-changing writer must mutate this same object.
3. **`split_append_only_intent_event_reconcile`** — a durable immutable intent is recorded, the two data files are updated separately, and a deterministic commit event is appended only after the pair is verified. Current terminality requires the commit event plus current-parent validation; the journal is a recovery layer rather than a substitute for current authority.

### Primary mechanism counts

| mechanism slice | split two-CAS, pair-checked | co-located one-CAS | split + intent/event |
|---|---:|---:|---:|
| strong-protocol false terminalization | 0 | 0 | 0 |
| strong-protocol duplicate integration | 0 | 0 | 0 |
| any physical split-state exposure after first data write | 30,720 / 147,456 | 0 / 147,456 | 30,720 / 147,456 |
| final partial/in-doubt state | 26,880 / 147,456 | 0 / 147,456 | 34,480 / 147,456 |
| recovery-needed cases resolved by one current read | 0 / 146,304 | 145,920 / 145,920 | 0 / 49,072 |
| current terminal states provable from one current read | 0 / 4,800 | 11,520 / 11,520 | 0 / 2,000 |

The strong split candidate is therefore **safe only because its terminal predicate is explicitly multi-object**. Two independent CAS operations do not create an atomic authority domain. In 30,720 scenarios the first successful file mutation is externally visible before the second file mutation. The pair-checked reader refuses to call those states terminal, but it must read both current files to decide authority or recovery.

By contrast, the co-located candidate exposes no split state in this finite model. When recovery is needed, one current object read is sufficient in all 145,920 recovery-needed scenarios because the parent generation/lifecycle, integrator epoch, canonical disposition, and deterministic integration identity move under the same storage version. This result is scoped to the explicit assumption that **every authority-changing writer uses that same object**; storing the integrator claim or parent generation elsewhere would reopen the race.

The append-only intent/event candidate also has zero strong-protocol false terminalizations, and every 34,480 final partial state in the tested grammar remains classifiable/recoverable because the intended transaction is durable. However, it does not create atomic publication: the same 30,720 first-write split exposures remain, and none of its 49,072 recovery-needed cases can be resolved from one current read. The journal improves crash recovery and provenance; it does not collapse multiple authority domains into one.

### Negative controls

The finite lattice contains three useful ablations:

- If the split design treats the **parent file's terminal bit alone** as sufficient authority, it transiently exposes a false terminal state in `18,240 / 147,456` scenarios. Parent-first success is enough to create the window even if the manifest later succeeds.
- If an ambiguous-applied canonical append is **blindly retried** instead of read-before-retry with deterministic transaction identity, the split design duplicates the logical integration in `4,608 / 147,456` scenarios.
- If the journal design treats a historical **commit event alone** as sufficient current authority and does not cross-check the current parent generation/lifecycle, a later cancel leaves `1,000 / 147,456` stale event-only terminal claims.

The structural conclusion is that storage CAS, durable intent, idempotent retry, and current authority are non-substitutable. A journal can recover a partial transaction; it cannot by itself prove that a past commit event still describes the current parent. Likewise, a per-file CAS can prevent a lost update on that file while still exposing an invalid cross-file combination.

## Public-source and Chat-surface audit

GitHub's repository-contents documentation describes create/update as a **single-file** operation and notes that conflicting contents operations must be serialized. That is consistent with treating two Contents API writes as two independent authority mutations rather than one cross-file transaction.

Public source: https://docs.github.com/en/rest/repos/contents

GitHub's Git database API provides a stronger multi-file publication primitive: a tree can contain multiple file changes, a commit points to the complete tree snapshot, and a branch reference is then moved to that commit. The official reference-update endpoint supports non-force updates and returns `409 Conflict` when the ref update cannot be performed under its rules.

Public sources:
- https://docs.github.com/en/rest/git/trees
- https://docs.github.com/en/rest/git/commits
- https://docs.github.com/en/rest/git/refs

Read-only connector capability discovery during this invocation confirmed that the ordinary connected GitHub surface exposes `create_tree`, `create_commit`, and `update_ref`, in addition to per-file `create_file` / `update_file`. No mutation was performed merely to probe capability. This exposes a fourth Chat-capable candidate for the next leaf: build a multi-path tree and commit as non-authoritative objects, then use one non-force branch-ref update as the publication point. Its crash/readback and takeover semantics still require explicit testing; in particular, a non-force fast-forward check is not identical to an API that accepts an explicit expected-old-SHA CAS parameter.

## Updated protocol obligations

- **A1 one authority domain when possible:** co-locate parent generation/lifecycle, integrator epoch, accepted child digests, terminal disposition, and deterministic integration identity behind one conditional mutation.
- **A2 multi-object terminality is conjunctive:** if authority must remain split, no single file may independently assert global terminality; readers validate the complete pair/set against one transaction identity and current generation.
- **A3 journal is recovery, not authority:** immutable intent/commit events preserve provenance and allow reconciliation, but current parent authority must still be checked.
- **A4 deterministic transaction identity:** every retryable integration carries a stable ID derived from the parent generation, current integrator epoch, accepted child digests, and terminal disposition; read-before-retry suppresses ambiguous-response duplication.
- **A5 currentness after historical commit:** later cancel/supersession can make an old commit/event historical. Current terminality must bind to the current generation/lifecycle, not merely the existence of a past success marker.
- **A6 partial states are first-class:** split authority designs explicitly expose `PREPARED / PARTIAL / IN_DOUBT` rather than pretending the first successful write is terminal.
- **A7 atomic publication alternative:** when multiple repository paths must change together, a Git tree + commit + single branch-ref publication is a candidate authority boundary and should be compared against single-file co-location and journaling.
- **A8 no hidden background completion:** an intent record, created Git object, lease, cancellation request, elapsed time, or worker existence is not terminal evidence until the authoritative publication predicate is satisfied.

## Failure tests added

1. Parent file commits terminal state and process crashes before manifest CAS: parent-local reader must not terminalize.
2. Manifest commits first and parent CAS fails: canonical evidence alone must remain nonterminal.
3. First file applies but response is lost: retry must read the transaction identity before any second append.
4. Integrator takeover occurs between file CAS operations: old transaction cannot finish under the old epoch; partial evidence remains historical/recoverable.
5. Cancel occurs between file CAS operations: any old partial state is non-current even if one file says success.
6. Intent exists but neither data write landed: recovery may retry only after current authority revalidation.
7. Intent + one data file exist: reconciler must inspect the missing authority file and current parent before finishing or aborting.
8. Both data files exist but commit event is missing: journal reader remains nonterminal until current authority and pair match are revalidated.
9. Commit event exists and later parent generation cancels: event-only reader is rejected as stale.
10. Co-located object CAS succeeds but response is lost: one current read checks deterministic integration ID before retry.
11. Co-located object is superseded/canceled before stale integrator CAS: same-object version change must reject the stale mutation.
12. Any authority field is moved outside the co-located CAS object: rerun the race because the one-read/one-CAS proof no longer applies.
13. Multi-file Git candidate: concurrent sibling commit advances the branch before ref publication; non-force ref update must fail closed rather than overwrite.
14. Multi-file Git candidate: ref-update response is lost and the branch later advances again; recovery must prove whether the proposed commit was ever published, not infer from object existence.

## Scope limits

- The finite lattice abstracts repository reads as current/authoritative once issued; it does not model CDN/cache staleness or branch-read propagation delay.
- Ambiguous-not-applied requests with retry are modeled as succeeding on the one allowed read-before-retry attempt; repeated transport failures are not assigned a probability.
- The journal uses deterministic unique intent/commit identities and assumes append-only records themselves are not silently overwritten.
- Pair-checked split safety depends on every consumer honoring the conjunctive terminal predicate. A legacy consumer that reads only one file is outside the positive result and is represented by the parent-local negative control.
- Co-located safety depends on every authority-changing writer sharing the same CAS object. External claim state or parent lifecycle stored elsewhere invalidates the one-domain assumption.
- Git tree/commit/ref publication was capability- and documentation-audited but not yet included in the exhaustive enumerator; it is the exact next Phase-1 leaf.
- All counts are synthetic mechanism counts, not deployment incidence estimates.

## Base continuation preserved, not resumed

The pre-overlay base continuation remains preserved exactly as fallback metadata and was not resumed while Phase 1 is active:

`Resolve/freeze latest sanitized control. Continue from FOLLOWUP_2026-08-28_200940_JST.md. Extend compensation repair from one ambiguous writer to multiple refund resource IDs and amount conservation over unique capture/refund/reversal identities; model accepted-but-no-resource-ID timeout; add late failure/reversal to newly issued compensation; expand to two captures and multi-irreversible branching DAG; compare independent repair proposals against early cross-critique on safe Pareto/QD coverage. Retry JudgmentBench only after source-qualified byte-stable transfer plus local publisher-hash verification; retry only source-qualified SymFail item artifact discovery.`

## Exact next Phase-1 action

Resolve/freeze the newest sanitized control first. If the Phase-1 overlay still assigns `phase1-clean-multi-agent-concurrency-claims`, extend this authority-domain leaf by testing the **Git commit/ref publication candidate** against the two strongest existing designs: (a) one co-located Contents-CAS object, (b) multi-path `create_tree -> create_commit -> update_ref(force=false)` publication, and (c) split files + append-only intent/event reconciliation. Enumerate sibling concurrent commits, integrator takeover/cancel encoded on the same ref versus a separate claim domain, crash after tree/commit creation but before ref publication, ambiguous ref-update response followed by a later ref advance, replay of the same proposed commit, orphan Git objects, and recovery with/without a persistent `applied_integration_id`. Measure false terminalization, duplicate integration, partial published state, orphan-but-nonauthoritative artifacts, exact reads/ancestry checks required for recovery, and whether non-force fast-forward rejection is sufficient for the intended CAS semantics. If that leaf is exhausted, move to the next unresolved generic Phase-1 concurrency candidate; do not restore the base objective while Phase 1 remains active.
