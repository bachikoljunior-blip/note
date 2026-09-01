# CLEAN long_horizon preflight

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`

## Frozen authority tuple

- INSTRUCTION_CONTROL_MANIFEST: control_revision `40`, blob `4b96273483ec18493894d2e0eb5cc71a120b39ea`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Selected bounded effect chain

- effect_chain_id: `clean-rate-limit-envelope-stale-sequence-binding-v1`
- exact predecessor LATEST blob: `e69025d5ffb248f7e49a700266610cb385a666af`
- authority branch: `clean-long-horizon-phase1-active`
- expected current LIVE blob from predecessor: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- expected current LIVE state_sequence / plan_generation: `6 / 3`
- injected negative coordinate only: stale `state_sequence=5` bound to predecessor LIVE blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff`
- planned atomic boundary: re-read LIVE once; if exact current blob and generation still match, classify stale sequence binding without mutating LIVE; persist/read back result and continuation.
- forecast: one LIVE read plus compact checkpoint/receipt/LATEST persistence chain.
- switch threshold: any authority/blob/generation mismatch, connector error, CAS conflict, or inability to finish the persistence chain within the bounded slice => persist diagnostic if safely possible and return recurring-open; no same-run retry/backoff/poll and no second leaf.
- residual richer-mode/Work/protected/user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
