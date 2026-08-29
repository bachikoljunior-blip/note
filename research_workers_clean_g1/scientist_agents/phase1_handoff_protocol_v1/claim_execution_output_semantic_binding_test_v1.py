#!/usr/bin/env python3
import copy,json
from pathlib import Path
from jsonschema import Draft202012Validator
from claim_execution_output_semantic_binding_validator_v1 import load_schema,semantic_validate

def h(c):return c*64
def base():
  return {'schema_version':1,'gate_implementation':{'repository':'Omni-Scientist/OmniScientist','revision':'1'*40,'edition':'cli','gate_blob_sha':'2'*40,'policy_revision':'semantic-bind-v1'},'execution':{'entry_sha256':h('a'),'returncode':0,'timed_out':False,'script_sha256':h('b'),'argv_sha256':h('c'),'input_manifest_sha256':h('d'),'environment_manifest_sha256':h('e'),'output_record_complete':True},'outputs':[{'output_id':'metric.accuracy','execution_entry_sha256':h('a'),'field_locator':'results.metrics.accuracy','quantity_id':'classification_accuracy','normalized_value':'0.947','normalized_unit':'1','record_artifact_sha256':h('f')},{'output_id':'metric.cosine','execution_entry_sha256':h('a'),'field_locator':'results.metrics.cosine_similarity','quantity_id':'cosine_similarity','normalized_value':'0.947','normalized_unit':'1','record_artifact_sha256':h('1')}],'claim':{'claim_id':'c1','source_output_id':'metric.accuracy','quantity_id':'classification_accuracy','normalized_value':'0.947','normalized_unit':'1','presented_token':'94.7%','presentation_transform':'percent','presentation_transform_digest':h('2')},'authorization':{'authority_scope':'scientific_quantitative_claim','authorized':True,'authorization_packet_sha256':h('3')}}
def cases():
  out=[('valid_semantic_binding',base(),True)]
  d=base();d['claim']['source_output_id']='metric.cosine';out.append(('same_number_wrong_quantity_rejected',d,False))
  d=base();d['claim']['quantity_id']='cosine_similarity';out.append(('quantity_label_drift',d,False))
  d=base();d['claim']['normalized_value']='0.948';out.append(('value_drift',d,False))
  d=base();d['claim']['normalized_unit']='percent';out.append(('unit_drift',d,False))
  d=base();d['execution']['returncode']=4;d['authorization']['authorized']=False;out.append(('failed_execution_rejected',d,False))
  d=base();d['execution']['timed_out']=True;d['authorization']['authorized']=False;out.append(('timed_out_rejected',d,False))
  d=base();d['execution']['output_record_complete']=False;d['authorization']['authorized']=False;out.append(('incomplete_output_rejected',d,False))
  d=base();d['outputs'][0]['execution_entry_sha256']=h('9');out.append(('output_execution_binding_drift',d,False))
  d=base();d['claim']['source_output_id']='missing';d['authorization']['authorized']=False;out.append(('missing_source_output',d,False))
  d=base();d['outputs'][1]['output_id']='metric.accuracy';out.append(('duplicate_output_id',d,False))
  d=base();d['claim']['presentation_transform']='identity';d['claim']['presentation_transform_digest']=None;d['claim']['presented_token']='0.947';out.append(('valid_identity_presentation',d,True))
  d=base();d['claim']['presentation_transform_digest']=None;out.append(('nonidentity_transform_without_digest',d,False))
  d=base();d['claim']['presentation_transform']='identity';out.append(('identity_transform_with_digest',d,False))
  d=base();d['authorization']['authorized']=False;out.append(('false_negative_authorization_flag',d,False))
  return out

def main():
  sv=Draft202012Validator(load_schema());rs=[]
  for n,d,e in cases():
    s=not list(sv.iter_errors(d));sem=not semantic_validate(d);rs.append({'case':n,'schema_valid':s,'semantic_valid':sem,'expected':e,'pass':s and sem==e})
  m={'schema_version':1,'suite':'claim_execution_output_semantic_binding_v1','cases':rs,'structurally_valid':sum(x['schema_valid'] for x in rs),'semantic_expected_pass':sum(x['pass'] for x in rs),'total':len(rs)}
  Path(__file__).with_name('claim_execution_output_semantic_binding_test_manifest_v1.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2));raise SystemExit(0 if all(x['pass'] for x in rs) else 1)
if __name__=='__main__':main()
