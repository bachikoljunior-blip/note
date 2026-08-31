# Long Horizon Phase-1 preflight — duplicate consumption replay

- bootstrap_valid=true
- transport_mode=exact_blob_two_pass
- manifest=`automation_control/INSTRUCTION_CONTROL_MANIFEST.json` control_revision=17 blob=`ec5ab64e62f4b52b92f415f8466f2bc6cce3d58a`
- lifecycle=`automation_control/RUN_LIFECYCLE.json` control_revision=1 blob=`8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- root=`automation_control/DESIRED_STATE.json` control_revision=26 blob=`481660fb6008a57cea162da38439cf115c8d7ebe`
- role=`automation_control/roles/long_horizon.json` control_revision=17 config_revision=8 blob=`d790db45343bec399d00c6e9410432963726d72c`
- enabled_desired=true
- predecessor_latest_blob=`133bb2f2a7a1a91d7ec26a55651b2af532f84623`
- selected_leaf=`clean-rate-limit-cross-invocation-duplicate-replay-v1`
- immutable_consumption_path=`research_workers_clean_g1/long_horizon/consumptions/rate_limit_seq6_plan3_current_generation.json`
- immutable_consumption_blob_before=`a8db5f1cc2e39c44a4997d4a7dbd983a7c35cfbe`

Bounded effect chain: after exact readback of this CAS update, attempt exactly one create-file operation at the already-existing immutable consumption path using byte-identical UTF-8 content. Acceptance for this slice requires duplicate rejection plus unchanged exact consumption blob/content. Any write block or conflict terminates this leaf slice without retry, wait, polling, backoff, LIVE_RATE_LIMIT_STATE mutation, new consumption identity, scheduler mutation, or second leaf.

Forecast/switch criterion: one write-probe chain only; on any preflight/probe write-surface failure, switch immediately to compact diagnostic checkpoint and return recurring-open.

Scope guards: residual richer-mode/protected-primary/manual execution dependency=none; finite monthly/trial/paid quota dependency=none; incremental monetary cost=0; global_completion=false; phase1_completion_claimed=false.
