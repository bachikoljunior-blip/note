"""Evidence-bound bootstrap for replay-authorized v5 research runtime.

This loader binds certificate issuance evidence, the trust provider, and the v5
runtime into one immutable manifest. It rederives the certificate payload digest,
fixed-horizon screening contract, and provider/runtime-snapshot consistency
before constructing RuntimeContext. Callers cannot supply trust roots.

Research scope: the bundled provider is a static toy fixture. Production needs a
verified live runtime/invalidation provider and an independently justified
structural determinism attestation.
"""
from __future__ import annotations
from hashlib import sha1, sha256
from pathlib import Path
import json, math, sys
from types import MappingProxyType
from typing import Any

SCHEMA_VERSION=2
MANIFEST_FILENAME="replay_authorization_bootstrap_manifest_v2_2026_08_28.json"
MANIFEST_GIT_BLOB="070cad3e8a66c3bd90e3b2b3d65f207c1adc9f83"
EXPECTED_BOOTSTRAP_OBJECT_DIGEST="d643b3900e82ec61c87b307571dac9fd1b33d2f1ea61dafaa6f6b4b425322a84"

class BootstrapAuthorityError(RuntimeError):pass

def _canon(obj:Any)->bytes:
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
def _git_blob(data:bytes)->str:
    return sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()
def _sha256_obj(obj:Any)->str:return sha256(_canon(obj)).hexdigest()

def _read_verified(path:Path,expected_blob:str)->bytes:
    data=path.read_bytes();got=_git_blob(data)
    if got!=expected_blob:
        raise BootstrapAuthorityError(f"Git blob mismatch for {path.name}: expected {expected_blob}, got {got}")
    return data

def _load_verified_module(path:Path,expected_blob:str,name:str):
    data=_read_verified(path,expected_blob)
    mod=type(sys)(name);mod.__file__=str(path);mod.__package__=""
    sys.modules[name]=mod;exec(compile(data,str(path),"exec"),mod.__dict__);return mod

def _verify_certificate_record(raw:bytes,bindings:dict[str,Any])->dict[str,Any]:
    doc=json.loads(raw.decode("utf-8"))
    if doc.get("schema_version")!=2 or not isinstance(doc.get("record"),dict):
        raise BootstrapAuthorityError("unsupported certificate record")
    record=doc["record"]
    if record.get("schema_version")!=2:
        raise BootstrapAuthorityError("unsupported certificate record payload schema")
    if _sha256_obj(record)!=doc.get("record_digest"):
        raise BootstrapAuthorityError("certificate record digest mismatch")
    cinfo=bindings["certificate_record"]
    if doc.get("record_digest")!=cinfo["record_digest"]:
        raise BootstrapAuthorityError("certificate record differs from bootstrap manifest")
    issued=bindings["issued_certificate"]
    for key in ("certificate_id","certificate_digest","structural_attestation_digest"):
        if record.get(key)!=issued[key]:
            raise BootstrapAuthorityError(f"certificate record {key} mismatch")
    if record.get("issuance_gate_git_blob")!=bindings["certificate_issuance_gate"]["git_blob"]:
        raise BootstrapAuthorityError("certificate record was not issued by pinned gate")
    evidence=record.get("fresh_process_evidence");policy=record.get("issuance_policy")
    if not isinstance(evidence,dict) or not isinstance(policy,dict):
        raise BootstrapAuthorityError("certificate record lacks issuance evidence")
    if int(evidence.get("mismatches",-1))!=0:
        raise BootstrapAuthorityError("certificate record contains observed protected-statistic mismatch")
    planned=int(policy.get("planned_challenge_count",-1))
    if planned<1 or int(evidence.get("planned_fixed_horizon",-2))!=planned or int(evidence.get("trials",-3))!=planned:
        raise BootstrapAuthorityError("certificate fixed horizon was not honored")
    A=float(policy.get("lifetime_false_certification_budget",0.0));j=int(policy.get("certificate_generation_index",0))
    if not (0<A<1) or j<1:
        raise BootstrapAuthorityError("invalid lifetime certificate budget")
    alpha_expected=A/(j*(j+1))
    if not math.isclose(float(policy.get("generation_alpha",-1)),alpha_expected,rel_tol=0,abs_tol=1e-15):
        raise BootstrapAuthorityError("certificate generation alpha does not match lifetime spending rule")
    if not math.isclose(float(evidence.get("alpha",-1)),alpha_expected,rel_tol=0,abs_tol=1e-15):
        raise BootstrapAuthorityError("evidence alpha does not match issuance policy")
    upper=float(evidence.get("fixed_horizon_average_conditional_mean_upper",1.0))
    tolerance=float(policy.get("mismatch_tolerance",0.0))
    if not upper<=tolerance:
        raise BootstrapAuthorityError("certificate mismatch bound exceeds tolerance")
    if policy.get("require_zero_observed_mismatch") is not True:
        raise BootstrapAuthorityError("certificate does not require zero observed mismatch")
    payload=record.get("certificate_payload")
    if not isinstance(payload,dict) or _sha256_obj(payload)!=record.get("certificate_digest"):
        raise BootstrapAuthorityError("certificate payload digest mismatch")
    if payload.get("runtime_snapshot")!=record.get("runtime_snapshot"):
        raise BootstrapAuthorityError("certificate payload/runtime snapshot mismatch")
    if payload.get("structural_attestation_digest")!=record.get("structural_attestation_digest"):
        raise BootstrapAuthorityError("certificate payload/attestation mismatch")
    if payload.get("fresh_process_evidence_digest")!=_sha256_obj(evidence):
        raise BootstrapAuthorityError("certificate payload/evidence digest mismatch")
    if payload.get("issuance_policy_digest")!=_sha256_obj(policy):
        raise BootstrapAuthorityError("certificate payload/policy digest mismatch")
    return record

class BootstrapRuntime:
    def __init__(self,root:str|Path):
        self.root=Path(root).resolve()
        mbytes=_read_verified(self.root/MANIFEST_FILENAME,MANIFEST_GIT_BLOB)
        manifest=json.loads(mbytes.decode("utf-8"))
        if manifest.get("schema_version")!=SCHEMA_VERSION:
            raise BootstrapAuthorityError("unsupported bootstrap manifest schema")
        bindings=manifest.get("bindings")
        if not isinstance(bindings,dict):
            raise BootstrapAuthorityError("bootstrap manifest lacks bindings")
        digest=_sha256_obj(bindings)
        if digest!=manifest.get("bootstrap_object_digest") or digest!=EXPECTED_BOOTSTRAP_OBJECT_DIGEST:
            raise BootstrapAuthorityError("bootstrap object digest mismatch")
        self._manifest=json.loads(json.dumps(manifest))
        for key in ("runtime","authorization_facade","certificate_issuance_gate","trust_provider","certificate_record"):
            item=bindings[key];_read_verified(self.root/item["filename"],item["git_blob"])
        record_raw=_read_verified(self.root/bindings["certificate_record"]["filename"],bindings["certificate_record"]["git_blob"])
        record=_verify_certificate_record(record_raw,bindings)
        pinfo=bindings["trust_provider"]
        provider=_load_verified_module(self.root/pinfo["filename"],pinfo["git_blob"],f"_eval_bootstrap_provider_v2_{id(self)}")
        registry=provider.trusted_registry_payload();snapshot=provider.runtime_snapshot_payload()
        invalidation=list(provider.triggered_invalidation_conditions())
        if _sha256_obj(registry)!=pinfo["trusted_registry_payload_sha256"]:
            raise BootstrapAuthorityError("trusted registry payload differs from manifest")
        if _sha256_obj(snapshot)!=pinfo["runtime_snapshot_payload_sha256"]:
            raise BootstrapAuthorityError("runtime snapshot payload differs from manifest")
        if _sha256_obj(invalidation)!=pinfo["triggered_invalidation_payload_sha256"]:
            raise BootstrapAuthorityError("invalidation payload differs from manifest")
        cid=record["certificate_id"];cdig=record["certificate_digest"]
        if registry["certificates"].get(cid)!=cdig:
            raise BootstrapAuthorityError("provider registry does not pin evidence-bound certificate")
        if snapshot!=record["runtime_snapshot"]:
            raise BootstrapAuthorityError("provider runtime snapshot differs from certificate record")
        self._registry={
            "generation":str(registry["generation"]),
            "certificates":MappingProxyType(dict(registry["certificates"])),
            "revoked_certificate_ids":frozenset(registry.get("revoked_certificate_ids",())),
        }
        self._runtime_snapshot=MappingProxyType(dict(snapshot))
        self._invalidation=tuple(str(x) for x in invalidation)
        self._runtime_info=dict(bindings["runtime"]);self._record=json.loads(json.dumps(record))
        self._authority_digest=digest

    @property
    def authority_digest(self)->str:return self._authority_digest

    def authority_summary(self)->dict[str,Any]:
        return {
            "bootstrap_object_digest":self._authority_digest,
            "manifest_git_blob":MANIFEST_GIT_BLOB,
            "runtime_git_blob":self._runtime_info["git_blob"],
            "certificate_record_git_blob":self._manifest["bindings"]["certificate_record"]["git_blob"],
            "certificate_record_digest":self._manifest["bindings"]["certificate_record"]["record_digest"],
            "certificate_id":self._record["certificate_id"],
            "certificate_digest":self._record["certificate_digest"],
            "registry_generation":self._registry["generation"],
            "caller_supplied_trust_roots":False,
        }

    def build_context(self):
        runtime=_load_verified_module(self.root/self._runtime_info["filename"],self._runtime_info["git_blob"],f"_eval_bootstrap_runtime_v2_{id(self)}")
        registry={
            "generation":self._registry["generation"],
            "certificates":dict(self._registry["certificates"]),
            "revoked_certificate_ids":frozenset(self._registry["revoked_certificate_ids"]),
        }
        snapshot=dict(self._runtime_snapshot);invalidation=tuple(self._invalidation)
        ctx=runtime.RuntimeContext(
            trusted_registry=registry,
            runtime_snapshot_provider=lambda:dict(snapshot),
            invalidation_provider=lambda:tuple(invalidation),
        )
        if ctx.authorization_root_digest is None:
            raise BootstrapAuthorityError("runtime context did not accept bootstrap registry")
        return ctx

__all__=["SCHEMA_VERSION","MANIFEST_FILENAME","MANIFEST_GIT_BLOB",
         "EXPECTED_BOOTSTRAP_OBJECT_DIGEST","BootstrapAuthorityError","BootstrapRuntime"]
