# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260827T0102_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, `RUN_20260826T1407_JST.md`, `RUN_20260826T1501_JST.md`, `RUN_20260826T1601_JST.md`, `RUN_20260826T1703_JST.md`, `RUN_20260826T1758_JST.md`, `RUN_20260826T1807_JST.md`, `RUN_20260826T1808_JST.md`, `RUN_20260826T2002_JST.md`, `RUN_20260826T2104_JST.md`, `RUN_20260826T2157_JST.md`, `RUN_20260826T2302_JST.md`, `RUN_20260827T0008_JST.md`, and `RUN_20260827T0102_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **Data Mixing Agent adds a separate control axis:** parameter-write protection/routing and data/replay-mixture scheduling should be evaluated independently. ACL 2026 Data Mixing Agent learns a 2.1M-parameter feedback-driven domain-mixture policy from 384 proxy trajectories with offline CQL. On the reported LLaMA-DCLM math continual-pretraining setup, DataAgent-RL reaches balanced average `47.03` versus RegMix `44.01` and DBL `43.50`, while the main target run uses fewer GPU hours than RegMix.
- **Its apparent efficiency must include acquisition cost.** Proxy trajectory collection/evaluation costs `1996.08 GPU h`; SFT+CQL for the small controller is under 10 minutes. The controller therefore becomes attractive only when its policy transfers/amortizes across enough future model/domain adaptations. Main-run savings alone are not total-cost savings.
- **Data efficiency is concrete but scoped:** DataAgent-RL stops at `19.92B` of a nominal `21B` token budget and the paper reports `2.14B` fewer source-field tokens while outperforming RegMix on general+math balance. It still requires a source/target mixture or synthetic-source substitute, explicit domain organization, and an evaluation-feedback signal; it does not solve hidden-boundary discovery.
- **ELLA artifact status remains weak:** fresh searches of the EACL/Amazon publication surfaces, the first author's public GitHub repositories, `amazon-science`, and exact-title public GitHub results found no ELLA implementation. Keep paper-level evidence but do not infer exact merge/discard/restart lifecycle from equations alone.
- SpaRTA/TSR/ELLA/FST/TFGN/Share/SLoRA/FLEX/CLDD/replay/plasticity/world-model/drift branches remain live with prior scope guards.

Exact next action:
1. Data Mixing Agent: locate public code/supplement and resolve the paper's internal `52` vs `54` domain-space wording; pin proxy-model/trajectory/evaluation acquisition cost precisely.
2. With one fixed updater, compare fixed replay ratio vs hand-coded/dynamic heuristic vs feedback-driven learned mixer, including controller acquisition, evaluation queries, source-token use, target training compute, durable state and restart cost.
3. Cross the winning/representative data-mixture controllers with single shared LoRA, static shared/specific split, ELLA-style selective de-correlation and unsupervised routing under identical trajectories.
4. ELLA: continue artifact search; if unavailable, build only a clearly labeled equation-level reconstruction rather than claiming exact reproduction.
5. Continue SpaRTA hidden-boundary falsification and TSR persist/reload/full-byte accounting, plus earlier live branches under exact tested-scope rules.

Frontier must remain nonempty.
