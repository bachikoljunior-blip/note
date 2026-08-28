"""Content-bound bootstrap for the replay-authorized v5 research runtime.

The only caller input is the role-local artifact directory. The bootstrap reads
one pinned manifest, verifies every authority artifact named by that manifest,
snapshots the provider outputs, then constructs RuntimeContext. Callers cannot
supply or override the certificate registry, runtime snapshot provider,
invalidation provider, or certificate digest.

The bootstrap manifest is the immutable authority object. This module's own Git
blob must also be pinned by the deployment/checkpoint that chooses to trust it.
"""
from __future__ import annotations
from hashlib import sha1, sha256
from pathlib import Path
import json, sys
from types import MappingProxyType
from typing import Any

SCHEMA_VERSION=1
MANIFEST_FILENAME="replay_authorization_bootstrap_manifest_v1_2026_08_28.json"
MANIFEST_GIT_BLOB="74007fa667939fe2ffb4560cba5010054f7ad0b5"
EXPECTED_BOOTSTRAP_OBJECT_DIGEST="98c5a8686715ea218f8f91ecaf7fd59fa3fbe878725882d70257301f6d0ef57e"

class BootstrapAuthorityError(RuntimeError):
    pass

def _canon(obj:Any)->bytes:
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def _git_blob(data:bytes)->str:
    return sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()

def _sha256_obj(obj:Any)->str:
    return sha256(_canon(obj)).hexdigest()

def _read_verified(path:Path, expected_blob:str)->bytes:
    data=path.read_bytes()
    got=_git_blob(data)
    if got!=expected_blob:
        raise BootstrapAuthorityError(f"Git blob mismatch for {path.name}: expected {expected_blob}, got {got}")
    return data

def _load_verified_module(path:Path, expected_blob:str, name:str):
    # Snapshot bytes first, verify them, then execute exactly that byte snapshot.
    data=_read_verified(path,expected_blob)
    mod=type(sys)(name)
    mod.__file__=str(path)
    mod.__package__=""
    sys.modules[name]=mod
    exec(compile(data,str(path),"exec"),mod.__dict__)
    return mod

class BootstrapRuntime:
    def __init__(self, root: str|Path):
        self.root=Path(root).resolve()
        manifest_bytes=_read_verified(self.root/MANIFEST_FILENAME,MANIFEST_GIT_BLOB)
        manifest=json.loads(manifest_bytes.decode("utf-8"))
        if manifest.get("schema_version")!=SCHEMA_VERSION:
            raise BootstrapAuthorityError("unsupported bootstrap manifest schema")
        bindings=manifest.get("bindings")
        if not isinstance(bindings,dict):
            raise BootstrapAuthorityError("bootstrap manifest lacks bindings")
        digest=_sha256_obj(bindings)
        if digest!=manifest.get("bootstrap_object_digest") or digest!=EXPECTED_BOOTSTRAP_OBJECT_DIGEST:
            raise BootstrapAuthorityError("bootstrap object digest mismatch")
        self._manifest=json.loads(json.dumps(manifest))
        # Verify all authority artifacts before importing anything.
        for key in ("runtime","authorization_facade","certificate_issuance_gate","trust_provider"):
            item=bindings[key]
            _read_verified(self.root/item["filename"],item["git_blob"])
        pinfo=bindings["trust_provider"]
        provider=_load_verified_module(self.root/pinfo["filename"],pinfo["git_blob"],f"_eval_bootstrap_provider_{id(self)}")
        registry=provider.trusted_registry_payload()
        runtime_snapshot=provider.runtime_snapshot_payload()
        invalidation=list(provider.triggered_invalidation_conditions())
        if _sha256_obj(registry)!=pinfo["trusted_registry_payload_sha256"]:
            raise BootstrapAuthorityError("trusted registry payload differs from manifest")
        if _sha256_obj(runtime_snapshot)!=pinfo["runtime_snapshot_payload_sha256"]:
            raise BootstrapAuthorityError("runtime snapshot payload differs from manifest")
        if _sha256_obj(invalidation)!=pinfo["triggered_invalidation_payload_sha256"]:
            raise BootstrapAuthorityError("invalidation payload differs from manifest")
        cert=bindings["issued_certificate"]
        if registry["certificates"].get(cert["certificate_id"])!=cert["certificate_digest"]:
            raise BootstrapAuthorityError("bootstrap registry does not pin issued certificate")
        # Freeze plain-data snapshots now; provider module is not consulted again.
        self._registry={
            "generation":str(registry["generation"]),
            "certificates":MappingProxyType(dict(registry["certificates"])),
            "revoked_certificate_ids":frozenset(registry.get("revoked_certificate_ids",())),
        }
        self._runtime_snapshot=MappingProxyType(dict(runtime_snapshot))
        self._invalidation=tuple(str(x) for x in invalidation)
        self._runtime_info=dict(bindings["runtime"])
        self._authority_digest=digest

    @property
    def authority_digest(self)->str:
        return self._authority_digest

    @property
    def certificate_id(self)->str:
        return str(self._manifest["bindings"]["issued_certificate"]["certificate_id"])

    def authority_summary(self)->dict[str,Any]:
        return {
            "bootstrap_object_digest":self._authority_digest,
            "manifest_git_blob":MANIFEST_GIT_BLOB,
            "runtime_git_blob":self._runtime_info["git_blob"],
            "certificate_id":self.certificate_id,
            "certificate_digest":self._manifest["bindings"]["issued_certificate"]["certificate_digest"],
            "registry_generation":self._registry["generation"],
            "runtime_snapshot_sha256":_sha256_obj(dict(self._runtime_snapshot)),
            "triggered_invalidation_conditions":list(self._invalidation),
            "caller_supplied_trust_roots":False,
        }

    def build_context(self):
        # No caller-supplied trust inputs exist in this API.
        runtime=_load_verified_module(
            self.root/self._runtime_info["filename"],
            self._runtime_info["git_blob"],
            f"_eval_bootstrap_runtime_{id(self)}",
        )
        registry={
            "generation":self._registry["generation"],
            "certificates":dict(self._registry["certificates"]),
            "revoked_certificate_ids":frozenset(self._registry["revoked_certificate_ids"]),
        }
        snapshot=dict(self._runtime_snapshot)
        invalidation=tuple(self._invalidation)
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
