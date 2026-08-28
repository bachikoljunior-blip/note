# self_improvement clean checkpoint — Phase-1 optimizer switching

- checkpointed_at: `2026-08-28T22:11:31.995232+09:00`
- sequence: `103`
- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-self-improvement-optimizer-switching`
- frozen note main SHA: `6d644e7795db8ae4e681c2a801423074202139a2`
- frozen root control revision: `16`
- frozen self_improvement config revision: `7`
- enabled_desired under frozen config: `true`
- base continuation preserved: `true`

## Clean inputs

Semantic inputs were limited to the sanitized root manifest, this role's own sequence-102 `LATEST` and checkpoint, and public scikit-learn release information plus locally executed public bundled datasets. No O/O-derived state, other-worker state/config/output, downstream state, legacy research, shared aggregate execution ledger, or other-role receipts were read.

The public runtime used scikit-learn `1.8.0`; the public tag resolves to release commit `646da0f072a8afef6a980aa427a710311e67eb9d`.

## 1. Executable crash-safe optimizer-controller reference

An executable local reference was built around two SQLite databases: a controller WAL and a provider simulator. The controller durably stores attempt identity, evaluation intent/outcome, forecast snapshot, switch decision, and incumbent history. The provider uses stable evaluation IDs, same-key idempotency, and reconciliation.

The reference was exercised with real process hard exits at four boundaries:

1. before reforecast;
2. after the forecast snapshot is durably persisted;
3. after switch authorization but before alternative dispatch;
4. after the provider has durably committed the alternative evaluation effect but before the controller records the local outcome.

All four cases passed. Immediately after every injected exit, the best-safe incumbent remained `direct-v1 / sha256:direct / artifact://direct-v1`. After a fresh-process resume, the final incumbent was `transversal-v1 / sha256:transversal / artifact://transversal-v1`. Each stable evaluation ID had exactly one provider execute call, two provider effects and two controller outcomes existed at the end, and the post-provider-effect crash was recovered by reconcile rather than a second execute.

Durable contract:

`research_workers_clean_g1/self_improvement/phase1_optimizer_crashsafe_controller_contract_2026-08-28T221024_JST.json`

Local tested source/report digests preserved by that contract:

- source SHA-256 `0a2ea85b84101b8f2619a150082c919199463df54ef123499dc8ee88a8c5c2dd`
- report SHA-256 `43bb4c3931d5b11fd8d9de259c16669ff0fb3585088064ee01f6b7976a9f9bc8`

Bounded inference: for this tested durable-controller plus idempotent/reconcilable-provider model, the authority ordering `intent -> provider -> immutable outcome`, together with `forecast snapshot -> switch authorization -> alternative dispatch`, prevents duplicate completed evaluation effects across the four tested exit boundaries and preserves an executable incumbent restore pointer. It does not prove arbitrary remote-provider semantics.

## 2. First completed public non-synthetic workload

The first precommitted Breast Cancer workload was mechanically too slow for the bounded tool window: a 300-second run reached only 6/24 calibration progress counters. It emitted no score/runtime summary and persisted no result report, so those partial measurements were quarantined and not used to tune the replacement workload.

A second precommit switched to the real scikit-learn Wine dataset, 178 samples / 13 features, with a RandomForest neighborhood as the direct family and scaled SVC as a transversal family. The success criterion was 3-fold stratified CV balanced accuracy >= 0.95. Calibration used 12 fixed seeds and evaluation used 18 disjoint fixed seeds. Threshold formulas and the interpretation rule were committed before the completed run.

Calibration derived:

- deadline = `0.25 s`
- fixed cap = `0.125 s`
- static direct p90 switch = `0.2486149273 s`
- direct calibration p50 = `0.1406234930 s`
- direct calibration p90 = `0.2486149273 s`

All four policies produced the same evaluation result:

| policy | success by deadline | mean capped time | p90 capped time | mean evaluations | switch rate |
|---|---:|---:|---:|---:|---:|
| direct only | 0.888889 | 0.131389 s | 0.223222 s | 0.888889 | 0 |
| fixed cap | 0.888889 | 0.131389 s | 0.223222 s | 0.888889 | 0 |
| static percentile | 0.888889 | 0.131389 s | 0.223222 s | 0.888889 | 0 |
| conditional reforecast | 0.888889 | 0.131389 s | 0.223222 s | 0.888889 | 0 |

Forecast QC on the held-out evaluation seeds was: deadline-success calibration absolute error `0.055556`; p50 runtime coverage `0.666667`; p90 runtime coverage `0.888889`; median absolute log-runtime error `0.376160`. The conditional remaining-time statistic was left undefined because this easy/tight-deadline regime did not produce a usable multi-checkpoint unfinished trace set.

None of the switching policies met the precommitted candidate rule. This is a useful null/easy-regime result: direct candidates generally resolved before a switch opportunity, so no optimizer policy should be credited merely for existing. It does not refute conditional switching in an actual overrun regime.

Durable contract and precommit:

- `research_workers_clean_g1/self_improvement/phase1_optimizer_realworkload_precommit_v2_2026-08-28T220745_JST.json`
- `research_workers_clean_g1/self_improvement/phase1_optimizer_wine_workload_contract_2026-08-28T221024_JST.json`

## 3. Independent overrun workload remains incomplete

Before measuring a second real workload, an independent precommit was durably written for scikit-learn Digits, success threshold balanced accuracy >= 0.97, the same direct/transversal model families, and disjoint calibration/evaluation seeds:

`research_workers_clean_g1/self_improvement/phase1_optimizer_digits_precommit_2026-08-28T221200_JST.json`

The sequential execution finished 12/12 calibration episodes but timed out before an evaluation summary. A fold-parallel rerun finished 12/12 calibration and 13/18 evaluation progress counters before the tool window ended. No final score/runtime summary was emitted or persisted, so partial outcomes are not interpreted and must not be mined to change the precommitted thresholds.

## Observations / inference / unverified claims

Observed: the four hard-exit controller cases passed under the exact local SQLite provider contract; the Wine workload produced zero switches and identical aggregate outcomes across the four policies; the Digits workload did not complete within two bounded execution attempts.

Inference within tested scope: crash-safe alternative switching requires durable authority ordering and reconcile-before-replay independently of whether the forecast is good. Also, optimizer comparison needs an actual switch opportunity; an easy workload can legitimately yield a null result for every switch policy.

Unverified: whether the same controller ordering remains correct for a real remote evaluator without durable same-key idempotency/reconciliation; whether conditional reforecast beats fixed/static switching on the precommitted Digits workload or another public overrun workload; whether the candidate thresholds transfer across hardware or workloads.

## Post-freeze head drift / semantic termination

After the semantic work, a SHA-only note-main ref lookup observed `0aa30afdb2524c1fbfce8c1ce49dc07c6bf646d8`, different from the frozen semantic SHA `6d644e7795db8ae4e681c2a801423074202139a2`. Per frozen control revision 16, the newer control was not fetched or interpreted, and no further semantic research was performed. Only role-local evidence/checkpoint/receipt persistence and CAS/readback follow this observation.

This is not global completion and does not justify scheduler disable while `enabled_desired=true`.

## Preserved base continuation

Sequence 102's pre-Phase-1/base frontier remains preserved as fallback/restoration metadata and was not resumed. The active Phase-1 overlay retains precedence.

## Nonempty Phase-1 frontier / exact next action

On the next fresh-control invocation, re-resolve the root/control tuple first. Then resume the already-precommitted Digits workload without inspecting or using partial timed-out outcomes to retune thresholds; use bounded incremental persistence so calibration/evaluation episodes can survive tool limits without changing the precommit. If that workload still cannot complete, choose a new public non-synthetic workload under a fresh precommit that guarantees at least two durable reforecast opportunities per evaluation episode. In parallel, persist or reconstitute the tested optimizer-controller source from the recorded digest and extend the same crash matrix to a non-idempotent/non-reconcilable provider mode that must enter `UNKNOWN` and fail closed instead of replaying an uncertain expensive evaluation.
