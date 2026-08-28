"""Fail-closed classifier for authorization provenance vs effect binding.

Phase-1 open_source artifact. This intentionally distinguishes:
- durable authorization revision provenance,
- request-bound authorization checks,
- effect-local policy gates,
- and the still-unobserved case where an external effect API atomically
  accepts an authorization decision revision as a mutation precondition.
"""

from dataclasses import dataclass
from enum import Enum


class Provenance(str, Enum):
    NONE = "NONE"
    OBSERVATION_ONLY = "OBSERVATION_ONLY"
    REVISION_TOKEN = "REVISION_TOKEN"
    WRITE_REVISION = "WRITE_REVISION"


class Binding(str, Enum):
    DETACHED_CHECK = "DETACHED_CHECK"
    REQUEST_BOUND_GATE = "REQUEST_BOUND_GATE"
    EFFECT_LOCAL_ATOMIC_GATE = "EFFECT_LOCAL_ATOMIC_GATE"


class Verdict(str, Enum):
    REVISION_PROVENANCE_ONLY = "REVISION_PROVENANCE_ONLY"
    REQUEST_GATE_NO_DURABLE_REVISION = "REQUEST_GATE_NO_DURABLE_REVISION"
    EFFECT_LOCAL_GATE = "EFFECT_LOCAL_GATE"
    MUTATION_REVISION_ERASED = "MUTATION_REVISION_ERASED"
    SANDBOX_REVISION_CHECK = "SANDBOX_REVISION_CHECK"
    TRUE_EXTERNAL_REVISION_GATE = "TRUE_EXTERNAL_REVISION_GATE"
    UNPROVED = "UNPROVED"


@dataclass(frozen=True)
class Capability:
    provenance: Provenance
    binding: Binding
    production_target: bool
    mutation: bool = False
    external_effect_accepts_auth_revision: bool = False
    revision_exposed_to_agent: bool = False
    scope_exception: bool = False


def classify(c: Capability) -> Verdict:
    """Classify conservatively; missing evidence never upgrades effect authority."""
    if c.scope_exception:
        return Verdict.UNPROVED

    if c.external_effect_accepts_auth_revision and c.revision_exposed_to_agent:
        return Verdict.TRUE_EXTERNAL_REVISION_GATE

    if c.binding == Binding.EFFECT_LOCAL_ATOMIC_GATE:
        return Verdict.EFFECT_LOCAL_GATE

    if c.mutation and c.provenance == Provenance.NONE:
        return Verdict.MUTATION_REVISION_ERASED

    if c.binding == Binding.REQUEST_BOUND_GATE and not c.revision_exposed_to_agent:
        return Verdict.REQUEST_GATE_NO_DURABLE_REVISION

    if c.provenance == Provenance.REVISION_TOKEN and c.revision_exposed_to_agent:
        if not c.production_target:
            return Verdict.SANDBOX_REVISION_CHECK
        return Verdict.REVISION_PROVENANCE_ONLY

    return Verdict.UNPROVED


def self_test() -> None:
    fixtures = [
        (
            "zed_dev_check",
            Capability(
                Provenance.REVISION_TOKEN,
                Binding.DETACHED_CHECK,
                production_target=False,
                revision_exposed_to_agent=True,
            ),
            Verdict.SANDBOX_REVISION_CHECK,
        ),
        (
            "authzed_reference_echo",
            Capability(
                Provenance.NONE,
                Binding.REQUEST_BOUND_GATE,
                production_target=True,
                revision_exposed_to_agent=False,
            ),
            Verdict.REQUEST_GATE_NO_DURABLE_REVISION,
        ),
        (
            "zed_dev_relationship_write",
            Capability(
                Provenance.NONE,
                Binding.DETACHED_CHECK,
                production_target=False,
                mutation=True,
                revision_exposed_to_agent=False,
            ),
            Verdict.MUTATION_REVISION_ERASED,
        ),
        (
            "postgres_rls_update",
            Capability(
                Provenance.NONE,
                Binding.EFFECT_LOCAL_ATOMIC_GATE,
                production_target=True,
                mutation=True,
            ),
            Verdict.EFFECT_LOCAL_GATE,
        ),
        (
            "postgres_bypassrls_scope_exception",
            Capability(
                Provenance.NONE,
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
                Provenance.REVISION_TOKEN,
                Binding.DETACHED_CHECK,
                production_target=True,
                revision_exposed_to_agent=True,
            ),
            Verdict.REVISION_PROVENANCE_ONLY,
        ),
        (
            "hypothetical_external_revision_precondition",
            Capability(
                Provenance.REVISION_TOKEN,
                Binding.REQUEST_BOUND_GATE,
                production_target=True,
                mutation=True,
                external_effect_accepts_auth_revision=True,
                revision_exposed_to_agent=True,
            ),
            Verdict.TRUE_EXTERNAL_REVISION_GATE,
        ),
    ]

    for name, capability, expected in fixtures:
        actual = classify(capability)
        assert actual == expected, (name, actual, expected)


if __name__ == "__main__":
    self_test()
    print("7 fixtures passed")
