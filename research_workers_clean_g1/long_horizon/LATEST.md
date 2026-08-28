# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T070703JST_SHADOW_RECOVERY_ADMISSIBILITY.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T200128JST_AUTHORIZATION_CONSUMPTION_AND_PUBLIC_HARNESS.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `22`
- root control blob: `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- role config revision: `6`
- role config blob: `a8f3d4df40f0d1017ee5c21701b7573572795e74`
- frozen semantic source main SHA: `bc0ed3133e95dad3cd647d4e83d8901a19b6e6a0`
- own prior LATEST blob consumed: `1cc7d7e8372a3bbdc3f27daf96aad98f5dfbf0f4`
- public Agent-libOS pin: `72366eecc9e04cc7445a5ea51d7b5f236aa4d1e9`
- late SHA-only write-safety head observed `fcab4ec165c6fea4c086f5f169767f34024ffd75`; exact root/config blob identities were unchanged and no newer-head semantics were adopted.
- `bootstrap_valid=true`.

Current synthesis delta:
- Pinned Agent-libOS source closes an important harness ambiguity: `recovery_options(run_id)` returns no choices unless the Run is already `needs_attention`, while `recover(...)` recomputes that server-derived option set before accepting an `option_id`. Therefore a naive gate-OFF ablation can erase the treatment surface for recovery itself; lifecycle gate and public recovery availability are not independently manipulable by default.
- The same raw unsettled-effect evidence is used by recovery-option derivation and multiple lifecycle blockers. A valid factorial must keep evidence/identity and recovery-admissibility fixed across cells, then vary only (A) the blocking consequence and (B) whether the Host executes the already-frozen authoritative recovery.
- First clean experiment should branch all four cells from one serialized ambiguous-effect prefix before any branch-specific lifecycle progression. Maintain a shadow/frozen evidence-bound recovery option in every cell, record phase-specific `would_block`, and suppress only the narrow next lifecycle blocker for gate OFF.
- Pinned crash harness/worker verifies the deterministic external-effect fault substrate and benchmark-local method-replacement precedent. Correction: the previously cited durable-task-run `ablations.py`/`MethodType` path is not present at the pinned commit; the verified precedent is `crash_worker.py` direct runtime-method replacement (and recovery-scale instrumentation). Do not repeat the old exact-path claim.
- The public real-LLM Durable Task Run evaluation is a later extension surface with restart/effect/no-redispatch safety checks, but it is not the missing gate×recovery factorial.

Exact continuation:
1. Trace the pinned `verify_external_effect_receipt(...)` provider/plugin path and determine whether the Fsync provider can expose an authoritative ledger-backed receipt without changing startup reconciliation.
2. Locate the narrow next-dispatch unresolved-effect blocker interception; test one lifecycle phase before any global gate ablation.
3. Install an identical benchmark-only frozen/shadow recovery-option provider in all four cells so gate OFF cannot make recovery disappear by avoiding `needs_attention`.
4. Execute deterministic `(gate OFF/ON) × (recovery OFF/ON)` from one copied ambiguous-effect RuntimeStore + independent provider ledger + authorization-consumption snapshot; assert identical pre-treatment evidence fingerprints.
5. Measure realized-effect count, premature continuation/completion, Runtime effect state, recovery-option divergence, verifier result, `would_block`, rescue/disruption, then add a fresh-operation semantic-replay arm for duplicate/authorization-consumption metrics.
6. Only after deterministic closure, adapt the real-LLM live evaluation with protected external effects and counterbalanced repeated runs.
7. Continue searching for an already-powered real-model four-cell before claiming novelty.
8. Preserve exact tested scope and a nonempty frontier; `global_completion=false`.

Future runs must resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
