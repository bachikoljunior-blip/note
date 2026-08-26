# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T0305JST.md`
Current invocation chain: `2026-08-27T0305JST.md`
Previous checkpoint chain: `2026-08-27T0207JST.md` -> `2026-08-27T0107JST.md` -> `2026-08-27T0107JST-followup.md` -> `2026-08-27T0107JST-followup2.md`
Earlier predecessor chain: `2026-08-27T0033JST.md` -> `2026-08-27T0006JST.md` -> `2026-08-27T0006JST-followup.md` -> `2026-08-27T0006JST-followup2.md` -> `2026-08-27T0006JST-followup3.md` -> `2026-08-27T0006JST-followup4.md` -> `2026-08-27T0006JST-followup5.md`

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Chronology note

Current invocation observations: start `2026-08-27T03:00:48+09:00`, checkpoint `2026-08-27T03:05:08+09:00`; chronology is valid. Prior chronology corrections remain authoritative for earlier artifacts.

## Top unresolved frontier

1. Execute C263 unchanged in the first environment able to faithfully materialize pinned CSSC; never promote static inspection to runtime evidence.
2. Specify/implement a replayable **generated/randomized** OPA topdown-vs-exact-Wasm semantic differential/metamorphic harness. OPA already has broad paired shared-corpus conformance; the remaining gap is generated direct differential testing with seed persistence and shrinking.
3. Use an explicit semantic projection: strict-error-only behavior and known >64-bit Wasm exclusions are not raw-equality cases.
4. Distinguish source-level `rego` vs fresh `wasm` target comparison from comparison against the **exact deployed Wasm artifact** and intended runtime route.
5. Evaluate optional third-route triangulation with an independent IR executor such as Swift-OPA, while keeping Rego→IR compilation outside that evidence claim.
6. Search for proof/certificate-producing Rego or IR evaluation and machine-checked Rego→IR / IR→Wasm semantic preservation or translation validation.
7. Treat assurance as a layered typed evidence graph: theorem/certificate, shared-corpus fixed E2E, generated differential/metamorphic, independent implementation, schema/ABI/interface and manual-specification evidence are distinct.
8. Preserve `PolicyActivationCertificate -> ToolDispatchAuthorizationWitness -> atomic consume/effect commit -> EffectReceipt -> optional OutputReleaseAuthorizationWitness`, exact artifact/runtime identity, immutable provider-cost events and all crash/replay/epsilon=0 gates.
9. Deterministic provider pilot remains blocked; `epsilon>0` remains forbidden until every deterministic pre-randomization contract passes.

## Newest synthesis

- **C429:** at OPA commit `263253cc...`, both topdown and Wasm E2E runners load the same official v0/v1 compliance corpus; Wasm compiles each case to exact bytes and executes them through the SDK. OPA therefore already has broad shared-corpus paired conformance, though not the generated randomized direct differential oracle sought here.
- **C430:** raw source/Wasm equality is invalid universally: Wasm does not support strict builtin errors under this path and its E2E suite excludes known >64-bit integer cases. Differential testing needs a versioned semantic projection and explicit exception partition.
- **C431:** source-level `rego`/`wasm` target differential and exact-deployment-artifact differential are different evidence classes. The latter must bind the actual Wasm digest and runtime; OPA issue #8124 is relevant to avoiding accidental recompilation instead of artifact-direct execution.
- **C432:** Swift-OPA consumes OPA-derived compliance cases carrying IR plans and evaluates them with an independent Swift engine. This can triangulate IR execution semantics, but because OPA generates the plans it is not independent evidence for Rego→IR lowering. Known-issue scope must remain explicit.
- **C433:** the next experiment is a replayable Rego generator feeding OPA topdown, exact emitted Wasm bytes/runtime, and optionally independent IR/source implementations, with seed persistence, semantic partitioning, exact version/artifact identities and mismatch shrinking.
- **C263:** no runtime-evidence promotion this invocation; static evidence remains static-only.

## Exact continuation

1. Execute C263 unchanged when faithful pinned CSSC materialization becomes available.
2. Define the minimal supported Rego v1 fragment and implement/specify a seed-replayable generator against the intersection already covered by OPA topdown and Wasm E2E.
3. Search OPA history/external tooling once more for generated cross-backend fuzzing/shrinking before making a broad absence claim.
4. Add optional independent IR/source execution only with exact supported-feature and known-issue scope.
5. Search whether OPA/IR traces can become proof/certificate objects for a separately formalized useful fragment, and continue Rego→IR / IR→Wasm proof/translation-validation search.
6. Preserve every prior deterministic safety and measurement gate; `epsilon>0` remains forbidden.

`2026-08-27T0305JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.