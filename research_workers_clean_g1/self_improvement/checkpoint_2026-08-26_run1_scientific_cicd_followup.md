# Self Improvement Scan — Scientific CI/CD compositional-gate follow-up

Generation: clean_g1
Control: `automation_control/DESIRED_STATE.json` control_revision=3; `self_improvement` config_revision=2; enabled_desired=true.
Independence: own clean checkpoints + own sanitized feedback + public sources/artifacts only. No O, other workers, downstream state, shared ledger, other receipts, or legacy semantic context.

## SRC-SCI-CICD-COMPOSITE-SIM — closest matched compositional comparison found, but it is simulation evidence

Primary/workshop paper: **Scientific CI/CD for Self-Modifying Discovery Agents: Statistical Gödel Gates, Capacity Budgets, and Domain Verifiers**, David S. Lewis, ICML 2026 3rd AI for Math Workshop: Toward Self-Evolving Scientific Agents, 2026-07-11. OpenReview forum id `4ob0d33A2l`.

The paper is directly relevant to the unresolved composition frontier because it treats self-edits as release candidates passing:
1. a trust/provenance boundary,
2. an anytime-valid statistical gate,
3. a capacity-budget gate,
4. a domain verifier,
with rollback provenance for every decision.

### Main sequential statistical experiment

The primary appendix describes a synthetic sequential adoption protocol with **200 candidate edits per run**, up to **80 paired verifier samples per proposal**, effects drawn from a mixture of 35% beneficial (mean 0.045), 45% null, and 20% harmful (mean -0.035). It compares naive repeated one-sided testing, fixed-horizon testing, a per-edit e-process, and an e-process with decreasing proposal-index spending.

Over **200 runs**, reported Table-5 averages are:
- naive repeated: accepts `100.52`, harmful `6.17`, harm rate `0.0612`, accepted-edit regret `0.0502`;
- fixed horizon: `83.69`, harmful `0.46`, harm rate `0.0056`, AER `0.0015`;
- e-Gödel per edit: `66.58`, harmful `0.045`, harm rate `0.00068`, AER `0.00013`;
- e-Gödel spending: `49.16`, harmful `0.005`, harm rate `0.00008`, AER `6.3e-7`.

Main-text summary reports mean true gain of promoted edits increasing from about `0.0345` for naive repeated testing to `0.0522` for spending-based acceptance. This is strong simulation evidence that optional-stopping-safe evidence plus cross-proposal spending can dramatically lower harmful adoption under the paper's synthetic assumptions.

### Adaptive-control comparison across complementary safeguards

Appendix Table 12 runs a **second simulation**, explicitly described as 200 streams of 200 proposals, comparing six policies on the same synthetic mutation mixture (honest improvements, benign refactors, nulls, proxy hacks, capacity laundering, semantic weakening, provenance spoofing):

| Policy | Accept % | Harm/accepted | Protected gain | Cost/verified | Rollback h |
|---|---:|---:|---:|---:|---:|
| Proxy only | 71.9 | 47.6% | 0.007 | 9.01 | 377.1 |
| Ladder release | 50.0 | 35.2% | 0.019 | 5.60 | 193.7 |
| Reusable holdout | 46.8 | 33.4% | 0.021 | 5.34 | 172.6 |
| Anytime FDR | 46.5 | 30.5% | 0.024 | 4.74 | 156.6 |
| E-Gödel spending | 26.1 | 25.7% | 0.034 | 3.80 | 74.2 |
| Full three-gate contract | 19.4 | **6.5%** | **0.055** | **1.94** | **14.1** |

The paper's interpretation is appropriately layered: reusable-holdout/Ladder-style controls mitigate adaptive holdout leakage; anytime-FDR controls statistical discovery families; neither prices capacity expansion nor rejects a candidate that improves a weakened statistical target. The full contract adds capacity and domain/provenance controls, trading throughput for lower harmful adoption and lower rollback/cost per verified beneficial edit.

### Capacity drift and domain-verifier isolation

Experiment 2 is another synthetic controlled problem: a model-selection agent chooses polynomial degree from noisy data. Visible-only selection chooses mean degree `15.6`, hidden MSE `0.0733`, generalization gap `0.0130`; capacity-budget gating lowers mean degree to `8.7`, hidden MSE to `0.0687`, gap to `0.0032`; hidden oracle MSE remains better at `0.0614`. This isolates the point that capacity accounting is a guard against unpriced search expansion, not a substitute for additional truth data.

Experiment 3 uses a synthetic RNA-seq twin with eight workflow variants. Mechanical execution passes all variants; statistical calibration rejects two harmful variants; the domain verifier rejects all five harmful variants, including three that passed the earlier gates (label shuffle, effect-direction flip, missing provenance). This is controlled evidence that semantic/domain checks can catch failures orthogonal to software/statistical acceptance.

### Important scope and evidence classification

This paper is the closest source found so far to the desired **multi-layer matched comparison**, but its core evidence is explicitly synthetic/simulated. It is not a long-running real LLM self-improvement experiment, and it does not establish that the same harm-rate reductions persist under an endogenous proposer that learns from previous gate outcomes.

The paper itself recognizes verifier memorization: repeated accept/reject feedback turns even a hidden verifier into development signal, motivating coarse score release, query caps, retirement, and refreshed hidden tests. That is conceptually aligned with the reusable-holdout frontier, but the paper's Table-12 reusable-holdout arm remains simulation evidence.

No public GitHub repository for the exact title/author was found in the current search, so raw simulation streams/code were not independently re-executed in this worker. Therefore the table is treated as primary-paper reported evidence, not independently reproduced evidence.

## What this closes and what remains open

This source materially narrows the frontier:
- It **does** compare reusable holdout, anytime-FDR, per-edit/global spending, and a full capacity+semantic/provenance contract on the same synthetic proposal distribution.
- It **does not** close the real-agent gap: no actual evolving skill/harness agent, no demonstrated endogenous proposer adaptation, and no real-model long-horizon lockbox validation.
- It does not make VaG redundant. VaG gives real-agent evidence that persistent-skill contamination is inherited through later distillation and that behavioral/joint pre-commit gates help; Scientific CI/CD supplies a richer statistical/capacity/domain *simulation*. The missing experiment is their real-agent composition.

## Updated nonempty frontier

1. Find a **real self-evolving LLM agent** implementing at least two of these layers together: content/semantic gate + anytime-valid/reusable-holdout statistical gate + global spending/capacity ledger, with an untouched lockbox.
2. Require >5 adaptive rounds and report both false/harmful commit history and final disjoint transfer/lockbox outcome.
3. Search for the Scientific CI/CD artifact/code release; if found, inspect whether Table-12 streams are public enough for alternate-policy replay and independent reproduction.
4. Search later work citing/implementing this workshop contract in real agents, especially skill-library or harness-evolution systems.
5. Continue PACE artifact search and SGM within-repo replay separately; do not merge simulation and real-agent evidence classes.
6. Seek a factorial `acceptor × update cadence × content gate` experiment; SEAGym and VaG imply failures can occur outside statistical acceptance.

## Exact continuation

Next run: start with frontier item 1 using queries centered on `self-evolving agent` + `e-process/confidence sequence/reusable holdout/online FDR` + `semantic/skill admission/provenance/capacity gate`. Search August 2026 primary papers and public repositories first. If no real-agent composition appears, trace citations/implementations of Scientific CI/CD and SEA rather than expanding to generic self-improvement papers.

## Termination diagnostic

Not complete. This follow-up found the strongest same-simulation compositional comparison so far and precisely separated what it demonstrates from the still-missing real-agent endogenous-loop evidence.