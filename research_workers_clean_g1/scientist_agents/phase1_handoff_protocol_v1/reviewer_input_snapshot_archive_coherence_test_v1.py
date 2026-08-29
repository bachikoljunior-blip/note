#!/usr/bin/env python3
import copy, hashlib, json
from pathlib import Path
from jsonschema import Draft202012Validator
from reviewer_input_snapshot_archive_coherence_validator_v1 import load_schema, semantic_validate, manifest_digest

def h(c): return c*64
def item(i,r,c): return {'item_id':i,'role':r,'path_hint':f'{i}.dat','content_sha256':h(c)}
def base(mode='self_contained'):
  items=[item('trace','trace','a'),item('artifact','produced_artifact','b'),item('claim','claim_reference','c')]
  md=manifest_digest(items)
  embedded=[i['item_id'] for i in items] if mode=='self_contained' else ['trace']
  ext=[] if mode=='self_contained' else [
    {'item_id':'artifact','locator':'cas://artifact','content_sha256':h('b'),'content_addressed':True,'resolvable':True},
    {'item_id':'claim','locator':'cas://claim','content_sha256':h('c'),'content_addressed':True,'resolvable':True}]
  return {'schema_version':1,'evaluator':{'repository':'JHU-CLSP/AutoMat','revision':'1'*40,'runner_artifact_sha256':h('d'),'model_identity':'model-v1','prompt_sha256':h('e'),'policy_revision':'eval-v1'},'input_manifest':{'manifest_sha256':md,'items':items},'observed_item_ids':['trace','artifact'],'archive':{'mode':mode,'archive_manifest_sha256':h('f'),'embedded_item_ids':embedded,'external_refs':ext},'verdict':{'input_manifest_sha256':md,'verdict_artifact_sha256':h('1'),'overall_score':4},'reevaluation':{'previous_verdict_artifact_sha256':None,'previous_input_manifest_sha256':None,'reuse_previous_verdict':False}}
def cases():
  out=[('valid_self_contained',base(),True),('valid_thin_content_addressed',base('thin'),True)]
  d=base();d['input_manifest']['items'][0]['content_sha256']=h('9');out.append(('manifest_content_changed_digest_stale',d,False))
  d=base();d['input_manifest']['items'][2]['item_id']='trace';out.append(('duplicate_item_id',d,False))
  d=base();d['input_manifest']['items'][2]['path_hint']='trace.dat';out.append(('duplicate_path_hint',d,False))
  d=base();d['input_manifest']['items']=[x for x in d['input_manifest']['items'] if x['role']!='trace'];d['input_manifest']['manifest_sha256']=manifest_digest(d['input_manifest']['items']);d['verdict']['input_manifest_sha256']=d['input_manifest']['manifest_sha256'];d['archive']['embedded_item_ids']=['artifact','claim'];out.append(('missing_trace',d,False))
  d=base();d['observed_item_ids'].append('ghost');out.append(('observation_outside_manifest',d,False))
  d=base();d['verdict']['input_manifest_sha256']=h('9');out.append(('verdict_manifest_mismatch',d,False))
  d=base();d['archive']['embedded_item_ids']=['trace','artifact'];out.append(('self_contained_missing_claim',d,False))
  d=base('thin');d['archive']['external_refs'][0]['content_addressed']=False;out.append(('thin_mutable_external_ref',d,False))
  d=base('thin');d['archive']['external_refs'][0]['resolvable']=False;out.append(('thin_unresolvable_ref',d,False))
  d=base('thin');d['archive']['external_refs'][0]['content_sha256']=h('9');out.append(('thin_external_digest_mismatch',d,False))
  d=base();d['reevaluation']={'previous_verdict_artifact_sha256':h('1'),'previous_input_manifest_sha256':d['input_manifest']['manifest_sha256'],'reuse_previous_verdict':True};out.append(('valid_same_snapshot_verdict_reuse',d,True))
  d=base();d['reevaluation']={'previous_verdict_artifact_sha256':h('1'),'previous_input_manifest_sha256':h('9'),'reuse_previous_verdict':True};out.append(('changed_snapshot_cannot_reuse_verdict',d,False))
  d=base();d['reevaluation']={'previous_verdict_artifact_sha256':h('2'),'previous_input_manifest_sha256':d['input_manifest']['manifest_sha256'],'reuse_previous_verdict':True};out.append(('reused_verdict_identity_mismatch',d,False))
  d=base();d['reevaluation']={'previous_verdict_artifact_sha256':None,'previous_input_manifest_sha256':d['input_manifest']['manifest_sha256'],'reuse_previous_verdict':False};out.append(('partial_previous_identity',d,False))
  return out

def main():
  sv=Draft202012Validator(load_schema());rs=[]
  for n,d,e in cases():
    s=not list(sv.iter_errors(d));sem=not semantic_validate(d);rs.append({'case':n,'schema_valid':s,'semantic_valid':sem,'expected':e,'pass':s and sem==e})
  m={'schema_version':1,'suite':'reviewer_input_snapshot_archive_coherence_v1','cases':rs,'structurally_valid':sum(x['schema_valid'] for x in rs),'semantic_expected_pass':sum(x['pass'] for x in rs),'total':len(rs)}
  Path(__file__).with_name('reviewer_input_snapshot_archive_coherence_test_manifest_v1.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2));raise SystemExit(0 if all(x['pass'] for x in rs) else 1)
if __name__=='__main__':main()
