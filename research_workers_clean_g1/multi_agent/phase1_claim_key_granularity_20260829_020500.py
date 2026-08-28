from itertools import product
from collections import Counter
import json
P=('global','task_key','effect_keys','two_level','staged_integrator')
PT=[('same_spec','none'),('same_spec','same')]+[(t,e) for t in ('drift_same_name','independent') for e in ('none','same','overlap','disjoint')]
def tasks(t,e):
    if t=='same_spec': na=nb='report'; sa=sb='spec_v1'
    elif t=='drift_same_name': na=nb='report'; sa,sb='spec_v1','spec_v2'
    else: na,nb='report_A','report_B'; sa,sb='spec_A','spec_B'
    ea,eb={'none':((),()),'same':(('e1',),('e1',)),'overlap':(('e1','e2'),('e2','e3')),'disjoint':(('e1',),('e2',))}[e]
    return {'A':{'name':na,'spec':sa,'effects':ea},'B':{'name':nb,'spec':sb,'effects':eb}}
def tk(s,a): return 'T_ALIAS' if a else 'T:'+s
def ek(e,a): return 'E_ALIAS' if a and e in ('e1','e2') else 'E:'+e
def keys(p,t,ta,ea):
    if p=='global': return ('GLOBAL',)
    if p=='task_key': return (tk(t['spec'],ta),)
    if p=='effect_keys': return tuple(sorted(ek(e,ea) for e in t['effects']))
    if p=='two_level': return tuple(sorted((tk(t['spec'],ta),)+tuple(ek(e,ea) for e in t['effects'])))
    return ()
def strong(p,s):
    a,b=tasks(s['task_relation'],s['effect_relation']).values(); ca=(a['spec'],a['effects']); cb=(b['spec'],b['effects'])
    same=ca==cb; nonconf=a['spec']!=b['spec'] and set(a['effects']).isdisjoint(b['effects'])
    o=Counter({k:0 for k in ('duplicate_computation','duplicate_logical_integration','duplicate_authoritative_effect','stale_result_acceptance','safe_parallel_admission','false_parallel_exclusion','recovery_reads','accepted_tasks','blocked_tasks','computed_tasks','unsafe_parallel_admission')})
    if p=='staged_integrator':
        o['computed_tasks']=2; o['duplicate_computation']=int(same); o['safe_parallel_admission']=int(nonconf and s['simultaneous_first'])
        if s['parent_supersede']: o['blocked_tasks']=2; return o
        seen=set(); eff=set()
        for t in (a,b):
            c=(t['spec'],t['effects'])
            if c in seen or set(t['effects'])&eff: o['blocked_tasks']+=1
            else: seen.add(c); eff.update(t['effects']); o['accepted_tasks']+=1
        return o
    ka,kb=set(keys(p,a,s['task_key_alias'],s['effect_key_alias'])),set(keys(p,b,s['task_key_alias'],s['effect_key_alias']))
    conf=bool(ka&kb)
    if ka and (s['claim_outcome']!='ok' or s['restart_lost']): o['recovery_reads']+=1
    o['computed_tasks']=1; bi=not conf; bc=bi or (conf and s['ttl_expire'] and s['takeover']); o['computed_tasks']+=int(bc); o['duplicate_computation']=int(same and bc)
    if nonconf and s['simultaneous_first']:
        o['safe_parallel_admission']=int(bi); o['false_parallel_exclusion']=int(not bi)
    if s['parent_supersede']: o['blocked_tasks']=1+int(bc); return o
    acc=[]; ac=(not ka) or (not s['ttl_expire'])
    if ac: acc.append(a)
    else: o['blocked_tasks']+=1
    if bc: acc.append(b)
    o['accepted_tasks']=len(acc); o['duplicate_logical_integration']=int(len(acc)==2 and ca==cb)
    seen=set()
    for t in acc:
        for e in t['effects']:
            if e in seen: o['duplicate_authoritative_effect']=1
            seen.add(e)
    o['unsafe_parallel_admission']=int(o['duplicate_authoritative_effect'] and s['simultaneous_first'])
    return o
def noepoch(s):
    a,b=tasks(s['task_relation'],s['effect_relation']).values(); ka,kb=set(keys('two_level',a,s['task_key_alias'],s['effect_key_alias'])),set(keys('two_level',b,s['task_key_alias'],s['effect_key_alias']))
    bc=not bool(ka&kb) or (bool(ka&kb) and s['ttl_expire'] and s['takeover'])
    if s['parent_supersede']: return Counter()
    acc=[a]+([b] if bc else []); o=Counter(stale_result_acceptance=int(bool(ka) and s['ttl_expire']))
    o['duplicate_logical_integration']=int(len(acc)==2 and (a['spec'],a['effects'])==(b['spec'],b['effects'])); seen=set()
    for t in acc:
        for e in t['effects']:
            if e in seen:o['duplicate_authoritative_effect']=1
            seen.add(e)
    return o
S=[]
for pt,ta,ea,co,rl,si,te,to,ps in product(PT,(0,1),(0,1),('ok','ambiguous_applied','ambiguous_not_applied'),(0,1),(0,1),(0,1),(0,1),(0,1)):
    S.append(dict(task_relation=pt[0],effect_relation=pt[1],task_key_alias=bool(ta),effect_key_alias=bool(ea),claim_outcome=co,restart_lost=bool(rl),simultaneous_first=bool(si),ttl_expire=bool(te),takeover=bool(to),parent_supersede=bool(ps)))
M=('accepted_tasks','blocked_tasks','computed_tasks','duplicate_authoritative_effect','duplicate_computation','duplicate_logical_integration','false_parallel_exclusion','recovery_reads','safe_parallel_admission','stale_result_acceptance','unsafe_parallel_admission')
def agg(xs):
    out={}
    for p in P:
        c=sum((strong(p,s) for s in xs),Counter()); out[p]={k:c.get(k,0) for k in M}
    return out
clean=[s for s in S if not s['task_key_alias'] and not s['effect_key_alias']]
ov=[s for s in S if s['task_relation']!='same_spec' and s['effect_relation'] in ('same','overlap') and not s['task_key_alias'] and not s['effect_key_alias'] and not s['parent_supersede'] and not s['ttl_expire']]
ro=[s for s in clean if s['task_relation']=='same_spec' and s['effect_relation']=='none' and not s['parent_supersede'] and not s['ttl_expire']]
ne=[s for s in S if s['task_relation']=='same_spec' and s['effect_relation']=='same' and s['ttl_expire'] and s['takeover'] and not s['parent_supersede'] and not s['task_key_alias'] and not s['effect_key_alias']]
n=Counter(); [n.update(noepoch(s)) for s in ne]
nd=[s for s in S if s['task_relation']=='drift_same_name' and s['effect_relation'] in ('none','disjoint') and s['simultaneous_first'] and not s['parent_supersede'] and not s['ttl_expire'] and not s['task_key_alias'] and not s['effect_key_alias']]
R={'schema_version':1,'scenario_count':len(S),'clean_no_alias_scenario_count':len(clean),'protocols':agg(S),'clean_no_alias_protocols':agg(clean),'safe_parallel_opportunity_count':sum(s['task_relation']!='same_spec' and s['effect_relation'] in ('none','disjoint') and s['simultaneous_first'] for s in S),'distinct_task_overlap_current_slice':{'scenario_count':len(ov),'duplicate_authoritative_effect_by_protocol':{p:sum(strong(p,s)['duplicate_authoritative_effect'] for s in ov) for p in P}},'same_task_read_only_current_clean_slice':{'scenario_count':len(ro),'duplicate_logical_integration_by_protocol':{p:sum(strong(p,s)['duplicate_logical_integration'] for s in ro) for p in P}},'negative_controls':{'lease_without_epoch_fence_same_task_effect_takeover':{'scenario_count':len(ne),**dict(n)},'display_name_only_task_key_spec_drift_nonconflicting':{'scenario_count':len(nd),'false_parallel_exclusion':len(nd)}},'interpretation_scope':['Equal-weight synthetic mechanism enumeration; counts are not operational probabilities.','Strong claim protocols use current parent generation and current claim epoch as independent integration gates.','Effect-key and two-level reservation assume all required keys are acquired atomically as one reservation; partial multi-key acquisition is outside the positive claim.','Synthetic task/effect key alias flags model collision or canonicalization aliasing; they do not estimate cryptographic collision probability.','Staged integrator uses full canonical task/effect identities at the authoritative sink; claim-key alias flags therefore affect claim protocols but not the sink identity in this model.']}
assert len(S)==3840 and R['distinct_task_overlap_current_slice']['duplicate_authoritative_effect_by_protocol']['task_key']==len(ov)>0
assert all(R['protocols'][p]['duplicate_authoritative_effect']==0 for p in ('global','effect_keys','two_level','staged_integrator'))
assert R['negative_controls']['lease_without_epoch_fence_same_task_effect_takeover']['duplicate_authoritative_effect']==len(ne)
assert R['negative_controls']['display_name_only_task_key_spec_drift_nonconflicting']['false_parallel_exclusion']==len(nd)
assert R['same_task_read_only_current_clean_slice']['duplicate_logical_integration_by_protocol']['effect_keys']==len(ro)
print(json.dumps(R,indent=2,sort_keys=True))
