from dataclasses import dataclass


@dataclass(frozen=True)
class Case:
    name: str
    client_key_before_effect: bool = False
    correlation_id_only: bool = False
    preflight_state_received_before_effect: bool = False
    key_integrity_bound: bool = False
    atomic_create_or_get: bool = False
    exact_readback: bool = False
    version_cas: bool = False
    external_executor: bool = False
    active_intent_marker: bool = False
    stale_head: bool = False
    branching_supported: bool = False
    unique_descendant_only: bool = False


def classify(c: Case) -> str:
    if c.correlation_id_only:
        return "UNSAFE_CORRELATION_ONLY"
    if c.stale_head:
        if c.active_intent_marker and c.exact_readback:
            return "FENCED_COMMIT_RECOVERABLE"
        if c.unique_descendant_only and c.branching_supported:
            return "PARTIAL_BRANCH_INTENT"
        return "ACTIVE_HEAD_AMBIGUITY"
    if c.preflight_state_received_before_effect:
        if c.key_integrity_bound and c.atomic_create_or_get and c.exact_readback:
            return "IDEMPOTENT_CREATE_RECOVERABLE"
        return "PARTIAL_PREFLIGHT"
    if c.client_key_before_effect:
        if c.atomic_create_or_get and c.exact_readback:
            if c.external_executor:
                return "EXTERNAL_EXECUTOR_RECOVERABLE_CREATE"
            return "IDEMPOTENT_CREATE_RECOVERABLE"
        return "PARTIAL_CLIENT_KEY"
    return "PRE_HANDLE_AMBIGUITY"


FIXTURES = [
    (Case("MCP stock task direct"), "PRE_HANDLE_AMBIGUITY"),
    (Case("JSON-RPC request id", correlation_id_only=True), "UNSAFE_CORRELATION_ONLY"),
    (
        Case(
            "MCP MRTR preflight no keyed store",
            preflight_state_received_before_effect=True,
            key_integrity_bound=True,
        ),
        "PARTIAL_PREFLIGHT",
    ),
    (
        Case(
            "MCP MRTR preflight keyed store",
            preflight_state_received_before_effect=True,
            key_integrity_bound=True,
            atomic_create_or_get=True,
            exact_readback=True,
        ),
        "IDEMPOTENT_CREATE_RECOVERABLE",
    ),
    (
        Case(
            "Kubernetes deterministic name",
            client_key_before_effect=True,
            atomic_create_or_get=True,
            exact_readback=True,
            version_cas=True,
        ),
        "IDEMPOTENT_CREATE_RECOVERABLE",
    ),
    (Case("Kubernetes generateName"), "PRE_HANDLE_AMBIGUITY"),
    (
        Case(
            "Temporal stable WorkflowId USE_EXISTING",
            client_key_before_effect=True,
            atomic_create_or_get=True,
            exact_readback=True,
            external_executor=True,
        ),
        "EXTERNAL_EXECUTOR_RECOVERABLE_CREATE",
    ),
    (Case("OpenHands stale head no marker", stale_head=True), "ACTIVE_HEAD_AMBIGUITY"),
    (
        Case(
            "OpenHands valid commit marker",
            stale_head=True,
            active_intent_marker=True,
            exact_readback=True,
        ),
        "FENCED_COMMIT_RECOVERABLE",
    ),
    (
        Case(
            "OpenHands unique descendant with branching",
            stale_head=True,
            unique_descendant_only=True,
            branching_supported=True,
        ),
        "PARTIAL_BRANCH_INTENT",
    ),
]


def self_test() -> None:
    failures = []
    for case, expected in FIXTURES:
        actual = classify(case)
        if actual != expected:
            failures.append((case.name, expected, actual))
    if failures:
        raise AssertionError(failures)
    print(f"{len(FIXTURES)}/{len(FIXTURES)} fixtures passed")


if __name__ == "__main__":
    self_test()
