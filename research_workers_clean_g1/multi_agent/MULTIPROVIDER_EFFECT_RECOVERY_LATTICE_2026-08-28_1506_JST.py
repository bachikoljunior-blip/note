from itertools import product
import json

LIVE = ["PRESENT", "ABSENT", "UNKNOWN"]
RECORDED = ["SUCCESS", "NO_EFFECT", "UNKNOWN"]


def latent_actuals(live):
    if live == "PRESENT":
        return [1]
    if live == "ABSENT":
        return [0]
    return [0, 1]


def proof_gated(p1, p2):
    lives = [p1["live"], p2["live"]]
    if all(x == "PRESENT" for x in lives):
        return ("TERMINAL_FORWARD", "forward")
    if all(x == "ABSENT" for x in lives):
        return ("TERMINAL_ROLLBACK", "rollback")
    if any(x == "UNKNOWN" for x in lives):
        if all((p["live"] != "UNKNOWN") or p["fenced"] for p in (p1, p2)):
            return ("PENDING_RECONCILE_FORWARD", None)
        if all((p["live"] != "UNKNOWN") or p["compensable"] for p in (p1, p2)):
            return ("PENDING_RECONCILE_COMPENSATE", None)
        return ("BLOCK", None)
    if all(p["compensable"] for p in (p1, p2) if p["live"] == "PRESENT"):
        return ("PENDING_COMPENSATE", None)
    if all(p["fenced"] for p in (p1, p2) if p["live"] == "ABSENT"):
        return ("PENDING_FORWARD", None)
    return ("BLOCK", None)


def trust_record(p1, p2):
    inferred = []
    for p in (p1, p2):
        if p["live"] == "PRESENT":
            inferred.append(1)
        elif p["live"] == "ABSENT":
            inferred.append(0)
        else:
            inferred.append(1 if p["recorded"] == "SUCCESS" else 0)
    if inferred == [1, 1]:
        return ("TERMINAL_FORWARD", "forward")
    if inferred == [0, 0]:
        return ("TERMINAL_ROLLBACK", "rollback")
    return ("BLOCK", None)


def terminal_safe(term, actual):
    if term == "forward":
        return actual == (1, 1)
    if term == "rollback":
        return actual == (0, 0)
    return True


providers = [
    {"live": live, "recorded": recorded, "fenced": fenced, "compensable": compensable}
    for live, recorded, fenced, compensable
    in product(LIVE, RECORDED, [False, True], [False, True])
]
pairs = list(product(providers, repeat=2))

out = {
    "scope": {
        "providers": 2,
        "observable_combinations": len(pairs),
        "grid_semantics": "Mechanism lattice, not a prevalence-weighted or real-world probability model.",
        "actual_effect": "0 or 1 per provider; PRESENT fixes 1, ABSENT fixes 0, UNKNOWN allows either.",
        "compensation_success": "hidden 0/1 bit per provider in common latent world measure."
    },
    "compatible_latent_worlds": 0,
    "policies": {
        "proof_gated": {"terminal_admissions": 0, "unsafe_terminal": 0},
        "trust_record": {"terminal_admissions": 0, "unsafe_terminal": 0},
        "blind_retry": {"terminal_admissions": 0, "unsafe_terminal": 0},
        "blind_compensate": {"terminal_admissions": 0, "unsafe_terminal": 0}
    }
}

for p1, p2 in pairs:
    for a1, a2 in product(latent_actuals(p1["live"]), latent_actuals(p2["live"])):
        for cs1, cs2 in product([0, 1], [0, 1]):
            out["compatible_latent_worlds"] += 1
            actual = (a1, a2)

            _, term = proof_gated(p1, p2)
            if term is not None:
                d = out["policies"]["proof_gated"]
                d["terminal_admissions"] += 1
                if not terminal_safe(term, actual):
                    d["unsafe_terminal"] += 1

            _, term = trust_record(p1, p2)
            if term is not None:
                d = out["policies"]["trust_record"]
                d["terminal_admissions"] += 1
                if not terminal_safe(term, actual):
                    d["unsafe_terminal"] += 1

            d = out["policies"]["blind_retry"]
            d["terminal_admissions"] += 1
            retry_unsafe = False
            final = []
            for p, a in ((p1, a1), (p2, a2)):
                if p["live"] == "PRESENT":
                    final.append(1)
                elif p["fenced"]:
                    final.append(1)
                else:
                    if a == 1:
                        retry_unsafe = True
                    final.append(1)
            if retry_unsafe or tuple(final) != (1, 1):
                d["unsafe_terminal"] += 1

            d = out["policies"]["blind_compensate"]
            can_attempt = True
            candidates = []
            for p, a, cs in ((p1, a1, cs1), (p2, a2, cs2)):
                believed_present = (
                    p["live"] == "PRESENT"
                    or (p["live"] == "UNKNOWN" and p["recorded"] == "SUCCESS")
                )
                if believed_present and not p["compensable"]:
                    can_attempt = False
                candidates.append((a, cs if believed_present else None))
            if can_attempt:
                d["terminal_admissions"] += 1
                final = []
                for p, (a, cs) in zip((p1, p2), candidates):
                    believed_present = (
                        p["live"] == "PRESENT"
                        or (p["live"] == "UNKNOWN" and p["recorded"] == "SUCCESS")
                    )
                    if believed_present:
                        final.append(0 if (a == 1 and cs == 1) else a)
                    else:
                        final.append(a)
                if tuple(final) != (0, 0):
                    d["unsafe_terminal"] += 1

for name, d in out["policies"].items():
    d["unsafe_fraction_of_terminal"] = (
        d["unsafe_terminal"] / d["terminal_admissions"] if d["terminal_admissions"] else None
    )

removals = 0
violations = 0
for p1, p2 in pairs:
    _, original_term = proof_gated(p1, p2)
    pair = [p1, p2]
    for i in range(2):
        variants = []
        p = pair[i]
        if p["live"] in ("PRESENT", "ABSENT"):
            q = p.copy()
            q["live"] = "UNKNOWN"
            variants.append(q)
        if p["fenced"]:
            q = p.copy()
            q["fenced"] = False
            variants.append(q)
        if p["compensable"]:
            q = p.copy()
            q["compensable"] = False
            variants.append(q)
        for q in variants:
            pp = [dict(pair[0]), dict(pair[1])]
            pp[i] = q
            _, weakened_term = proof_gated(pp[0], pp[1])
            removals += 1
            if weakened_term is not None and original_term is None:
                violations += 1

out["policies"]["proof_gated"]["terminal_admission_monotonicity"] = {
    "one_step_evidence_or_capability_removals_tested": removals,
    "violations": violations,
    "definition": "Removing one live-state proof or one retry/compensation capability must not create a new terminal admission."
}

print(json.dumps(out, indent=2, sort_keys=True))
