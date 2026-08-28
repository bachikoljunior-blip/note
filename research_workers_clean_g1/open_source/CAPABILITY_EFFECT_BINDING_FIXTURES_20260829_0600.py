"""Source-shaped fixtures for detached capability verification vs effect-bound verification.

This models a contract shape observed in ShiftLock v0.11.0:
- the capability authority has exact epoch verification and revocation;
- some effect managers receive only a capability/auth identifier after the caller
  is expected to verify separately.

The fixture demonstrates why a strong credential verifier does not automatically
make a later ID-only effect call revocation-safe.
"""

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Token:
    token_id: str
    epoch: int
    permission: str
    resource: str


class Result(str, Enum):
    COMMITTED = "COMMITTED"
    DENIED = "DENIED"


class Authority:
    def __init__(self) -> None:
        self.epoch = 0
        self.revoked: set[str] = set()

    def verify(self, token: Token, permission: str, resource: str) -> bool:
        return (
            token.token_id not in self.revoked
            and token.epoch == self.epoch
            and token.permission == permission
            and token.resource == resource
        )

    def advance_epoch(self) -> None:
        self.epoch += 1

    def revoke(self, token_id: str) -> None:
        self.revoked.add(token_id)


class DetachedIdOnlyManager:
    """Effect manager that treats a non-empty auth identifier as caller evidence."""

    def commit(self, auth_id: str) -> Result:
        return Result.COMMITTED if auth_id else Result.DENIED


class EffectBoundManager:
    """Effect manager that verifies current authority immediately at the boundary."""

    def __init__(self, authority: Authority) -> None:
        self.authority = authority

    def commit(self, token: Token, permission: str, resource: str) -> Result:
        if not self.authority.verify(token, permission, resource):
            return Result.DENIED
        # In a real system the verify+effect reachability must share one trusted
        # serialization/transaction boundary or an equivalent fail-closed gate.
        return Result.COMMITTED


def self_test() -> None:
    auth = Authority()
    token = Token("cap_1", 0, "maintenance.enter", "service:payments")
    detached = DetachedIdOnlyManager()
    bound = EffectBoundManager(auth)

    # Baseline: both paths can proceed while authority is current.
    assert auth.verify(token, token.permission, token.resource)
    assert detached.commit(token.token_id) == Result.COMMITTED
    assert bound.commit(token, token.permission, token.resource) == Result.COMMITTED

    # TOCTOU: caller verifies, then a global/security epoch advances before effect.
    assert auth.verify(token, token.permission, token.resource)
    auth.advance_epoch()
    assert not auth.verify(token, token.permission, token.resource)
    assert detached.commit(token.token_id) == Result.COMMITTED
    assert bound.commit(token, token.permission, token.resource) == Result.DENIED

    # Per-token revocation has the same detached-ID failure shape.
    fresh = Token("cap_2", 1, "lockdown.unlock", "service:payments")
    assert auth.verify(fresh, fresh.permission, fresh.resource)
    auth.revoke(fresh.token_id)
    assert not auth.verify(fresh, fresh.permission, fresh.resource)
    assert detached.commit(fresh.token_id) == Result.COMMITTED
    assert bound.commit(fresh, fresh.permission, fresh.resource) == Result.DENIED

    # A non-empty opaque string is not proof that strong auth was verified.
    assert detached.commit("forged-nonempty-auth-id") == Result.COMMITTED


if __name__ == "__main__":
    self_test()
    print("detached-vs-bound capability fixtures passed")
