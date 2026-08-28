"""Fail-closed classifier for authorization provenance, capability revocation, and effect binding.

Phase-1 open_source artifact V3. It distinguishes:
- trace/policy identifiers from authorization-state revisions,
- resource versions from authorization versions,
- bearer/sender-constrained capability validity from revocation-aware enforcement,
- revocation identifiers whose distribution freshness is unproved,
- request-bound revocation checks from effect-side epoch gates,
- and the still-unobserved cross-system case where an external effect atomically
  accepts and rejects a stale prior authorization decision revision.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TokenSemantics(str, Enum):
    NONE = "NONE"
    TRACE_ID = "TRACE_ID"
    POLICY_VERSION = "POLICY_VERSION"
    AUTH_STATE_REVISION = "AUTH_STATE_REVISION"
    AUTH_SNAPSHOT_FRESHNESS = "AUTH_SNAPSHOT_FRESHNESS"
    WRITE_REVISION = "WRITE_REVISION"
    RESOURCE_VERSION = "RESOURCE_VERSION"
    CAPABILITY_TOKEN = "CAPABILITY_TOKEN"
    REVOCATION_ID = "REVOCATION_ID"
    REVOCATION_EPOCH = "REVOCATION_EPOCH"
    PROOF_OF_POSSESSION = "PROOF_OF_POSSESSION"


class Binding(str, Enum):
    DETACHED_CHECK = "DETACHED_CHECK"
    REQUEST_BOUND_GATE = "REQUEST_BOUND_GATE"
    EFFECT_LOCAL_ATOMIC_GATE = "EFFECT_LOCAL_ATOMIC_GATE"


class Verdict(str, Enum):
    TRACE_PROVENANCE_ONLY = "TRACE_PROVENANCE_ONLY"
    POLICY_VERSION_ONLY = "POLICY_VERSION_ONLY"
    RESOURCE_CAS_ONLY = "RESOURCE_CAS_ONLY"
    REVISION_PROVENANCE_ONLY = "REVISION_PROVENANCE_ONLY"
    CAUSAL_AUTH_FRESHNESS_ONLY = "CAUSAL_AUTH_FRESHNESS_ONLY"
    REQUEST_GATE_NO_DURABLE_REVISION = "REQUEST_GATE_NO_DURABLE_REVISION"
    EFFECT_LOCAL_GATE = "EFFECT_LOCAL_GATE"
    MUTATION_REVISION_ERASED = "MUTATION_REVISION_ERASED"
    SANDBOX_REVISION_CHECK = "SANDBOX_REVISION_CHECK"
    TRUE_EXTERNAL_REVISION_GATE = "TRUE_EXTERNAL_REVISION_GATE"
    BEARER_CAPABILITY_ONLY = "BEARER_CAPABILITY_ONLY"
    PROOF_OF_POSSESSION_ONLY = "PROOF_OF_POSSESSION_ONLY"
    REVOCATION_STATE_FRESHNESS_UNPROVED = "REVOCATION_STATE_FRESHNESS_UNPROVED"
    REVOCATION_AWARE_REQUEST_GATE = "REVOCATION_AWARE_REQUEST_GATE"
    REVOCATION_GATE_FAIL_OPEN = "REVOCATION_GATE_FAIL_OPEN"
    EFFECT_SIDE_REVOCATION_EPOCH_GATE = "EFFECT_SIDE_REVOCATION_EPOCH_GATE"
    UNPROVED = "UNPROVED"


@dataclass(frozen=True)
class ProvenanceCapsule:
    decision: str
    subject: str
    resource: str
    permission: str
    consistency_mode: str
    token: str = ""
    token_semantics: TokenSemantics = TokenSemantics.NONE
    source_system: str = ""

    def structural_errors(self) -> tuple[str, ...]:
        errors = []
        if self.decision not in {"ALLOW", "DENY"}:
            errors.append("decision")
        if not self.subject:
            errors.append("subject")
        if not self.resource:
            errors.append("resource")
        if not self.permission:
            errors.append("permission")
        if not self.consistency_mode:
            errors.append("consistency_mode")
        if self.token_semantics != TokenSemantics.NONE and not self.token:
            errors.append("token")
        return tuple(errors)

    def carries_auth_state_provenance(self) -> bool:
        return (
            not self.structural_errors()
            and self.token_semantics
            in {
                TokenSemantics.AUTH_STATE_REVISION,
                TokenSemantics.AUTH_SNAPSHOT_FRESHNESS,
                TokenSemantics.REVOCATION_EPOCH,
            }
        )

    def carries_exact_auth_revision(self) -> bool:
        return (
            not self.structural_errors()
            and self.token_semantics == TokenSemantics.AUTH_STATE_REVISION
        )


@dataclass(frozen=True)
class Capability:
    capsule: Optional[ProvenanceCapsule]
    binding: Binding
    production_target: bool
    mutation: bool = False
    backend_mutation_returns_revision: bool = False
    revision_exposed_to_agent: bool = False
    external_effect_accepts_auth_revision: bool = False
    external_effect_rejects_stale_auth_revision_atomically: bool = False
    effect_resource_cas: bool = False
    scope_exception: bool = False

    # Capability/revocation-specific evidence.
    revocation_state_checked_at_effect: bool = False
    revocation_state_authoritative_or_fresh: bool = False
    revocation_check_fail_closed: bool = True
    effect_compares_current_revocation_epoch: bool = False


def classify(c: Capability) -> Verdict:
    """Classify conservatively; version-looking values never upgrade authority by name."""
    if c.scope_exception:
        return Verdict.UNPROVED

    capsule = c.capsule
    if capsule is not None and capsule.structural_errors():
        return Verdict.UNPROVED

    exact_auth_revision = (
        capsule is not None
        and capsule.carries_exact_auth_revision()
        and c.revision_exposed_to_agent
    )

    if (
        exact_auth_revision
        and c.external_effect_accepts_auth_revision
        and c.external_effect_rejects_stale_auth_revision_atomically
        and c.revocation_check_fail_closed
    ):
        return Verdict.TRUE_EXTERNAL_REVISION_GATE

    # Strong same-authority analogue: token carries an epoch and the effect-serving
    # authority compares it against current state before the effect handler runs.
    if (
        capsule is not None
        and capsule.token_semantics == TokenSemantics.REVOCATION_EPOCH
        and c.binding == Binding.EFFECT_LOCAL_ATOMIC_GATE
        and c.effect_compares_current_revocation_epoch
        and c.revocation_check_fail_closed
    ):
        return Verdict.EFFECT_SIDE_REVOCATION_EPOCH_GATE

    if c.binding == Binding.EFFECT_LOCAL_ATOMIC_GATE:
        return Verdict.EFFECT_LOCAL_GATE

    if c.mutation and c.backend_mutation_returns_revision and not c.revision_exposed_to_agent:
        return Verdict.MUTATION_REVISION_ERASED

    if capsule is not None and capsule.token_semantics == TokenSemantics.PROOF_OF_POSSESSION:
        return Verdict.PROOF_OF_POSSESSION_ONLY

    # A revocation lookup that can fail open is not a fail-closed revocation gate.
    if c.revocation_state_checked_at_effect and not c.revocation_check_fail_closed:
        return Verdict.REVOCATION_GATE_FAIL_OPEN

    if c.revocation_state_checked_at_effect:
        if c.revocation_state_authoritative_or_fresh:
            return Verdict.REVOCATION_AWARE_REQUEST_GATE
        return Verdict.REVOCATION_STATE_FRESHNESS_UNPROVED

    if c.binding == Binding.REQUEST_BOUND_GATE and not exact_auth_revision:
        if capsule is not None and capsule.token_semantics == TokenSemantics.CAPABILITY_TOKEN:
            return Verdict.BEARER_CAPABILITY_ONLY
        return Verdict.REQUEST_GATE_NO_DURABLE_REVISION

    if capsule is not None:
        if capsule.token_semantics == TokenSemantics.TRACE_ID:
            return Verdict.TRACE_PROVENANCE_ONLY
        if capsule.token_semantics == TokenSemantics.POLICY_VERSION:
            return Verdict.POLICY_VERSION_ONLY
        if capsule.token_semantics == TokenSemantics.RESOURCE_VERSION:
            return Verdict.RESOURCE_CAS_ONLY
        if capsule.token_semantics == TokenSemantics.CAPABILITY_TOKEN:
            return Verdict.BEARER_CAPABILITY_ONLY
        if capsule.token_semantics == TokenSemantics.REVOCATION_ID:
            return Verdict.REVOCATION_STATE_FRESHNESS_UNPROVED
        if (
            capsule.token_semantics == TokenSemantics.AUTH_SNAPSHOT_FRESHNESS
            and c.revision_exposed_to_agent
        ):
            return Verdict.CAUSAL_AUTH_FRESHNESS_ONLY
        if exact_auth_revision:
            if not c.production_target:
                return Verdict.SANDBOX_REVISION_CHECK
            return Verdict.REVISION_PROVENANCE_ONLY

    if c.effect_resource_cas:
        return Verdict.RESOURCE_CAS_ONLY

    return Verdict.UNPROVED


def cap(
    token_semantics: TokenSemantics,
    *,
    token: str = "t",
    decision: str = "ALLOW",
    consistency_mode: str = "documented",
    source_system: str = "fixture",
) -> ProvenanceCapsule:
    return ProvenanceCapsule(
        decision=decision,
        subject="user:alice",
        resource="doc:1",
        permission="edit",
        consistency_mode=consistency_mode,
        token=token if token_semantics != TokenSemantics.NONE else "",
        token_semantics=token_semantics,
        source_system=source_system,
    )


def self_test() -> None:
    fixtures = [
        ("zed_dev_check", Capability(cap(TokenSemantics.AUTH_STATE_REVISION, source_system="authzed-zed-dev"), Binding.DETACHED_CHECK, production_target=False, revision_exposed_to_agent=True), Verdict.SANDBOX_REVISION_CHECK),
        ("authzed_reference_echo", Capability(None, Binding.REQUEST_BOUND_GATE, production_target=True), Verdict.REQUEST_GATE_NO_DURABLE_REVISION),
        ("zed_dev_relationship_write", Capability(None, Binding.DETACHED_CHECK, production_target=False, mutation=True, backend_mutation_returns_revision=True, revision_exposed_to_agent=False), Verdict.MUTATION_REVISION_ERASED),
        ("postgres_rls_update", Capability(None, Binding.EFFECT_LOCAL_ATOMIC_GATE, production_target=True, mutation=True), Verdict.EFFECT_LOCAL_GATE),
        ("postgres_bypassrls_scope_exception", Capability(None, Binding.EFFECT_LOCAL_ATOMIC_GATE, production_target=True, mutation=True, scope_exception=True), Verdict.UNPROVED),
        ("spicedb_check_then_external_write", Capability(cap(TokenSemantics.AUTH_STATE_REVISION, source_system="spicedb"), Binding.DETACHED_CHECK, production_target=True, revision_exposed_to_agent=True), Verdict.REVISION_PROVENANCE_ONLY),
        ("permify_snap_token_check_then_external_write", Capability(cap(TokenSemantics.AUTH_SNAPSHOT_FRESHNESS, source_system="permify", consistency_mode="at_least_as_fresh_as_snap_token"), Binding.DETACHED_CHECK, production_target=True, revision_exposed_to_agent=True), Verdict.CAUSAL_AUTH_FRESHNESS_ONLY),
        ("opa_decision_id", Capability(cap(TokenSemantics.TRACE_ID, source_system="opa"), Binding.DETACHED_CHECK, production_target=True, revision_exposed_to_agent=True), Verdict.TRACE_PROVENANCE_ONLY),
        ("opa_bundle_revision", Capability(cap(TokenSemantics.POLICY_VERSION, source_system="opa"), Binding.DETACHED_CHECK, production_target=True, revision_exposed_to_agent=True), Verdict.POLICY_VERSION_ONLY),
        ("openfga_authorization_model_id", Capability(cap(TokenSemantics.POLICY_VERSION, source_system="openfga"), Binding.DETACHED_CHECK, production_target=True, revision_exposed_to_agent=True), Verdict.POLICY_VERSION_ONLY),
        ("github_blob_sha_not_auth_revision", Capability(cap(TokenSemantics.RESOURCE_VERSION, source_system="github"), Binding.DETACHED_CHECK, production_target=True, revision_exposed_to_agent=True, effect_resource_cas=True), Verdict.RESOURCE_CAS_ONLY),
        ("oauth_bearer_signature_and_expiry_only", Capability(cap(TokenSemantics.CAPABILITY_TOKEN, source_system="oauth"), Binding.REQUEST_BOUND_GATE, production_target=True, revision_exposed_to_agent=True), Verdict.BEARER_CAPABILITY_ONLY),
        ("oauth_rfc7662_introspection_no_cache_fail_closed", Capability(cap(TokenSemantics.CAPABILITY_TOKEN, source_system="oauth-rfc7662"), Binding.REQUEST_BOUND_GATE, production_target=True, revision_exposed_to_agent=True, revocation_state_checked_at_effect=True, revocation_state_authoritative_or_fresh=True, revocation_check_fail_closed=True), Verdict.REVOCATION_AWARE_REQUEST_GATE),
        ("oauth_introspection_cached_revocation_window", Capability(cap(TokenSemantics.CAPABILITY_TOKEN, source_system="oauth-rfc7662"), Binding.REQUEST_BOUND_GATE, production_target=True, revision_exposed_to_agent=True, revocation_state_checked_at_effect=True, revocation_state_authoritative_or_fresh=False, revocation_check_fail_closed=True), Verdict.REVOCATION_STATE_FRESHNESS_UNPROVED),
        ("dpop_sender_constraint", Capability(cap(TokenSemantics.PROOF_OF_POSSESSION, source_system="rfc9449"), Binding.REQUEST_BOUND_GATE, production_target=True, revision_exposed_to_agent=True), Verdict.PROOF_OF_POSSESSION_ONLY),
        ("biscuit_revocation_id_with_distributed_list_freshness_unproved", Capability(cap(TokenSemantics.REVOCATION_ID, source_system="biscuit"), Binding.REQUEST_BOUND_GATE, production_target=True, revision_exposed_to_agent=True, revocation_state_checked_at_effect=True, revocation_state_authoritative_or_fresh=False, revocation_check_fail_closed=True), Verdict.REVOCATION_STATE_FRESHNESS_UNPROVED),
        ("contextforge_jti_db_revocation_check_fail_open_on_lookup_error", Capability(cap(TokenSemantics.REVOCATION_ID, source_system="ibm-contextforge"), Binding.REQUEST_BOUND_GATE, production_target=True, revision_exposed_to_agent=True, revocation_state_checked_at_effect=True, revocation_state_authoritative_or_fresh=True, revocation_check_fail_closed=False), Verdict.REVOCATION_GATE_FAIL_OPEN),
        ("nonos_syscall_effect_side_epoch", Capability(cap(TokenSemantics.REVOCATION_EPOCH, source_system="nonos"), Binding.EFFECT_LOCAL_ATOMIC_GATE, production_target=True, mutation=True, revision_exposed_to_agent=True, effect_compares_current_revocation_epoch=True, revocation_check_fail_closed=True), Verdict.EFFECT_SIDE_REVOCATION_EPOCH_GATE),
        ("macaroon_third_party_caveat_without_revocation_epoch", Capability(cap(TokenSemantics.CAPABILITY_TOKEN, source_system="macaroon"), Binding.REQUEST_BOUND_GATE, production_target=True, revision_exposed_to_agent=True), Verdict.BEARER_CAPABILITY_ONLY),
        ("hypothetical_accepts_revision_but_does_not_reject_stale_atomically", Capability(cap(TokenSemantics.AUTH_STATE_REVISION), Binding.REQUEST_BOUND_GATE, production_target=True, mutation=True, revision_exposed_to_agent=True, external_effect_accepts_auth_revision=True, external_effect_rejects_stale_auth_revision_atomically=False), Verdict.REVISION_PROVENANCE_ONLY),
        ("hypothetical_true_external_revision_precondition", Capability(cap(TokenSemantics.AUTH_STATE_REVISION), Binding.REQUEST_BOUND_GATE, production_target=True, mutation=True, revision_exposed_to_agent=True, external_effect_accepts_auth_revision=True, external_effect_rejects_stale_auth_revision_atomically=True, revocation_check_fail_closed=True), Verdict.TRUE_EXTERNAL_REVISION_GATE),
        ("malformed_trace_capsule_missing_permission", Capability(ProvenanceCapsule(decision="ALLOW", subject="user:alice", resource="doc:1", permission="", consistency_mode="n/a", token="decision-123", token_semantics=TokenSemantics.TRACE_ID), Binding.DETACHED_CHECK, production_target=True, revision_exposed_to_agent=True), Verdict.UNPROVED),
    ]

    for name, capability, expected in fixtures:
        actual = classify(capability)
        assert actual == expected, (name, actual, expected)

    assert cap(TokenSemantics.TRACE_ID).carries_auth_state_provenance() is False
    assert cap(TokenSemantics.POLICY_VERSION).carries_auth_state_provenance() is False
    assert cap(TokenSemantics.RESOURCE_VERSION).carries_auth_state_provenance() is False
    assert cap(TokenSemantics.PROOF_OF_POSSESSION).carries_auth_state_provenance() is False
    assert cap(TokenSemantics.AUTH_SNAPSHOT_FRESHNESS).carries_exact_auth_revision() is False
    assert cap(TokenSemantics.REVOCATION_EPOCH).carries_exact_auth_revision() is False
    assert cap(TokenSemantics.AUTH_STATE_REVISION).carries_exact_auth_revision() is True


if __name__ == "__main__":
    self_test()
    print("22 fixtures passed; 7 provenance invariants passed")
