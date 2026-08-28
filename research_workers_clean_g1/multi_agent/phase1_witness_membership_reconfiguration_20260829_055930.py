#!/usr/bin/env python3
from itertools import combinations
from collections import Counter
import json

OLD={'A','B','C'}
NEW={'B','C','D'}
OLD_PAIRS=[set(x) for x in combinations(['A','B','C'],2)]
NEW_PAIRS=[set(x) for x in combinations(['B','C','D'],2)]

def scenarios():
    out=[]
    for old_pair in OLD_PAIRS:
        for bits in range(1,8):
            new_mask={['B','C','D'][i] for i in range(3) if bits&(1<<i)}
            for failed in [None,'A','B','C','D']:
                for reader_config in ['old','new']:
                    pairs=OLD_PAIRS if reader_config=='old' else NEW_PAIRS
                    for read_pair in pairs:
                        for old_decision in ['COMMIT','ABORT']:
                            for reuse in [False,True]:
                                current=('ABORT' if old_decision=='COMMIT' else 'COMMIT') if reuse else old_decision
                                out.append(dict(old_pair=old_pair,new_mask=new_mask,failed=failed,
                                    reader_config=reader_config,read_pair=read_pair,
                                    old_decision=old_decision,current_decision=current,reuse=reuse))
    return out

def node_state(s,n):
    if s['failed']==n: return ('DOWN',None)
    if n in s['new_mask']: return ('NEW_EPOCH',s['current_decision'])
    if n in s['old_pair']: return ('OLD_EPOCH',s['old_decision'])
    return ('NONE',None)

def result(**kw):
    base=dict(unsafe=0,stale_epoch_accept=0,wrong=0,split_authority=0,
              reconfig_unavailable=0,read_unavailable=0,manual=0,recovered=0,lost=0,cost=0)
    base.update(kw); return base

def evaluate(policy,s):
    if policy in ('joint_quorum','consensus_store') and len(s['new_mask'])<2:
        return result(reconfig_unavailable=1,cost=4 if policy=='joint_quorum' else 2)

    if policy=='consensus_store':
        alive_new=len(NEW-({s['failed']} if s['failed'] else set()))
        if alive_new>=2: return result(recovered=1,cost=2)
        return result(read_unavailable=1,manual=1,lost=1,cost=2)

    obs=[node_state(s,n) for n in sorted(s['read_pair'])]
    cost=4 if policy=='joint_quorum' else (2 if policy=='epoch_failclosed' else 1)
    if any(k=='DOWN' for k,_ in obs):
        return result(read_unavailable=1,manual=1,lost=1,cost=cost)

    if policy=='joint_quorum':
        if s['reader_config']!='new': return result(manual=1,lost=1,cost=cost)
        current=[v for k,v in obs if k=='NEW_EPOCH']
        if current: return result(recovered=1,cost=cost)
        return result(manual=1,lost=1,cost=cost)

    if policy=='epoch_failclosed':
        if s['reader_config']!='new': return result(manual=1,lost=1,cost=cost)
        current=[v for k,v in obs if k=='NEW_EPOCH']
        if current: return result(recovered=1,cost=cost)
        return result(manual=1,lost=1,cost=cost)

    if policy=='naive_switch':
        chosen=None; kind=None
        for k,v in obs:
            if k in ('NEW_EPOCH','OLD_EPOCH'):
                kind,chosen=k,v; break
        if chosen is None:
            kind,chosen='DEFAULT','ABORT'
        stale=int(kind=='OLD_EPOCH')
        wrong=int(chosen!=s['current_decision'])
        split=int(stale and len(s['new_mask'])>=2)
        return result(unsafe=int(bool(stale or wrong)),stale_epoch_accept=stale,wrong=wrong,
                      split_authority=split,recovered=int(not stale and not wrong),
                      lost=int(kind=='DEFAULT'),cost=cost)
    raise ValueError(policy)

def main():
    ss=scenarios()
    policies=['naive_switch','joint_quorum','epoch_failclosed','consensus_store']
    out={'schema_version':1,'model':'phase1_witness_membership_reconfiguration','scenario_count':len(ss),'policy_summary':{}}
    for p in policies:
        c=Counter()
        for s in ss: c.update(evaluate(p,s))
        out['policy_summary'][p]=dict(c)
    insufficient=[s for s in ss if len(s['new_mask'])<2]
    old_reader=[s for s in ss if len(s['new_mask'])>=2 and s['reader_config']=='old']
    out['slices']={
      'cutover_before_new_quorum_has_witness':{
        'scenario_count':len(insufficient),
        'naive_unsafe':sum(evaluate('naive_switch',s)['unsafe'] for s in insufficient),
        'naive_lost':sum(evaluate('naive_switch',s)['lost'] for s in insufficient),
        'joint_reconfig_unavailable':sum(evaluate('joint_quorum',s)['reconfig_unavailable'] for s in insufficient)},
      'old_reader_after_new_quorum_exists':{
        'scenario_count':len(old_reader),
        'naive_stale_epoch_accept':sum(evaluate('naive_switch',s)['stale_epoch_accept'] for s in old_reader),
        'naive_split_authority':sum(evaluate('naive_switch',s)['split_authority'] for s in old_reader),
        'joint_failclosed_manual':sum(evaluate('joint_quorum',s)['manual'] for s in old_reader)}
    }
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
