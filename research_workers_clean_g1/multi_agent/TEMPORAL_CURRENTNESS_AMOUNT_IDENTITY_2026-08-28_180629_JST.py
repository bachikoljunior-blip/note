import json
from itertools import product

# Study 1: fresh current absence is not stable absence if an earlier forward mutation is still in flight.
toctx = []
# One quiescent world plus three worlds with an in-flight forward attempt whose eventual outcome is unknown at read time.
toctx.append({"inflight": False, "eventual": "NONE"})
for eventual in ["NONE", "PARTIAL", "COMPLETE"]:
    toctx.append({"inflight": True, "eventual": eventual})

policies1 = {k:{"terminal":0,"unsafe":0,"safe":0} for k in ["fresh_only","quiescence_gated","settle_then_read"]}
for w in toctx:
    # A fresh read at t0 says NONE in every world.
    # fresh_only immediately claims rollback complete.
    terminal=True
    unsafe=w["eventual"] != "NONE"
    policies1["fresh_only"]["terminal"] += int(terminal)
    policies1["fresh_only"]["unsafe"] += int(unsafe)
    policies1["fresh_only"]["safe"] += int(terminal and not unsafe)

    # quiescence_gated claims rollback only if there is no unresolved writer.
    terminal=not w["inflight"]
    unsafe=terminal and w["eventual"] != "NONE"
    policies1["quiescence_gated"]["terminal"] += int(terminal)
    policies1["quiescence_gated"]["unsafe"] += int(unsafe)
    policies1["quiescence_gated"]["safe"] += int(terminal and not unsafe)

    # settle_then_read waits for the unresolved writer (if any), then reads again and claims rollback only on NONE.
    terminal=w["eventual"] == "NONE"
    unsafe=False
    policies1["settle_then_read"]["terminal"] += int(terminal)
    policies1["settle_then_read"]["unsafe"] += 0
    policies1["settle_then_read"]["safe"] += int(terminal)

# Study 2: amount conservation must dedupe by physical resource identity, not observation count.
amount_worlds = [
    {"name":"one50_one_delivery", "resources":{"cap1":50}, "deliveries":[("cap1",50)]},
    {"name":"one50_two_deliveries", "resources":{"cap1":50}, "deliveries":[("cap1",50),("cap1",50)]},
    {"name":"one50_three_deliveries", "resources":{"cap1":50}, "deliveries":[("cap1",50),("cap1",50),("cap1",50)]},
    {"name":"two50_one_each", "resources":{"cap1":50,"cap2":50}, "deliveries":[("cap1",50),("cap2",50)]},
    {"name":"two50_duplicate_first", "resources":{"cap1":50,"cap2":50}, "deliveries":[("cap1",50),("cap1",50),("cap2",50)]},
    {"name":"physical90_duplicate30", "resources":{"cap1":60,"cap2":30}, "deliveries":[("cap1",60),("cap2",30),("cap2",30)]},
]
intended=100
policies2={k:{"terminal":0,"unsafe":0,"safe":0} for k in ["sum_observations","dedupe_resource_identity"]}
world_details=[]
for w in amount_worlds:
    physical=sum(w["resources"].values())
    observed_sum=sum(a for _,a in w["deliveries"])
    dedup={}
    for rid,a in w["deliveries"]:
        dedup[rid]=max(dedup.get(rid,0),a)
    dedup_sum=sum(dedup.values())
    row={"name":w["name"],"physical_total":physical,"observed_sum":observed_sum,"dedup_sum":dedup_sum}
    for name,total in [("sum_observations",observed_sum),("dedupe_resource_identity",dedup_sum)]:
        terminal=total>=intended
        unsafe=terminal and physical<intended
        policies2[name]["terminal"] += int(terminal)
        policies2[name]["unsafe"] += int(unsafe)
        policies2[name]["safe"] += int(terminal and not unsafe)
        row[name+"_terminal"]=terminal
        row[name+"_unsafe"]=unsafe
    world_details.append(row)

# Study 3: rollback amount also needs resource-identity dedupe.
refund_worlds = [
    {"name":"refund50_once", "captured":100,"refund_resources":{"r1":50},"deliveries":[("r1",50)]},
    {"name":"refund50_twice_delivery", "captured":100,"refund_resources":{"r1":50},"deliveries":[("r1",50),("r1",50)]},
    {"name":"refund50_thrice_delivery", "captured":100,"refund_resources":{"r1":50},"deliveries":[("r1",50),("r1",50),("r1",50)]},
    {"name":"two_refunds50", "captured":100,"refund_resources":{"r1":50,"r2":50},"deliveries":[("r1",50),("r2",50)]},
    {"name":"two_refunds50_dup", "captured":100,"refund_resources":{"r1":50,"r2":50},"deliveries":[("r1",50),("r1",50),("r2",50)]},
    {"name":"physical80_duplicate30", "captured":100,"refund_resources":{"r1":50,"r2":30},"deliveries":[("r1",50),("r2",30),("r2",30)]},
]
policies3={k:{"terminal":0,"unsafe":0,"safe":0} for k in ["sum_observations","dedupe_resource_identity"]}
refund_details=[]
for w in refund_worlds:
    physical=sum(w["refund_resources"].values())
    observed_sum=sum(a for _,a in w["deliveries"])
    dedup={}
    for rid,a in w["deliveries"]:
        dedup[rid]=max(dedup.get(rid,0),a)
    dedup_sum=sum(dedup.values())
    row={"name":w["name"],"physical_refund_total":physical,"observed_sum":observed_sum,"dedup_sum":dedup_sum}
    for name,total in [("sum_observations",observed_sum),("dedupe_resource_identity",dedup_sum)]:
        terminal=total>=w["captured"]
        unsafe=terminal and physical<w["captured"]
        policies3[name]["terminal"] += int(terminal)
        policies3[name]["unsafe"] += int(unsafe)
        policies3[name]["safe"] += int(terminal and not unsafe)
        row[name+"_terminal"]=terminal
        row[name+"_unsafe"]=unsafe
    refund_details.append(row)

# Study 4: a state can be 'current' but not lifecycle-final. This is a target-predicate counterexample.
late_worlds=["STAYS_COMPLETE","LATE_FAILURE"]
current_complete_terminal={"terminal":2,"unsafe_for_durable_finality":1,"safe_for_durable_finality":1}

out={
  "study":"temporal_currentness_and_amount_identity_exact_lattice",
  "scope":"balanced synthetic mechanism enumeration; proportions are not empirical incident rates",
  "toctou_absence":{"worlds":toctx,"policies":policies1},
  "capture_amount_identity":{"intended":intended,"worlds":world_details,"policies":policies2},
  "refund_amount_identity":{"worlds":refund_details,"policies":policies3},
  "lifecycle_finality":{"worlds":late_worlds,"current_complete_policy":current_complete_terminal,"note":"If the objective is durable finality rather than current capture success, a current COMPLETE-like state is insufficient whenever the documented lifecycle permits a later adverse transition."},
  "controller_implications":[
    "freshness and quiescence are non-substitutable: a fresh read at t can be invalidated by an earlier in-flight writer after t",
    "terminal/destructive authority should carry a generation or in-flight-attempt certificate, not only a resource snapshot",
    "amount conservation must aggregate unique physical operation/resource identities, not webhook/API observation count",
    "target terminal predicate must distinguish operational capture success from durable settlement/finality when the provider lifecycle permits late failure or reversal"
  ]
}
print(json.dumps(out,indent=2,sort_keys=True))
