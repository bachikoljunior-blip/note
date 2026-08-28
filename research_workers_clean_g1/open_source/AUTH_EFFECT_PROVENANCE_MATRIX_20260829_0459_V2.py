"""Fail-closed classifier for authorization provenance vs effect binding.

Phase-1 open_source artifact. It distinguishes:
- trace/policy identifiers from authorization-state freshness tokens,
- durable decision provenance from resource-coupled freshness fences,
- request-bound/effect-local enforcement from detached checks,
- resource-version CAS from authorization-version gating,
- and the still-unobserved case where an external effect API atomically rejects
  a stale authorization decision revision/epoch.
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
            in {TokenSemantics.AUTH_STATE_REVISION, TokenSemantics.AUTH_SNAPSHOT_FRESHNESS}
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


def classify(c: Capability) -> Verdict:
    """Classify conservatively; missing evidence never upgrades effect authority."""
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
    ):
        return Verdict.TRUE_EXTERNAL_REVISION_GATE

    if c.binding == Binding.EFFECT_LOCAL_ATOMIC_GATE:
        return Verdict.EFFECT_LOCAL_GATE

    if c.mutation and c.backend_mutation_returns_revision and not c.revision_exposed_to_agent:
        return Verdict.MUTATION_REVISION_ERASED

    if c.binding == Binding.REQUEST_BOUND_GATE and not exact_auth_revision:
        return Verdict.REQUEST_GATE_NO_DURABLE_REVISION

    if capsule is not None:
        if capsule.token_semantics == TokenSemantics.TRACE_ID:
            return Verdict.TRACE_PROVENANCE_ONLY
        if capsule.token_semantics == TokenSemantics.POLICY_VERSION:
            return Verdict.POLICY_VERSION_ONLY
        if capsule.token_semantics == TokenSemantics.RESOURCE_VERSION:
            return Verdict.RESOURCE_CAS_ONLY
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
        (
            "zed_dev_check",
            Capability(
                cap(TokenSemantics.AUTH_STATE_REVISION, source_system="authzed-zed-dev"),
                Binding.DETACHED_CHECK,
                production_target=False,
                revision_exposed_to_agent=True,
            ),
            Verdict.SANDBOX_REVISION_CHECK,
        ),
        (
            "authzed_reference_echo",
            Capability(None, Binding.REQUEST_BOUND_GATE, production_target=True),
            Verdict.REQUEST_GATE_NO_DURABLE_REVISION,
        ),
        (
            "zed_dev_relationship_write",
            Capability(
                None,
                Binding.DETACHED_CHECK,
                production_target=False,
                mutation=True,
                backend_mutation_returns_revision=True,
                revision_exposed_to_agent=False,
            ),
            Verdict.MUTATION_REVISION_ERASED,
        ),
        (
            "postgres_rls_update",
            Capability(
                None,
                Binding.EFFECT_LOCAL_ATOMIC_GATE,
                production_target=True,
                mutation=True,
            ),
            Verdict.EFFECT_LOCAL_GATE,
        ),
        (
            "postgres_bypassrls_scope_exception",
            Capability(
                None,
                Binding.EFFECT_LOCAL_ATOMIC_GATE,
                production_target=True,
                mutation=True,
                scope_exception=True,
            ),
            Verdict.UNPROVED,
        ),
        (
            "spicedb_check_then_external_write",
            Capability(
                cap(TokenSemantics.AUTH_STATE_REVISION, source_system="spicedb"),
                Binding.DETACHED_CHECK,
                production_target=True,
                revision_exposed_to_agent=True,
            ),
            Verdict.REVISION_PROVENANCE_ONLY,
        ),
        (
            "permify_snap_token_check_then_external_write",
            Capability(
                cap(
                    TokenSemantics.AUTH_SNAPSHOT_FRESHNESS,
                    source_system="permify",
                    consistency_mode="at_least_as_fresh_as_snap_token",
                ),
                Binding.DETACHED_CHECK,
                production_target=True,
                revision_exposed_to_agent=True,
            ),
            Verdict.CAUSAL_AUTH_FRESHNESS_ONLY,
        ),
        (
            "opa_decision_id",
            Capability(
                cap(TokenSemantics.TRACE_ID, source_system="opa"),
                Binding.DETACHED_CHECK,
                production_target=True,
                revision_exposed_to_agent=True,
            ),
            Verdict.TRACE_PROVENANCE_ONLY,
        ),
        (
            "opa_bundle_revision",
            Capability(
                cap(TokenSemantics.POLICY_VERSION, source_system="opa"),
                Binding.DETACHED_CHECK,
                production_target=True,
                revision_exposed_to_agent=True,
            ),
            Verdict.POLICY_VERSION_ONLY,
        ),
        (
            "openfga_authorization_model_id",
            Capability(
                cap(TokenSemantics.POLICY_VERSION, source_system="openfga"),
                Binding.DETACHED_CHECK,
                production_target=True,
                revision_exposed_to_agent=True,
            ),
            Verdict.POLICY_VERSION_ONLY,
        ),
        (
            "github_blob_sha_not_auth_revision",
            Capability(
                cap(TokenSemantics.RESOURCE_VERSION, source_system="github"),
                Binding.DETACHED_CHECK,
                production_target=True,
                revision_exposed_to_agent=True,
                effect_resource_cas=True,
            ),
            Verdict.RESOURCE_CAS_ONLY,
        ),
        (
            "envoy_ext_authz_request_gate",
            Capability(None, Binding.REQUEST_BOUND_GATE, production_target=True),
            Verdict.REQUEST_GATE_NO_DURABLE_REVISION,
        ),
        (
            "hypothetical_accepts_revision_but_does_not_reject_stale_atomically",
            Capability(
                cap(TokenSemantics.AUTH_STATE_REVISION),
                Binding.REQUEST_BOUND_GATE,
                production_target=True,
                mutation=True,
                revision_exposed_to_agent=True,
                external_effect_accepts_auth_revision=True,
                external_effect_rejects_stale_auth_revision_atomically=False,
            ),
            Verdict.REVISION_PROVENANCE_ONLY,
        ),
        (
            "hypothetical_true_external_revision_precondition",
            Capability(
                cap(TokenSemantics.AUTH_STATE_REVISION),
                Binding.REQUEST_BOUND_GATE,
                production_target=True,
                mutation=True,
                revision_exposed_to_agent=True,
                external_effect_accepts_auth_revision=True,
                external_effect_rejects_stale_auth_revision_atomically=True,
            ),
            Verdict.TRUE_EXTERNAL_REVISION_GATE,
        ),
        (
            "malformed_trace_capsule_missing_permission",
            Capability(
                ProvenanceCapsule(
                    decision="ALLOW",
                    subject="user:alice",
                    resource="doc:1",
                    permission="",
                    consistency_mode="n/a",
                    token="decision-123",
                    token_semantics=TokenSemantics.TRACE_ID,
                ),
                Binding.DETACHED_CHECK,
                production_target=True,
                revision_exposed_to_agent=True,
            ),
            Verdict.UNPROVED,
        ),
    ]

    for name, capability, expected in fixtures:
        actual = classify(capability)
        assert actual == expected, (name, actual, expected)

    assert cap(TokenSemantics.TRACE_ID).carries_auth_state_provenance() is False
    assert cap(TokenSemantics.POLICY_VERSION).carries_auth_state_provenance() is False
    assert cap(TokenSemantics.AUTH_SNAPSHOT_FRESHNESS).carries_exact_auth_revision() is False
    assert cap(TokenSemantics.AUTH_STATE_REVISION).carries_exact_auth_revision() is True


if __name__ == "__main__":
    self_test()
    print("15 fixtures passed; 4 provenance invariants passed")
