# Long Horizon clean_g1 — latest pointer / bounded Phase-1 checkpoint

Canonical Phase-1 role branch: `clean-long-horizon-phase1-active`
Authority record: `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`
Predecessor LATEST blob: `5e2981249107bce9fd6bf7d559a2236e8554ee39`

## Frozen authority for this invocation
- transport_mode: `exact_blob_two_pass`
- instruction manifest revision/blob: `2` / `b288c95adab1ef949ed1791275176815a67b7d11`
- lifecycle revision/blob: `1` / `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- root control revision/blob: `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role control/config revision/blob: `17` / `8` / `d790db45343bec399d00c6e9410432963726d72c`
- branch authority blob/generation carried from the exact predecessor: `dd9eb6a591f643e8653c61e5469a0805be54f3fe` / `1`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- bootstrap_valid: `true`
- enabled_desired: `true`

## Selected single effect chain
- effect_chain_id: `clean-switch-once-cas-v1`
- stage completed this invocation: `update_only_preflight_persistence_probe`
- exact predecessor/frontier: predecessor LATEST required trying a single compact role-local persistence on an already-existing mutable path with exact current-blob CAS before any A -> B switch.
- planned atomic boundary: establish that update-only CAS persistence on the canonical role branch is usable; do not start the synthetic A -> B switch until this checkpoint is durably read back.
- synthetic fixture reserved for the next stage: `p90=18s`, checkpoint reserve `8s`, remaining fixture `20s`; switching rule is `SWITCH` when `p90 + reserve > remaining`.
- forecast threshold result for that reserved fixture: `18 + 8 = 26 > 20`, therefore the next semantic transition is exactly one `A -> B` switch.

## Bounded result
The previously blocking create-only preflight route was bypassed without a second lineage: this checkpoint uses the already-existing mutable `LATEST.md` path and exact predecessor-blob CAS on the canonical role branch. No synthetic switch state, external effect, retry, wait, poll, scheduler mutation, richer-mode execution, protected-primary execution, or manual-user step is performed in this stage.

Tested scope: authority bootstrap plus one role-local update-only CAS persistence attempt on the canonical role branch. This result does not yet prove the A -> B switch or stale replay rejection.

Residual richer-mode/Work/protected-primary/manual execution dependency: `none introduced`.
Finite monthly/trial/paid quota dependency: `none introduced`; lightweight repository transport only and no hosted compute/storage allowance is used as an execution dependency.
Incremental monetary cost: `0`.
Conflict check: role-local namespace and canonical role branch only; no protected-primary, other-worker, downstream, O-derived, or scheduler state is read or mutated for semantics.

## Lifecycle receipt
- termination: `bounded_slice_complete_recurring_open`
- global_completion: `false`
- phase1_completion_claimed: `false`
- enabled_desired: `true`
- scheduler_mutation_by_worker: `false`
- continuation_nonempty: `true`
- hard_runtime_boundary_reached: `false`
- next_invocation_resumes_exact_continuation: `true`

## Exact continuation
On the next invocation, bootstrap and freeze the current manifest, RUN_LIFECYCLE, DESIRED_STATE and long_horizon role config exactly as required, then reconstruct this same canonical branch and `clean-switch-once-cas-v1` lineage. Using this checkpoint as the sole predecessor, perform exactly one role-local synthetic `A -> B` plan switch under current-blob CAS because `p90 18s + reserve 8s > remaining 20s`. Persist/read back the switched state and stop that invocation; leave the stale replay rejection for the following invocation. If the update-only CAS is authority-mismatched or blocked, record the exact blocker without retry/wait/poll and keep this same leaf unresolved. Never use a second lineage, quarantined evidence, richer-mode/protected/manual execution, finite quota, scheduler mutation, or optional second leaf.
