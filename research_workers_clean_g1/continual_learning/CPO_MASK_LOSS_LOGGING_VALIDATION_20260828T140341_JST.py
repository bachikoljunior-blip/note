from __future__ import annotations
import json, math
import torch

SOURCE_CPO_COMMIT='9429452cb536a9e713b73b91c0011b96df44962c'
SOURCE_TRAINER_BLOB='2715d5f79fd45fcbc0f7e4155d82f2042042a358'
LAMBDA=100.0


def part(n,w,r):
    p=math.ceil(n/w)
    s=r*p
    return s,min(s+p,n)


def full_metric(params):
    x=0.0
    for cur, ref, idx in params:
        N=idx.numel()
        if N==0:
            continue
        x += (cur[idx]-ref).abs().sum().item()/N
    return LAMBDA*x


def zero3_partials(params,w):
    vals=[]
    for r in range(w):
        acc=0.0
        for cur,ref,idx in params:
            N=idx.numel()
            if N==0:
                continue
            s,t=part(cur.numel(),w,r)
            keep=(idx>=s)&(idx<t)
            if bool(keep.any()):
                acc += (cur[idx[keep]]-ref[keep]).abs().sum().item()/N
        vals.append(LAMBDA*acc)
    return vals


def release_log(partials):
    return torch.tensor(partials,dtype=torch.float64).nanmean().item()


def corrected_log(partials,zero3):
    t=torch.tensor(partials,dtype=torch.float64)
    return (t.nansum() if zero3 else t.nanmean()).item()


def make(seed):
    g=torch.Generator().manual_seed(seed)
    params=[]
    specs=[(1,0.0),(7,0.17),(19,0.43),(103,0.09),(1009,0.31),(4093,0.013)]
    for n,d in specs:
        cur=torch.randn(n,generator=g,dtype=torch.float64)
        mask=torch.rand(n,generator=g)<d
        idx=mask.nonzero(as_tuple=True)[0]
        ref=cur[idx] + torch.randn(idx.numel(),generator=g,dtype=torch.float64)*0.3
        params.append((cur,ref,idx))
    return params


def run():
    rows=[]
    corrected_mismatch=0
    ratio_mismatch=0
    z2_mismatch=0
    max_abs=0.0
    for seed in range(100):
        ps=make(1000+seed)
        target=full_metric(ps)
        for w in (1,2,3,4,8,16):
            partials=zero3_partials(ps,w)
            rel=release_log(partials)
            cor=corrected_log(partials,True)
            err=abs(cor-target)
            max_abs=max(max_abs,err)
            if err>1e-10:
                corrected_mismatch+=1
            if abs(rel-target/w)>1e-10:
                ratio_mismatch+=1
            rows.append({'seed':seed,'world_size':w,'target':target,'release':rel,'corrected':cor,'release_over_target':(rel/target if target else None),'corrected_abs_error':err})
        for w in (1,2,4,8):
            gathered=[target]*w
            cor=corrected_log(gathered,False)
            if abs(cor-target)>1e-12:
                z2_mismatch+=1
    return {
      'torch_version':torch.__version__,
      'source_cpo_commit':SOURCE_CPO_COMMIT,
      'source_trainer_blob':SOURCE_TRAINER_BLOB,
      'test_scope':'source-equivalent mask_loss aggregation only; not DeepSpeed runtime execution',
      'zero3_cases':len(rows),
      'corrected_sum_mismatch_count_tol_1e-10':corrected_mismatch,
      'release_mean_equals_full_over_world_mismatch_count_tol_1e-10':ratio_mismatch,
      'zero2_mean_mismatch_count':z2_mismatch,
      'max_corrected_abs_error':max_abs,
      'sample_seed0':[r for r in rows if r['seed']==0],
      'recommended_logging_contract':{
        'zero3':'gather rank-local partial mask_loss scalars and nansum across DP ranks',
        'zero2_or_unsharded_dp':'gather replicated full mask_loss scalars and nanmean across DP ranks',
        'training_gradient_scaling':'unchanged by this logging repair; test separately'
      }
    }

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
