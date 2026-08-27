# Long Horizon clean_g1 checkpoint — replay disruption and recoverability classification

Checkpointed: 2026-08-28T00:08:27+09:00
Invocation started: 2026-08-28T00:02:05+09:00
Chronology valid: true

## Frozen semantic control tuple
- note main SHA: `88b728ad99e70e1b860e7878e62c164f14dfb9f9`
- root control revision: `12`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- clean semantic boundary preserved: own role-local state + public sources only; no O, other worker, downstream, legacy/pre-independence, shared ledger, or other-role receipt semantic input.
- repeated SHA-only head lookup matched before semantic work. Later repository movement, if any, is write-safety only and is not adopted semantically.

Predecessor: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T230614JST_AUTHORITY_EFFECT_CLOSURE_AND_LOCALIZED_REPAIR.md`

## New primary evidence

### 1. Full rerun has a large disruption channel even on previously successful trajectories
Primary source: Luan et al., *Repair or Resample? Rethinking Failure Debugging in LLM Multi-Agent Systems*, arXiv:2608.25920, submitted 2026-08-26, updated 2026-08-27. https://arxiv.org/abs/2608.25920

The paper reruns 54 initially successful SymTrace executions three times each under the same runtime configuration. Of 162 rerun attempts, **85 fail**, and **39/54 source-success cases regress at least once**. This is direct evidence that broad re-execution is not merely an opportunity to rescue failures; it also has a large `success -> failure` disruption channel in this MAS setting.

The same paper reports, on 536 source failures:
- Unguided Full Rerun pass@3 repair: **6.90%**
- Self-Reflection pass@3: **4.29%**
- Critic-Agent pass@3: **3.73%**
- Last-Node pass@1: **1.31%**
- Random-Node pass@1: **3.73%**
- Suspicious-Node pass@1: **20.15%**

Across the three MASs, Suspicious-Node has the highest descriptive repair yield per API call and lowest calls/repair among reported methods, but the paper explicitly notes that different methods may have different trajectory lengths and attempt budgets, so API-call efficiency is not a compute-matched causal estimate. Suspicious-Node also jointly changes target selection and symptom-conditioned guidance; its 20.15% must not be attributed to either component alone.

**Implication:** a recovery policy must be evaluated on at least two paired outcomes: `failure -> success rescue` and `success -> failure disruption`. Repair rate on failed-only cohorts can select an over-intervening controller. Controlled prefix replay is preferable to unconstrained full rerun when the scientific question is whether the source failure mechanism was actually repaired.

### 2. Recoverability is fault-class conditional; generic repair cannot substitute for classification
Primary source: Sigdel & Baral, *ToolMisuseBench: An Offline Deterministic Benchmark for Tool Misuse and Recovery in Agentic Systems*, arXiv:2604.01508. https://arxiv.org/abs/2604.01508
Official public implementation located and read-only verified: https://github.com/akgitrepos/toolmisusebench

The public-test baseline table reports:
- Heuristic: success **0.250**, recovery **0.000**, calls **2.95**
- Schema repair: success **0.250**, recovery **0.250**, calls **3.25**
- Policy aware: success **0.250**, recovery **0.250**, calls **3.25**

Fault-specific results:
- timeout recovery: heuristic **0.000**, schema/policy **0.502**
- schema-drift recovery: heuristic **0.000**, schema/policy **0.497**
- authorization success: **0.000 for all**
- rate-limit success: **0.000 for all**

Thus schema-aware repair materially recovers two tractable operational fault classes while **aggregate task success stays 0.250**, and it does nothing for the released authorization and persistent rate-limit settings. The paper's policy-aware baseline is explicitly lightweight, so this is not evidence that all policy-aware replanning fails; it is evidence that recovery benefit is sharply conditional on the failure class and available continuation semantics.

The official repository exposes deterministic environments, fault injection, configs, tests, and experiment scripts. Generated paper result tables were not identified as committed standalone artifacts in the inspected public tree, so the exact numeric baseline values above remain primary-paper verified rather than independently artifact-recomputed in this invocation.

**Implication:** insert a `recoverability class / continuation feasibility` decision before spending critic/rollback/retry budget. For faults like schema drift or transient timeout, local repair/retry can be productive; for authorization or persistent hard availability failures, repeated local repair can consume budget without changing reachability. The right action may instead be fallback, reconcile, wait/abstain, or change the plan, depending on what the interface permits.

## Updated synthesis
The current long-horizon recovery controller should separate at least:

`state/interface distinguishability -> authorization/effect-identity closure -> recoverability classification -> intervention-value decision -> safe cut/admissibility -> historical target selection -> guidance/replan -> restore/carry-forward -> effect settlement -> commit revalidation -> repair stopping`

Two additional evaluation obligations are now load-bearing:
1. **Rescue-disruption accounting:** score both failed-source rescue and successful/benign-source disruption under matched intervention exposure.
2. **Fault-conditioned reachability:** do not pool faults where the same action cannot plausibly change outcome; otherwise aggregate recovery metrics can hide that repair is useful only on a subset and wastes budget elsewhere.

This does **not** establish that the above composed controller is optimal. No primary study located in this invocation cleanly crosses `ambiguous/legacy interface vs operable + authority/effect-bound interface` with `no recovery vs the same fixed recovery policy` under matched tasks, faults, model, provider state, and budget. Keep that factorial as an open gap.

## Artifact/status correction
- The SymTrace paper states that the supplementary material includes complete SymTrace source and the complete SymFail dataset, but the intended official source repository/API was still not independently located in read-only web/GitHub discovery this invocation. Do not treat the runtime API, no-op-guidance behavior, or code release URL as verified merely from secondary 'code released' badges.
- ToolMisuseBench's official public GitHub repository was located and its experiment/config/test structure was verified read-only.

## Exact continuation
1. Continue read-only search for the intended official SymTrace/SymFail source artifact; verify exact selective-replay API, target/guidance plumbing, and whether guidance can be held constant/no-op across target-selector arms.
2. Search for a matched `interface operability/authority-effect semantics × fixed recovery policy` 2x2. If absent, specify a minimal reproducible factorial using deterministic fault injection rather than inferring interaction effects from separate papers.
3. Find or specify same-prefix randomized reviewer/advice application on both failed and initially successful/benign prefixes; measure rescue, pass-to-fail disruption, realized recovery dose, and compute.
4. Preserve rollback-selector-only comparison under identical alarm, checkpoint candidate set, restore layers, carry-forward, inference state, model, guidance, stochastic coupling, and post-intervention budget.
5. Extend recoverability classification beyond timeout/schema/authz/rate-limit to distinguish transient, repairable-schema, state-loss, policy/authority, irreversible-effect, and external-unavailable classes with explicit permitted actions.
6. Continue exact single-admitted-update future-task ON/OFF frozen replay; randomized/propensity-logged reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; common-replicate admission × maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
7. Recover official numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
8. Maintain a nonempty frontier. This checkpoint is not global completion.
