#!/usr/bin/env python3
from __future__ import annotations
import json
import torch

RELEASE_COMMIT='9429452cb536a9e713b73b91c0011b96df44962c'
SELECTION_BLOB='5f17be7ad91bdc162a0d1e466198c1bdb2ded921'
TRAINER_BLOB='2715d5f79fd45fcbc0f7e4155d82f2042042a358'

# Source-locked executable extraction from compute_importance_mask.py at RELEASE_COMMIT.
# The statements below preserve the public release's selection semantics exactly,
# but accept in-memory state dicts so no model loading is required.
def release_select_exact(cur_sd, prev_sd, top_percent):
    float_keys = [k for k in cur_sd if k in prev_sd and torch.is_floating_point(cur_sd[k])]
    new_mask = {}
    total_params=0; total_masked_new=0
    for key in float_keys:
        diff=(cur_sd[key].float()-prev_sd[key].float()).abs()
        n=diff.numel(); total_params += n
        k=int(n*top_percent/100.0)
        if k==0: continue
        flat_diff=diff.flatten()
        top_vals, top_indices=torch.topk(flat_diff,k,largest=True,sorted=False)
        valid_mask=top_vals>0.0
        valid_indices=top_indices[valid_mask]
        actual_k=valid_indices.numel()
        if actual_k==0: continue
        m=torch.zeros(n,dtype=torch.bool); m[valid_indices]=True
        new_mask[key]=m.view(diff.shape); total_masked_new += actual_k
    return new_mask, total_params, total_masked_new

# Independent implementation retained from the previous role-local synthetic test.
def independent_per_tensor(movement, top_percent):
    masks={k: torch.zeros_like(v,dtype=torch.bool) for k,v in movement.items()}
    for name,diff in movement.items():
        n=diff.numel(); k=int(n*top_percent/100.0)
        if k<=0: continue
        vals,idx=torch.topk(diff.abs().reshape(-1),k,largest=True,sorted=False)
        idx=idx[vals>0]; masks[name].reshape(-1)[idx]=True
    return masks

# Source-locked executable extraction from CLGRPOTrainer._compute_loss ZeRO-2 branch.
# It returns exactly the pending regularizer gradients the release stores per tensor.
def release_pending_grads_exact(params, refs_selected, masks, mask_lambda=1.0, normalizer=1.0):
    pending={}; mask_loss_value=0.0
    for name,param in params.items():
        if name not in masks: continue
        flat_idx=masks[name].view(-1).nonzero(as_tuple=True)[0].to(param.device)
        ref=refs_selected[name].to(param.device,dtype=torch.float32)
        n_masked=flat_idx.numel()
        diff=param.data.view(-1)[flat_idx].float()-ref
        mask_loss_value += diff.abs().sum().item()/max(n_masked,1)
        scale=mask_lambda/max(n_masked,1)/normalizer
        pending[name]=(scale*torch.sign(diff)).detach()
    return pending, mask_lambda*mask_loss_value

# Independent autograd formulation of per-tensor-normalized masked L1.
def independent_per_tensor_loss(params, refs_full, masks, lam=1.0, normalizer=1.0):
    loss=torch.zeros((),dtype=torch.float64)
    for name,p in params.items():
        idx=masks[name].reshape(-1).nonzero(as_tuple=True)[0]
        if idx.numel()==0: continue
        diff=p.reshape(-1)[idx]-refs_full[name].reshape(-1)[idx]
        loss=loss+(lam/normalizer)/idx.numel()*diff.abs().sum()
    return loss

def main():
    selection_case={
        'small': torch.linspace(0.001,0.010,10,dtype=torch.float64),
        'medium': torch.linspace(0.001,0.100,100,dtype=torch.float64),
        'large': torch.linspace(0.001,10.0,1000,dtype=torch.float64),
    }
    prev={k:torch.zeros_like(v) for k,v in selection_case.items()}
    rel, total, selected=release_select_exact(selection_case,prev,10.0)
    indep=independent_per_tensor(selection_case,10.0)
    assert set(rel)==set(k for k,v in indep.items() if v.any())
    for k in indep:
        if indep[k].any(): assert torch.equal(rel[k],indep[k])
    counts={k:int(rel[k].sum()) for k in rel}
    assert counts=={'small':1,'medium':10,'large':100}
    assert total==1110 and selected==111

    small=torch.zeros(10,dtype=torch.float64); large=torch.zeros(90,dtype=torch.float64)
    small[0]=100.0; large[:9]=torch.linspace(50.0,42.0,9,dtype=torch.float64)
    movement={'small':small,'large':large}; prev2={k:torch.zeros_like(v) for k,v in movement.items()}
    masks,_,_=release_select_exact(movement,prev2,10.0)
    params={k:torch.ones_like(v,dtype=torch.float64,requires_grad=True) for k,v in movement.items()}
    refs_full={k:torch.zeros_like(v,dtype=torch.float64) for k,v in movement.items()}
    refs_selected={k:refs_full[k].view(-1)[masks[k].view(-1)].float().clone() for k in masks}

    release_grads, release_logged=release_pending_grads_exact(params,refs_selected,masks,mask_lambda=1.0,normalizer=1.0)
    loss=independent_per_tensor_loss(params,refs_full,masks,lam=1.0,normalizer=1.0); loss.backward()
    grad_checks={}
    for name,p in params.items():
        idx=masks[name].view(-1).nonzero(as_tuple=True)[0]
        independent_selected=p.grad.view(-1)[idx].float()
        assert torch.allclose(release_grads[name],independent_selected,atol=0,rtol=0)
        grad_checks[name]={
            'n_masked': int(idx.numel()),
            'release_per_coord_abs_grad': float(release_grads[name].abs().max()),
            'release_grad_l1': float(release_grads[name].abs().sum()),
        }
    assert abs(sum(v['release_grad_l1'] for v in grad_checks.values())-2.0)<1e-12
    assert abs(grad_checks['small']['release_per_coord_abs_grad']-1.0)<1e-12
    assert abs(grad_checks['large']['release_per_coord_abs_grad']-(1/9))<1e-6
    assert abs(float(loss.detach())-release_logged)<1e-12

    pending4,_=release_pending_grads_exact(params,refs_selected,masks,mask_lambda=1.0,normalizer=4.0)
    for name in pending4:
        assert torch.allclose(pending4[name],release_grads[name]/4.0,atol=0,rtol=0)

    out={
        'schema_version':1,
        'scope':'source-locked synthetic equivalence of release selection and ZeRO-2 regularizer gradient semantics; no model-quality claim',
        'release':{'commit':RELEASE_COMMIT,'selection_blob':SELECTION_BLOB,'trainer_blob':TRAINER_BLOB},
        'selection':{'total_float_coordinates':total,'release_selected':selected,'per_tensor_counts':counts,'matches_independent_per_tensor':True},
        'regularizer':{
            'same_support_counts':{k:int(masks[k].sum()) for k in masks},
            'per_tensor':grad_checks,
            'aggregate_coordinate_grad_l1':sum(v['release_grad_l1'] for v in grad_checks.values()),
            'release_logged_mask_loss':release_logged,
            'matches_independent_autograd':True,
            'gradient_accumulation_normalizer_4_scales_pending_grads_by_quarter':True,
        },
        'interpretation':{
            'confirmed':'The prior role-local synthetic implementation matches the public release selection semantics and the public ZeRO-2 pending-gradient semantics on the fixed cases.',
            'not_confirmed':'Training quality, ZeRO-3 distributed execution, or which semantics produced paper tables.'
        }
    }
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
