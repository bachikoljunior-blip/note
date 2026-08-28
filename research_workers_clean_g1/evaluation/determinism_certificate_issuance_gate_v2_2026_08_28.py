"""Fixed-horizon protected-statistic replay certificate issuance gate.

This revision supersedes the v1 statistical screen for general certificate
issuance. V1 used a beta-binomial mixture that is valid under a common Bernoulli
mismatch parameter. V2 instead precommits the number of distinct challenge
attempts and uses a one-sided Hoeffding-Azuma bound for the running average of
conditional mismatch probabilities, so challenge-specific/adaptive mismatch
rates are allowed within the bounded fresh-process trial contract.

Statistical screening remains only a sanity check. Replay eligibility still
requires a separately pinned structural exactness attestation.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json, math
from typing import Any, Sequence

SCHEMA_VERSION=2
ALLOWED_PROTECTED_STATISTICS=frozenset({
    "raw_output","token_ids","score","paired_score_bits",
    "oriented_discordance_sign","custom_digest",
})
ALLOWED_PROOF_KINDS=frozenset({
    "content_addressed_pure_function",
    "verified_deterministic_runtime_contract",
})

class CertificateIssuanceError(RuntimeError): pass

def _canon(obj:Any)->bytes:
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
def _digest(obj:Any)->str:return sha256(_canon(obj)).hexdigest()
def _hex64(name:str,v:str)->str:
    v=str(v)
    if len(v)!=64 or any(c not in "0123456789abcdef" for c in v):
        raise CertificateIssuanceError(f"{name} must be lowercase sha256 hex")
    return v
def _nonempty(name:str,v:str)->str:
    v=str(v)
    if not v: raise CertificateIssuanceError(f"{name} must be nonempty")
    return v

@dataclass(frozen=True)
class RuntimeSnapshot:
    runtime_fingerprint_digest:str
    scorer_config_digest:str
    decoder_config_digest:str
    protected_statistic:str
    attempt_id_version:str
    def payload(self)->dict[str,Any]:
        _hex64("runtime_fingerprint_digest",self.runtime_fingerprint_digest)
        _hex64("scorer_config_digest",self.scorer_config_digest)
        _hex64("decoder_config_digest",self.decoder_config_digest)
        if self.protected_statistic not in ALLOWED_PROTECTED_STATISTICS:
            raise CertificateIssuanceError("unsupported protected_statistic")
        _nonempty("attempt_id_version",self.attempt_id_version)
        return asdict(self)

@dataclass(frozen=True)
class StructuralAttestation:
    snapshot:RuntimeSnapshot
    proof_kind:str
    proof_artifact_digest:str
    proof_provenance_digest:str
    invalidation_conditions:tuple[str,...]
    def payload(self)->dict[str,Any]:
        if self.proof_kind not in ALLOWED_PROOF_KINDS:
            raise CertificateIssuanceError("unsupported structural proof kind")
        _hex64("proof_artifact_digest",self.proof_artifact_digest)
        _hex64("proof_provenance_digest",self.proof_provenance_digest)
        cond=tuple(str(x) for x in self.invalidation_conditions)
        if not cond or any(not x for x in cond) or len(set(cond))!=len(cond):
            raise CertificateIssuanceError("invalidation_conditions must be unique nonempty strings")
        return {
            "snapshot":self.snapshot.payload(),
            "proof_kind":self.proof_kind,
            "proof_artifact_digest":self.proof_artifact_digest,
            "proof_provenance_digest":self.proof_provenance_digest,
            "invalidation_conditions":list(cond),
        }
    @property
    def attestation_digest(self)->str:return _digest(self.payload())

@dataclass(frozen=True)
class ChallengePair:
    challenge_id:str
    attempt_id:str
    fresh_process_id_a:str
    fresh_process_id_b:str
    protected_value_digest_a:str
    protected_value_digest_b:str
    def payload(self)->dict[str,Any]:
        for k in ("challenge_id","attempt_id","fresh_process_id_a","fresh_process_id_b"):
            _nonempty(k,getattr(self,k))
        if self.fresh_process_id_a==self.fresh_process_id_b:
            raise CertificateIssuanceError("challenge pair must use distinct fresh processes")
        _hex64("protected_value_digest_a",self.protected_value_digest_a)
        _hex64("protected_value_digest_b",self.protected_value_digest_b)
        return asdict(self)

@dataclass(frozen=True)
class IssuancePolicy:
    lifetime_false_certification_budget:float
    certificate_generation_index:int
    mismatch_tolerance:float
    planned_challenge_count:int
    require_zero_observed_mismatch:bool=True
    def alpha_for_generation(self)->float:
        A=float(self.lifetime_false_certification_budget);j=int(self.certificate_generation_index)
        if not (0<A<1):raise CertificateIssuanceError("lifetime budget must be in (0,1)")
        if j<1:raise CertificateIssuanceError("generation index must be >=1")
        if not (0<self.mismatch_tolerance<1):raise CertificateIssuanceError("mismatch_tolerance must be in (0,1)")
        if int(self.planned_challenge_count)<1:raise CertificateIssuanceError("planned_challenge_count must be >=1")
        return A/(j*(j+1))
    def payload(self)->dict[str,Any]:
        return {
            "lifetime_false_certification_budget":self.lifetime_false_certification_budget,
            "certificate_generation_index":self.certificate_generation_index,
            "generation_alpha":self.alpha_for_generation(),
            "mismatch_tolerance":self.mismatch_tolerance,
            "planned_challenge_count":int(self.planned_challenge_count),
            "require_zero_observed_mismatch":bool(self.require_zero_observed_mismatch),
            "spending_rule":"A/[j(j+1)]",
            "statistical_model":"bounded adaptive fresh-process mismatch; fixed horizon Hoeffding-Azuma for average conditional mean",
        }

def fixed_horizon_upper(n:int,s:int,alpha:float)->float:
    if n<=0:return 1.0
    if not (0<=s<=n):raise ValueError("require 0<=s<=n")
    if not (0<alpha<1):raise ValueError("alpha")
    return min(1.0,s/n+math.sqrt(math.log(1/alpha)/(2*n)))

def zero_mismatch_trials_needed(tolerance:float,alpha:float)->int:
    if not (0<tolerance<1 and 0<alpha<1):raise ValueError("range")
    return math.ceil(math.log(1/alpha)/(2*tolerance*tolerance))

def issue_certificate(*,certificate_id:str,snapshot:RuntimeSnapshot,
                      structural_attestation:StructuralAttestation,
                      challenge_pairs:Sequence[ChallengePair],
                      policy:IssuancePolicy)->dict[str,Any]:
    _nonempty("certificate_id",certificate_id)
    if structural_attestation.snapshot!=snapshot:
        raise CertificateIssuanceError("structural attestation snapshot mismatch")
    snap=snapshot.payload();att=structural_attestation.payload();pp=policy.payload()
    pairs=[p.payload() for p in challenge_pairs]
    if len(pairs)!=policy.planned_challenge_count:
        raise CertificateIssuanceError("challenge count differs from precommitted fixed horizon")
    cids=[p["challenge_id"] for p in pairs];aids=[p["attempt_id"] for p in pairs]
    if len(set(cids))!=len(cids):raise CertificateIssuanceError("duplicate challenge_id")
    if len(set(aids))!=len(aids):raise CertificateIssuanceError("each statistical trial must be a distinct attempt_id")
    procs=[x for p in pairs for x in (p["fresh_process_id_a"],p["fresh_process_id_b"])]
    if len(set(procs))!=len(procs):raise CertificateIssuanceError("fresh process identifiers are reused across challenge trials")
    mismatches=sum(p["protected_value_digest_a"]!=p["protected_value_digest_b"] for p in pairs)
    alpha=policy.alpha_for_generation();upper=fixed_horizon_upper(len(pairs),int(mismatches),alpha)
    status="certified";reason=None
    if policy.require_zero_observed_mismatch and mismatches:
        status="rejected";reason="observed_protected_statistic_mismatch"
    elif upper>policy.mismatch_tolerance:
        status="rejected";reason="fixed_horizon_average_conditional_mismatch_bound_exceeds_tolerance"
    evidence={
        "trial_unit_contract":"one distinct attempt_id, evaluated once in each of two distinct fresh process epochs",
        "planned_fixed_horizon":policy.planned_challenge_count,
        "trials":len(pairs),"mismatches":int(mismatches),
        "fixed_horizon_average_conditional_mean_upper":upper,
        "alpha":alpha,"challenge_set_digest":_digest(pairs),
    }
    out={
        "schema_version":SCHEMA_VERSION,"status":status,"reason":reason,
        "certificate_id":certificate_id,"runtime_snapshot":snap,
        "structural_attestation_digest":structural_attestation.attestation_digest,
        "structural_attestation":att,"issuance_policy":pp,
        "fresh_process_evidence":evidence,"certificate_digest":None,"certificate_payload":None,
        "validity_notes":[
            "The fixed horizon is committed before protected-statistic outcomes are observed; no optional stopping is authorized.",
            "The Hoeffding-Azuma screen targets the average conditional mismatch rate and does not require a common mismatch probability across challenge attempts.",
            "The statistical screen is not proof of exact determinism; structural attestation remains mandatory.",
            "One trial is one distinct attempt_id in two distinct fresh process epochs; all-pairs output reuse is forbidden.",
            "Generation alpha follows the summable A/[j(j+1)] lifetime schedule and is never reset.",
        ],
    }
    if status=="certified":
        payload={
            "schema_version":SCHEMA_VERSION,"certificate_id":certificate_id,
            "runtime_snapshot":snap,
            "structural_attestation_digest":structural_attestation.attestation_digest,
            "fresh_process_evidence_digest":_digest(evidence),
            "issuance_policy_digest":_digest(pp),
            "invalidation_conditions":list(structural_attestation.invalidation_conditions),
        }
        out["certificate_payload"]=payload;out["certificate_digest"]=_digest(payload)
    return out

__all__=["SCHEMA_VERSION","CertificateIssuanceError","RuntimeSnapshot","StructuralAttestation",
         "ChallengePair","IssuancePolicy","fixed_horizon_upper","zero_mismatch_trials_needed","issue_certificate"]
