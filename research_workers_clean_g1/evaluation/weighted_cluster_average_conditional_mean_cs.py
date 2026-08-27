#!/usr/bin/env python3
"""Anytime-valid upper CS for a predictably weighted average conditional mean.

Each top-level cluster i contributes one score Y_i in [0,1] and one weight
w_i in (0,1]. The weight MUST be F_{i-1}-measurable: fixed before the current
cluster outcome/score is observed. The target is

    mu_w,t = sum_i w_i E[Y_i | F_{i-1}] / sum_i w_i.

This is useful when process/exposure sizes are known prospectively. A realized
cluster size that can depend on the current outcome is not automatically a valid
weight; use a prospective exposure plan, a fixed-size block design, or a separate
theorem.

For lambda>0, a_i=1-exp(-lambda*w_i). Convexity on [0,1] gives

    E[exp(-lambda*w_i*Y_i) | F_{i-1}] <= 1-a_i*mu_i.

Hence prod exp(-lambda*w_i*Y_i)/(1-a_i*mu_i) is a nonnegative
supermartingale. Since 1-x <= exp(-x) and

    (1-exp(-lambda*w))/w >= 1-exp(-lambda),   0<w<=1,

we have

    prod_i (1-a_i*mu_i)
      <= exp(-(1-exp(-lambda))*sum_i w_i*mu_i).

Therefore, at the true weighted average mu_w,t,

    E_t(lambda,m) = exp(-lambda*sum_i w_i Y_i
                         +(1-exp(-lambda))*sum_i w_i*m)

is pathwise upper-bounded by that supermartingale. Any fixed convex mixture over
lambda values is likewise dominated by a nonnegative supermartingale, and Ville's
inequality yields an anytime-valid upper confidence sequence.

The target changes with t. Do not running-intersect endpoints across times unless
a separate constant-target contract has been proved.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

DEFAULT_LAMBDAS = (0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0)


def _logsumexp(xs: list[float]) -> float:
    m = max(xs)
    return m + math.log(sum(math.exp(x-m) for x in xs))


def _csv(raw: str) -> tuple[float, ...]:
    vals = tuple(float(x.strip()) for x in raw.split(',') if x.strip())
    if not vals or any((not math.isfinite(x)) or x <= 0 for x in vals):
        raise ValueError('lambda/weight values must be finite and >0')
    return vals


def _weights(raw: str | None, n: int) -> tuple[float, ...]:
    if raw is None:
        return tuple(1/n for _ in range(n))
    vals = _csv(raw)
    if len(vals) != n:
        raise ValueError('mixture weights must match lambda count')
    s = sum(vals)
    return tuple(x/s for x in vals)


def log_e(weighted_score_sum: float, weight_sum: float, m: float,
          lambdas: tuple[float, ...], mix_weights: tuple[float, ...]) -> float:
    if not 0 <= m <= 1:
        raise ValueError('candidate mean must be in [0,1]')
    vals=[]
    for lam,p in zip(lambdas,mix_weights):
        a=1-math.exp(-lam)
        vals.append(math.log(p)-lam*weighted_score_sum+a*weight_sum*m)
    return _logsumexp(vals)


def upper_endpoint(weighted_score_sum: float, weight_sum: float, alpha: float,
                   lambdas: tuple[float, ...], mix_weights: tuple[float, ...]) -> float:
    thr=math.log(1/alpha)
    if log_e(weighted_score_sum,weight_sum,1.0,lambdas,mix_weights) < thr:
        return 1.0
    lo,hi=0.0,1.0
    for _ in range(90):
        mid=(lo+hi)/2
        if log_e(weighted_score_sum,weight_sum,mid,lambdas,mix_weights) >= thr:
            hi=mid
        else:
            lo=mid
    return hi


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--records-json',required=True,
        help="JSON list or {'clusters':[...]} with cluster_id, score, predictable_weight")
    ap.add_argument('--weight-contract',required=True)
    ap.add_argument('--score-contract',required=True)
    ap.add_argument('--fingerprint-scope',required=True)
    ap.add_argument('--alpha',type=float,default=0.05)
    ap.add_argument('--lambdas',default=','.join(str(x) for x in DEFAULT_LAMBDAS))
    ap.add_argument('--mixture-weights',default=None)
    ap.add_argument('--emit-prefix',action='store_true')
    args=ap.parse_args()
    if not 0 < args.alpha < 1:
        raise ValueError('alpha must be in (0,1)')
    lams=_csv(args.lambdas)
    mix=_weights(args.mixture_weights,len(lams))
    payload=json.loads(Path(args.records_json).read_text(encoding='utf-8'))
    records=payload['clusters'] if isinstance(payload,dict) else payload
    if not isinstance(records,list) or not records:
        raise ValueError('records must be a nonempty list')
    ids=set(); S=0.0; W=0.0; prefix=[]
    for i,rec in enumerate(records,1):
        cid=str(rec.get('cluster_id','')).strip()
        if not cid or cid in ids:
            raise ValueError('cluster_id must be unique and nonempty')
        ids.add(cid)
        y=float(rec['score']); w=float(rec['predictable_weight'])
        if not math.isfinite(y) or not 0 <= y <= 1:
            raise ValueError('score must be in [0,1]')
        if not math.isfinite(w) or not 0 < w <= 1:
            raise ValueError('predictable_weight must be in (0,1]')
        S += w*y; W += w
        u=upper_endpoint(S,W,args.alpha,lams,mix)
        if args.emit_prefix:
            prefix.append({'cluster_index':i,'cluster_id':cid,'score':y,
                           'predictable_weight':w,'weight_sum':W,
                           'weighted_score_sum':S,'weighted_mean_upper':u})
    out={
      'schema_version':1,
      'fingerprint_scope':args.fingerprint_scope,
      'score_contract':args.score_contract,
      'weight_contract':args.weight_contract,
      'estimand':'sum_i w_i E[Y_i|F_{i-1}] / sum_i w_i',
      'alpha':args.alpha,
      'cluster_count':len(records),
      'weight_sum':W,
      'weighted_score_sum':S,
      'empirical_weighted_score':S/W,
      'weighted_average_conditional_mean_upper':upper_endpoint(S,W,args.alpha,lams,mix),
      'lambdas':list(lams),'mixture_weights':list(mix),
      'validity_notes':[
        'Each predictable_weight must be fixed before its current cluster outcome is observed.',
        'Weights are normalized to <=1 by contract; if a prospective raw exposure exceeds its declared cap, fail closed or start a separately declared generation rather than renormalizing retrospectively.',
        'Cross-cluster independence is not required; validity is conditional-mean/filtration based.',
        'This targets a predictably weighted average conditional mean, not an equal-process mean unless all weights are equal.',
        'Do not use a running intersection when the weighted average target changes with time.'
      ]
    }
    if args.emit_prefix: out['prefix']=prefix
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__':
    main()
