#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

EFFECT_POINTS = ["before_seen","while_pending","concurrent","after_applied","after_failed"]

def valid_cancel_variants(point, cap):
    if cap and point in ("before_seen","while_pending","concurrent"):
        out=[]
        for obs in ["clear_canceled","clear_not_canceled"]:
            out.append((obs, True))
        for obs in ["ambiguous_canceled","ambiguous_not_canceled"]:
            for vis in [False,True]:
                out.append((obs,vis))
        return out
    return [("unsupported_or_too_late", True)]

def valid_comp_variants(reverse_cap):
    if not reverse_cap:
        return [dict(comp_dedupe=False, comp_obs="unsupported",
                     comp_finality="none", comp_status_visible=False)]
    out=[]
    for dedupe, obs, fin, vis in product(
        [False,True],
        ["clear_applied","ambiguous_applied","ambiguous_absent"],
        ["succeeded","failed","reversed","pending"],
        [False,True],
    ):
        out.append(dict(comp_dedupe=dedupe, comp_obs=obs,
                        comp_finality=fin, comp_status_visible=vis))
    return out

def scenarios():
    out=[]
    for point, ccap, rcap, takeover in product(
        EFFECT_POINTS,[False,True],[False,True],[False,True]
    ):
        for cobs,cvis in valid_cancel_variants(point,ccap):
            for cv in valid_comp_variants(rcap):
                out.append(dict(effect_point=point,sink_cancel_cap=ccap,
                                reverse_cap=rcap,takeover=takeover,
                                cancel_obs=cobs,cancel_status_visible=cvis,**cv))
    return out

def cancel_state(s):
    p=s["effect_point"]; obs=s["cancel_obs"]
    if p=="after_failed": return ("FAILED",False,True)
    if p=="after_applied": return ("APPLIED",False,True)
    if obs=="clear_canceled": return ("CANCELED",True,True)
    if obs=="clear_not_canceled":
        return ("APPLIED" if p=="concurrent" else "MAY_APPLY",False,True)
    if obs=="ambiguous_canceled":
        return ("CANCELED",False,s["cancel_status_visible"])
    if obs=="ambiguous_not_canceled":
        return ("APPLIED" if p=="concurrent" else "MAY_APPLY",
                False,s["cancel_status_visible"])
    return ("APPLIED" if p=="concurrent" else "MAY_APPLY",False,True)

def materialize_effect(state, continue_delivery=True):
    if state=="MAY_APPLY":
        return "APPLIED" if continue_delivery else "LOST"
    return state

def compensation(s, retry_on_ambiguous):
    if not s["reverse_cap"]:
        return dict(any_applied=False,duplicate=False,finality_known=False,
                    finality=None,retried=False)
    obs=s["comp_obs"]
    first_applied=obs in ("clear_applied","ambiguous_applied")
    duplicate=False; retried=False
    if obs.startswith("ambiguous") and s["takeover"] and retry_on_ambiguous:
        retried=True
        if first_applied and not s["comp_dedupe"]:
            duplicate=True
        elif not first_applied:
            first_applied=True
    finality_known=first_applied and (
        s["comp_status_visible"] or obs=="clear_applied"
    )
    return dict(any_applied=first_applied,duplicate=duplicate,
                finality_known=finality_known,
                finality=s["comp_finality"] if first_applied else None,
                retried=retried)

def classify(terminal,canceled_claim,effect_final,comp=None,lost=False,unresolved=False):
    dup=bool(comp and comp["duplicate"])
    residual=(effect_final=="APPLIED")
    if comp and comp["any_applied"] and comp["finality_known"]:
        if comp["finality"]=="succeeded":
            residual=False
        elif comp["finality"] in ("failed","reversed"):
            residual=True
    false_terminal=terminal and canceled_claim and (
        residual or lost or dup or unresolved
    )
    unsafe=false_terminal or lost or dup
    safe_terminal=terminal and not unsafe and not unresolved and not residual
    return dict(terminal=terminal,safe_terminal=safe_terminal,unsafe=unsafe,
                false_terminal=false_terminal,residual_exposure=residual,
                lost_authorized_effect=lost,duplicate_compensation=dup,
                unresolved=unresolved)

def pretend_revocation(s):
    p=s["effect_point"]
    if p in ("before_seen","while_pending"): ef="LOST"
    elif p in ("concurrent","after_applied"): ef="APPLIED"
    else: ef="FAILED"
    return classify(True,True,ef,lost=ef=="LOST")

def cancel_if_pending(s):
    st,confirmed,known=cancel_state(s)
    if (s["sink_cancel_cap"] and
        s["effect_point"] in ("before_seen","while_pending","concurrent") and
        s["cancel_obs"] in ("clear_canceled","ambiguous_canceled",
                            "ambiguous_not_canceled")):
        ef=materialize_effect(st,True)
        unresolved=(
            s["cancel_obs"]=="ambiguous_not_canceled" or
            (s["cancel_obs"]=="ambiguous_canceled" and
             not s["cancel_status_visible"])
        )
        return classify(True,True,ef,unresolved=unresolved)
    ef=materialize_effect(st,True)
    if ef=="FAILED": return classify(True,True,"FAILED")
    return classify(False,False,ef)

def compensate_after_apply(s):
    st,confirmed,known=cancel_state(s)
    if st=="CANCELED" and (confirmed or known):
        return classify(True,True,"CANCELED")
    ef=materialize_effect(st,True)
    if ef=="FAILED": return classify(True,True,"FAILED")
    if ef=="APPLIED" and s["reverse_cap"]:
        c=compensation(s,retry_on_ambiguous=True)
        if c["any_applied"]:
            unresolved=not(
                c["finality_known"] and c["finality"]=="succeeded"
            )
            return classify(True,True,ef,comp=c,unresolved=unresolved)
        return classify(False,False,ef,comp=c,unresolved=True)
    return classify(False,False,ef,
                    unresolved=(not known and
                                s["cancel_obs"].startswith("ambiguous")))

def manual_irreversibility(s):
    st,confirmed,known=cancel_state(s)
    if st=="CANCELED" and (confirmed or known):
        return classify(True,True,"CANCELED")
    ef=materialize_effect(st,True)
    if ef=="FAILED": return classify(True,True,"FAILED")
    return classify(False,False,ef,
                    unresolved=(not known and
                                s["cancel_obs"].startswith("ambiguous")))

def safe_archive(s):
    st,confirmed,known=cancel_state(s)
    if st=="CANCELED" and (confirmed or known):
        return classify(True,True,"CANCELED")
    ef=materialize_effect(st,True)
    if ef=="FAILED": return classify(True,True,"FAILED")
    if not known and s["cancel_obs"]=="ambiguous_canceled":
        return classify(False,False,"CANCELED",unresolved=True)
    if ef=="APPLIED" and s["reverse_cap"]:
        c=compensation(s,retry_on_ambiguous=s["comp_dedupe"])
        if c["duplicate"]:
            return classify(False,False,ef,comp=c,unresolved=True)
        if (c["any_applied"] and c["finality_known"] and
            c["finality"]=="succeeded"):
            return classify(True,True,ef,comp=c)
        return classify(False,False,ef,comp=c,unresolved=True)
    return classify(False,False,ef,
                    unresolved=(not known and
                                s["cancel_obs"].startswith("ambiguous")))

POLICIES = {
    "pretend_revocation": pretend_revocation,
    "cancel_if_pending": cancel_if_pending,
    "compensate_after_apply": compensate_after_apply,
    "manual_irreversibility": manual_irreversibility,
    "safe_archive": safe_archive,
}

def aggregate(ss):
    out={}
    for name,fn in POLICIES.items():
        c=Counter(n=len(ss))
        for s in ss:
            r=fn(s)
            for k,v in r.items():
                if v is True:
                    c[k]+=1
        out[name]=dict(c)
    return out

def select(ss, pred):
    return [s for s in ss if pred(s)]

def main():
    ss=scenarios()
    result={
        "schema_version":1,
        "model":"authorization-cancel-compensation finite mechanism lattice",
        "scenario_count":len(ss),
        "aggregate":aggregate(ss),
        "targeted_slices":{
            "concurrent_cancel_apply_race":aggregate(select(
                ss,lambda s:s["effect_point"]=="concurrent"
                and s["sink_cancel_cap"]
            )),
            "ambiguous_cancel_actually_not_canceled":aggregate(select(
                ss,lambda s:s["effect_point"] in
                ("before_seen","while_pending","concurrent")
                and s["sink_cancel_cap"]
                and s["cancel_obs"]=="ambiguous_not_canceled"
            )),
            "ambiguous_cancel_canceled_but_unobservable":aggregate(select(
                ss,lambda s:s["effect_point"] in
                ("before_seen","while_pending","concurrent")
                and s["sink_cancel_cap"]
                and s["cancel_obs"]=="ambiguous_canceled"
                and not s["cancel_status_visible"]
            )),
            "ambiguous_compensation_applied_takeover_no_dedupe":aggregate(select(
                ss,lambda s:s["effect_point"]=="after_applied"
                and s["reverse_cap"] and
                s["comp_obs"]=="ambiguous_applied" and s["takeover"]
                and not s["comp_dedupe"]
            )),
            "compensation_late_failed_reversed_or_pending":aggregate(select(
                ss,lambda s:s["effect_point"]=="after_applied"
                and s["reverse_cap"] and
                s["comp_obs"] in ("clear_applied","ambiguous_applied")
                and s["comp_finality"] in ("failed","reversed","pending")
            )),
            "compensation_authoritatively_succeeded":aggregate(select(
                ss,lambda s:s["effect_point"]=="after_applied"
                and s["reverse_cap"] and
                s["comp_obs"] in ("clear_applied","ambiguous_applied")
                and s["comp_finality"]=="succeeded" and
                (s["comp_status_visible"] or s["comp_obs"]=="clear_applied")
            )),
        },
        "notes":[
            "Equal-weight synthetic mechanism counts, not production incident rates.",
            "AUTHORIZED(effect_id) is irrevocable in X; cancellation is a new operation, not retroactive claim revocation.",
            "safe_archive terminalizes only after authoritative cancel success, terminal effect failure, or authoritative successful compensation finality.",
            "safe_archive retries ambiguous compensation after takeover only when a durable dedupe contract is present.",
            "Residual exposure on a nonterminal/manual branch is tracked separately from unsafe terminalization."
        ]
    }
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
