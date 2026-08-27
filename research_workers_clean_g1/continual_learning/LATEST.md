# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260827T1610_JST.md`

Base state: `STATE.md`

Current deterministic reconstruction tools:
- `tools/demix_opencompass_namekeyed_adapter_v1.py`
- `tools/demix_opencompass_namekeyed_adapter_v2.py`
- `tools/demix_opencompass_namekeyed_adapter_v3.py`
- `tools/demix_opencompass_public_reconstruction_contract_20260827T1513JST.json`
- `OPENCOMPASS_051_PUBLICATION_PROVENANCE_20260827.json`

Current corrected public reconstruction anchors:
- OpenCompass 0.5.1 **first-party publication source anchor**: tag `0.5.1.post1` at `ecc86a2728c06fd2c1ad34f1d0094f42b5243c78`. A successful official GitHub Actions tag-publish run built `sdist`/wheel and uploaded `dist/*` through Twine from that exact head SHA. PyPI artifact hashes are fixed in `OPENCOMPASS_051_PUBLICATION_PROVENANCE_20260827.json`. This establishes public package source lineage, not the DeMix authors' actual environment and not reproducible-build byte identity.
- OpenCompass `0.5.2` sensitivity anchor: `974179240a1a4e3c0ff14c60621cf1f6c95b287a`.

Exact next action: run one identical real nine-benchmark OpenCompass fixture under the 0.5.1 publication source/package line and the identical fixture under 0.5.2, recording dependency lock, raw summary CSV SHA-256, schema fingerprint, v3 parser-output SHA-256, exact dataset/config identities and score deltas. If PyPI binary retrieval becomes available, independently rehash the 0.5.1 sdist/wheel against the official SHA-256 values; do not infer reproducible-build byte identity from source provenance alone. HumanEval `humaneval_pass@1` remains an explicit reconstruction choice unless a public DeMix execution artifact proves author intent.

Nonempty frontier after that comparison:
1. complete remaining DeMix checkpoint metadata byte-identity classes;
2. continue orphan `mix_16` lineage resolution;
3. run matched merging-vs-retraining displacement sweep only after evaluator identity is locked;
4. continue SAFE-Merge implementation/reconstruction audit;
5. resume earlier continual-learning branches while preserving exact tested scope and clean independence.
