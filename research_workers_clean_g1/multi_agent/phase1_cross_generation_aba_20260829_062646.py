#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

OPS=["cancel","compensate"]
G1_STATES=["PENDING","APPLIED"]
G2_STATES=["PENDING","APPLIED"]
RESPONSES=["clear_applied","ambiguous_applied","ambiguous_absent"]

def scenarios():
    keys=["old_op","g1_state","g2_state","historical_addressable",
          "repair_quiescent","response","takeover","dedupe_valid",
          "tombstone_present"]
    out=[]
    for vals in product(
        OPS,G1_STATES,G2_STATES,[False,True],[False,True],
        RESPONSES,[False,True],[False,True],[False,True]
    ):
        out.append(dict(zip(keys,vals)))
    return out

def legitimate_old_op(s):
    if s["repair_quiescent"]:
        return False
    return (
        (s["old_op"]=="cancel" and s["g1_state"]=="PENDING") or
        (s["old_op"]=="compensate" and s["g1_state"]=="APPLIED")
    )

def first_applied(s):
    return s["response"] in ("clear_applied","ambiguous_applied")

def eventual_apply_on_retry(s,retry):
    if first_applied(s):
        return True
    return s["response"]=="ambiguous_absent" and s["takeover"] and retry

def classify(terminal=False,mis_cancel=False,mis_comp=False,dup_comp=False,
             false_terminal=False,orphan=False,unresolved=False):
    unsafe=mis_cancel or mis_comp or dup_comp or false_terminal
    safe_terminal=terminal and not unsafe and not orphan and not unresolved
    return dict(
        terminal=terminal,safe_terminal=safe_terminal,unsafe=unsafe,
        mis_cancel=mis_cancel,mis_compensation=mis_comp,
        duplicate_compensation=dup_comp,
        false_terminal_g1=false_terminal,
        orphan_repair=orphan,unresolved=unresolved,
    )

def logical_key_reuse(s):
    legit=legitimate_old_op(s)
    retry=s["response"].startswith("ambiguous") and s["takeover"]
    applied=eventual_apply_on_retry(s,retry)
    mis_cancel=(
        applied and s["old_op"]=="cancel" and s["g2_state"]=="PENDING"
    )
    mis_comp=(
        applied and s["old_op"]=="compensate" and s["g2_state"]=="APPLIED"
    )
    dup=(
        s["old_op"]=="compensate" and s["g2_state"]=="APPLIED" and
        s["response"]=="ambiguous_applied" and s["takeover"] and
        not s["dedupe_valid"]
    )
    terminal=applied or s["response"]=="clear_applied"
    false_term=terminal and legit
    if not terminal and legit:
        return classify(orphan=True,unresolved=True)
    return classify(
        terminal=terminal,mis_cancel=mis_cancel,mis_comp=mis_comp,
        dup_comp=dup,false_terminal=false_term,
        unresolved=(not terminal and not legit),
    )

def unique_per_generation(s):
    legit=legitimate_old_op(s)
    if not legit:
        return classify(terminal=True)
    if not s["historical_addressable"]:
        return classify(orphan=True,unresolved=True)
    if s["response"]=="clear_applied":
        return classify(terminal=True)
    if s["response"]=="ambiguous_applied":
        if s["takeover"]:
            if s["dedupe_valid"] or s["old_op"]=="cancel":
                return classify(terminal=True)
            return classify(terminal=True,dup_comp=True)
        return classify(unresolved=True)
    if s["takeover"]:
        return classify(terminal=True)
    return classify(unresolved=True)

def watermark_only(s):
    if legitimate_old_op(s):
        return classify(orphan=True,unresolved=True)
    return classify(terminal=True)

def tombstone_per_incarnation(s):
    legit=legitimate_old_op(s)
    if not legit:
        return classify(terminal=True)
    if not s["tombstone_present"]:
        return classify(orphan=True,unresolved=True)
    if s["response"] in ("clear_applied","ambiguous_applied"):
        return classify(terminal=True)
    if s["takeover"]:
        return classify(terminal=True)
    return classify(unresolved=True)

def safe_archive(s):
    legit=legitimate_old_op(s)
    if not legit:
        # A logical-slot minimum-generation fence may safely reject old work
        # only after historical repair for g1 is quiescent/not needed.
        return classify(terminal=True)
    route=s["historical_addressable"] or s["tombstone_present"]
    if not route:
        return classify(orphan=True,unresolved=True)
    if s["response"]=="clear_applied":
        return classify(terminal=True)
    if s["response"]=="ambiguous_applied":
        if s["tombstone_present"]:
            return classify(terminal=True)
        if s["takeover"] and s["dedupe_valid"]:
            return classify(terminal=True)
        return classify(unresolved=True)
    if s["takeover"]:
        if s["tombstone_present"] or s["dedupe_valid"]:
            return classify(terminal=True)
        return classify(unresolved=True)
    return classify(unresolved=True)

POLICIES={
    "logical_key_reuse":logical_key_reuse,
    "unique_per_generation":unique_per_generation,
    "watermark_only":watermark_only,
    "tombstone_per_incarnation":tombstone_per_incarnation,
    "safe_archive":safe_archive,
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

def select(ss,pred):
    return [s for s in ss if pred(s)]

def main():
    ss=scenarios()
    result={
        "schema_version":1,
        "model":"cross-generation cancel/compensation ABA finite mechanism lattice",
        "scenario_count":len(ss),
        "aggregate":aggregate(ss),
        "targeted_slices":{
            "legitimate_historical_repair_remains":aggregate(select(
                ss,legitimate_old_op
            )),
            "historical_repair_quiescent":aggregate(select(
                ss,lambda s:s["repair_quiescent"]
            )),
            "current_g2_vulnerable_to_old_logical_key_action":aggregate(select(
                ss,lambda s:
                (s["old_op"]=="cancel" and s["g2_state"]=="PENDING") or
                (s["old_op"]=="compensate" and s["g2_state"]=="APPLIED")
            )),
            "ambiguous_old_comp_applied_takeover_dedupe_expired":aggregate(select(
                ss,lambda s:
                s["old_op"]=="compensate" and legitimate_old_op(s) and
                s["response"]=="ambiguous_applied" and s["takeover"] and
                not s["dedupe_valid"] and s["historical_addressable"]
            )),
            "no_historical_route_or_tombstone":aggregate(select(
                ss,lambda s:
                legitimate_old_op(s) and
                not s["historical_addressable"] and
                not s["tombstone_present"]
            )),
        },
        "notes":[
            "Equal-weight synthetic mechanism counts, not production incident rates.",
            "Logical-key reuse intentionally models ABA: generation g1 and g2 share a mutable logical handle.",
            "A minimum-generation watermark prevents old-generation actions from touching g2, but watermark-only also rejects still-legitimate historical g1 repair.",
            "Per-incarnation routing/tombstones preserve historical repair identity; dedupe retention remains a separate retry proof.",
            "The safe archive compacts to a logical-slot watermark only when historical repair is quiescent/not needed."
        ]
    }
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
