# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-28T1112JST.md`
Current invocation chain: `2026-08-28T1112JST.md` -> `2026-08-28T1013JST.md` -> `2026-08-28T0907JST.md` -> earlier immutable clean reasoning history.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict.

Frozen semantic control for the newest invocation: note main `bd1b817ef65d7a3f9e5f83652d8040fc07634397`; DESIRED_STATE control rev 13 / blob `cc9b1f22f0fda9cf26296057fd35b19a090618b4`; reasoning config rev 6 / blob `cc8b37410994561a016a72c467b25ff0582d6462`. The SHA-only pre-semantic freshness recheck matched. Later note-main advances were not adopted as a new semantic control tuple.

## Top unresolved frontier

1. Freeze **C589–C610** and all associated confirmation/disagreement pools. Never recalibrate and retest a policy on the split that exposed its failure/success.
2. Preserve the **retained verified incumbent + optional challenger + sequential value-of-computation** architecture. The incumbent is the hard no-harm output fallback; learned allocation only controls optional compute.
3. `scaled_dev_v1` is now a frozen **pre-fit failure**, not an active model candidate. Exact replay found 65 permitted v1-stop states and **0 positive incremental-over-v1 labels**; fitting/threshold/OOD/bootstrap steps are forbidden on that same data.
4. The exact compact support replay and frozen negative result are `experiments/coalition_seeded_tail_value_model_scaled_dev_v1_support_replay_v0.json` and `experiments/coalition_seeded_tail_value_model_scaled_dev_v1_replay_result.json`.
5. A wholly-new support-collection/model protocol is preregistered at `experiments/coalition_seeded_tail_value_model_scaled_dev_v2_protocol.json`. It fixes 160 fresh n=16/n=18 development cases and exhaustively audits every eligible frozen-v1 stop state before fitting. Old successful confirmations/disagreement pools remain excluded.
6. Before any v2 fit, require the frozen support gate: >=60 applicable stop-region rows, >=8 positive target rows, and positives in >=2 families. Otherwise freeze insufficient-support and do not retune.
7. The general lesson is **selective-label support**: if a deterministic stop policy censors all positive outcomes in its own action region, a learned override is not identifiable there. Keep the safe incumbent but deliberately buy known-propensity audit continuation in rejected states.
8. Public formal-proof evidence remains split: current Lean cost-quality routing learns binary `Attempt/Terminate`; VERITAS preserves Phase-1 solves and applies a fixed Phase-2 search only to failures. A retained baseline with learned sequential *amount* of Phase-2 compute remains an open target in this scan.
9. Preserve exact propensity logging/nonzero audits, cumulative anytime-valid inference, and true marginal-cost accounting. Sparse zero discoveries are not evidence of zero tail value outside observed support.
10. Preserve all older rebuild/TDD/lemma/result-graph/C263/OPA-Regorus/deterministic-safety frontiers and the untouched original n=20 portfolio holdout.

## Newest synthesis

- **C606:** deterministic replay reproduces all stored n=12/n=14 aggregate results exactly and reproduces the old 31-feature development mean vector with max absolute error `3.55e-15`.
- **C607:** among the 65 exact states where frozen v1 stops at index65, the preregistered incremental target is all-zero; `scaled_dev_v1` therefore fails before fitting by single-class support.
- **C608:** the zero-positive region is structurally explained by v1's gap64 threshold 11 being chosen as the maximum active-positive development gap; it must not be generalized to unseen distributions.
- **C609:** `scaled_dev_v2` preregisters fresh stop-region auditing with retained-incumbent safety and a pre-fit positive-support gate. No new v2 outcome has been opened yet.
- **C610:** fresh public search still finds binary adaptive routing and fixed second-stage retained-baseline search as separate pieces, not a directly evaluated sequential quantity-of-second-stage-compute controller.
- Scope guard: synthetic ROBDD results motivate controller architecture only. Formal-proof claims remain source/config/benchmark qualified.

## Exact continuation

1. Execute `coalition_seeded_tail_value_model_scaled_dev_v2_protocol.json` incrementally on its frozen 912xxx/913xxx development seeds; collect only preregistered v1-stop labels and costs.
2. After all 160 cases, evaluate the support gate **before** model fit. Fail without retuning if applicable/positive/family support is insufficient.
3. If support passes, build the exact frozen 27-feature table and fit/evaluate the unchanged scaler+logistic/LOFO/threshold/bootstrap/OOD specification. Freeze the artifact before selecting any new confirmation.
4. Continue public formal-proof search for retained verified baseline + learned sequential quantity of second-stage compute, and for explicit audit/randomized-continuation logging of stop decisions.
5. Preserve exact propensity logging, cumulative audit inference, all older replay/safety frontiers, and the untouched n=20 holdout.

`2026-08-28T1112JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.
