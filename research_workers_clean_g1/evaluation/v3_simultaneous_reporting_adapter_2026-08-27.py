"""Adapter binding the simultaneous-reporting contract to the production V3 CS.

This file changes no statistical family. It only freezes alpha at stream construction
so the generic dual-channel reporter can run the existing decision-IUT streams at
alpha=.05 and separate simultaneous numeric-report streams at their precommitted
reporting alphas.
"""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from typing import Any


def _load_sibling(filename: str, module_name: str) -> Any:
    path = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


_V3 = _load_sibling(
    "weighted_average_incremental_lsm_v3_warm_root_2026-08-27.py",
    "_evaluation_weighted_v3_prod",
)


class AlphaBoundV3Stream:
    """Production V3 stream with a construction-time confidence alpha."""

    def __init__(self, alpha: float) -> None:
        self.alpha = float(alpha)
        self.inner = _V3.IncrementalExactWeightedUpperCS(
            _V3.DEFAULT_LAMBDAS,
            _V3.DEFAULT_MIXTURE,
        )

    def append(self, weight: float, score: float) -> None:
        self.inner.append(weight, score)

    def log_e(self, mu0: float) -> float:
        return self.inner.log_e(mu0)

    def upper_endpoint(self) -> float:
        return self.inner.upper_endpoint(alpha=self.alpha)

    def total_stats_calls(self) -> int:
        return self.inner.total_stats_calls()


def production_v3_stream_factory(alpha: float) -> AlphaBoundV3Stream:
    return AlphaBoundV3Stream(alpha)
