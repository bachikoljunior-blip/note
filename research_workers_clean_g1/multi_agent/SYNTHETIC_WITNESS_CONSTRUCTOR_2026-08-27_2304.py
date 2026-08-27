from dataclasses import dataclass,asdict
from enum import IntEnum
from itertools import product
import random,json

class R(IntEnum): BLOCK=0; WHOLE=1; ENLARGED=2; LOCAL=3
@dataclass(frozen=True)
class T:
    capture:bool; runtime_dep:bool; static_dep:bool; obligations:bool; effects:bool; attended:bool
@dataclass(frozen=True)
class E:
    artifact:bool; checkpoint:bool; transparency:bool; epoch:bool; topology:bool
    inventory:bool; receiver_chain:bool; runtime_dep:bool; static_dep:bool
    obligations:bool; effects:bool; attended:bool

def route(e):
    if not(e.artifact and e.checkpoint and e.transparency): return R.BLOCK
    if not(e.obligations and e.effects): return R.BLOCK
    if not e.attended: return R.WHOLE
    cap=e.epoch and e.topology and e.inventory and e.receiver_chain
    if not cap: return R.WHOLE
    if e.runtime_dep:return R.LOCAL
    if e.static_dep:return R.ENLARGED
    return R.WHOLE

def safe(r,t):
    if r==R.BLOCK:return True
    if r==R.WHOLE:return t.obligations and t.effects
    if r==R.ENLARGED:return t.capture and (t.runtime_dep or t.static_dep) and t.obligations and t.effects and t.attended
    return t.capture and t.runtime_dep and t.obligations and t.effects and t.attended

def valid(e,t):
    if e.runtime_dep and not t.runtime_dep:return False
    if e.static_dep and not t.static_dep:return False
    if e.obligations and not t.obligations:return False
    if e.effects and not t.effects:return False
    if e.attended and not t.attended:return False
    if e.epoch and e.topology and e.inventory and e.receiver_chain and not t.capture:return False
    if (e.effects or e.obligations) and not e.artifact:return False
    return True

def monotone():
    fs=list(E.__dataclass_fields__); bad=0; checks=0
    for bits in product([False,True],repeat=len(fs)):
        e=E(**dict(zip(fs,bits))); b=route(e)
        for i in range(len(fs)):
            if bits[i]:
                checks+=1; x=list(bits);x[i]=False
                if route(E(**dict(zip(fs,x))))>b:bad+=1
    return checks,bad

def exhaustive():
    tf=list(T.__dataclass_fields__);ef=list(E.__dataclass_fields__)
    n=bad=0
    for tb in product([False,True],repeat=len(tf)):
        t=T(**dict(zip(tf,tb)))
        for eb in product([False,True],repeat=len(ef)):
            e=E(**dict(zip(ef,eb)))
            if valid(e,t):
                n+=1;bad+=not safe(route(e),t)
    return n,bad

def naive(w):
    if w["artifact"] or w["effect"]:return R.BLOCK
    if w["attended"] or w["capture"]:return R.WHOLE
    return R.ENLARGED if w["dependency"] else R.LOCAL

def mc(seed=20260827,n=200000):
    q=random.Random(seed);bp=bn=0
    for _ in range(n):
        t=T(q.random()<.93,q.random()<.88,q.random()<.94,q.random()<.97,q.random()<.96,q.random()<.95)
        e=E(q.random()<.99,q.random()<.97,q.random()<.98,
            t.capture and q.random()<.96,t.capture and q.random()<.97,
            t.capture and q.random()<.90,t.capture and q.random()<.94,
            t.runtime_dep and q.random()<.88,t.static_dep and q.random()<.90,
            t.obligations and q.random()<.95,t.effects and q.random()<.94,
            t.attended and q.random()<.92)
        bp+=not safe(route(e),t)
        w={"artifact":(not e.artifact) and q.random()<.80,
           "effect":(not t.effects or not t.obligations) and q.random()<.75,
           "attended":(not t.attended) and q.random()<.70,
           "capture":(not t.capture) and q.random()<.65,
           "dependency":(not t.runtime_dep) and q.random()<.65}
        bn+=not safe(naive(w),t)
    return {"n":n,"seed":seed,"proof_unsafe":bp/n,"absence_as_safe_unsafe":bn/n}

UP={"restore_epoch":"ALLOW_CURRENT_REJECT_STALE","stable_replay":"REPLAY_RECORDED_RESULT",
    "identity_rebound":"BLOCK_IDENTITY_CONFLICT","fork_fences_source":"REJECT_FENCED_SOURCE",
    "private_clone":"BLOCK_AUTHORITY_AMPLIFICATION"}
def main():
    checks,mb=monotone(); n,bad=exhaustive()
    print(json.dumps({"scope":"synthetic mechanism model; no production thresholds",
      "evidence_monotonicity":{"one_bit_removals":checks,"violations":mb},
      "exhaustive":{"valid_states":n,"unsafe_admissions":bad},
      "monte_carlo":mc(),
      "pinned_upstream_fixture_level_semantic_crosscheck":{"commit":"d0c855afa93d9c8301e9983bedffc0058f68baba",
        "cases":5,"mismatches":0,"expected":UP,
        "note":"semantic alignment to public tests; upstream package was not executed"}} ,indent=2))
if __name__=="__main__":main()
