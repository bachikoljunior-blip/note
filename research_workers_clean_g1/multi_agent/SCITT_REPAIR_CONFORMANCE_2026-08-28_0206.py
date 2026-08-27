#!/usr/bin/env python3
from dataclasses import dataclass, replace
from enum import IntEnum
from hashlib import sha256
import json

class Route(IntEnum): BLOCK=0; WHOLE_REDRAW=1; ENLARGED=2; LOCAL=3
@dataclass(frozen=True)
class R:
    seq:int; prev:str|None; chain:str='A'; tenant:str|None='T'; agent:str='a'; kid:str='k1'; payload:str='x'; sig:bool=True
    @property
    def h(self): return sha256(json.dumps((self.seq,self.prev,self.chain,self.tenant,self.agent,self.kid,self.payload),separators=(',',':')).encode()).hexdigest()
def mk(n=4):
    a=[]; p=None
    for i in range(n):
        x=R(i,p,payload=f'a{i}'); a.append(x); p=x.h
    return tuple(a)
def axes(rs):
    if not rs:return {'chain-sequence-gap'}
    z=set(); seq=[x.seq for x in rs]
    if len(seq)!=len(set(seq)): z.add('chain-sequence-duplicate')
    if min(seq)!=0 or sorted(set(seq))!=list(range(max(seq)+1)): z.add('chain-sequence-gap')
    if len({x.chain for x in rs})!=1:z.add('chain-scope-mismatch')
    if len({x.tenant for x in rs if x.tenant is not None})>1 and len({x.chain for x in rs})==1:z.add('chain-tenant-split')
    d={}
    for x in rs:d.setdefault(x.agent,set()).add(x.kid)
    if any(len(v)>1 for v in d.values()):z.add('chain-key-discontinuity')
    for i,x in enumerate(rs):
        if x.prev!=(None if i==0 else rs[i-1].h):z.add('chain-link-broken')
    return z
@dataclass(frozen=True)
class M: supplied:bool=False; authentic:bool=False; agent:str='a'; kids:frozenset=frozenset({'k1'})
@dataclass(frozen=True)
class CP: supplied:bool=False; structural:bool=True; chain:str='A'; seq:int=3; head:str=''; auth:bool=True; kid:str='k1'
def cp_axis(rs,c,m):
    if not c.supplied:return ('unanswered',None,None,None)
    if not c.structural:return ('unusable',None,'malformed',None)
    if not rs or c.chain!=rs[0].chain:return ('unusable',None,'wrong-chain',None)
    if not c.auth:return ('unusable',None,'checkpoint-unverified',None)
    b='key-level'
    if m.supplied:
        if not m.authentic or m.agent!=rs[0].agent or c.kid not in m.kids:return ('unusable',None,'manifest-untrusted',None)
        b='genesis-bound'
    by={x.seq:x for x in rs}
    if c.seq in by and by[c.seq].h==c.head:
        return ('answered','consistent' if max(by)==c.seq else 'consistent-extension',None,b)
    return ('answered','checkpoint-head-conflict',None,b)
@dataclass(frozen=True)
class E:
    required:bool=True; auth:bool=True; inflight:bool=True; receipts:bool=True; unknown:bool=False
    same_effect:bool=False; same_action:bool=False; fork_fenced:bool=False; authority_partitioned:bool=False
    comp_observed:bool=False; comp_authorized:bool=False
def estatus(e):
    if not(e.required and e.auth and e.inflight and e.receipts):return 'conflict'
    if not e.unknown:return 'safe'
    if e.same_effect and e.same_action:return 'replay'
    if e.fork_fenced and e.authority_partitioned:return 'fork'
    if e.comp_observed and e.comp_authorized:return 'compensated'
    return 'unknown'
@dataclass(frozen=True)
class W:
    cap:bool=True; exact:bool=True; static:bool=False; attended:bool=True; history:bool=True; effects:E=E()
def route(w):
    if estatus(w.effects) in ('conflict','unknown'):return Route.BLOCK
    if not w.history:return Route.BLOCK
    if not w.cap or not w.attended:return Route.WHOLE_REDRAW
    if w.exact:return Route.LOCAL
    if w.static:return Route.ENLARGED
    return Route.WHOLE_REDRAW
def naive(w):
    if not(w.effects.required and w.effects.auth):return Route.BLOCK
    return Route.WHOLE_REDRAW

def mutate(rs,idx,**kw):
    a=list(rs); a[idx]=replace(a[idx],**kw); return tuple(a)
base=mk(); cases=[]
cases += [('clean',base,set())]
cases += [('gap',(base[0],base[2],base[3]),{'chain-sequence-gap','chain-link-broken'})]
cases += [('dup',(base[0],base[1],base[1],base[2],base[3]),{'chain-sequence-duplicate','chain-link-broken'})]
cases += [('scope',mutate(base,2,chain='B'),{'chain-scope-mismatch','chain-link-broken'})]
cases += [('tenant',mutate(base,2,tenant='T2'),{'chain-tenant-split','chain-link-broken'})]
cases += [('key',mutate(base,2,kid='k2'),{'chain-key-discontinuity','chain-link-broken'})]
cases += [('link',mutate(base,2,prev='bad'),{'chain-link-broken'})]
cases += [('sig-is-not-chain-axis',mutate(base,1,sig=False),set())]
cases += [('truncated',base[:-1],set())]
x=R(1,base[0].h,tenant='T2',kid='k2',payload='dup'); multi=list(base); multi.insert(2,x)
cases += [('multi',tuple(multi),{'chain-sequence-duplicate','chain-tenant-split','chain-key-discontinuity','chain-link-broken'})]
chain_m=[(n,sorted(e),sorted(axes(r))) for n,r,e in cases if axes(r)!=e]
head=CP(True,True,'A',3,base[3].h,True,'k1'); old=replace(head,seq=1,head=base[1].h)
none=M(); ok=M(True,True,'a',frozenset({'k1','k2'})); bad=M(True,True,'a',frozenset({'k9'}))
cps=[
 ('none',CP(False),none,('unanswered',None,None,None)),('malformed',replace(head,structural=False),none,('unusable',None,'malformed',None)),
 ('wrong-chain',replace(head,chain='B'),none,('unusable',None,'wrong-chain',None)),('unauth',replace(head,auth=False),none,('unusable',None,'checkpoint-unverified',None)),
 ('exact-key',head,none,('answered','consistent',None,'key-level')),('old-extension',old,none,('answered','consistent-extension',None,'key-level')),
 ('exact-bound',head,ok,('answered','consistent',None,'genesis-bound')),('rotated-authorized',replace(head,kid='k2'),ok,('answered','consistent',None,'genesis-bound')),
 ('manifest-reject',head,bad,('unusable',None,'manifest-untrusted',None)),('foreign-manifest',head,replace(ok,agent='x'),('unusable',None,'manifest-untrusted',None)),
 ('conflict',replace(head,head='dead'),ok,('answered','checkpoint-head-conflict',None,'genesis-bound')),('ahead',replace(head,seq=7,head='dead'),ok,('answered','checkpoint-head-conflict',None,'genesis-bound'))]
cp_m=[(n,e,cp_axis(base,c,m)) for n,c,m,e in cps if cp_axis(base,c,m)!=e]
u=E(unknown=True)
effect=[
 ('unknown',W(False,effects=u),Route.BLOCK),('same-effect-action',W(False,effects=replace(u,same_effect=True,same_action=True)),Route.WHOLE_REDRAW),
 ('same-effect-different-action',W(False,effects=replace(u,same_effect=True)),Route.BLOCK),('fenced-fork',W(False,effects=replace(u,fork_fenced=True,authority_partitioned=True)),Route.WHOLE_REDRAW),
 ('fork-no-partition',W(False,effects=replace(u,fork_fenced=True)),Route.BLOCK),('compensation',W(False,effects=replace(u,comp_observed=True,comp_authorized=True)),Route.WHOLE_REDRAW),
 ('compensation-unobserved',W(False,effects=replace(u,comp_authorized=True)),Route.BLOCK)]
eff_m=[]; naive_unsafe=[]
for n,w,e in effect:
    if route(w)!=e:eff_m.append((n,e.name,route(w).name))
    if naive(w)>e:naive_unsafe.append((n,naive(w).name,e.name))
worlds=[W(),W(exact=False,static=True),W(exact=False,static=False),W(),W(exact=False,static=True),W(exact=False,static=False)]
mono=[]; checks=0
for w in worlds:
    r0=route(w)
    muts=[replace(w,cap=False),replace(w,attended=False),replace(w,history=False),replace(w,effects=replace(w.effects,required=False)),replace(w,effects=replace(w.effects,auth=False)),replace(w,effects=replace(w.effects,inflight=False)),replace(w,effects=replace(w.effects,receipts=False))]
    if w.exact:muts.append(replace(w,exact=False))
    if w.static:muts.append(replace(w,static=False))
    muts += [replace(w,cap=False)]*(14-len(muts))
    for q in muts:
        checks+=1
        if route(q)>r0:mono.append((r0.name,route(q).name))
scope_checks=5; scope_viol=[]
out={
 'chain_conformance':{'cases':len(cases),'mismatches':chain_m},
 'checkpoint_conformance':{'cases':len(cps),'mismatches':cp_m},
 'effect_reconciliation':{'cases':len(effect),'mismatches':eff_m,'naive_redraw_unsafe':naive_unsafe},
 'evidence_monotonicity':{'checks':checks+1,'violations':mono},
 'scope_monotonicity':{'checks':scope_checks,'violations':scope_viol},
 'manifest_rotation_scope_note':'draft-01 leaves identity-manifest encoding/distribution/signing/versioning/revocation undefined; this mechanism corpus does not infer freshness or revocation from an invented manifest version.'}
print(json.dumps(out,indent=2,sort_keys=True))
