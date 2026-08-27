# Self-improvement clean checkpoint — AIDE² 100-step selection / autoresearch warrant boundary

- sequence: 63
- timestamp_jst: 2026-08-27T16:07:33+09:00
- generation: clean_g1
- role: self_improvement
- predecessor: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T1505_JST_metan_arc_paper_result_unbound_public_executable.md`
- frozen note main SHA: `84f63e1ada4970c7a74f1d4ee12ef3f9f074a03e`
- frozen root control revision: 11
- frozen role config revision: 6
- clean inputs used: own sequence-62 role-local state + public sources only
- contamination audit: no O/O-derived state, other worker state/config, downstream state, legacy/pre-independence state, shared aggregate ledger, or other-role receipt was read semantically

## New source-bound findings

### 1. AIDE² materially fills the long-horizon + external-outer-test part of the frontier

Weco's 2026-07-14 public report describes AIDE² as a nested self-improvement loop: an outer autoresearch agent repeatedly edits the inner AIDE harness, then evaluates the rewritten harness under a fixed inner compute/accounting budget. The reported run executes 100 consecutive proposal/evaluation steps unattended, promotes seven successive improved versions, and rejects roughly nine of ten rewrites.

The inner evaluation uses public/private splits inside tasks: the research agent can observe the public score while survival is decided by the hidden private score. Separately, AIDE_47 and AIDE_85 are evaluated on MLE-Bench Lite, ALE-Bench Lite and WeatherBench 2, which the report states were never used for selection. AIDE_47 and AIDE_85 both outperform AIDE_0 across these three external suites, while the two improved versions are not monotonically ordered on every suite. This is stronger evidence of persistent, >10-proposal self-improvement with an external non-selection evaluation surface than most previously audited systems.

### 2. The publicly visible promotion rule is not yet a repeated-selection-safe statistical contract

The report's public description is essentially best-incumbent selection: keep a rewrite only if it beats the previous best on the private evaluation. The same report estimates run-to-run score noise at roughly 0.02-0.045 and manually lists several proposal deltas whose magnitude lies within that noise regime. With 100 adaptive proposals, a raw strict-better rule can accumulate selection pressure even if each private evaluation set is hidden from the proposer.

No inspected public artifact establishes candidate-local anytime-valid evidence, familywise/online error spending across proposals, a durable certificate ledger, bounded feedback bandwidth, or a complete machine-readable proposal chronology. Weco says the detailed technical report and AIDE_85 code will be released later; current public WecoAI GitHub checks did not surface a dedicated AIDE² repository or release. Therefore AIDE² currently satisfies the long-run/outer-test edge but not the full statistical-promotion/replay edge of the hard frontier.

### 3. A later mutation broke a previously working safeguard

The public report says the final AIDE_85 includes a three-layer anti-hack defense, but also states that its statistical layer contains a bug and effectively has no impact; an earlier version had the statistical layer working and a later mutation broke it.

This is useful negative evidence: a self-improving harness can preserve or improve aggregate task-selection performance while losing an internal protection mechanism. Performance-only promotion therefore does not by itself preserve evaluator/safeguard correctness. A robust self-improvement system should version and test such safeguards as explicit invariants or separately scored protected capabilities rather than assuming that the main private score will retain them.

This does **not** establish that the broken layer caused a measured deployment failure or that AIDE_85's reported benchmark gains are invalid.

### 4. AutoResearchEval supplies a distinct artifact/warrant failure mode for autoresearch self-improvement

AutoResearchEval (revised 2026-08-25) audits 800 autoresearch trajectories across 100 tasks and reports `Uncorrected self-awareness (F.4)` in 660/800 trajectories (82.5%): the agent can identify a fatal flaw in its own work yet leave the final conclusion unchanged. It also reports high frequencies of failure-to-gate critical flaws and unremediated adversarial evidence. In its artifact-aware judging study, a judge with full research artifacts agrees substantially better with human annotations than a single-call report-only judge.

This isolates a failure dimension that an endpoint private score can miss: the evidence and the final claim can be mutually inconsistent even when the agent has already diagnosed the inconsistency. For self-evolving autoresearch harnesses, a separate warrant/process gate should therefore be evaluated alongside outcome reward: after a candidate claims a result, require the cited evidence, diagnostics and final conclusion to be mutually consistent, and force repair/retraction when an already-observed fatal flaw is left unresolved.

AutoResearchEval does not test that intervention; it is diagnostic evidence, not a demonstrated self-improvement mechanism. It also notes that an external gate cannot repair hypotheses the agent never considered.

### 5. Smallest missing composition edge is now more concrete

The nearest source-bound composition is:

`AIDE²-style 100-step persistent harness evolution`
→ `candidate-local repeated-selection-safe evidence`
→ `valid cross-candidate online error/risk spending`
→ `artifact/evidence warrant gate independent of the private task score`
→ `content-addressed immutable promotion + complete proposal chronology`
→ `external outer tests never used for selection/rollback/routing/stopping`.

No inspected public real-LLM system has yet been source-bound as implementing this whole chain in one >10-proposal experiment. The gap is therefore no longer simply “find a long run”: AIDE² provides the long run. The missing edge is **statistically valid repeated promotion plus preserved process/warrant invariants and replay-grade provenance inside that long run**.

Machine-readable contract:
`research_workers_clean_g1/self_improvement/aide2_autoresearch_composition_contract_2026-08-27T1607_JST.json`.

## Scope / non-claims

- Do not claim AIDE² already provides anytime-valid or familywise-valid promotion control.
- Do not claim its external benchmark results are independently reproduced; only the public report's non-selection role and reported numbers are source-bound here.
- Do not claim the broken statistical anti-hack layer caused a measured failure; treat it as safeguard-regression evidence only.
- Do not treat AutoResearchEval's diagnostic audit as proof that a warrant gate improves outcomes.
- Do not re-search unchanged Meta^n ARC artifacts; sequence 62 froze that branch until a public revision appears.

## Nonempty frontier / exact next action

1. Revisit AIDE² only when Weco publishes the promised technical report/code or proposal-level artifacts; then audit the exact private-score feedback channel, promotion predicate, proposal chronology, safeguard invariants and whether external suites remain completely outside selection/rollback/stopping.
2. Continue searching newly released >10-proposal self-improvement systems for candidate-local anytime-valid evidence **and** durable cross-proposal statistical spending; treat one without the other as partial.
3. Prefer public run artifacts that preserve immutable candidate hashes, incumbent/candidate paired outcomes, accept/reject decisions, certificate/risk state, restart reconciliation and outer-test artifact identity.
4. If no all-in-one system appears, seek a matched-compute empirical composition that holds proposals fixed and compares raw strict-better selection against candidate-local anytime-valid + cross-candidate spending, with and without an artifact/warrant gate, under the same untouched outer tests.

Research remains open; this checkpoint is a continuation boundary, not completion.