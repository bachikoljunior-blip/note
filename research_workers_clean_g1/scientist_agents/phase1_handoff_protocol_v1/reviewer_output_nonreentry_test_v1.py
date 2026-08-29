#!/usr/bin/env python3
import copy,json
from pathlib import Path
from jsonschema import Draft202012Validator
from reviewer_output_nonreentry_validator_v1 import load_schema,semantic_validate

def h(c):return c*64
def base(mode='primary_independent'):
  return {'schema_version':1,'review_mode':mode,'snapshot_frozen_before_current_output':True,'input_root_inventory':[{'item_id':'trace','producer_class':'harness','content_sha256':h('a')},{'item_id':'artifact','producer_class':'agent','content_sha256':h('b')}],'visible_item_ids':['trace','artifact'],'tool_read_policy':'root_read_all','output_namespace':{'disjoint_from_input_root':True,'verdict_artifact_sha256':h('c'),'prompt_artifact_sha256':h('d'),'prior_verdict_visibility_reason':'not_visible' if mode=='primary_independent' else 'comparison_only'}}
def cases():
  out=[('valid_primary_clean_root',base(),True)]
  d=base();d['input_root_inventory'].append({'item_id':'oldverdict','producer_class':'evaluator_prior','content_sha256':h('e')});out.append(('primary_root_read_all_prior_present',d,False))
  d=base();d['input_root_inventory'].append({'item_id':'oldverdict','producer_class':'evaluator_prior','content_sha256':h('e')});d['tool_read_policy']='allowlist_only';out.append(('valid_primary_prior_hidden_by_allowlist',d,True))
  d=base();d['input_root_inventory'].append({'item_id':'oldverdict','producer_class':'evaluator_prior','content_sha256':h('e')});d['tool_read_policy']='allowlist_only';d['visible_item_ids'].append('oldverdict');out.append(('primary_prior_explicitly_visible',d,False))
  d=base();d['input_root_inventory'].append({'item_id':'newverdict','producer_class':'evaluator_current','content_sha256':h('f')});out.append(('current_output_in_snapshot',d,False))
  d=base();d['snapshot_frozen_before_current_output']=False;out.append(('snapshot_after_output',d,False))
  d=base();d['output_namespace']['disjoint_from_input_root']=False;out.append(('primary_output_same_root',d,False))
  d=base();d['output_namespace']['prior_verdict_visibility_reason']='comparison_only';out.append(('primary_wrong_visibility_reason',d,False))
  d=base();d['visible_item_ids'].append('ghost');out.append(('visible_outside_inventory',d,False))
  d=base();d['input_root_inventory'].append({'item_id':'trace','producer_class':'reference','content_sha256':h('e')});out.append(('duplicate_inventory_id',d,False))
  d=base('meta_comparison');d['input_root_inventory'].append({'item_id':'oldverdict','producer_class':'evaluator_prior','content_sha256':h('e')});d['visible_item_ids'].append('oldverdict');out.append(('valid_meta_comparison_prior_visible',d,True))
  d=base('meta_comparison');d['input_root_inventory'].append({'item_id':'oldverdict','producer_class':'evaluator_prior','content_sha256':h('e')});d['visible_item_ids'].append('oldverdict');d['output_namespace']['prior_verdict_visibility_reason']='not_visible';out.append(('meta_visible_prior_unlabeled',d,False))
  return out

def main():
  sv=Draft202012Validator(load_schema());rs=[]
  for n,d,e in cases():
    s=not list(sv.iter_errors(d));sem=not semantic_validate(d);rs.append({'case':n,'schema_valid':s,'semantic_valid':sem,'expected':e,'pass':s and sem==e})
  m={'schema_version':1,'suite':'reviewer_output_nonreentry_v1','cases':rs,'structurally_valid':sum(x['schema_valid'] for x in rs),'semantic_expected_pass':sum(x['pass'] for x in rs),'total':len(rs)}
  Path(__file__).with_name('reviewer_output_nonreentry_test_manifest_v1.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2));raise SystemExit(0 if all(x['pass'] for x in rs) else 1)
if __name__=='__main__':main()
