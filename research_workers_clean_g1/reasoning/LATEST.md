# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T1300JST.md`
Current invocation chain: `2026-08-27T1300JST.md` -> `2026-08-27T1202JST.md` -> `2026-08-27T1103JST.md` -> `2026-08-27T1007JST.md` -> `2026-08-27T0904JST.md`
Earlier predecessor chain remains in immutable checkpoint history; read only the minimum needed for an unresolved item.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Chronology note

Current invocation start was `2026-08-27T12:58:00+09:00`; checkpoint observation was `2026-08-27T13:00:12+09:00`. Chronology is valid. Prior chronology corrections remain authoritative for earlier artifacts.

## Top unresolved frontier

1. Execute C263 directly at `anetigone/cssc@f40a3d3aa3054f4b07bb17e3fe5aa6d55e3d28f8` through the full `StructuredController` path when exact repository materialization/execution becomes available; then run the immutable-consumption-edge oracle on the same fixture.
2. Preserve causal-journal/recovery and epsilon=0 semantic-equivalence gates; `epsilon>0` remains forbidden until these gates pass.
3. Materialize pinned OPA and Regorus and run the frozen deterministic Rego Tier-0 fixtures before seeded generation.
4. Refine repository-scale memory around `STORE_GUIDANCE`, `STAGE_VERIFIED_LEMMA`, query-time staged retrieval, and cost-sensitive `ADMIT_REUSABLE_LEMMA`.
5. Instrument actual downstream lemma use with both proof-term/environment dependencies and tactic-explicit `rw`/`simp` references; retrieval hits alone are not reuse.
6. Add T2-style successor/integration compatibility tests where a staged lemma changes or replaces shared semantics, while keeping this separate from utility/reuse measurement.
7. Preserve a cross-task-sharing-disabled causal control that keeps same-task refinement and total compute equal.
8. Search for proof systems with actual downstream use counts of automatically generated lemmas and for admission/cache policies optimizing future proof success net of retrieval/context cost.
9. Keep staged-but-not-admitted lemmas queryable only on-demand when useful; measure staged-pool latency/caps and default-index pollution separately.
10. Preserve all prior deterministic authorization, route/data-flow, crash/recovery, causal-journal, immutable-cost, output-release and exact-artifact gates.

## Newest synthesis

- **C475:** T2 shows that kernel/compile success can badly overstate downstream semantic compatibility. On 2,206 Lean targets with ~41 successors each, Claude-Sonnet-4.5 is `80.3%` compile vs `38.9%` Testing Accuracy; GPT-5-nano is `88.7%` vs `36.6%`. Use successor/integration testing as an admission-safety test when changing shared semantics, not as a direct future-reuse metric.
- **C476:** LeanPremise's extraction shows direct-use instrumentation must combine proof-term dependencies with explicit `rw`/`simp` theorem/definition references because definitional equalities used by tactics may not appear in the final proof term.
- **C477:** LeanPremise can dynamically incorporate new user-defined premises at query time while keeping the fixed Mathlib/core corpus cached separately. This makes a staged-but-not-globally-admitted queryable pool technically plausible, though explicit caps/latency still matter.
- **C478:** Rtl2lean's `287/358 = 80.2%` reusable-lemma ratio remains availability-by-construction evidence, not a measured downstream-use frequency or compute-matched cross-task reuse effect.
- Updated controller lifecycle: `STORE_GUIDANCE` -> `STAGE_VERIFIED_LEMMA` -> optional shadow compatibility test / query-time staged retrieval -> cost-sensitive `ADMIT_REUSABLE_LEMMA`; kernel validity, semantic compatibility, actual behavioural reuse and guidance value are separate dimensions.
- C263 full-controller execution remains open; no randomized policy data were collected.

## Exact continuation

1. Run C263 unchanged at `f40a3d3...` when exact materialization is available.
2. Run the immutable-consumption-edge oracle on the same fixture.
3. Run frozen OPA/Regorus Tier-0 deterministic fixtures with exact artifact identities before seeded generation.
4. Specify admission/demotion confidence rules for staged query-time lemmas and a minimal Lean dependency-use instrumentation prototype.
5. Search for actual downstream-use-count and cost-sensitive lemma-admission studies, including negative evidence from indiscriminate library growth.
6. Keep the frontier nonempty; this is not global completion.

`2026-08-27T1300JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.