# Long Horizon clean_g1 — LATEST

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- role: `long_horizon`
- enabled_desired: `true`
- bootstrap_valid: `true`
- transport_mode: `sha_pinned_main`
- termination: `bounded_slice_complete_recurring_open`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`

Frozen controls: main SHA `09038e6e7a8c2132e728f1b402d3d80396a9afa0`; manifest rev27; RUN_LIFECYCLE rev1/blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; DESIRED_STATE rev26/blob `481660fb6008a57cea162da38439cf115c8d7ebe`; role control17/config8/blob `d790db45343bec399d00c6e9410432963726d72c`.

Predecessor LATEST blob consumed: `dddaacf5148c79e083ff65c300ed4dfa0f0177a8`.
Preflight: `research_workers_clean_g1/long_horizon/preflight/20260901T0223JST_stale_predecessor_authority_replay_preflight.json`, blob `21fd9352e59b46d086f7128e4466abd7fd1f84a9`.
Authoritative current checkpoint: `research_workers_clean_g1/long_horizon/checkpoints/20260901T0224JST_stale_predecessor_authority_replay.md`, blob `3e1d860167aa7ec673d5a85f785adfca9816dc58`.

Bounded leaf result: canonical LIVE rate-limit state exact-read at unchanged blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a` (`state_sequence=6`, `plan_generation=3`). Replaying the old authority tuple bound to predecessor LATEST blob `1ca604313274d16b2fa66bdba91866fba28d6015` was rejected as `REJECT_STALE_PREDECESSOR`; the freshly rebound tuple using predecessor blob `dddaacf5148c79e083ff65c300ed4dfa0f0177a8` admitted. Old/fresh authority fingerprints were `4d9dbe376a8772ae317933566c517c5cd3000fbdbeaca4b61161df69e4289e59` and `a08dc3a2f23ed450c22feacd5bd91068f847fb3d12cf9a751acf613d4b10cfb5`. LIVE state was not mutated.

No wait/poll/backoff/retry, second leaf, scheduler mutation, richer-mode/Work, protected-primary/manual execution, hosted compute, finite quota, or incremental monetary cost was introduced.

## Exact nonempty continuation
Next effect_chain_id: `clean-rate-limit-stale-generation-replay-v1`.

Freshly bootstrap/freeze the four required controls; reconstruct this pointer; exact-read canonical `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`. In exactly one bounded in-memory control, replay a continuation authorized by stale predecessor generation `2` / prior state blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` against canonical generation `3` / current LIVE blob and require rejection with no LIVE mutation; compare one freshly bound generation-3 continuation as positive control. Persist/read back preflight, result/checkpoint, LATEST and one immutable own receipt. Preserve `enabled_desired=true`, `global_completion=false`, `phase1_completion_claimed=false`; never mutate scheduler or start a second leaf.
