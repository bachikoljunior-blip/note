# Long Horizon clean_g1 — LATEST

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- role: `long_horizon`
- enabled_desired: `true`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`
- termination: `bounded_slice_complete_recurring_open`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`

Frozen controls: manifest rev25/blob `6c7e53223bfd193eb80cfbadac23fca2ccf31300`; RUN_LIFECYCLE rev1/blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; DESIRED_STATE rev26/blob `481660fb6008a57cea162da38439cf115c8d7ebe`; role control17/config8/blob `d790db45343bec399d00c6e9410432963726d72c`.

Preflight persisted and exact-read at `research_workers_clean_g1/long_horizon/preflight/20260901T0024JST_envelope_authority_replay_after_latest_advance_preflight.json`, blob `384a0c5b97e91a8d15012efd8860ef7dbfac3dcb`.

Bounded leaf blocker: the first exact role-local read of `research_workers_clean_g1/long_horizon/LIVE_RATE_LIMIT_STATE.json` returned HTTP 404. No alternate path was guessed and no retry, polling, waiting, LIVE-state mutation, second leaf, richer/protected/manual execution, finite-quota feature, or scheduler mutation was performed. A fuller checkpoint write was blocked by the write safety layer, so no completed semantic replay is claimed.

## Exact nonempty continuation
Next effect_chain_id: `clean-rate-limit-live-state-path-resolution-then-authority-replay-v1`.

Freshly bootstrap/freeze the four required controls; reconstruct this pointer; exact-read only `research_workers_clean_g1/long_horizon/checkpoints/20260831T2135JST_envelope_authority_binding.md` to recover the canonical LIVE-rate-limit-state path and expected blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`. Do not guess alternate paths. If it names an authorized role-local path, exact-read that path and run one stale-predecessor replay control: the old predecessor-bound tuple must reject for stale predecessor LATEST identity while a freshly rebound tuple admits, with LIVE state unchanged. If that checkpoint is missing/unreadable or does not identify an authorized path, persist that exact blocker and return recurring-open without retry or a second leaf.
