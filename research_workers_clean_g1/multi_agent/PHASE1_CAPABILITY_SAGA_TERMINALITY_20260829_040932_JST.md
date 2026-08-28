# Phase-1 revocable/irrevocable capability + saga terminality stress test

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- semantic control tuple remains frozen for this invocation: note main `63e0f497bc9157c6c5075a8c615327dc49b8e76a`, root control revision `21`, root blob `87e2d9e19b16d39b495a4a5512d871069d7521ee`, role config revision `6`, role config blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`.
- after own/concurrent repository writes advanced main, exact empty-content blob checks at later head `5e745b9296bed616098a86d92c54226dd23b0d7c` confirmed the frozen authoritative root/config blob identities were unchanged, so revision-21 post-freeze identity rules allowed this next Phase-1 leaf without consuming newer-head semantics.
- semantic inputs: own immediately preceding cross-shard and external-effect handoff artifacts, public AWS Prescriptive Guidance saga documentation, and this finite synthetic model. No O/O-derived state, downstream state, other-worker state/config/receipts, shared aggregate ledger, or legacy research was used.

## Leaf objective

The external-effect handoff leaf exposed a check-to-effect revocation race that local fencing cannot close when the sink is in another authority domain. This leaf asks whether the race can be removed by **changing the authorization contract** rather than pretending a revocable check remained current.

It compares:

- **revocable-until-effect** authorization: parent supersession before effect application must prevent the effect;
- **irrevocable-after-authorize** authorization: once a capability is validly minted while the parent is current, later parent supersession does not revoke that already-authorized effect.

The second contract can remove the post-mint revocation race, but only if capability mint itself is atomic with the current parent generation and capability consumption is replay-safe. Multi-sink partial completion is then handled separately with saga compensation/finality.

## Public mechanism evidence used

AWS Prescriptive Guidance describes Saga as a sequence of local transactions with compensating transactions when a later step fails. Its orchestration guidance explicitly warns that:

- compensating transactions and retries add complexity,
- saga participants should be **idempotent** so repeated execution after crashes/orchestrator failures is safe,
- saga lacks transaction isolation and concurrent sagas can see stale data, for which semantic locking is recommended.

- https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga.html
- https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html

This is used only to support the compensation/idempotency/isolation mechanism boundary. The single-use capability semantics below are synthetic protocol contracts, not claimed AWS features.

## Finite model

The executable enumerates **768 equal-weight synthetic scenarios** over:

- authorization contract: revocable-until-effect vs irrevocable-after-authorize,
- capability mint: atomic with parent currentness vs separate read-then-mint,
- capability consumption: durable single-use vs replayable,
- parent transition: stable / supersede before mint / supersede after mint before first effect / supersede after first effect,
- second effect: success vs blocked,
- compensation availability: none vs available,
- compensation result: success / ambiguous-applied / late-failed,
- dispatcher takeover: none vs takeover.

Compared protocols:

1. **revocable local check** — local currentness check followed by effect call; replayable capability may be reused after dispatcher takeover.
2. **cooperative revocable sink** — strong sink capability that enforces revocable authority at application time and durable single-use consumption.
3. **irrevocable atomic single-use capability** — parent currentness validation and capability mint are one atomic authority transition; later parent supersession is non-revoking by contract.
4. **NEG irrevocable separate mint** — read parent current, then mint capability in a later step.
5. **strong saga finality** — atomic irrevocable single-use authorization plus compensation; parent is terminalized as compensated only after compensation is final.
6. **NEG saga terminal-on-compensation-accept** — declares compensated terminality when compensation is merely accepted/ambiguous, even if it can later fail.

## Main results

| protocol | terminals | compensated terminals | unsafe | stale effects | duplicate effects | partial-effect cases | false terminals | structural blocks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| revocable local check | 36 | 0 | **144** | **96** | **48** | 144 | 0 | 384 |
| cooperative revocable sink | 24 | 0 | 0 | 0 | 0 | 24 | 0 | 576 |
| irrevocable atomic single-use | 36 | 0 | 0 | 0 | 0 | 36 | 0 | 672 |
| NEG irrevocable separate mint | 54 | 0 | **84** | **48** | **48** | 96 | 0 | 576 |
| strong saga finality | 42 | 6 | 0 | 0 | 0 | 36 | 0 | 672 |
| NEG saga terminal-on-accept | 54 | 18 | **6** | 0 | 0 | 36 | **6** | 672 |

Structural blocks are deliberate: capability-specific protocols refuse to claim safety outside the exact contract/capability surface they require.

## Result 1: revocable authorization remains vulnerable to local-check TOCTOU

The `revocable_after_local_check` slice contains **96** scenarios where the parent supersedes after the local authorization check/mint point but before the first external effect. The local-check protocol produces **96/96 stale-authority effects** and 96 unsafe cases.

The cooperative revocable sink is safe only in its supported single-use sink-capability subset because the effect application itself enforces current authority. This repeats the previous leaf's conclusion: local fencing cannot prove a revocable authorization remained current at another system's effect boundary.

## Result 2: irrevocable capability semantics can close that race, but only by changing the contract

In the **48-scenario** slice where:

- authorization is `irrevocable_after_authorize`,
- capability mint is atomic with current parent authority,
- consumption is durable single-use,
- parent supersedes after mint but before/after the first effect,

the atomic capability protocol has **0 unsafe / 0 stale / 0 duplicate effects**. Later parent supersession is not a revocation under this contract; the effect was already authorized.

This is not proof that a revocable authorization stayed current. It is a semantic shift: the system defines a one-way authorization point. That boundary must be explicit in terminality/audit metadata because rollback/reassignment after mint cannot assume the effect is still cancellable.

## Result 3: separate read-then-mint recreates the race

The `irrevocable_separate_mint_race` slice contains **48** scenarios where the parent changes after the authority read but before capability mint. The negative separate-mint protocol is **48/48 unsafe and 48/48 stale-authority**. A later irrevocable capability cannot repair the fact that it was minted without current authority.

Therefore `current parent -> mint capability` must itself be one atomic authority transition (or use an equivalent fencing predicate), not two independent steps.

## Result 4: single-use is a separate replay proof

In the **48-scenario** `capability_replay_takeover` slice, the replayable separate-mint negative control produces **48/48 duplicate effects** under dispatcher takeover. Atomic mint/currentness and replay safety are distinct: even a valid authorization can be applied twice if the sink does not consume a durable single-use identity.

The current candidate therefore binds capability identity to deterministic effect identity and requires durable single-use/deduplicated consumption at the sink.

## Result 5: Saga compensation is not atomic rollback, and acceptance is not finality

The `compensation_late_failure` slice has **8** scenarios with:

- atomic irrevocable single-use authorization,
- first effect applied,
- second effect blocked,
- compensation available,
- compensation later fails after an accepted/apparently successful state.

The strong saga policy leaves all supported cases nonterminal/ambiguous until compensation finality is known. The negative early-terminal policy marks **6** supported cases compensated-terminal and all **6/6 become false terminal / unsafe** when the compensation later fails.

This matches the public Saga boundary: compensation is another distributed action with its own retry/idempotency/failure semantics. A compensation request or acceptance cannot be collapsed into durable rollback completion.

## Result 6: partial multi-effect state is independent of stale/duplicate safety

Even the safe capability protocols have partial-effect cases when effect 1 succeeds and effect 2 blocks. The strong Saga policy can turn a subset into compensated terminal states only when compensation reaches its modeled final success state. Therefore terminal predicates need at least three distinguishable dispositions:

- all required effects durably complete,
- compensating rollback durably complete,
- unresolved partial/compensating state.

A single `COMMITTED`/`DONE` bit loses required recovery semantics.

## Current candidate protocol

1. Define the authorization semantics explicitly before execution:
   - **revocable-until-effect** requires effect-boundary cooperation/shared authority; local pre-check is insufficient;
   - **irrevocable-after-authorize** permits a one-way capability point, after which parent supersession cannot revoke that already-authorized effect.
2. For irrevocable authorization, mint the capability atomically with the parent generation/current claimant epoch. A separate read-then-mint is rejected.
3. Bind each capability to canonical `effect_id`, target/effect contract, parent generation and authorization epoch; consume it durably exactly once at the sink (or via equivalent application-level deduplication).
4. Treat capability mint as an irreversible effect in planning/rollback accounting. Parent reassignment after mint must reconcile already-authorized effects rather than pretending they can still be canceled.
5. For multi-sink objectives, track per-effect lifecycle separately. If a later effect fails, enter a Saga/compensation branch rather than marking the parent failed/done without disposition evidence.
6. Compensation is a new effect with its own deterministic identity, current compensator epoch, ambiguity handling and finality. Do not terminalize on compensation acceptance alone.
7. Saga participants must be retry-safe/idempotent where retries are possible; concurrency isolation/semantic locking remains a separate gate.

## Scope limits

- `irrevocable_after_authorize` is a deliberately different business/authority contract, not a universal replacement for revocable authorization.
- capability mint atomicity and durable single-use sink consumption are explicit assumptions; this leaf does not claim generic HTTP/payment APIs expose them.
- compensation can be semantically non-invertible or only partially restorative; the model treats a successful compensation as an objective-defined rollback result and does not assume byte-for-byte restoration.
- late compensation failure is modeled as a mechanism stressor, not attributed to every Saga provider.
- counts are finite equal-weight synthetic mechanism counts, not empirical frequencies.

## Exact Phase-1 continuation

Continue with **capability lifecycle + compensation graph / terminality certificate** rather than returning to base research.

Next finite grammar:

- one-way authorization/capability states `PREPARED / MINTED / CONSUMED / EXPIRED / REVOKED_WHERE_SUPPORTED`,
- effect states `NOT_SEEN / AMBIGUOUS / APPLIED / FAILED`,
- compensation states with separate effect IDs and late reversal/failure,
- two and three effects with independent irreversible/compensatable flags,
- parent supersession before/after each capability mint/consume,
- dispatcher and compensator epoch takeovers,
- duplicate/replayed capability delivery,
- compensation cycles and multiple valid recovery branches,
- terminality certificate as an effect-vector over unique effect/compensation identities rather than a root Boolean,
- compare greedy rollback, forward-complete, fail-closed/manual, and Pareto/QD archive of safe recovery policies.

Measure stale authorization, duplicate effect, duplicate compensation, false terminalization, unresolved ambiguity, irreversible residual exposure, compensation depth/cost, and safe recovery coverage separately. Preserve the contract distinction: authorization semantics, effect identity, and compensation finality are non-substitutable proof dimensions.