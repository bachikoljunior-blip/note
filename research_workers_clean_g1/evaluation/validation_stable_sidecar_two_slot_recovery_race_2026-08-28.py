"""Two-slot concurrency/recovery stress for stable-sidecar evaluation journals.

The test keeps one slot normal while a second slot has duplicate reservation
contenders and a SLOT-vs-deadline-CLOSE race. If the racing SLOT wins, its
COMMIT is deliberately omitted to simulate a crash and is recovered from the
same durable SLOT identity before CLOSE.
"""
from __future__ import annotations
from hashlib import sha256
import json
import multiprocessing as mp
import os
from pathlib import Path
import random
import tempfile
import time
from typing import Any

from stable_sidecar_journal_io_2026_08_28 import StableSidecarJournalIO


def canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest_obj(obj: Any) -> str:
    return sha256(canon(obj)).hexdigest()


def enc(event: dict[str, Any]) -> bytes:
    body = canon(event)
    return f"{len(body):08x}:{sha256(body).hexdigest()}:".encode() + body + b"\n"


def dec(blob: bytes) -> tuple[list[dict[str, Any]], int, str]:
    out=[]; pos=0
    while pos < len(blob):
        start=pos
        if len(blob)-pos < 74: return out,start,"partial_header"
        try: n=int(blob[pos:pos+8].decode(),16)
        except Exception: return out,start,"bad_length"
        pos += 8
        if blob[pos:pos+1] != b":": return out,start,"bad_header_sep"
        pos += 1; dg=blob[pos:pos+64]; pos += 64
        if blob[pos:pos+1] != b":": return out,start,"bad_digest_sep"
        pos += 1
        if len(blob)-pos < n+1: return out,start,"partial_body"
        body=blob[pos:pos+n]; pos += n
        if blob[pos:pos+1] != b"\n": return out,start,"missing_newline"
        pos += 1
        if sha256(body).hexdigest().encode() != dg: return out,start,"checksum_mismatch"
        try: out.append(json.loads(body.decode()))
        except Exception: return out,start,"bad_json"
    return out,pos,"clean_eof"


def append_worker(path, expected, frame, delay, q, tag):
    if delay: time.sleep(delay)
    io=StableSidecarJournalIO(path)
    try:
        io.append_fsync_readback(expected, frame)
        q.put((tag,"ok"))
    except Exception as e:
        q.put((tag,type(e).__name__))


def reserve_worker(path, expected, frame, delay, q, launches):
    if delay: time.sleep(delay)
    io=StableSidecarJournalIO(path)
    try:
        io.append_fsync_readback(expected, frame)
        with launches.get_lock(): launches.value += 1
        q.put(("reserve0","ok"))
    except Exception as e:
        q.put(("reserve0",type(e).__name__))


def slot_no_commit_worker(path, expected, frame, delay, q):
    append_worker(path, expected, frame, delay, q, "slot0")


def close_worker(path, expected, frame, delay, q):
    append_worker(path, expected, frame, delay, q, "close")


def replay(main_blob: bytes, ledger_blob: bytes, block_id: str) -> dict[str, Any]:
    me,mn,ms=dec(main_blob); le,ln,ls=dec(ledger_blob)
    assert ms=="clean_eof" and mn==len(main_blob)
    assert ls=="clean_eof" and ln==len(ledger_blob)
    assert len([e for e in me if e.get("kind")=="ADMIT"])==1
    assert len([e for e in me if e.get("kind")=="CLOSE"])==1
    rs=[e for e in le if e.get("kind")=="RESERVE"]
    assert len(rs)==2
    attempts=[e["reservation"]["attempt_id"] for e in rs]
    assert len(set(attempts))==2
    slots={e["slot_id"]:e for e in me if e.get("kind")=="SLOT"}
    commits={e["slot_id"]:e for e in le if e.get("kind")=="COMMIT"}
    assert "s1" in slots and "s1" in commits
    assert ("s0" in slots) == ("s0" in commits)
    vals=[float(slots[s]["score"]) if s in slots else 1.0 for s in ("s0","s1")]
    return {
        "slot0_committed": "s0" in slots,
        "slot1_committed": True,
        "block_score": sum(vals)/2,
        "attempt_ids_unique": True,
        "main_digest": sha256(main_blob).hexdigest(),
        "ledger_digest": sha256(ledger_blob).hexdigest(),
    }


def campaign(seed: int) -> dict[str, Any]:
    r=random.Random(seed)
    with tempfile.TemporaryDirectory(prefix="eval-two-slot-") as td:
        root=Path(td); mpth=root/"main"; lpth=root/"ledger"
        mio=StableSidecarJournalIO(mpth); lio=StableSidecarJournalIO(lpth)
        q=mp.Queue()
        block=f"b{seed}"
        admit={"schema_version":1,"kind":"ADMIT","event_id":f"admit:{block}","block_id":block,
               "slot_ids":["s0","s1"],"admitted_at":0.0,"deadline":1.0,"b_cap":2,
               "reserved_score_runtime_contract":{"schema_version":1,"enforce_for_new_reservations":True}}
        af=enc(admit); main=mio.append_fsync_readback(b"",af)

        def reserve_event(sid: str):
            payload={"block_id":block,"slot_id":sid,"attempt_id":sha256(f"{block}:{sid}".encode()).hexdigest(),
                     "retry_policy":"fail_closed_unresolved","request_binding_digest":sha256(f"req:{seed}:{sid}".encode()).hexdigest()}
            ev={"schema_version":1,"kind":"RESERVE","event_id":f"reserve:{block}:{sid}","block_id":block,"slot_id":sid,
                "reservation":payload,"reservation_digest":digest_obj(payload)}
            return ev,enc(ev)

        r0,r0f=reserve_event("s0")
        launches=mp.Value("i",0)
        ps=[mp.Process(target=reserve_worker,args=(str(lpth),b"",r0f,r.random()*0.004,q,launches)) for _ in range(2)]
        [p.start() for p in ps]; [p.join(10) for p in ps]
        rr=[q.get(timeout=2) for _ in range(2)]
        assert sum(x[1]=="ok" for x in rr)==1
        assert launches.value==1
        ledger=lpth.read_bytes()

        r1,r1f=reserve_event("s1")
        ledger=lio.append_fsync_readback(ledger,r1f)
        with launches.get_lock(): launches.value += 1
        assert launches.value==2

        s1={"schema_version":1,"kind":"SLOT","event_id":f"slot:{block}:s1","block_id":block,"slot_id":"s1",
            "score":0.2,"observed_at":0.8,"attempt_id":r1["reservation"]["attempt_id"],
            "reservation_digest":r1["reservation_digest"]}
        s1f=enc(s1); main=mio.append_fsync_readback(main,s1f)
        c1={"schema_version":1,"kind":"COMMIT","event_id":f"commit:{block}:s1","block_id":block,"slot_id":"s1",
            "reservation_digest":r1["reservation_digest"],"slot_event_digest":digest_obj(s1),"committed_at":0.8}
        ledger=lio.append_fsync_readback(ledger,enc(c1))

        s0={"schema_version":1,"kind":"SLOT","event_id":f"slot:{block}:s0","block_id":block,"slot_id":"s0",
            "score":0.4,"observed_at":1.0,"attempt_id":r0["reservation"]["attempt_id"],
            "reservation_digest":r0["reservation_digest"]}
        s0f=enc(s0)
        close={"schema_version":1,"kind":"CLOSE","event_id":f"close:{block}","block_id":block,"closed_at":1.0,
               "reservation_runtime_provenance_contract":{"pre_score_admit_binding_required_for_enforcement":True}}
        cf=enc(close)
        p0=mp.Process(target=slot_no_commit_worker,args=(str(mpth),main,s0f,r.random()*0.006,q))
        pc=mp.Process(target=close_worker,args=(str(mpth),main,cf,r.random()*0.006,q))
        p0.start(); pc.start(); p0.join(10); pc.join(10)
        a=q.get(timeout=2); b=q.get(timeout=2)
        statuses={a[0]:a[1],b[0]:b[1]}
        main_now=mpth.read_bytes(); evs,n,s=dec(main_now)
        assert s=="clean_eof" and n==len(main_now)
        kinds=[e["kind"] for e in evs]
        recovered_commit=False
        if "SLOT" in kinds and any(e.get("slot_id")=="s0" for e in evs if e.get("kind")=="SLOT"):
            c0={"schema_version":1,"kind":"COMMIT","event_id":f"commit:{block}:s0","block_id":block,"slot_id":"s0",
                "reservation_digest":r0["reservation_digest"],"slot_event_digest":digest_obj(s0),"committed_at":1.0}
            ledger=lio.append_fsync_readback(ledger,enc(c0)); recovered_commit=True
            if "CLOSE" not in kinds:
                main_now=mio.append_fsync_readback(main_now,cf)
        else:
            assert "CLOSE" in kinds

        final=replay(mpth.read_bytes(),lpth.read_bytes(),block)
        again=replay(mpth.read_bytes(),lpth.read_bytes(),block)
        assert final==again
        assert launches.value==2
        expected=0.3 if final["slot0_committed"] else 0.6
        assert abs(final["block_score"]-expected)<1e-12
        final.update({"seed":seed,"scorer_launch_count":launches.value,"recovery_commit":recovered_commit,
                      "slot0_race":statuses.get("slot0"),"close_race":statuses.get("close")})
        return final


def main():
    mp.set_start_method("fork",force=True)
    N=300
    rows=[campaign(i) for i in range(N)]
    out={
        "schema_version":1,"campaigns":N,"failures":0,
        "exactly_two_scorer_launches":sum(x["scorer_launch_count"]==2 for x in rows),
        "unique_attempt_ids":sum(x["attempt_ids_unique"] for x in rows),
        "slot0_committed_with_recovery_commit":sum(x["slot0_committed"] and x["recovery_commit"] for x in rows),
        "slot0_fail_closed_after_close_win":sum(not x["slot0_committed"] for x in rows),
        "block_score_0_3":sum(abs(x["block_score"]-0.3)<1e-12 for x in rows),
        "block_score_0_6":sum(abs(x["block_score"]-0.6)<1e-12 for x in rows),
        "restart_replay_exact":N,
    }
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
