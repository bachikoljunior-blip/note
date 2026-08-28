import json, math, time, statistics, torch

def one(numel,support,world,rank,iters,seed):
 g=torch.Generator().manual_seed(seed); n=max(1,int(numel*support)); idx=torch.randperm(numel,generator=g)[:n].sort().values; ref=torch.randn(n,generator=g)
 P=math.ceil(numel/world); s=rank*P; e=min(s+P,numel); data=torch.randn(P,generator=g)
 t=time.perf_counter(); lo=int(torch.searchsorted(idx,torch.tensor(s))); hi=int(torch.searchsorted(idx,torch.tensor(e))); gi=idx[lo:hi].clone(); li=(gi-s).clone(); rl=ref[lo:hi].clone(); prep=time.perf_counter()-t
 keep=(idx>=s)&(idx<e); assert torch.equal(gi,idx[keep]); assert torch.equal(data[li]-rl,data[idx[keep]-s]-ref[keep])
 t=time.perf_counter(); a=0.
 for _ in range(iters):
  keep=(idx>=s)&(idx<e); d=data[idx[keep]-s]-ref[keep]; a+=float(d.abs().sum())
 pub=time.perf_counter()-t
 t=time.perf_counter(); b=0.
 for _ in range(iters): b+=float((data[li]-rl).abs().sum())
 loc=time.perf_counter()-t; assert a==b
 return prep,pub/iters,loc/iters,li.numel()
rows=[]; numel=2_000_000; iters=40
for support in (0.01,0.10,0.3439):
 for world in (2,8,16):
  rank=world//2-1 if world>2 else 0; reps=[]
  for rep in range(3): reps.append(one(numel,support,world,rank,iters,1000+rep+world+int(support*10000)))
  pre=[x[0] for x in reps]; pub=[x[1] for x in reps]; loc=[x[2] for x in reps]; cnt=[x[3] for x in reps]
  mp,mg,ml=statistics.median(pre),statistics.median(pub),statistics.median(loc)
  rows.append({'support_fraction':support,'world_size':world,'rank':rank,'rank_support_count_median':int(statistics.median(cnt)),'prepartition_ms_median':mp*1000,'public_ms_per_step_median':mg*1000,'ranklocal_ms_per_step_median':ml*1000,'speedup_median':mg/ml,'break_even_steps_median':mp/max(mg-ml,1e-30)})
print(json.dumps({'torch_version':torch.__version__,'numel':numel,'iterations_per_rep':iters,'repeats':3,'rows':rows},indent=2))
