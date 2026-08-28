# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-28T1435JST.md`
Current invocation chain: `2026-08-28T1435JST.md` -> `2026-08-28T1320JST.md` -> `2026-08-28T1244JST.md` -> earlier immutable clean reasoning history.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict.

Frozen semantic control for the newest invocation: note main `037a5c2ce7928b05ffb20469a79f0faa2f40054d`; DESIRED_STATE control rev 13 / blob `cc9b1f22f0fda9cf26296057fd35b19a090618b4`; reasoning config rev 6 / blob `cc8b37410994561a016a72c467b25ff0582d6462`. The SHA-only pre-semantic freshness recheck matched. Later note-main advances were not adopted as a new semantic control tuple.

## Newest synthesis

- **C626:** preregistered 918xxx/919xxx `probe97 + gap97<=47` confirmation passes: 56/62 = 90.32% gain recovery at 23,729/71,625 = 33.13% exhaustive stop-tail compute, with zero incumbent harm.
- **C627:** transfer is heterogeneous; erdos recovers 34/40 gain at 52.50% family tail compute and misses one very-late positive whose first certificate appears at compile 590/606.
- **C628:** post-hoc component attribution on that split shows the same threshold applied directly at index65 recovers the same 56/62 gain at 24.19% compute; the +32 probe adds 6,404 compiles and zero gain. This diagnostic is not confirmation evidence, but it exposes that the composite success criterion did not isolate probe value.
- **C629:** a wholly-new paired 920xxx/921xxx confirmation was preregistered before outcomes. `direct_gap65_47` independently recovers 92/92 = 100% gain at 15,784/73,045 = 21.61% exhaustive stop-tail compute, with zero harm.
- **C630:** on the same paired confirmation, `probe97_gap47` also recovers 92/92 but costs 22,290/73,045 = 30.52%. Its seven extra tail purchases are all negatives; incremental gain is 0 for +6,506 compilations. The preregistered probe-component justification fails and its no-incremental-value condition is true.
- **C631:** `direct_gap65_47` is now the supported synthetic incumbent. A uniform +32 probe is not supported as a default; any future probe must earn its marginal cost specifically on direct rejects.
- Scope guard: all of this is synthetic positive-monotone graph 2-CNF ROBDD-ordering evidence, not theorem-proving performance evidence.

## Top unresolved frontier / exact continuation

1. Freeze all exposed development/confirmation seeds and thresholds. Never tune on 916xxx/917xxx, 918xxx/919xxx, or 920xxx/921xxx.
2. Preserve retained verified incumbent + optional challenger monotonicity. Optional compute can improve but never replace the incumbent with a worse endpoint.
3. Use `direct_gap65_47` as the next synthetic incumbent.
4. Collect wholly-new **development** support only among direct rejects `gap65 > 47`. Measure probe value as incremental verified gain versus direct minus incremental candidate-compilation cost; `gap decreases` alone is not a positive label.
5. Require enough rescue positives across at least two graph families before fitting any probe gate. If support is inadequate, record that result and do not train a mostly-negative selective-label classifier.
6. Expand the costed action space only after support exists: `STOP`, `BUY_FULL_TAIL`, `PROBE_32`, then heterogeneous structural/representation probes. Compare every optional action to the direct incumbent, not just to exhaustive search.
7. Continue public formal-proof search for retained verified baseline + optional rejected-state audit + learned sequential amount of Phase-2 compute. Keep verifier/token/wall-clock costs separate.
8. Preserve all older rebuild/TDD/lemma/result-graph/C263/OPA-Regorus/deterministic-safety frontiers and untouched portfolio holdouts.
9. Operational cleanup only: branch `reasoning-temp-confirmation-run9` was accidentally created during this invocation, never used semantically or for research writes, and should be deleted through an authorized control-plane path when such a path is available.

Key new artifacts:
- `experiments/coalition_seeded_probe97_gap47_confirmation_v0_results.json`
- `experiments/coalition_seeded_probe97_gap47_confirmation_v0_runner.py`
- `experiments/coalition_seeded_gap65_vs_probe97_confirmation_v1_protocol.json`
- `experiments/coalition_seeded_gap65_vs_probe97_confirmation_v1_results.json`

`2026-08-28T1435JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.
