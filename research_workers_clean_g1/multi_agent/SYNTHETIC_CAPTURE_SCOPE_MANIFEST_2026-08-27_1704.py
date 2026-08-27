"""Deterministic clean-role mechanism study for capture-scope completeness.

This is NOT a production measurement. It models 30-node DAG rollback with
correlated whole-surface blind spots. All pseudo-randomness is SHA-256 seeded.
"""
import collections, hashlib, math, random

N=30
N_GRAPHS=4000
SURFACES=["keyed","reducer","handoff","whole","runnable","routing","dynamic_tool","custom_wrapper","reflection"]
WEIGHTS=[0.18,0.12,0.13,0.08,0.09,0.11,0.10,0.10,0.09]
RISKY={"routing","dynamic_tool","custom_wrapper","reflection"}
UNLISTED={"custom_wrapper","reflection"}
KNOWN_UNCAP={"runnable"}
TARGET_RT=0.69
TARGET_ST=0.75


def rng_for(*parts):
    h=hashlib.sha256("||".join(map(str,parts)).encode()).hexdigest()
    return random.Random(int(h[:16],16))


def desc(edges,src):
    adj=[[] for _ in range(N)]
    for a,b in edges: adj[a].append(b)
    seen=set(); stack=[src]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen: seen.add(v); stack.append(v)
    return seen


def gen_graph(gid):
    r=rng_for("graph",gid); e=[]; p=.105
    for i in range(N-1):
        for j in range(i+1,N):
            if r.random() < p*math.exp(-(j-i-1)/18):
                e.append((i,j,r.choices(SURFACES,weights=WEIGHTS,k=1)[0]))
    for i in range(0,N-1,5):
        j=min(N-1,i+r.randint(1,4))
        if not any(a==i and b==j for a,b,_ in e):
            e.append((i,j,r.choices(SURFACES,weights=WEIGHTS,k=1)[0]))
    cand=[i for i in range(N//2) if len(desc([(a,b) for a,b,_ in e],i))>=2]
    return e,r.choice(cand) if cand else 0

GRAPHS=[gen_graph(i) for i in range(N_GRAPHS)]


def affected_surfaces(edges,src,td):
    reach={src}|td
    return {s for a,b,s in edges if a in reach and b in td}


def calibrate(p_blind,target,kind):
    # Binary-search capture probability for risky non-blind edges while safe
    # surfaces use fixed capture. Keeps marginal edge recall approximately fixed.
    lo,hi=0.0,1.0
    for _ in range(28):
        x=(lo+hi)/2; hit=tot=0
        for gid,(edges,_) in enumerate(GRAPHS):
            rb=rng_for("blind",gid,p_blind)
            blind={s for s in RISKY if rb.random()<p_blind}
            rr=rng_for(kind,gid,p_blind,x)
            for _,_,s in edges:
                tot+=1
                if s in blind: q=0.0
                elif kind=="rt": q=0.0 if s=="runnable" else (x if s in RISKY else .98)
                else: q=x if s in RISKY else .86
                hit += rr.random()<q
        if hit/tot < target: lo=x
        else: hi=x
    return (lo+hi)/2


def fixed_marginal(p_blind):
    xr=calibrate(p_blind,TARGET_RT,"rt")
    ys=calibrate(p_blind,TARGET_ST,"st")
    names=["local","warning","union","observed_unlisted","mediated_manifest","whole"]
    c={n:collections.Counter() for n in names}; s={n:collections.defaultdict(float) for n in names}
    meta=collections.Counter()
    for gid,(edges,src) in enumerate(GRAPHS):
        true={(a,b) for a,b,_ in edges}; td=desc(true,src); whole=set(range(N))-{src}
        rb=rng_for("blind",gid,p_blind); blind={q for q in RISKY if rb.random()<p_blind}
        rt=set(); st=set(); rt_rng=rng_for("rt",gid,p_blind,xr); st_rng=rng_for("st",gid,p_blind,ys)
        for a,b,q in edges:
            if q in blind: qr=qs=0.0
            else:
                qr=0.0 if q=="runnable" else (xr if q in RISKY else .98)
                qs=ys if q in RISKY else .86
            if rt_rng.random()<qr: rt.add((a,b))
            if st_rng.random()<qs: st.add((a,b))
        surfaces=affected_surfaces(edges,src,td)
        known=bool(surfaces&KNOWN_UNCAP); unlisted=bool(surfaces&UNLISTED)
        obs_unlisted=any(q in UNLISTED and (a,b) in (rt|st) and a in ({src}|td) and b in td for a,b,q in edges)
        blind_aff=bool(surfaces&blind)
        local=desc(rt,src); union=desc(rt|st,src)
        policies={"local":local,"warning":whole if known else local,"union":union,
                  "observed_unlisted":whole if obs_unlisted else union,
                  "mediated_manifest":whole if unlisted else union,"whole":whole}
        meta["blind_affected"]+=blind_aff; meta["unlisted_affected"]+=unlisted
        for name,replay in policies.items():
            ok=td.issubset(replay); cost=1+len(replay); c[name]["ok"]+=ok; c[name]["n"]+=1
            s[name]["cost"]+=cost; s[name]["replay"]+=len(replay)
    return {"p_blind":p_blind,"runtime_capture_nonblind_risky":xr,"static_capture_nonblind_risky":ys,
            "blind_affected":meta["blind_affected"]/N_GRAPHS,"unlisted_affected":meta["unlisted_affected"]/N_GRAPHS,
            "rows":[{"policy":n,"recovery":c[n]["ok"]/N_GRAPHS,"mean_replay":s[n]["replay"]/N_GRAPHS,
                     "correct_per_100k":c[n]["ok"]/s[n]["cost"]*100000} for n in names]}


def positive_scope(p_blind,detector_sensitivity=.90):
    # Listed surfaces are perfectly represented in normal union. Only unlisted
    # custom/reflection classes can be jointly blind. A perfect scope manifest
    # knows that an unlisted surface was used and fails closed; an ideal mediator
    # additionally captures exact edges at the chokepoint.
    names=["silent_union","manifest_awareness","mediated_capture","imperfect_manifest","whole"]
    c={n:collections.Counter() for n in names}; s={n:collections.defaultdict(float) for n in names}; meta=collections.Counter()
    for gid,(edges,src) in enumerate(GRAPHS):
        true={(a,b) for a,b,_ in edges}; td=desc(true,src); whole=set(range(N))-{src}
        r=rng_for("blindB",gid,p_blind); blind={q for q in UNLISTED if r.random()<p_blind}
        normal={(a,b) for a,b,q in edges if q not in blind}; union=desc(normal,src)
        surfaces=affected_surfaces(edges,src,td); blind_aff=surfaces&blind
        detected=False
        if blind_aff:
            rd=rng_for("detectB",gid,p_blind,detector_sensitivity)
            detected=any(rd.random()<detector_sensitivity for _ in sorted(blind_aff))
        policies={"silent_union":union,"manifest_awareness":whole if blind_aff else union,
                  "mediated_capture":td,"imperfect_manifest":whole if detected else union,"whole":whole}
        meta["blind_affected"]+=bool(blind_aff); meta["unlisted_affected"]+=bool(surfaces&UNLISTED)
        for name,replay in policies.items():
            ok=td.issubset(replay); c[name]["ok"]+=ok; c[name]["n"]+=1; s[name]["replay"]+=len(replay); s[name]["cost"]+=1+len(replay)
    return {"p_blind":p_blind,"detector_sensitivity":detector_sensitivity,
            "blind_affected":meta["blind_affected"]/N_GRAPHS,"unlisted_affected":meta["unlisted_affected"]/N_GRAPHS,
            "rows":[{"policy":n,"recovery":c[n]["ok"]/N_GRAPHS,"mean_replay":s[n]["replay"]/N_GRAPHS,
                     "correct_per_100k":c[n]["ok"]/s[n]["cost"]*100000} for n in names]}

if __name__=="__main__":
    print("FIXED MARGINAL EDGE RECALL / CORRELATED SURFACE BLINDNESS")
    for p in (0.0,.10,.25,.40): print(fixed_marginal(p))
    print("POSITIVE CAPTURE-SCOPE CONTRACT")
    for p in (0.0,.10,.25,.40): print(positive_scope(p,.90))
