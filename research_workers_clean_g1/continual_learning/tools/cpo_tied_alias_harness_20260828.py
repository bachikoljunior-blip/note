import argparse, json, os, resource, time
import torch
from torch import nn

class Inner(nn.Module):
    def __init__(self, vocab, hidden):
        super().__init__()
        self.embed_tokens = nn.Embedding(vocab, hidden)
        self.proj = nn.Linear(hidden, hidden, bias=False)

class TinyTiedCPO(nn.Module):
    def __init__(self, vocab=8192, hidden=128):
        super().__init__()
        self.model = Inner(vocab, hidden)
        self.lm_head = nn.Linear(hidden, vocab, bias=False)
        self.lm_head.weight = self.model.embed_tokens.weight

def storage_sig(t):
    s = t.untyped_storage()
    return (int(s.data_ptr()), int(t.storage_offset()), tuple(t.shape), tuple(t.stride()), str(t.dtype))

def build_state(vocab, hidden):
    torch.manual_seed(123); prev = TinyTiedCPO(vocab, hidden)
    torch.manual_seed(123); cur = TinyTiedCPO(vocab, hidden)
    with torch.no_grad():
        torch.manual_seed(456); cur.model.embed_tokens.weight.add_(0.01 * torch.randn_like(cur.model.embed_tokens.weight))
        torch.manual_seed(789); cur.model.proj.weight.add_(0.01 * torch.randn_like(cur.model.proj.weight))
    return prev, cur, {k:v.cpu() for k,v in prev.state_dict().items()}, {k:v.cpu() for k,v in cur.state_dict().items()}

def compute_release_equiv(cur_sd, prev_sd, top_percent, dedup=False):
    float_keys=[k for k in cur_sd if k in prev_sd and torch.is_floating_point(cur_sd[k])]
    if dedup:
        seen=set(); kept=[]
        for k in float_keys:
            sig=storage_sig(cur_sd[k])
            if sig in seen: continue
            seen.add(sig); kept.append(k)
        float_keys=kept
    new_mask={}; total_params=0; total_masked=0
    for key in float_keys:
        diff=(cur_sd[key].float()-prev_sd[key].float()).abs(); n=diff.numel(); total_params += n
        k=int(n*top_percent/100.0)
        if k==0: continue
        vals,idx=torch.topk(diff.flatten(),k,largest=True,sorted=False); idx=idx[vals>0.0]
        if idx.numel()==0: continue
        m=torch.zeros(n,dtype=torch.bool); m[idx]=True; new_mask[key]=m.view(diff.shape); total_masked += idx.numel()
    ref={key:cur_sd[key].float().view(-1)[m.view(-1)].clone() for key,m in new_mask.items()}
    return float_keys,total_params,total_masked,new_mask,ref

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--mode',choices=['baseline','dedup'],required=True); ap.add_argument('--vocab',type=int,default=8192); ap.add_argument('--hidden',type=int,default=128); ap.add_argument('--top',type=float,default=10.0); ap.add_argument('--out',required=True); a=ap.parse_args()
    t0=time.perf_counter(); prev,cur,prev_sd,cur_sd=build_state(a.vocab,a.hidden); named=list(cur.named_parameters()); named_keys=[n for n,_ in named]
    keys,total_params,total_masked,masks,refs=compute_release_equiv(cur_sd,prev_sd,a.top,a.mode=='dedup'); idx={n:m.view(-1).nonzero(as_tuple=True)[0] for n,m in masks.items()}; torch.save({'masks':masks,'ref_weights':refs},a.out)
    out={'mode':a.mode,'torch_version':torch.__version__,'state_dict_keys':list(cur_sd),'named_parameter_keys':named_keys,'float_keys':keys,'builder_total_params':total_params,'builder_total_masked_new':total_masked,'mask_keys':list(masks),'mask_selected_counts':{k:int(m.sum()) for k,m in masks.items()},'trainer_consumed_mask_keys':[n for n,_ in named if n in masks],'dead_mask_keys':[k for k in masks if k not in set(named_keys)],'mask_file_bytes':os.stat(a.out).st_size,'logical_mask_bytes':sum(m.numel()*m.element_size() for m in masks.values()),'logical_ref_bytes':sum(r.numel()*r.element_size() for r in refs.values()),'logical_flat_idx_bytes':sum(i.numel()*i.element_size() for i in idx.values()),'wall_seconds':time.perf_counter()-t0,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    print(json.dumps(out,sort_keys=True))
if __name__=='__main__': main()
