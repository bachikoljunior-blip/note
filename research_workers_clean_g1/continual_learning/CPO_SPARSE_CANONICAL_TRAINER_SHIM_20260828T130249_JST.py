from __future__ import annotations
import hashlib,json,math
from typing import Any,Mapping
import torch

FORMAT='cpo_sparse_canonical_shim_v1'

def _dtype(t): return str(t.dtype).replace('torch.','')
def namespace(model):
    return [{'name':n,'shape':list(p.shape),'numel':p.numel(),'dtype':_dtype(p)} for n,p in model.named_parameters(recurse=True,remove_duplicate=True)]
def digest(rows): return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def part(n,w,r):
    p=math.ceil(n/w); s=r*p; return p,s,min(s+p,n)

def convert(model,raw):
    rows=namespace(model); canon={x['name']:x for x in rows}; out={}; dropped=[]
    for n,m in raw['masks'].items():
        if n not in canon: dropped.append(n); continue
        row=canon[n]
        if m.dtype!=torch.bool or list(m.shape)!=row['shape'] or n not in raw['ref_weights']: raise ValueError(n)
        idx=m.reshape(-1).nonzero(as_tuple=True)[0].cpu().clone(); ref=raw['ref_weights'][n].reshape(-1).cpu().float().clone()
        if ref.numel()!=idx.numel() or (idx.numel()>1 and not bool(torch.all(idx[1:]>idx[:-1]))): raise ValueError(n)
        out[n]={'shape':row['shape'],'numel':row['numel'],'dtype':row['dtype'],'idx':idx,'ref':ref,'global_n':idx.numel()}
    return {'format':FORMAT,'namespace':rows,'namespace_sha256':digest(rows),'parameters':out,'dropped_noncanonical':sorted(dropped)}

def prepartition(model,artifact,w,r,zero3):
    rows=namespace(model)
    if digest(rows)!=artifact['namespace_sha256']: raise RuntimeError('namespace drift')
    params=dict(model.named_parameters(recurse=True,remove_duplicate=True)); out={}
    for n,e in artifact['parameters'].items():
        p=params[n]; numel=p.numel()
        if e['shape']!=list(p.shape) or e['numel']!=numel or e['dtype']!=_dtype(p): raise RuntimeError(n)
        if zero3 and (not hasattr(p,'ds_numel') or not hasattr(p,'ds_tensor') or int(p.ds_numel)!=numel): raise RuntimeError(n)
        P,s,t=part(numel,w,r); idx=e['idx']
        lo=int(torch.searchsorted(idx,torch.tensor(s,dtype=idx.dtype))); hi=int(torch.searchsorted(idx,torch.tensor(t,dtype=idx.dtype)))
        gidx=idx[lo:hi].clone(); ref=e['ref'][lo:hi].clone()
        out[n]={'gidx':gidx,'lidx':(gidx-s).clone(),'ref':ref,'global_n':e['global_n'],'start':s,'end':t,'partition_size':P}
    return out

class SparseCanonicalCPOCore:
    '''Drop-in mask-state core preserving released CPO scaling. No world-size correction is applied.'''
    def __init__(self,model,raw,mask_lambda,world_size=1,rank=0,zero3=False):
        self.model=model; self.mask_lambda=float(mask_lambda); self.zero3=zero3
        self.artifact=convert(model,raw); self.local=prepartition(model,self.artifact,world_size,rank,zero3); self.pending={}
    def compute(self,normalizer):
        self.pending.clear(); loss=0.; params=dict(self.model.named_parameters(recurse=True,remove_duplicate=True))
        for n,s in self.local.items():
            p=params[n]; N=s['global_n']
            if not p.requires_grad or N==0: continue
            scale=self.mask_lambda/N/normalizer
            if self.zero3:
                if s['lidx'].numel()==0: continue
                d=p.ds_tensor.to(p.device).float().reshape(-1)[s['lidx'].to(p.device)]-s['ref'].to(p.device)
                loss+=d.abs().sum().item()/N
                self.pending[n]={'global_idx':s['gidx'].cpu(),'grad':(scale*torch.sign(d)).detach().cpu()}
            else:
                e=self.artifact['parameters'][n]; idx=e['idx'].to(p.device); d=p.data.reshape(-1)[idx].float()-e['ref'].to(p.device)
                loss+=d.abs().sum().item()/N; self.pending[n]=(scale*torch.sign(d)).detach()
        return loss
    def hook(self,name,grad):
        if name not in self.pending: return grad
        x=self.pending[name]
        if isinstance(x,dict):
            idx=x['global_idx'].to(grad.device); g=x['grad'].to(grad.device,dtype=grad.dtype); out=grad.clone().reshape(-1); out[idx]+=g; return out.reshape_as(grad)
        idx=self.artifact['parameters'][name]['idx'].to(grad.device); add=torch.zeros(grad.numel(),dtype=grad.dtype,device=grad.device); add[idx]=x.to(grad.dtype); return grad+add.reshape_as(grad)

def _reference(model,raw,lam,norm,w,r,zero3):
    masks=raw['masks']; refs={k:v.float() for k,v in raw['ref_weights'].items()}; idxs={k:v.reshape(-1).nonzero(as_tuple=True)[0] for k,v in masks.items()}; pending={}; loss=0.
    for n,p in model.named_parameters(recurse=True,remove_duplicate=True):
        if n not in masks or not p.requires_grad: continue
        idx=idxs[n].to(p.device); ref=refs[n].to(p.device); N=idx.numel()
        if zero3:
            _,s,t=part(int(p.ds_numel),w,r); keep=(idx>=s)&(idx<t)
            if not bool(keep.any()): continue
            gidx=idx[keep]; d=p.ds_tensor.to(p.device).float().reshape(-1)[gidx-s]-ref[keep]; loss+=d.abs().sum().item()/max(N,1); pending[n]={'global_idx':gidx.cpu(),'grad':(lam/max(N,1)/norm*torch.sign(d)).cpu()}
        else:
            d=p.data.reshape(-1)[idx].float()-ref; loss+=d.abs().sum().item()/max(N,1); pending[n]=(lam/max(N,1)/norm*torch.sign(d)).detach()
    return pending,loss

def self_test():
    class M(torch.nn.Module):
        def __init__(self):
            super().__init__(); x=torch.nn.Parameter(torch.randn(17,5)); self.e=x; self.h=x; self.p=torch.nn.Parameter(torch.randn(5,7)); self.register_buffer('buf',torch.randn(9))
    mismatch=0; cases=hooks=0
    for seed in range(12):
        m=M(); gen=torch.Generator().manual_seed(seed+900); raw={'masks':{},'ref_weights':{}}
        canon=set(dict(m.named_parameters(recurse=True,remove_duplicate=True)))
        for n,t in m.state_dict().items():
            q=torch.rand(t.shape,generator=gen)<((seed+1)/20); raw['masks'][n]=q; ii=q.reshape(-1).nonzero(as_tuple=True)[0]; raw['ref_weights'][n]=t.reshape(-1)[ii].float()+torch.randn(ii.numel(),generator=gen)*.2
        for zero3 in (False,True):
            for w in ((1,) if not zero3 else (1,2,3,4,8)):
                for r in range(w):
                    if zero3:
                        for _,p in m.named_parameters(recurse=True,remove_duplicate=True):
                            P,s,t=part(p.numel(),w,r); z=torch.zeros(P,dtype=p.dtype); z[:max(t-s,0)]=p.detach().reshape(-1)[s:t]; p.ds_numel=p.numel(); p.ds_tensor=z
                    exp,el=_reference(m,raw,100.,3.,w,r,zero3); core=SparseCanonicalCPOCore(m,raw,100.,w,r,zero3); gl=core.compute(3.)
                    mismatch+=int(el!=gl or set(exp)!=set(core.pending))
                    for n,x in exp.items():
                        y=core.pending[n]
                        if isinstance(x,dict): mismatch+=int(not torch.equal(x['global_idx'],y['global_idx']) or not torch.equal(x['grad'],y['grad']))
                        else: mismatch+=int(not torch.equal(x,y))
                        p=dict(m.named_parameters(recurse=True,remove_duplicate=True))[n]; g=torch.randn_like(p)
                        if isinstance(x,dict): eo=g.clone().reshape(-1); eo[x['global_idx']]+=x['grad'].to(g.dtype); eo=eo.reshape_as(g)
                        else:
                            ii=raw['masks'][n].reshape(-1).nonzero(as_tuple=True)[0]; a=torch.zeros(g.numel()); a[ii]=x.to(g.dtype); eo=g+a.reshape_as(g)
                        mismatch+=int(not torch.equal(eo,core.hook(n,g))); hooks+=1
                    cases+=1
    return {'torch_version':torch.__version__,'source_cpo_commit':'9429452cb536a9e713b73b91c0011b96df44962c','source_trainer_blob':'2715d5f79fd45fcbc0f7e4155d82f2042042a358','cases':cases,'hook_comparisons':hooks,'mismatch_count':mismatch}
if __name__=='__main__': print(json.dumps(self_test(),indent=2))
