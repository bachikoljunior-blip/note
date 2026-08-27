import json, torch
from torch import nn


def storage_sig(t):
    s=t.untyped_storage()
    return (int(s.data_ptr()), int(t.storage_offset()), tuple(t.shape), tuple(t.stride()), str(t.dtype))


def compute(model_cur, model_prev, top_percent=50.0, mode='release'):
    cur_sd=model_cur.state_dict(); prev_sd=model_prev.state_dict()
    keys=[k for k in cur_sd if k in prev_sd and torch.is_floating_point(cur_sd[k])]
    if mode=='storage_dedup':
        seen=set(); out=[]
        for k in keys:
            sg=storage_sig(cur_sd[k])
            if sg in seen: continue
            seen.add(sg); out.append(k)
        keys=out
    elif mode=='trainer_filter':
        allowed={n for n,p in model_cur.named_parameters(remove_duplicate=True) if torch.is_floating_point(p)}
        prev_allowed={n for n,p in model_prev.named_parameters(remove_duplicate=True) if torch.is_floating_point(p)}
        allowed &= prev_allowed
        keys=[k for k in keys if k in allowed]
    masks={}
    for k in keys:
        d=(cur_sd[k].float()-prev_sd[k].float()).abs().flatten(); n=d.numel(); count=int(n*top_percent/100)
        if count<=0: continue
        vals,idx=torch.topk(d,count,largest=True,sorted=False); idx=idx[vals>0]
        if idx.numel():
            m=torch.zeros(n,dtype=torch.bool); m[idx]=1; masks[k]=m.view(cur_sd[k].shape)
    named=[n for n,p in model_cur.named_parameters(remove_duplicate=True) if torch.is_floating_point(p)]
    return {'candidate_keys':keys,'mask_keys':list(masks),'trainer_keys':named,'trainer_consumed':[n for n in named if n in masks], 'dead_mask_keys':[k for k in masks if k not in set(named)]}


class Tied(nn.Module):
    def __init__(self):
        super().__init__(); self.a=nn.Linear(4,4,bias=False); self.b=nn.Linear(4,4,bias=False); self.b.weight=self.a.weight


class DistinctSameStorage(nn.Module):
    def __init__(self):
        super().__init__(); x=torch.zeros(4,4); self.p=nn.Parameter(x); self.q=nn.Parameter(self.p.data)


class ParamBuffer(nn.Module):
    def __init__(self):
        super().__init__(); self.p=nn.Parameter(torch.zeros(4,4)); self.register_buffer('buf',torch.zeros(4,4),persistent=True)


def pair(cls):
    a=cls(); b=cls()
    with torch.no_grad():
        if isinstance(b,Tied): b.a.weight.add_(1)
        elif isinstance(b,DistinctSameStorage): b.p.add_(1)
        elif isinstance(b,ParamBuffer): b.p.add_(1); b.buf.add_(1)
    return a,b


out={'torch_version':torch.__version__,'top_percent':50.0,'cases':{}}
for cls in [Tied,DistinctSameStorage,ParamBuffer]:
    prev,cur=pair(cls)
    out['cases'][cls.__name__]={m:compute(cur,prev,mode=m) for m in ['release','storage_dedup','trainer_filter']}
    out['cases'][cls.__name__]['named_parameters_all']=[n for n,_ in cur.named_parameters(remove_duplicate=False)]
    out['cases'][cls.__name__]['named_parameters_dedup']=[n for n,_ in cur.named_parameters(remove_duplicate=True)]
print(json.dumps(out,indent=2,sort_keys=True))
