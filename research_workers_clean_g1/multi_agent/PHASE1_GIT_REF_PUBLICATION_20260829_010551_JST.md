# Phase-1 Git commit/ref publication and claim-fencing stress test

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- packaging clock observation: `2026-08-29T01:05:51+09:00`
- frozen note main SHA: `40b09e47cf596eb6a9846988bc2f860b719afb8b`
- frozen root control revision: `19`
- frozen role config revision: `6`
- frozen role config blob: `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- control_change_after_semantic_start: `true`
- newer observed note main SHA after semantic start: `4d9810ed6f848a4e8d0361938eaad6b7d4b3609d`
- newer root/config semantic contents were not read or adopted after the freeze barrier.
- semantic inputs used: frozen sanitized root manifest; own role config; own `LATEST.json`; own prior authority-domain checkpoint/script; official public GitHub Git database documentation. No O/O-derived state, downstream state, other worker state/config/receipts, shared aggregate ledger, or legacy/pre-independence research was used.

## Leaf objective

Test the prior candidate `create_tree -> create_commit -> update_ref(force=false)` as a multi-path publication primitive and determine exactly when its non-force fast-forward check is sufficient to fence stale integrators, when it is not equivalent to an explicit expected-old-SHA CAS, and what crash/readback evidence is required to avoid duplicate logical integration.

The companion executable enumerates `6,912` equal-weight synthetic scenarios over:

- authority location: `same_ref / separate_claim`,
- pre-publication authority transition: `none / takeover / cancel`,
- sibling branch advance before publication,
- ref request outcome: `ok / fail / ambiguous-applied / ambiguous-not-applied`,
- crash point: none, after tree/commit object creation before publication, or after ref request before readback,
- later ref movement to a descendant containing the proposal or to a branch excluding it,
- environments that do or do not permit force/history rewrite,
- replay/no replay,
- persistent `applied_integration_id` present/absent, and
- durable proposal commit SHA present/absent.

Counts are finite mechanism counts, not operational failure probabilities.

## Public mechanism facts used

GitHub documents Git tree creation as producing tree objects that must then be committed and followed by a branch update before the changes become branch state:

- https://docs.github.com/en/rest/git/trees

GitHub's Git commit endpoint creates a commit object with explicit parent SHA(s), which lets a proposal commit `P` be constructed with exact parent `B`:

- https://docs.github.com/en/rest/git/commits

GitHub's ref-update endpoint accepts a target `sha` and `force` flag. With `force=false` (the default), GitHub requires a fast-forward update; the documented request does **not** accept a separate expected-old ref SHA:

- https://docs.github.com/en/rest/git/refs

This distinction is the basis of the tested scope below.

## Main result: non-force ref update is a scoped fence, not a universal claim CAS

For the `git_ref_only_negative_control`, the branch ref is the only fence and a separate claim/lifecycle domain is never rechecked.

Across all `6,912` scenarios it produced:

- false terminalization: **192**
- duplicate logical integration on replay: **288**
- actual current terminal states missed by exact-ref-SHA-only recovery: **576**
- multi-path partial published state: **0**

The stale-authority slice is the key discriminator:

| stale authority before publication | scenarios | direct old-proposal ref applies | false terminal claims |
|---|---:|---:|---:|
| takeover/cancel encoded on the **same publication ref** | 2,304 | **0** | **0** |
| takeover/cancel stored in a **separate claim domain** | 2,304 | **384** | **192** |

Because proposal `P` is built with exact parent `B`, any same-ref takeover/cancel creates a sibling/current head that is not an ancestor of `P`; `update_ref(force=false)` rejects the stale proposal under the monotonic no-force assumption. But if claim epoch/lifecycle changes somewhere else while the publication ref stays at `B`, the old proposal is still a valid fast-forward from the ref's point of view. Therefore:

> `force=false` is CAS-like for this fixed-parent proposal only when every authority-invalidating transition is encoded in the same ref history (or separately revalidated). It is not an explicit expected-old-SHA CAS over an external claim domain.

## Strong candidate

`git_force_false_plus_claim_recheck_and_reconcile` adds four requirements:

1. Build proposal commit `P` from the exact observed base `B`.
2. Recheck current claim/lifecycle immediately before publish/replay when authority is not encoded on the same ref.
3. Use `update_ref(force=false)` for publication.
4. After ambiguous response/crash, prove the **logical current effect** using either:
   - exact current ref `== P` while proposal identity is still known,
   - a persistent `applied_integration_id` in the canonical tree, or
   - a durable proposal SHA plus ancestry comparison.
   Otherwise block rather than infer absence from an exact-SHA mismatch.

Across the same `6,912` scenarios the strong candidate produced:

- false terminalization: **0**
- duplicate logical integration: **0**
- actual current terminal states: **768**
- proven terminal states: **648**
- safe actual terminals intentionally left unclaimed: **120**
- recovery-needed scenarios: **6,528**
- recovery-resolved scenarios: **6,144**
- fail-closed unresolved scenarios: **384**
- multi-path partial published state: **0**

The unresolved cases are deliberate evidence insufficiency, not false success.

## Response-loss / descendant recovery

A current branch head can be a descendant `D` that contains proposal `P` in its ancestry even when the current ref SHA is not exactly `P`. In the synthetic descendant slice with no stale authority:

- current logical effect actually present: **576**
- exact-ref-SHA-only negative control proves: **0**
- exact-ref-SHA-only negative control retries into duplicate logical integration in **288** replay cases
- strong candidate proves: **480**
- strong candidate blocks/misses: **96**

The evidence split is exact:

- when either a persistent `applied_integration_id` or a durable proposal SHA is available, all **432 / 432** actual descendant terminals in that slice are proved;
- when both are absent, **96** actual descendant terminals cross a crash/readback boundary and are intentionally not terminalized.

Crash-recovery slices show the same separation:

| crash/readback evidence | scenarios | actual terminals | proved terminals | recoverable |
|---|---:|---:|---:|---:|
| persistent applied ID | 2,304 | 240 | 240 | 2,304 |
| no marker, durable proposal SHA | 1,152 | 120 | 120 | 1,152 |
| neither marker nor durable SHA | 1,152 | 120 | 0 after recovery boundary | 768 |

The model intentionally does not use full per-path digest reconstruction as a fallback. Adding that is a possible later extension.

## Tree/commit objects before publication

The strong Git candidate exposes **no partial multi-path branch state** in this model because all file changes are assembled into one tree, then one commit, and the publication boundary is one ref move.

Crashing after object creation but before ref publication can leave a proposal object with no current ref authority. The model counts these as `proposal_not_in_current_ref_ancestry`; it does **not** claim global Git unreachability, garbage-collection behavior, or absence from other refs. Object existence is never accepted as terminal evidence.

This is structurally different from the prior split-files + intent/event design, where physical partial file states were possible, and from the prior one-object Contents-CAS design, where no pre-publication Git objects exist.

## Comparison to the two prior strong candidates

| property | co-located Contents CAS | Git tree + commit + one ref publish | split files + intent/event |
|---|---|---|---|
| multi-path partial publication | no, if all authority is in one object | **no** in this finite model | yes |
| stale writer fencing | same-object CAS/version | fast-forward fence only for same-ref authority; external claim must be rechecked | per-file CAS + generation/epoch checks |
| crash before publication | no separate Git proposal object | nonauthoritative tree/commit object may remain | durable intent/partial file state may remain |
| ambiguous publication response | current object + applied ID | ref + marker or ancestry/proposal SHA | inspect intent + files + current authority |
| one current read sufficient | yes under prior one-domain assumptions | sometimes; descendant/readback can require 2 reads | no in prior model |
| journal/provenance | optional | commit history helps but is not enough for logical currentness | explicit intent/event log |

## Executable assertions added

The companion script hard-asserts that:

- strong Git candidate has zero false terminals and zero duplicate logical integrations in this finite lattice;
- stale same-ref takeover/cancel yields zero old-proposal direct ref applies under `force=false`;
- stale separate-claim takeover/cancel yields positive old-proposal ref applies unless separately rechecked;
- exact-SHA-only replay duplicates some already-current descendant integrations;
- marker-or-durable-SHA descendant recovery has zero missed safe terminals;
- crash-before-publication proposal objects never become terminal evidence merely by existing.

## Scope limits

- The positive same-ref fence assumes a monotonic non-force branch discipline. If authorized writers can force/reset/rewrite the ref, the simple ancestry argument no longer provides the same guarantee.
- `update_ref(force=false)` is treated as a fast-forward predicate exactly as documented; no stronger expected-old-SHA contract is inferred.
- The model tracks current canonical repository effect, not out-of-band hooks or external side effects that may have fired during historical/transient publication.
- `proposal_not_in_current_ref_ancestry` does not imply the object is globally unreachable or eligible for garbage collection.
- A later descendant that contains `P` is allowed by the mechanism model because Git commits can name explicit parent SHAs; the model does not assign a deployment probability to that path.
- Full path-by-path digest reconstruction, branch protection/rulesets, merge queues, signed commits, and CDN/read-propagation behavior are outside this leaf.
- All counts are synthetic equal-weight mechanism counts, not empirical incident frequencies.

## Exact Phase-1 continuation

Resolve/freeze the latest sanitized control first. If `phase1-clean-multi-agent-concurrency-claims` remains active, move to the next unresolved concurrency leaf: **logical-effect claim-key granularity and sharded reservation**.

Build a finite model comparing:

1. one coarse global claim,
2. deterministic per-task claim keys,
3. deterministic per-exclusive-effect claim keys,
4. task-key + effect-key two-level reservation, and
5. append-only result staging with a single fenced integrator.

Enumerate task-spec drift under the same human-readable task name, hash collision/adversarial aliasing, worker restart with lost local state, simultaneous first claim, stale takeover epoch, multi-effect tasks with overlapping subsets, independent non-conflicting tasks, retry after ambiguous claim write, claim TTL expiry before result integration, and parent supersession. Measure duplicate computation separately from duplicate authoritative effect, safe parallel admission, false exclusion of non-conflicting work, stale result acceptance, and recovery reads. Preserve independence: workers may share only claim metadata necessary for exclusion, never each other's semantic solution content.

Do not restore the base research objective while the Phase-1 overlay is active.
