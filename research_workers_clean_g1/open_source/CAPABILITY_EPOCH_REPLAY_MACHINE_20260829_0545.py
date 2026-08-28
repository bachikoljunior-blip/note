"""Fail-closed replay model for checkpointed capability tokens.

The effect server owns current epoch state. A token is usable only when:
- current epoch can be read authoritatively,
- token epoch exactly matches current epoch,
- token resource and method constraints cover the requested effect,
- token is not expired,
- and the gate itself is configured fail-closed.

This is deliberately stricter than systems where an unforgeable issuer makes
future epochs impossible and a '< current' comparison is sufficient.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, FrozenSet


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY_STALE_EPOCH = "DENY_STALE_EPOCH"
    DENY_FUTURE_EPOCH = "DENY_FUTURE_EPOCH"
    DENY_SCOPE = "DENY_SCOPE"
    DENY_METHOD = "DENY_METHOD"
    DENY_EXPIRED = "DENY_EXPIRED"
    DENY_AUTH_STATE_UNAVAILABLE = "DENY_AUTH_STATE_UNAVAILABLE"
    DENY_FAIL_OPEN_CONFIGURATION = "DENY_FAIL_OPEN_CONFIGURATION"


@dataclass(frozen=True)
class CapabilityToken:
    epoch: int
    resource: str
    methods: FrozenSet[str]
    expires_at: Optional[int] = None


@dataclass(frozen=True)
class EffectRequest:
    resource: str
    method: str
    now: int


@dataclass(frozen=True)
class EpochAuthority:
    current_epoch: Optional[int]
    authoritative: bool
    fail_closed: bool


def decide(token: CapabilityToken, req: EffectRequest, auth: EpochAuthority) -> Decision:
    if not auth.fail_closed:
        return Decision.DENY_FAIL_OPEN_CONFIGURATION
    if not auth.authoritative or auth.current_epoch is None:
        return Decision.DENY_AUTH_STATE_UNAVAILABLE
    if token.epoch < auth.current_epoch:
        return Decision.DENY_STALE_EPOCH
    if token.epoch > auth.current_epoch:
        return Decision.DENY_FUTURE_EPOCH
    if token.expires_at is not None and req.now >= token.expires_at:
        return Decision.DENY_EXPIRED
    if token.resource != req.resource:
        return Decision.DENY_SCOPE
    if req.method not in token.methods:
        return Decision.DENY_METHOD
    return Decision.ALLOW


def self_test() -> None:
    base = CapabilityToken(epoch=7, resource="repo:acme/app", methods=frozenset({"read", "write"}), expires_at=200)
    req = EffectRequest(resource="repo:acme/app", method="write", now=100)

    fixtures = [
        ("current token", base, req, EpochAuthority(7, True, True), Decision.ALLOW),
        ("checkpoint replay after revoke", base, req, EpochAuthority(8, True, True), Decision.DENY_STALE_EPOCH),
        ("future epoch token", CapabilityToken(8, base.resource, base.methods, 200), req, EpochAuthority(7, True, True), Decision.DENY_FUTURE_EPOCH),
        ("fresh token after revoke", CapabilityToken(8, base.resource, base.methods, 200), req, EpochAuthority(8, True, True), Decision.ALLOW),
        ("fresh epoch wrong resource", CapabilityToken(8, "repo:other/app", base.methods, 200), req, EpochAuthority(8, True, True), Decision.DENY_SCOPE),
        ("fresh epoch wrong method", CapabilityToken(8, base.resource, frozenset({"read"}), 200), req, EpochAuthority(8, True, True), Decision.DENY_METHOD),
        ("expired token", CapabilityToken(8, base.resource, base.methods, 100), req, EpochAuthority(8, True, True), Decision.DENY_EXPIRED),
        ("epoch store unavailable", base, req, EpochAuthority(None, False, True), Decision.DENY_AUTH_STATE_UNAVAILABLE),
        ("stale local epoch copy not authoritative", base, req, EpochAuthority(7, False, True), Decision.DENY_AUTH_STATE_UNAVAILABLE),
        ("fail-open configuration rejected", base, req, EpochAuthority(None, False, False), Decision.DENY_FAIL_OPEN_CONFIGURATION),
    ]

    for name, token, request, authority, expected in fixtures:
        actual = decide(token, request, authority)
        assert actual == expected, (name, actual, expected)


if __name__ == "__main__":
    self_test()
    print("10 capability-epoch replay fixtures passed")
