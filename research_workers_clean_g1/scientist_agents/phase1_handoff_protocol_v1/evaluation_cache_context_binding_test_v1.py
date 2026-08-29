#!/usr/bin/env python3
import copy, hashlib, json
from pathlib import Path
from jsonschema import Draft202012Validator
from evaluation_cache_context_binding_validator_v1 import load_schema, semantic_validate, canonical_context_digest

def h(c): return c*64

def context():
  return {'runner_revision':'1'*40,'runner_artifact_sha256':h('a'),'environment_artifact_sha256':h('b'),'environment_transition_contract_sha256':h('c'),'dataset_record_sha256':h('d'),'codebook_sha256':h('e'),'system_prompt_sha256':h('f'),'user_prompt_sha256':h('1'),'generation_config_sha256':h('2'),'backend_fingerprint_sha256':h('3'),'sampling_contract_sha256':h('4'),'cache_policy_revision':'cache-v1'}

def base():
  e=context(); c=copy.deepcopy(e)
  return {'schema_version':1,'claim_scope':'empty_codebook_rollout_cache','entry_context':e,'current_context':c,'cache_entry':{'cache_key_sha256':h('5'),'bound_context_sha256':canonical_context_digest(e),'result_artifact_sha256':h('6'),'outcome_digest_sha256':h('7'),'original_execution_id_sha256':h('8')},'reuse_request':{'codebook_is_empty':True,'reuse_semantics':'memoized_same_execution','cache_hit_authorized':True,'treat_as_new_independent_sample':False}}

def cases():
  out=[('valid_exact_context_memoization',base(),True)]
  for field,value in [('runner_revision','9'*40),('runner_artifact_sha256',h('9')),('environment_artifact_sha256',h('9')),('environment_transition_contract_sha256',h('9')),('dataset_record_sha256',h('9')),('backend_fingerprint_sha256',h('9')),('sampling_contract_sha256',h('9'))]:
    d=base(); d['current_context'][field]=value; out.append((f'drift_{field}',d,False))
  d=base();d['current_context']['cache_policy_revision']='cache-v2';out.append(('drift_cache_policy_revision',d,False))
  d=base();d['cache_entry']['bound_context_sha256']=h('9');out.append(('bad_bound_context_digest',d,False))
  d=base();d['reuse_request']['codebook_is_empty']=False;out.append(('nonempty_codebook_out_of_scope',d,False))
  d=base();d['reuse_request']['cache_hit_authorized']=False;out.append(('unauthorized_cache_hit',d,False))
  d=base();d['reuse_request']['reuse_semantics']='independent_replication';out.append(('independent_replication_must_execute',d,False))
  d=base();d['reuse_request']['treat_as_new_independent_sample']=True;out.append(('memoized_hit_not_new_sample',d,False))
  d=base();d['current_context']['generation_config_sha256']=h('9');out.append(('drift_generation_config',d,False))
  d=base();d['current_context']['codebook_sha256']=h('9');out.append(('drift_codebook',d,False))
  return out

def main():
  sv=Draft202012Validator(load_schema()); rs=[]
  for name,d,exp in cases():
    s=not list(sv.iter_errors(d)); sem=not semantic_validate(d); rs.append({'case':name,'schema_valid':s,'semantic_valid':sem,'expected':exp,'pass':s and sem==exp})
  m={'schema_version':1,'suite':'evaluation_cache_context_binding_v1','cases':rs,'structurally_valid':sum(x['schema_valid'] for x in rs),'semantic_expected_pass':sum(x['pass'] for x in rs),'total':len(rs)}
  Path(__file__).with_name('evaluation_cache_context_binding_test_manifest_v1.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2));raise SystemExit(0 if all(x['pass'] for x in rs) else 1)
if __name__=='__main__': main()
