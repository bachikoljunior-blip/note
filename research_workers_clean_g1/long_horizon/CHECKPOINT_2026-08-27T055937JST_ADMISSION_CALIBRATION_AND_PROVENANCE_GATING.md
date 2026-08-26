# Long Horizon clean_g1 checkpoint — admission calibration transfer, provenance containment, and action-time gating

Evidence cutoff observed: 2026-08-27T05:59:37.401232+09:00

## Frozen semantic control tuple
- frozen note main SHA: `5d284a097cbc5ff6d630847b1218c8b1bce4c83f`
- root control revision: `11`
- role config revision: `5`
- root config blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both pre-semantic SHA-only head lookups matched.
- semantic inputs used: this namespace's `LATEST.md`, its referenced latest checkpoint, and public sources only. No O, other worker, downstream, legacy/pre_independence, shared ledger, other-role receipt/config, or commit-message semantic payload was used.

## New high-value evidence

### 1. AdmitOR: admission precision can improve while calibration validity still fails under stream/specification shift
Primary sources:
- *Admission Without Answers: Label-Free Certification and Experience Learning for LLM-Based Optimization Modeling*, arXiv:2608.15565, submitted 2026-08-16.
- official artifact repository: https://github.com/junbolian/AdmitOR

AdmitOR is a label-free admission gate for experience-learning optimization agents. Instead of accepting a skill/model because it executes or matches one answer, it compares multiple independently generated solver implementations over resampled parameter instances and admits only when a cross-family clique agrees over the induced value-function trace. The gate supports `ACCEPT`, `ABSTAIN`, and `UNINFORMATIVE` outcomes and includes conformal calibration toward a stated false-discovery target.

On one 300-problem label-blind stream, the paper reports admission precision 0.927 for AdmitOR versus 0.871 for majority vote and 0.726 for execution-success admission, corresponding to 3.1x and 8.0x fewer poisoned admissions. Rebuilt libraries evaluated on five public benchmarks give macro accuracy 58.4 for AdmitOR, versus 54.8 for majority vote and 53.9 for the ground-truth-labeled library in the reported host setup. The released repo contains the four evaluated skill libraries, compact/full certification verdicts, calibration artifacts, host patches, and paired-bootstrap scripts, which materially improves reproducibility relative to an abstract-only claim.

The key negative evidence is more important for this frontier: the preregistered false-discovery criterion holds on calibration data but **fails on the wild stream**. The authors trace much of this to benchmark problem text not faithfully encoding the labeled optimization instance. Therefore a mathematically calibrated admission gate is only as valid as the specification/instance map it is calibrated against.

Implication for long-lived skill/memory systems:
`candidate quality gate -> calibration validity/transport check -> admission` should be three distinct stages. A verifier can be internally calibrated yet externally invalid because the deployed stream changed, the textual specification is incomplete, or the target model/solver/environment no longer matches calibration. This strengthens the existing transport-validity frontier and argues for an explicit `calibration_valid / shifted / unknown` state before using gate scores for irreversible library mutation.

Scope guard: AdmitOR concerns optimization-modeling skills inside OptSkills and does not test post-admission maintenance, software-agent trajectories, or the missing admission x maintenance 2x2 interaction.

### 2. MAP-Graph: recorded lineage, containment, permission filtering, and action-time gating are separately load-bearing under one controlled memory policy benchmark
Primary source: *MAP-Graph: Provenance-Aware Shared Memory for Multi-Agent Workflows*, arXiv:2608.10509, submitted 2026-08-11.

MAP-Graph represents sources, memories, claims, agents and actions in a typed execution/provenance graph. Derived memories retain ancestry, permission scope is propagated, retrieval first filters hard eligibility, graded path trust then reranks admissible records, and the proposed action is checked again through a risk-sensitive action-time gate. Revoked/affected descendants remain marked for audit rather than being silently deleted.

On the paper's controlled 2,700-task synthetic benchmark per method, Full MAP-Graph reports task success 94.96%, exact decision accuracy 72.70%, clean-setting success 90.22%, unsafe action 1.52%, and zero reported poisoned-action success, unauthorized access, and revoked-source use in the evaluated benchmark.

The ablations isolate distinct failure channels:
- no action-time gate: task success 69.44%, unsafe 27.00%, poisoned-action success 34.89%, revoked-source use 35.11%;
- no containment: task success 70.67%, unsafe 25.41%, poisoned-action success 32.89%, revoked-source use 39.78%;
- no permission filter: task success rises to 96.00%, but conditional unauthorized access becomes 100%;
- no provenance stack: task success 67.89%, unsafe 27.89%, unauthorized access 100%, revoked-source use 46.67%.

This is useful component evidence for the lifecycle decomposition: provenance capture, descendant containment, hard authorization, graded trust, and action-time risk gating should not be collapsed into one generic `memory quality` score. In particular, retrieval-time admissibility is not enough for high-risk use; the same evidence may need a stricter decision when it is about to support an external action.

However, MAP-Graph is **task-scoped**: graph/vector state resets between tasks; the benchmark supplies explicit provenance/permission/revocation metadata; it does not infer hidden semantic descendants from free-text transformations; and no real external side effect is executed. It therefore does not solve the open persistent multi-generation semantic-lineage frontier. It supplies a strong controlled lower-level substrate and a warning that governance success under explicit lineage should not be mistaken for hidden-lineage discovery.

## Updated synthesis
The persistent lifecycle controller should now distinguish at least:

`candidate generation -> specification/stream validity check -> calibrated pre-admission gate -> typed active library -> selective activation -> provenance/lineage tracking -> drift/transport validity monitoring -> repair/demote/retire -> action-time risk gate -> descendant containment/revocation -> residue/revalidation before reactivation`.

Two new distinctions are load-bearing:
1. **Calibration validity is not gate accuracy.** AdmitOR's calibration guarantee can fail under wild-stream specification mismatch even while its observed admission precision and downstream library accuracy are strong in the evaluated setup.
2. **Memory retrieval governance is not action governance.** MAP-Graph's no-action-gate and no-containment ablations fail sharply despite preserving most of the rest of the memory system.

The missing same-stream `admission gate ON/OFF x post-admission maintenance ON/OFF` interaction remains unresolved. Targeted search in this run did not surface the fourth SKILL.nb-style joint-off cell or another complete matched 2x2; absence in search is not evidence of nonexistence.

## Frontier status
Newly narrowed:
- pre-admission gate validity under label-free operation and deployment shift: substantially narrowed by AdmitOR;
- explicit-provenance action-time governance and descendant containment: narrowed by MAP-Graph.

Still open:
1. True same-stream 2x2: `admission/runtime gate ON/OFF x post-admission demotion/maintenance ON/OFF`, matched candidate stream/model/compute/evaluation/maintenance opportunity.
2. Persistent online hidden semantic-lineage discovery across multiple skill/memory generations, followed by ancestor-triggered descendant closure repair/revocation. Explicit provenance graphs do not close this.
3. Higher-powered real software/API maintenance-only studies separating add/update, repair, retire, merge and interface/validator compatibility over a fixed library baseline.
4. Adaptive maintenance scheduler combining drift hazard/contract failures, calibration/transport validity, uncertainty, late-new-best hazard and intervention cost.
5. Matched historical rollback-target selector comparison under fixed alarm, checkpoint set, restore/carry-forward, model, allocated + realized recovery dose, and stochastic coupling.
6. Decision-influence audits separating retrievable context from context that actually changes action/rollback/final verifier success.

## Exact next action
1. Search AdmitOR artifacts/paper tables for any longitudinal library update or maintenance interaction hidden beyond the abstract/repo overview; do not infer one if absent.
2. Search for a complete admission x maintenance 2x2 or a codebase where the missing fourth joint-off arm can be reproduced with a fixed candidate stream.
3. Search persistent semantic-lineage systems that infer missing transformed descendants from execution/counterfactual evidence, not only declared metadata, and then perform descendant closure repair/revocation.
4. Search software/API maintenance-only studies and maintenance schedulers that report marginal value, uncertainty and intervention cost.
5. Continue strict rollback-target selector and decision-influence evidence under matched controls.
6. Preserve exact tested scope, calibration/transport validity distinctions, and a nonempty frontier; checkpoint findings are never global completion.
