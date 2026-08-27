#!/usr/bin/env python3
"""Explicit-channel repair witness mechanism study.

Synthetic/deterministic only; not a deployment failure-rate estimate.
Separates live transaction-local trusted-head evidence, checkpoint-relative tail
evidence, consistency-monitored anti-equivocation evidence, capture completeness,
dependency scope, effect/authority state, and attended model state.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from enum import IntEnum, Enum
from hashlib import sha256
import json

class Route(IntEnum):
    BLOCK=0; WHOLE_REDRAW=1; ENLARGED=2; LOCAL=3
class Mode(str, Enum):
    LIVE_LOCAL="live_local"; OFFLINE_GLOBAL="offline_global"

@dataclass(frozen=True)
class Receipt:
    seq:int; prev_hash:str|None; payload:str; scope:str="txn-A"; signature_valid:bool=True
    @property
    def digest(self):
        b=json.dumps({"seq":self.seq,"prev_hash":self.prev_hash,"payload":self.payload,"scope":self.scope},sort_keys=True,separators=(",",":")).encode()
        return sha256(b).hexdigest()

def make_chain(n=4,scope="txn-A"):
    out=[]; prev=None
    for i in range(n):
        r=Receipt(i,prev,f"action-{i}",scope,True); out.append(r); prev=r.digest
    return tuple(out)

@dataclass(frozen=True)
class Head:
    seq:int; digest:str; scope:str="txn-A"; authenticated:bool=True
@dataclass(frozen=True)
class Checkpoint:
    seq:int; digest:str; scope:str="txn-A"; authenticated:bool=True; identity_bound:bool=True
@dataclass(frozen=True)
class Transparency:
    inclusion:bool=False; consistency:bool=False; monitoring:bool=False; fork_observed:bool=False
@dataclass(frozen=True)
class Capture:
    manifest_signed:bool=True; epoch:int=7; current_epoch:int=7; topology:str="topo-v3"; current_topology:str="topo-v3"
    registered:frozenset=frozenset({"tool","message","memory","delegation","model"})
    inventory_complete:bool=True; registry_chain_complete:bool=True
    observed:frozenset=frozenset({"tool","message"}); unregistered_activity:frozenset=frozenset()
    unknown_surface_effect_capable_possible:bool=False
@dataclass(frozen=True)
class Deps:
    exact_runtime:bool=True; static_overapprox:bool=False
@dataclass(frozen=True)
class Effects:
    required_results:bool=True; authorization:bool=True; inflight_accounted:bool=True; effect_receipts:bool=True; external_effect_unknown:bool=False
@dataclass(frozen=True)
class Attended:
    committed_digest:bool=True; rebind_or_epoch:bool=True
@dataclass(frozen=True)
class World:
    mode:Mode; presented:tuple[Receipt,...]; trusted_head:Head|None; checkpoint:Checkpoint|None; transparency:Transparency
    capture:Capture; deps:Deps; effects:Effects; attended:Attended; effect_bearing:bool=True

def verify_chain(rs):
    if not rs or rs[0].seq!=0 or rs[0].prev_hash is not None: return False,None
    scope=rs[0].scope; prev=None
    for i,r in enumerate(rs):
        if not r.signature_valid or r.seq!=i or r.scope!=scope or r.prev_hash!=prev: return False,None
        prev=r.digest
    return True,Head(rs[-1].seq,rs[-1].digest,scope,True)

def checkpoint_relation(cp,rs):
    if cp is None or not cp.authenticated or not cp.identity_bound: return "unanswered"
    ok,_=verify_chain(rs)
    if not ok or cp.scope!=rs[0].scope: return "unusable"
    if cp.seq<0 or cp.seq>=len(rs) or rs[cp.seq].digest!=cp.digest: return "conflict"
    return "answered"

def anti_eq(t): return t.inclusion and t.consistency and t.monitoring and not t.fork_observed

def capture_status(c):
    if c.unregistered_activity: return "known_uncaptured"
    if not (c.manifest_signed and c.epoch==c.current_epoch and c.topology==c.current_topology and c.inventory_complete and c.registry_chain_complete): return "unknown"
    if not c.observed.issubset(c.registered): return "known_uncaptured"
    return "proved"

def history_status(w):
    ok,ph=verify_chain(w.presented)
    if not ok: return "invalid"
    if w.mode==Mode.LIVE_LOCAL:
        h=w.trusted_head
        if h is None or not h.authenticated: return "unanswered"
        if h.scope!=ph.scope or h.seq!=ph.seq or h.digest!=ph.digest: return "conflict"
        return "local_bound"
    rel=checkpoint_relation(w.checkpoint,w.presented)
    if rel!="answered": return rel
    if not anti_eq(w.transparency): return "anti_equivocation_unanswered"
    return "global_bound"

def effects_safe(w):
    e=w.effects
    if not (e.required_results and e.authorization and e.inflight_accounted and e.effect_receipts) or e.external_effect_unknown: return False
    if capture_status(w.capture)!="proved" and w.capture.unknown_surface_effect_capable_possible: return False
    return True

def split_route(w):
    if not effects_safe(w): return Route.BLOCK
    if history_status(w) not in {"local_bound","global_bound"}: return Route.BLOCK if w.effect_bearing else Route.WHOLE_REDRAW
    if capture_status(w.capture)!="proved": return Route.WHOLE_REDRAW
    if not (w.attended.committed_digest and w.attended.rebind_or_epoch): return Route.WHOLE_REDRAW
    if w.deps.exact_runtime: return Route.LOCAL
    if w.deps.static_overapprox: return Route.ENLARGED
    return Route.WHOLE_REDRAW

def overglobal_route(w):
    if not effects_safe(w): return Route.BLOCK
    if not anti_eq(w.transparency): return Route.BLOCK if w.effect_bearing else Route.WHOLE_REDRAW
    return split_route(w)

def naive_route(w):
    ok,_=verify_chain(w.presented)
    if not ok or not w.effects.required_results or not w.effects.authorization or w.effects.external_effect_unknown: return Route.BLOCK
    if w.capture.unregistered_activity and w.capture.unknown_surface_effect_capable_possible: return Route.BLOCK
    if not (w.attended.committed_digest and w.attended.rebind_or_epoch): return Route.WHOLE_REDRAW
    if w.deps.exact_runtime: return Route.LOCAL
    if w.deps.static_overapprox: return Route.ENLARGED
    return Route.WHOLE_REDRAW

chain=make_chain(); head=Head(3,chain[-1].digest); cp=Checkpoint(1,chain[1].digest)
cap=Capture(); eff=Effects(); att=Attended()
live=World(Mode.LIVE_LOCAL,chain,head,None,Transparency(),cap,Deps(),eff,att,True)
offline=World(Mode.OFFLINE_GLOBAL,chain,None,cp,Transparency(True,True,True,False),cap,Deps(),eff,att,True)
S=[]
def add(n,w,m): S.append((n,w,m))
add("live_clean_exact",live,Route.LOCAL)
add("live_clean_static",replace(live,deps=Deps(False,True)),Route.ENLARGED)
add("live_unknown_dependency",replace(live,deps=Deps(False,False)),Route.WHOLE_REDRAW)
add("live_suffix_suppression",replace(live,presented=chain[:-1]),Route.BLOCK)
fork=Receipt(3,chain[2].digest,"evil-action",chain[0].scope,True)
add("live_divergent_head",replace(live,presented=chain[:-1]+(fork,)),Route.BLOCK)
add("live_receiver_chain_gap",replace(live,presented=(chain[0],chain[1],chain[3])),Route.BLOCK)
add("live_stale_capture_epoch",replace(live,capture=replace(cap,current_epoch=8)),Route.WHOLE_REDRAW)
add("live_topology_mismatch",replace(live,capture=replace(cap,current_topology="topo-v4")),Route.WHOLE_REDRAW)
add("live_inventory_unproved_effectless",replace(live,capture=replace(cap,inventory_complete=False,unknown_surface_effect_capable_possible=False)),Route.WHOLE_REDRAW)
add("live_inventory_unproved_effectcapable",replace(live,capture=replace(cap,inventory_complete=False,unknown_surface_effect_capable_possible=True)),Route.BLOCK)
add("live_unregistered_effectless",replace(live,capture=replace(cap,unregistered_activity=frozenset({"wrapper"}),unknown_surface_effect_capable_possible=False)),Route.WHOLE_REDRAW)
add("live_unregistered_effectcapable",replace(live,capture=replace(cap,unregistered_activity=frozenset({"wrapper"}),unknown_surface_effect_capable_possible=True)),Route.BLOCK)
add("live_effect_receipt_missing",replace(live,effects=replace(eff,effect_receipts=False)),Route.BLOCK)
add("live_inflight_unknown",replace(live,effects=replace(eff,inflight_accounted=False)),Route.BLOCK)
add("live_attended_state_unbound",replace(live,attended=replace(att,rebind_or_epoch=False)),Route.WHOLE_REDRAW)
add("offline_clean_exact",offline,Route.LOCAL)
add("offline_clean_static",replace(offline,deps=Deps(False,True)),Route.ENLARGED)
add("offline_no_checkpoint",replace(offline,checkpoint=None),Route.BLOCK)
add("offline_foreign_checkpoint",replace(offline,checkpoint=replace(cp,scope="txn-B")),Route.BLOCK)
add("offline_unauthenticated_checkpoint",replace(offline,checkpoint=replace(cp,authenticated=False)),Route.BLOCK)
add("offline_checkpoint_missing_from_chain",replace(offline,checkpoint=Checkpoint(2,sha256(b"not-in-chain").hexdigest())),Route.BLOCK)
add("offline_single_transparency_inclusion",replace(offline,transparency=Transparency(True,False,False,False)),Route.BLOCK)
add("offline_consistency_without_monitor",replace(offline,transparency=Transparency(True,True,False,False)),Route.BLOCK)
add("offline_monitored_fork",replace(offline,transparency=Transparency(True,True,True,True)),Route.BLOCK)
add("offline_receiver_chain_gap",replace(offline,presented=(chain[0],chain[1],chain[3])),Route.BLOCK)
add("offline_stale_capture_epoch",replace(offline,capture=replace(cap,current_epoch=8)),Route.WHOLE_REDRAW)
add("offline_unregistered_effectcapable",replace(offline,capture=replace(cap,unregistered_activity=frozenset({"wrapper"}),unknown_surface_effect_capable_possible=True)),Route.BLOCK)

def evaluate(fn):
    unsafe=[]; conservative=[]; exact=0
    for n,w,m in S:
        r=fn(w)
        if r>m: unsafe.append((n,r.name,m.name))
        elif r<m: conservative.append((n,r.name,m.name))
        else: exact+=1
    return {"unsafe":unsafe,"conservative":conservative,"exact_count":exact}

def removals(w):
    out=[]
    if w.presented and w.presented[-1].signature_valid:
        p=list(w.presented); p[-1]=replace(p[-1],signature_valid=False); out.append(replace(w,presented=tuple(p)))
    if w.trusted_head is not None: out.append(replace(w,trusted_head=None))
    if w.checkpoint is not None:
        out += [replace(w,checkpoint=None),replace(w,checkpoint=replace(w.checkpoint,authenticated=False)),replace(w,checkpoint=replace(w.checkpoint,identity_bound=False))]
    t=w.transparency
    if t.inclusion: out.append(replace(w,transparency=replace(t,inclusion=False)))
    if t.consistency: out.append(replace(w,transparency=replace(t,consistency=False)))
    if t.monitoring: out.append(replace(w,transparency=replace(t,monitoring=False)))
    c=w.capture
    out += [replace(w,capture=replace(c,manifest_signed=False)),replace(w,capture=replace(c,current_epoch=c.current_epoch+1)),replace(w,capture=replace(c,current_topology=c.current_topology+"-x")),replace(w,capture=replace(c,inventory_complete=False)),replace(w,capture=replace(c,registry_chain_complete=False))]
    d=w.deps
    if d.exact_runtime: out.append(replace(w,deps=replace(d,exact_runtime=False)))
    if d.static_overapprox: out.append(replace(w,deps=replace(d,static_overapprox=False)))
    e=w.effects
    out += [replace(w,effects=replace(e,required_results=False)),replace(w,effects=replace(e,authorization=False)),replace(w,effects=replace(e,inflight_accounted=False)),replace(w,effects=replace(e,effect_receipts=False))]
    a=w.attended
    out += [replace(w,attended=replace(a,committed_digest=False)),replace(w,attended=replace(a,rebind_or_epoch=False))]
    return out

viol=[]; checks=0
for w in [live,replace(live,deps=Deps(False,True)),replace(live,deps=Deps(False,False)),offline,replace(offline,deps=Deps(False,True)),replace(offline,deps=Deps(False,False))]:
    r0=split_route(w)
    for w2 in removals(w):
        checks+=1
        r2=split_route(w2)
        if r2>r0: viol.append((r0.name,r2.name))

print(json.dumps({"scenario_count":len(S),"split_policy":evaluate(split_route),"overglobal_policy":evaluate(overglobal_route),"naive_policy":evaluate(naive_route),"evidence_removal_checks":checks,"evidence_monotonicity_violations":viol},indent=2,sort_keys=True))
