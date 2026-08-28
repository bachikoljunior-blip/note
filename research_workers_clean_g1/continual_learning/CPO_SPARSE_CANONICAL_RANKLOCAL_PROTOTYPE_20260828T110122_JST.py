from __future__ import annotations
import hashlib, json, math
from typing import Any, Mapping, MutableMapping
import torch

SCHEMA_VERSION = 1


def _dtype_name(t: torch.Tensor) -> str:
    return str(t.dtype).replace("torch.", "")


def canonical_namespace(model: torch.nn.Module) -> list[dict[str, Any]]:
    """Return exactly the duplicate-free parameter namespace visible to the trainer."""
    rows = []
    for name, p in model.named_parameters(recurse=True, remove_duplicate=True):
        rows.append({
            "name": name,
            "shape": list(p.shape),
            "numel": int(p.numel()),
            "dtype": _dtype_name(p),
        })
    return rows


def namespace_digest(rows: list[dict[str, Any]]) -> str:
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _validate_sorted_idx(idx: torch.Tensor, numel: int, *, name: str) -> None:
    if idx.dtype != torch.long or idx.ndim != 1:
        raise ValueError(f"{name}: global_idx must be 1-D int64")
    if idx.numel():
        if int(idx[0]) < 0 or int(idx[-1]) >= numel:
            raise ValueError(f"{name}: global_idx out of bounds")
        if idx.numel() > 1 and not bool(torch.all(idx[1:] > idx[:-1])):
            raise ValueError(f"{name}: global_idx must be strictly increasing")


def convert_release_mask_to_sparse_canonical(
    model: torch.nn.Module,
    raw_saved: Mapping[str, Any],
    *,
    source_identity: Mapping[str, str] | None = None,
    destructive_release: bool = False,
) -> dict[str, Any]:
    """Convert public CPO release-format dense masks to canonical sparse trainer state.

    Semantics intentionally preserve the public release artifact rather than recomputing
    TopP.  State-dict-only aliases and floating buffers are discarded because the trainer
    consumes masks only through duplicate-free named_parameters().  Distinct Parameter
    objects are retained even if they share storage.
    """
    if not (isinstance(raw_saved, Mapping) and "masks" in raw_saved and "ref_weights" in raw_saved):
        raise ValueError("requires release-format {'masks','ref_weights'} payload")
    masks = raw_saved["masks"]
    refs = raw_saved["ref_weights"]
    if not isinstance(masks, MutableMapping) or not isinstance(refs, Mapping):
        raise TypeError("masks must be mutable mapping and refs a mapping")

    ns = canonical_namespace(model)
    canon = {row["name"]: row for row in ns}
    parameters: dict[str, Any] = {}
    dropped_noncanonical: list[str] = []

    # Stable key snapshot permits dense masks to be popped immediately after conversion.
    for name in list(masks.keys()):
        mask = masks[name]
        if name not in canon:
            dropped_noncanonical.append(name)
            if destructive_release:
                masks.pop(name, None)
            continue
        row = canon[name]
        if list(mask.shape) != row["shape"]:
            raise ValueError(f"{name}: mask shape {list(mask.shape)} != canonical {row['shape']}")
        if mask.dtype != torch.bool:
            raise ValueError(f"{name}: mask dtype must be bool")

        idx = mask.reshape(-1).nonzero(as_tuple=True)[0].cpu().clone()
        _validate_sorted_idx(idx, row["numel"], name=name)
        if name not in refs:
            raise ValueError(f"{name}: missing ref_weights")
        ref = refs[name].reshape(-1).cpu().float().clone()
        if ref.numel() != idx.numel():
            raise ValueError(f"{name}: ref count {ref.numel()} != mask count {idx.numel()}")

        parameters[name] = {
            "shape": row["shape"],
            "numel": row["numel"],
            "dtype": row["dtype"],
            "global_idx": idx,
            "ref": ref,
            "global_n_masked": int(idx.numel()),
        }
        if destructive_release:
            masks.pop(name, None)

    return {
        "schema_version": SCHEMA_VERSION,
        "format": "cpo_sparse_canonical_v1",
        "source_identity": dict(source_identity or {}),
        "canonical_namespace": ns,
        "canonical_namespace_sha256": namespace_digest(ns),
        "parameters": parameters,
        "dropped_noncanonical": sorted(dropped_noncanonical),
    }


def validate_runtime_and_prepartition(
    model: torch.nn.Module,
    artifact: Mapping[str, Any],
    *,
    world_size: int,
    rank: int,
    require_zero3_attrs: bool = False,
) -> dict[str, Any]:
    """Fail closed on namespace/runtime drift, then clone rank-local sparse slices.

    global_n_masked deliberately remains the global per-parameter support count.  Replacing
    it with the rank-local count changes the regularizer under support imbalance.
    """
    if artifact.get("schema_version") != SCHEMA_VERSION or artifact.get("format") != "cpo_sparse_canonical_v1":
        raise ValueError("unsupported sparse artifact schema")
    if world_size < 1 or rank < 0 or rank >= world_size:
        raise ValueError("invalid distributed tuple")

    ns = canonical_namespace(model)
    digest = namespace_digest(ns)
    if digest != artifact.get("canonical_namespace_sha256"):
        raise RuntimeError(
            f"canonical namespace mismatch runtime={digest} artifact={artifact.get('canonical_namespace_sha256')}"
        )
    canon_params = dict(model.named_parameters(recurse=True, remove_duplicate=True))
    out_params: dict[str, Any] = {}

    for name, entry in artifact["parameters"].items():
        if name not in canon_params:
            raise RuntimeError(f"{name}: missing canonical runtime parameter")
        p = canon_params[name]
        expected_shape = list(p.shape)
        expected_numel = int(p.numel())
        expected_dtype = _dtype_name(p)
        if entry["shape"] != expected_shape or int(entry["numel"]) != expected_numel or entry["dtype"] != expected_dtype:
            raise RuntimeError(f"{name}: runtime shape/numel/dtype tuple mismatch")

        idx = entry["global_idx"]
        ref = entry["ref"]
        _validate_sorted_idx(idx, expected_numel, name=name)
        if int(entry["global_n_masked"]) != idx.numel() or ref.numel() != idx.numel():
            raise RuntimeError(f"{name}: global_n_masked/ref alignment mismatch")

        if require_zero3_attrs:
            if not hasattr(p, "ds_numel"):
                raise RuntimeError(f"{name}: missing ds_numel under required ZeRO-3 runtime")
            if int(p.ds_numel) != expected_numel:
                raise RuntimeError(f"{name}: ds_numel={int(p.ds_numel)} != canonical numel={expected_numel}")

        full_numel = int(getattr(p, "ds_numel", expected_numel))
        if full_numel != expected_numel:
            raise RuntimeError(f"{name}: full_numel mismatch")
        partition_size = math.ceil(full_numel / world_size)
        start = rank * partition_size
        end = min(start + partition_size, full_numel)

        # Sorted global indices permit O(log s) bounds rather than an O(s) boolean filter.
        lo = int(torch.searchsorted(idx, torch.tensor(start, dtype=idx.dtype), right=False).item())
        hi = int(torch.searchsorted(idx, torch.tensor(end, dtype=idx.dtype), right=False).item())
        # clone() is required: a view would keep the full global idx/ref storage alive.
        global_idx = idx[lo:hi].clone()
        ref_local = ref[lo:hi].clone()
        local_idx = (global_idx - start).clone()

        out_params[name] = {
            "global_idx": global_idx,
            "local_idx": local_idx,
            "ref": ref_local,
            "global_n_masked": int(entry["global_n_masked"]),
            "partition": {
                "world_size": world_size,
                "rank": rank,
                "partition_size": partition_size,
                "start": start,
                "end": end,
                "full_numel": full_numel,
            },
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "canonical_namespace_sha256": digest,
        "world_size": world_size,
        "rank": rank,
        "parameters": out_params,
    }


def sparse_regularizer_pending_grad(
    local_data: torch.Tensor,
    local_idx: torch.Tensor,
    ref: torch.Tensor,
    *,
    global_n_masked: int,
    mask_lambda: float,
    normalizer: float,
) -> tuple[torch.Tensor, float]:
    """Source-equivalent local algebra for the current public-code regularizer.

    This intentionally does not fix the separately identified ZeRO-3 reduce-scatter
    world-size attenuation; distributed scaling remains an independent experimental axis.
    """
    if ref.numel() != local_idx.numel():
        raise ValueError("local ref/index mismatch")
    if global_n_masked < local_idx.numel():
        raise ValueError("global denominator smaller than local support")
    if local_idx.numel() == 0:
        return torch.empty(0, dtype=torch.float32), 0.0
    diff = local_data.reshape(-1)[local_idx].float() - ref.float()
    denom = max(int(global_n_masked), 1)
    scale = float(mask_lambda) / denom / float(normalizer)
    return scale * torch.sign(diff), diff.abs().sum().item() / denom
