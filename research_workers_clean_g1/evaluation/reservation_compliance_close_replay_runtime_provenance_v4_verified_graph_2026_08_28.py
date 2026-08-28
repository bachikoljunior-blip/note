"""Verified-graph entrypoint for evaluation compliance CLOSE/replay v3.

The persisted v3 replay layer records expected Git blob IDs in its bindings but
its filename-based sibling loader does not itself verify that the bytes loaded
from disk match those IDs. This wrapper makes code identity an executable
precondition for the default scientific replay path.

Scope: accidental/deployment drift in the single-process filesystem graph. The
wrapper verifies the complete transitive graph used by v3 recover/prepare_close
immediately before and after each operation and refuses caller-supplied module
injection. It does not claim protection against an adversary that can rewrite
files during a call and restore them before the post-check, or against mutation
of this wrapper/interpreter itself. Those require a stronger trusted loader or
OS-level immutable content-addressed deployment.
"""
from __future__ import annotations

from hashlib import sha1
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from typing import Any

SCHEMA_VERSION = 1
V3_FILENAME = "reservation_compliance_close_replay_runtime_provenance_v3_2026_08_28.py"
V3_BLOB = "99c74f7134210d88cc4cfd0ab857fdd197f7e626"

# Exact transitive semantic graph exercised by the default v3 CLOSE/replay path.
# Files named only as dormant constants in imported modules are intentionally not
# included unless their code is actually imported/executed by this path.
VERIFIED_GRAPH = {
    V3_FILENAME: V3_BLOB,
    "atomic_dual_channel_journal_2026-08-27T2107_JST.py": "36540f1e8d0b47d4c678f091da87e90c385ef6f7",
    "durable_k_guard_hybrid_journal_2026-08-28.py": "d70f42076ad04549c82c5906132aaae59657e335",
    "v3_k_guard_hybrid_reporter_2026-08-28.py": "66a3f0744deb3ba5c5ee52a2e29f683fa8e94987",
    "weighted_average_incremental_lsm_v3_warm_root_2026-08-27.py": "54159990956368010b3445909f8bd8e8f569ecb7",
    "v3_same_history_K_guard_2026-08-28_v2.py": "6f4a5ef2340730b5de493ad46ec21650486689f4",
    "reservation_compliance_auditor_2026-08-28.py": "0a845daa2675ba2c769c231769b1729f7e78f01d",
    "durable_attempt_reservation_ledger_2026-08-28.py": "f51cc37e5897d8dc0f395da95c1f6dd1c12da791",
    "reservation_compliance_auditor_runtime_provenance_2026-08-28.py": "dd5e09bde7e91b0f534896922aeb5b2529e92996",
    "reserved_score_runtime_compliance_2026-08-28.py": "3e58813f34079e7f92eb0728bd7f9c27810d5418",
    "reservation_runtime_provenance_contract_2026-08-28.py": "f6a4d996381bd100038d6ccfcf1b7c5f3f28e905",
    "reservation_compliance_auditor_runtime_provenance_v2_2026_08_28.py": "b74465bd5f68882cee4c5b3fbd2a98d73a684b81",
    "reservation_runtime_provenance_contract_registry_v2_2026_08_28.py": "c4d0439dba3ddf2183835c3fbaa3b3012ec1f468",
}

class DependencyIdentityError(RuntimeError):
    pass


def git_blob_sha1(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def verify_graph() -> dict[str, str]:
    root = Path(__file__).resolve().parent
    observed: dict[str, str] = {}
    for filename, expected in VERIFIED_GRAPH.items():
        p = root / filename
        if not p.is_file():
            raise DependencyIdentityError(f"missing verified dependency: {filename}")
        got = git_blob_sha1(p.read_bytes())
        observed[filename] = got
        if got != expected:
            raise DependencyIdentityError(
                f"dependency blob mismatch for {filename}: expected {expected}, got {got}"
            )
    return observed


def _load_verified_v3() -> Any:
    verify_graph()
    p = Path(__file__).resolve().with_name(V3_FILENAME)
    spec = spec_from_file_location("_evaluation_verified_graph_v3", p)
    if spec is None or spec.loader is None:
        raise DependencyIdentityError("cannot load verified v3 entrypoint")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    # Catch ordinary drift that occurred between pre-check and import.
    verify_graph()
    return module


def recover(main_blob: bytes, ledger_blob: bytes) -> Any:
    v3 = _load_verified_v3()
    result = v3.recover(bytes(main_blob), bytes(ledger_blob))
    verify_graph()
    return result


def prepare_close(
    main_blob: bytes,
    ledger_blob: bytes,
    *,
    block_id: str,
    closed_at: float,
):
    v3 = _load_verified_v3()
    result = v3.prepare_close(
        bytes(main_blob), bytes(ledger_blob),
        block_id=str(block_id), closed_at=float(closed_at),
    )
    verify_graph()
    return result

__all__ = [
    "SCHEMA_VERSION", "V3_FILENAME", "V3_BLOB", "VERIFIED_GRAPH",
    "DependencyIdentityError", "git_blob_sha1", "verify_graph", "recover", "prepare_close",
]
