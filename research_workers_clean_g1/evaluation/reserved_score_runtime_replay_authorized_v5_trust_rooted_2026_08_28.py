"""Trust-rooted non-default runtime for replay_authorized_v1 evaluation blocks.

This candidate supersedes the first v4 runtime sketch. FAIL_CLOSED remains
available. DETERMINISTIC_REPLAY authority is owned by the RuntimeContext: a
trusted certificate registry and runtime-snapshot provider are fixed at context
construction, not supplied by each score caller.
It loads the attempt ledger exactly once per RuntimeContext so launch-permit HMACs
remain stable inside a process epoch. New ADMITs are schema-v2
replay_authorized_v1 before durable capability issuance. CLOSE/recover use the
verified-graph replay entrypoint.

The runtime verifies the Git blob identity of every launch-path dependency before
scientific operations. The verified CLOSE wrapper separately verifies its own
transitive replay graph. This is a forward-only research candidate, not the
default runtime.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha1
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from typing import Any, Callable
from collections.abc import Mapping

SCHEMA_VERSION=1
GATE_FILENAME="durable_launch_capability_gate_replay_authorized_v1_2026_08_28.py"
GATE_BLOB="f31436df64a0e19474d399bb191471cbb4342ff6"
ATTEMPT_FILENAME="durable_attempt_reservation_ledger_2026-08-28.py"
ATTEMPT_BLOB="f51cc37e5897d8dc0f395da95c1f6dd1c12da791"
SCORE_FILENAME="score_launch_capability_wrapper_2026-08-28.py"
SCORE_BLOB="e610805ab1f495198c1b44ab82f02086233f1eda"
PIPELINE_FILENAME="reserved_score_pipeline_2026-08-28.py"
PIPELINE_BLOB="811bee4ddac614cd1ebd517a465cfb978006e91a"
AUTH_FILENAME="deterministic_replay_authorization_facade_v1_2026_08_28.py"
AUTH_BLOB="f21613ebb6db487d70983ad46caf063ac86c804b"
REGISTRY_FILENAME="reservation_runtime_provenance_contract_registry_v2_2026_08_28.py"
REGISTRY_BLOB="c4d0439dba3ddf2183835c3fbaa3b3012ec1f468"
CLOSE_FILENAME="reservation_compliance_close_replay_runtime_provenance_v4_verified_graph_2026_08_28.py"
CLOSE_BLOB="c65203aa9cac3b83e9cc1413046e1a71b7ddaca8"
RUNTIME_GRAPH={GATE_FILENAME:GATE_BLOB,ATTEMPT_FILENAME:ATTEMPT_BLOB,SCORE_FILENAME:SCORE_BLOB,PIPELINE_FILENAME:PIPELINE_BLOB,AUTH_FILENAME:AUTH_BLOB,REGISTRY_FILENAME:REGISTRY_BLOB,CLOSE_FILENAME:CLOSE_BLOB}

class ReplayAuthorizedRuntimeError(RuntimeError):pass

def git_blob_sha1(data:bytes)->str:return sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def verify_runtime_graph()->dict[str,str]:
    root=Path(__file__).resolve().parent; out={}
    for fn,expected in RUNTIME_GRAPH.items():
        p=root/fn
        if not p.is_file(): raise ReplayAuthorizedRuntimeError(f"missing runtime dependency {fn}")
        got=git_blob_sha1(p.read_bytes());out[fn]=got
        if got!=expected: raise ReplayAuthorizedRuntimeError(f"runtime dependency mismatch for {fn}: expected {expected}, got {got}")
    return out

def _load(fn:str,name:str)->Any:
    p=Path(__file__).resolve().with_name(fn);s=spec_from_file_location(name,p)
    if s is None or s.loader is None:raise ImportError(p)
    m=module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m

@dataclass(frozen=True)
class ReservationHandle:
    permit:Any
    reservation:Any
    effective_request_binding:Any
    retry_policy:str

class RuntimeContext:
    """One process epoch. A new context intentionally gets a new attempt HMAC key."""
    def __init__(self,*,trusted_registry:Any|None=None,runtime_snapshot_provider:Callable[[],Any]|None=None,invalidation_provider:Callable[[],Any]|None=None)->None:
        verify_runtime_graph()
        self.gate=_load(GATE_FILENAME,f"_eval_ra_gate_{id(self)}")
        self.attempt=_load(ATTEMPT_FILENAME,f"_eval_ra_attempt_{id(self)}")
        self.score=_load(SCORE_FILENAME,f"_eval_ra_score_{id(self)}")
        self.pipeline=_load(PIPELINE_FILENAME,f"_eval_ra_pipeline_{id(self)}")
        self.auth=_load(AUTH_FILENAME,f"_eval_ra_auth_{id(self)}")
        self.registry=_load(REGISTRY_FILENAME,f"_eval_ra_registry_{id(self)}")
        self.close=_load(CLOSE_FILENAME,f"_eval_ra_close_{id(self)}")
        self._runtime_snapshot_provider=runtime_snapshot_provider
        self._invalidation_provider=invalidation_provider or (lambda:())
        self._trusted_registry=self._normalize_registry(trusted_registry) if trusted_registry is not None else None
        verify_runtime_graph()

    def _field(self,obj:Any,key:str):
        if hasattr(obj,key): return getattr(obj,key)
        if isinstance(obj,Mapping): return obj[key]
        raise ReplayAuthorizedRuntimeError(f"authorization object lacks {key}")

    def _normalize_registry(self,trusted_registry:Any):
        if isinstance(trusted_registry,self.auth.TrustedCertificateRegistry): return trusted_registry
        return self.auth.TrustedCertificateRegistry(
            str(self._field(trusted_registry,'generation')),
            dict(self._field(trusted_registry,'certificates')),
            frozenset(self._field(trusted_registry,'revoked_certificate_ids')),
        )

    @property
    def authorization_root_digest(self)->str|None:
        return self._trusted_registry.registry_digest if self._trusted_registry is not None else None

    def _require_authorization_root(self):
        if self._trusted_registry is None or self._runtime_snapshot_provider is None:
            raise ReplayAuthorizedRuntimeError("DETERMINISTIC_REPLAY is disabled: runtime has no fixed authorization root")
        current=self._runtime_snapshot_provider()
        invalid=tuple(self._invalidation_provider())
        return current,self._trusted_registry,invalid

    def admit_and_issue_capability(self,writer:Any,main_blob:bytes,ledger_blob:bytes,**kwargs:Any):
        verify_runtime_graph()
        out=self.gate.admit_and_issue_capability(writer,bytes(main_blob),bytes(ledger_blob),**kwargs)
        verify_runtime_graph();return out

    def normalize_authorization(self,current_runtime:Any,replay_contract:Any):
        """Rehydrate runtime/contract data into this process epoch's module types."""
        if isinstance(current_runtime,self.auth.RuntimeDeterminismSnapshot): snap=current_runtime
        else:
            snap=self.auth.RuntimeDeterminismSnapshot(
                str(self._field(current_runtime,'runtime_fingerprint_digest')),
                str(self._field(current_runtime,'scorer_config_digest')),
                str(self._field(current_runtime,'decoder_config_digest')),
                str(self._field(current_runtime,'protected_statistic')),
                str(self._field(current_runtime,'attempt_id_version')),
            )
        if isinstance(replay_contract,self.auth.DeterminismReplayContract): contract=replay_contract
        else:
            contract=self.auth.DeterminismReplayContract(
                int(self._field(replay_contract,'schema_version')),str(self._field(replay_contract,'runtime_fingerprint_digest')),
                str(self._field(replay_contract,'scorer_config_digest')),str(self._field(replay_contract,'decoder_config_digest')),
                str(self._field(replay_contract,'protected_statistic')),str(self._field(replay_contract,'attempt_id_version')),
                str(self._field(replay_contract,'certificate_id')),str(self._field(replay_contract,'certificate_digest')),
                str(self._field(replay_contract,'certificate_provenance_digest')),tuple(self._field(replay_contract,'invalidation_conditions')),
            )
        return snap,contract

    def reserve_and_issue(self,writer:Any,ledger_blob:bytes,main_blob:bytes,capability:Any,*,block_id:str,slot_id:str,request_binding:Any,reserved_at:float,retry_policy:str,replay_contract:Any|None=None):
        verify_runtime_graph();legacy=self.gate._default_adapter()
        if retry_policy==self.attempt.FAIL_CLOSED:
            if replay_contract is not None:
                raise ReplayAuthorizedRuntimeError("FAIL_CLOSED does not consume deterministic replay authorization")
            effective=request_binding
            _old,event,reservation=self.attempt.prepare_reservation(bytes(ledger_blob),bytes(main_blob),capability,block_id=str(block_id),slot_id=str(slot_id),request_binding=effective,reserved_at=float(reserved_at),retry_policy=retry_policy,gate_module=self.gate,adapter_module=legacy,score_wrapper_module=self.score)
        elif retry_policy==self.attempt.DETERMINISTIC_REPLAY:
            if replay_contract is None:
                raise ReplayAuthorizedRuntimeError("DETERMINISTIC_REPLAY requires a persisted replay contract")
            current_runtime,trusted_registry,triggered_invalidation_conditions=self._require_authorization_root()
            current_runtime,replay_contract=self.normalize_authorization(current_runtime,replay_contract)
            effective=self.auth.authorized_request_binding(request_binding,replay_contract,trusted_registry,current_runtime,triggered_invalidation_conditions=triggered_invalidation_conditions)
            _old,event,reservation=self.auth.prepare_reservation(self.attempt,bytes(ledger_blob),bytes(main_blob),capability,block_id=str(block_id),slot_id=str(slot_id),request_binding=request_binding,reserved_at=float(reserved_at),retry_policy=retry_policy,current_runtime=current_runtime,replay_contract=replay_contract,trusted_registry=trusted_registry,triggered_invalidation_conditions=triggered_invalidation_conditions,gate_module=self.gate,adapter_module=legacy,score_wrapper_module=self.score)
        else: raise ReplayAuthorizedRuntimeError("unsupported retry policy")
        event=dict(event);event["gate_binding"]={"filename":GATE_FILENAME,"blob":GATE_BLOB};event[self.registry.BINDING_FIELD]=self.registry.binding_for_id(self.registry.REPLAY_AUTHORIZED_V1_BINDING_ID)
        frame=self.attempt._encode_frame(event);durable=writer.append_fsync_readback(bytes(ledger_blob),frame);permit=self.attempt.acknowledge_reservation(bytes(ledger_blob),frame,durable)
        verify_runtime_graph();return durable,ReservationHandle(permit,reservation,effective,retry_policy),event

    def recover_deterministic_replay_handle(self,ledger_blob:bytes,main_blob:bytes,capability:Any,*,block_id:str,slot_id:str,request_binding:Any,replay_contract:Any):
        verify_runtime_graph();legacy=self.gate._default_adapter();current_runtime,trusted_registry,triggered_invalidation_conditions=self._require_authorization_root();current_runtime,replay_contract=self.normalize_authorization(current_runtime,replay_contract);effective=self.auth.authorized_request_binding(request_binding,replay_contract,trusted_registry,current_runtime,triggered_invalidation_conditions=triggered_invalidation_conditions)
        permit=self.auth.recover_deterministic_replay_permit(self.attempt,bytes(ledger_blob),bytes(main_blob),capability,block_id=str(block_id),slot_id=str(slot_id),request_binding=request_binding,current_runtime=current_runtime,replay_contract=replay_contract,trusted_registry=trusted_registry,triggered_invalidation_conditions=triggered_invalidation_conditions,gate_module=self.gate,adapter_module=legacy,score_wrapper_module=self.score)
        state=self.attempt.recover(bytes(ledger_blob));reservation=state.reservations[self.attempt._reservation_key(str(block_id),str(slot_id))]
        return ReservationHandle(permit,reservation,effective,self.attempt.DETERMINISTIC_REPLAY)

    def launch_reserved_score(self,main_blob:bytes,ledger_blob:bytes,capability:Any,handle:ReservationHandle,*,scorer:Callable[[str],float],clock:Callable[[],float]):
        verify_runtime_graph();legacy=self.gate._default_adapter();result=self.pipeline.launch_reserved_score(bytes(main_blob),bytes(ledger_blob),capability,handle.permit,request_binding=handle.effective_request_binding,scorer=scorer,clock=clock,gate_module=self.gate,adapter_module=legacy,score_module=self.score,attempt_module=self.attempt);verify_runtime_graph();return result

    def prepare_bound_slot(self,main_blob:bytes,ledger_blob:bytes,capability:Any,handle:ReservationHandle,result:Any):
        legacy=self.gate._default_adapter();return self.pipeline.prepare_bound_slot(bytes(main_blob),bytes(ledger_blob),capability,handle.permit,result,request_binding=handle.effective_request_binding,gate_module=self.gate,adapter_module=legacy,score_module=self.score,attempt_module=self.attempt)

    def prepare_commit(self,ledger_blob:bytes,handle:ReservationHandle,*,slot_event_digest:str,committed_at:float):
        return self.attempt.prepare_commit(bytes(ledger_blob),handle.permit,slot_event_digest=str(slot_event_digest),committed_at=float(committed_at))

    def prepare_recovery_commit_from_main(self,ledger_blob:bytes,main_blob:bytes,*,block_id:str,slot_id:str,committed_at:float):
        legacy=self.gate._default_adapter();return self.pipeline.prepare_recovery_commit_from_main(bytes(ledger_blob),bytes(main_blob),block_id=str(block_id),slot_id=str(slot_id),committed_at=float(committed_at),gate_module=self.gate,adapter_module=legacy,attempt_module=self.attempt)

    def prepare_close(self,main_blob:bytes,ledger_blob:bytes,*,block_id:str,closed_at:float):
        verify_runtime_graph();out=self.close.prepare_close(bytes(main_blob),bytes(ledger_blob),block_id=str(block_id),closed_at=float(closed_at));verify_runtime_graph();return out

    def recover(self,main_blob:bytes,ledger_blob:bytes):
        verify_runtime_graph();out=self.close.recover(bytes(main_blob),bytes(ledger_blob));verify_runtime_graph();return out

__all__=["SCHEMA_VERSION","RUNTIME_GRAPH","ReplayAuthorizedRuntimeError","ReservationHandle","RuntimeContext","verify_runtime_graph"]
