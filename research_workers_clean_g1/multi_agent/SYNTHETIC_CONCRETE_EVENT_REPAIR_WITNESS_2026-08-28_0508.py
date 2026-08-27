#!/usr/bin/env python3
"""Concrete-event repair witness mechanism study.

Synthetic, deterministic mechanism/conformance study for a clean multi-agent
research role. Counts are structural test/fuzz counts, not deployment rates.

Main question:
Can a rollback/recovery controller derive repair admissibility from concrete
channel events while preserving claim scope, evidence monotonicity, and
authorization/effect semantics under simultaneous omission/replay faults?
"""

from dataclasses import dataclass, replace
from enum import Enum, IntEnum
from typing import Optional, Tuple
import hashlib
import json
import random


class RepairScope(IntEnum):
    LOCAL = 0
    ENLARGED = 1
    WHOLE_REDRAW = 2
    BLOCK = 3


class EffectPerm(IntEnum):
    REDISPATCH = 0
    REPLAY_RESULT_ONLY = 1
    NO_PROVIDER_ACTION = 2
    BLOCK = 3


class Scope(str, Enum):
    LIVE = "live"
    OFFLINE = "offline"


class Intent(str, Enum):
    INTERNAL_REPAIR = "internal_repair"
    REPLAY_RECORDED_RESULT = "replay_recorded_result"
    REDISPATCH_EFFECT = "redispatch_effect"


class EffectState(str, Enum):
    NO_DISPATCH = "no_dispatch"
    CONFIRMED_ONCE = "confirmed_once"
    CERTIFIED_NO_EFFECT = "certified_no_effect"
    AMBIGUOUS = "ambiguous"
    IRREVERSIBLE_UNRECONCILED = "irreversible_unreconciled"


class AuthState(str, Enum):
    CURRENT = "current"
    CONSUMED = "consumed"
    UNKNOWN = "unknown"


class ObsEffect(str, Enum):
    NO_DISPATCH_PROVED = "no_dispatch_proved"
    CONFIRMED_ONCE = "confirmed_once"
    CERTIFIED_NO_EFFECT_FENCED = "certified_no_effect_fenced"
    CERTIFIED_NO_EFFECT_UNFENCED = "certified_no_effect_unfenced"
    AMBIGUOUS = "ambiguous"
    IRREVERSIBLE_UNRECONCILED = "irreversible_unreconciled"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Context:
    scope: Scope
    claim_scope_id: str
    active_manifest_epoch: int
    active_topology_digest: str
    active_identity_epoch: int
    active_authorization_epoch: int
    committed_app_state_digest: str
    current_serving_epoch: int
    intended_action_digest: str
    operation_id: str
    intent: Intent


@dataclass(frozen=True)
class Truth:
    history_ok: bool = True
    identity_current: bool = True
    capture_epoch_current: bool = True
    topology_current: bool = True
    hidden_effect_capable_surface: bool = False
    runtime_closure_exact: bool = True
    static_overapprox_complete: bool = True
    action_binding_match: bool = True
    authorization_state: AuthState = AuthState.CURRENT
    authorization_epoch_current: bool = True
    effect_state: EffectState = EffectState.NO_DISPATCH
    delivery_fence_present: bool = True
    recorded_result_binding_match: bool = True
    serving_fresh: bool = True


@dataclass(frozen=True)
class Receipt:
    seq: int
    payload_hash: str
    prev_hash: str
    issuer: str
    valid_signature: bool = True


@dataclass(frozen=True)
class ReceiverHead:
    head_hash: str
    trusted_direct: bool = True


@dataclass(frozen=True)
class Checkpoint:
    head_hash: str
    claim_scope_id: str
    identity_epoch: int
    manifest_epoch: int
    topology_digest: str
    authenticated: bool = True


@dataclass(frozen=True)
class TransparencyEvidence:
    included: bool
    consistency_monitored: bool
    conflict: bool = False


@dataclass(frozen=True)
class IdentityBinding:
    claim_scope_id: str
    identity_epoch: int
    authorized_issuer: str
    valid_signature: bool = True


@dataclass(frozen=True)
class MediationManifest:
    epoch: int
    topology_digest: str
    registered_surfaces: Tuple[str, ...]
    signed: bool = True


@dataclass(frozen=True)
class SurfaceCensus:
    epoch: int
    topology_digest: str
    surfaces_seen: Tuple[str, ...]
    complete: bool
    activity_gap: bool = False


@dataclass(frozen=True)
class DependencyReceipt:
    source_version: str
    consumer: str
    epoch: int
    topology_digest: str
    complete_closure: bool


@dataclass(frozen=True)
class StaticDependencyDecl:
    topology_digest: str
    complete_overapprox: bool
    signed: bool = True


@dataclass(frozen=True)
class AuthorizationRecord:
    action_digest: str
    grant_epoch: int
    state: AuthState


@dataclass(frozen=True)
class EffectObservation:
    operation_id: str
    action_digest: str
    state: ObsEffect
    result_hash: Optional[str] = None


@dataclass(frozen=True)
class ServingRebind:
    app_state_digest: str
    serving_epoch: int
    fresh_rebind: bool


@dataclass(frozen=True)
class Bundle:
    receipts: Tuple[Receipt, ...]
    receiver_head: Optional[ReceiverHead]
    checkpoint: Optional[Checkpoint]
    transparency: Optional[TransparencyEvidence]
    identity: Optional[IdentityBinding]
    manifest: Optional[MediationManifest]
    census: Optional[SurfaceCensus]
    dependency: Optional[DependencyReceipt]
    static_decl: Optional[StaticDependencyDecl]
    authorization: Optional[AuthorizationRecord]
    effect: Optional[EffectObservation]
    serving: Optional[ServingRebind]


@dataclass(frozen=True)
class Decision:
    repair: RepairScope
    effect: EffectPerm


def h(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def receipt_hash(r: Receipt) -> str:
    return h(f"{r.seq}|{r.payload_hash}|{r.prev_hash}|{r.issuer}")


def chain_head(receipts: Tuple[Receipt, ...]) -> Optional[str]:
    if not receipts:
        return None
    prev = "GENESIS"
    expected_seq = 0
    for r in receipts:
        if r.seq != expected_seq or not r.valid_signature or r.prev_hash != prev:
            return None
        prev = receipt_hash(r)
        expected_seq += 1
    return prev


def oracle(ctx: Context, t: Truth) -> Decision:
    """Hidden-state safety oracle for this synthetic model."""
    if not (t.history_ok and t.identity_current and t.capture_epoch_current and t.topology_current):
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
    if t.hidden_effect_capable_surface:
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
    if not t.action_binding_match or not t.serving_fresh:
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)

    if t.runtime_closure_exact:
        repair = RepairScope.LOCAL
    elif t.static_overapprox_complete:
        repair = RepairScope.ENLARGED
    else:
        repair = RepairScope.WHOLE_REDRAW

    if ctx.intent == Intent.INTERNAL_REPAIR:
        return Decision(repair, EffectPerm.NO_PROVIDER_ACTION)

    if ctx.intent == Intent.REPLAY_RECORDED_RESULT:
        if t.effect_state == EffectState.CONFIRMED_ONCE and t.recorded_result_binding_match:
            return Decision(repair, EffectPerm.REPLAY_RESULT_ONLY)
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)

    if t.authorization_state != AuthState.CURRENT or not t.authorization_epoch_current:
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
    if t.effect_state == EffectState.NO_DISPATCH:
        return Decision(repair, EffectPerm.REDISPATCH)
    if t.effect_state == EffectState.CERTIFIED_NO_EFFECT and t.delivery_fence_present:
        return Decision(repair, EffectPerm.REDISPATCH)
    return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)


def construct(ctx: Context, b: Bundle) -> Decision:
    """Derive the repair witness only from concrete, positively bound events."""
    head = chain_head(b.receipts)
    if head is None:
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)

    if ctx.scope == Scope.LIVE:
        if b.receiver_head is None or not b.receiver_head.trusted_direct or b.receiver_head.head_hash != head:
            return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
    else:
        if b.checkpoint is None or not b.checkpoint.authenticated:
            return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
        if (
            b.checkpoint.head_hash != head
            or b.checkpoint.claim_scope_id != ctx.claim_scope_id
            or b.checkpoint.identity_epoch != ctx.active_identity_epoch
            or b.checkpoint.manifest_epoch != ctx.active_manifest_epoch
            or b.checkpoint.topology_digest != ctx.active_topology_digest
        ):
            return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
        if (
            b.transparency is None
            or not b.transparency.included
            or not b.transparency.consistency_monitored
            or b.transparency.conflict
        ):
            return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)

    if (
        b.identity is None
        or not b.identity.valid_signature
        or b.identity.claim_scope_id != ctx.claim_scope_id
        or b.identity.identity_epoch != ctx.active_identity_epoch
        or b.identity.authorized_issuer != "receiver"
    ):
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)

    if b.manifest is None or not b.manifest.signed:
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
    if (
        b.manifest.epoch != ctx.active_manifest_epoch
        or b.manifest.topology_digest != ctx.active_topology_digest
    ):
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
    if b.census is None:
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
    if (
        b.census.epoch != ctx.active_manifest_epoch
        or b.census.topology_digest != ctx.active_topology_digest
        or not b.census.complete
        or b.census.activity_gap
        or not set(b.census.surfaces_seen).issubset(set(b.manifest.registered_surfaces))
    ):
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)

    if (
        b.serving is None
        or not b.serving.fresh_rebind
        or b.serving.app_state_digest != ctx.committed_app_state_digest
        or b.serving.serving_epoch != ctx.current_serving_epoch
    ):
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)

    if (
        b.authorization is None
        or b.authorization.action_digest != ctx.intended_action_digest
        or b.authorization.grant_epoch != ctx.active_authorization_epoch
    ):
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)

    if ctx.intent == Intent.INTERNAL_REPAIR:
        effect_perm = EffectPerm.NO_PROVIDER_ACTION

    elif ctx.intent == Intent.REPLAY_RECORDED_RESULT:
        if (
            b.effect is None
            or b.effect.operation_id != ctx.operation_id
            or b.effect.action_digest != ctx.intended_action_digest
            or b.effect.state != ObsEffect.CONFIRMED_ONCE
            or not b.effect.result_hash
        ):
            return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
        effect_perm = EffectPerm.REPLAY_RESULT_ONLY

    else:
        if b.authorization.state != AuthState.CURRENT:
            return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
        if (
            b.effect is None
            or b.effect.operation_id != ctx.operation_id
            or b.effect.action_digest != ctx.intended_action_digest
        ):
            return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
        if b.effect.state not in {
            ObsEffect.NO_DISPATCH_PROVED,
            ObsEffect.CERTIFIED_NO_EFFECT_FENCED,
        }:
            return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
        effect_perm = EffectPerm.REDISPATCH

    if (
        b.dependency is not None
        and b.dependency.epoch == ctx.active_manifest_epoch
        and b.dependency.topology_digest == ctx.active_topology_digest
        and b.dependency.complete_closure
    ):
        repair = RepairScope.LOCAL
    elif (
        b.static_decl is not None
        and b.static_decl.signed
        and b.static_decl.topology_digest == ctx.active_topology_digest
        and b.static_decl.complete_overapprox
    ):
        repair = RepairScope.ENLARGED
    else:
        repair = RepairScope.WHOLE_REDRAW

    return Decision(repair, effect_perm)


def absence_as_safe(ctx: Context, b: Bundle) -> Decision:
    if chain_head(b.receipts) is None:
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
    if b.effect is not None and b.effect.state in {
        ObsEffect.AMBIGUOUS,
        ObsEffect.IRREVERSIBLE_UNRECONCILED,
    }:
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
    if ctx.intent == Intent.REPLAY_RECORDED_RESULT:
        if b.authorization is not None and b.authorization.state != AuthState.CURRENT:
            return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
        return Decision(RepairScope.LOCAL, EffectPerm.REPLAY_RESULT_ONLY)
    if ctx.intent == Intent.REDISPATCH_EFFECT:
        return Decision(RepairScope.LOCAL, EffectPerm.REDISPATCH)
    return Decision(RepairScope.LOCAL, EffectPerm.NO_PROVIDER_ACTION)


def current_auth_everywhere(ctx: Context, b: Bundle) -> Decision:
    d = construct(ctx, b)
    if d.repair == RepairScope.BLOCK:
        return d
    if ctx.intent != Intent.INTERNAL_REPAIR and (
        b.authorization is None or b.authorization.state != AuthState.CURRENT
    ):
        return Decision(RepairScope.BLOCK, EffectPerm.BLOCK)
    return d


def more_permissive(got: Decision, safe: Decision) -> bool:
    return got.repair < safe.repair or got.effect < safe.effect


def make_context(scope: Scope, intent: Intent, seed: int) -> Context:
    return Context(
        scope=scope,
        claim_scope_id=f"scope-{seed % 5}",
        active_manifest_epoch=7,
        active_topology_digest=h(f"topology-{seed}")[:16],
        active_identity_epoch=11,
        active_authorization_epoch=13,
        committed_app_state_digest=h(f"app-state-{seed}")[:16],
        current_serving_epoch=5,
        intended_action_digest=h(f"action-{seed}")[:16],
        operation_id=f"op-{seed}",
        intent=intent,
    )


def honest_bundle(ctx: Context, t: Truth, seed: int) -> Bundle:
    r0 = Receipt(0, h(f"payload-0-{seed}"), "GENESIS", "receiver")
    r1 = Receipt(1, h(f"payload-1-{seed}"), receipt_hash(r0), "receiver")
    r2 = Receipt(2, h(f"payload-2-{seed}"), receipt_hash(r1), "receiver")
    receipts = (r0, r1, r2)
    head = chain_head(receipts)

    surfaces = ("llm", "tool", "memory")
    seen = surfaces + (("wrapper-x",) if t.hidden_effect_capable_surface else ())
    registered = surfaces

    effect_state = {
        EffectState.NO_DISPATCH: ObsEffect.NO_DISPATCH_PROVED,
        EffectState.CONFIRMED_ONCE: ObsEffect.CONFIRMED_ONCE,
        EffectState.CERTIFIED_NO_EFFECT: (
            ObsEffect.CERTIFIED_NO_EFFECT_FENCED
            if t.delivery_fence_present
            else ObsEffect.CERTIFIED_NO_EFFECT_UNFENCED
        ),
        EffectState.AMBIGUOUS: ObsEffect.AMBIGUOUS,
        EffectState.IRREVERSIBLE_UNRECONCILED: ObsEffect.IRREVERSIBLE_UNRECONCILED,
    }[t.effect_state]

    return Bundle(
        receipts=receipts,
        receiver_head=ReceiverHead(head_hash=head if t.history_ok else h("newer-live-head")),
        checkpoint=Checkpoint(
            head_hash=head,
            claim_scope_id=ctx.claim_scope_id,
            identity_epoch=ctx.active_identity_epoch if t.identity_current else ctx.active_identity_epoch - 1,
            manifest_epoch=ctx.active_manifest_epoch if t.capture_epoch_current else ctx.active_manifest_epoch - 1,
            topology_digest=ctx.active_topology_digest if t.topology_current else "stale-topology",
        ),
        transparency=TransparencyEvidence(
            included=True,
            consistency_monitored=t.history_ok,
            conflict=(not t.history_ok and ctx.scope == Scope.OFFLINE),
        ),
        identity=IdentityBinding(
            claim_scope_id=ctx.claim_scope_id,
            identity_epoch=ctx.active_identity_epoch if t.identity_current else ctx.active_identity_epoch - 1,
            authorized_issuer="receiver",
        ),
        manifest=MediationManifest(
            epoch=ctx.active_manifest_epoch if t.capture_epoch_current else ctx.active_manifest_epoch - 1,
            topology_digest=ctx.active_topology_digest if t.topology_current else "stale-topology",
            registered_surfaces=registered,
        ),
        census=SurfaceCensus(
            epoch=ctx.active_manifest_epoch if t.capture_epoch_current else ctx.active_manifest_epoch - 1,
            topology_digest=ctx.active_topology_digest if t.topology_current else "stale-topology",
            surfaces_seen=seen,
            complete=not t.hidden_effect_capable_surface,
            activity_gap=t.hidden_effect_capable_surface,
        ),
        dependency=DependencyReceipt(
            source_version="src-v2",
            consumer="sink",
            epoch=ctx.active_manifest_epoch if t.capture_epoch_current else ctx.active_manifest_epoch - 1,
            topology_digest=ctx.active_topology_digest if t.topology_current else "stale-topology",
            complete_closure=t.runtime_closure_exact,
        ),
        static_decl=StaticDependencyDecl(
            topology_digest=ctx.active_topology_digest if t.topology_current else "stale-topology",
            complete_overapprox=t.static_overapprox_complete,
        ),
        authorization=AuthorizationRecord(
            action_digest=ctx.intended_action_digest if t.action_binding_match else h("other-action")[:16],
            grant_epoch=ctx.active_authorization_epoch if t.authorization_epoch_current else ctx.active_authorization_epoch - 1,
            state=t.authorization_state,
        ),
        effect=EffectObservation(
            operation_id=ctx.operation_id,
            action_digest=ctx.intended_action_digest if t.action_binding_match else h("other-action")[:16],
            state=effect_state,
            result_hash=(
                h(f"result-{seed}")
                if t.effect_state == EffectState.CONFIRMED_ONCE and t.recorded_result_binding_match
                else None
            ),
        ),
        serving=ServingRebind(
            app_state_digest=ctx.committed_app_state_digest if t.serving_fresh else "stale-app-state",
            serving_epoch=ctx.current_serving_epoch if t.serving_fresh else ctx.current_serving_epoch - 1,
            fresh_rebind=t.serving_fresh,
        ),
    )


def named_cases():
    out = []

    def add(name, ctx, truth, mutate=lambda b: b):
        out.append((name, ctx, truth, mutate(honest_bundle(ctx, truth, len(out) + 1))))

    ctx = make_context(Scope.LIVE, Intent.INTERNAL_REPAIR, 1)
    truth = replace(Truth(), history_ok=False, identity_current=False)
    add("suffix_suppression_plus_stale_identity", ctx, truth, lambda b: replace(b, receiver_head=ReceiverHead(h("trusted-newer-head"))))

    ctx = make_context(Scope.OFFLINE, Intent.INTERNAL_REPAIR, 2)
    truth = replace(Truth(), history_ok=False)
    add("equivocation_plus_single_inclusion", ctx, truth, lambda b: replace(b, transparency=TransparencyEvidence(included=True, consistency_monitored=False, conflict=False)))

    ctx = make_context(Scope.LIVE, Intent.INTERNAL_REPAIR, 3)
    truth = replace(Truth(), hidden_effect_capable_surface=True)
    add("unregistered_effect_wrapper_plus_missing_warning", ctx, truth, lambda b: replace(b, census=SurfaceCensus(ctx.active_manifest_epoch, ctx.active_topology_digest, ("llm", "tool", "memory", "wrapper-x"), False, False)))

    ctx = make_context(Scope.LIVE, Intent.INTERNAL_REPAIR, 4)
    truth = replace(Truth(), hidden_effect_capable_surface=True)
    add("unregistered_wrapper_plus_replayed_old_complete_census", ctx, truth, lambda b: replace(b, census=SurfaceCensus(ctx.active_manifest_epoch - 1, "old-topology", ("llm", "tool", "memory"), True, False)))

    ctx = make_context(Scope.LIVE, Intent.INTERNAL_REPAIR, 5)
    truth = replace(Truth(), topology_current=False)
    add("stale_topology_plus_apparent_runtime_closure", ctx, truth, lambda b: replace(b, dependency=replace(b.dependency, complete_closure=True)))

    ctx = make_context(Scope.LIVE, Intent.REPLAY_RECORDED_RESULT, 6)
    truth = replace(Truth(), authorization_state=AuthState.CONSUMED, effect_state=EffectState.CONFIRMED_ONCE)
    add("consumed_auth_plus_exact_recorded_result_replay", ctx, truth)

    ctx = make_context(Scope.LIVE, Intent.REDISPATCH_EFFECT, 7)
    truth = replace(Truth(), effect_state=EffectState.AMBIGUOUS)
    add("ambiguous_effect_plus_retry", ctx, truth)

    ctx = make_context(Scope.LIVE, Intent.INTERNAL_REPAIR, 8)
    truth = replace(Truth(), serving_fresh=False)
    add("stale_serving_state_plus_valid_workflow_repair", ctx, truth)

    ctx = make_context(Scope.LIVE, Intent.REDISPATCH_EFFECT, 9)
    truth = replace(Truth(), effect_state=EffectState.CERTIFIED_NO_EFFECT, delivery_fence_present=False)
    add("certified_no_effect_plus_missing_delivery_fence", ctx, truth)

    ctx = make_context(Scope.LIVE, Intent.REDISPATCH_EFFECT, 10)
    truth = replace(Truth(), effect_state=EffectState.CONFIRMED_ONCE)
    add("confirmed_effect_plus_retry_request", ctx, truth)

    ctx = make_context(Scope.OFFLINE, Intent.INTERNAL_REPAIR, 11)
    truth = replace(Truth(), identity_current=False)
    add("stale_identity_checkpoint_plus_healthy_transparency", ctx, truth)

    ctx = make_context(Scope.OFFLINE, Intent.INTERNAL_REPAIR, 12)
    truth = Truth()
    add("checkpoint_scope_rotation_mismatch", ctx, truth, lambda b: replace(b, checkpoint=replace(b.checkpoint, claim_scope_id="old-agent-scope")))

    ctx = make_context(Scope.LIVE, Intent.REDISPATCH_EFFECT, 13)
    truth = replace(Truth(), action_binding_match=False)
    add("action_binding_mismatch_plus_current_authorization", ctx, truth)

    ctx = make_context(Scope.LIVE, Intent.REDISPATCH_EFFECT, 14)
    truth = replace(Truth(), authorization_epoch_current=False)
    add("stale_authorization_epoch_plus_current_status_bit", ctx, truth, lambda b: replace(b, authorization=replace(b.authorization, state=AuthState.CURRENT, grant_epoch=ctx.active_authorization_epoch - 1)))

    ctx = make_context(Scope.LIVE, Intent.INTERNAL_REPAIR, 15)
    truth = replace(Truth(), runtime_closure_exact=False, static_overapprox_complete=True)
    add("runtime_miss_plus_complete_static_overapprox", ctx, truth)

    return out


def truth_random(rng: random.Random):
    scope = rng.choice(list(Scope))
    intent = rng.choices(list(Intent), weights=[0.50, 0.20, 0.30], k=1)[0]
    seed = rng.randrange(1, 10**9)
    ctx = make_context(scope, intent, seed)
    effect = rng.choices(list(EffectState), weights=[0.48, 0.20, 0.16, 0.11, 0.05], k=1)[0]
    auth = rng.choices(list(AuthState), weights=[0.74, 0.22, 0.04], k=1)[0]
    return ctx, Truth(
        history_ok=rng.random() < 0.96,
        identity_current=rng.random() < 0.97,
        capture_epoch_current=rng.random() < 0.97,
        topology_current=rng.random() < 0.97,
        hidden_effect_capable_surface=rng.random() < 0.05,
        runtime_closure_exact=rng.random() < 0.76,
        static_overapprox_complete=rng.random() < 0.92,
        action_binding_match=rng.random() < 0.98,
        authorization_state=auth,
        authorization_epoch_current=rng.random() < 0.97,
        effect_state=effect,
        delivery_fence_present=rng.random() < 0.90,
        recorded_result_binding_match=rng.random() < 0.98,
        serving_fresh=rng.random() < 0.98,
    )


def degrade_bundle(ctx: Context, b: Bundle, rng: random.Random) -> Bundle:
    """Omission/replay-only attacker: never forges a fresh positive signature."""
    ops = []
    if ctx.scope == Scope.LIVE:
        ops += ["drop_receiver", "truncate_presented_chain"]
    else:
        ops += ["drop_checkpoint", "single_inclusion", "stale_checkpoint_scope", "stale_checkpoint_identity"]
    ops += [
        "drop_identity", "replay_old_identity", "drop_manifest", "replay_old_census",
        "drop_census", "replay_old_dependency", "drop_static", "replay_old_authorization",
        "drop_authorization", "drop_effect", "stale_serving",
    ]
    chosen = rng.sample(ops, k=min(rng.randint(0, 4), len(ops)))
    out = b
    for op in chosen:
        if op == "drop_receiver": out = replace(out, receiver_head=None)
        elif op == "truncate_presented_chain" and len(out.receipts) > 1: out = replace(out, receipts=out.receipts[:-1])
        elif op == "drop_checkpoint": out = replace(out, checkpoint=None)
        elif op == "single_inclusion" and out.transparency is not None: out = replace(out, transparency=replace(out.transparency, consistency_monitored=False))
        elif op == "stale_checkpoint_scope" and out.checkpoint is not None: out = replace(out, checkpoint=replace(out.checkpoint, claim_scope_id="old-scope"))
        elif op == "stale_checkpoint_identity" and out.checkpoint is not None: out = replace(out, checkpoint=replace(out.checkpoint, identity_epoch=ctx.active_identity_epoch - 1))
        elif op == "drop_identity": out = replace(out, identity=None)
        elif op == "replay_old_identity" and out.identity is not None: out = replace(out, identity=replace(out.identity, identity_epoch=ctx.active_identity_epoch - 1))
        elif op == "drop_manifest": out = replace(out, manifest=None)
        elif op == "replay_old_census" and out.census is not None: out = replace(out, census=SurfaceCensus(ctx.active_manifest_epoch - 1, "old-topology", tuple(s for s in out.census.surfaces_seen if s != "wrapper-x"), True, False))
        elif op == "drop_census": out = replace(out, census=None)
        elif op == "replay_old_dependency" and out.dependency is not None: out = replace(out, dependency=replace(out.dependency, epoch=ctx.active_manifest_epoch - 1, complete_closure=True))
        elif op == "drop_static": out = replace(out, static_decl=None)
        elif op == "replay_old_authorization" and out.authorization is not None: out = replace(out, authorization=replace(out.authorization, grant_epoch=ctx.active_authorization_epoch - 1, state=AuthState.CURRENT))
        elif op == "drop_authorization": out = replace(out, authorization=None)
        elif op == "drop_effect": out = replace(out, effect=None)
        elif op == "stale_serving" and out.serving is not None: out = replace(out, serving=replace(out.serving, serving_epoch=ctx.current_serving_epoch - 1, fresh_rebind=True))
    return out


def positive_event_losses(ctx: Context, b: Bundle):
    out = []
    if ctx.scope == Scope.LIVE and b.receiver_head is not None: out.append(replace(b, receiver_head=None))
    if ctx.scope == Scope.OFFLINE:
        if b.checkpoint is not None: out.append(replace(b, checkpoint=None))
        if b.transparency is not None and b.transparency.consistency_monitored: out.append(replace(b, transparency=replace(b.transparency, consistency_monitored=False)))
    if b.identity is not None: out.append(replace(b, identity=None))
    if b.manifest is not None: out.append(replace(b, manifest=None))
    if b.census is not None: out.append(replace(b, census=None))
    if b.dependency is not None and b.dependency.complete_closure: out.append(replace(b, dependency=replace(b.dependency, complete_closure=False)))
    if b.static_decl is not None and b.static_decl.complete_overapprox: out.append(replace(b, static_decl=replace(b.static_decl, complete_overapprox=False)))
    if b.authorization is not None: out.append(replace(b, authorization=None))
    if b.effect is not None: out.append(replace(b, effect=None))
    if b.serving is not None and b.serving.fresh_rebind: out.append(replace(b, serving=replace(b.serving, fresh_rebind=False)))
    return out


def main():
    cases = named_cases()
    policies = {
        "event_constructor": construct,
        "absence_as_safe": absence_as_safe,
        "current_auth_everywhere": current_auth_everywhere,
    }
    named = {}
    rows = []
    for pname, fn in policies.items():
        match = unsafe = over = 0
        for name, ctx, truth, bundle in cases:
            expected = oracle(ctx, truth)
            got = fn(ctx, bundle)
            if got == expected: match += 1
            elif more_permissive(got, expected): unsafe += 1
            else: over += 1
            rows.append({"case": name, "policy": pname, "oracle_repair": expected.repair.name, "oracle_effect": expected.effect.name, "got_repair": got.repair.name, "got_effect": got.effect.name})
        named[pname] = {"exact": match, "unsafe": unsafe, "overconservative": over}

    rng = random.Random(202608280500)
    fuzz = {p: {"exact": 0, "unsafe": 0, "overconservative": 0} for p in policies}
    fuzz_n = 100000
    safe_result_replay = strict_result_replay_blocks = constructor_result_replay_accepts = 0
    for i in range(fuzz_n):
        ctx, truth = truth_random(rng)
        bundle = degrade_bundle(ctx, honest_bundle(ctx, truth, i + 1000), rng)
        expected = oracle(ctx, truth)
        for pname, fn in policies.items():
            got = fn(ctx, bundle)
            if got == expected: fuzz[pname]["exact"] += 1
            elif more_permissive(got, expected): fuzz[pname]["unsafe"] += 1
            else: fuzz[pname]["overconservative"] += 1
        if (ctx.intent == Intent.REPLAY_RECORDED_RESULT and truth.effect_state == EffectState.CONFIRMED_ONCE and truth.recorded_result_binding_match and truth.authorization_state == AuthState.CONSUMED and oracle(ctx, truth).repair != RepairScope.BLOCK):
            safe_result_replay += 1
            if construct(ctx, bundle).effect == EffectPerm.REPLAY_RESULT_ONLY: constructor_result_replay_accepts += 1
            if current_auth_everywhere(ctx, bundle).repair == RepairScope.BLOCK: strict_result_replay_blocks += 1

    honest_replay_total = 5000
    honest_replay_event_accepts = honest_replay_strict_blocks = 0
    for j in range(honest_replay_total):
        ctx = make_context(Scope.LIVE, Intent.REPLAY_RECORDED_RESULT, 900000 + j)
        truth = replace(Truth(), authorization_state=AuthState.CONSUMED, effect_state=EffectState.CONFIRMED_ONCE)
        b = honest_bundle(ctx, truth, 900000 + j)
        if construct(ctx, b).effect == EffectPerm.REPLAY_RESULT_ONLY: honest_replay_event_accepts += 1
        if current_auth_everywhere(ctx, b).repair == RepairScope.BLOCK: honest_replay_strict_blocks += 1

    rng2 = random.Random(202608280501)
    mono_samples = 20000
    mono_checks = mono_violations = used = 0
    while used < mono_samples:
        ctx, truth = truth_random(rng2)
        expected = oracle(ctx, truth)
        if expected.repair == RepairScope.BLOCK: continue
        b = honest_bundle(ctx, truth, used + 500000)
        before = construct(ctx, b)
        if before.repair == RepairScope.BLOCK: continue
        used += 1
        for degraded in positive_event_losses(ctx, b):
            mono_checks += 1
            after = construct(ctx, degraded)
            if more_permissive(after, before): mono_violations += 1

    print(json.dumps({
        "schema_version": 1,
        "scope": "Synthetic concrete-event mechanism/conformance study; counts are not deployment probabilities.",
        "named_case_count": len(cases),
        "named": named,
        "multi_fault_fuzz": {"seed": 202608280500, "episodes": fuzz_n, "policies": fuzz},
        "result_replay_slice": {"safe_consumed_auth_confirmed_result_replay_episodes": safe_result_replay, "event_constructor_permitted": constructor_result_replay_accepts, "current_auth_everywhere_blocked": strict_result_replay_blocks, "note": "Counts are after omission/replay attacks; constructor acceptance requires surviving bound result evidence."},
        "honest_result_replay_slice": {"episodes": honest_replay_total, "event_constructor_permitted": honest_replay_event_accepts, "current_auth_everywhere_blocked": honest_replay_strict_blocks, "scope": "Synthetic exact confirmed-result replay only; no provider redispatch."},
        "evidence_loss_monotonicity": {"seed": 202608280501, "safe_honest_bundles": used, "one_positive_event_loss_checks": mono_checks, "violations": mono_violations},
        "rows": rows,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
