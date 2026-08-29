#!/usr/bin/env python3
import copy,json
from pathlib import Path
from jsonschema import Draft202012Validator
from calibrated_judge_scope_revision_validator_v1 import load_schema,semantic_validate

def h(c):return c*64
def judge():return {'code_revision':'1'*40,'runner_sha256':h('a'),'model_identity_sha256':h('b'),'prompt_sha256':h('c'),'rubric_sha256':h('d'),'input_exposure_policy_sha256':h('e')}
def base():
  j=judge()
  return {'schema_version':1,'certificate':{'judge':copy.deepcopy(j),'metrics':{'sample_n':40,'quadratic_weighted_kappa':0.69,'within_one_accuracy':0.80,'human_protocol_sha256':h('f'),'calibration_snapshot_sha256':h('1')},'domains':['computational_materials_science'],'claim_types':['from_paper','from_artifact','from_artifact_interpretation'],'certificate_sha256':h('2')},'current_judge':copy.deepcopy(j),'target':{'domain':'computational_materials_science','claim_type':'from_artifact','input_snapshot_sha256':h('3')},'claim':{'calibration_status':'calibrated_in_scope','authority_level':'benchmark_score_support','certificate_applied':True,'downstream_human_or_scientific_verification_required':True}}
def cases():
  out=[('valid_in_scope_exact_revision',base(),True)]
  for field,value in [('code_revision','9'*40),('runner_sha256',h('9')),('model_identity_sha256',h('9')),('prompt_sha256',h('9')),('rubric_sha256',h('9')),('input_exposure_policy_sha256',h('9'))]:
    d=base();d['current_judge'][field]=value;d['claim']['calibration_status']='uncalibrated_changed_revision';d['claim']['certificate_applied']=False;out.append((f'valid_changed_{field}',d,True))
    bad=copy.deepcopy(d);bad['claim']['calibration_status']='calibrated_in_scope';bad['claim']['certificate_applied']=True;out.append((f'changed_{field}_cannot_inherit',bad,False))
  d=base();d['target']['domain']='chemistry';d['claim']['calibration_status']='uncalibrated_out_of_scope';d['claim']['certificate_applied']=False;out.append(('valid_out_of_scope_domain',d,True))
  d=base();d['target']['claim_type']='adversarial_nonreproducible';d['claim']['calibration_status']='uncalibrated_out_of_scope';d['claim']['certificate_applied']=False;out.append(('valid_out_of_scope_claim_type',d,True))
  d=base();d['target']['domain']='chemistry';out.append(('out_of_scope_cannot_apply',d,False))
  d=base();d['claim']['authority_level']='final_scientific_authority';out.append(('calibrated_judge_not_final_authority',d,False))
  d=base();d['claim']['downstream_human_or_scientific_verification_required']=False;out.append(('downstream_verification_required',d,False))
  d=base();d['certificate']['metrics']['sample_n']=1;out.append(('single_sample_not_calibration',d,False))
  d=base();d['claim']['calibration_status']='uncalibrated_changed_revision';d['claim']['certificate_applied']=False;out.append(('exact_match_mislabeled_changed',d,False))
  return out

def main():
  sv=Draft202012Validator(load_schema());rs=[]
  for n,d,e in cases():
    s=not list(sv.iter_errors(d));sem=not semantic_validate(d);rs.append({'case':n,'schema_valid':s,'semantic_valid':sem,'expected':e,'pass':s and sem==e})
  m={'schema_version':1,'suite':'calibrated_judge_scope_revision_v1','cases':rs,'structurally_valid':sum(x['schema_valid'] for x in rs),'semantic_expected_pass':sum(x['pass'] for x in rs),'total':len(rs)}
  Path(__file__).with_name('calibrated_judge_scope_revision_test_manifest_v1.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2));raise SystemExit(0 if all(x['pass'] for x in rs) else 1)
if __name__=='__main__':main()
