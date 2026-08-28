#!/usr/bin/env python3
import importlib.util, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "coalition_seeded_stage_option_value_dev_v0_runner.py"
spec = importlib.util.spec_from_file_location("stage_base", BASE_PATH)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

FAMILIES = ("cubic", "quartic", "watts", "erdos")
CHECKPOINT = 97
THRESHOLD = 47


def cases():
    for n, base_seed in ((16, 918000), (18, 919000)):
        for j, family in enumerate(FAMILIES):
            for seed in range(base_seed + 100*j, base_seed + 100*j + 20):
                yield n, family, seed


def evaluate(n, family, seed):
    r = base.challenger(n, family, seed)
    inc = r["two_live"]
    ev65 = next((e for e in r["events"] if e["idx"] == 65), r["events"][-1])
    best65 = ev65["best"]
    remains = r["total_challenger"] > ev65["idx"]
    v1_stop = bool(remains and best65 >= inc and best65 - inc > 11)
    out = {
        "n": n, "family": family, "seed": seed,
        "incumbent": inc, "best65": best65, "gap65": best65-inc,
        "v1_stop": v1_stop, "total": r["total_challenger"],
        "exhaustive_best": r["exhaustive_best"], "gain": r["gain"],
        "first_cert": r["first_cert"]
    }
    if not v1_stop:
        return out
    target = min(CHECKPOINT, r["total_challenger"])
    ev = next(e for e in r["events"] if e["idx"] == target)
    best97 = ev["best"]
    exhausted = target == r["total_challenger"]
    buy_tail = False if exhausted else (best97 - inc <= THRESHOLD)
    selected_tail = (r["total_challenger"] - target) if buy_tail else 0
    deployed_best = r["exhaustive_best"] if buy_tail else best97
    deployed_gain = max(0, inc - deployed_best)
    out.update({
        "best97": best97, "gap97": best97-inc,
        "probe_cost": target-65, "buy_tail": buy_tail,
        "selected_tail_cost": selected_tail,
        "deploy_cost": target-65+selected_tail,
        "deploy_gain": deployed_gain,
        "regret": r["gain"]-deployed_gain
    })
    return out


def summarize(rows):
    stop = [r for r in rows if r["v1_stop"]]
    pos = [r for r in stop if r["gain"] > 0]
    available = sum(r["gain"] for r in pos)
    recovered = sum(r["deploy_gain"] for r in stop)
    exhaustive = sum(r["total"]-65 for r in stop)
    deployed = sum(r["deploy_cost"] for r in stop)
    return {
        "total_cases": len(rows), "stop_rows": len(stop),
        "positive_stop_rows": len(pos), "available_gain": available,
        "recovered_gain": recovered,
        "gain_weighted_recall": recovered/available if available else None,
        "exhaustive_stop_tail_compiles": exhaustive,
        "deployed_post65_compiles": deployed,
        "deployed_compute_fraction": deployed/exhaustive if exhaustive else None,
        "positive_row_recall": sum(r["deploy_gain"] > 0 for r in pos)/len(pos) if pos else None,
        "selected_tail_rows": sum(bool(r["buy_tail"]) for r in stop),
        "missed_regret_sum": sum(r["regret"] for r in stop),
        "missed_regret_max": max((r["regret"] for r in stop), default=0)
    }


def main():
    rows = [evaluate(*c) for c in cases()]
    print(json.dumps({
        "schema": "coalition_seeded_probe97_gap47_confirmation_v0_replay",
        "protocol": "coalition_seeded_probe97_gap47_confirmation_v0_protocol.json",
        "aggregate": summarize(rows),
        "records": rows
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
