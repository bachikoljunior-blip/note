# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T2302_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, `RUN_20260826T1407_JST.md`, `RUN_20260826T1501_JST.md`, `RUN_20260826T1601_JST.md`, `RUN_20260826T1703_JST.md`, `RUN_20260826T1758_JST.md`, `RUN_20260826T1807_JST.md`, `RUN_20260826T1808_JST.md`, `RUN_20260826T2002_JST.md`, `RUN_20260826T2104_JST.md`, `RUN_20260826T2157_JST.md`, and `RUN_20260826T2302_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **Fast-Slow Training (FST) added as a high-value provisional LLM continual-learning control.** It co-evolves slow model weights with a population of textual fast weights/prompts. Primary paper reports 3.0x/1.4x/3.0x fewer steps to RL peak on CodeIO/Math/HoVer, higher fitted asymptotes, up to 70% lower KL at matched reward, and materially better later-task plasticity.
- **FST continual run has stronger task-free properties than first assumed:** the authors' official blog says the HoVer→CodeIO→Physics continual run uses 100% task-agnostic seed prompts and the prompt optimizer autonomously changes the system prompt in response to changing data. But the stream still changes externally every 200 steps and is not a smooth unknown-boundary mixture.
- **FST compute/reproducibility scope:** equal optimizer steps are not equal compute; GEPA/reflection is extra work and uses `gpt-5.2`. The advertised public code page still says code is coming soon, so prompt persistence/reset, RNG/model pinning and exact continual-run lifecycle remain unverified from code.
- **TFGN evidence scope tightened further:** its paper explicitly says architecture/code/weights/reproducible recipe are NDA-gated pending patent prosecution and that headline BWT/HellaSwag results are single-seed point estimates without confidence intervals. Extension A publicly exposes a five-role capability loop (sensing, next-state prediction, surprise gating, stability-triggered consolidation, cross-layer coupling) and an ablation ladder `-0.06010 → -0.03880 → -0.01900 → -0.01140` BWT at ~398M/1B-token phases, but the core write-separation lever remains undisclosed.
- **New matched-comparison axis:** external fast-context offloading (FST) vs dense shared read/protected write (public TFGN surrogate) vs routed expert state vs single shared slow state. Compare under identical stream/storage/compute while separately scoring BWT, new-task acquisition, plasticity, KL drift, gradient interference, prompt/context overhead, restart persistence, task-boundary supervision, replay and total GPU-hours.
- Earlier Share/SLoRA/FLEX/CLDD/replay/plasticity/world-model/drift frontiers remain live with their existing scope guards.

Exact next action:
1. FST: watch for the promised code release; inspect continual-run data loader, reward/verifier switching, `Phi` carryover/reset, archival state, and reproducibility pins.
2. FST: construct/find a continuously changing language mixture with no exposed stage boundary; measure fast-context persistence/storage/token cost and compare carryover vs reset.
3. TFGN: continue public patent/code/independent-replication search. Until the core lever is public, keep its numbers single-seed/unreproduced.
4. Build only a clearly labeled public surrogate for the disclosed TFGN principle: dense shared read + input-conditioned write partition + surprise gating + stability consolidation.
5. Run/seek a matched comparison of single shared state vs FST-like fast context vs protected-write surrogate vs routing under equal data, storage, replay=0 and total compute.
6. Continue Share/SLoRA/FLEX/CLDD/replay/plasticity/world-model/drift-detector frontier under exact-scope rules.

Frontier must remain nonempty.
