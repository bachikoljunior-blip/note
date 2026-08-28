#!/usr/bin/env python3
"""
Source-equivalent algebra test for MaolinLuo/CPO public ZeRO-3 mask regularizer.

Scope:
- Reproduces the public grpo_trainer_cl.py partition/filter/diff/sign algebra after
  tensors are on the same device.
- Compares the current "global idx/ref then filter each step" calculation against
  a repair that prepartitions idx/ref once per rank while preserving the GLOBAL
  masked-count denominator.
- Does not emulate DeepSpeed hooks/reduce-scatter, bus traffic, or PyTorch 2.8.
"""
import math
import random
import torch

SEED = 826
TRIALS = 1000

def current_pending(full_data, flat_idx, ref, world_size, rank, lam, normalizer):
    n = full_data.numel()
    part = math.ceil(n / world_size)
    start = rank * part
    end = min(start + part, n)
    if start >= end:
        return torch.empty(0, dtype=torch.long), torch.empty(0), 0.0
    inpart = (flat_idx >= start) & (flat_idx < end)
    if not bool(inpart.any()):
        return torch.empty(0, dtype=torch.long), torch.empty(0), 0.0
    global_idx = flat_idx[inpart]
    local_idx = global_idx - start
    ref_local = ref[inpart]
    local_data = full_data[start:end].float()
    diff = local_data[local_idx] - ref_local
    n_masked = flat_idx.numel()
    loss_partial = diff.abs().sum().item() / max(n_masked, 1)
    scale = lam / max(n_masked, 1) / normalizer
    grad = (scale * torch.sign(diff)).detach().cpu()
    return global_idx.cpu(), grad, loss_partial

def prepartition_once(flat_idx, ref, n, world_size):
    part = math.ceil(n / world_size)
    out = []
    for rank in range(world_size):
        start = rank * part
        end = min(start + part, n)
        inpart = (flat_idx >= start) & (flat_idx < end)
        out.append((
            flat_idx[inpart].cpu().clone(),
            ref[inpart].cpu().clone(),
            start,
            end,
        ))
    return out

def ranklocal_pending(full_data, rank_entry, global_n_masked, lam, normalizer):
    global_idx, ref_local, start, end = rank_entry
    if global_idx.numel() == 0 or start >= end:
        return torch.empty(0, dtype=torch.long), torch.empty(0), 0.0
    local_idx = global_idx - start
    local_data = full_data[start:end].float()
    diff = local_data[local_idx] - ref_local
    loss_partial = diff.abs().sum().item() / max(global_n_masked, 1)
    scale = lam / max(global_n_masked, 1) / normalizer
    grad = (scale * torch.sign(diff)).detach().cpu()
    return global_idx.clone(), grad, loss_partial

def main():
    random.seed(SEED)
    torch.manual_seed(SEED)
    rank_cases = 0
    failures = []
    coverage_failures = []
    loss_failures = []
    edge = {
        "zero_support": 0,
        "nondivisible": 0,
        "empty_rank_partition": 0,
        "zero_diff": 0,
        "boundary_hits": 0,
    }

    for trial in range(TRIALS):
        n = random.randint(1, 20000)
        world = random.randint(1, 16)
        support_n = random.randint(0, min(n, max(1, int(n * 0.4))))
        idx = torch.sort(torch.randperm(n)[:support_n]).values.long()
        base = torch.randn(n)
        current = base + 0.1 * torch.randn(n)
        if support_n and random.random() < 0.4:
            zcount = random.randint(1, support_n)
            zsel = idx[torch.randperm(support_n)[:zcount]]
            current[zsel] = base[zsel]
            edge["zero_diff"] += 1
        ref = base[idx].float().clone()
        lam = random.choice([0.0, 0.5, 1.0, 100.0])
        normalizer = random.choice([1.0, 2.0, 4.0, 8.0])

        pre = prepartition_once(idx, ref, n, world)
        union = []
        for rank in range(world):
            a = current_pending(current, idx, ref, world, rank, lam, normalizer)
            b = ranklocal_pending(current, pre[rank], idx.numel(), lam, normalizer)
            rank_cases += 1
            if not torch.equal(a[0], b[0]) or not torch.equal(a[1], b[1]):
                failures.append((trial, rank, n, world, support_n))
            if a[2] != b[2]:
                loss_failures.append((trial, rank, a[2], b[2]))
            union.append(b[0])

        cat = torch.cat(union) if union else torch.empty(0, dtype=torch.long)
        if not torch.equal(cat, idx):
            coverage_failures.append((trial, n, world, support_n))

        if support_n == 0:
            edge["zero_support"] += 1
        if n % world:
            edge["nondivisible"] += 1
        if world > n:
            edge["empty_rank_partition"] += 1
        part = math.ceil(n / world)
        boundaries = {k * part for k in range(1, world)}
        if any(int(i) in boundaries for i in idx):
            edge["boundary_hits"] += 1

    print({
        "torch_version": torch.__version__,
        "trials": TRIALS,
        "rank_cases": rank_cases,
        "bitwise_failures": len(failures),
        "partial_loss_failures": len(loss_failures),
        "partition_coverage_failures": len(coverage_failures),
        "edge_stats": edge,
    })

if __name__ == "__main__":
    main()
