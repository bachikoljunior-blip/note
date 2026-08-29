from itertools import product
import json

AUTH = [("none", False)] + [(t, w) for t in ("before_winner","between_winner_loser","after_loser") for w in (False, True)]
RESP = [(False, False), (True, False), (True, True)]
STRATEGIES = ["blind_last_writer","cas_drop","cas_preserve_intent","append_index_fenced","fail_closed_authority"]

def scenarios():
    i = 0
    for (timing,new_writer), relation, (winner_loss,winner_crash), loser_retry, merge_loss in product(
        AUTH, ("compatible","conflicting"), RESP, (False,True), (False,True)
    ):
        i += 1
        yield dict(id=i, authority_timing=timing, new_authority_latest=new_writer,
                   relation=relation, winner_response_lost=winner_loss,
                   winner_crash_after_loss=winner_crash,
                   loser_retry_after_conflict=loser_retry,
                   merge_response_lost=merge_loss)

def change_authority(st, new_writer):
    st["authority"] = "A1"
    if new_writer:
        st["latest_token"] += 1
        st["latest_contrib"] = []
        st["latest_label"] = "N"

def write_latest(st, label, contrib, expected=None, blind=False):
    if not blind and expected != st["latest_token"]:
        return False
    if st["authority"] != "A0":
        st["stale"] += 1
    st["latest_token"] += 1
    st["latest_contrib"] = list(contrib)
    st["latest_label"] = label
    return True

def lost(st):
    seen = set(st["refs"]) | {c for c in st["latest_contrib"] if c in ("C1","C2")}
    return sum(c not in seen for c in ("C1","C2"))

def run(sc, strategy):
    st = dict(authority="A0", latest_token=0, latest_contrib=[], latest_label="L0",
              refs=set(), stale=0, duplicate=0, io=0, pending=0)
    if strategy == "append_index_fenced":
        st["refs"].update(("C1","C2")); st["io"] += 2

    if sc["authority_timing"] == "before_winner":
        change_authority(st, sc["new_authority_latest"])

    if strategy == "blind_last_writer":
        write_latest(st,"C1",["C1"],blind=True); st["io"] += 1; r1=True
    elif strategy in ("cas_drop","cas_preserve_intent"):
        r1=write_latest(st,"C1",["C1"],expected=0); st["io"] += 1
        if not r1 and strategy == "cas_preserve_intent":
            st["refs"].add("C1"); st["io"] += 2; st["pending"] += 1
    elif strategy == "fail_closed_authority":
        st["io"] += 1
        if st["authority"] != "A0":
            r1=False; st["refs"].add("C1"); st["io"] += 1; st["pending"] += 1
        else:
            r1=write_latest(st,"C1",["C1"],expected=0); st["io"] += 1
            if not r1:
                st["refs"].add("C1"); st["io"] += 1; st["pending"] += 1
    else:
        r1=False

    if sc["authority_timing"] == "between_winner_loser":
        change_authority(st, sc["new_authority_latest"])

    if strategy == "blind_last_writer":
        write_latest(st,"C2",["C2"],blind=True); st["io"] += 1
    elif strategy in ("cas_drop","cas_preserve_intent"):
        r2=write_latest(st,"C2",["C2"],expected=0); st["io"] += 1
        if not r2 and strategy == "cas_preserve_intent":
            st["refs"].add("C2")
            st["refs"].update(c for c in st["latest_contrib"] if c in ("C1","C2"))
            st["io"] += 2; st["pending"] += 1
    elif strategy == "fail_closed_authority":
        st["io"] += 1
        if st["authority"] != "A0":
            st["refs"].add("C2"); st["io"] += 1; st["pending"] += 1
        else:
            r2=write_latest(st,"C2",["C2"],expected=0); st["io"] += 1
            if not r2:
                st["refs"].add("C2"); st["io"] += 1; st["pending"] += 1

    if sc["authority_timing"] == "after_loser":
        change_authority(st, sc["new_authority_latest"])

    if strategy == "blind_last_writer":
        if sc["loser_retry_after_conflict"]:
            write_latest(st,"C2-retry",["C2"],blind=True); st["io"] += 1
        if sc["winner_response_lost"]:
            if sc["winner_crash_after_loss"]:
                write_latest(st,"C1-recovery",["C1"],blind=True); st["io"] += 1
            else:
                st["io"] += 1

    elif strategy == "cas_drop":
        if sc["winner_response_lost"] and r1 and not sc["winner_crash_after_loss"]:
            st["io"] += 1

    elif strategy == "cas_preserve_intent":
        if sc["winner_response_lost"] and r1 and not sc["winner_crash_after_loss"]:
            st["io"] += 1
        visible = st["refs"] | {c for c in st["latest_contrib"] if c in ("C1","C2")}
        if sc["relation"] == "compatible" and st["authority"] == "A0" and {"C1","C2"} <= visible:
            st["io"] += 3
            write_latest(st,"M12",["C1","C2"],expected=st["latest_token"])
            st["refs"].update(("C1","C2")); st["pending"] = 0
            if sc["merge_response_lost"] and sc["loser_retry_after_conflict"]:
                st["io"] += 2
                write_latest(st,"M12-dup",["C1","C2","C2"],expected=st["latest_token"])
                st["duplicate"] += 1

    elif strategy == "append_index_fenced":
        st["io"] += 2
        if st["authority"] == "A0":
            write_latest(st, "M12" if sc["relation"]=="compatible" else "C1-selected",
                         ["C1","C2"] if sc["relation"]=="compatible" else ["C1"],
                         expected=st["latest_token"])
            st["io"] += 1
            if sc["merge_response_lost"]:
                st["io"] += 1
            if sc["merge_response_lost"] and sc["loser_retry_after_conflict"]:
                st["io"] += 1
        else:
            st["pending"] += 1

    elif strategy == "fail_closed_authority":
        if sc["winner_response_lost"] and r1 and not sc["winner_crash_after_loss"]:
            st["io"] += 1
            if "C1" not in st["latest_contrib"]:
                st["refs"].add("C1"); st["io"] += 1; st["pending"] += 1

    return dict(**sc, strategy=strategy, semantic_result_loss=lost(st),
                duplicate_integration=st["duplicate"], stale_current_selection=st["stale"],
                coord_io=st["io"], pending_branches=st["pending"])

def aggregate(rows):
    out={}
    for s in STRATEGIES:
        rr=[r for r in rows if r["strategy"]==s]
        out[s]=dict(
            scenarios=len(rr),
            semantic_result_loss_scenarios=sum(r["semantic_result_loss"]>0 for r in rr),
            semantic_results_lost_total=sum(r["semantic_result_loss"] for r in rr),
            duplicate_integration_scenarios=sum(r["duplicate_integration"]>0 for r in rr),
            stale_selection_scenarios=sum(r["stale_current_selection"]>0 for r in rr),
            stale_selection_events=sum(r["stale_current_selection"] for r in rr),
            avg_coord_io=sum(r["coord_io"] for r in rr)/len(rr),
            max_coord_io=max(r["coord_io"] for r in rr),
            pending_scenarios=sum(r["pending_branches"]>0 for r in rr),
        )
    return out

if __name__ == "__main__":
    sc=list(scenarios())
    rows=[run(x,s) for x in sc for s in STRATEGIES]
    print(json.dumps({"scenario_count":len(sc),"strategy_evaluations":len(rows),
                      "strategies":aggregate(rows)}, indent=2, sort_keys=True))
