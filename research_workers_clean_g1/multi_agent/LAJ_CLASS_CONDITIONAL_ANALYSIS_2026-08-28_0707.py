#!/usr/bin/env python3
"""Reproduce the LAJ-Gherkin class-conditional verifier analysis.

Public source is pinned to inflaton/LAJ-Gherkin commit
`ee8649376b51f9e4c5b955369a88c4a5a6bba5da`.
The script downloads only the ground truth, five gpt-4o-mini runs, and run-1
for gpt-4.1-mini, then computes the same-verifier and cross-verifier error
statistics plus a deterministic calibration/test routing pilot.
"""
from __future__ import annotations
import csv, hashlib, io, json, urllib.request
import numpy as np

COMMIT='ee8649376b51f9e4c5b955369a88c4a5a6bba5da'
ROOT=f'https://raw.githubusercontent.com/inflaton/LAJ-Gherkin/{COMMIT}'

def read_csv(path):
    with urllib.request.urlopen(ROOT+'/'+path, timeout=30) as r:
        return list(csv.DictReader(io.StringIO(r.read().decode('utf-8'))))

def scores(path):
    rows=read_csv(path)
    return np.array([float(r['coverage_percentage']) for r in rows])

def ok(pred, gt):
    return np.abs(pred-gt) <= 5

def corr(x,y):
    x=np.asarray(x,dtype=float); y=np.asarray(y,dtype=float)
    return float(np.corrcoef(x,y)[0,1])

gt=scores('dataset/jira_coverage_ground_truth.csv')
A=np.column_stack([scores(f'results/r{i}/jira_coverage_gpt-4o-mini.csv') for i in range(1,6)])
B=scores('results/r1/jira_coverage_gpt-4.1-mini.csv')
CA=ok(A,gt[:,None]); CB=ok(B,gt)
EA=~CA[:,0]; EB=~CB
pair=[]
for i in range(5):
    for j in range(i+1,5): pair.append(corr(~CA[:,i],~CA[:,j]))

ids=np.arange(1,len(gt)+1)
h=np.array([int(hashlib.sha256(f'multi_agent_laj_v1:{i}'.encode()).hexdigest()[:8],16)/2**32 for i in ids])
cal=h<0.6; test=~cal
bins=np.where(A[:,0]<=85,'<=85',np.where(A[:,0]<=90,'86-90','>90'))
actions={'keep_A1':A[:,0], 'same_repeat_mean2':A[:,:2].mean(1), 'switch_B1':B}

def closeacc(p,m): return float(ok(p[m],gt[m]).mean())
def mae(p,m): return float(np.abs(p[m]-gt[m]).mean())

def choose(metric):
    out={}
    for bn in ['<=85','86-90','>90']:
        m=cal & (bins==bn)
        vals={k:metric(v,m) for k,v in actions.items()}
        if metric is closeacc:
            best=max(vals.values()); order=['keep_A1','same_repeat_mean2','switch_B1']
            out[bn]=next(k for k in order if vals[k]==best)
        else: out[bn]=min(vals,key=vals.get)
    return out

result={
 'n':len(gt), 'A_run_close_accuracy':[float(CA[:,i].mean()) for i in range(5)],
 'A1_MAE':mae(A[:,0],np.ones(len(gt),bool)), 'B1_MAE':mae(B,np.ones(len(gt),bool)),
 'same_verifier_pairwise_error_phi_mean':float(np.mean(pair)),
 'A1_B1_error_phi':corr(EA,EB),
 'p_B1_correct_given_A1_wrong':float(CB[EA].mean()),
 'p_A2_correct_given_A1_wrong':float(CA[EA,1].mean()),
 'p_all_A2_to_A5_wrong_given_A1_wrong':float(np.all(~CA[EA,1:],axis=1).mean()),
 'stable_identical_n':int(np.all(A==A[:,[0]],axis=1).sum()),
 'stable_identical_wrong_n':int((np.all(A==A[:,[0]],axis=1)&EA).sum()),
 'split':{'calibration':int(cal.sum()),'test':int(test.sum())},
}
for objective,metric in [('close_accuracy',closeacc),('mae',mae)]:
    ch=choose(metric); p=A[:,0].copy(); extra=0
    for i in range(len(gt)):
        if test[i]:
            act=ch[bins[i]]; p[i]=actions[act][i]; extra += act!='keep_A1'
    result[objective]={'choice':ch,'test_value':metric(p,test),'extra_calls':int(extra)}
print(json.dumps(result,indent=2,sort_keys=True))
