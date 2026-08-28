from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Classification(str, Enum):
    PRIOR_AUTH_REVISION_EFFECT_GATE = "PRIOR_AUTH_REVISION_EFFECT_GATE"
    AUTH_DECISION_CONTENT_EPOCH_BINDING = "AUTH_DECISION_CONTENT_EPOCH_BINDING"
    DECISION_REVISION_FENCE = "DECISION_REVISION_FENCE"
    POLICY_MODEL_PIN_ONLY = "POLICY_MODEL_PIN_ONLY"
    MUTABLE_POLICY_CAS = "MUTABLE_POLICY_CAS"
    REQUEST_LOCAL_AUTH_WITH_STATE_CAS = "REQUEST_LOCAL_AUTH_WITH_STATE_CAS"
    SAME_CONTENT_APPROVAL_EFFECT_CAS = "SAME_CONTENT_APPROVAL_EFFECT_CAS"
    IDEMPOTENT_EFFECT_RETRY = "IDEMPOTENT_EFFECT_RETRY"
    MATERIALIZED_REVISION_TXN_CHECKPOINT = "MATERIALIZED_REVISION_TXN_CHECKPOINT"
    PROVENANCE_ONLY = "PROVENANCE_ONLY"
    UNPROVED = "UNPROVED"


@dataclass(frozen=True)
class Evidence:
    auth_decision_revision: bool = False
    exact_snapshot_replay: bool = False
    prior_auth_revision_effect_precondition: bool = False
    content_stores_auth_revision: bool = False
    content_change_authorized_at_revision: bool = False
    immutable_policy_model_id: bool = False
    stronger_read_consistency_only: bool = False
    mutation_state_token: Optional[str] = None
    mutation_precondition_same_token: bool = False
    request_local_authorization: bool = False
    approval_content_id: Optional[str] = None
    effect_content_precondition: Optional[str] = None
    approval_precondition_same_content: bool = False
    idempotency_key_replay: bool = False
    materialized_data_cursor_revision_same_txn: bool = False
    provenance_id_only: bool = False


def classify(e: Evidence) -> Classification:
    if e.auth_decision_revision and e.prior_auth_revision_effect_precondition:
        return Classification.PRIOR_AUTH_REVISION_EFFECT_GATE

    # A client can causally bind newly written content to the authorization
    # snapshot used to authorize the content change without proving the content
    # storage effect endpoint consumes that revision as an atomic precondition.
    if (
        e.auth_decision_revision
        and e.content_stores_auth_revision
        and e.content_change_authorized_at_revision
    ):
        return Classification.AUTH_DECISION_CONTENT_EPOCH_BINDING

    # Strong collaboration form: approval itself and the eventual effect both
    # fail closed against the same evolving content identity.
    if (
        e.approval_precondition_same_content
        and e.approval_content_id
        and e.effect_content_precondition
        and e.approval_content_id == e.effect_content_precondition
    ):
        return Classification.SAME_CONTENT_APPROVAL_EFFECT_CAS

    if (
        e.request_local_authorization
        and e.mutation_state_token
        and e.mutation_precondition_same_token
    ):
        return Classification.REQUEST_LOCAL_AUTH_WITH_STATE_CAS

    # Durable stream/snapshot recovery class; not an authorization effect gate.
    if e.materialized_data_cursor_revision_same_txn:
        return Classification.MATERIALIZED_REVISION_TXN_CHECKPOINT

    if e.mutation_state_token and e.mutation_precondition_same_token:
        return Classification.MUTABLE_POLICY_CAS

    if e.auth_decision_revision and e.exact_snapshot_replay:
        return Classification.DECISION_REVISION_FENCE

    if e.immutable_policy_model_id or e.stronger_read_consistency_only:
        return Classification.POLICY_MODEL_PIN_ONLY

    if e.idempotency_key_replay:
        return Classification.IDEMPOTENT_EFFECT_RETRY

    if e.provenance_id_only:
        return Classification.PROVENANCE_ONLY

    return Classification.UNPROVED


def self_test() -> None:
    fixtures = {
        "spicedb_zedtoken": (
            Evidence(auth_decision_revision=True, exact_snapshot_replay=True),
            Classification.DECISION_REVISION_FENCE,
        ),
        "synthetic_true_external_gate": (
            Evidence(
                auth_decision_revision=True,
                prior_auth_revision_effect_precondition=True,
            ),
            Classification.PRIOR_AUTH_REVISION_EFFECT_GATE,
        ),
        "zanzibar_content_change_binding": (
            Evidence(
                auth_decision_revision=True,
                content_stores_auth_revision=True,
                content_change_authorized_at_revision=True,
            ),
            Classification.AUTH_DECISION_CONTENT_EPOCH_BINDING,
        ),
        "authzed_materialize_txn_checkpoint": (
            Evidence(materialized_data_cursor_revision_same_txn=True),
            Classification.MATERIALIZED_REVISION_TXN_CHECKPOINT,
        ),
        "gitlab_head_bound_approval_and_merge": (
            Evidence(
                approval_content_id="head_sha",
                effect_content_precondition="head_sha",
                approval_precondition_same_content=True,
            ),
            Classification.SAME_CONTENT_APPROVAL_EFFECT_CAS,
        ),
        "different_approval_and_effect_ids_are_not_same_content_cas": (
            Evidence(
                approval_content_id="review_commit_id",
                effect_content_precondition="current_head_sha",
            ),
            Classification.UNPROVED,
        ),
        "kubernetes_request_auth_resource_version": (
            Evidence(
                request_local_authorization=True,
                mutation_state_token="resourceVersion",
                mutation_precondition_same_token=True,
            ),
            Classification.REQUEST_LOCAL_AUTH_WITH_STATE_CAS,
        ),
        "google_iam_etag": (
            Evidence(
                mutation_state_token="etag",
                mutation_precondition_same_token=True,
            ),
            Classification.MUTABLE_POLICY_CAS,
        ),
        "openfga_model_plus_higher_consistency": (
            Evidence(
                immutable_policy_model_id=True,
                stronger_read_consistency_only=True,
            ),
            Classification.POLICY_MODEL_PIN_ONLY,
        ),
        "stripe_idempotency": (
            Evidence(idempotency_key_replay=True),
            Classification.IDEMPOTENT_EFFECT_RETRY,
        ),
        "opa_or_policy_id_provenance": (
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
