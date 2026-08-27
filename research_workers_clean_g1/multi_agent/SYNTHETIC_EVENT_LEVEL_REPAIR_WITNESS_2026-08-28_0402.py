#!/usr/bin/env python3
"""Event-level rollback/admissibility witness mechanism study.

Synthetic, deterministic mechanism test. Counts are structural test counts, not deployment rates.
Frozen semantic scope: clean multi_agent role; public evidence only.
"""

from dataclasses import dataclass, replace
from enum import Enum, IntEnum
import json, random


class Route(IntEnum):
    LOCAL = 0
    ENLARGED = 1
    WHOLE_REDRAW = 2
    BLOCK = 3


class Scope(str, Enum):
    LIVE = "live"
    OFFLINE = "offline"


class Head(str, Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    UNAVAILABLE = "unavailable"


class Checkpoint(str, Enum):
    CONSISTENT = "consistent"
    CONFLICT = "conflict"
    UNAUTHENTICATED = "unauthenticated"
    STALE_IDENTITY = "stale_identity"
    UNAVAILABLE = "unavailable"


class Transparency(str, Enum):
    MONITORED_CONSISTENT = "monitored_consistent"
    INCLUSION_ONLY = "inclusion_only"
    CONFLICT = "conflict"
    UNAVAILABLE = "unavailable"


class Surface(str, Enum):
    COMPLETE = "complete"
    KNOWN_UNCAPTURED_EFFECTLESS = "known_uncaptured_effectless"
    KNOWN_UNCAPTURED_EFFECT_CAPABLE = "known_uncaptured_effect_capable"
    UNKNOWN = "unknown"


class Dep(str, Enum):
    EXACT = "exact"
    COMPLETE_OVERAPPROX = "complete_overapprox"
    INCOMPLETE = "incomplete"
    UNKNOWN = "unknown"


class Binding(str, Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    UNKNOWN = "unknown"


class Auth(str, Enum):
    CURRENT = "current"
    CONSUMED = "consumed"
    UNKNOWN = "unknown"


class Effect(str, Enum):
    NO_EFFECT = "no_effect"
    CONFIRMED_ONCE_REPLAYABLE = "confirmed_once_replayable"
    AMBIGUOUS = "ambiguous"
    IRREVERSIBLE_UNRECONCILED = "irreversible_unreconciled"
    UNKNOWN = "unknown"


class Attended(str, Enum):
    FRESH_REBIND = "fresh_rebind"
    STALE = "stale"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Witness:
    scope: Scope
    receipt_artifact_valid: bool = True
    presented_chain_consistent: bool = True
    live_receiver_head: Head = Head.MATCH
    checkpoint: Checkpoint = Checkpoint.CONSISTENT
    transparency: Transparency = Transparency.MONITORED_CONSISTENT
    manifest_epoch_match: bool = True
    topology_digest_match: bool = True
    surface_inventory: Surface = Surface.COMPLETE
    runtime_dependency: Dep = Dep.EXACT
    static_dependency: Dep = Dep.COMPLETE_OVERAPPROX
    action_binding: Binding = Binding.MATCH
    authorization: Auth = Auth.CURRENT
    effect: Effect = Effect.NO_EFFECT
    attended_state: Attended = Attended.FRESH_REBIND


def route(w: Witness) -> Route:
    # History claim scopes must not substitute for each other.
    if not (w.receipt_artifact_valid and w.presented_chain_consistent):
        return Route.BLOCK
    if w.scope == Scope.LIVE:
        if w.live_receiver_head != Head.MATCH:
            return Route.BLOCK
    else:
        if w.checkpoint != Checkpoint.CONSISTENT:
            return Route.BLOCK
        if w.transparency != Transparency.MONITORED_CONSISTENT:
            return Route.BLOCK

    # Stale capture/topology epochs invalidate partial closures; without an explicit
    # effectless completeness proof, do not treat "no warning" as safe.
    if not (w.manifest_epoch_match and w.topology_digest_match):
        return Route.BLOCK

    # Independent action/authority/effect/attended-state proof axes.
    if w.action_binding != Binding.MATCH or w.authorization != Auth.CURRENT:
        return Route.BLOCK
    if w.effect not in {Effect.NO_EFFECT, Effect.CONFIRMED_ONCE_REPLAYABLE}:
        return Route.BLOCK
    if w.attended_state != Attended.FRESH_REBIND:
        return Route.BLOCK

    # Unknown/effect-capable uncaptured surfaces make whole redraw unsafe.
    if w.surface_inventory in {Surface.KNOWN_UNCAPTURED_EFFECT_CAPABLE, Surface.UNKNOWN}:
        return Route.BLOCK
    if w.surface_inventory == Surface.KNOWN_UNCAPTURED_EFFECTLESS:
        return Route.WHOLE_REDRAW

    if w.runtime_dependency == Dep.EXACT:
        return Route.LOCAL
    if w.static_dependency == Dep.COMPLETE_OVERAPPROX:
        return Route.ENLARGED
    return Route.WHOLE_REDRAW


def naive_no_warning(w: Witness) -> Route:
    """Negative control: a valid presented receipt-chain plus no explicit local warning."""
    if not (w.receipt_artifact_valid and w.presented_chain_consistent):
        return Route.BLOCK
    if w.action_binding == Binding.MISMATCH or w.authorization == Auth.CONSUMED:
        return Route.BLOCK
    if w.effect in {Effect.AMBIGUOUS, Effect.IRREVERSIBLE_UNRECONCILED}:
        return Route.BLOCK
    if w.attended_state == Attended.STALE:
        return Route.BLOCK
    if w.surface_inventory == Surface.KNOWN_UNCAPTURED_EFFECT_CAPABLE:
        return Route.BLOCK
    return Route.LOCAL


def global_everywhere(w: Witness) -> Route:
    """Negative control: global checkpoint/transparency proof substitutes for live-head claim."""
    if not (w.receipt_artifact_valid and w.presented_chain_consistent):
        return Route.BLOCK
    if w.checkpoint != Checkpoint.CONSISTENT:
        return Route.BLOCK
    if w.transparency != Transparency.MONITORED_CONSISTENT:
        return Route.BLOCK
    return route(replace(w, scope=Scope.OFFLINE))


def cases():
    live = Witness(scope=Scope.LIVE)
    off = Witness(scope=Scope.OFFLINE)
    return [
        ("live_baseline_exact", live, Route.LOCAL),
        ("offline_baseline_exact", off, Route.LOCAL),
        ("live_without_global_transparency",
         replace(live, checkpoint=Checkpoint.UNAVAILABLE, transparency=Transparency.UNAVAILABLE), Route.LOCAL),
        ("offline_transparency_inclusion_only",
         replace(off, transparency=Transparency.INCLUSION_ONLY), Route.BLOCK),
        ("offline_equivocation_detected",
         replace(off, transparency=Transparency.CONFLICT), Route.BLOCK),
        ("live_suffix_suppression_head_mismatch",
         replace(live, live_receiver_head=Head.MISMATCH), Route.BLOCK),
        ("offline_tail_checkpoint_conflict",
         replace(off, checkpoint=Checkpoint.CONFLICT), Route.BLOCK),
        ("offline_stale_identity_checkpoint",
         replace(off, checkpoint=Checkpoint.STALE_IDENTITY), Route.BLOCK),
        ("capture_epoch_stale", replace(live, manifest_epoch_match=False), Route.BLOCK),
        ("topology_digest_stale", replace(live, topology_digest_match=False), Route.BLOCK),
        ("known_uncaptured_effectless_surface",
         replace(live, surface_inventory=Surface.KNOWN_UNCAPTURED_EFFECTLESS), Route.WHOLE_REDRAW),
        ("known_uncaptured_effect_capable_surface",
         replace(live, surface_inventory=Surface.KNOWN_UNCAPTURED_EFFECT_CAPABLE), Route.BLOCK),
        ("unknown_surface_no_warning",
         replace(live, surface_inventory=Surface.UNKNOWN), Route.BLOCK),
        ("runtime_miss_static_complete",
         replace(live, runtime_dependency=Dep.INCOMPLETE, static_dependency=Dep.COMPLETE_OVERAPPROX), Route.ENLARGED),
        ("runtime_and_static_incomplete",
         replace(live, runtime_dependency=Dep.INCOMPLETE, static_dependency=Dep.INCOMPLETE), Route.WHOLE_REDRAW),
        ("action_digest_mismatch",
         replace(live, action_binding=Binding.MISMATCH), Route.BLOCK),
        ("authorization_consumed",
         replace(live, authorization=Auth.CONSUMED), Route.BLOCK),
        ("effect_ambiguous_after_dispatch",
         replace(live, effect=Effect.AMBIGUOUS), Route.BLOCK),
        ("effect_confirmed_once_replayable",
         replace(live, effect=Effect.CONFIRMED_ONCE_REPLAYABLE), Route.LOCAL),
        ("stale_attended_kv",
         replace(live, attended_state=Attended.STALE), Route.BLOCK),
        ("offline_checkpoint_unavailable",
         replace(off, checkpoint=Checkpoint.UNAVAILABLE), Route.BLOCK),
        ("live_global_proof_cannot_substitute_head_mismatch",
         replace(live, live_receiver_head=Head.MISMATCH,
                 checkpoint=Checkpoint.CONSISTENT,
                 transparency=Transparency.MONITORED_CONSISTENT), Route.BLOCK),
        ("offline_local_head_cannot_substitute_global_proof",
         replace(off, live_receiver_head=Head.MATCH,
                 checkpoint=Checkpoint.UNAVAILABLE,
                 transparency=Transparency.UNAVAILABLE), Route.BLOCK),
    ]


def degraded_variants(w: Witness):
    out = []
    if w.receipt_artifact_valid:
        out.append(replace(w, receipt_artifact_valid=False))
    if w.presented_chain_consistent:
        out.append(replace(w, presented_chain_consistent=False))
    if w.scope == Scope.LIVE and w.live_receiver_head == Head.MATCH:
        out.append(replace(w, live_receiver_head=Head.UNAVAILABLE))
    if w.scope == Scope.OFFLINE and w.checkpoint == Checkpoint.CONSISTENT:
        out.append(replace(w, checkpoint=Checkpoint.UNAVAILABLE))
    if w.scope == Scope.OFFLINE and w.transparency == Transparency.MONITORED_CONSISTENT:
        out.append(replace(w, transparency=Transparency.INCLUSION_ONLY))
    if w.manifest_epoch_match:
        out.append(replace(w, manifest_epoch_match=False))
    if w.topology_digest_match:
        out.append(replace(w, topology_digest_match=False))
    if w.surface_inventory == Surface.COMPLETE:
        out.append(replace(w, surface_inventory=Surface.UNKNOWN))
    elif w.surface_inventory == Surface.KNOWN_UNCAPTURED_EFFECTLESS:
        out.append(replace(w, surface_inventory=Surface.UNKNOWN))
    if w.runtime_dependency == Dep.EXACT:
        out.append(replace(w, runtime_dependency=Dep.UNKNOWN))
    if w.static_dependency == Dep.COMPLETE_OVERAPPROX:
        out.append(replace(w, static_dependency=Dep.UNKNOWN))
    if w.action_binding == Binding.MATCH:
        out.append(replace(w, action_binding=Binding.UNKNOWN))
    if w.authorization == Auth.CURRENT:
        out.append(replace(w, authorization=Auth.UNKNOWN))
    if w.effect in {Effect.NO_EFFECT, Effect.CONFIRMED_ONCE_REPLAYABLE}:
        out.append(replace(w, effect=Effect.UNKNOWN))
    if w.attended_state == Attended.FRESH_REBIND:
        out.append(replace(w, attended_state=Attended.UNKNOWN))
    return out


def random_witness(rng):
    return Witness(
        scope=rng.choice(list(Scope)),
        receipt_artifact_valid=rng.random() > 0.08,
        presented_chain_consistent=rng.random() > 0.08,
        live_receiver_head=rng.choice(list(Head)),
        checkpoint=rng.choice(list(Checkpoint)),
        transparency=rng.choice(list(Transparency)),
        manifest_epoch_match=rng.random() > 0.15,
        topology_digest_match=rng.random() > 0.15,
        surface_inventory=rng.choice(list(Surface)),
        runtime_dependency=rng.choice(list(Dep)),
        static_dependency=rng.choice(list(Dep)),
        action_binding=rng.choice(list(Binding)),
        authorization=rng.choice(list(Auth)),
        effect=rng.choice(list(Effect)),
        attended_state=rng.choice(list(Attended)),
    )


def main():
    c = cases()
    policies = {
        "event_witness": route,
        "naive_no_warning": naive_no_warning,
        "global_everywhere": global_everywhere,
    }
    summary = {}
    rows = []
    for pname, fn in policies.items():
        match = unsafe = over = 0
        for name, w, expected in c:
            got = fn(w)
            if got == expected:
                match += 1
            elif got < expected:
                unsafe += 1
            else:
                over += 1
            rows.append({
                "case": name, "policy": pname, "expected": expected.name, "got": got.name
            })
        summary[pname] = {"match": match, "unsafe": unsafe, "overconservative": over}

    rng = random.Random(202608280357)
    checks = violations = 0
    for _ in range(50000):
        w = random_witness(rng)
        before = route(w)
        for degraded in degraded_variants(w):
            checks += 1
            after = route(degraded)
            if after < before:
                violations += 1

    print(json.dumps({
        "schema_version": 1,
        "named_case_count": len(c),
        "named_case_summary": summary,
        "evidence_loss_monotonicity": {
            "seed": 202608280357,
            "sampled_witnesses": 50000,
            "one-proof-loss_checks": checks,
            "violations": violations,
        },
        "rows": rows,
        "scope": "Synthetic deterministic mechanism study; counts are not deployment probabilities.",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
