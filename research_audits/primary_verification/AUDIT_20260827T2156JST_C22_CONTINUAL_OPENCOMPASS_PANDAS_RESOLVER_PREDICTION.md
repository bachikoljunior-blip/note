# Primary verification audit — C22 continual_learning OpenCompass 0.5.1/0.5.2 pandas resolver prediction

Observed: 2026-08-27T21:56:00+09:00
Verifier semantic tuple remains frozen at note `76f8f14c697b65938f3dbabcda310b47293faf12` / control revision 28 / primary_source_verifier config revision 8.
Clean source tuple: `research_workers_clean_g1/continual_learning/RUN_20260827T1801_JST.md` @ blob `a33fa0171002928b292ea941f823a5a4dcdd428b`, with machine-readable boundary `OPENCOMPASS_051_052_TRACK_A_DEPENDENCY_BOUNDARY_20260827.json` @ blob `cfdde9e1663462869dcef105887afba952bfb3cb`.

## Verdict

**STATIC RELEASE-TIME PREDICTION VERIFIED; ACTUAL RESOLVER LOCK STILL UNOBSERVED.** The exact OpenCompass source anchors and PyPI release/Python metadata support the worker's prediction that, under a fresh Python 3.10 environment at the 0.5.2 release date and absent transitive/external constraints, 0.5.1's top-level `pandas<2.0.0` ceiling selects pandas 1.5.3 while 0.5.2's unbounded `pandas` can select pandas 2.3.3. This is not evidence that the historical OpenCompass environments actually resolved those versions.

## Exact source-anchor delta

OpenCompass anchor `ecc86a2728c06fd2c1ad34f1d0094f42b5243c78` has in `requirements/runtime.txt`:

- `pandas<2.0.0`
- `pyext`

OpenCompass anchor `974179240a1a4e3c0ff14c60621cf1f6c95b287a` has:

- `pandas`
- `# pyext`

The rest of the visible runtime requirement lines are equal between the two frozen files. This directly verifies the worker's top-level dependency-delta statement.

Primary source URLs:
- `https://github.com/open-compass/opencompass/blob/ecc86a2728c06fd2c1ad34f1d0094f42b5243c78/requirements/runtime.txt`
- `https://github.com/open-compass/opencompass/blob/974179240a1a4e3c0ff14c60621cf1f6c95b287a/requirements/runtime.txt`

## Release-time package facts

PyPI reports:

- OpenCompass `0.5.1` uploaded 2025-10-17.
- OpenCompass `0.5.2` uploaded 2026-02-14.
- pandas `1.5.3` released 2023-01-19 and requires Python `>=3.8`.
- pandas `2.3.3` was already released before OpenCompass 0.5.2 and requires Python `>=3.9`, including Python 3.10.
- pandas `3.0.0` requires Python `>=3.11`, so it is not an admissible Python-3.10 candidate even though the 3.0 line existed by the 0.5.2 release date.

Therefore, with only the stated top-level pandas constraint and Python 3.10 compatibility considered, the worker's `1.5.3` versus `2.3.3` prediction is consistent with public package metadata.

## Scope guard

This audit does **not** execute pip's historical resolver and does not prove the final package-native environment. A real fresh resolver can be constrained by transitive requirements, platform/wheel availability, external constraints files, installer version/behavior, cache/index state, prerelease policy, or other package metadata. Historical DeMix/OpenCompass runs may also have used an explicitly pinned or pre-existing environment.

Accordingly:

- keep `1.5.3 vs 2.3.3` labeled as a falsifiable release-time prediction under the worker's explicit assumptions;
- do not use it as observed provenance for any score delta until the two package-native resolver outputs are frozen and read back;
- the proposed Track A common-lock experiment remains the cleaner source-isolation experiment because it deliberately removes this dependency delta.

No exploration worker state, worker feedback, comparator output, O state, or feed was modified by this audit.