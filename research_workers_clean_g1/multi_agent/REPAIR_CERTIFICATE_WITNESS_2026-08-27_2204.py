#!/usr/bin/env python3
"""Finite repair-certificate witness construction and routing litmus.

Mechanism study only. Missing positive evidence is modeled as unknown rather
than safe. Public fixture ports preserve selected upstream test semantics but
do not execute the upstream repository.
"""

from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from itertools import product
import json

class Capture(Enum):
    OBSERVED = "observed"
    KNOWN_UNCAPTURED = "known_uncaptured"
    UNKNOWN = "unknown"

class Static(Enum):
    COMPLETE = "complete_overapprox"
    PARTIAL = "partial"
    ABSENT = "absent"

class Serving(Enum):
    EXACT = "exact_rebind"
    COLD = "cold_rebuild_available"
    UNKNOWN = "unknown"

class Route(Enum):
    LOCAL = "local"
    ENLARGED = "enlarged"
    WHOLE = "whole"
    BLOCK = "block"

@dataclass(frozen=True)
class Case:
    epoch_matches: bool = True
    topology_matches: bool = True
    surface_registered: bool = True
    receiver_chain_complete: bool = True
    runtime_capture: Capture = Capture.OBSERVED
    static_status: Static = Static.COMPLETE
    required_results_known: bool = True
    committed_effect: bool = False
    action_equivalence_known: bool = True
    authorization_safe: bool = True
    inflight_safe: bool = True
    effect_receipt_present: bool = True
    serving: Serving = Serving.EXACT

@dataclass(frozen=True)
class Witness:
    capture_status: str
    capture_basis: str
    reasons: tuple[str, ...]

def construct_witness(c: Case) -> Witness:
    if not c.epoch_matches or not c.topology_matches:
        return Witness("unknown", "stale_epoch_or_topology",
                       ("capture_epoch_or_topology_mismatch",))
    if not c.surface_registered:
        return Witness("unknown", "surface_inventory",
                       ("surface_not_positively_registered",))
    if not c.receiver_chain_complete:
        return Witness("known_uncaptured", "receiver_omission",
                       ("receiver_or_transparency_gap",))
    if c.runtime_capture == Capture.KNOWN_UNCAPTURED:
        if c.static_status == Static.COMPLETE:
            return Witness("proved", "static_complete_overapprox_after_known_gap",
                           ("runtime_known_uncaptured", "static_complete_overapprox"))
        return Witness("known_uncaptured", "runtime_adapter",
                       ("runtime_known_uncaptured",))
    if c.runtime_capture == Capture.UNKNOWN:
        if c.static_status == Static.COMPLETE:
            return Witness("proved", "static_complete_overapprox",
                           ("runtime_capture_unknown", "static_complete_overapprox"))
        return Witness("unknown", "runtime_and_static_incomplete",
                       ("runtime_capture_unknown",))
    if c.static_status == Static.COMPLETE:
        return Witness("proved", "runtime_plus_static",
                       ("runtime_observed", "static_complete_overapprox"))
    return Witness("proved", "runtime_observed", ("runtime_observed",))

def route(c: Case, w: Witness) -> Route:
    # A receiver/transparency gap can hide an already-issued external action.
    # Static dependency closure cannot establish effect absence.
    if not c.receiver_chain_complete:
        return Route.BLOCK
    if not c.required_results_known:
        return Route.BLOCK
    if c.committed_effect:
        if not c.effect_receipt_present:
            return Route.BLOCK
        if (not c.action_equivalence_known
                or not c.authorization_safe
                or not c.inflight_safe):
            return Route.BLOCK
    if not c.epoch_matches or not c.topology_matches:
        return Route.WHOLE if c.serving != Serving.UNKNOWN else Route.BLOCK
    if c.serving == Serving.UNKNOWN:
        return Route.BLOCK
    if c.serving == Serving.COLD:
        return Route.WHOLE

    if w.capture_status == "proved":
        if w.capture_basis in ("runtime_observed", "runtime_plus_static"):
            return Route.LOCAL
        return Route.ENLARGED
    if w.capture_status == "known_uncaptured":
        if w.capture_basis == "runtime_adapter" and c.static_status == Static.COMPLETE:
            return Route.ENLARGED
        return Route.WHOLE
    return Route.WHOLE

def true_capture_sufficient(c: Case) -> bool:
    if not (c.epoch_matches and c.topology_matches
            and c.surface_registered and c.receiver_chain_complete):
        return False
    if c.runtime_capture == Capture.OBSERVED:
        return True
    return c.static_status == Static.COMPLETE

def true_edit_safe(c: Case) -> bool:
    if not c.required_results_known or not c.receiver_chain_complete:
        return False
    if c.committed_effect:
        if (not c.effect_receipt_present
                or not c.action_equivalence_known
                or not c.authorization_safe
                or not c.inflight_safe):
            return False
    return True

def route_safe(c: Case, r: Route) -> bool:
    if r == Route.BLOCK:
        return True
    if not true_edit_safe(c):
        return False
    if r in (Route.LOCAL, Route.ENLARGED):
        return true_capture_sufficient(c) and c.serving == Serving.EXACT
    if r == Route.WHOLE:
        return c.serving in (Serving.EXACT, Serving.COLD)
    raise AssertionError(r)

def absence_as_safe(c: Case) -> Route:
    """Anti-pattern: explicit warning is bad; otherwise missing proof is safe."""
    if not c.required_results_known:
        return Route.BLOCK
    if c.committed_effect and (
        not c.effect_receipt_present
        or not c.action_equivalence_known
        or not c.authorization_safe
        or not c.inflight_safe
    ):
        return Route.BLOCK
    if not c.receiver_chain_complete or c.runtime_capture == Capture.KNOWN_UNCAPTURED:
        return Route.WHOLE if c.serving != Serving.UNKNOWN else Route.BLOCK
    if c.serving == Serving.UNKNOWN:
        return Route.BLOCK
    return Route.LOCAL

def injection_litmuses() -> dict[str, str]:
    cases = {
        "healthy_precise": Case(),
        "runtime_known_uncaptured_static_complete":
            Case(runtime_capture=Capture.KNOWN_UNCAPTURED, static_status=Static.COMPLETE),
        "runtime_unknown_static_complete":
            Case(runtime_capture=Capture.UNKNOWN, static_status=Static.COMPLETE),
        "surface_inventory_unknown": Case(surface_registered=False),
        "epoch_mismatch": Case(epoch_matches=False),
        "receiver_chain_gap": Case(receiver_chain_complete=False),
        "required_result_ambiguity": Case(required_results_known=False),
        "committed_effect_equivalence_unknown":
            Case(committed_effect=True, action_equivalence_known=False),
        "authorization_conflict":
            Case(committed_effect=True, authorization_safe=False),
        "inflight_conflict":
            Case(committed_effect=True, inflight_safe=False),
        "effect_receipt_missing":
            Case(committed_effect=True, effect_receipt_present=False),
        "serving_state_unknown": Case(serving=Serving.UNKNOWN),
        "serving_cold_rebuild": Case(serving=Serving.COLD),
    }
    return {name: route(case, construct_witness(case)).value
            for name, case in cases.items()}

def public_fixture_ports() -> dict[str, object]:
    # Upstream artifact snapshot-local litmus: the same fresh reserve is safe
    # after replace and unsafe after live restore because the old claim remains.
    snapshot = {"replace_safe": 1 <= 1, "live_safe": 2 <= 1}
    assert snapshot == {"replace_safe": True, "live_safe": False}

    # Upstream lineage litmus: OR-lineage transport charges old/restored once;
    # naive copying charges the same lineage twice.
    lineage = {"or_transport_allows": 2 <= 2, "naive_copy_allows": 4 <= 2}
    assert lineage == {"or_transport_allows": True, "naive_copy_allows": False}

    # Upstream effect-proxy semantics: stable OperationID+ResultHash is
    # replayable after receipt/query recovery; a different logical route gets
    # a distinct call identity and must not alias.
    stable_op = ("op-stable", "c" * 64)
    retry_op = ("op-stable", "c" * 64)
    charge = "effect-route-idempotency-v1:6:charge:order/A-17:payment"
    refund = "effect-route-idempotency-v1:6:refund:order/A-17:payment"
    effect = {
        "stable_retry_equivalent": stable_op == retry_op,
        "different_route_aliases": charge == refund,
    }
    assert effect == {"stable_retry_equivalent": True,
                      "different_route_aliases": False}
    return {"snapshot_local": snapshot, "lineage_or": lineage,
            "effect_proxy": effect}

def exhaustive() -> dict[str, object]:
    axes = [
        [True, False], [True, False], [True, False], [True, False],
        list(Capture), list(Static), [True, False], [True, False],
        [True, False], [True, False], [True, False], [True, False],
        list(Serving),
    ]
    total = witness_unsafe = naive_unsafe = 0
    witness_routes = Counter()
    naive_routes = Counter()
    for values in product(*axes):
        c = Case(*values)
        w = construct_witness(c)
        wr = route(c, w)
        nr = absence_as_safe(c)
        total += 1
        witness_routes[wr.value] += 1
        naive_routes[nr.value] += 1
        witness_unsafe += int(not route_safe(c, wr))
        naive_unsafe += int(not route_safe(c, nr))
    return {
        "states": total,
        "witness_router_unsafe": witness_unsafe,
        "absence_as_safe_unsafe": naive_unsafe,
        "witness_routes": dict(sorted(witness_routes.items())),
        "absence_as_safe_routes": dict(sorted(naive_routes.items())),
    }

def main() -> None:
    out = {
        "schema_version": 1,
        "injection_litmuses": injection_litmuses(),
        "public_fixture_ports": public_fixture_ports(),
        "exhaustive": exhaustive(),
        "scope": [
            "finite mechanism model only; no production threshold claim",
            "Static.COMPLETE is a positive over-approximation premise, not an estimator",
            "receiver/transparency gaps block because hidden external effects are not repaired by static dependency closure",
            "public fixture ports preserve published test semantics but do not execute upstream code",
        ],
    }
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
