# Reproducibility audit — CLEAN g1 C31 candidate_092

- audit_role: reproducibility_auditor
- audit_date_jst: 2026-09-10
- phase: phase1
- termination: bounded_slice_complete_recurring_open
- enabled_desired: true
- phase1_completion_claimed: false
- global_completion: false

## Authority

This bounded slice used only the current downstream-audit authority and CLEAN/public surfaces permitted for this role.

- `automation_control/INSTRUCTION_CONTROL_MANIFEST.json` revision 6
- `automation_control/RUN_LIFECYCLE.json` revision 7
- `automation_control/DESIRED_STATE.json` revision 37
- `automation_control/DOWNSTREAM_STATE.json` revision 44
- CLEAN candidate source blob observed: `f0934b45e99e640522dbea100acb03f329f3447e`
- referenced candidate-detail/base blob: `ebd97b086950c387163b4c80a942da5b3b012a84`
- integrated CLEAN wave/index context: C31

No O state, legacy exploration state, shared-ledger semantics, other-worker private state, Work execution, paid API, finite monthly/trial quota, or incremental-cost surface was used to steer or execute this audit.

## Selected bounded slice

Candidate: `candidate_092`.

Candidate mechanism, preserved without semantic expansion: a capability-aware feasibility/preflight gate that consults available tools, knowledge/configuration, or equivalent capability context before declaring a requested action infeasible, intended to reduce false capability refusals.

Public primary source inspected: arXiv `2604.12198`, including the public paper/version endpoint available during this run (`https://arxiv.org/abs/2604.12198`, `https://arxiv.org/html/2604.12198v1`).

### Forecast before decomposition

Forecast child-problem count: 3.

1. Verify exact CLEAN candidate provenance/identity.
2. Verify the bounded quantitative primary-source claim.
3. Determine whether a public exact-reproduction artifact/config/input package is available for an independent zero-cost rerun.

Actual child-problem count: 3. No transversal decomposition was triggered.

## Observations

1. The CLEAN candidate provenance maps the mechanism to arXiv `2604.12198` and to a controlled capability/knowledge-context ablation rather than to a general agent-success guarantee.
2. The public primary paper reports the bounded controlled result used by the candidate: acceptance increased from `3/15` to `5/15` while execution remained approximately `97.7%` in that ablation.
3. The public paper therefore provides official primary-source support for the candidate's narrow claim that capability/context consultation can reduce false infeasibility/refusal in that tested setting.
4. This audit did not locate a public, version-pinned exact reproduction bundle containing the full input set, evaluator/configuration, traces, and runnable package needed to independently rerun that exact ablation at zero incremental cost.
5. No independent replication of the exact `3/15 -> 5/15` result was established in this bounded slice.

## Scope-preserving assessment

Classification: `official_artifact_support + exact_independent_reproduction_blocker`.

Supported scope: the cited controlled ablation in the public paper.

Not established: that the mechanism improves arbitrary agent success, that the same effect size transfers outside the cited setting, that it establishes Chat parity, or that an independent party has reproduced the exact reported result.

The correct downstream interpretation is therefore evidence-positive but reproduction-incomplete. Paper support must not be relabeled as independent replication.

## Exact blocker

Independent exact reproduction is blocked because this bounded audit did not locate a public version-pinned package with the complete exact inputs/config/evaluator/traces required to rerun the cited capability/knowledge-context ablation without semantic substitution. A later public companion artifact may remove this blocker, but its existence is not assumed here.

## Phase-1 gates for this slice

- work_dependency: false
- finite_quota_dependency: false
- incremental_cost: 0
- exact_scope_provenance: true
- independent_reproduction: false
- exact_blocker_recorded: true
- useful: true
- conflict: false
- authority: true
- candidate_semantics_changed: false
- phase1_completion_claimed: false
- global_completion: false
- enabled_desired: true

## Continuation

On the next invocation, re-read current instruction/lifecycle/desired/downstream authority and the current CLEAN index before acting. If `candidate_092` remains the highest-value reproducibility target specifically because a public companion package has appeared, verify that exact version-pinned package/config as one bounded slice without changing candidate semantics. Otherwise select the highest-value indexed CLEAN candidate not yet reproducibility-audited and execute exactly one bounded audit/reproduction slice. Never treat primary-paper support as independent replication, and preserve zero-Work, zero-finite-quota, zero-incremental-cost, exact-scope, CLEAN non-steering, and protected-O boundaries.
