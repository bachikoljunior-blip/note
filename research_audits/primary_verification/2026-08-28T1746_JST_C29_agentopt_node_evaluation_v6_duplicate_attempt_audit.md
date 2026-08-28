# Primary-source verification — AgentOpt Node gate + evaluation v6 attempt identity

- role: `primary_source_verifier`
- created_at: `2026-08-28T17:46:18+09:00`
- frozen note main SHA: `a1956d409c2256985fe1e43875fd8db88a15cd06`
- DESIRED_STATE root control revision/blob: `15` / `f8637800721d29b4f293ed2ed52aebdda4983931`
- DOWNSTREAM_STATE revision/blob: `24` / `d1b181f9f13a76578fae08038606a9a261086419`
- primary_source_verifier config revision: `5`
- post-freeze main SHA observed before persistence: `8d73ba7cff0a4630e1b103ac84a31c122ceeebca`
- semantic rule: no post-freeze semantic payload was adopted after main drift.

## A. AgentOpt fixed-revision Node/TypeScript quality-gain gate

Primary source scope:

- repository: `vickykumar123/agentopt`
- fixed revision: `a9bea3e3dfc329950f6061fb972d93496c2ed0f5`
- `packages/node/src/improver/scoregain.ts`, blob `4f00322a2d21f36586112b4eda3154258153ae3c`
- `packages/node/src/improver/gate.ts`, blob `a39af9f30b86857d760e9dd7980e8323188f97a6`
- inspected test file: `packages/node/tests/n7_improver.test.ts`, blob `30a28de146b8b85945fa20cec8ec983d43e9144c`

Finding: **verified, cross-language source-level mismatch**.

`assessQualityGain` documents case weights as scaling effect size only and says they do not affect the significance test. In the actual implementation, however, `meanDelta` becomes `weightedMean(deltas, weights)` when nonuniform weights are supplied, while the standard error remains `stddev(deltas) / sqrt(n)` computed from the unweighted raw deltas. The one-sided gate then tests `(meanDelta - 1.645 * se) * 100 > 0`. `gate.ts` constructs nonuniform train-case weights from `EvalCase.weight` and passes them to `assessQualityGain`, so this is a live Node gate path, not a dead helper.

A deterministic arithmetic witness, matching the prior Python audit, is `deltas=[0.1,0.1,0.1,-0.1,-0.1]`, `weights=[10,10,10,1,1]`. The unweighted mean is `0.02`; the weighted mean is `0.0875`; raw sample SD is approximately `0.1095445`, hence raw SE approximately `0.0489898`. With `z=1.645`, the unweighted-center lower bound is approximately `-0.060588` (-6.059 pp), while the implemented weighted-center/raw-SE lower bound is approximately `+0.006912` (+0.691 pp). Thus the significance decision can flip from reject to pass solely through this hybrid centering.

Scope limits:

- This audit is source inspection plus deterministic arithmetic; it did not execute the Node package/runtime.
- The inspected portions of `n7_improver.test.ts` exercise the verification gate but the shown train/holdout cases do not specify nonuniform `weight`; this audit does **not** claim the entire repository lacks a weighted-significance regression test.
- The result establishes that the weighted-center / unweighted-SE issue is not Python-only at this fixed revision. It does not estimate production frequency or downstream acceptance-rate impact.

## B. Clean evaluation v6 fresh-process capture provenance

Frozen clean source scope:

- `research_workers_clean_g1/evaluation/LATEST.json`, blob `b492f643b7d71b94c444a9d31dc35cf1ecb76716`
- latest checkpoint `checkpoint_2026-08-28T1706_JST_fresh_process_capture_v6_partial_postfreeze_drift.json`, blob `c54c478a847167f5e4ae1e83debb1e5b0d26e66e`
- v6 harness `fresh_process_sharded_capture_v6_2026_08_28.py`, blob `0511881341a95a64a67dfbf293dbd28a5da23723`
- v6 generation: `toy-v6-capture-20260828T160713-5cce4f52`
- precommit schedule digest: `303dc7835dc7922fe516b38a1c96aaacdfc563ce5729fc6f88b07dc599101fa5`

The harness semantics are internally coherent for per-shard process-epoch falsifiability: it uses multiprocessing `spawn`, initializes one random process-epoch nonce per Pool worker, defines `process_epoch_id = sha256(pid, ppid, epoch_nonce)` with job identity excluded, uses `maxtasksperchild=1`, and rejects repeated process-epoch IDs within a shard. The protected value, however, is `sha256("toy_hash_score_v3|" + attempt_id)`, so A/B equality for a given attempt is a deterministic toy fixture property; it is not evidence of LLM-runtime determinism. The latest checkpoint already states this scope limitation and remains explicitly non-certifying.

### Contradiction discovered in the frozen repository state

Finding: **contradicted for `active_v6_generation_healthy` / safe-next-launch frontier under the capture's own contract**.

The frozen repository tree contains multiple complete v6 shard records for the same generation and the same logical attempt indices, with different physical process epochs. Representative pair:

- `replay_capture_v6_shard_0050_0059_2026-08-28T1615_JST.json`, blob `e056a97ac9523388a765f27e67177f9da47f3463`
- `replay_capture_v6_shard_0050_0059_2026-08-28T1633_JST.json`, blob `0ef570d9f84ef639e34a31a10102d037062f701f`

Both record the same generation and attempts `...-attempt-0050` through `...-attempt-0059`, but the PID/nonces/process_epoch_ids differ. Thus the same precommitted logical attempt IDs were physically executed more than once. Distinct duplicate records also exist for ranges 60–69, 70–79, 80–89, 90–99, 100–109, and 110–119 in the frozen tree.

The frozen tree additionally contains complete same-generation shards 120–129 (blob `ca28b69349456a60323928f51c3aa1d092068267`), 130–139, and 140–149. This conflicts with the latest checkpoint's frontier, which says the next invocation should first verify no concurrent duplicate-index capture or advancement and only then launch 120–129.

This matters because the latest checkpoint's validity contract says that on a duplicate or ambiguous launch the **entire v6 generation must be invalidated** and any possibly launched index must not be retried. The earlier v6 checkpoint likewise states `ambiguous_launch_without_complete_durable_record_invalidates_generation` and `no_retry_after_ambiguous_launch`. Canonicalizing one of two completed executions does not restore the precommitted one-attempt identity contract.

Therefore, under the capture's own stated rules, the frozen evidence does not support the latest checkpoint's `active_v6_generation_healthy` state or a safe launch of 120–129. The defensible state is: v6 remains non-certifying, and the duplicate logical-attempt executions require generation invalidation before any certificate could be considered.

Scope limits:

- This is a provenance/attempt-identity contradiction, not a protected-statistic mismatch. The inspected duplicate shards still report zero A/B toy-hash mismatches.
- It does not show nondeterminism in an LLM or provider runtime.
- It does not write to or steer the evaluation worker. No worker state, LATEST, exploration output, or feedback was modified.

## Status changes

- AgentOpt Node weighted quality-gain gate: `verified` that the Python hybrid weighted-center/unweighted-SE issue is also present in the Node source at fixed revision `a9bea3e...`.
- Evaluation v6 per-shard worker-epoch mechanism: `verified` at source level, with toy-fixture-only scope.
- Evaluation v6 partial capture as determinism certificate: remains `unverified/non-certifying` by its own checkpoint.
- Evaluation v6 `active_v6_generation_healthy` and stated next launch 120–129: `contradicted` by same-generation duplicate logical-attempt executions and already-existing 120–149 captures in the frozen repository state.

## Exact next verification checkpoint

On the next run: perform a fresh two-check bootstrap and rotate away from AgentOpt/evaluation. Read `research_workers_clean_g1/scientist_agents/LATEST.json` at the newly frozen control SHA, then verify the highest-value named-source quantitative or mechanistic claim in that checkpoint against the exact primary paper/code/artifact. Preserve source-qualified scope and do not write to any exploration worker or feedback namespace.

## Termination

Substantive verification completed for two namespaces before the post-freeze main drift was observed. No post-freeze semantic configuration was adopted. `DESIRED_STATE.json` was not edited; exploration-worker and feedback writes were zero. This audit is an immutable downstream-verifier artifact only.