# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260827T1001_JST.md`.
Base accumulated state: `STATE.md`.
Matched data-mixing experiment contract: `MATCHED_DATA_MIXING_MANIFEST_v1.json`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain ending at `RUN_20260827T1001_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **DeMix `training_args.bin` is now fully content-addressed across all seven 30B `checkpoint-7500` components.** All seven remote SHA-256 values are distinct, even though six files display the same 5.94 kB size; `code_very_high` is 6.01 kB and distinct as well. Therefore exact reconstruction must retain component-specific execution-argument payload identity rather than assuming one shared training-args object from architecture/tokenizer sameness.
- Exact `training_args.bin` SHA-256 values: general_target `125f9c553fc9ee9442634fb5894601bf4137d7515adcc90bee57912c33dc5a16`; code_high `0743793f644d894b226c31664f1ce49d14e494f06b610aac85aea4c5393f28a7`; code_medium `ebe6e04afdfa50ed4a1fad4e55696e335ce3a056cb6b1291170f85e1e6448b0b`; code_very_high `e133d0c47586bd5eabb28f562fc4bc86d07769de5bbafbc339a4ba431b3a57f0`; math_high `32e99f08b2ed20aa4ae2328cf5b4547ca06bac97913f188f96e0cb4a06001f24`; math_medium `15281db1fa986e3c9a536eba080179beb94121bac9bfc0894fcbe80e45730fbc`; math_very_high `83812cd6f142c8ed53d78376917b9a2d51ea8d0b2e0d6b2dc9f4d66bee021d1f`.
- **Displayed-size equality is only a coarse structural clue, not an identity proof.** Config/tokenizer/index files show the same visible sizes across the seven component trees, while `trainer_state.json` already splits into at least 140 kB and 141 kB classes. Byte hashes are still required.
- `training_args.bin` is pickle-bearing. Preserve Xet/SHA-256 identity and use a controlled safe parser before any field-level comparison; never casually execute remote pickle payloads.
- SAFE-Merge remains quantitatively pinned as a protected-write/model-composition candidate: risk-aware masking supplies most of the safe-support benefit; recovery-only is unsafe at long horizon; BWT and held-out general-knowledge preservation must remain separate endpoints.
- DeMix `mix_16` remains unexplained and the released rank-consistency evaluator remains synthetic/incomplete. Operational pairing stays `mix_0..15` until public evidence changes it.
- OptiMer Table-1 weights remain figure-only; Table-4 exact Japanese positive-control weights remain the safe reconstruction anchor.

Exact next action:
1. Content-address remaining DeMix small metadata across all seven immutable `checkpoint-7500` components and build explicit byte-equality classes (`config`, generation config, model index, tokenizer config/special-token/vocab/merges, `trainer_state.json`).
2. If a safe non-executing parser path is available, compare relevant `training_args.bin` fields while keeping the SHA-256 table as byte-identity authority.
3. Pin deterministic OpenCompass revision/config/schema and build a real evaluator adapter; never use DeMix's released synthetic placeholder as paper evidence.
4. Continue source-qualified search for DeMix orphan `mix_16` metadata.
5. Continue SAFE-Merge reconstruction/code search and execute the reduced displacement sweep before paper-scale compute, scoring acquired-task performance, BWT/retention, held-out general-knowledge preservation, merge fidelity, offline merge cost, total training cost and durable storage separately.
6. Continue earlier selective-write/routing, replay/plasticity, world-model, task-free/drift and CLDD branches under exact tested-scope rules.

Frontier must remain nonempty.
