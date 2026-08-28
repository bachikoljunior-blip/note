from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Classification(str, Enum):
    PRIOR_AUTH_REVISION_EFFECT_GATE = "PRIOR_AUTH_REVISION_EFFECT_GATE"
    DECISION_REVISION_FENCE = "DECISION_REVISION_FENCE"
    POLICY_MODEL_PIN_ONLY = "POLICY_MODEL_PIN_ONLY"
    MUTABLE_POLICY_CAS = "MUTABLE_POLICY_CAS"
    REQUEST_LOCAL_AUTH_WITH_STATE_CAS = "REQUEST_LOCAL_AUTH_WITH_STATE_CAS"
    APPROVAL_AND_EXACT_INTENT = "APPROVAL_AND_EXACT_INTENT"
    IDEMPOTENT_EFFECT_RETRY = "IDEMPOTENT_EFFECT_RETRY"
    PROVENANCE_ONLY = "PROVENANCE_ONLY"
    UNPROVED = "UNPROVED"


@dataclass(frozen=True)
class Evidence:
    auth_decision_revision: bool = False
    exact_snapshot_replay: bool = False
    prior_auth_revision_effect_precondition: bool = False
    immutable_policy_model_id: bool = False
    stronger_read_consistency_only: bool = False
    mutation_state_token: Optional[str] = None
    mutation_precondition_same_token: bool = False
    request_local_authorization: bool = False
    approval_content_id: Optional[str] = None
    effect_content_precondition: Optional[str] = None
    idempotency_key_replay: bool = False
    provenance_id_only: bool = False


def classify(e: Evidence) -> Classification:
    # Strongest class: the effect-serving API itself accepts the prior
    # authorization decision revision as an atomic mutation precondition.
    if e.auth_decision_revision and e.prior_auth_revision_effect_precondition:
        return Classification.PRIOR_AUTH_REVISION_EFFECT_GATE

    # Strong request-local pattern: current authorization is evaluated on the
    # mutation request and mutable target state is guarded by a matching token.
    if (
        e.request_local_authorization
        and e.mutation_state_token
        and e.mutation_precondition_same_token
    ):
        return Classification.REQUEST_LOCAL_AUTH_WITH_STATE_CAS

    # Approval provenance + an independently guarded exact mutation target.
    if e.approval_content_id and e.effect_content_precondition:
        return Classification.APPROVAL_AND_EXACT_INTENT

    # Exact mutable policy/state read-modify-write CAS.
    if e.mutation_state_token and e.mutation_precondition_same_token:
        return Classification.MUTABLE_POLICY_CAS

    # Authorization datastore revision: useful for causal/exact reads, not
    # proof that a later external side effect remains authorized.
    if e.auth_decision_revision and e.exact_snapshot_replay:
        return Classification.DECISION_REVISION_FENCE

    # Model/schema pin and "read current" consistency are not tuple-state epochs.
    if e.immutable_policy_model_id or e.stronger_read_consistency_only:
        return Classification.POLICY_MODEL_PIN_ONLY

    # Retry identity solves ambiguous execution without proving authorization.
    if e.idempotency_key_replay:
        return Classification.IDEMPOTENT_EFFECT_RETRY

    # Request/decision/policy IDs are audit provenance unless the provider
    # documents them as an enforcement precondition.
    if e.provenance_id_only:
        return Classification.PROVENANCE_ONLY

    return Classification.UNPROVED


def self_test() -> None:
    fixtures = {
        "spicedb_zedtoken_is_not_external_effect_gate": (
            Evidence(auth_decision_revision=True, exact_snapshot_replay=True),
            Classification.DECISION_REVISION_FENCE,
        ),
        "synthetic_true_external_gate_requires_explicit_effect_precondition": (
            Evidence(
                auth_decision_revision=True,
                prior_auth_revision_effect_precondition=True,
            ),
            Classification.PRIOR_AUTH_REVISION_EFFECT_GATE,
        ),
        "openfga_model_plus_higher_consistency": (
            Evidence(
                immutable_policy_model_id=True,
                stronger_read_consistency_only=True,
            ),
            Classification.POLICY_MODEL_PIN_ONLY,
        ),
        "google_iam_etag": (
            Evidence(
                mutation_state_token="etag",
                mutation_precondition_same_token=True,
            ),
            Classification.MUTABLE_POLICY_CAS,
        ),
        "kubernetes_request_auth_resource_version": (
            Evidence(
                request_local_authorization=True,
                mutation_state_token="resourceVersion",
                mutation_precondition_same_token=True,
            ),
            Classification.REQUEST_LOCAL_AUTH_WITH_STATE_CAS,
        ),
        "github_review_and_merge_head": (
            Evidence(
                approval_content_id="commit_id",
                effect_content_precondition="sha",
            ),
            Classification.APPROVAL_AND_EXACT_INTENT,
        ),
        "stripe_idempotency": (
            Evidence(idempotency_key_replay=True),
            Classification.IDEMPOTENT_EFFECT_RETRY,
        ),
        "opa_decision_id": (
            Evidence(provenance_id_only=True),
            Classification.PROVENANCE_ONLY,
        ),
        "aws_verified_permissions_policy_ids_only": (
            Evidence(provenance_id_only=True),
            Classification.PROVENANCE_ONLY,
        ),
    }
    for name, (evidence, expected) in fixtures.items():
        got = classify(evidence)
        assert got == expected, (name, got, expected)
    print(f"PASS {len(fixtures)} fixtures")


if __name__ == "__main__":
    self_test()
