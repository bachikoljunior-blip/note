# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260827T0209_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, `RUN_20260826T1407_JST.md`, `RUN_20260826T1501_JST.md`, `RUN_20260826T1601_JST.md`, `RUN_20260826T1703_JST.md`, `RUN_20260826T1758_JST.md`, `RUN_20260826T1807_JST.md`, `RUN_20260826T1808_JST.md`, `RUN_20260826T2002_JST.md`, `RUN_20260826T2104_JST.md`, `RUN_20260826T2157_JST.md`, `RUN_20260826T2302_JST.md`, `RUN_20260827T0008_JST.md`, `RUN_20260827T0102_JST.md`, `RUN_20260827T0204_JST.md`, and `RUN_20260827T0209_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **OptiMer adds post-CPT mixture control.** It independently trains one CPT model per distribution, extracts parameter deltas, then searches merge weights post-hoc. On Gemma 3 27B with 1B-token distributions, reported averages are `69.98` vs uniform DataMix `67.86` for Ja+Math, `69.68` vs `67.23` for Ja+Code, and `70.37` vs `63.71` for Ja+Zh+Math. OptiMer-derived ratios also improve retrained DataMix, but remain below OptiMer in these tests.
- **Do not claim OptiMer beats optimized data mixing.** Its paper compares against uniform DataMix and explicitly says direct 27B comparison with DoReMi/RegMix remains future work. This is the key missing matched test against Data Mixing Agent/RegMix-like controllers.
- **Official OptiMer artifact is currently code-only on observed public surfaces.** The NICT repo has one commit and only LICENSE/README/search script; no releases, model/checkpoint bundle, study DB, or published winning-weight artifact was located. Exact winning-trial replay therefore remains unavailable without rerunning search.
- **Current public OptiMer search has reproducibility hazards:** unseeded Optuna/Python RNG; paper/code default mismatch (`100` trials and `100→300` proxy/top-K sample limits in paper vs code defaults `50` and `300→100`); negative-weight experiments require explicit range override.
- **Current public code has a high-impact CPT-name collision risk.** It names weight parameters from each model path's parent directory. Sibling checkpoint paths like the official README example can therefore produce the same Optuna parameter name and silently tie distinct CPT weights. Treat this as a public-code defect only, not evidence about the paper's internal experiment implementation.
- **Data Mixing Agent acquisition is pinned:** 384 trajectories, 50M proxy models, 27,266 feedbacks, `1996.08 GPU h` proxy/evaluation acquisition, 2.1M agent with SFT+CQL under 10 min. The paper's `52` vs `54` dimensional wording remains internally inconsistent.
- Data Mixing Agent, ELLA, SpaRTA/TSR/FST/TFGN/Share/SLoRA/FLEX/CLDD/replay/plasticity/world-model/drift branches remain live with prior scope guards.

Exact next action:
1. Search for Table-1 winning weights, original study DB, checkpoints/model hashes or an archival artifact outside the current OptiMer GitHub roots; otherwise keep the label `deterministic reconstruction`, not exact replay.
2. Specify a budget-matched comparison of uniform DataMix vs RegMix/learned online mixing vs OptiMer post-hoc composition vs OptiMer-derived-ratio retraining, including evaluator queries, controller acquisition, training FLOPs, objective-switch cost and persistent checkpoint/vector storage.
3. Quantify full-27B checkpoint/delta persistence and restart cost versus Data Mixing Agent controller + trajectory/evaluation corpus persistence.
4. Test whether OptiMer survives optimized mixing, longer-than-1B CPT and non-Gemma backbones before broad generalization.
5. Cross representative mixture controllers with the parameter-write axis only after holding data trajectories fixed.
6. Continue earlier live branches under exact tested-scope rules.

Frontier must remain nonempty.
