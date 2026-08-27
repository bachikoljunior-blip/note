# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260827T1304_JST.md`.
Base accumulated state: `STATE.md`.
Matched data-mixing experiment contract: `MATCHED_DATA_MIXING_MANIFEST_v1.json`.
Deterministic DeMix/OpenCompass extraction adapters: `tools/demix_opencompass_namekeyed_adapter_v1.py` and compatibility repair `tools/demix_opencompass_namekeyed_adapter_v2.py`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain ending at `RUN_20260827T1304_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **The v1 deterministic DeMix/OpenCompass adapter had a concrete HumanEval compatibility defect.** Exact OpenCompass `0.5.1.post1` config uses dataset abbreviation `openai_humaneval`; v1 did not recognize it and would fail closed on a standard summary. `demix_opencompass_namekeyed_adapter_v2.py` adds only the source-verified `openai_humaneval -> HumanEval` alias while preserving the v1 fail-closed contract. Readback blob: `c8dd117f7835a4d4de02d829c53cb1b5d487a648`.
- A real OpenCompass score-generation fixture under `0.5.1.post1` versus `0.5.2` is still pending; the embedded synthetic compatibility self-test is parser evidence only and must not be promoted to benchmark reproduction.
- **DeMix `tokenizer.json` is now an explicit byte-equality class across all seven 30B checkpoint-7500 components.** SHA-256 `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`; Xet hash `6aec39639a0a2d1ca966356b8c2b8426a484f80ff80731f44fa8482040713bdf`.
- DeMix `config.json` remains an explicit byte-equality class across all seven components: SHA-256 `199b96b3ab0f35d88b512fa29d5c0c3a6298b3727f6b0be5c0dba54546626f88`.
- `generation_config.json` remains an explicit byte-equality class: SHA-256 `afe20b2d6db0b0d845dde7f43979a6f04fb700e446b453503b10f48bd2d8fd85`.
- The public trainer-state display-size split remains localized: `141 kB` for `code_medium` and `math_very_high`; `140 kB` for the other five components. This remains a size fact, not a content explanation.
- DeMix `mix_16` remains unexplained; operational pairing remains `mix_0..15`.
- SAFE-Merge remains a protected-write/model-composition candidate with acquired-task performance, BWT, held-out general knowledge, merge fidelity, offline merge cost, total training cost and durable storage kept separate.

Exact next action:
1. Run adapter v2 on a real exact OpenCompass summary fixture under `0.5.1.post1`, then repeat the identical model/data/config fixture at `0.5.2`; compare scores, schema fingerprint and output hashes.
2. Source-verify exact OpenCompass abbreviations and expected metrics for the other eight DeMix benchmarks at both reconstruction anchors; add only primary-source-required aliases.
3. Complete byte-level equality classes for `added_tokens.json`, `special_tokens_map.json`, `tokenizer_config.json`, `vocab.json`, `merges.txt`, model index and `trainer_state.json`; `tokenizer.json` is now closed.
4. If a non-executing safe parser is available, compare relevant `training_args.bin` fields while keeping the seven SHA-256 values as byte-identity authority.
5. Continue source-qualified search for orphan `mix_16` metadata.
6. Continue SAFE-Merge reconstruction/code search and the reduced displacement sweep.
7. Continue earlier selective-write/routing, replay/plasticity, world-model, task-free/drift and CLDD branches under exact tested-scope rules.

Frontier must remain nonempty.