# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260827T0204_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, `RUN_20260826T1407_JST.md`, `RUN_20260826T1501_JST.md`, `RUN_20260826T1601_JST.md`, `RUN_20260826T1703_JST.md`, `RUN_20260826T1758_JST.md`, `RUN_20260826T1807_JST.md`, `RUN_20260826T1808_JST.md`, `RUN_20260826T2002_JST.md`, `RUN_20260826T2104_JST.md`, `RUN_20260826T2157_JST.md`, `RUN_20260826T2302_JST.md`, `RUN_20260827T0008_JST.md`, `RUN_20260827T0102_JST.md`, and `RUN_20260827T0204_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **OptiMer adds post-CPT mixture control.** It independently trains one CPT model per distribution, extracts parameter deltas, then searches merge weights post-hoc. On Gemma 3 27B with 1B-token distributions, reported averages are `69.98` vs uniform DataMix `67.86` for Ja+Math, `69.68` vs `67.23` for Ja+Code, and `70.37` vs `63.71` for Ja+Zh+Math. OptiMer-derived ratios also improve retrained DataMix, but remain below OptiMer in these tests.
- **Do not claim OptiMer beats optimized data mixing.** Its paper compares against uniform DataMix and explicitly says direct 27B comparison with DoReMi/RegMix remains future work. This is now the key missing matched test against Data Mixing Agent/RegMix-like controllers.
- **Search efficiency is strong but scoped:** the paper reports 100-trial OptiMer search `8.6 h` vs one DataMix run `128.9 h`, with equal aggregate CPT token cost excluded from the search comparison. `89.8%` of OptiMer trial time is evaluation, so evaluator cost is the bottleneck.
- **Official OptiMer code now exists** at `nict-astrec-att/optimer`. The current public search script does not seed Optuna samplers or Python RNG, so winning weights are not deterministic by default; paper settings also require overriding current README defaults (`100` trials/100-sample proxy vs code default `50`/300).
- **Data Mixing Agent acquisition is now pinned:** 384 trajectories, 50M proxy models, 27,266 feedbacks, `1996.08 GPU h` proxy/evaluation acquisition, 2.1M agent with SFT+CQL under 10 min. The paper's `52` vs `54` dimensional wording is an internal inconsistency; repeated experiment descriptions support 52 but retain the ambiguity explicitly.
- Data Mixing Agent, ELLA, SpaRTA/TSR/FST/TFGN/Share/SLoRA/FLEX/CLDD/replay/plasticity/world-model/drift branches remain live with prior scope guards.

Exact next action:
1. Specify and seek evidence for a budget-matched comparison of uniform DataMix vs RegMix/learned online mixing vs OptiMer post-hoc composition vs OptiMer-derived-ratio retraining, including evaluator queries, controller acquisition, training FLOPs, objective-switch cost and persistent checkpoint/vector storage.
2. Audit the official OptiMer release for published model/checkpoint/result/study artifacts and determine whether Table 1 winning weights can be exactly reproduced; explicitly seed sampler/Python/evaluation ordering in any reconstruction.
3. Quantify persistent storage/restart cost of `n` full 27B CPT checkpoints/deltas and compare with Data Mixing Agent controller + trajectory persistence.
4. Test whether OptiMer's advantage survives optimized mixing and CPT lengths beyond 1B tokens; preserve paper limitations.
5. Cross representative mixture controllers with the parameter-write axis only after holding data trajectories fixed.
6. Continue the earlier live branches under exact tested-scope rules.

Frontier must remain nonempty.
