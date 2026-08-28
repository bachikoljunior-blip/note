"""Forward-only deterministic replay authorization facade.

This module wraps the historical durable attempt reservation ledger without
changing its FAIL_CLOSED wire behavior. DETERMINISTIC_REPLAY is authorized only
when a pre-score determinism contract is trusted and bound into the historical
RESERVE event through the request_binding_digest/attempt_id.

Historical deterministic-replay reservations that predate this facade are not
reinterpreted as authorized: recovery through this facade requires the exact
pre-score contract that was bound before reservation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha1, sha256
import json
import re
from types import MappingProxyType
from typing import Any, Iterable, Mapping

SCHEMA_VERSION = 1
AUTH_NAMESPACE = "__evaluation_deterministic_replay_authorization_v1__"
ATTEMPT_LEDGER_FILENAME = "durable_attempt_reservation_ledger_2026-08-28.py"
ATTEMPT_LEDGER_BLOB = "f51cc37e5897d8dc0f395da95c1f6dd1c12da791"
_ALLOWED_EQUALITY_LEVELS = frozenset({
    "raw_output",
    "token_ids",
    "score",
    "paired_score_bits",
    "oriented_discordance_sign",
    "custom_digest",
})
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ReplayAuthorizationError(RuntimeError):
    pass


def _canon(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _digest_obj(obj: Any) -> str:
    return sha256(_canon(obj)).hexdigest()


def _require_hex64(name: str, value: str) -> str:
    value = str(value)
    if not _HEX64.fullmatch(value):
        raise ReplayAuthorizationError(f"{name} must be lowercase sha256 hex")
    return value


def _require_nonempty(name: str, value: str) -> str:
    value = str(value)
    if not value:
        raise ReplayAuthorizationError(f"{name} must be nonempty")
    return value


@dataclass(frozen=True)
class RuntimeDeterminismSnapshot:
    runtime_fingerprint_digest: str
    scorer_config_digest: str
    decoder_config_digest: str
    protected_statistic: str
    attempt_id_version: str

    def validated(self) -> "RuntimeDeterminismSnapshot":
        _require_hex64("runtime_fingerprint_digest", self.runtime_fingerprint_digest)
        _require_hex64("scorer_config_digest", self.scorer_config_digest)
        _require_hex64("decoder_config_digest", self.decoder_config_digest)
        if self.protected_statistic not in _ALLOWED_EQUALITY_LEVELS:
            raise ReplayAuthorizationError("unsupported protected_statistic")
        _require_nonempty("attempt_id_version", self.attempt_id_version)
        return self

    def payload(self) -> dict[str, Any]:
        self.validated()
        return asdict(self)


@dataclass(frozen=True)
class DeterminismReplayContract:
    schema_version: int
    runtime_fingerprint_digest: str
    scorer_config_digest: str
    decoder_config_digest: str
    protected_statistic: str
    attempt_id_version: str
    certificate_id: str
    certificate_digest: str
    certificate_provenance_digest: str
    invalidation_conditions: tuple[str, ...]

    def payload(self) -> dict[str, Any]:
        if int(self.schema_version) != SCHEMA_VERSION:
            raise ReplayAuthorizationError("unsupported replay-contract schema")
        RuntimeDeterminismSnapshot(
            self.runtime_fingerprint_digest,
            self.scorer_config_digest,
            self.decoder_config_digest,
            self.protected_statistic,
            self.attempt_id_version,
        ).validated()
        _require_nonempty("certificate_id", self.certificate_id)
        _require_hex64("certificate_digest", self.certificate_digest)
        _require_hex64(
            "certificate_provenance_digest", self.certificate_provenance_digest
        )
        cond = tuple(str(x) for x in self.invalidation_conditions)
        if not cond or any(not x for x in cond):
            raise ReplayAuthorizationError(
                "invalidation_conditions must be a nonempty tuple"
            )
        if len(set(cond)) != len(cond):
            raise ReplayAuthorizationError("duplicate invalidation condition")
        return {
            "schema_version": SCHEMA_VERSION,
            "runtime_fingerprint_digest": self.runtime_fingerprint_digest,
            "scorer_config_digest": self.scorer_config_digest,
            "decoder_config_digest": self.decoder_config_digest,
            "protected_statistic": self.protected_statistic,
            "attempt_id_version": self.attempt_id_version,
            "certificate_id": self.certificate_id,
            "certificate_digest": self.certificate_digest,
            "certificate_provenance_digest": self.certificate_provenance_digest,
            "invalidation_conditions": list(cond),
        }

    @property
    def contract_digest(self) -> str:
        return _digest_obj(self.payload())


@dataclass(frozen=True)
class TrustedCertificateRegistry:
    generation: str
    certificates: Mapping[str, str]
    revoked_certificate_ids: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        generation = _require_nonempty("registry generation", self.generation)
        certs: dict[str, str] = {}
        for cid, digest in dict(self.certificates).items():
            cid = _require_nonempty("certificate id", str(cid))
            certs[cid] = _require_hex64(f"certificate {cid}", str(digest))
        revoked = frozenset(str(x) for x in self.revoked_certificate_ids)
        object.__setattr__(self, "generation", generation)
        object.__setattr__(self, "certificates", MappingProxyType(certs))
        object.__setattr__(self, "revoked_certificate_ids", revoked)

    @property
    def registry_digest(self) -> str:
        return _digest_obj({
            "generation": self.generation,
            "certificates": dict(self.certificates),
            "revoked_certificate_ids": sorted(self.revoked_certificate_ids),
        })

    def validate_contract(self, contract: DeterminismReplayContract) -> None:
        payload = contract.payload()
        cid = payload["certificate_id"]
        if cid in self.revoked_certificate_ids:
            raise ReplayAuthorizationError("determinism certificate is revoked")
        expected = self.certificates.get(cid)
        if expected is None:
            raise ReplayAuthorizationError("determinism certificate is not trusted")
        if expected != contract.certificate_digest:
            raise ReplayAuthorizationError("determinism certificate digest mismatch")


def validate_contract_for_runtime(
    contract: DeterminismReplayContract,
    registry: TrustedCertificateRegistry,
    current: RuntimeDeterminismSnapshot,
    *,
    triggered_invalidation_conditions: Iterable[str] = (),
) -> None:
    registry.validate_contract(contract)
    current.validated()
    expected = RuntimeDeterminismSnapshot(
        contract.runtime_fingerprint_digest,
        contract.scorer_config_digest,
        contract.decoder_config_digest,
        contract.protected_statistic,
        contract.attempt_id_version,
    )
    if current != expected:
        raise ReplayAuthorizationError(
            "current runtime/scorer/decoder/protected-statistic/attempt-id "
            "snapshot differs from replay contract"
        )
    triggered = {str(x) for x in triggered_invalidation_conditions}
    invalidating = triggered.intersection(contract.invalidation_conditions)
    if invalidating:
        raise ReplayAuthorizationError(
            "determinism contract invalidated by: " + ",".join(sorted(invalidating))
        )


def _bound_request_binding(
    request_binding: Any,
    contract: DeterminismReplayContract,
    registry: TrustedCertificateRegistry,
) -> dict[str, Any]:
    """Build the forward-only request binding used by the historical ledger.

    The historical ledger stores only request_binding_digest, but its attempt_id
    is also derived from that digest. Therefore the contract digest and registry
    generation are transitively bound into both the RESERVE event and attempt_id
    without changing the historical reservation schema.
    """
    if isinstance(request_binding, Mapping) and AUTH_NAMESPACE in request_binding:
        raise ReplayAuthorizationError("request_binding collides with auth namespace")
    return {
        "request_binding": request_binding,
        AUTH_NAMESPACE: {
            "schema_version": SCHEMA_VERSION,
            "contract_digest": contract.contract_digest,
            "certificate_id": contract.certificate_id,
            "registry_generation": registry.generation,
            "registry_digest": registry.registry_digest,
        },
    }


def verify_attempt_module_identity(attempt_module: Any) -> None:
    path = getattr(attempt_module, "__file__", None)
    if not path:
        raise ReplayAuthorizationError("attempt module has no source path")
    data = __import__("pathlib").Path(path).read_bytes()
    observed = sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()
    if observed != ATTEMPT_LEDGER_BLOB:
        raise ReplayAuthorizationError(
            f"attempt ledger blob mismatch: expected {ATTEMPT_LEDGER_BLOB}, got {observed}"
        )


def _retry_constants(attempt_module: Any) -> tuple[str, str]:
    return (
        str(attempt_module.FAIL_CLOSED),
        str(attempt_module.DETERMINISTIC_REPLAY),
    )


def prepare_reservation(
    attempt_module: Any,
    ledger_blob: bytes,
    main_blob: bytes,
    capability: Any,
    *,
    block_id: str,
    slot_id: str,
    request_binding: Any,
    reserved_at: float,
    retry_policy: str,
    current_runtime: RuntimeDeterminismSnapshot | None = None,
    replay_contract: DeterminismReplayContract | None = None,
    trusted_registry: TrustedCertificateRegistry | None = None,
    triggered_invalidation_conditions: Iterable[str] = (),
    verify_attempt_identity: bool = True,
    **attempt_kwargs: Any,
):
    if verify_attempt_identity:
        verify_attempt_module_identity(attempt_module)
    fail_closed, deterministic = _retry_constants(attempt_module)
    if retry_policy == fail_closed:
        if replay_contract is not None:
            raise ReplayAuthorizationError(
                "FAIL_CLOSED must not be reinterpreted with a replay contract"
            )
        return attempt_module.prepare_reservation(
            ledger_blob, main_blob, capability,
            block_id=block_id,
            slot_id=slot_id,
            request_binding=request_binding,
            reserved_at=reserved_at,
            retry_policy=retry_policy,
            **attempt_kwargs,
        )
    if retry_policy != deterministic:
        raise ReplayAuthorizationError("unsupported retry policy")
    if current_runtime is None or replay_contract is None or trusted_registry is None:
        raise ReplayAuthorizationError(
            "DETERMINISTIC_REPLAY requires pre-score runtime snapshot, "
            "replay contract, and trusted certificate registry"
        )
    validate_contract_for_runtime(
        replay_contract,
        trusted_registry,
        current_runtime,
        triggered_invalidation_conditions=triggered_invalidation_conditions,
    )
    bound = _bound_request_binding(request_binding, replay_contract, trusted_registry)
    return attempt_module.prepare_reservation(
        ledger_blob, main_blob, capability,
        block_id=block_id,
        slot_id=slot_id,
        request_binding=bound,
        reserved_at=reserved_at,
        retry_policy=retry_policy,
        **attempt_kwargs,
    )


def reserve_and_issue(
    attempt_module: Any,
    writer: Any,
    ledger_blob: bytes,
    main_blob: bytes,
    capability: Any,
    **kwargs: Any,
):
    frame, _event, reservation = prepare_reservation(
        attempt_module, ledger_blob, main_blob, capability, **kwargs
    )
    durable = writer.append_fsync_readback(bytes(ledger_blob), frame)
    permit = attempt_module.acknowledge_reservation(
        ledger_blob, frame, durable
    )
    return durable, permit, reservation


def recover_deterministic_replay_permit(
    attempt_module: Any,
    ledger_blob: bytes,
    main_blob: bytes,
    capability: Any,
    *,
    block_id: str,
    slot_id: str,
    request_binding: Any,
    current_runtime: RuntimeDeterminismSnapshot,
    replay_contract: DeterminismReplayContract,
    trusted_registry: TrustedCertificateRegistry,
    triggered_invalidation_conditions: Iterable[str] = (),
    verify_attempt_identity: bool = True,
    **attempt_kwargs: Any,
):
    """Reissue only an authorization-bound deterministic attempt.

    A historical DETERMINISTIC_REPLAY reservation created without this facade
    cannot be recovered here because its request_binding_digest/attempt_id will
    not match the forward-only authorization envelope.
    """
    if verify_attempt_identity:
        verify_attempt_module_identity(attempt_module)
    _fail_closed, deterministic = _retry_constants(attempt_module)
    validate_contract_for_runtime(
        replay_contract,
        trusted_registry,
        current_runtime,
        triggered_invalidation_conditions=triggered_invalidation_conditions,
    )
    state = attempt_module.recover(bytes(ledger_blob))
    key = f"{block_id}\x1f{slot_id}"
    reservation = state.reservations.get(key)
    if reservation is None:
        raise ReplayAuthorizationError("no durable reservation to recover")
    if reservation.retry_policy != deterministic:
        raise ReplayAuthorizationError(
            "only DETERMINISTIC_REPLAY can use replay authorization"
        )
    bound = _bound_request_binding(request_binding, replay_contract, trusted_registry)
    try:
        return attempt_module.recover_deterministic_replay_permit(
            ledger_blob, main_blob, capability,
            block_id=block_id,
            slot_id=slot_id,
            request_binding=bound,
            **attempt_kwargs,
        )
    except Exception as exc:
        raise ReplayAuthorizationError(
            "reservation is not bound to this pre-score replay authorization"
        ) from exc


def authorization_binding_summary(
    contract: DeterminismReplayContract,
    registry: TrustedCertificateRegistry,
) -> dict[str, Any]:
    registry.validate_contract(contract)
    return {
        "schema_version": SCHEMA_VERSION,
        "attempt_ledger_filename": ATTEMPT_LEDGER_FILENAME,
        "attempt_ledger_blob": ATTEMPT_LEDGER_BLOB,
        "contract_digest": contract.contract_digest,
        "certificate_id": contract.certificate_id,
        "registry_generation": registry.generation,
        "registry_digest": registry.registry_digest,
        "protected_statistic": contract.protected_statistic,
        "attempt_id_version": contract.attempt_id_version,
    }


__all__ = [
    "SCHEMA_VERSION", "AUTH_NAMESPACE", "ATTEMPT_LEDGER_FILENAME",
    "ATTEMPT_LEDGER_BLOB", "ReplayAuthorizationError",
    "RuntimeDeterminismSnapshot", "DeterminismReplayContract",
    "TrustedCertificateRegistry", "validate_contract_for_runtime", "verify_attempt_module_identity",
    "prepare_reservation", "reserve_and_issue",
    "recover_deterministic_replay_permit", "authorization_binding_summary",
]
