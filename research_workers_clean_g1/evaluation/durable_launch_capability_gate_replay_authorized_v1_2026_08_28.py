"""Forward-only launch gate for schema-v2 replay_authorized_v1 evaluation blocks.

New ADMITs are built from verified compliance replay state and are bound to the
registry-v2 replay_authorized_v1 predicate before the ADMIT can become durable.
The capability is issued only after exact durable readback and verified replay.
Historical/current-v1 blocks are replayed by the verified replay layer but this
gate never generates those older ADMIT contract versions.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
from typing import Any, Protocol

LEGACY_ADAPTER_FILENAME="durable_k_guard_hybrid_journal_2026-08-28.py"
LEGACY_ADAPTER_BLOB="d70f42076ad04549c82c5906132aaae59657e335"
VERIFIED_REPLAY_FILENAME="reservation_compliance_close_replay_runtime_provenance_v4_verified_graph_2026_08_28.py"
VERIFIED_REPLAY_BLOB="c65203aa9cac3b83e9cc1413046e1a71b7ddaca8"
REGISTRY_FILENAME="reservation_runtime_provenance_contract_registry_v2_2026_08_28.py"
REGISTRY_BLOB="c4d0439dba3ddf2183835c3fbaa3b3012ec1f468"
SCHEMA_VERSION=3

def _canon(obj:Any)->bytes:
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def _digest_obj(obj:Any)->str:return sha256(_canon(obj)).hexdigest()
def _digest_bytes(blob:bytes)->str:return sha256(blob).hexdigest()
def _load(fn:str,name:str)->Any:
    p=Path(__file__).resolve().with_name(fn); s=spec_from_file_location(name,p)
    if s is None or s.loader is None: raise ImportError(p)
    m=module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m

def _default_adapter(): return _load(LEGACY_ADAPTER_FILENAME,"_evaluation_replay_auth_gate_legacy")
def _default_replay(): return _load(VERIFIED_REPLAY_FILENAME,"_evaluation_replay_auth_gate_replay")
def _default_registry(): return _load(REGISTRY_FILENAME,"_evaluation_replay_auth_gate_registry")

class ReplayAuthorizedLaunchCapabilityError(RuntimeError):pass
class DurableAppendWriter(Protocol):
    def append_fsync_readback(self,expected_before:bytes,frame:bytes)->bytes:...

@dataclass(frozen=True)
class LaunchCapability:
    schema_version:int; block_id:str; admit_event_id:str; durable_prefix_len:int
    durable_prefix_sha256:str; admit_event_digest:str; reporting_admission_digest:str
    admitted_slot_set_digest:str; deadline:float; runtime_binding_digest:str
    compliance_history_digest:str; capability_digest:str
    def payload(self):
        d=asdict(self);d.pop("capability_digest",None);return d

@dataclass(frozen=True)
class _RawJournalState:
    base:Any;active_admit:dict[str,Any]|None;valid_len:int;tail_status:str

def _runtime_binding()->dict[str,Any]:
    return {"schema_version":SCHEMA_VERSION,
      "legacy_wire_adapter":{"filename":LEGACY_ADAPTER_FILENAME,"blob":LEGACY_ADAPTER_BLOB},
      "verified_compliance_replay":{"filename":VERIFIED_REPLAY_FILENAME,"blob":VERIFIED_REPLAY_BLOB},
      "runtime_provenance_registry":{"filename":REGISTRY_FILENAME,"blob":REGISTRY_BLOB},
      "required_admit_binding_id":"replay_authorized_v1"}

def _validate_capability_integrity(cap:LaunchCapability)->None:
    if int(cap.schema_version)!=SCHEMA_VERSION: raise ReplayAuthorizedLaunchCapabilityError("unsupported capability schema")
    if cap.runtime_binding_digest!=_digest_obj(_runtime_binding()): raise ReplayAuthorizedLaunchCapabilityError("runtime binding mismatch")
    if cap.capability_digest!=_digest_obj(cap.payload()): raise ReplayAuthorizedLaunchCapabilityError("capability digest mismatch")

def _decode_exact_admit(prefix:bytes,legacy:Any):
    atomic=legacy._default_atomic(); events,valid,tail=atomic.decode_valid_prefix(prefix)
    if tail!="clean_eof" or valid!=len(prefix) or not events: raise ReplayAuthorizedLaunchCapabilityError("acknowledged prefix is not a clean journal")
    e=events[-1]
    if e.get("kind")!="ADMIT": raise ReplayAuthorizedLaunchCapabilityError("acknowledged boundary is not ADMIT")
    return atomic,e

def _raw_journal_state(blob:bytes,legacy:Any)->_RawJournalState:
    atomic=legacy._default_atomic(); events,valid,tail=atomic.decode_valid_prefix(bytes(blob)); base=atomic.AtomicDualChannelJournal(); active=None
    for e in events:
        status=base.apply(e)
        if e.get("kind")=="ADMIT" and status=="admitted":active=e
        elif e.get("kind")=="CLOSE" and status=="closed":active=None
    return _RawJournalState(base,active,valid,tail)

def _reporting_fingerprint(state:Any)->dict[str,Any]:
    latest=getattr(state,"latest_compliance",None); snap=getattr(state,"latest_snapshot",None); pending=getattr(state,"pending_token",None)
    if pending is None:p=None
    elif hasattr(pending,"__dataclass_fields__"):p=asdict(pending)
    elif isinstance(pending,dict):p=pending
    else:p=repr(pending)
    return {"closed_rows":len(state.base.closed_rows),"reporting_rows":int(state.reporting_rows),"reporter":state.reporter.state(),"pending_token":p,"latest_snapshot":snap,"latest_compliance_digest":_digest_obj(latest) if latest is not None else None}

def prepare_admit(main_blob:bytes,ledger_blob:bytes,*,block_id:str,slot_ids:list[str]|tuple[str,...],admitted_at:float,deadline:float,b_cap:int,adapter_module=None,replay_module=None,registry_module=None):
    legacy=adapter_module or _default_adapter(); replay=replay_module or _default_replay(); registry=registry_module or _default_registry()
    state=replay.recover(bytes(main_blob),bytes(ledger_blob))
    if state.tail_status!="clean_eof" or state.valid_len!=len(main_blob): raise ReplayAuthorizedLaunchCapabilityError("repair/quarantine main tail before ADMIT")
    if state.base.active is not None or state.pending_token is not None: raise ReplayAuthorizedLaunchCapabilityError("cannot admit while a block is active")
    atomic=legacy._default_atomic(); event=atomic.AtomicDualChannelJournal.admit_event(str(block_id),slot_ids,float(admitted_at),float(deadline),int(b_cap))
    token=state.reporter.admit(len(tuple(slot_ids))/int(b_cap)); td=legacy._token_dict(token)
    event["reporting_binding"]=legacy._binding(); event["reporting_admission"]=td; event["reporting_admission_digest"]=_digest_obj(td); event["reporting_weight_prefix_digest"]=td["weight_prefix_digest"]
    event["reporting_contract"]={"pre_score_admission":True,"slot_launch_requires_durable_admit":True,"handoff_row_quarantined_if_guard_fails":True,"close_required_before_report_exposure":True,"recovery_authority":VERIFIED_REPLAY_FILENAME}
    event=registry.bind_admit_v2(event,registry.REPLAY_AUTHORIZED_V1_BINDING_ID)
    event["launch_gate_binding"]=_runtime_binding(); event["launch_gate_pre_admit_history_digest"]=_digest_obj(_reporting_fingerprint(state))
    return atomic.encode_frame(event),event,td

def acknowledge_admit(expected_before:bytes,admit_frame:bytes,durable_readback:bytes,*,ledger_blob:bytes,adapter_module=None,replay_module=None,registry_module=None)->LaunchCapability:
    legacy=adapter_module or _default_adapter(); replay=replay_module or _default_replay(); registry=registry_module or _default_registry(); expected=bytes(expected_before)+bytes(admit_frame)
    if durable_readback!=expected: raise ReplayAuthorizedLaunchCapabilityError("durable readback does not exactly acknowledge ADMIT")
    _,event=_decode_exact_admit(expected,legacy)
    enforced,status,_exp,bid,fail=registry.resolve_admit_binding(event)
    if not enforced or fail or status!="recognized_schema_v2" or bid!=registry.REPLAY_AUTHORIZED_V1_BINDING_ID: raise ReplayAuthorizedLaunchCapabilityError("ADMIT is not recognized replay_authorized_v1")
    state=replay.recover(expected,bytes(ledger_blob))
    if state.tail_status!="clean_eof" or state.valid_len!=len(expected) or state.base.active is None or state.pending_token is None: raise ReplayAuthorizedLaunchCapabilityError("ADMIT did not replay as active")
    slots=event.get("slot_ids");
    payload={"schema_version":SCHEMA_VERSION,"block_id":str(event["block_id"]),"admit_event_id":str(event["event_id"]),"durable_prefix_len":len(expected),"durable_prefix_sha256":_digest_bytes(expected),"admit_event_digest":_digest_obj(event),"reporting_admission_digest":str(event["reporting_admission_digest"]),"admitted_slot_set_digest":_digest_obj(slots),"deadline":float(event["deadline"]),"runtime_binding_digest":_digest_obj(_runtime_binding()),"compliance_history_digest":_digest_obj(_reporting_fingerprint(state))}
    return LaunchCapability(**payload,capability_digest=_digest_obj(payload))

def admit_and_issue_capability(writer:DurableAppendWriter,main_blob:bytes,ledger_blob:bytes,**kwargs):
    frame,event,_=prepare_admit(bytes(main_blob),bytes(ledger_blob),**kwargs); durable=writer.append_fsync_readback(bytes(main_blob),frame); cap=acknowledge_admit(bytes(main_blob),frame,durable,ledger_blob=bytes(ledger_blob)); return durable,cap,event

def _verify_capability_against_blob(blob:bytes,cap:LaunchCapability,*,block_id:str,slot_id:str,adapter:Any)->None:
    _validate_capability_integrity(cap)
    if str(block_id)!=cap.block_id: raise ReplayAuthorizedLaunchCapabilityError("wrong block for capability")
    if len(blob)<cap.durable_prefix_len: raise ReplayAuthorizedLaunchCapabilityError("journal shorter than acknowledged prefix")
    prefix=bytes(blob[:cap.durable_prefix_len])
    if _digest_bytes(prefix)!=cap.durable_prefix_sha256: raise ReplayAuthorizedLaunchCapabilityError("acknowledged prefix changed")
    _,event=_decode_exact_admit(prefix,adapter)
    if _digest_obj(event)!=cap.admit_event_digest or str(event.get("event_id"))!=cap.admit_event_id: raise ReplayAuthorizedLaunchCapabilityError("ADMIT identity mismatch")
    if str(slot_id) not in {str(x) for x in event.get("slot_ids",[])}: raise ReplayAuthorizedLaunchCapabilityError("slot outside admission")
    raw=_raw_journal_state(bytes(blob),adapter)
    if raw.tail_status!="clean_eof" or raw.valid_len!=len(blob): raise ReplayAuthorizedLaunchCapabilityError("repair/quarantine torn tail before slot launch")
    if raw.base.active is None or raw.active_admit is None or str(raw.active_admit.get("event_id"))!=cap.admit_event_id or _digest_obj(raw.active_admit)!=cap.admit_event_digest: raise ReplayAuthorizedLaunchCapabilityError("capability is stale")

def prepare_slot_authorized(blob:bytes,capability:LaunchCapability,*,block_id:str,slot_id:str,score:float,observed_at:float,adapter_module=None,reporter_factory=None):
    del reporter_factory; legacy=adapter_module or _default_adapter(); _verify_capability_against_blob(bytes(blob),capability,block_id=str(block_id),slot_id=str(slot_id),adapter=legacy); atomic=legacy._default_atomic(); e=atomic.AtomicDualChannelJournal.slot_event(str(block_id),str(slot_id),float(score),float(observed_at)); return atomic.encode_frame(e),e

__all__=["SCHEMA_VERSION","LaunchCapability","ReplayAuthorizedLaunchCapabilityError","prepare_admit","acknowledge_admit","admit_and_issue_capability","prepare_slot_authorized","_verify_capability_against_blob"]
