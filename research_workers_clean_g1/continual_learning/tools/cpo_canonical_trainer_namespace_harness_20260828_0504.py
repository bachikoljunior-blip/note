import json
import torch
from torch import nn


def public_release_compute(model_cur, model_prev, top_percent=50.0, previous_saved=None):
    """Source-equivalent to CPO release per-tensor mask/ref behavior for small fixtures."""
    cur_sd = model_cur.state_dict()
    prev_sd = model_prev.state_dict()
    float_keys = [k for k in cur_sd if k in prev_sd and torch.is_floating_point(cur_sd[k])]
    masks = {}
    for key in float_keys:
        diff = (cur_sd[key].float() - prev_sd[key].float()).abs()
        n = diff.numel()
        k = int(n * top_percent / 100.0)
        if k == 0:
            continue
        vals, idx = torch.topk(diff.flatten(), k, largest=True, sorted=False)
        idx = idx[vals > 0]
        if idx.numel():
            m = torch.zeros(n, dtype=torch.bool)
            m[idx] = True
            masks[key] = m.view(diff.shape)
    if previous_saved:
        prev_mask = previous_saved["masks"] if isinstance(previous_saved, dict) and "masks" in previous_saved else previous_saved
        for key, pm in prev_mask.items():
            masks[key] = (masks[key] | pm) if key in masks else pm.clone()
    refs = {}
    for key, m in masks.items():
        if key in cur_sd:
            refs[key] = cur_sd[key].float().view(-1)[m.view(-1)].clone()
    return {"masks": masks, "ref_weights": refs}


def canonical_param_map(model):
    return {
        name: p
        for name, p in model.named_parameters(remove_duplicate=True)
        if torch.is_floating_point(p)
    }


def trainer_namespace_compute(model_cur, model_prev, top_percent=50.0, previous_saved=None):
    """
    Repair candidate:
      * exactly mirror trainer canonical named_parameters(remove_duplicate=True) namespace;
      * fail closed on namespace/order/shape/dtype mismatch;
      * ignore accumulated legacy mask entries that no canonical trainer parameter can consume;
      * do not deduplicate by storage identity.
    """
    cur_params = canonical_param_map(model_cur)
    prev_params = canonical_param_map(model_prev)
    cur_names = list(cur_params)
    prev_names = list(prev_params)
    if cur_names != prev_names:
        raise ValueError(f"canonical namespace/order mismatch: cur={cur_names}, prev={prev_names}")

    cur_sd = model_cur.state_dict()
    prev_sd = model_prev.state_dict()
    for name in cur_names:
        if name not in cur_sd or name not in prev_sd:
            raise ValueError(f"canonical parameter missing from state_dict: {name}")
        if tuple(cur_params[name].shape) != tuple(prev_params[name].shape):
            raise ValueError(
                f"shape mismatch {name}: {tuple(cur_params[name].shape)} != {tuple(prev_params[name].shape)}"
            )
        if cur_params[name].dtype != prev_params[name].dtype:
            raise ValueError(
                f"dtype mismatch {name}: {cur_params[name].dtype} != {prev_params[name].dtype}"
            )
        if tuple(cur_sd[name].shape) != tuple(cur_params[name].shape):
            raise ValueError(f"current state_dict/parameter shape mismatch: {name}")
        if tuple(prev_sd[name].shape) != tuple(prev_params[name].shape):
            raise ValueError(f"previous state_dict/parameter shape mismatch: {name}")
        if cur_sd[name].dtype != cur_params[name].dtype:
            raise ValueError(f"current state_dict/parameter dtype mismatch: {name}")
        if prev_sd[name].dtype != prev_params[name].dtype:
            raise ValueError(f"previous state_dict/parameter dtype mismatch: {name}")

    masks = {}
    for name in cur_names:
        diff = (cur_sd[name].float() - prev_sd[name].float()).abs()
        n = diff.numel()
        k = int(n * top_percent / 100.0)
        if k == 0:
            continue
        vals, idx = torch.topk(diff.flatten(), k, largest=True, sorted=False)
        idx = idx[vals > 0]
        if idx.numel():
            m = torch.zeros(n, dtype=torch.bool)
            m[idx] = True
            masks[name] = m.view(diff.shape)

    ignored_previous_noncanonical = []
    if previous_saved:
        prev_mask = previous_saved["masks"] if isinstance(previous_saved, dict) and "masks" in previous_saved else previous_saved
        for name, pm in prev_mask.items():
            if name not in cur_params:
                ignored_previous_noncanonical.append(name)
                continue
            if tuple(pm.shape) != tuple(cur_params[name].shape):
                raise ValueError(
                    f"previous mask shape mismatch {name}: {tuple(pm.shape)} != {tuple(cur_params[name].shape)}"
                )
            masks[name] = (masks[name] | pm) if name in masks else pm.clone()

    refs = {
        name: cur_sd[name].float().view(-1)[mask.view(-1)].clone()
        for name, mask in masks.items()
    }
    return {
        "masks": masks,
        "ref_weights": refs,
        "canonical_names": cur_names,
        "ignored_previous_noncanonical": ignored_previous_noncanonical,
    }


class TiedAB(nn.Module):
    def __init__(self):
        super().__init__()
        self.a = nn.Linear(4, 4, bias=False)
        self.b = nn.Linear(4, 4, bias=False)
        self.b.weight = self.a.weight


class TiedBA(nn.Module):
    def __init__(self):
        super().__init__()
        self.b = nn.Linear(4, 4, bias=False)
        self.a = nn.Linear(4, 4, bias=False)
        self.a.weight = self.b.weight


class DistinctSameStorage(nn.Module):
    def __init__(self):
        super().__init__()
        base = torch.zeros(16)
        self.p = nn.Parameter(base.view(4, 4))
        self.q = nn.Parameter(self.p.data)


class DistinctSharedStorageViews(nn.Module):
    def __init__(self):
        super().__init__()
        base = torch.zeros(24)
        self.p = nn.Parameter(base[:16].view(4, 4))
        self.q = nn.Parameter(base[8:24].view(4, 4))


class ParamBuffer(nn.Module):
    def __init__(self):
        super().__init__()
        self.p = nn.Parameter(torch.zeros(4, 4))
        self.register_buffer("buf", torch.zeros(4, 4), persistent=True)


class Untied(nn.Module):
    def __init__(self):
        super().__init__()
        self.a = nn.Linear(4, 4, bias=False)
        self.b = nn.Linear(4, 4, bias=False)


class OneParam(nn.Module):
    def __init__(self, shape=(4, 4), dtype=torch.float32):
        super().__init__()
        self.p = nn.Parameter(torch.zeros(shape, dtype=dtype))


class TwoParam(nn.Module):
    def __init__(self):
        super().__init__()
        self.p = nn.Parameter(torch.zeros(4, 4))
        self.q = nn.Parameter(torch.zeros(4, 4))


def mutate(model):
    with torch.no_grad():
        if isinstance(model, (TiedAB, TiedBA)):
            p = next(model.parameters())
            p.add_(torch.arange(16, dtype=p.dtype).view(4, 4) / 10 + 1)
        elif isinstance(model, DistinctSameStorage):
            model.p.add_(torch.arange(16).view(4, 4).float() / 10 + 1)
        elif isinstance(model, DistinctSharedStorageViews):
            model.p.add_(1.0)
            model.q.add_(torch.linspace(0.1, 1.6, 16).view(4, 4))
        elif isinstance(model, ParamBuffer):
            model.p.add_(torch.arange(16).view(4, 4).float() / 10 + 1)
            model.buf.add_(2)
        elif isinstance(model, Untied):
            model.a.weight.add_(torch.arange(16).view(4, 4).float() / 10 + 1)
            model.b.weight.add_(torch.arange(16).flip(0).view(4, 4).float() / 10 + 0.5)


def summarize_case(cls):
    prev = cls()
    cur = cls()
    cur.load_state_dict(prev.state_dict())
    mutate(cur)
    release = public_release_compute(cur, prev)
    repair = trainer_namespace_compute(cur, prev)
    trainer_names = [
        name for name, p in cur.named_parameters(remove_duplicate=True)
        if torch.is_floating_point(p)
    ]
    invariance = {}
    for name in trainer_names:
        rm, fm = release["masks"].get(name), repair["masks"].get(name)
        rr, fr = release["ref_weights"].get(name), repair["ref_weights"].get(name)
        invariance[name] = {
            "mask_equal": (rm is None and fm is None) or (rm is not None and fm is not None and torch.equal(rm, fm)),
            "ref_equal": (rr is None and fr is None) or (rr is not None and fr is not None and torch.equal(rr, fr)),
        }
    return {
        "state_dict_keys": list(cur.state_dict()),
        "named_parameters_all": [n for n, _ in cur.named_parameters(remove_duplicate=False)],
        "named_parameters_canonical": trainer_names,
        "release_mask_keys": list(release["masks"]),
        "repair_mask_keys": list(repair["masks"]),
        "release_dead_mask_keys": [k for k in release["masks"] if k not in set(trainer_names)],
        "repair_dead_mask_keys": [k for k in repair["masks"] if k not in set(trainer_names)],
        "trainer_consumed_invariance": invariance,
    }


def main():
    out = {"torch_version": torch.__version__, "top_percent": 50.0, "cases": {}}
    for cls in [TiedAB, TiedBA, DistinctSameStorage, DistinctSharedStorageViews, ParamBuffer, Untied]:
        out["cases"][cls.__name__] = summarize_case(cls)

    for cls in [TiedAB, ParamBuffer]:
        prev0, cur0 = cls(), cls()
        cur0.load_state_dict(prev0.state_dict())
        mutate(cur0)
        legacy = public_release_compute(cur0, prev0)
        prev1, cur1 = cls(), cls()
        prev1.load_state_dict(cur0.state_dict())
        cur1.load_state_dict(prev1.state_dict())
        mutate(cur1)
        migrated = trainer_namespace_compute(cur1, prev1, previous_saved=legacy)
        out["cases"][cls.__name__]["migration_ignored_previous_noncanonical"] = (
            migrated["ignored_previous_noncanonical"]
        )

    mismatch = {}
    fixtures = [
        ("namespace", TwoParam(), OneParam()),
        ("shape", OneParam((4, 4)), OneParam((2, 8))),
        ("dtype", OneParam(dtype=torch.float32), OneParam(dtype=torch.float64)),
        ("registration_order", TiedAB(), TiedBA()),
    ]
    for name, prev, cur in fixtures:
        try:
            trainer_namespace_compute(cur, prev)
            mismatch[name] = {"failed_closed": False}
        except Exception as exc:
            mismatch[name] = {"failed_closed": True, "error": str(exc)}
    out["mismatch_tests"] = mismatch
    out["all_trainer_consumed_masks_refs_equal"] = all(
        all(v["mask_equal"] and v["ref_equal"] for v in case["trainer_consumed_invariance"].values())
        for case in out["cases"].values()
    )
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
