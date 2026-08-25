# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T0659JST.md`

Predecessor synthesis/state:
`research_workers_clean_g1/long_horizon/STATE.md`

Control snapshot frozen for the latest semantic run:
- root control revision: `9`
- role config revision: `5`
- frozen source main SHA: `bef75c9992d531894760890e0a092f1e7eb0da0e`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- post-freeze head later observed: `f04a4a0b7c6d2d400c8389d32989068b2ced9dc4`; no newer control/config was adopted after the semantic-freeze barrier.

Current synthesis delta:
- FailFast/RestartSmart primary tables now verify that alarm time and safe cut time are separate controls. On Qwen3.6-27B at 25% FPR, immediate RestartSmart resolves `68.8%` with `18.8%` false-positive loss, while waiting for a settled edit boundary resolves `71.8%` with `8.8%` false-positive loss. At 10% FPR the corresponding resolve difference is only `69.6% -> 69.8%`, so cut patience matters more under aggressive intervention in this tested setting.
- Under the same Qwen3.6-27B/FPR family, point estimates separate two likely recovery contributions: at 25% FPR cold restart is `66.8%`, immediate RestartSmart `68.8%`, and waited RestartSmart `71.8%`; however the paper does not report a dedicated significance test for immediate RestartSmart versus cold restart, so that sub-contrast remains an inference rather than a separately established causal result.
- Forced textual correction can reverse sign with policy strength: the paper's SWE-PRM reproduction improves Qwen3.5-9B `48.2% -> 52.4%` but degrades Qwen3.6-27B `66.6% -> 63.4%`.
- Atomix primary RQ1/RQ3 tables cleanly separate task recovery from external-effect safety. On the full tau-bench pool, Tx-Full `58.8%` vs Checkpoint-Replay `53.5%` is statistically tied (`p≈0.50`), yet irreversible-effect leakage is `0/500` vs `200/500`, and mixed fp=0.30 run-clean is `65%` vs `25%`.
- The recovery controller should therefore keep at least these variables separate: sensing, intervention decision, safe cut timing, historical target, carry-forward, local restore, external-effect settlement, commit-time revalidation, and repair stopping.

Exact continuation:
1. Resolve the newest control/config again at the next invocation using the SHA-only semantic-freeze protocol.
2. Find a strict detector-quality factorial that fixes recovery actuator, cut rule, carry-forward, policy/tasks, and FPR budget while varying detector quality/calibration and measuring final success/disruption.
3. Find a strict historical-target selector factorial that fixes alarm, checkpoint candidate set, restore/carry-forward, model and retry/token budget while varying only the selected prior checkpoint.
4. Keep the subgoal/folding negative-evidence branch alive: wrong decomposition, stale folded summaries, or over-aggressive compression that measurably reduce final task success.
5. If a first-party FailFast/RestartSmart code artifact appears, verify cut/pairing implementation against the primary tables rather than inferring it from prose.

This pointer does not supersede exact source/tested-scope guards in the checkpoint. Future runs should read this pointer first and only the minimum own predecessor material needed for unresolved frontier continuity.
