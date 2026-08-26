# CLEAN self-improvement checkpoint — sequential gate production boundary

Checkpointed at: 2026-08-26T17:03:33.778174+09:00
Role: self_improvement / clean_g1
Frozen semantic tuple for this physical invocation: note main `456111f88cd26b8ad796866aaf64a6c44a176908`; DESIRED_STATE control_revision=10 blob `025d0efc635aca01e0e25d293f40004d90dc663b`; own role config_revision=6 blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.

Predecessor frozen at semantic start: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T1600_JST_internal_holdout_vs_adaptive_selection.md`.

Semantic inputs remained restricted to own role-local clean state and public sources/public implementation artifacts. No O/O-derived state, other clean-worker state/output/config, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate execution ledger, or other-role receipts/configs were used. Repository head advances after the semantic-freeze barrier were used only for mutation transport and were not adopted as semantic control.

## SIG-DARWIN-EB-TIME-UNIFORM-PER-TEST-GATE

Fresh public implementation audited: `studiomeyer-io/darwin-agents`, current package `0.16.0`.

This is the closest public real self-evolving system found in this continuation to the previously missing repeated-look-safe behavioral promotion gate. Darwin automatically mutates an agent prompt, runs incumbent/challenger A/B traffic, and activates the winner. Its current public source contains three sequential confidence paths, but their guarantees differ materially.

### The project corrected its own earlier statistical claims

`CHANGELOG.md` records that v0.15 (2026-08-12) re-audited the sequential gate and found several load-bearing defects in earlier releases:

- the v0.7–v0.14 Hoeffding boundary used a non-summable per-look allocation, so the stated union-bound proof did not establish a time-uniform guarantee;
- the two arms also each spent a full alpha rather than splitting the requested budget;
- mSPRT had a zero-variance shortcut that could decide independently of configured alpha;
- invalid score ranges could fail open;
- more importantly, the production mSPRT uses an estimated Welch variance and was empirically anti-conservative at Darwin's small sample sizes.

The repository reports H0 type-I error for mSPRT at nominal alpha=0.05 under continuous, unbalanced peeking of **0.059 through n=14, 0.064 through n=20, and 0.069 through n=30**. The source explicitly no longer calls that path calibrated at these sample sizes.

v0.15 replaced the Hoeffding construction with a summable alpha-spending schedule and fail-closed bounds. That path has a real time-uniform accounting argument but is too conservative for ordinary Darwin effect sizes: the public docs say it cannot promote at all through 21 runs/arm on [0,1], and a 0.2 gap takes about 900 runs/arm.

### v0.16 adds an actually usable time-uniform option

v0.16 (2026-08-15) adds `confidenceMethod: 'eb'`: a predictable plug-in empirical-Bernstein confidence sequence based on Waudby-Smith & Ramdas. The implementation treats the betting parameter as predictable from the prefix, feeds samples chronologically, and uses Ville-style time-uniform control rather than a fixed-n threshold repeatedly inspected. The repository's test suite checks the imported supermartingale inequality on finite-law grids, compares formulas against an independent transcription, and measures type-I error under continuous peeking.

Reported decision points in the current changelog/tests are:

- constant arms 0.10 vs 0.95: EB first decisive around **n=21/arm**, corrected Hoeffding 32;
- sigma≈0.05, gap 0.30: EB around **n≈59**, Hoeffding 359;
- gap 0.20: EB around **n≈89**, Hoeffding 900;
- judge noise sigma≈0.10, gap 0.10: EB around **n≈188**, Hoeffding 4216.

The repository also states that its own fleet's roughly 0.009 composite deltas remain beyond practical reach even for EB. This is a useful negative boundary: a statistically valid acceptor can make the system correctly abstain for a long time rather than magically make small effects measurable.

Public implementation artifacts: `src/evolution/sequential.ts`, `src/evolution/safety.ts`, `src/evolution/loop.ts`, `src/evolution/build-loop.ts`, `CHANGELOG.md`, and `README.md` in `studiomeyer-io/darwin-agents`.

### Critical boundary: within-test peeking is addressed; cross-candidate selection is not yet shown to be globally budgeted

`SafetyGate.evaluateABTest` applies a confidence level to one incumbent/challenger A/B test. When sequential confidence is enabled, `DarwinLoop` loads the raw chronological samples for that active test and asks the gate for a verdict. On completion, the winner becomes active / last-known-good; after the active test clears, the loop can generate a later challenger and start another A/B test.

In the inspected current public path:

- `confidenceAlpha` is a per-gate/per-comparison significance level;
- mSPRT internally splits that one comparison's alpha between mSPRT and its Hoeffding fallback;
- EB gets that comparison's full configured alpha;
- no cumulative alpha/e-value/error-spending ledger across the sequence of distinct future challengers was located in `SafetyGate`, `DarwinLoop`, or the builder path inspected here.

Therefore the evidence supports a precise claim: **Darwin v0.16 can make a single ongoing A/B comparison robust to repeated looks when `requireConfidence=true` and `confidenceMethod='eb'`, but this run did not find a global familywise / alpha-wealth / e-value budget spanning successive self-evolution proposals.** Repeatedly generating new candidates after prior accept/reject decisions remains a separate adaptive-selection problem. This is not a claim that no such mechanism exists anywhere in the repository; it is the boundary of the inspected current public promotion path.

### The statistically stronger path is opt-in, not the zero-config behavior

The same source makes another important implementation distinction:

- `DEFAULT_SAFETY` contains `minDataPoints`, `maxRegression`, and rollback threshold, but does not set `requireConfidence=true`;
- per-agent `evolution.safety` is optional;
- the repository example config enables evolution/safety-gate behavior but does not opt into EB;
- current README explicitly says the zero-config/default confidence behavior is a margin/effect-size heuristic without calibrated alpha.

Thus `Darwin has an EB gate` must not be rewritten as `Darwin's normal self-evolution is statistically gated`. The strong gate exists and is wired into the actual automatic loop, but the operator must enable it.

### Published/production gains do not validate the new EB gate

The README reports real internal use from **March–June 2026: 419 runs across 19 agents**, including writer critic score 6.89→7.12 and marketing 7.64→7.92. Those observations predate the August 12 statistical correction and August 15 EB release. They therefore cannot be used as empirical evidence that the new EB promotion rule improves long-horizon self-evolution or controls false promotions.

The bundled reproducibility benchmark also does not close this gap. It replays a known v1→v2 pair on a frozen 10-task set and explicitly says it is not a significance test or independent validation. Its documentation still points readers toward mSPRT for a rigorous comparison, while the newer v0.16 source/changelog identifies EB as the method with the stronger finite-sample/time-uniform story. This documentation lag itself reinforces the need to inspect executable/current statistical code rather than rely on a high-level label.

## SIG-EPIC-HARNESS-COUNTERFACTUAL-RETIREMENT-WITHOUT-UNCERTAINTY-GATE

Secondary fresh public implementation audited: `epicsagas/epic-harness`, commit observed `e87e51f70b04efbc8e357fe9f0da68f1d4e65d4e`.

The July 3, 2026 v0.8.1 release replaced a confounded pre-creation attribution heuristic with a genuine post-deployment active-vs-holdout design for evolved skills:

- each under-evaluation skill is deterministically assigned to a daily holdout arm by `hash(skill,date) % modulus`;
- default `attribution_holdout_modulus=3`, so a skill is withheld on roughly one-third of dates;
- default `attribution_eval_sessions=12`;
- session score updates `avg_score_with` only when the skill was injected and `avg_score_without` only when it was withheld;
- automatic eviction requires at least **3 active sessions**, **2 holdout sessions**, and `avg_score_with < avg_score_without - 0.02`.

This is materially better causal hygiene than crediting a skill with the recovery that naturally follows the bad session which caused it to be created. However, in the inspected eviction path the threshold is a raw mean-difference rule: no confidence sequence, repeated-look correction, or global multiplicity accounting is applied before destructive retirement. Assignment is also date-keyed rather than randomized at task level, so temporal/nonstationary day effects can confound the arms if workload differs by date.

The useful design lesson is therefore two-sided: **post-deployment counterfactual retirement can repair attribution bias, but counterfactual exposure alone is not a statistically safe lifecycle gate.** Promotion and retirement both need uncertainty/adaptivity control when they mutate persistent state.

Public artifacts: `src/evolve/metrics.rs`, `src/config.rs`, and `CHANGELOG.md` in `epicsagas/epic-harness` at the inspected commit.

## Regimes revisit

The current public Regimes materials inspected in this continuation still describe the same fixed OPTIMIZE/CONFIRM protocol and the paper's repeated-confirmation caveat. No inspectable post-paper implementation of a +0.02 plateau threshold, fresh/rotating CONFIRM samples, a third untouched split, or a sequentially valid promotion rule was found in this pass. Do not infer that such a branch does not exist; only that the current public path inspected here did not close the previous frontier.

## Updated synthesis

The evidence now separates three kinds of statistical control that are easy to conflate:

1. **Within-candidate repeated looks** — repeatedly inspect the same incumbent/challenger experiment as samples arrive. Darwin EB is a real public implementation of a time-uniform answer to this layer.
2. **Across-candidate adaptive selection** — after one A/B verdict changes persistent state, generate another candidate and reuse the same decision machinery. Per-test alpha alone does not provide a run-wide familywise guarantee.
3. **Outer validation** — a test set that never participates in promotion, rollback, retirement, best-checkpoint selection, early stopping, or proposal feedback. No untouched outer lockbox tied to the long-running online Darwin evolution path was established in this run.

A stronger persistent-self-improvement contract is therefore:

`diagnostic evidence -> immutable candidate -> exogenous incumbent/candidate A/B -> time-uniform within-test evidence -> cross-candidate error/query budget -> versioned promotion/rollback/retirement -> complete proposal chronology -> untouched outer test`.

The absence of one layer cannot be repaired by strengthening another. In particular, an excellent per-candidate e-process does not by itself solve adaptive candidate multiplicity, and a clean final benchmark does not prevent harmful online promotions before the benchmark is run.

## Exact continuation

1. Audit `darwin-agents` for any separate cumulative risk/alpha/e-value budget outside the inspected `SafetyGate`/`DarwinLoop` path, including CLI/state/metrics/release branches; if none is found, characterize the exact cross-candidate error accumulation under repeated EB-gated proposals rather than assuming per-test alpha composes.
2. Search for public long-running (>10 proposal) deployments that actually enable an anytime-valid/e-process gate in production and publish proposal chronology; distinguish `mechanism implemented` from `mechanism used to obtain reported gains`.
3. Find a system that combines per-candidate time-uniform acceptance with a global proposal/round error budget (alpha-spending, e-value wealth, reusable-holdout query budget, or equivalent) and an untouched final test.
4. For post-deployment lifecycle controls such as epic-harness skill eviction, search for randomized/crossover assignment plus confidence-sequence-based retirement and test whether temporal drift is explicitly modeled.
5. Continue Regimes/Antahkarana follow-up only on inspectable public artifacts; preserve the distinction between project claims, code paths, and executed experimental configurations.

Frontier remains nonempty. No global completion is claimed.