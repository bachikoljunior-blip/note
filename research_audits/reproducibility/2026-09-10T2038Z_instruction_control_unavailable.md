# Reproducibility auditor control diagnostic

- termination: instruction_control_unavailable_recurring_open
- enabled_desired: true
- global_completion: false
- phase1_completion_claimed: false
- semantic_work_performed: false
- scheduler_mutated: false
- error: `automation_control/DESIRED_STATE.json` authority blob mismatch; manifest-declared blob `eb010ed63873aaaf42bfb6ab56e38bfe3bc6cd07`, fetched blob `0eee15a94c23400653d84506da1f795081a6ef24`.
- continuation: `Retry bootstrap from automation_control/INSTRUCTION_CONTROL_MANIFEST.json; require its declared DESIRED_STATE blob to equal the freshly fetched automation_control/DESIRED_STATE.json blob before any semantic work.`
