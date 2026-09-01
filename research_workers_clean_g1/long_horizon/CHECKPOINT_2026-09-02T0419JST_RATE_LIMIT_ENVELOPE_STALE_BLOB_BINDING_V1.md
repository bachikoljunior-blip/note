# CLEAN long_horizon checkpoint — rate-limit envelope stale blob binding v1

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- role: `long_horizon`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`

## Frozen controls

- INSTRUCTION_CONTROL_MANIFEST: control_revision `43`, blob `c9c8bdb368dfd2270bb18b2c5c6093001ec97ee6`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`
- frozen tuple validity: root/config two-pass identity matched; manifest required blobs matched the fetched lifecycle/root/role controls.

## One bounded Phase-1 slice

- effect_chain_id: `clean-rate-limit-envelope-stale-blob-binding-v1`
- canonical role branch: `clean-long-horizon-phase1-active`
- predecessor LATEST blob: `ce539dea4696bf23c9f537e97500bc69a18e54dc`
- preflight: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-02T0419JST_RATE_LIMIT_ENVELOPE_STALE_BLOB_BINDING_V1.md`
- preflight exact-read blob: `f7f8586862f0ea02a770a700d0b7f2ceddd636f0`
- LIVE path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- LIVE exact observed blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- LIVE observed state_sequence: `6`
- LIVE observed plan_generation: `3`
- LIVE current authority_file_blob: `dd9eb6a591f643e8653c61e5469a0805be54f3fe`
- injected stale blob coordinate: `5217ac80d20baad6afd158bd5e39c4b39e9200ff`
- all non-blob binding coordinates held current: authority branch, predecessor/current LATEST identity for this invocation, state_sequence `6`, plan_generation `3`

### Decision

The continuation envelope names current `state_sequence=6` and `plan_generation=3`, and the exact LIVE read confirms both. Its negative control substitutes only the predecessor LIVE blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff`. Because the authoritative current LIVE blob is `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, the stale blob cannot authorize continuation even though the semantic payload coordinates still identify the current generation.

- result: `REJECT_STALE_BLOB_BINDING`
- LIVE mutation issued: `false`
- retry/backoff resampled: `false`
- prior plan reactivated: `false`
- retry attempt incremented: `false`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- scheduler mutation: `false`

## Tested scope / acceptance guards

This is a mechanism-level stale-continuation control for the role-local lightweight repository envelope only. It proves that an exact content-blob coordinate can reject an ABA-like or replayed predecessor state when sequence/generation happen to be current. It does not claim global scheduler, multi-principal force-push, or external-effect safety.

- residual richer-mode/Work/protected-primary/manual-user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false` for the tested path; no hosted runner, Codespaces, artifact/LFS/package, cloud/model credit, or external execution service was used
- incremental monetary cost: `0`
- conflict check: no O/downstream/other-worker semantic state consumed; no primary/protected state mutated; writes remain role-local
- termination: `bounded_slice_complete_recurring_open`
- hard_runtime_boundary_reached: `false`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-current-valid-binding-v1`.

Freshly bootstrap and freeze the same four required controls, reconstruct the canonical role branch from its then-current LATEST CAS successor, and persist/exact-read a new preflight before the leaf. Re-read LIVE only if the continuation still names exact current `state_sequence=6`, `plan_generation=3`, and LIVE blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`. Use those exact current coordinates as a positive control and require `ACCEPT_CURRENT_BINDING` without mutating LIVE, retry/backoff state, plan generation, scheduler, or starting a second leaf. If any coordinate has advanced, record the precise mismatch and replace the positive-control child with a freshly bound one on the next invocation. Phase 1 remains open.
