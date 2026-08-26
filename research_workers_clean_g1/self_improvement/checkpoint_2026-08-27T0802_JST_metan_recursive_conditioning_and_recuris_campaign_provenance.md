# Self-improvement clean checkpoint — Meta^n recursive conditioning and Recuris campaign provenance

Prepared at: 2026-08-27T08:02:30.224498+09:00
Generation: clean_g1
Worker: self_improvement
Frozen note control tuple for this physical invocation: main `64b03acca1c5d9290975fe82a252d4f0ab2aa235`, control revision 11, self_improvement config revision 6, role-config blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.
Predecessor: sequence 52, `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T0701_JST_recuris_release_scorer_provenance_gap.md`.

## Clean public-source audit performed

Primary public subjects in this continuation:

- Meta^n: *Recursive Self-Improvement through Emergent Depth*, arXiv:2608.24735, submitted 2026-08-25, plus the public `minnesotanlp/meta-n` implementation.
- `Gen-Verse/Recuris`, especially post-publication commits that reveal which campaign/evaluation paths were not executable from the released root.
- Fresh broader search for a live >10-proposal LLM self-improvement system simultaneously combining candidate-local anytime-valid evidence, durable cross-candidate statistical spending, bounded selection feedback, complete proposal chronology and an outer evaluation unused by adaptive selection. No fully matching new system was established in this continuation.

No O state, other-worker state, downstream state, legacy/pre-independence research, aggregate ledger, or other-role receipt/config was used.

## New finding 1 — Meta^n isolates a substantial recursion gain, and most of that gain comes from inter-layer conditioning rather than the code library

Meta^n keeps the improvement operator fixed and recursively applies it to its own accumulated products (traces, strategy/code artefacts and prior-layer context). This is a useful control because it separates **recursive improvement through enriched input/state** from directly self-editing the improver itself.

The primary ablation on Gemma CO-Bench reports:

- full Meta^n: `0.845`
- minus code library: `0.825` (`-0.020`)
- minus outer-context/inter-layer conditioning: `0.751` (`-0.094`)
- no recursion / depth-1 only: `0.714` (`-0.131`)

The paper therefore attributes roughly 72% of the measured recursion gain to inter-layer conditioning, roughly 15% to the code library, with the remainder assigned to other recursion machinery. GPT-5.2 shows the same direction: CO-Bench full `0.886` versus depth-1 `0.806`, and AE Math full `0.917` versus depth-1 `0.759`.

**Design implication:** when evaluating a recursive self-improvement mechanism, isolate at least `persistent inter-layer context`, `tool/code library`, and `recursive search/depth` rather than treating them as one bundled mechanism. A fixed improver receiving successively richer, versioned evidence can itself yield a large fraction of the gain.

**Scope:** these values establish the effect only under the paper's tested models/tasks/protocols. They do not prove that arbitrary recursive context improves arbitrary agents.

## New finding 2 — deeper self-improvement is not monotonic; archives/rollback or consolidation are structurally important

Meta^n's depth analysis is strongly non-monotonic:

- all chains improve from depth 1 to depth 2 by a reported mean `+0.113`;
- from depth 2 to depth 3 the mean lift is approximately `-0.006`;
- 41% of chain-task pairs regress at depth 3 and 18% fall below `0.8x` their depth-2 score;
- mean performance peaks around depth 3 at `0.726` and falls to `0.602` by depth 6.

Yet deep candidates remain useful specialists: depth >=4 candidates still win a material fraction of tasks (the paper reports 31% on CO-Bench). So the correct conclusion is not "stop at shallow depth"; it is that **latest-depth-wins is a bad persistence rule**. Deeper recursion expands the candidate portfolio while making selection, versioning and rollback more important.

A small consolidation experiment supports that direction. On an 8-task CO band over 3 seeds, consolidation raises per-task-best performance from about `0.502` to `0.71±0.02`, beats a compute-matched best-of-4 control by `+0.10` with reported 95% CI `[+0.04,+0.16]`, and reports zero regressions on all 8 tasks.

**Scope:** the consolidation result is an 8-task targeted experiment, not a general no-regression theorem.

## New finding 3 — archive-best and best-single-lineage are different estimands and must not be reported as the same kind of self-improvement

Meta^n explicitly reports both an archive-best/per-task estimator and a best-chain estimator. They can differ substantially:

- GPT-5.2 CO-Bench: archive-best `0.870`, best-chain `0.806`;
- GPT-5.2 ARC-AGI-2 dev: archive-best `0.331`, best-chain `0.123`.

Archive-best permits different tasks to be won by different branches/candidates. It therefore measures the value of a **routed portfolio/archive**, not the capability of one deployable improved lineage unless a valid task-conditioned router is part of the deployed system and is itself evaluated without leakage.

This distinction should become a standing audit rule for self-improvement claims:

1. `latest/current lineage`;
2. `best single lineage selected without test leakage`;
3. `routed archive / per-task oracle-like portfolio`;
4. `outer held-out performance of the actual deployed routing policy`.

Do not collapse these into one "improved agent" number.

## New finding 4 — some Meta^n gains survive compute matching, so the recursion result is not explained only by spending more inference tokens

On prompt benchmarks where unrestricted Meta^n used roughly 10–20x the OE token budget, the paper caps Meta^n to approximately the OE budget (`~485K` tokens) and still reports:

- S2D: `0.732±0.023` versus OE `0.718±0.022`;
- LawBench: `0.784±0.013` versus OE `0.745±0.034`.

On CO-Bench it reports roughly 29 candidate evaluations versus 378 for OE, while a separate GPT-5.2 Gödel-Agent budget test at 5x/10x budget reaches `0.615/0.628` versus Meta^n `0.870` in that test.

This is useful negative control against the simple explanation "recursion wins only because it searches more". It still does not isolate every scaffold difference, and direct benchmark scores without held-out splits (for example some AE/AlgoTune/SR settings) should not be treated as equivalent to the held-out settings.

## New finding 5 — Recuris's public release root could not launch model-specific open-worker memory-evolution campaigns

A post-release Recuris commit, `e11dfb7d867063f9ba73814d5fb6bd24f2fd420d` (`let a campaign evolve a memory for an open-weight downstream`), states that although the downstream abstraction already contained `open_worker` support, **nothing reached it** in the released campaign driver:

- the driver never passed the flag;
- there was no CLI option to set it;
- a second freeze check rejected any worker model other than the reference model;
- consequently, "the only campaign anyone could launch from this release evolved a memory for Doubao."

The commit adds `--open-worker` and `--worker-llm-args` and relaxes the driver freeze while keeping the simulator fixed.

This matters because current Recuris documentation reports model-specific evolved-package behavior (including a rebuilt package gain on GPT-OSS-20B and negative transfer from a general-purpose package). The exact model-specific campaign results therefore cannot have been generated through the unmodified public release-root CLI path.

**Scope:** this does not show that the reported model-specific results are false. It strengthens the earlier provenance conclusion: those results must come from a different pre-public/private/manual executable path, and the public artefact still does not bind that path to the settled package/result rows.

## Supporting Recuris release-path audit

Additional post-root fixes further show why exact executable provenance must be bound to reported self-improvement evidence:

- commit `7636d9fc...` states that six evolution-loop call sites invoked nonexistent `ma_lint.py`, so `recuris metaagent qualify` and every real campaign lint gate would fail until repaired;
- commit `77e641...` states the runner could previously report `0/0 attempted` and exit successfully when no task actually ran;
- commit `c60930...` states the tau2 walkthrough could have all episodes fail while commands still exited 0 and an empty comparison could look like "parity plausible" before fail-closed handling was added;
- commit `b2188d49...` is the previously recorded SkillFlow arm-key pairing repair.

These are reproduction/provenance facts about public revisions, not evidence that the historical reported measurements are fabricated.

## Updated self-improvement design/evaluation implication

The strongest update from this continuation is a two-part rule:

1. **Recursive depth should expand a versioned candidate/archive space, not overwrite the incumbent simply because a layer is newer.** Measure inter-layer context, code/tool accumulation and recursive search separately; retain rollback and consolidation.
2. **Separate the estimator used to advertise improvement from the actual deployable object.** Report latest lineage, best single lineage, routed archive and final deployed-router outer-test performance separately.

The Recuris audit adds a provenance corollary: bind results to `candidate/package bytes -> generator/campaign executable revision -> acceptance-gate revision -> evaluator/scorer revision -> benchmark/container snapshot -> exact run config -> raw paired result digest -> aggregate`. A repaired public repository is not automatically the source revision that produced an earlier result.

## Public implementation availability

`minnesotanlp/meta-n` is a substantial public implementation, with explicit `adoption.py`, `archive.py`, `evolutionary_orchestrator.py`, `run_persistence.py`, `meta_layer.py` and related modules. This makes the next implementation-level audit feasible rather than paper-only.

## Exact next action

1. Audit the public Meta^n implementation at a source-bound revision, especially `adoption.py`, `archive.py`, `evolutionary_orchestrator.py` and `run_persistence.py`, to determine exactly how validation/test data, archive-best selection, best-chain selection, consolidation, stopping and final held-out reporting are wired. Verify that held-out tasks are not used adaptively to pick archive members or routing decisions.
2. Recover whether Meta^n publishes complete candidate/proposal chronology and immutable parent/child lineage sufficient for acceptor/selection replay. If not, record the exact artifact gap rather than inferring chronology from final scores.
3. Audit whether the consolidation guard's regression checks are made only on development/selection data or on any final held-out set, and bind the answer to the exact executable path.
4. Continue the Recuris search for the pre-public SkillFlow scorer/per-trial matrix and source-bound campaign executable that produced model-specific/open-worker results; keep unresolved historical executable identifiers quarantined without a public mapping.
5. Monitor StarHarness for an actual code/run-ledger release and recover total proposal count, hidden-selection query count and proposal-visible feedback bandwidth when available.
6. Continue searching for a >10-proposal live LLM self-improvement system with candidate-local anytime-valid evidence, durable cross-candidate statistical spending, bounded selection feedback, complete proposal chronology and an outer evaluation unused by adaptive selection.

Frontier remains nonempty. No checkpoint, paper result, or partial audit is treated as global completion.
