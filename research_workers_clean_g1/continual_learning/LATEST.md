# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260827T0404_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, `RUN_20260826T1407_JST.md`, `RUN_20260826T1501_JST.md`, `RUN_20260826T1601_JST.md`, `RUN_20260826T1703_JST.md`, `RUN_20260826T1758_JST.md`, `RUN_20260826T1807_JST.md`, `RUN_20260826T1808_JST.md`, `RUN_20260826T2002_JST.md`, `RUN_20260826T2104_JST.md`, `RUN_20260826T2157_JST.md`, `RUN_20260826T2302_JST.md`, `RUN_20260827T0008_JST.md`, `RUN_20260827T0102_JST.md`, `RUN_20260827T0204_JST.md`, `RUN_20260827T0209_JST.md`, `RUN_20260827T0302_JST.md`, and `RUN_20260827T0404_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **DeMix artifacts are strongly content-addressed but the public search generator is not fully deterministic.** `Lucius-lsr/DeMix@d0c945ca84d5632c6ed1bfe469337cf880757422` seeds NumPy to 42 in `sample.py` but uses Python `random.choice`/`random.sample` without `random.seed`; candidate mixtures therefore cannot be exactly regenerated from the stated NumPy seed alone. Evaluation discovery also uses unsorted `glob` selection, and the repo has no dependency lock/environment pinning.
- **DeMix model identity is nevertheless unusually inspectable.** The Hugging Face reproduction release exposes LFS/Xet SHA-256 and sizes; e.g. one released Qwen3-1.7B reference-model shard is SHA-256 `3ec6c05c9f12fa1dd1ad4e637a351e7a146e04caa7eacb2921c80b308e82a4fb`, size `4,969,539,560` bytes. Current release surface is ~`6.1 TB`, with ~`552 GB` of reference models.
- **OptiMer now has an official NICT code release with a much stronger environment contract.** `nict-astrec-att/optimer@582cf63d3dfef8fa6d7e35068afa412288147c5b` pins Python 3.11, torch/transformers/Optuna/lm-eval/vLLM/etc. and mergekit commit `d4b4b6c...`. Correct the older state that treated its software environment as largely unpinned.
- **OptiMer exact paper replay is still unavailable.** The official script does not seed TPE/CMA/random Optuna samplers; the repo has no winning paper `optuna.db`, model/checkpoint/distribution-vector hashes, Table-1 weight artifact, or GitHub release. Treat public reruns as re-search/deterministic reconstruction only after explicit seeding.
- **Conditional current-code defect:** OptiMer names CPT weight parameters from `Path(checkpoint).parent.name`. The README sibling-path example `/path/to/japanese_ckpt /path/to/math_ckpt` gives the same parent name `to`, which reuses one Optuna parameter name and couples CPT weights. This only applies when parent names collide; do not infer the internal paper run did so.
- **Matched falsifier is now sharper:** same backbone/data/components, compare uniform real DataMix, trained-proxy ratio search, DeMix merged-proxy ratio search + real retraining, OptiMer post-hoc composition, and OptiMer-derived-ratio retraining; explicitly seed all randomness and sweep parameter displacement while measuring merge-vs-real-mixture fidelity, storage and restart cost.
- Earlier OptiMer/DeMix/Data Mixing Agent/ELLA/SpaRTA/TSR/FST/TFGN/Share/SLoRA/FLEX/CLDD/replay/plasticity/world-model/drift branches remain live under their prior scope guards.

Exact next action:
1. Inspect DeMix `component_models` history and record representative component-model LFS SHA-256 plus `sampled_mixture.json` identity; determine whether the 30B consistency experiment is pinned to one HF revision.
2. Inspect DeMix OpenCompass/evaluation version/config pinning and quantify which unsorted-glob cases can alter search scores.
3. Extract OptiMer paper winning weights and compare them with the corrected public-search parameterization after unique checkpoint names + explicit sampler seeds; search for later NICT study/model releases.
4. Write an executable small-scale matched protocol for the five mixture paths with identical component models, objective, seed family and displacement sweep.
5. Quantify dense checkpoint/vector persistence versus compressed/sparse deltas and objective-switch amortization.
6. Cross representative mixture controllers with the parameter-write axis only after holding data trajectories fixed.
7. Continue earlier live branches under exact tested-scope rules.

Frontier must remain nonempty.
