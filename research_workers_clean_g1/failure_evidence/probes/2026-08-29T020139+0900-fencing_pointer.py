import hashlib
import json
import sqlite3


def fencing_probe():
    """Deterministic single-process protected-resource comparison.

    Event order is held fixed: claimant B (generation 2) commits, then delayed
    claimant A (generation 1) resumes.  The no-fence arm accepts both writes;
    the fenced arm rejects generations older than the resource's current fence.
    """
    no_fence = {"value": None, "last_writer": None}
    no_fence["value"], no_fence["last_writer"] = "B_current", "B_gen2"
    no_fence["value"], no_fence["last_writer"] = "A_stale", "A_gen1"

    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE resource(id INTEGER PRIMARY KEY, value TEXT NOT NULL, fence INTEGER NOT NULL)"
    )
    conn.execute("INSERT INTO resource(id, value, fence) VALUES(1, 'initial', 0)")

    cur_b = conn.execute(
        "UPDATE resource SET value=?, fence=? WHERE id=1 AND ? >= fence",
        ("B_current", 2, 2),
    )
    cur_a = conn.execute(
        "UPDATE resource SET value=?, fence=? WHERE id=1 AND ? >= fence",
        ("A_stale", 1, 1),
    )
    row = conn.execute("SELECT value, fence FROM resource WHERE id=1").fetchone()

    return {
        "scenario": "B(gen2) commits, then delayed A(gen1) resumes",
        "no_fence": {
            "final_value": no_fence["value"],
            "last_writer": no_fence["last_writer"],
            "stale_overwrite_committed": no_fence["value"] == "A_stale",
        },
        "fenced": {
            "B_rowcount": cur_b.rowcount,
            "A_rowcount": cur_a.rowcount,
            "final_value": row[0],
            "final_fence": row[1],
            "stale_overwrite_rejected": cur_a.rowcount == 0
            and row == ("B_current", 2),
        },
    }


def digest(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def pointer_probe():
    """Deterministic stale cached-pointer reconstruction comparison."""
    cp1 = {
        "checkpoint_id": "cp1",
        "seq": 1,
        "predecessor": None,
        "payload": {"state": "older"},
    }
    cp2 = {
        "checkpoint_id": "cp2",
        "seq": 2,
        "predecessor": "cp1",
        "payload": {"state": "newer"},
    }
    cp1_hash, cp2_hash = digest(cp1), digest(cp2)
    cached_pointer = {"checkpoint_id": "cp1", "seq": 1, "hash": cp1_hash}
    authoritative_pointer = {
        "checkpoint_id": "cp2",
        "seq": 2,
        "hash": cp2_hash,
    }
    objects = {"cp1": cp1, "cp2": cp2}

    naive_selected = objects[cached_pointer["checkpoint_id"]]
    mismatch = (
        cached_pointer["checkpoint_id"] != authoritative_pointer["checkpoint_id"]
        or cached_pointer["seq"] != authoritative_pointer["seq"]
        or cached_pointer["hash"] != authoritative_pointer["hash"]
    )

    selected_after_revalidation = None
    provenance_ok = False
    if mismatch:
        obj = objects[authoritative_pointer["checkpoint_id"]]
        provenance_ok = (
            digest(obj) == authoritative_pointer["hash"]
            and obj["seq"] == authoritative_pointer["seq"]
            and obj["predecessor"] == "cp1"
        )
        if provenance_ok:
            selected_after_revalidation = obj

    return {
        "cached_pointer": cached_pointer,
        "authoritative_pointer": authoritative_pointer,
        "naive_cache_only_resume": {
            "selected_checkpoint_id": naive_selected["checkpoint_id"],
            "selected_seq": naive_selected["seq"],
            "stale_resume": naive_selected["seq"] < authoritative_pointer["seq"],
        },
        "guarded_resume": {
            "pointer_mismatch_detected": mismatch,
            "resume_refused_until_revalidated": mismatch,
            "authoritative_object_provenance_ok": provenance_ok,
            "selected_checkpoint_id_after_revalidation": (
                selected_after_revalidation["checkpoint_id"]
                if selected_after_revalidation
                else None
            ),
            "selected_seq_after_revalidation": (
                selected_after_revalidation["seq"]
                if selected_after_revalidation
                else None
            ),
        },
    }


if __name__ == "__main__":
    result = {
        "schema_version": 1,
        "probe": "phase1_failure_evidence_fencing_and_pointer_reconstruction",
        "fencing": fencing_probe(),
        "cached_latest": pointer_probe(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
