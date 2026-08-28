"""Reproduce the process-epoch permit reload defect on the exact critical modules.

Run from a checkout containing the evaluation role-local files. The harness
copies the exact top/base/attempt modules into a temporary directory and writes
minimal deterministic stubs for unrelated sibling semantics. It therefore
isolates the module-instance/HMAC contract without claiming full-sibling byte
execution.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha1
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json, shutil, sys, tempfile

EXACT = {
    "reserved_score_runtime_compliance_provenance_2026-08-28.py": "f9a3b7a120c36fe3ff37c8fe7167d1c4e66e8d6f",
    "reserved_score_runtime_compliance_2026-08-28.py": "3e58813f34079e7f92eb0728bd7f9c27810d5418",
    "durable_attempt_reservation_ledger_2026-08-28.py": "f51cc37e5897d8dc0f395da95c1f6dd1c12da791",
}

def blob_sha(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def load(path: Path, name: str):
    s=spec_from_file_location(name,path); m=module_from_spec(s); sys.modules[name]=m; s.loader.exec_module(m); return m

class Writer:
    def append_fsync_readback(self, expected_before: bytes, frame: bytes) -> bytes:
        return bytes(expected_before)+bytes(frame)
@dataclass
class Cap:
    capability_digest: str = "cap"

def main() -> None:
    src=Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        for fn, expected in EXACT.items():
            data=(src/fn).read_bytes()
            got=blob_sha(data)
            if got != expected: raise RuntimeError(f"{fn}: expected {expected}, got {got}")
            (root/fn).write_bytes(data)
        (root/"durable_launch_capability_gate_compliance_2026-08-28.py").write_text(
            "class Adapter: pass\n_ADAPTER=Adapter()\ndef _default_adapter(): return _ADAPTER\ndef _verify_capability_against_blob(main_blob, capability, block_id, slot_id, adapter): return None\n")
        (root/"score_launch_capability_wrapper_2026-08-28.py").write_text(
            "from hashlib import sha256\ndef _attempt_id(capability_digest, block_id, slot_id, request_binding_digest):\n    return sha256(f'{capability_digest}|{block_id}|{slot_id}|{request_binding_digest}'.encode()).hexdigest()\n")
        (root/"reserved_score_pipeline_2026-08-28.py").write_text(
            "def launch_reserved_score(main_blob, ledger_blob, capability, permit, *, attempt_module, scorer=None, **kwargs):\n    attempt_module.validate_launch_permit(ledger_blob, permit)\n    return scorer() if scorer is not None else 'ok'\n")
        top=load(root/"reserved_score_runtime_compliance_provenance_2026-08-28.py","top_exact")
        writer=Writer(); cap=Cap(); args=dict(block_id="b",slot_id="s",request_binding={"x":1},reserved_at=1.0)
        ledger, permit, _=top.reserve_and_issue(writer,b"",b"",cap,**args)
        n={"v":0}
        try:
            top.launch_reserved_score(b"",ledger,cap,permit,scorer=lambda:(n.__setitem__("v",n["v"]+1) or "scored"))
            default_error=None
        except Exception as e:
            default_error=f"{type(e).__name__}: {e}"
        base=load(root/"reserved_score_runtime_compliance_2026-08-28.py","base_stable")
        attempt=load(root/"durable_attempt_reservation_ledger_2026-08-28.py","attempt_stable")
        gate=load(root/"durable_launch_capability_gate_compliance_2026-08-28.py","gate_stable")
        score=load(root/"score_launch_capability_wrapper_2026-08-28.py","score_stable")
        pipeline=load(root/"reserved_score_pipeline_2026-08-28.py","pipeline_stable")
        ledger2, permit2, _=top.reserve_and_issue(writer,b"",b"",cap,base_runtime_module=base,attempt_module=attempt,gate_module=gate,score_module=score,**args)
        n2={"v":0}
        stable=top.launch_reserved_score(b"",ledger2,cap,permit2,scorer=lambda:(n2.__setitem__("v",n2["v"]+1) or "scored"),base_runtime_module=base,pipeline_module=pipeline,gate_module=gate,attempt_module=attempt,score_module=score)
        print(json.dumps({"default_error":default_error,"default_scorer_calls":n["v"],"stable_result":stable,"stable_scorer_calls":n2["v"]},indent=2))

if __name__ == "__main__": main()
