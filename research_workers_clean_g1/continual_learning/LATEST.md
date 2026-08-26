# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260827T0501_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain ending at `RUN_20260827T0501_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **DeMix current public rank-consistency code is incomplete, not merely under-pinned.** `eval_merged/proxy_eval.py` currently returns synthetic `random.random()+index` benchmark values instead of parsing OpenCompass output. The README's rank-consistency reproduction path therefore needs missing evaluation extraction code/results plus a pinned OpenCompass contract.
- **DeMix's concrete CSV parser is brittle.** `iterative_sample/train_predictor.py` hard-codes benchmark row numbers and score column 4, uses unversioned OpenCompass, and selects unsorted glob matches. Version/schema and filesystem-order drift can change interpreted scores.
- **DeMix has a public mapping mismatch:** current `reference_models` contains 16 model directories `mix_0..mix_15`, while `sampled_mixture.json` contains 17 keys `mix_0..mix_16`, despite the README claiming 16 corresponding mixtures. Resolve before assuming id equality.
- **Representative 30B component identity is now pinned:** `general_target/checkpoint-7500/model-00001-of-00002.safetensors` SHA-256 `cb4fccd9f51d3229117c6e27c94faba5683a5d41970860e3a62b5c5f06ae5b29`, 4.97 GB. Current public DeMix HF main observed is `82a2eff...`, but the reproduction guide does not designate an immutable paper snapshot.
- **OptiMer weight availability is partly better than previously recorded.** arXiv v2 Table 4 publishes exact objective-specific winning weights. Example Japanese objective `[0,1]`: `it=.569, ja=.055, zh=.006, en=.129, math=.489, code=.033`, score `73.37`. Chinese and Math objective weights are also tabulated, plus negative-weight variants.
- **OptiMer exact trial replay remains unavailable.** Official NICT GitHub main remains `582cf63d...`; no winning `optuna.db` or Gemma CPT/vector model bundle was found in the current NICT Hugging Face organization. Main Table-1 combination-specific weights were not recovered as exact machine-readable values in this run; distinguish them from the exact Table-4 objective weights.
- Earlier OptiMer/DeMix/Data Mixing Agent/ELLA/SpaRTA/TSR/FST/TFGN/Share/SLoRA/FLEX/CLDD/replay/plasticity/world-model/drift branches remain live under their prior scope guards.

Exact next action:
1. Resolve DeMix 17-mixture/16-model mapping via reference-model training metadata/history; identify any orphan/shifted entry.
2. Inspect `proxy_eval.py` history and released evaluation outputs/configs for a real OpenCompass parser and paper-pinned evaluator version.
3. Pin SHA-256 for all seven 30B `checkpoint-7500` component sources and one immutable HF dataset revision containing the complete artifact set.
4. Recover exact OptiMer Table-1 combination weights from arXiv source/Figure-4 data if possible; otherwise explicitly classify them as figure-only and use Table-4 weights as the exact public positive control.
5. Search later NICT/HF releases for CPT/vector artifacts and study DB.
6. Materialize the five-path matched experiment manifest with identical model/data/evaluator/seed/displacement contracts.
7. Continue earlier live branches under exact tested-scope rules.

Frontier must remain nonempty.
