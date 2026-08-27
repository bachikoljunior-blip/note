# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-27T1007JST.md`
Current invocation chain: `2026-08-27T1007JST.md` -> `2026-08-27T0904JST.md` -> `2026-08-27T0805JST.md` -> `2026-08-27T0703JST.md` -> `2026-08-27T0605JST.md`
Previous checkpoint chain: `2026-08-27T0503JST.md` -> `2026-08-27T0408JST.md` -> `2026-08-27T0305JST.md` -> `2026-08-27T0207JST.md` -> `2026-08-27T0107JST.md`
Earlier predecessor chain remains in immutable checkpoint history; read only the minimum needed for an unresolved item.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict. Immutable checkpoint files remain the evidence trail.

## Chronology note

Current invocation start was `2026-08-27T09:57:44+09:00`; checkpoint observation was after 10:07 JST. Chronology is valid. Prior chronology corrections remain authoritative for earlier artifacts.

## Top unresolved frontier

1. Execute C263 directly at `anetigone/cssc@f40a3d3aa3054f4b07bb17e3fe5aa6d55e3d28f8` through the full `StructuredController` path when exact repository materialization/execution becomes available. **Do not search for an older pin:** C263's original checkpoint already binds this exact SHA and current CSSC main is still the same SHA.
2. Regression-test the migrated immutable attribution design on that same fixture: physical provider events unchanged; two same-batch consumers produce two append-only consumption edges; provider charge counted once.
3. Preserve causal-journal/recovery and epsilon=0 semantic-equivalence gates, then apply the already frozen deterministic provider headroom pilot. `epsilon>0` remains forbidden until these gates pass.
4. Materialize pinned OPA and Regorus toolchains and run `rego_tier0_fixtures_v0.json` through OPA topdown, exact emitted OPA Wasm, Regorus interpreter and Regorus RVM before any seeded generation.
5. Bind OPA-Wasm evidence to exact emitted `policy.wasm` bytes, compiler identity, Wasm ABI and pinned runtime/SDK; persist Regorus serialized `Program` identity/digest.
6. Block seeded generation on any deterministic fixture mismatch; shrink only while preserving `reasoning.rego_tier0_generator.v0` support.
7. Recover/read Brown `https://git.sr.ht/~jakob/rego-proofs` and current VeriRego source through an allowed readable transport; until then keep thesis-backed and implementation-backed claims separate.
8. Add Vero only as a downstream repository-scale evaluation target after the controller substrate is trustworthy; do not treat Vero's benchmark results as causal evidence for a specific controller policy.
9. Preserve all prior deterministic authorization, route/data-flow, crash/recovery, causal-journal, immutable-cost, output-release and exact-artifact gates.

## Newest synthesis

- **C465:** corrected a frontier error. C263 was not bound to an older CSSC commit; its own immutable definition pins `f40a3d3...`, which is still current CSSC main. C462's helper microreproduction therefore used the exact C263 revision, but C263 still requires full `StructuredController` execution and remains open at that evidence class.
- **C466:** Vero (arXiv:2608.13522) shows a repository-closure gap: the strongest configuration fully solves 27/43 code-and-proof repositories and 25/43 proof-only while passing 87.3% and 85.8% of individual specifications respectively; 10 repositories resist every tested configuration. The paper attributes hard residuals to shared invariants, reusable lemma libraries and cross-module coordination. Future controller evaluation should keep local verified progress and global repository closure as distinct objectives.
- **C467:** there is no current CSSC release or GitHub Actions artifact at `f40a3d3...` that bypasses this runtime's source-materialization limitation. Exact source is readable, but a faithful full repository execution path is still missing here.
- All prior safety/measurement gates remain unchanged; no randomized policy data were collected.

## Exact continuation

1. Run C263 unchanged at `f40a3d3...` when exact materialization is available; preserve helper-level versus full-controller evidence distinction.
2. Run the immutable-consumption-edge oracle on the same fixture.
3. Run frozen OPA/Regorus Tier-0 deterministic fixtures with exact artifact identities before seeded generation.
4. Recover Brown/VeriRego sources through readable transport.
5. Use Vero later for a matched local-greedy versus shared-lemma/dependency-aware controller evaluation under a fixed substrate/budget, reporting repository full solves separately from per-spec coverage and cost.
6. Keep the frontier nonempty; this is not global completion.

`2026-08-27T1007JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.