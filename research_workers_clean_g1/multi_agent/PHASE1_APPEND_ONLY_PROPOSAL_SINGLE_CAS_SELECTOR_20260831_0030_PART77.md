# Phase-1 Multi-Agent Part77 — Append-only proposal + single CAS selector

## Frozen authority
- role: `multi_agent`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-multi-agent-concurrency-claims`
- frozen main SHA: `7edb516ac139dc69e502a428b2eb4827c12301ee`
- DESIRED_STATE blob/revision: `481660fb6008a57cea162da38439cf115c8d7ebe` / 26
- role-config blob/config revision: `f6bade5e0f774a0623e615b1fc5f924475732d5c` / 8
- transport: preferred SHA-only main ref + exact-SHA control reads
- presemantic liveness witness: `automation_control/receipts/multi_agent/receipt_2026-08-31T0030_JST_presemantic_liveness_config8_control26.json`, exact-read back before the first own-state/public semantic read.

## Selected bounded leaf
Part77 from the prior role-local `LATEST.json`: test a repository-native immutable proposal object plus one canonical selector file updated by current blob-SHA CAS, specifically against the ambiguity isolated for issue markers in Part76. No live proposal/selector mutation was required for the mechanism test; the experiment is a finite state-machine trace analysis grounded in the currently exposed GitHub connector contract and current public GitHub REST documentation.

Candidate protocol under test:
1. Derive a deterministic `transition_id` and deterministic immutable proposal path from current generation + task/effect identity + proposal digest. A create collision is read/verify, never blind overwrite.
2. Keep *all authority-critical currentness fields* in one selector object: current generation, selector epoch/incarnation token, selected transition ID, selected proposal digest, effect/terminal contract identity, and applied transition ID.
3. A contender may publish only by reading the current selector, validating generation/contract, then replacing that selector using its current blob SHA. Competing contenders that read the same old selector are not both authoritative; after any conflict/ambiguous response they must read the selector before any later retry.
4. The immutable proposal is audit/staging evidence, not the authority source. The selector must be self-contained enough to decide which transition is authoritative even if the proposal object later disappears.
5. Rate-limit/transport interruption never causes same-run retry or waiting. Persist/checkpoint and, on a later invocation, read the selector first: matching `applied_transition_id` means applied; a different selected transition means lost; unchanged selector with still-current generation means retry remains possible later.

## Finite adversarial trace grammar and result
A 32-scenario equal-weight synthetic grid was enumerated over:
- proposal multiplicity: 1 vs 2 concurrent proposals;
- selector outcome: acknowledged apply / response-lost-but-applied / response-lost-not-applied / conflict-other-wins;
- generation state: current vs advanced-before-selector-publication;
- proposal retention: present vs deleted after selection.

Three mechanisms were compared:
- deterministic proposal marker without a canonical selector;
- selector that stores only a pointer/reference to the proposal;
- self-contained selector described above.

Observed within this finite model:
- Marker-only: 8/32 duplicate-authority cases under two current concurrent proposals; 16/32 stale-authority cases when generation advanced before publication; 16/32 response-loss cases remained authority-ambiguous without a canonical readback boundary.
- Pointer-only selector: 0/32 duplicate authority and 0/32 stale authority under the stated single-file CAS/current-generation assumptions, but 6/32 scenarios became unreconstructible after a *selected* proposal object was deleted. Those six are exactly the current-generation terminal-selection slices with deleted proposal evidence.
- Self-contained selector: 0/32 duplicate authority, 0/32 stale authority, and 0/32 selector-level reconstruction ambiguity. It terminalized only the 12/32 cases where the generation was current and the selector was known/apparently applied or another contender had already won; the remaining 20/32 fail closed or remain retryable rather than fabricating terminality. Deleting the proposal audit object did not erase the selected transition identity/digest/currentness proof because those authority-critical fields were co-located in the selector.

These are mechanism counts over a deliberately balanced finite grammar, not production failure-rate estimates.

## Public/connector evidence
Observation from the currently exposed GitHub connector schema: `create_file` requires a path that does not already exist, while `update_file` requires the current blob SHA of the file being replaced and returns the resulting commit/content identity. This gives a deterministic-path first-create primitive for proposal staging and a per-file compare-before-replace surface for the selector.

Current GitHub REST documentation for repository contents states that “Create or update file contents” creates a new file or replaces an existing one, requires `sha` when updating a file, documents `409 Conflict`, and warns that concurrent contents mutations can conflict and should be serialized. Source: https://docs.github.com/en/rest/repos/contents (retrieved 2026-08-31).

GitHub’s current REST rate-limit documentation says primary/secondary exhaustion can return 403/429 and that callers should not retry until the indicated reset/`Retry-After`. Source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api (retrieved 2026-08-31). For this recurring-Chat design, that maps to checkpoint-and-return, not an in-run wait/backoff loop.

## What this leaf establishes — and does not
Scoped positive: compared with an issue-marker/search scheme, a deterministic immutable proposal plus one *self-contained* selector object materially strengthens uniqueness and ambiguous-response reconciliation using only lightweight repository transport. Under a monotonic selector history where every authority/generation transition mutates that same selector and stale writers must present the current selector blob SHA, the finite traces above had no duplicate or stale authority.

Scope guard / unresolved child: GitHub file `sha` is a content blob identity, not a separately documented path-incarnation/version counter. This leaf did **not** test delete/recreate, force-rewind, or restore-to-an-identical-old-selector-content ABA. A stale writer could become dangerous if an old selector blob becomes current again. Therefore the mechanism is *not* accepted as a complete Phase-1 coordination proof yet; selector-history anti-rollback/incarnation fencing remains open.

## Zero-dependency / quota / cost assessment
- residual richer-mode / protected-primary / manual-user execution dependency added by this leaf: **none**;
- external hosted coordination accepted: **none**;
- finite monthly/trial/paid compute/storage/API-credit dependency added: **none**; lightweight repository API is transport only and rate-limit interruption is fail-closed/checkpointed;
- incremental monetary cost: **0**;
- global Phase-1 completion claimed: **false**.

## Exact continuation
Part78: execute exactly one bounded leaf on selector-object ABA and rollback. Compare (a) blob-SHA-only selector CAS, (b) selector containing a monotonic incarnation/epoch but stored in the same rollback domain, and (c) selector plus a non-reusable transition/incarnation witness that can be checked without hosted coordination. Enumerate delete+recreate with identical content, repository ref rewind/restore to an old selector blob, stale writer holding the old SHA, ambiguous response across the rewind, and deterministic proposal-path reuse. The key falsification is whether a stale pre-rewind writer can again satisfy the selector compare after old content becomes current. Preserve fail-closed behavior and zero richer-mode/protected/manual dependency, zero finite monthly/trial/paid quota, and zero added cost.
