# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260827T1105_JST.md`.
Base accumulated state: `STATE.md`.
Matched data-mixing experiment contract: `MATCHED_DATA_MIXING_MANIFEST_v1.json`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain ending at `RUN_20260827T1105_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **DeMix `config.json` is now an explicit byte-equality class across all seven 30B checkpoint-7500 components.** The retrieved canonical raw serialization is exactly 727 UTF-8 bytes in every component; SHA-256 of that exact retrieved serialization is `199b96b3ab0f35d88b512fa29d5c0c3a6298b3727f6b0be5c0dba54546626f88`. This is a locally computed hash of the exact public raw bytes, not a claimed Xet/server digest.
- **DeMix `generation_config.json` is likewise identical across all seven components:** 143 bytes; SHA-256 `afe20b2d6db0b0d845dde7f43979a6f04fb700e446b453503b10f48bd2d8fd85` under the same raw-byte convention.
- The common model config pins Qwen3ForCausalLM, 28 layers, hidden size 2048, 16 attention heads/8 KV heads, max position 32768, `torch_dtype=float32`, `transformers_version=4.51.3`, and `use_cache=false`. These shared files should be deduplicated in a reconstruction, while the seven previously pinned `training_args.bin` payloads remain byte-distinct.
- **The released DeMix evaluation path is not deterministic paper-reproduction code.** `eval_merged/proxy_eval.py` generates synthetic `random.random()+index` benchmark values. `iterative_sample/train_predictor.py` reads OpenCompass outputs but selects unsorted wildcard matches and hard-codes summary CSV row numbers and score column 4, without validating benchmark/metric names.
- DeMix does not pin an OpenCompass version. For a public reconstruction only, use OpenCompass `0.5.1.post1@ecc86a2728c06fd2c1ad34f1d0094f42b5243c78` as a pre-paper stable anchor and `0.5.2@974179240a1a4e3c0ff14c60621cf1f6c95b287a` as a sensitivity comparator; do **not** claim the authors used the anchor. The two tags differ by 65 commits; target benchmark config files did not change in that interval, but core OpenICL evaluation/inference code and runtime requirements did, so output-schema/score equivalence must be tested rather than assumed.
- A replacement evaluator must extract by benchmark+metric name, record OpenCompass commit/config/schema/output hashes, and fail closed on missing or duplicate names instead of using `iloc` positions.
- DeMix `mix_16` remains unexplained; operational pairing remains `mix_0..15`.
- SAFE-Merge remains a protected-write/model-composition candidate with acquired-task performance, BWT, held-out general knowledge, merge fidelity, offline merge cost, total training cost and durable storage kept separate.

Exact next action:
1. Complete byte-level equality classes for `added_tokens.json`, `special_tokens_map.json`, `tokenizer_config.json`, `tokenizer.json`, `vocab.json`, `merges.txt`, model index and `trainer_state.json`; explain the 140/141 kB trainer-state split by content rather than size.
2. Build a deterministic name-keyed OpenCompass adapter at `0.5.1.post1`, then run an identical tiny fixture at `0.5.2` to measure score/schema sensitivity before paper-scale evaluation.
3. If a non-executing safe parser is available, compare relevant `training_args.bin` fields while keeping the seven SHA-256 values as byte-identity authority.
4. Continue source-qualified search for orphan `mix_16` metadata.
5. Continue SAFE-Merge reconstruction/code search and the reduced displacement sweep.
6. Continue earlier selective-write/routing, replay/plasticity, world-model, task-free/drift and CLDD branches under exact tested-scope rules.

Frontier must remain nonempty.