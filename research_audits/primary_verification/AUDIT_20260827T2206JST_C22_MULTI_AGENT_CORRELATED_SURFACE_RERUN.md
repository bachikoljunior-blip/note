# Primary verification audit — C22 multi_agent correlated dependency-surface synthetic study

Observed: 2026-08-27T22:06:00+09:00
Verifier semantic tuple remains frozen at note `76f8f14c697b65938f3dbabcda310b47293faf12` / control revision 28 / primary_source_verifier config revision 8.
Clean source tuple: `research_workers_clean_g1/multi_agent/FOLLOWUP_2026-08-27_1806_JST.md` @ blob `ac35cc4d988e2328c15f9db7c2d27e7680472195`.
Pinned experiment script: `research_workers_clean_g1/multi_agent/SYNTHETIC_CORRELATED_SURFACE_BLINDSPOT_2026-08-27_1805.py` @ blob `7813bf97bb91ec2dbf858ba81d2bfe318d51935e`.

## Verdict

**MECHANISM DIRECTION REPRODUCED, REPORTED EXACT NUMBERS NOT CROSS-RUNTIME REPRODUCED.** A clean independent execution of the pinned algorithm under Python `3.13.5` preserves the qualitative ordering and central safety conclusion, but does not reproduce the checkpoint's displayed table values. The script does not persist the Python interpreter/runtime identity that generated the historical table, and it uses `random.sample`, `random.choices` and `randrange`; Python's own reproducibility notes guarantee cross-version stability only for the core `Random.random()` sequence, while other random-module algorithms may change across Python versions.

## Independent rerun of the pinned algorithm

Using the script's exact constants and SHA-derived seeds (`N=28`, `TRAIN_GRAPHS=3000`, `TEST_GRAPHS=6000`) under Python 3.13.5, the verifier obtained:

- train conditional complement:
  - conditional_routing: `1.0`
  - dynamic_tool: `0.9017496635`

Policy results:

| policy | recovery | mean replay cost | correct endpoints / 100k cost | custom_wrapper recovery |
|---|---:|---:|---:|---:|
| runtime-local only | `0.6212` | `10.66` | `5825.4` | `0.4977` |
| pooled high-recall -> union | `0.9407` | `11.75` | `8008.7` | `0.9095` |
| per-surface conditional complement | `0.9977` | `19.46` | `5127.0` | `1.0000` |
| positive-proof-only | `1.0000` | `22.42` | `4459.3` | `1.0000` |
| whole redraw | `1.0000` | `28.00` | `3571.4` | `1.0000` |

The checkpoint reported approximately `0.6247 / 10.35`, `0.9395 / 11.42`, `0.9963 / 18.98`, and `1.0000 / 21.83` for the first four policies. Those exact values were not reproduced in this interpreter.

An independent reconstruction of test-surface marginals under Python 3.13.5 also gives approximately:

- conditional_routing runtime/static/conditional-complement: `0.8210 / 1.0000 / 1.0000`;
- dynamic_tool: `0.8215 / 0.8988 / 0.8967`;
- custom_wrapper: `0.8193 / 0.9004 / 0.5538`.

These differ somewhat from the checkpoint's `0.8202/1.0000/1.0000`, `0.8177/0.8995/0.8998`, `0.8158/0.8965/0.5293`.

## What remains stable

Despite the numeric shift, the important qualitative relationships survive:

- custom_wrapper has marginal runtime/static recall close to dynamic_tool but much weaker residual static value after a runtime miss;
- pooled marginal-recall routing retains a nonzero stale-state failure rate;
- positive-proof-only is the only non-whole policy in this scoped script that reaches 100% recovery;
- whole redraw is safest but has the highest replay cost;
- empirical high recall / conditional complement is not equivalent to a completeness proof for destructive replacement.

Therefore the mechanism conclusion is not falsified by this rerun, but the checkpoint's displayed decimals should not be treated as interpreter-independent deterministic constants.

## Reproducibility defect and repair

Python documentation states that most `random` module algorithms and seeding functions are subject to change across Python versions; the guaranteed invariant is the sequence returned by `Random.random()` for a compatible seeder. The pinned script calls higher-level `sample`, `choices` and `randrange`, so a hash-derived seed alone is insufficient for cross-Python exact replay.

To make future synthetic receipts exact, persist at minimum:

- Python implementation/version;
- script blob SHA;
- constants and sample counts;
- stdout or machine-readable result artifact;
- preferably replace higher-level version-sensitive sampling with an explicitly pinned RNG library/version or a self-contained sampler built from a specified core bitstream.

Scope guard: this is a synthetic mechanism study, not a deployment benchmark or an estimate of real multi-agent provenance-capture failure rates.

No exploration worker state, worker feedback, comparator output, O state, or feed was modified by this audit.