#!/usr/bin/env python3
import json, math
from scipy.stats import beta, chi2_contingency, norm

# Aggregate counts from arXiv:2608.25920v1 Appendix B, Table 5.
rows = [
    ("unanimous", 210, 23),
    ("2-1_split", 214, 42),
    ("all_distinct", 112, 35),
]

def jeffreys(k, n, alpha=0.05):
    lo, hi = beta.ppf([alpha/2, 1-alpha/2], k + 0.5, n - k + 0.5)
    return float(lo), float(hi)

out = {"source":"arXiv:2608.25920v1 Appendix B Table 5", "rows":[]}
for label,n,k in rows:
    lo,hi = jeffreys(k,n)
    out["rows"].append({"pattern":label,"cases":n,"new_tuple":k,"rate":k/n,"jeffreys95":[lo,hi]})

# Independence test across the three disagreement-pattern strata.
import numpy as np
groups=np.array([r[1] for r in rows], dtype=float)
novel=np.array([r[2] for r in rows], dtype=float)
table=np.column_stack([novel, groups-novel])
chi2,p,dof,_ = chi2_contingency(table)
out["chi_square_independence"]={"chi2":float(chi2),"df":int(dof),"p_two_sided":float(p)}

# Cochran-Armitage trend test for scores unanimous=0, split=1, all-distinct=2.
scores=np.array([0.,1.,2.])
N=float(groups.sum()); Y=float(novel.sum()); pbar=Y/N
xbar=float(np.sum(groups*scores)/N)
num=float(np.sum(scores*(novel-groups*pbar)))
den=math.sqrt(pbar*(1-pbar)*float(np.sum(groups*(scores-xbar)**2)))
z=num/den
out["cochran_armitage_trend"]={"z":float(z),"p_two_sided":float(2*norm.sf(abs(z)))}

# Descriptive risk ratios relative to unanimous; not causal or operational thresholds.
base=novel[0]/groups[0]
out["risk_ratio_vs_unanimous"]={
    "2-1_split":float((novel[1]/groups[1])/base),
    "all_distinct":float((novel[2]/groups[2])/base),
}

# Majority strict tuple retained when a strict majority exists (unanimous or 2-1).
majority_cases=210+214
majority_retained=187+124
lo,hi=jeffreys(majority_retained,majority_cases)
out["strict_majority_retained_as_final"]={
    "retained":majority_retained,"cases":majority_cases,"rate":majority_retained/majority_cases,"jeffreys95":[lo,hi]
}

print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
