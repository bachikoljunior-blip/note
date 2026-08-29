from itertools import product
from collections import Counter

OBJECT_STATE = ["reachable", "unreachable_retained", "unreachable_gone"]
HIST_TRANSPORT = ["ok", "rate_limit"]
COPY_STATE = ["none", "exact", "deleted_gc", "wrong_reincarnation"]
COPY_TRANSPORT = ["ok", "rate_limit"]
ANCHOR_STATE = ["expected", "moved", "deleted_recreated", "absent"]
ANCHOR_TRANSPORT = ["ok", "rate_limit"]
AUTHORITY = ["same", "superseded"]
RETAIN_RESPONSE = ["observed_success", "applied_response_lost", "not_applied_response_lost"]

SCENARIOS = list(product(OBJECT_STATE, HIST_TRANSPORT, COPY_STATE, COPY_TRANSPORT,
                         ANCHOR_STATE, ANCHOR_TRANSPORT, AUTHORITY, RETAIN_RESPONSE))
STRATEGIES = [
    "historical_sha_fenced",
    "current_path_fallback_no_digest",
    "mutable_anchor_name_fenced",
    "mutable_anchor_sha_fenced",
    "copy_digest_fenced",
    "copy_digest_no_authority",
    "copy_digest_blind_retry",
]

def evaluate(s, name):
    ostate, htransport, cstate, ctransport, astate, atransport, auth, rresp = s
    out = dict(success=0, false_wrong=0, stale=0, fail_closed=0, dup_retention=0, reads=0)

    def historical_available():
        return htransport == "ok" and ostate in ("reachable", "unreachable_retained")

    def auth_gate(kind="correct"):
        out["reads"] += 1
        if auth == "superseded":
            out["fail_closed"] = 1
        elif kind == "correct":
            out["success"] = 1
        else:
            out["false_wrong"] = 1

    if name == "historical_sha_fenced":
        out["reads"] = 1
        if historical_available(): auth_gate("correct")
        else: out["fail_closed"] = 1

    elif name == "current_path_fallback_no_digest":
        out["reads"] = 1
        if historical_available():
            auth_gate("correct")
        else:
            out["reads"] += 1
            if ctransport == "rate_limit": out["fail_closed"] = 1
            elif cstate == "exact": auth_gate("correct")
            elif cstate == "wrong_reincarnation": auth_gate("wrong")
            else: out["fail_closed"] = 1

    elif name == "mutable_anchor_name_fenced":
        out["reads"] = 1
        if atransport == "rate_limit": out["fail_closed"] = 1
        elif astate == "expected": auth_gate("correct")
        elif astate in ("moved", "deleted_recreated"): auth_gate("wrong")
        else: out["fail_closed"] = 1

    elif name == "mutable_anchor_sha_fenced":
        out["reads"] = 1
        if atransport == "rate_limit": out["fail_closed"] = 1
        elif astate == "expected": auth_gate("correct")
        else: out["fail_closed"] = 1

    else:
        out["reads"] = 1
        source = "correct" if ctransport == "ok" and cstate == "exact" else None
        if source is None:
            out["reads"] += 1
            if historical_available(): source = "correct"
        if name == "copy_digest_blind_retry" and rresp == "applied_response_lost":
            out["dup_retention"] = 1
        if source is None:
            out["fail_closed"] = 1
        elif name == "copy_digest_no_authority":
            if auth == "superseded": out["stale"] = 1
            else: out["success"] = 1
        else:
            auth_gate(source)
    return out

if __name__ == "__main__":
    print("scenarios", len(SCENARIOS), "strategy_evaluations", len(SCENARIOS) * len(STRATEGIES))
    for name in STRATEGIES:
        total = Counter()
        for s in SCENARIOS:
            total.update(evaluate(s, name))
        print(name, dict(total), "avg_reads", round(total["reads"] / len(SCENARIOS), 4))
