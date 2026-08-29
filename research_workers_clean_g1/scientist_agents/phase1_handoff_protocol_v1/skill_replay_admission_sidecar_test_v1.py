#!/usr/bin/env python3
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from skill_replay_admission_sidecar_validator_v1 import load_schema, validate_semantic

def h(c): return c*64

def base(level='replay_verified_admission'):
  return {
    'schema_version':1,'claim_level':level,
    'implementation':{'repository':'JHU-CLSP/speedrunner','revision':'1'*40,'asisleep_blob_sha':'2'*40,'config_blob_sha':'3'*40,'policy_revision':'asi-replay-v1'},
    'environment':{'package':'scienceworld','version':'1.2.3','artifact_filename':'scienceworld.whl','artifact_sha256':h('a'),'dataset_manifest_sha256':h('b'),'replay_equivalence_packet_sha256':h('c')},
    'transaction':{'batch_index':0,'successful_task_ids':['t1'],'allow_replay':True,'pre_codebook_sha256':h('d'),'candidate_codebook_sha256':h('e'),'candidate_functions':[{'name':'f','code_sha256':h('f')}]},
    'replays':[{'task_id':'t1','problem_record_sha256':h('1'),'reset_observation_sha256':h('2'),'test_trajectory_artifact_sha256':h('3'),'test_trajectory_digest':h('4'),'used_new_helper':True,'solution_success':True,'error_class':None,'result_artifact_sha256':h('5')}],
    'decision':{'status':'commit','post_codebook_sha256':h('e'),'decision_packet_sha256':h('6')}
  }

def cases():
  out=[('valid_replay_commit',base(),True)]
  d=base();d['environment']['replay_equivalence_packet_sha256']=None;out.append(('missing_env_equivalence',d,False))
  d=base();d['transaction']['allow_replay']=False;out.append(('claim_replay_but_disabled',d,False))
  d=base();d['replays']=[];d['decision']['status']='revert';d['decision']['post_codebook_sha256']=h('d');out.append(('valid_missing_replay_revert_transaction_only',{**d,'claim_level':'transaction_only'},True))
  d=base();d['replays'][0]['used_new_helper']=False;d['decision']['status']='revert';d['decision']['post_codebook_sha256']=h('d');out.append(('valid_failed_usage_revert',{**d,'claim_level':'transaction_only'},True))
  d=base();d['replays'][0]['solution_success']=False;out.append(('failed_replay_cannot_commit',d,False))
  d=base();d['decision']['status']='revert';d['decision']['post_codebook_sha256']=h('d');out.append(('all_pass_cannot_revert',d,False))
  d=base();d['decision']['post_codebook_sha256']=h('d');out.append(('commit_post_digest_wrong',d,False))
  d=base();d['transaction']['pre_codebook_sha256']=h('e');out.append(('candidate_equals_pre',d,False))
  d=base();d['transaction']['successful_task_ids']=['t1','t2'];out.append(('missing_successful_task_replay',d,False))
  d=base();d['transaction']['candidate_functions'].append({'name':'f','code_sha256':h('7')});out.append(('duplicate_candidate_name',d,False))
  d=base(level='transaction_only');d['transaction']['allow_replay']=False;d['replays']=[];d['environment']['replay_equivalence_packet_sha256']=None;d['decision']['status']='commit';d['decision']['post_codebook_sha256']=h('e');out.append(('valid_no_replay_static_commit',d,True))
  d=base(level='transaction_only');d['transaction']['allow_replay']=False;d['replays']=[];d['environment']['replay_equivalence_packet_sha256']=None;d['decision']['status']='revert';d['decision']['post_codebook_sha256']=h('d');out.append(('no_replay_revert_invalid',d,False))
  return out

def main():
  sv=Draft202012Validator(load_schema()); rs=[]
  for name,d,exp in cases():
    so=not list(sv.iter_errors(d)); sem=not validate_semantic(d); rs.append({'case':name,'schema_valid':so,'semantic_valid':sem,'expected':exp,'pass':so and sem==exp})
  m={'schema_version':1,'suite':'skill_replay_admission_sidecar_v1','cases':rs,'structurally_valid':sum(x['schema_valid'] for x in rs),'semantic_expected_pass':sum(x['pass'] for x in rs),'total':len(rs)}
  Path(__file__).with_name('skill_replay_admission_sidecar_test_manifest_v1.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2));raise SystemExit(0 if all(x['pass'] for x in rs) else 1)
if __name__=='__main__': main()
