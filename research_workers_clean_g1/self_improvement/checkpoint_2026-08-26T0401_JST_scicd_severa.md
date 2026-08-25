# CLEAN self-improvement checkpoint — joint adaptive-control gates and deterministic formal verification

Time: 2026-08-26 04:01 JST
Role: self_improvement / clean_g1
Control: DESIRED_STATE control_revision=6; self_improvement config_revision=3.
Continuation: own clean `LATEST.json` checkpoint + public primary/public artifact sources + own sanitized feedback only. No O, other-worker, downstream, or legacy semantic state was read.
Feedback: own source-local ID-stability item was already acknowledged; new candidate identifiers below are source-qualified.

## SIG-SCICICD-ADAPTIVE-CONTROL

Primary/workshop paper: David S. Lewis, *Scientific CI/CD for Self-Modifying Discovery Agents: Statistical Gödel Gates, Capacity Budgets, and Domain Verifiers*, ICML 2026 3rd AI for Math Workshop / OpenReview, July 2026.
Primary PDF/searchable record: https://openreview.net/forum?id=4ob0d33A2l (paper PDF is linked from the forum / ICML workshop listing).

This is the closest source found in this run to the frontier asking for **joint control of adaptive repeated selection, statistical acceptance, capacity growth, domain semantics/provenance, and rollback**. It does not implement SkillBrew-style Keep/Rewrite/Remove persistent-skill curation, but it directly compares several adaptive-control mechanisms under the same long proposal stream.

### Merge contract

A proposed self-edit is treated as a high-risk pull request. The contract includes:
1. sandboxed candidate construction + diff/dependency/tool-privilege/seeds/rollback provenance;
2. paired incumbent-candidate verifier samples with an anytime-valid e-process / confidence-sequence gate;
3. a capacity-budget gate that prices expansion in model/tool/memory/data/autonomy surfaces;
4. a domain verifier for semantic/scientific invariants and provenance;
5. promotion only after all gates pass.

This cleanly separates statistical evidence from semantic/domain correctness. The paper explicitly motivates that reusable-holdout leakage, optional stopping, evaluator access, and capacity expansion are distinct failure surfaces.

### Sequential adoption experiment

The paper simulates **200 candidate self-edits per stream**, with each proposal allowed up to **80 paired verifier samples**. Compared policies include naive repeated one-sided tests, fixed-horizon tests, per-edit e-Gödel tests, and a spending-based e-Gödel rule.

Reported values:
- naive repeated testing: **100.5 accepted edits/stream**, **6.17 harmful adoptions/stream** on average;
- spending-based e-Gödel: **49.2 accepted edits/stream**, **0.005 harmful edits/stream**, reported harmful-adoption rate **0.008%**;
- mean true gain of promoted edits increases from **0.0345** (naive) to **0.0522** (spending gate).

The important causal scope is statistical/admission policy under this synthetic edit-mixture simulator. It is not evidence that a real LLM agent will realize these exact rates.

### Direct adaptive-control comparison (200 streams × 200 proposals)

The supplement compares six policies over the same proposal-mixture setup containing honest improvements, benign refactors, null edits, proxy hacks, capacity-laundering edits, semantic weakening, and provenance spoofing.

| policy | accept % | harmful / accepted | mean protected gain | normalized cost / verified beneficial edit | rollback hours |
|---|---:|---:|---:|---:|---:|
| proxy-only | 71.9 | 47.6% | 0.007 | 9.01 | 377.1 |
| Ladder-style release | 50.0 | 35.2% | 0.019 | 5.60 | 193.7 |
| reusable holdout / Thresholdout-style | 46.8 | 33.4% | 0.021 | 5.34 | 172.6 |
| anytime-FDR / stopped e-BH | 46.5 | 30.5% | 0.024 | 4.74 | 156.6 |
| e-Gödel spending | 26.1 | 25.7% | 0.034 | 3.80 | 74.2 |
| **full three-gate contract** | **19.4** | **6.5%** | **0.055** | **1.94** | **14.1** |

This directly demonstrates that **reusable holdout, anytime multiple-testing control, global spending, capacity control, and semantic/provenance verification protect different error surfaces** in the simulator. Reusable holdout or anytime-FDR alone materially reduce harmful acceptance but still admit edits whose proxy/statistical target has been weakened. The full contract sacrifices throughput but has the best protected gain and rollback-cost outcome in this tested setup.

This is stronger than treating one statistical gate as sufficient. It supports a layered acceptor for self-improvement: `anytime statistical evidence + global spend/capacity accounting + semantic/domain/provenance verifier`.

### Capacity-drift experiment

A self-modifying model-selection agent chooses polynomial degree against a small visible verifier.
- visible-only selection: mean degree **15.6**, hidden MSE **0.0733**, generalization gap **0.0130**;
- capacity-budget gate: mean degree **8.7**, hidden MSE **0.0687**, gap **0.0032**;
- hidden oracle MSE: **0.0614**.

So capacity pricing reduces hidden-risk overfitting but does not substitute for fresh hidden data.

### Dry-lab domain verifier

In a synthetic RNA-seq twin, eight workflow variants include benign and harmful modifications. Mechanical execution passes every variant. Statistical calibration rejects two harmful edits; the domain verifier rejects **all five harmful edits**, including three that passed mechanical/statistical gates (examples described include shuffled labels, flipped effect directions, and missing provenance).

This is direct evidence, in a synthetic biomedical workflow, that semantic/domain checks are not redundant with software execution or statistical significance.

### Scope / limitation

- The key 200-proposal results are **simulation**, not a persistent real LLM skill-bank stream.
- The model-selection and RNA-seq experiments are controlled/synthetic instantiations.
- This paper therefore fills the **joint adaptive-control / multiplicity / capacity / semantic-verification** part of the frontier, but not the still-missing integrated experiment combining these gates with >10-round Keep/Rewrite/Remove skill curation and a truly untouched final lockbox.
- The paper should not be used to claim global safety of self-modification; it validates a governance architecture under its tested simulated/controlled settings.

## SIG-SEVERA-FORMAL-GUARD

Primary: Debangshu Banerjee, Changming Xu, Eugene Ie, Ming Zhang, Daiyi Peng, Chu-Cheng Lin, Gagandeep Singh, *SEVerA: Verified Synthesis of Self-Evolving Agents*, arXiv:2603.25111 (v1 2026-03-26; later 2026 revision), https://arxiv.org/abs/2603.25111
Public repository: https://github.com/uiuc-focal-lab/severa — current README says **“Code will be released soon”**, so artifact evidence is currently repository-level metadata/README rather than executable reproduction.

SEVerA directly addresses another branch of the frontier: when the domain admits a **deterministic/formal verifier**, replace LLM-only diagnosis for hard constraints with executable/formal contracts.

### Mechanism

SEVerA synthesizes agent programs containing Formally Guarded Generative Model (FGGM) calls. Each call has a first-order-logic output contract, a deterministic checker, rejection sampling, and a **verified fallback**. The fallback is essential: if all samples fail the checker, the call still returns a formally valid output. Verification is parameter-independent, so model parameters can later be optimized without invalidating the hard contract.

The overall loop is Search → Verification → Learning: candidate parametric programs are synthesized, verified against hard constraints for all parameter values, then optimized on soft task objectives.

### Actual agentic-tool-use results

On $\tau^2$-bench with Qwen3-8B:

**Retail**
- vanilla LLM: pass **11.3%**, violations **76.3%**;
- Agent-C baseline: **42.2%**, violations **0%**;
- SEVerA without constraints: **49.4%**, violations **10.3%**;
- full SEVerA: **53.6%**, violations **0%**.

**Airline**
- vanilla LLM: **13.2%**, violations **68.4%**;
- Agent-C: **39.4%**, violations **0%**;
- SEVerA without constraints: **44.7%**, violations **25.5%**;
- full SEVerA: **52.6%**, violations **0%**.

Thus in these tested policy-compliant tool-use tasks, hard formal constraints eliminate the policy violations while the verified synthesis loop also improves task pass rate relative to the same framework without constraints.

### Symbolic-math matched evidence

GSM-Symbolic with Qwen3-8B:
- vanilla: **38.3% accuracy / 10.6% violations**;
- CRANE: **44.7% / 2.1%**;
- SEVerA without parameter tuning: **53.2% / 0%**;
- SEVerA with tuning: **66.0% / 0%**.

Constraint/tuning decomposition:
- no parameter tuning: **53.2%**;
- local-contract-only tuning: **55.3%**;
- global-task-only tuning: **61.7%**;
- full local+global tuning: **66.0%**;
- all four SEVerA variants report **0% violations** in this table.

This shows that a hard deterministic contract need not be a pure safety tax; in this setting it prunes invalid behavior while soft/global optimization still improves utility.

Constrained symbolic regression likewise reports test-specification violation rates of **62.86%** for PySR, **31.43–34.29%** for LLM-SR, and **0%** for SEVerA, with lower NMSE on the constraint-satisfying comparison set.

### Scope / limitation

- SEVerA verifies **hard formal behavioral constraints**, not fuzzy/general task-quality attribution.
- It does not solve adaptive reuse of a small acceptance set, proposal multiplicity, or persistent Keep/Rewrite/Remove skill-bank lifecycle.
- Therefore the best synthesis is hybrid: use deterministic/formal verifiers for mechanically specifiable invariants, and reserve statistical/semantic/LLM judges for residual properties that cannot be formalized; those residual judges still need calibration and adaptive-selection control.
- Public code was not yet released in the repository observed in this run, so independent executable reproduction remains open.

## SkillBrew artifact/status follow-up

The SkillBrew primary paper contains no GitHub/repository link in the arXiv text. The first author Wentao Hu's homepage now labels SkillBrew **EMNLP 2026 (Main)**, upgrading the publication status from the earlier under-review checkpoint. The same homepage links to the author's GitHub, whose public profile currently shows only three repositories (`wentaohu1208.github.io`, `mmskills`, `CityU-CS-Guide`), none named/identified as SkillBrew. Broad exact-title/arXiv/GitHub searches in this run did not surface an official implementation or an independent reproduction. This is an **artifact-access finding**, not proof that no private or unindexed implementation exists.

## Synthesis

The frontier now has a clearer layered design:

`candidate generation`
→ `mechanical/formal invariant checks where possible (SEVerA-style)`
→ `paired anytime-valid incumbent/candidate evidence`
→ `global statistical spending / multiplicity control`
→ `capacity-expansion pricing`
→ `semantic/domain/provenance verifier`
→ `versioned promotion + rollback`
→ `fresh/untouched outer outcome audit`.

SkillBrew/SAPO-style lifecycle curation and Scientific-CI/CD-style adaptive control cover complementary layers. The missing decisive experiment is still a **real persistent LLM agent over >10 rounds** that combines lifecycle Keep/Rewrite/Remove, deterministic checks where applicable, global adaptive statistical acceptance, capacity control, and a truly untouched final panel.

## Nonempty frontier / exact continuation

1. Search for a real >10-round LLM-agent implementation that combines persistent skill/memory lifecycle repair/retirement with e-process/reusable-holdout/global spending; Scientific CI/CD currently supplies only simulated/controlled adaptive-control evidence.
2. Search for systems that use deterministic program/test/formal verifiers to attribute the ordinary *utility* of persistent skills, not only hard safety/specification validity; compare with LLM-judge counterfactual diagnosis.
3. Investigate joint multiplicity at two levels: multiple candidate edits generated inside a round and repeated incumbent/checkpoint selection across rounds. Look specifically for hierarchical e-values/e-BH/alpha-investing or closed-testing wrappers applied to agent evolution.
4. Check for public SkillBrew code/reproduction after EMNLP 2026 publication assets appear; if released, verify leave-one-out replay caching, null-bank candidate handling, round count, and whether Remove retains benefit on a fresh outer panel.
5. Continue seeking an untouched lockbox/final test after the full adaptive loop; protected/reused holdouts are not equivalent to an untouched final audit.
