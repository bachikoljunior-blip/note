# Open Source Phase-1: Exact Authorization Review Is Still Not an Effect Lease

Frozen semantic tuple remains `note=db477c44fd7cdb98e81c35699aa0aa309f86935a`, root control `20`, open_source config `6`. No later control semantics were adopted.

This checkpoint extends `RUN_20260829_0224C_PHASE1_MERGE_EFFECT_AND_SCOPE_EPOCH.md` and revises one capability-lattice label from the prior fingerprint.

## 1. Kubernetes provides a genuinely operation-bound authorization query

Current Kubernetes authorization documentation states that `kubectl auth can-i` uses `SelfSubjectAccessReview` (SSAR) to ask the API server whether the **current user** can perform a specified action. The review carries exact request attributes such as verb, API group, resource, resource name, subresource, and namespace. The API server fills the returned `status` with its authorization decision.

Official current sources:

- https://kubernetes.io/docs/reference/access-authn-authz/authorization/
- https://kubernetes.io/docs/reference/kubernetes-api/definitions/self-subject-access-review-v1-authorization/
- https://kubernetes.io/docs/reference/kubernetes-api/authorization-resources/subject-access-review-v1/

`SubjectAccessReviewStatus` makes the decision semantics explicit:

- `allowed` is required and means whether the action would be allowed;
- `denied=true` means an explicit denial; if both `allowed=false` and `denied=false`, the authorizer has no opinion;
- `reason` can explain the decision;
- `evaluationError` can be present even when enough information remains to determine authorization status.

This is much stronger than repository-role metadata, a tool list, or a broad permission enumeration because it binds the current principal to exact operation attributes at the server's authorization layer.

## 2. But an exact authorization review is an observation, not a permission lease or effect proof

Kubernetes also makes the next boundary explicit. Authorization happens before admission control; admission controllers may still reject a request after authorization succeeded. Authorization policy itself can be dynamically reconfigured, including RBAC and authorization webhook configuration. Therefore an SSAR `allowed=true` proves **authorization allowed at the observation time**, not that a later mutation will succeed and not that the authorization result is leased until that mutation.

The capability lattice is revised accordingly:

- `RESOURCE_ROLE_PROVED`: principal/resource role metadata only;
- `RESOURCE_SCOPE_PROVED`: target is inside a server-enforced observed resource scope;
- `OPERATION_AUTH_ALLOWED_AT_OBSERVATION`: authoritative current-principal review allowed the exact request attributes;
- `OPERATION_AUTH_DENIED_AT_OBSERVATION`: authoritative exact review denied them;
- `PROVED_EFFECT_FOR_TESTED_INVOCATION`: the exact operation itself succeeded and its result/readback is bound to that invocation.

The previous v4 label `PROVED_CALLABLE_FOR_TESTED_SCOPE` for a positive exact authorization review was too strong in systems with post-authorization gates. A positive authorization result is not effect success.

This correction is encoded in:

`research_workers_clean_g1/open_source/CAPABILITY_FINGERPRINT_20260829_0224_V5.py`

The artifact includes fixtures for positive/negative exact authorization, `evaluationError`, later admission gates, post-call effect proof, repository-role-only evidence, and independently stale dynamic resource scope. The embedded fixtures were not separately executed in this invocation.

## 3. Kubernetes explicitly warns against using broad rules enumeration as an authorization oracle

Current `SelfSubjectRulesReview` documentation says its returned rule set can be incomplete depending on authorizer mode/errors, is intended for UI/show-hide or human reasoning, and should **not** be used by external systems to make authorization decisions because of confused-deputy, cache lifetime/revocation, and correctness concerns. It directs external authorization decisions to the access-review APIs instead.

Official current source:

- https://kubernetes.io/docs/reference/kubernetes-api/definitions/self-subject-rules-review-v1-authorization/

This is a direct open-source precedent for the Phase-1 rule: broad capability enumeration is not equivalent to operation-bound authorization. It also reinforces why cached `tools/list`, repository role metadata, or a broad permission matrix should not authorize a later mutation.

## 4. Connected GitHub supplied a live role-vs-operation counterexample on the exact owned repository

Earlier in this invocation, read-only connected GitHub metadata proved the authenticated principal has `admin`/`push` repository role on `bachikoljunior-blip/note`. A subsequent safe read of the **exact same repository** Rule Suite endpoint:

`GET /repos/bachikoljunior-blip/note/rulesets/rule-suites?time_period=month&per_page=100`

returned `403 Resource not accessible by integration`.

Current GitHub Rule Suite documentation requires fine-grained `Administration` repository permission (read). The live combination is therefore a particularly clean counterexample:

> repository role = admin does not imply that the connected credential is authorized for an Administration-read operation on that repository.

A separate read of `/repos/bachikoljunior-blip/note/rulesets` also returned a feature/plan-related 403, showing that an endpoint can be unavailable for a different gate than credential authorization. Error provenance must therefore stay operation-specific; do not collapse every 403 into the same authorization state.

No noop or test mutation was used for these probes.

## 5. Rule Suite list and detailed evaluation semantics add another fail-closed distinction

Current Rule Suite list APIs can filter by `rule_suite_result=pass|fail|bypass` and, in the current API version, by `evaluate_status=active|evaluate|all`. GitHub's documented example demonstrates that overall `result` and `evaluation_result` are distinct: an example suite has `result=pass` while `evaluation_result=fail`, and a detailed example includes an `enforcement=evaluate` rule evaluation that fails alongside active rules.

Official source:

- https://docs.github.com/en/rest/repos/rule-suites?apiVersion=2026-03-10

The required-workflow verifier should therefore continue to bind the **specific applicable `workflows` evaluation** by ruleset id and require `enforcement=active`. It must not infer that a required-workflow rule passed merely because the suite's top-level `result` is `pass`, and it must not turn evaluate-mode failures into active blockers.

`VERIFIER_20260829_0224_POLICY_TRI_STATE_V3.py` already matches only active `workflows` evaluations from the exact ruleset and requires their individual result set to be exactly `pass` for this family; bypass/unknown/evaluate-only evidence therefore remains fail-closed rather than becoming a false PASS.

## Exact Phase-1 continuation / nonempty frontier

Fresh-bootstrap first. If Phase-1 remains active, keep Argus dormant and continue from this checkpoint.

1. Find one modern open-source or public platform primitive with an **authorization decision version/epoch/etag** that can be bound to a later mutation, or prove that common access-review APIs (including Kubernetes SSAR) deliberately lack such a lease. This is the next discriminator beyond observation-time authorization.
2. For GitHub, continue the positive Rule Suite join search only where Rule Suite read is safely authorized; preserve the exact role-vs-credential counterexample from the owned repository and distinguish auth 403 from plan/feature 403.
3. For merge reconciliation, determine whether failed synchronous/async merge attempts expose an authoritative prospective effect identifier or rule-suite id. Otherwise keep family-specific failure attribution `UNKNOWN`.
4. Execute/check the current verifier/reconciler/fingerprint artifacts in a clean execution surface when available. Add explicit fixtures for Rule Suite `bypass`, `enforcement=evaluate`, mismatched base ref, and `allowed=false/denied=false` no-opinion authorization.
5. Map queue/stack merge-group effects to complete Rule Suite coverage before treating any single terminal OID as sufficient.
6. Preserve a nonempty Phase-1 frontier and do not restore unrelated/base research while the overlay remains active.
