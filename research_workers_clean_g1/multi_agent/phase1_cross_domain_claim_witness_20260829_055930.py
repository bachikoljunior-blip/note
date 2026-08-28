#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

def scenarios():
    out=[]
    for x_advance in ['none','before_read','after_read']:
        for x_read_fresh,y_status,dedupe,takeover in product([False,True],repeat=4):
            for y_resp in ['clear_success','clear_fail','ambiguous']:
                actuals=[False,True] if y_resp=='ambiguous' else ([True] if y_resp=='clear_success' else [False])
                for y_actual in actuals:
                    out.append(dict(x_advance=x_advance,x_read_fresh=x_read_fresh,y_status=y_status,
                                    dedupe=dedupe,takeover=takeover,y_resp=y_resp,y_actual=y_actual))
    return out

def evaluate(policy,s):
    stale=dup=orphan=manual=effect=resolved=actions=0
    before=s['x_advance']=='before_read'; after=s['x_advance']=='after_read'
    if policy=='x_authoritative':
        if before and s['x_read_fresh']: resolved=1
        else:
            actions+=1
            if s['y_actual'] and s['takeover']:
                effect=1
                if not s['dedupe']: dup=1
            else:
                effect=int(s['y_resp']!='clear_fail' or s['takeover'])
            if effect and ((before and not s['x_read_fresh']) or after): stale=1
            resolved=int(effect and not stale and not dup)
            orphan=int(not effect)
    elif policy=='y_authoritative':
        actions+=1
        if s['y_actual']: effect=1
        elif s['y_resp']=='clear_fail' and s['takeover']: effect=1
        elif s['y_resp']=='ambiguous':
            if s['y_status']: effect=int(s['y_actual'])
            elif s['takeover']: effect=1
        if effect and s['x_advance']!='none': stale=1
        resolved=int(effect and not stale); orphan=int(not effect)
    elif policy=='read_both_then_act':
        if before and s['x_read_fresh']: resolved=1
        else:
            if s['y_actual'] and s['y_status']: effect=1
            else:
                actions+=1
                if s['y_actual'] and s['takeover'] and not s['dedupe']: effect=1; dup=1
                elif s['y_resp']=='clear_fail' and not s['takeover']: effect=0
                else: effect=1
            if effect and ((before and not s['x_read_fresh']) or after): stale=1
            resolved=int(effect and not stale and not dup); orphan=int(not effect)
    elif policy=='intent_revocable':
        if before and s['x_read_fresh']: resolved=1
        else:
            actions+=1
            intent=s['y_actual'] or s['y_resp']=='clear_success'
            if s['y_resp']=='ambiguous' and not s['y_status'] and s['takeover']: intent=True
            if s['y_resp']=='clear_fail' and s['takeover']: intent=True
            if intent:
                effect=1
                if (before and not s['x_read_fresh']) or after: stale=1
            else: orphan=1
            resolved=int(effect and not stale)
    elif policy=='intent_irrevocable':
        if before: resolved=1
        else:
            actions+=1  # atomic verify+AUTHORIZATION in X
            actions+=1  # conditional effect-id write/retry in Y
            effect=1
            resolved=1
    elif policy=='single_domain_colocation':
        actions+=1
        if before: resolved=1
        else: effect=1; resolved=1
    else: raise ValueError(policy)
    unsafe=int(bool(stale or dup))
    if unsafe: resolved=0
    return dict(unsafe=unsafe,stale=stale,duplicate=dup,orphan=orphan,manual=manual,
                effect_applied=effect,resolved=resolved,actions=actions)

def main():
    ss=scenarios(); policies=['x_authoritative','y_authoritative','read_both_then_act','intent_revocable','intent_irrevocable','single_domain_colocation']
    out={'schema_version':1,'model':'phase1_cross_domain_claim_witness_coupling','scenario_count':len(ss),'policy_summary':{}}
    for p in policies:
        c=Counter()
        for s in ss:c.update(evaluate(p,s))
        out['policy_summary'][p]=dict(c)
    after=[s for s in ss if s['x_advance']=='after_read']
    dup=[s for s in ss if s['y_resp']=='ambiguous' and s['y_actual'] and s['takeover'] and not s['dedupe'] and s['x_advance']=='none']
    out['slices']={
      'claim_advances_after_final_read_before_effect':{'scenario_count':len(after),**{p+'_unsafe':sum(evaluate(p,s)['unsafe'] for s in after) for p in policies}},
      'ambiguous_y_already_applied_takeover_no_dedupe':{'scenario_count':len(dup),**{p+'_duplicate':sum(evaluate(p,s)['duplicate'] for s in dup) for p in policies}}
    }
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
