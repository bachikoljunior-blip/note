from itertools import product
from collections import Counter, defaultdict
import json

DOMAINS = ("same_ref", "separate_claim")
TRANSITIONS = ("none", "takeover", "cancel")
PREPUBLISH_BRANCH = ("none", "sibling")
OUTCOMES = ("ok", "fail", "amb_applied", "amb_not_applied")
CRASH = ("none", "after_object_before_publish", "after_request_before_readback")
LATER_REF = ("none", "descendant_of_p", "sibling_without_p")
BOOLEANS = (False, True)

def contains_proposal(head):
    return head in ("P", "D")

def base_head(domain, transition, sibling):
    head = "B"
    if domain == "same_ref" and transition != "none":
        head = "S"
    if sibling == "sibling":
        head = "S"
    return head

def publish(head, attempt, outcome):
    if not attempt:
        return head, False
    can_fast_forward = head == "B"  # proposal P has parent B
    applied = can_fast_forward and outcome in ("ok", "amb_applied")
    return ("P" if applied else head), applied

def apply_later_ref(head, later, force_possible):
    if later == "none":
        return head
    if later == "descendant_of_p":
        # D has P in ancestry. B -> D and P -> D are fast-forward.
        # S -> D requires an overwrite/force-like history rewrite.
        if head in ("B", "P", "D") or force_possible:
            return "D"
        return head
    if later == "sibling_without_p":
        # W excludes P. B/S/W -> W can be monotonic; P/D -> W requires force/rewrite.
        if not contains_proposal(head) or force_possible:
            return "W"
        return head
    raise ValueError(later)

def actual_current_terminal(head, transition):
    # A pre-publication takeover/cancel invalidates this old integrator's authority.
    return contains_proposal(head) and transition == "none"

def git_ref_only(s):
    """
    Negative control:
    - relies on update_ref(force=false) as the only stale-writer fence;
    - does not recheck a separate claim domain;
    - after response loss, exact current ref SHA == P is the only success proof;
    - if current SHA differs and replay is requested, it retries/rebuilds.
    """
    head0 = base_head(s["domain"], s["transition"], s["sibling"])
    attempt = s["crash"] != "after_object_before_publish"
    head1, direct_applied = publish(head0, attempt, s["outcome"])
    head2 = apply_later_ref(head1, s["later_ref"], s["force_possible"])

    actual = actual_current_terminal(head2, s["transition"])
    claimed = head2 == "P"
    false_terminal = claimed and not actual
    missed_safe = (not claimed) and actual

    duplicate = (
        s["replay"]
        and head2 != "P"
        and contains_proposal(head2)
        and s["transition"] == "none"
    )

    return {
        "actual_terminal": actual,
        "claimed_terminal": claimed,
        "false_terminal": false_terminal,
        "missed_safe_terminal": missed_safe,
        "duplicate_logical_integration": duplicate,
        "direct_ref_apply": direct_applied,
        "partial_published_state": False,
        "proposal_not_in_current_ref_ancestry": not contains_proposal(head2),
        "recovery_needed": (
            s["crash"] != "none"
            or s["outcome"].startswith("amb_")
            or s["later_ref"] != "none"
        ),
        "recoverable": True,
        "recovery_reads": 1,
        "final_head": head2,
    }

def git_fenced_reconcile(s):
    """
    Strong candidate:
    - proposal P is built from exact base B;
    - force=false publication is used;
    - when claim authority is separate, current claim/lifecycle is rechecked before publish/replay;
    - when authority is same-ref, any pre-publication takeover/cancel advances that ref and
      force=false rejects the old sibling proposal;
    - ambiguous/readback recovery uses exact P, or a persistent applied_integration_id marker,
      or a durable proposal SHA plus ancestry;
    - replay occurs only after current authority and current absence are re-established.
    """
    head0 = base_head(s["domain"], s["transition"], s["sibling"])
    current_authority = s["transition"] == "none"
    attempt = s["crash"] != "after_object_before_publish" and current_authority
    head1, direct_applied = publish(head0, attempt, s["outcome"])
    head2 = apply_later_ref(head1, s["later_ref"], s["force_possible"])

    actual = actual_current_terminal(head2, s["transition"])
    recovery_needed = (
        s["crash"] != "none"
        or s["outcome"].startswith("amb_")
        or s["later_ref"] != "none"
    )

    knows_proposal_sha = s["proposal_sha_durable"] or s["crash"] == "none"

    if not current_authority:
        claimed = False
        recoverable = True
        reads = 1  # current claim/lifecycle
    elif s["persistent_applied_id"]:
        # A logical marker in the current canonical tree directly answers current-effect presence.
        claimed = contains_proposal(head2)
        recoverable = True
        reads = 2  # current ref + canonical marker/tree
    elif knows_proposal_sha and head2 == "P":
        claimed = True
        recoverable = True
        reads = 1  # exact current ref SHA
    elif knows_proposal_sha and contains_proposal(head2):
        claimed = True
        recoverable = True
        reads = 2  # current ref + ancestry comparison
    elif knows_proposal_sha and not contains_proposal(head2):
        claimed = False
        recoverable = True
        reads = 2  # current ref + ancestry comparison proves current absence
    elif recovery_needed:
        # After a crash/readback ambiguity, losing both the logical marker and proposal SHA
        # leaves ref-only recovery unable to identify the logical proposal. Fail closed.
        claimed = False
        recoverable = False
        reads = None
    else:
        # No recovery boundary occurred; volatile proposal identity is still available.
        claimed = head2 == "P"
        recoverable = True
        reads = 1

    false_terminal = claimed and not actual
    missed_safe = (not claimed) and actual

    # Strong replay is suppressed whenever current effect is proven present and is blocked
    # whenever current claim is stale. A changed sibling ref requires rebase/rebuild under
    # a freshly validated generation instead of replaying the old P.
    duplicate = False

    return {
        "actual_terminal": actual,
        "claimed_terminal": claimed,
        "false_terminal": false_terminal,
        "missed_safe_terminal": missed_safe,
        "duplicate_logical_integration": duplicate,
        "direct_ref_apply": direct_applied,
        "partial_published_state": False,
        "proposal_not_in_current_ref_ancestry": not contains_proposal(head2),
        "recovery_needed": recovery_needed,
        "recoverable": recoverable,
        "recovery_reads": reads,
        "final_head": head2,
    }

def aggregate(fn, scenarios):
    c = Counter()
    reads = []
    for s in scenarios:
        r = fn(s)
        c["scenarios"] += 1
        for key in (
            "actual_terminal", "claimed_terminal", "false_terminal",
            "missed_safe_terminal", "duplicate_logical_integration",
            "direct_ref_apply", "partial_published_state",
            "proposal_not_in_current_ref_ancestry", "recovery_needed", "recoverable"
        ):
            if r[key]:
                c[key] += 1
        if r["recovery_needed"] and r["recovery_reads"] is not None:
            reads.append(r["recovery_reads"])
    c["unrecoverable"] = c["scenarios"] - c["recoverable"]
    c["avg_recovery_reads_when_resolved"] = (
        sum(reads) / len(reads) if reads else 0.0
    )
    return dict(c)

def slice_counts(fn, scenarios):
    out = {}
    def collect(name, pred):
        c = Counter()
        for s in scenarios:
            if not pred(s):
                continue
            r = fn(s)
            c["n"] += 1
            for key in (
                "actual_terminal", "claimed_terminal", "false_terminal",
                "missed_safe_terminal", "duplicate_logical_integration",
                "direct_ref_apply", "proposal_not_in_current_ref_ancestry", "recoverable"
            ):
                if r[key]:
                    c[key] += 1
        out[name] = dict(c)

    collect("same_ref_stale_prepublication",
            lambda s: s["domain"] == "same_ref" and s["transition"] != "none")
    collect("separate_claim_stale_prepublication",
            lambda s: s["domain"] == "separate_claim" and s["transition"] != "none")
    collect("descendant_current_no_stale_authority",
            lambda s: s["transition"] == "none" and s["later_ref"] == "descendant_of_p")
    collect("crash_after_object_before_publish",
            lambda s: s["crash"] == "after_object_before_publish")
    collect("descendant_actual_marker_or_sha",
            lambda s: (
                s["transition"] == "none"
                and s["later_ref"] == "descendant_of_p"
                and (s["persistent_applied_id"] or s["proposal_sha_durable"])
            ))
    collect("descendant_actual_no_marker_no_sha",
            lambda s: (
                s["transition"] == "none"
                and s["later_ref"] == "descendant_of_p"
                and not s["persistent_applied_id"]
                and not s["proposal_sha_durable"]
            ))
    collect("crash_recovery_with_marker",
            lambda s: s["crash"] != "none" and s["persistent_applied_id"])
    collect("crash_recovery_no_marker_with_durable_sha",
            lambda s: (
                s["crash"] != "none"
                and not s["persistent_applied_id"]
                and s["proposal_sha_durable"]
            ))
    collect("crash_recovery_no_marker_no_durable_sha",
            lambda s: (
                s["crash"] != "none"
                and not s["persistent_applied_id"]
                and not s["proposal_sha_durable"]
            ))
    return out

def main():
    names = [
        "domain", "transition", "sibling", "outcome", "crash", "later_ref",
        "force_possible", "replay", "persistent_applied_id", "proposal_sha_durable"
    ]
    axes = [
        DOMAINS, TRANSITIONS, PREPUBLISH_BRANCH, OUTCOMES, CRASH, LATER_REF,
        BOOLEANS, BOOLEANS, BOOLEANS, BOOLEANS
    ]
    scenarios = [dict(zip(names, vals)) for vals in product(*axes)]

    result = {
        "schema_version": 1,
        "model": "git_commit_ref_publication_claim_fencing_finite_lattice",
        "scenario_count": len(scenarios),
        "axes": {name: list(axis) for name, axis in zip(names, axes)},
        "protocols": {
            "git_ref_only_negative_control": aggregate(git_ref_only, scenarios),
            "git_force_false_plus_claim_recheck_and_reconcile": aggregate(git_fenced_reconcile, scenarios),
        },
        "slices": {
            "git_ref_only_negative_control": slice_counts(git_ref_only, scenarios),
            "git_force_false_plus_claim_recheck_and_reconcile": slice_counts(git_fenced_reconcile, scenarios),
        },
        "structural_comparison_to_prior_candidates": {
            "co_located_contents_cas": {
                "publication_boundary": "one CAS-protected authority object",
                "multi_path_partial_publication": False,
                "orphan_git_objects": False,
                "same_object_stale_writer_fence": True,
                "single_current_read_can_include_generation_epoch_and_applied_id": True,
            },
            "git_tree_commit_ref": {
                "publication_boundary": "single branch ref update after immutable tree+commit creation",
                "multi_path_partial_publication": False,
                "orphan_git_objects_or_unpublished_objects_possible": True,
                "force_false_fences_same_ref_sibling_advances": True,
                "force_false_fences_separate_claim_domain": False,
                "response_loss_can_require_ancestry_or_persistent_applied_id": True,
            },
            "split_files_plus_intent_event": {
                "publication_boundary": "multiple file writes plus commit event",
                "multi_path_partial_publication": True,
                "orphan_git_objects": False,
                "journal_improves_recovery_but_is_not_current_authority": True,
                "multiple_current_reads_required": True,
            },
        },
        "scope_notes": [
            "Counts are exhaustive over an equal-weight synthetic mechanism lattice, not operational failure probabilities.",
            "Proposal P has exact parent B. Under a monotonic no-force history, update_ref(force=false) rejects a sibling ref advance because P is not a descendant of that new head.",
            "A separate claim/lifecycle domain is deliberately not changed by the branch-ref publication; force=false therefore cannot fence stale authority there without an explicit recheck.",
            "A later descendant D may contain P even when P was never the branch head, because another actor can create D with parent P and fast-forward B directly to D. Exact ref-SHA equality is therefore weaker than current-effect proof.",
            "Persistent applied_integration_id means a logical marker stored in the canonical tree; durable proposal SHA enables ancestry comparison after restart. If a crash loses both, the strong policy blocks rather than infer logical effect from ref movement alone. Full per-path digest reconstruction is intentionally not modeled as a fallback.",
            "Creating tree/commit objects is modeled as non-authoritative until the branch ref reaches a commit whose current tree carries the integration. The counter named proposal_not_in_current_ref_ancestry does not claim global Git reachability or garbage-collection status; other refs are outside the model.",
            "force_possible permits later history rewrite in the synthetic environment. The positive stale-writer claim for force=false is scoped to writers that obey the non-force publication rule and to authority changes encoded on the same ref or explicitly rechecked.",
            "The model concerns canonical repository state. It does not claim that historical publication is harmless for external hooks or side effects triggered by transient ref movement.",
        ],
    }

    # Assertions make the intended mechanism claims executable.
    neg = result["protocols"]["git_ref_only_negative_control"]
    strong = result["protocols"]["git_force_false_plus_claim_recheck_and_reconcile"]
    neg_s = result["slices"]["git_ref_only_negative_control"]
    strong_s = result["slices"]["git_force_false_plus_claim_recheck_and_reconcile"]

    assert len(scenarios) == 6912
    assert strong.get("false_terminal", 0) == 0
    assert strong.get("duplicate_logical_integration", 0) == 0
    assert strong.get("partial_published_state", 0) == 0
    assert neg_s["same_ref_stale_prepublication"].get("false_terminal", 0) == 0
    assert neg_s["same_ref_stale_prepublication"].get("direct_ref_apply", 0) == 0
    assert neg_s["separate_claim_stale_prepublication"]["false_terminal"] > 0
    assert neg_s["separate_claim_stale_prepublication"]["direct_ref_apply"] > 0
    assert neg.get("duplicate_logical_integration", 0) > 0
    assert strong_s["descendant_actual_marker_or_sha"].get("missed_safe_terminal", 0) == 0
    assert strong_s["descendant_actual_no_marker_no_sha"].get("missed_safe_terminal", 0) > 0
    assert strong_s["crash_after_object_before_publish"].get("false_terminal", 0) == 0
    assert strong_s["crash_after_object_before_publish"].get("proposal_not_in_current_ref_ancestry", 0) > 0

    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
