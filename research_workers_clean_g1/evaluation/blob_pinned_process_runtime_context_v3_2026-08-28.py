"""Blob-pinned process-stable runtime context v3 for evaluation research.

V3 retains the V2 replay-authority fix and restores ordinary prepare_commit API parity.

V2 fixed replay authority for subsequent ADMITs after a runtime-provenance CLOSE:
ADMIT recovery uses the provenance-aware close/replay module, not the historical
compliance replay module. The process-stable attempt-module identity contract is
otherwise unchanged.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha1
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from typing import Any

MANIFEST = {
    "top": ("reserved_score_runtime_compliance_provenance_2026-08-28.py", "f9a3b7a120c36fe3ff37c8fe7167d1c4e66e8d6f"),
    "base": ("reserved_score_runtime_compliance_2026-08-28.py", "3e58813f34079e7f92eb0728bd7f9c27810d5418"),
    "contract": ("reservation_runtime_provenance_contract_2026-08-28.py", "f6a4d996381bd100038d6ccfcf1b7c5f3f28e905"),
    "closeprov": ("reservation_compliance_close_replay_runtime_provenance_2026-08-28.py", "c9982f2ef14cff5b1f59b314e95250745706c5e4"),
    "runtime_auditor": ("reservation_compliance_auditor_runtime_provenance_2026-08-28.py", "dd5e09bde7e91b0f534896922aeb5b2529e92996"),
    "historical_close": ("reservation_compliance_close_replay_2026-08-28.py", "ac69f485383118192b533e258bb6033b454ca9b3"),
    "historical_auditor": ("reservation_compliance_auditor_2026-08-28.py", "0a845daa2675ba2c769c231769b1729f7e78f01d"),
    "gate": ("durable_launch_capability_gate_compliance_2026-08-28.py", "a2aa84a3ef98d1647430a384a514d7cbc18303c3"),
    "attempt": ("durable_attempt_reservation_ledger_2026-08-28.py", "f51cc37e5897d8dc0f395da95c1f6dd1c12da791"),
    "score": ("score_launch_capability_wrapper_2026-08-28.py", "e610805ab1f495198c1b44ab82f02086233f1eda"),
    "pipeline": ("reserved_score_pipeline_2026-08-28.py", "811bee4ddac614cd1ebd517a465cfb978006e91a"),
    "legacy": ("durable_k_guard_hybrid_journal_2026-08-28.py", "d70f42076ad04549c82c5906132aaae59657e335"),
    "atomic": ("atomic_dual_channel_journal_2026-08-27T2107_JST.py", "36540f1e8d0b47d4c678f091da87e90c385ef6f7"),
    "reporter": ("v3_k_guard_hybrid_reporter_2026-08-28.py", "66a3f0744deb3ba5c5ee52a2e29f683fa8e94987"),
    "v3": ("weighted_average_incremental_lsm_v3_warm_root_2026-08-27.py", "54159990956368010b3445909f8bd8e8f569ecb7"),
    "kguard": ("v3_same_history_K_guard_2026-08-28_v2.py", "6f4a5ef2340730b5de493ad46ec21650486689f4"),
    "writer": ("stable_sidecar_journal_io_2026_08_28.py", "a7fc9e82ccb636e0aaa55bf1793a28dac8ac58fc"),
}

class RuntimeContextError(RuntimeError): pass

def git_blob_sha(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def _load_exact(root: Path, key: str) -> Any:
    filename, expected_blob = MANIFEST[key]
    path = root / filename
    data = path.read_bytes()
    observed = git_blob_sha(data)
    if observed != expected_blob:
        raise RuntimeContextError(f"{filename}: expected Git blob {expected_blob}, got {observed}")
    name = f"_evaluation_process_context_v2_{key}"
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None: raise ImportError(path)
    module = module_from_spec(spec); sys.modules[name] = module; spec.loader.exec_module(module); return module

@dataclass
class ProcessStableRuntimeContextV3:
    root: Path; top: Any; base: Any; contract: Any; closeprov: Any; runtime_auditor: Any; historical_close: Any; historical_auditor: Any; gate: Any; attempt: Any; score: Any; pipeline: Any; legacy: Any; atomic: Any; reporter: Any; writer_module: Any
    @classmethod
    def load(cls, directory: str | Path):
        root=Path(directory).resolve()
        for key,(filename,expected_blob) in MANIFEST.items():
            data=(root/filename).read_bytes(); got=git_blob_sha(data)
            if got != expected_blob: raise RuntimeContextError(f"{key}:{filename}: expected {expected_blob}, got {got}")
        atomic=_load_exact(root,"atomic"); legacy=_load_exact(root,"legacy"); historical_auditor=_load_exact(root,"historical_auditor"); historical_close=_load_exact(root,"historical_close"); gate=_load_exact(root,"gate"); attempt=_load_exact(root,"attempt"); score=_load_exact(root,"score"); pipeline=_load_exact(root,"pipeline"); base=_load_exact(root,"base"); contract=_load_exact(root,"contract"); runtime_auditor=_load_exact(root,"runtime_auditor"); closeprov=_load_exact(root,"closeprov"); top=_load_exact(root,"top"); reporter=_load_exact(root,"reporter"); writer_module=_load_exact(root,"writer")
        return cls(root,top,base,contract,closeprov,runtime_auditor,historical_close,historical_auditor,gate,attempt,score,pipeline,legacy,atomic,reporter,writer_module)
    def admit_and_issue_capability(self, writer, main, ledger, **kwargs):
        return self.top.admit_and_issue_capability(writer,main,ledger,base_runtime_module=self.base,contract_module=self.contract,gate_module=self.gate,adapter_module=self.legacy,compliance_module=self.closeprov,attempt_module=self.attempt,reporter_factory=self.reporter.KGuardHybridReporter,**kwargs)
    def reserve_and_issue(self, writer, ledger, main, capability, **kwargs):
        return self.top.reserve_and_issue(writer,ledger,main,capability,base_runtime_module=self.base,attempt_module=self.attempt,gate_module=self.gate,score_module=self.score,**kwargs)
    def launch_reserved_score(self, main, ledger, capability, permit, **kwargs):
        return self.top.launch_reserved_score(main,ledger,capability,permit,base_runtime_module=self.base,pipeline_module=self.pipeline,gate_module=self.gate,attempt_module=self.attempt,score_module=self.score,**kwargs)
    def prepare_bound_slot(self, main, ledger, capability, permit, result, **kwargs):
        return self.top.prepare_bound_slot(main,ledger,capability,permit,result,base_runtime_module=self.base,pipeline_module=self.pipeline,gate_module=self.gate,attempt_module=self.attempt,score_module=self.score,reporter_factory=self.reporter.KGuardHybridReporter,**kwargs)
    def prepare_commit(self, ledger, permit, **kwargs):
        return self.top.prepare_commit(ledger,permit,base_runtime_module=self.base,attempt_module=self.attempt,**kwargs)
    def prepare_recovery_commit_from_main(self, ledger, main, **kwargs):
        return self.top.prepare_recovery_commit_from_main(ledger,main,base_runtime_module=self.base,pipeline_module=self.pipeline,gate_module=self.gate,attempt_module=self.attempt,**kwargs)
    def prepare_close(self, main, ledger, **kwargs):
        return self.top.prepare_close(main,ledger,base_runtime_module=self.base,close_module=self.closeprov,gate_module=self.gate,attempt_module=self.attempt,auditor_module=self.runtime_auditor,historical_auditor_module=self.historical_auditor,contract_module=self.contract,reporter_factory=self.reporter.KGuardHybridReporter,**kwargs)
    def recover(self, main, ledger, **kwargs):
        return self.top.recover(main,ledger,base_runtime_module=self.base,close_module=self.closeprov,gate_module=self.gate,attempt_module=self.attempt,auditor_module=self.runtime_auditor,historical_auditor_module=self.historical_auditor,contract_module=self.contract,reporter_factory=self.reporter.KGuardHybridReporter,**kwargs)
