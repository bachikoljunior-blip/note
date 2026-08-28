import json
import os
import sqlite3
import tempfile
import multiprocessing as mp
import time
import hashlib


def run_probe():
    out = {"schema_version": 1, "probe": "phase1_failure_evidence_concurrency_resume", "tests": {}}

    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "fence.db")
        con = sqlite3.connect(db)
        con.execute("create table nofence(id integer primary key, value text, generation integer)")
        con.execute("insert into nofence values(1,'init',0)")
        con.execute("create table fenced(id integer primary key, value text, generation integer)")
        con.execute("insert into fenced values(1,'init',0)")
        con.commit()
        con.close()

        def writer(db_path, table, gen, value, delay, q):
            time.sleep(delay)
            c = sqlite3.connect(db_path, timeout=5)
            if table == "nofence":
                cur = c.execute("update nofence set value=?, generation=? where id=1", (value, gen))
            else:
                cur = c.execute(
                    "update fenced set value=?, generation=? where id=1 and generation < ?",
                    (value, gen, gen),
                )
            c.commit()
            row = c.execute(f"select value,generation from {table} where id=1").fetchone()
            q.put({"table": table, "gen": gen, "rowcount": cur.rowcount, "observed": row})
            c.close()

        q = mp.Queue()
        processes = [
            mp.Process(target=writer, args=(db, "nofence", 2, "B_current", 0.05, q)),
            mp.Process(target=writer, args=(db, "nofence", 1, "A_stale", 0.20, q)),
            mp.Process(target=writer, args=(db, "fenced", 2, "B_current", 0.05, q)),
            mp.Process(target=writer, args=(db, "fenced", 1, "A_stale", 0.20, q)),
        ]
        for p in processes:
            p.start()
        for p in processes:
            p.join()
        events = [q.get() for _ in processes]

        con = sqlite3.connect(db)
        nofence_final = con.execute("select value,generation from nofence where id=1").fetchone()
        fenced_final = con.execute("select value,generation from fenced where id=1").fetchone()
        con.close()

        out["tests"]["multiprocess_fencing"] = {
            "event_order": "generation 2 process commits before delayed generation 1 process",
            "events": sorted(events, key=lambda e: (e["table"], e["gen"])),
            "no_fence_final": {"value": nofence_final[0], "generation": nofence_final[1]},
            "fenced_final": {"value": fenced_final[0], "generation": fenced_final[1]},
            "pass": nofence_final == ("A_stale", 1) and fenced_final == ("B_current", 2),
        }

        def child(attempt, delay, q):
            time.sleep(delay)
            q.put(
                {
                    "logical_child": "child-1",
                    "parent_attempt": attempt,
                    "value": f"result_from_{attempt}",
                }
            )

        q2 = mp.Queue()
        old = mp.Process(target=child, args=(1, 0.20, q2))
        current = mp.Process(target=child, args=(2, 0.05, q2))
        old.start()
        time.sleep(0.03)
        current_attempt = 2
        current.start()
        received = [q2.get(), q2.get()]
        old.join()
        current.join()

        unbound = {}
        bound = {}
        rejected = []
        for result in received:
            unbound[result["logical_child"]] = result["value"]
            if result["parent_attempt"] == current_attempt:
                bound[result["logical_child"]] = result["value"]
            else:
                rejected.append(result)

        out["tests"]["late_child_binding"] = {
            "current_parent_attempt": current_attempt,
            "arrival_order": received,
            "unbound_final": unbound.get("child-1"),
            "bound_final": bound.get("child-1"),
            "rejected": rejected,
            "pass": (
                unbound.get("child-1") == "result_from_1"
                and bound.get("child-1") == "result_from_2"
                and len(rejected) == 1
            ),
        }

        records = [
            {
                "transport_id": "evt_A",
                "object_id": "invoice_42",
                "event_type": "invoice.paid",
                "effect": "mark_order_paid",
            },
            {
                "transport_id": "evt_B",
                "object_id": "invoice_42",
                "event_type": "invoice.paid",
                "effect": "mark_order_paid",
            },
        ]
        seen_transport = set()
        seen_logical = set()
        commits_transport = []
        commits_logical = []
        for record in records:
            if record["transport_id"] not in seen_transport:
                seen_transport.add(record["transport_id"])
                commits_transport.append(record["effect"])
            logical_key = (record["object_id"], record["event_type"])
            if logical_key not in seen_logical:
                seen_logical.add(logical_key)
                commits_logical.append(record["effect"])

        out["tests"]["distinct_transport_duplicate"] = {
            "records": records,
            "message_id_only_commit_count": len(commits_transport),
            "logical_effect_commit_count": len(commits_logical),
            "pass": len(commits_transport) == 2 and len(commits_logical) == 1,
        }

        state_path = os.path.join(td, "state.json")
        resume_token = "resume-" + hashlib.sha256(b"phase1").hexdigest()[:12]

        def pause_writer(path, token):
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"stage": "paused", "resume_token": token, "seq": 1}, f, sort_keys=True)

        def resumer(path, token):
            with open(path, encoding="utf-8") as f:
                state = json.load(f)
            if state.get("resume_token") != token or state.get("stage") != "paused":
                raise RuntimeError("resume identity mismatch")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"stage": "completed", "resume_token": token, "seq": 2}, f, sort_keys=True)

        paused = mp.Process(target=pause_writer, args=(state_path, resume_token))
        paused.start()
        paused.join()
        with open(state_path, encoding="utf-8") as f:
            after_pause = json.load(f)
        time.sleep(0.35)
        with open(state_path, encoding="utf-8") as f:
            after_idle_wait = json.load(f)

        resumed = mp.Process(target=resumer, args=(state_path, resume_token))
        resumed.start()
        resumed.join()
        with open(state_path, encoding="utf-8") as f:
            after_explicit_resume = json.load(f)

        out["tests"]["no_hidden_background_resume"] = {
            "after_pause_exit": after_pause,
            "after_idle_wait": after_idle_wait,
            "after_explicit_resume": after_explicit_resume,
            "pass": (
                after_pause == after_idle_wait
                and after_explicit_resume["seq"] == 2
                and after_explicit_resume["stage"] == "completed"
            ),
        }

    out["pass"] = all(test["pass"] for test in out["tests"].values())
    return out


if __name__ == "__main__":
    print(json.dumps(run_probe(), indent=2, sort_keys=True))
