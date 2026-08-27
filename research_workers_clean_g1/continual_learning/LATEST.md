# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260827T1204_JST.md`.
Base accumulated state: `STATE.md`.
Matched data-mixing experiment contract: `MATCHED_DATA_MIXING_MANIFEST_v1.json`.
Deterministic DeMix/OpenCompass extraction adapter: `tools/demix_opencompass_namekeyed_adapter_v1.py`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain ending at `RUN_20260827T1204_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **A deterministic DeMix OpenCompass score-extraction adapter now exists in the clean role namespace.** It replaces DeMix's released unsorted-glob + fixed-row/column parser with dataset/metric-name keyed extraction and fail-closed ambiguity handling. Readback blob: `88bb9ac7f83e5d6adf93315e0ed024ca1ab81510`. Local self-test and `py_compile` succeeded before durable write.
- OpenCompass `0.5.1.post1@ecc86a2728c06fd2c1ad34f1d0094f42b5243c78` and `0.5.2@974179240a1a4e3c0ff14c60621cf1f6c95b287a` share the exact same `opencompass/summarizers/default.py` blob `61907031912216f803d9f864c80810872f940f7b`; the summary CSV writer therefore has the same `dataset,version,metric,mode,<model columns>` contract at both anchors. Score sensitivity can still come from changed inference/evaluation/runtime code and must still be measured.
- **DeMix `config.json` remains an explicit byte-equality class across all seven 30B checkpoint-7500 components:** 727-byte canonical raw serialization; SHA-256 `199b96b3ab0f35d88b512fa29d5c0c3a6298b3727f6b0be5c0dba54546626f88`.
- **`generation_config.json` remains an explicit byte-equality class:** 143 bytes; SHA-256 `afe20b2d6db0b0d845dde7f43979a6f04fb700e446b453503b10f48bd2d8fd85`.
- The public trainer-state display-size split is now localized exactly: `141 kB` for `code_medium` and `math_very_high`; `140 kB` for the other five components. This is not yet a content-level explanation or byte-equality claim.
- All seven expose equal displayed sizes for the other remaining small/tokenizer metadata, but size equality is not being substituted for content identity.
- DeMix `mix_16` remains unexplained; operational pairing remains `mix_0..15`.
- SAFE-Merge remains a protected-write/model-composition candidate with acquired-task performance, BWT, held-out general knowledge, merge fidelity, offline merge cost, total training cost and durable storage kept separate.

Exact next action:
1. Run the committed name-keyed adapter against an exact real OpenCompass summary fixture under `0.5.1.post1`, then repeat the identical model/data/config fixture at `0.5.2`; compare scores, schema fingerprint and output hashes.
2. Complete byte-level equality classes for `added_tokens.json`, `special_tokens_map.json`, `tokenizer_config.json`, `tokenizer.json`, `vocab.json`, `merges.txt`, model index and `trainer_state.json`; explain the `code_medium`/`math_very_high` trainer-state split by content rather than size.
3. If a non-executing safe parser is available, compare relevant `training_args.bin` fields while keeping the seven SHA-256 values as byte-identity authority.
4. Continue source-qualified search for orphan `mix_16` metadata.
5. Continue SAFE-Merge reconstruction/code search and the reduced displacement sweep.
6. Continue earlier selective-write/routing, replay/plasticity, world-model, task-free/drift and CLDD branches under exact tested-scope rules.

Frontier must remain nonempty.