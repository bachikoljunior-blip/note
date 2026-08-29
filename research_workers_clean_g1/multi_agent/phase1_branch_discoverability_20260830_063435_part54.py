from itertools import product
import json

NVALS=(2,8,32)
LISTING=("complete","truncated_recovered","interrupted")
STRATEGIES=("mutable_index_root","checkpoint_tree_enumeration","sharded_manifests","latest_parent_dag","pending_receipts")

def scenarios():
    i=0
    for n,retry,resp,listing,orphan,dup,auth,old in product(
        NVALS,(False,True),(False,True),LISTING,(False,True),(False,True),(False,True),(False,True)
    ):
        i+=1
        yield dict(id=i,n_branches=n,root_retry=retry,index_response_lost=resp,
                   listing_state=listing,orphan_index_or_manifest=orphan,
                   duplicate_manifest=dup,authority_change_during_discovery=auth,
                   old_pending_branch=old)

def run(sc,strategy):
    n=sc["n_branches"]; reads=1; mutable=0; missing=0; fail=False
    if strategy=="mutable_index_root":
        attempted=n-(1 if sc["orphan_index_or_manifest"] else 0)
        discovered=attempted if sc["root_retry"] else min(attempted,1)
        missing=n-discovered
        mutable=attempted
        if sc["root_retry"] and attempted>1:
            mutable += attempted-1
            reads += attempted-1
        if sc["index_response_lost"]:
            reads += 1
    elif strategy=="checkpoint_tree_enumeration":
        if sc["listing_state"]=="complete":
            reads += 1
        elif sc["listing_state"]=="truncated_recovered":
            reads += 4
        else:
            reads += 2; missing=1; fail=True
    elif strategy=="sharded_manifests":
        missing=1 if sc["orphan_index_or_manifest"] else 0
        if sc["listing_state"]=="complete":
            reads += min(4,n)
        elif sc["listing_state"]=="truncated_recovered":
            reads += min(8,n+2)
        else:
            reads += 2; missing=max(1,missing); fail=True
        if sc["index_response_lost"]:
            reads += 1
    elif strategy=="latest_parent_dag":
        missing=max(0,n-1); reads += 1
    elif strategy=="pending_receipts":
        missing=1 if sc["orphan_index_or_manifest"] else 0
        if sc["listing_state"]=="complete":
            reads += 1
        elif sc["listing_state"]=="truncated_recovered":
            reads += 4
        else:
            reads += 2; missing=max(1,missing); fail=True
        if sc["index_response_lost"]:
            reads += 1
    if sc["authority_change_during_discovery"]:
        fail=True
    return dict(**sc,strategy=strategy,undiscoverable_branches=missing,
                false_omission_branches=0 if fail else missing,
                duplicate_selection=0,stale_selection=0,
                mutable_hotspot_write_attempts=mutable,recovery_reads=reads,fail_closed=fail)

def aggregate(rows):
    out={}
    for s in STRATEGIES:
        rr=[r for r in rows if r["strategy"]==s]
        out[s]=dict(
            scenarios=len(rr),
            undiscoverable_scenarios=sum(r["undiscoverable_branches"]>0 for r in rr),
            undiscoverable_branches_total=sum(r["undiscoverable_branches"] for r in rr),
            false_omission_scenarios=sum(r["false_omission_branches"]>0 for r in rr),
            false_omission_branches_total=sum(r["false_omission_branches"] for r in rr),
            fail_closed_scenarios=sum(r["fail_closed"] for r in rr),
            avg_mutable_hotspot_write_attempts=sum(r["mutable_hotspot_write_attempts"] for r in rr)/len(rr),
            max_mutable_hotspot_write_attempts=max(r["mutable_hotspot_write_attempts"] for r in rr),
            avg_recovery_reads=sum(r["recovery_reads"] for r in rr)/len(rr),
            max_recovery_reads=max(r["recovery_reads"] for r in rr),
        )
    return out

if __name__=="__main__":
    sc=list(scenarios())
    rows=[run(x,s) for x in sc for s in STRATEGIES]
    print(json.dumps({"scenario_count":len(sc),"strategy_evaluations":len(rows),
                      "strategies":aggregate(rows)},indent=2,sort_keys=True))
