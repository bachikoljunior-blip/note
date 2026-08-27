#!/usr/bin/env python3
import argparse, importlib.util, json
from pathlib import Path
import networkx as nx

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "coalition_seeded_start_predictor_confirm_v1_runner.py"
spec = importlib.util.spec_from_file_location("seed_gate_base", BASE_PATH)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

# Reproducibility repair before any v2 outcome was observed:
# the persisted v1 runner compares truth bitsets across variable relabelings.
# Hamming-rank is permutation invariant, but the raw assignment-indexed truth
# bitset is not. Check each order against an exhaustive direct oracle in that
# order's own relabeled coordinates, and compare only rank across orders.
_orig_compile_order = base.compile_order
def _compile_order_checked(g, order, oracle_rank=None):
    r = _orig_compile_order(g, order, None)
    edges = base.relabeled_edges(g, order)
    direct_truth = base.direct_truth_bits(g.number_of_nodes(), edges)
    if r["truth"] != direct_truth:
        raise AssertionError("direct truth-bitset oracle mismatch")
    if oracle_rank is not None and r["rank"] != oracle_rank:
        raise AssertionError("Hamming-rank oracle mismatch")
    return r
base.compile_order = _compile_order_checked

FAMILY_ORDER = ("cubic", "quartic", "watts", "erdos")
DEFAULT_CASES = {
    "cubic": [884000,884001,884002,884003,884004,884005],
    "quartic": [884100,884101,884102,884103,884104,884105],
    "watts": [884200,884201,884202,884203,884204,884205],
    "erdos": [884300,884301,884302,884303,884304,884305],
}

def make_graph(family, seed):
    n = 16
    if family == "cubic":
        g = nx.random_regular_graph(3, n, seed=seed)
    elif family == "quartic":
        g = nx.random_regular_graph(4, n, seed=seed)
    elif family == "watts":
        g = nx.watts_strogatz_graph(n, 4, 0.2, seed=seed)
    elif family == "erdos":
        g = nx.erdos_renyi_graph(n, 0.25, seed=seed)
    else:
        raise ValueError(f"unknown family {family}")
    return nx.Graph(g)

def run_case(family, seed):
    g = make_graph(family, seed)
    natural = sorted(g.nodes())
    rcm = list(nx.utils.reverse_cuthill_mckee_ordering(g))
    seeded, sw, kd = base.seeded_order(g, seed, natural, rcm)
    ref = base.compile_order(g, natural)
    oracle_rank = ref["rank"]
    two, _ = base.commit_policy(g, {"rcm": rcm, "natural": natural}, oracle_rank)
    three, st3 = base.commit_policy(g, {"rcm": rcm, "natural": natural, "seeded": seeded}, oracle_rank)
    stage_live = [st3["natural"][1]["live"], st3["rcm"][1]["live"], st3["seeded"][1]["live"]]
    label = int(stage_live[2] < stage_live[0] and stage_live[2] < stage_live[1])
    x = base.graph_features(g, natural, rcm, seeded, sw, kd)
    p = base.probability(x)
    pred = int(p >= 0.5)
    width_open = int(sw <= min(base.vsw(g, natural), base.vsw(g, rcm)) + 1)
    learned = three if pred else two
    width = three if width_open else two
    return {
        "family": family, "seed": seed, "label": label, "prob": p, "pred": pred,
        "width_gate_open": bool(width_open),
        "widths": [base.vsw(g, natural), base.vsw(g, rcm), sw],
        "seeded_min_kendall": kd, "stage_live": stage_live,
        "two": [two["live"], two["compiles"]],
        "three": [three["live"], three["compiles"]],
        "learned": [learned["live"], learned["compiles"]],
        "width_plus1": [width["live"], width["compiles"]],
        "learned_regret": learned["live"] - three["live"],
        "width_regret": width["live"] - three["live"],
        "two_regret": two["live"] - three["live"],
        "oracle_ok": True,
    }

def confusion(records, pred_key="pred"):
    tn=fp=fn=tp=0
    for r in records:
        y=r["label"]; p=int(r[pred_key])
        if y==0 and p==0: tn+=1
        elif y==0 and p==1: fp+=1
        elif y==1 and p==0: fn+=1
        else: tp+=1
    return [[tn,fp],[fn,tp]]

def auroc(records):
    pos=[r["prob"] for r in records if r["label"]==1]
    neg=[r["prob"] for r in records if r["label"]==0]
    if not pos or not neg: return None
    wins=0.0
    for p in pos:
        for n in neg:
            wins += 1.0 if p>n else 0.5 if p==n else 0.0
    return wins/(len(pos)*len(neg))

def aggregate(records):
    three_comp=sum(r["three"][1] for r in records)
    learned_comp=sum(r["learned"][1] for r in records)
    width_comp=sum(r["width_plus1"][1] for r in records)
    two_comp=sum(r["two"][1] for r in records)
    def red(x): return 100.0*(three_comp-x)/three_comp if three_comp else 0.0
    return {
        "count":len(records), "positive_count":sum(r["label"] for r in records),
        "learned_open_count":sum(r["pred"] for r in records),
        "learned_open_rate":sum(r["pred"] for r in records)/len(records),
        "prob_min":min(r["prob"] for r in records), "prob_max":max(r["prob"] for r in records),
        "prob_mean":sum(r["prob"] for r in records)/len(records),
        "confusion":confusion(records), "auroc":auroc(records),
        "always_three":{"compiles":three_comp,"live_sum":sum(r["three"][0] for r in records)},
        "learned_gate":{"compiles":learned_comp,"compile_reduction_pct":red(learned_comp),"live_sum":sum(r["learned"][0] for r in records),"regret_sum":sum(r["learned_regret"] for r in records),"max_regret":max(r["learned_regret"] for r in records)},
        "width_plus1":{"compiles":width_comp,"compile_reduction_pct":red(width_comp),"live_sum":sum(r["width_plus1"][0] for r in records),"regret_sum":sum(r["width_regret"] for r in records),"max_regret":max(r["width_regret"] for r in records)},
        "two_arm":{"compiles":two_comp,"compile_reduction_pct":red(two_comp),"live_sum":sum(r["two"][0] for r in records),"regret_sum":sum(r["two_regret"] for r in records),"max_regret":max(r["two_regret"] for r in records)},
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--family", choices=FAMILY_ORDER); ap.add_argument("--seeds", nargs="+", type=int)
    args=ap.parse_args()
    if args.family:
        cases=[(args.family,s) for s in (args.seeds or DEFAULT_CASES[args.family])]
    else:
        if args.seeds: raise SystemExit("--seeds requires --family")
        cases=[(f,s) for f in FAMILY_ORDER for s in DEFAULT_CASES[f]]
    records=[run_case(f,s) for f,s in cases]
    out={"schema":"coalition_seeded_start_multifamily_transfer_v2_results","protocol":"coalition_seeded_start_multifamily_transfer_v2_protocol.json","oracle_note":"truth bitset checked against exhaustive direct oracle in each order's relabeled coordinates; Hamming rank checked invariant across orders","records":records,"aggregate":aggregate(records),"family_aggregate":{f:aggregate([r for r in records if r["family"]==f]) for f in FAMILY_ORDER if any(r["family"]==f for r in records)}}
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
