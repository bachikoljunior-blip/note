#!/usr/bin/env python3
"""Reproduce C84/C85 from public LAJ-Gherkin fixed traces.

Public source is pinned to commit ee8649376b51f9e4c5b955369a88c4a5a6bba5da.
This script performs no repository-state reads; it only downloads the pinned public CSVs.
"""
from __future__ import annotations

import csv
import io
import math
import random
import urllib.request
from statistics import median

PIN = "ee8649376b51f9e4c5b955369a88c4a5a6bba5da"
RAW = f"https://raw.githubusercontent.com/inflaton/LAJ-Gherkin/{PIN}"
CHEAP_RATE = 1.0080101800710406  # GPT-4o Mini adjusted $ / 1K evals
HET_RATE = 3.0770789171717174   # GPT-4.1 Mini adjusted $ / 1K evals


def fetch_csv(path: str):
    with urllib.request.urlopen(f"{RAW}/{path}") as r:
        text = r.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(text)))


def scores(path: str):
    rows = fetch_csv(path)
    return [float(r["coverage_percentage"]) for r in rows]


def mae(pred, truth):
    return sum(abs(a-b) for a,b in zip(pred, truth)) / len(truth)


def rmse(pred, truth):
    return math.sqrt(sum((a-b)**2 for a,b in zip(pred, truth)) / len(truth))


def mean_cols(cols):
    return [sum(v)/len(v) for v in zip(*cols)]


def bootstrap_diff(pred_a, pred_b, truth, n=50000, seed=20260826):
    rng = random.Random(seed)
    d = [abs(a-t)-abs(b-t) for a,b,t in zip(pred_a,pred_b,truth)]
    vals=[]
    N=len(d)
    for _ in range(n):
        vals.append(sum(d[rng.randrange(N)] for _ in range(N))/N)
    vals.sort()
    return sum(d)/N, (vals[int(.025*n)], vals[int(.975*n)])


gt_rows = fetch_csv("dataset/jira_coverage_ground_truth.csv")
truth = [float(r["coverage_percentage"]) for r in gt_rows]
mini41 = [scores(f"results/r{k}/jira_coverage_gpt-4.1-mini.csv") for k in range(1,6)]
mini4o = [scores(f"results/r{k}/jira_coverage_gpt-4o-mini.csv") for k in range(1,5)]

print("GPT-4.1 Mini single-run MAE:", [round(mae(r,truth),3) for r in mini41])
for k in range(1,6):
    pred=mean_cols(mini41[:k])
    ranges=[max(v)-min(v) for v in zip(*mini41[:k])]
    print("K",k,"MAE",round(mae(pred,truth),3),"RMSE",round(rmse(pred,truth),3),
          "mean_range",round(sum(ranges)/len(ranges),3),"identical",sum(x==0 for x in ranges))

mean5=mean_cols(mini41)
ranges5=[max(v)-min(v) for v in zip(*mini41)]
stable=[x==0 for x in ranges5]
print("stable",sum(stable),
      "stable_wrong",sum(s and p!=t for s,p,t in zip(stable,mean5,truth)),
      "stable_abs_error_gt5",sum(s and abs(p-t)>5 for s,p,t in zip(stable,mean5,truth)),
      "stable_max_error",max(abs(p-t) for s,p,t in zip(stable,mean5,truth) if s))

# Same-judge disagreement-triggered repeat policy.
dis=[a!=b for a,b in zip(mini41[0],mini41[1])]
adaptive=[]
for i,flag in enumerate(dis):
    if flag:
        adaptive.append(median(r[i] for r in mini41))
    else:
        adaptive.append((mini41[0][i]+mini41[1][i])/2)
print("GPT-4.1 Mini adaptive repeats calls",200+3*sum(dis),"MAE",round(mae(adaptive,truth),3))

# Five-fold cross-fit by item index mod 5. Tiny router class: observable base-score category only.
base=mini4o[0]
hetero=mini41[0]
pred_h=[None]*len(truth)
pred_repeat=[None]*len(truth)
switch=[False]*len(truth)
values=sorted(set(base))
for fold in range(5):
    train=[i for i in range(len(truth)) if i%5 != fold]
    test=[i for i in range(len(truth)) if i%5 == fold]
    for value in values:
        tr=[i for i in train if base[i]==value]
        te=[i for i in test if base[i]==value]
        use_hetero = bool(tr) and mae([hetero[i] for i in tr],[truth[i] for i in tr]) < mae([base[i] for i in tr],[truth[i] for i in tr])
        for i in te:
            if use_hetero:
                switch[i]=True
                pred_h[i]=hetero[i]
                pred_repeat[i]=sum(r[i] for r in mini4o)/4
            else:
                pred_h[i]=base[i]
                pred_repeat[i]=base[i]

n_switch=sum(switch)
print("base MAE",round(mae(base,truth),3))
print("heterogeneous cross-fit switched",n_switch,"MAE",round(mae(pred_h,truth),3))
print("same-slice cheap r1-r4 mean MAE",round(mae(pred_repeat,truth),3))
print("heterogeneous approximate cost $",round((100*CHEAP_RATE+n_switch*HET_RATE)/1000,6))
print("cheap-repeat approximate cost $",round((100+3*n_switch)*CHEAP_RATE/1000,6))
print("hetero-repeat bootstrap",bootstrap_diff(pred_h,pred_repeat,truth))
print("hetero-base bootstrap",bootstrap_diff(pred_h,base,truth))
