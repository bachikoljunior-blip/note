# Phase-1 integrator fencing, cancellation, and crash-recovery stress test

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- invocation start observed: `2026-08-28T22:58:00+09:00`
- checkpoint packaging clock observation: `2026-08-28T23:04:25+09:00`
- chronology_valid: `true`
- frozen note main SHA: `5d503a3b9ec6270a126e214205a28f624228a682`
- frozen root control revision: `17`
- frozen role config revision: `6`
- frozen role config blob: `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- control_change_after_semantic_start: `true`
- newer observed note main SHA after semantic start: `be134635d3bc2cba97aad352340ee8bb20b364e1`
- newer control/config contents were not read or adopted after the semantic freeze barrier.
- semantic inputs used: own `LATEST.json`, own previous Phase-1 checkpoint, sanitized root/own role config frozen at the SHA above, and the public sources listed below. No O, downstream, other-worker state/config/receipts, shared aggregate ledger, or legacy research was used.

## Result

The prior leaf showed that parent generation and leaf claim epoch are independent proof obligations. This continuation moved the race one level up to the canonical integrator itself and tested the sequence:

`integrator_read -> parent_supersede/cancel -> integrator_CAS -> crash-before-readback -> resume/reconcile`

with an optional integrator-claim takeover, a same-file CAS conflict, a later canonical mutation after the crash, and a late old-child completion before/after cancellation. The companion enumerator generates 2,940 finite scenarios. Supersession scenarios additionally enumerate every truth assignment to the three revalidation predicates `task_hash match`, `input_digest match`, and `effect_contract match`, plus whether explicit revalidation is actually performed. The counts below are mechanism-test counts over this finite lattice, not operational failure probabilities.

### Primary protocol comparison

Three protocol candidates are compared:

1. `cas_only`: same-file blob-SHA CAS, blind refresh+retry after a storage conflict, no parent-generation/leaf-epoch/integrator-epoch authority check, and only current-content readback after a crash.
2. `cancel_only`: `cas_only` plus a best-effort cancellation signal. Old work is blocked only if cancellation is observed before the authoritative write.
3. `generation_leaf_integrator_epoch_fenced`: revalidate current parent generation, current leaf slot/epoch, and current integrator epoch immediately before the canonical CAS; keep child slots single-assignment; preserve a monotonic `applied_integration_id` in the canonical manifest for crash reconciliation; and allow a superseded child to be adopted only through explicit proof that `task_hash + input_digest + effect_contract` all match.

| failure slice | cas_only | cancel_only | generation+leaf+integrator fenced |
|---|---:|---:|---:|
| parent supersede/cancel before old CAS: false parent terminalization | 2,856 / 2,856 | 1,428 / 2,856 | 0 / 2,856 |
| integrator takeover with no parent change: stale-authority terminalization | 42 / 42 | 42 / 42 | 0 / 42 |
| late old child after parent transition: orphan accepted result | 2,448 / 2,448 | 1,224 / 2,448 | 0 / 2,448 |
| successful CAS -> crash -> later canonical move: unresolved CAS outcome | 980 / 980 | 504 / 504 | 0 / 14 |

`cancel_only` is exactly 50% on the parent-transition slices because the lattice balances cancellation observed before CAS versus cancellation delayed. This is deliberately not an incidence estimate. It isolates the mechanism: cancellation helps when observed, but it does not revoke stale authority by itself. In the `integrator takeover with no parent change` slice, cancellation has nothing to say, so both unfenced baselines accept all 42 stale integrator writes.

A storage-level conflict is also not semantic fencing. In all 1,428 `parent transition + CAS conflict` scenarios, `cas_only` refreshes the blob SHA and then still performs a stale semantic write; `cancel_only` does so in the 714 delayed-cancellation half. The fenced protocol refreshes and then revalidates parent generation/integrator epoch before retry, so it has 0 false terminalizations in that slice.

### Crash-before-readback requires an application-level integration identity

GitHub's repository-contents API requires the current blob `sha` when updating an existing file and documents `409 Conflict` for conflicting writes. That protects the file update against a lost update on that path, but it does not by itself tell a crashed integrator whether its previous CAS succeeded once the canonical file has subsequently moved again.

The finite model therefore adds a candidate protocol obligation: every authoritative canonical write carries a deterministic `applied_integration_id = H(parent_generation, integrator_epoch, accepted_child_digests, terminal_disposition)` and later canonical mutations preserve the set/log of applied IDs. On resume, the integrator checks that identity before retrying. With that obligation, the fenced protocol resolves all 14 successful-CAS/crash/later-move cases in its admissible slice. If that one gate is removed, the same 14 cases become outcome-ambiguous in this model. This `applied_integration_id` log is a synthesized protocol requirement, not a native guarantee of the GitHub Contents API.

Public source: https://docs.github.com/en/rest/repos/contents

### Cancellation is a liveness signal, not a stale-writer fence

GitHub Actions' cancellation reference explicitly describes cancellation as a multi-step process: the server re-evaluates job conditions, sends a cancellation message to runners, then runners send signals and wait before force termination. Jobs whose conditions continue to evaluate true can keep running. This public mechanism is enough to reject the assumption that a cancellation request instantly proves the old worker can no longer emit a completion.

Public source: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-cancellation

Inference for this assignment: parent cancellation/supersession must advance an authority token or generation that the canonical integrator validates. A cancellation signal can be an optimization for resource use, but it cannot substitute for fencing.

### Explicit revalidation is non-substitutable

For a superseded parent, the fenced protocol never adopts a late old child automatically. Across 2,304 superseded-parent scenarios with a late child, it safely adopts 144 cases, all and only when explicit revalidation is requested and `task_hash`, `input_digest`, and `effect_contract` all match. It accepts 0 cases without explicit revalidation and 0 cases with any non-matching equivalence field.

A negative control that keeps parent/integrator fencing but auto-adopts a superseded result by child name would admit all 2,304 such cases; 2,160 of them lack the exact explicit equivalence proof and therefore become orphan authority under this model. Exact byte/content equality alone is also not enough if the effect contract differs: adoption authority must be re-proved against the current parent objective.

### One-gate ablation

Removing exactly one gate from the fenced candidate creates the following new failures in the same finite lattice:

| removed gate | new failure count |
|---|---:|
| parent-generation coherence | 1,428 false parent terminalizations |
| integrator-epoch fencing | 42 stale-authority terminalizations |
| child-slot single-assignment | 18 duplicate authoritative child integrations |
| monotonic `applied_integration_id` | 14 unresolved crash outcomes |
| exact explicit superseded-child revalidation | 2,160 orphan-authority admissions |

The counts are not comparable risk weights because the axes are differently expanded; their use is structural. Each removed gate exposes at least one counterexample while the other gates remain present, so these obligations are non-substitutable in the tested grammar.

### Public analogue for conditional update

Kubernetes documents `metadata.resourceVersion` as an object version and states that HTTP PUT updates use it to detect stale clients and return `409 Conflict` when the resource has changed. This is a useful public analogue for conditional write/version validation, but the assignment-specific inference remains: the version being validated must cover the semantic authority being protected. A CAS on only the canonical manifest cannot validate a separately stored parent generation unless the generation is also included in the CAS-protected state or re-read/revalidated immediately before commit.

Public source: https://kubernetes.io/docs/reference/using-api/api-concepts

## Updated protocol obligations

- **P1 parent-generation coherence:** canonical parent terminality is qualified by the current parent generation/task hash.
- **P2 leaf stale-writer exclusion:** only the current leaf claim epoch may authorize a child slot.
- **P3 child-slot single-assignment:** once a child slot is authoritatively accepted for a generation, a distinct later result cannot become a second authority without an explicit replacement protocol.
- **P4 integrator stale-writer exclusion:** the canonical writer itself has a monotonically advancing integrator claim epoch/fencing token; takeover invalidates the old integrator even if parent generation is unchanged.
- **P5 serialized storage CAS:** every canonical mutation uses the current storage version/blob SHA and reconciles conflicts.
- **P6 semantic revalidation after CAS conflict:** refreshing the storage version is followed by re-checking parent generation, integrator epoch, required child epochs/digests, and parent lifecycle before retry.
- **P7 crash reconciliation identity:** authoritative writes include a deterministic monotonic `applied_integration_id` preserved across later canonical mutations, so crash-before-readback can be reconciled before retry.
- **P8 cancellation is advisory:** cancellation may stop work, but terminal/canonical authority never depends on assuming that cancellation was instantaneous or complete.
- **P9 superseded-child adoption is explicit:** adoption requires exact `task_hash + input_digest + effect_contract` equivalence proof under the current parent plus a new current-generation acceptance record; child-name matching or byte coincidence is insufficient.
- **P10 immutable staging:** late/stale results may remain as evidence under unique immutable paths, but non-current results are not automatically canonical.
- **P11 no hidden background progress:** a claim, cancellation request, elapsed time, or existence of a worker is never completion evidence.

## Failure tests added

1. Old integrator reads generation 1, parent supersedes to generation 2, same-file CAS remains conflict-free: old CAS must still be rejected semantically.
2. Old integrator reads generation 1, integrator epoch is taken over from 1 to 2 without changing parent generation: epoch-1 CAS must be rejected.
3. Old integrator receives `409 Conflict`, refreshes blob SHA after parent supersession, then retries: storage refresh must not authorize the stale semantic write.
4. Cancellation is requested but not yet observed by the old integrator: old CAS must still be rejected by generation/epoch fencing.
5. Cancellation is observed promptly: protocol may save work, but safety must not rely on this timing.
6. Old child completes after cancellation/supersession: stage immutably; do not auto-adopt into the current parent.
7. Superseded child has equal task hash but different input digest: adoption denied.
8. Superseded child has equal task+input but different effect contract: adoption denied.
9. All three equivalence fields match but no explicit revalidation action exists: adoption denied.
10. Successful canonical CAS -> crash before response/readback -> later canonical mutation: resume checks `applied_integration_id` before any retry.
11. Same-generation current leaf completes after its child slot is already accepted: second distinct result is rejected by single-assignment.
12. No worker actually runs after takeover/cancellation: parent remains pending/blocked rather than inferring completion from claim metadata.

## Scope limits

- The model treats parent state and canonical manifest as separately mutable authority domains so it can expose the semantic gap in same-file CAS. It does not yet model a design that co-locates parent generation and canonical terminal state in one atomic object.
- The synthesized `applied_integration_id` is assumed to be preserved monotonically by all canonical writers. The model does not yet test bounded-log compaction, pruning, or multi-file failure between intent and canonical commit.
- It assumes exact comparison for `task_hash`, `input_digest`, and `effect_contract`; it does not claim a method for proving semantic equivalence when those digests/contracts are unavailable.
- Cancellation timing is a two-point abstraction (`observed` / `delayed`), not a latency distribution.
- Same-file CAS conflicts are modeled as one refresh+retry; network timeouts and accepted-but-response-lost writes are represented only by the crash-before-readback branch.
- All percentages/counts are finite synthetic mechanism counts, not field failure rates.

## Base continuation preserved, not resumed

The pre-overlay base continuation remains preserved exactly as fallback metadata and was not resumed while the Phase-1 overlay is active:

`Resolve/freeze latest sanitized control. Continue from FOLLOWUP_2026-08-28_200940_JST.md. Extend compensation repair from one ambiguous writer to multiple refund resource IDs and amount conservation over unique capture/refund/reversal identities; model accepted-but-no-resource-ID timeout; add late failure/reversal to newly issued compensation; expand to two captures and multi-irreversible branching DAG; compare independent repair proposals against early cross-critique on safe Pareto/QD coverage. Retry JudgmentBench only after source-qualified byte-stable transfer plus local publisher-hash verification; retry only source-qualified SymFail item artifact discovery.`

## Exact next Phase-1 action

Resolve/freeze the newest sanitized control first. If the Phase-1 overlay still assigns `phase1-clean-multi-agent-concurrency-claims`, continue from this leaf by testing **authority-domain atomicity** rather than restoring base work: compare (a) split `parent generation` + `canonical manifest` files with two independent CAS operations, (b) one co-located single-file parent+manifest state updated by one CAS, and (c) split files with an append-only integration-intent/event record plus reconciliation. Enumerate `parent update succeeds / canonical update fails`, `canonical succeeds / parent update fails`, crash between the two writes, retry after ambiguous connector response, concurrent integrator takeover, and cancellation during the partial commit. Measure false terminalization, duplicate integration, recoverable partial states, and whether a single current read is sufficient to recover. Keep superseded-child adoption gated by exact `task_hash + input_digest + effect_contract` proof. If that leaf is exhausted, move to the next unresolved generic Phase-1 concurrency candidate; do not restore the base objective until Phase 1 ends.
