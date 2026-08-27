#!/usr/bin/env python3
import argparse, json, math, random, time
import networkx as nx
import numpy as np

FEATURE_NAMES=["n","m","density","natural_width","rcm_width","seeded_width","seeded_minus_min_width","seeded_minus_max_width","abs_natural_rcm_width_gap","seeded_min_kendall","mean_degree","degree_std","min_degree","max_degree","transitivity","average_clustering","component_count","largest_component_fraction","max_core_number"]
SCALER_MEAN=np.array([12.0,21.083333333333332,0.3194444444444444,6.708333333333333,5.375,6.458333333333333,1.2083333333333333,-0.375,1.5833333333333333,0.5776515151515152,3.5138888888888893,0.5580955263396169,2.625,4.541666666666667,0.2588889868201893,0.25702711640211634,1.1666666666666667,0.9756944444444446,3.0833333333333335],dtype=float)
SCALER_SCALE=np.array([1.0,3.081080257889359,0.04668303421044483,1.059841445164742,1.1110243021644486,0.7626252174051305,0.7626252174051305,1.1110243021644486,1.2555432644432805,0.09890281355414322,0.513513376314893,0.6132123477880285,1.2849286620924396,1.224035901797365,0.10303969859615725,0.10700678940563758,0.372677996249965,0.07004944792302781,0.6400954789890507],dtype=float)
COEF=np.array([0.0,0.4111652145837726,0.41116521458377286,0.48913272200376856,-0.03659875377584846,0.21605230370957434,0.23364369529469348,-0.2937737088205423,0.401875680468718,0.5073609303816825,0.41116521458377286,-0.31980760011204445,0.42176509301713017,-0.20847725666467404,-0.773912060811247,-0.7177160889645726,-0.020001815436473145,0.01769425477640671,0.5696596568926124],dtype=float)
INTERCEPT=-3.5525907308070135

class ROBDD:
    def __init__(self,n):
        self.n=n; self.nodes=[None,None]; self.unique={}; self.apply_cache={}; self.rank_cache={}; self.truth_cache={0:0}; self.var_masks=None; self.universe=None
    def varpos(self,u): return self.n if u<=1 else self.nodes[u][0]
    def mk(self,var,lo,hi):
        if lo==hi: return lo
        k=(var,lo,hi)
        if k in self.unique: return self.unique[k]
        u=len(self.nodes); self.nodes.append(k); self.unique[k]=u; return u
    def clause2(self,a,b):
        x,y=sorted((a,b))
        if x==y: return self.mk(x,0,1)
        return self.mk(x,self.mk(y,0,1),1)
    def and_(self,u,v):
        if u==0 or v==0: return 0
        if u==1: return v
        if v==1: return u
        if u==v: return u
        if u>v: u,v=v,u
        k=(u,v)
        if k in self.apply_cache: return self.apply_cache[k]
        p=min(self.varpos(u),self.varpos(v))
        if self.varpos(u)==p: _,ulo,uhi=self.nodes[u]
        else: ulo=uhi=u
        if self.varpos(v)==p: _,vlo,vhi=self.nodes[v]
        else: vlo=vhi=v
        out=self.mk(p,self.and_(ulo,vlo),self.and_(uhi,vhi)); self.apply_cache[k]=out; return out
    def reachable(self,root):
        seen=set(); st=[root]
        while st:
            u=st.pop()
            if u<=1 or u in seen: continue
            seen.add(u); _,lo,hi=self.nodes[u]; st.extend((lo,hi))
        return len(seen)
    def _rank(self,u,level):
        k=(u,level)
        if k in self.rank_cache: return self.rank_cache[k]
        if u==0: out=(0,)*(self.n-level+1)
        elif u==1: out=tuple(math.comb(self.n-level,k) for k in range(self.n-level+1))
        else:
            var,lo,hi=self.nodes[u]; plo=self._rank(lo,var+1); phi=self._rank(hi,var+1); br=[0]*(self.n-var+1)
            for k,x in enumerate(plo): br[k]+=x
            for k,x in enumerate(phi): br[k+1]+=x
            gap=var-level
            if gap:
                acc=[0]*(self.n-level+1)
                for a in range(gap+1):
                    ca=math.comb(gap,a)
                    for b,cb in enumerate(br): acc[a+b]+=ca*cb
                out=tuple(acc)
            else: out=tuple(br)
        self.rank_cache[k]=out; return out
    def rank(self,root): return list(self._rank(root,0))
    def _ensure_masks(self):
        if self.var_masks is not None: return
        total=1<<self.n; self.universe=(1<<total)-1; masks=[]
        for v in range(self.n):
            block=1<<v; period=block<<1; m=0; ones=(1<<block)-1
            for start in range(block,total,period): m |= ones<<start
            masks.append(m)
        self.var_masks=masks; self.truth_cache[1]=self.universe
    def truth_bits(self,u):
        self._ensure_masks()
        if u in self.truth_cache: return self.truth_cache[u]
        var,lo,hi=self.nodes[u]; vm=self.var_masks[var]
        out=(self.truth_bits(lo)&(self.universe^vm)) | (self.truth_bits(hi)&vm)
        self.truth_cache[u]=out; return out

def frontier_size(g,prefix):
    p=set(prefix); return sum(1 for u in p if any(v not in p for v in g.neighbors(u)))

def vsw(g,order):
    p=[]; best=0
    for v in order[:-1]: p.append(v); best=max(best,frontier_size(g,p))
    return best

def normalized_kendall(a,b):
    pos={v:i for i,v in enumerate(b)}; seq=[pos[v] for v in a]; inv=0
    for i in range(len(seq)):
        for j in range(i+1,len(seq)):
            if seq[i]>seq[j]: inv+=1
    den=len(seq)*(len(seq)-1)//2
    return inv/den if den else 0.0

def seeded_order(g,seed,natural,rcm):
    rng=random.Random(seed+100000); nodes=sorted(g.nodes()); lim=min(vsw(g,natural),vsw(g,rcm))+2; eligible=[]; allc=[]
    for _ in range(16):
        o=nodes[:]; rng.shuffle(o); w=vsw(g,o); d=min(normalized_kendall(o,natural),normalized_kendall(o,rcm)); row=(o,w,d); allc.append(row)
        if w<=lim: eligible.append(row)
    if eligible: return min(eligible,key=lambda z:(-z[2],z[1],z[0]))
    return min(allc,key=lambda z:(z[1],z[0]))

def relabeled_edges(g,order):
    p={v:i for i,v in enumerate(order)}
    return sorted(tuple(sorted((p[u],p[v]))) for u,v in g.edges())

def direct_truth_bits(n,edges):
    total=1<<n; universe=(1<<total)-1; masks=[]
    for v in range(n):
        block=1<<v; period=block<<1; m=0; ones=(1<<block)-1
        for start in range(block,total,period): m |= ones<<start
        masks.append(m)
    out=universe
    for a,b in edges: out &= masks[a] | masks[b]
    return out

def compile_order(g,order,oracle=None):
    edges=relabeled_edges(g,order); mgr=ROBDD(g.number_of_nodes()); forest=[mgr.clause2(a,b) for a,b in edges]
    if not forest: root=1
    else:
        while len(forest)>1:
            nxt=[]
            for i in range(0,len(forest),2): nxt.append(forest[i] if i+1==len(forest) else mgr.and_(forest[i],forest[i+1]))
            forest=nxt
        root=forest[0]
    live=mgr.reachable(root); rank=mgr.rank(root); truth=mgr.truth_bits(root)
    if oracle is not None and (rank!=oracle[0] or truth!=oracle[1]): raise AssertionError("oracle mismatch")
    return {"live":live,"allocated":len(mgr.nodes)-2,"rank":rank,"truth":truth}

def neighbors(order):
    out=[]; n=len(order)
    for i in range(n):
        x=order[i]; base=order[:i]+order[i+1:]
        for j in range(n):
            cand=base[:j]+[x]+base[j:]
            if cand!=order: out.append(cand)
    return out

def local_stage(g,order,oracle):
    cur=compile_order(g,order,oracle); compiles=1
    best=None
    for cand in neighbors(order):
        if vsw(g,cand)>vsw(g,order)+1: continue
        r=compile_order(g,cand,oracle); compiles+=1
        key=(r["live"],r["allocated"],cand)
        if best is None or key<best[0]: best=(key,cand,r)
    if best and best[2]["live"]<cur["live"]: return best[1],best[2],compiles,True
    return order,cur,compiles,False

def run_arm(g,start,oracle,max_moves=2,prestage=None):
    if prestage is None:
        order=start; total=0; accepted=0; current=None
        while accepted<max_moves:
            order,current,c,ok=local_stage(g,order,oracle); total+=c
            if not ok: break
            accepted+=1
        if current is None: current=compile_order(g,order,oracle); total+=1
        return order,current,total,accepted
    order,current,total,accepted=prestage
    while accepted<max_moves:
        order,current,c,ok=local_stage(g,order,oracle); total+=c
        if not ok: break
        accepted+=1
    return order,current,total,accepted

def stage_arm(g,start,oracle):
    o,r,c,ok=local_stage(g,start,oracle); return (o,r,c,1 if ok else 0)

def commit_policy(g,arms,oracle):
    staged={k:stage_arm(g,v,oracle) for k,v in arms.items()}
    priority={"rcm":0,"natural":1,"seeded":2}
    winner=min(staged,key=lambda k:(staged[k][1]["live"],staged[k][2],priority[k]))
    o,r,total,acc=run_arm(g,arms[winner],oracle,2,staged[winner]); total += sum(staged[k][2] for k in staged if k!=winner)
    return {"live":r["live"],"compiles":total,"winner":winner}, staged

def graph_features(g,natural,rcm,seeded,seeded_width,kendall):
    deg=np.array([d for _,d in g.degree()],dtype=float); n=g.number_of_nodes(); m=g.number_of_edges(); nw=vsw(g,natural); rw=vsw(g,rcm)
    comps=list(nx.connected_components(g)); core=nx.core_number(g) if n else {}
    return np.array([n,m,nx.density(g),nw,rw,seeded_width,seeded_width-min(nw,rw),seeded_width-max(nw,rw),abs(nw-rw),kendall,deg.mean(),deg.std(),deg.min(),deg.max(),nx.transitivity(g),nx.average_clustering(g),len(comps),max(map(len,comps))/n,max(core.values()) if core else 0],dtype=float)

def probability(x):
    z=INTERCEPT + float(np.dot(COEF,(x-SCALER_MEAN)/SCALER_SCALE)); return 1/(1+math.exp(-z))

def run_seed(seed):
    g=nx.Graph(nx.random_regular_graph(4,16,seed=seed)); natural=sorted(g.nodes()); rcm=list(nx.utils.reverse_cuthill_mckee_ordering(g)); seeded,sw,kd=seeded_order(g,seed,natural,rcm)
    ref=compile_order(g,natural); oracle=(ref["rank"],ref["truth"])
    two,st2=commit_policy(g,{"rcm":rcm,"natural":natural},oracle); three,st3=commit_policy(g,{"rcm":rcm,"natural":natural,"seeded":seeded},oracle)
    stage_live=[st3["natural"][1]["live"],st3["rcm"][1]["live"],st3["seeded"][1]["live"]]
    label=int(stage_live[2]<stage_live[0] and stage_live[2]<stage_live[1]); x=graph_features(g,natural,rcm,seeded,sw,kd); p=probability(x); pred=int(p>=.5); wg=int(sw<=min(vsw(g,natural),vsw(g,rcm))+1)
    learned=three if pred else two; width=three if wg else two
    return {"seed":seed,"label":label,"prob":p,"pred":pred,"width_gate_open":bool(wg),"widths":[vsw(g,natural),vsw(g,rcm),sw],"seeded_min_kendall":kd,"stage_live":stage_live,"two":[two["live"],two["compiles"]],"three":[three["live"],three["compiles"]],"learned":[learned["live"],learned["compiles"]],"width_plus1":[width["live"],width["compiles"]],"oracle_ok":True}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--seeds",nargs="+",type=int,required=True); a=ap.parse_args()
    print(json.dumps([run_seed(s) for s in a.seeds],indent=2,sort_keys=True))
if __name__=="__main__": main()
