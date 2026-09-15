"""Current checker-v2r4 source materialization for Phase-1 evaluation.

This invocation only materializes and reads back source. It does not execute this
module, materialize schema/control fixtures, create a precommit, or emit RESULT.
The checker consumes caller-supplied current role-local schema/control mappings;
the pinned cfg10/r2 historical schema is provenance only and is never executed.
"""

CHECKER_ID = "phase1_eval_checker_v2_cfg13_r4"
SCHEMA_VERSION = 2
PINNED_HISTORICAL_SCHEMA = {
    "path": "research_workers_clean_g1/evaluation/phase1_rev25_cfg10_checker_v2r2_schema_20260829T1001JST.json",
    "git_blob_sha": "ac0d113a06e71b9ba98f4b7b3b387f08ae20b6f1",
    "sha256": "785db09f933b96d2bb6a4cf06d9588a82ace95f76d028b4ca6d83de6566eeede",
}
ARTIFACT_METADATA = {
    "role": "evaluation",
    "phase_id": "phase_1_chat_parity",
    "task_id": "phase1-clean-evaluation-parity-metrics",
    "effect_chain_id": "checker_v2r4_current_source_materialization_readback",
    "enabled_desired": True,
    "global_completion": False,
    "phase1_completion_claimed": False,
    "scheduler_mutation_by_worker": False,
    "continuation": (
        "Fresh-bootstrap next invocation; resolve role-local LATEST/STATE, persist/read back the required "
        "preflight, then materialize/read back exactly one current cfg13 schema/control-binding or pending-control "
        "activation artifact needed to run phase1_eval_checker_v2_cfg13_r4. Do not execute checker bytes or create "
        "a precommit/RESULT until the current role config explicitly authorizes that next bounded effect chain."
    ),
}


def _required_fields(schema):
    contract = schema.get("case_contract", {})
    required = contract.get("required", [])
    if not isinstance(required, list):
        raise ValueError("schema.case_contract.required must be a list")
    return required


def _identity_check(schema, control):
    identity = control.get("checker_v2_identity", {})
    if identity.get("checker_id") != CHECKER_ID:
        raise ValueError("control checker identity mismatch")
    if schema.get("checker_id") != CHECKER_ID:
        raise ValueError("schema checker identity mismatch")
    if schema.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("schema version mismatch")
    gates = control.get("control_gate_v2r4", {})
    if gates.get("baseline_parent_checker_id") not in (None, CHECKER_ID):
        raise ValueError("control baseline parent mismatch")


def _truthy(case, *keys):
    for key in keys:
        value = case.get(key)
        if value:
            return True
    return False


def _duplicate_committed_effect(case):
    if _truthy(case, "duplicate_committed_effect"):
        return True
    keys = case.get("committed_effect_keys", [])
    if isinstance(keys, list) and len(keys) != len(set(map(str, keys))):
        return True
    counts = case.get("committed_effect_counts", {})
    if isinstance(counts, dict) and any(isinstance(v, int) and v > 1 for v in counts.values()):
        return True
    return False


def _reducible_handoff(case):
    handoff = case.get("handoff", {})
    if not isinstance(handoff, dict) or not handoff.get("requested"):
        return False
    predecessors = case.get("predecessor_states", [])
    if not isinstance(predecessors, list):
        return False
    for predecessor in predecessors:
        if not isinstance(predecessor, dict):
            continue
        if (
            predecessor.get("chat_capable")
            and predecessor.get("safe")
            and predecessor.get("capability_available")
            and not predecessor.get("completed")
        ):
            return True
    return False


def _usefulness_low(case, schema):
    thresholds = schema.get("thresholds", {})
    minimum_ops = thresholds.get("minimum_progress_ops_before_usefulness_gate", 20)
    minimum_rate = thresholds.get("minimum_useful_output_rate", 0.8)
    opportunities = case.get("progress_opportunities", case.get("progress_ops", 0))
    useful = case.get("useful_outputs", case.get("useful_output_count", 0))
    if not isinstance(opportunities, (int, float)) or opportunities < minimum_ops:
        return False
    if not isinstance(useful, (int, float)) or opportunities <= 0:
        return False
    return (useful / opportunities) < minimum_rate


def evaluate(case, schema, control):
    """Evaluate one normalized case with hard-gate-first, order-independent semantics."""
    if not isinstance(case, dict) or not isinstance(schema, dict) or not isinstance(control, dict):
        raise TypeError("case, schema, and control must be mappings")
    _identity_check(schema, control)
    missing = [name for name in _required_fields(schema) if name not in case]
    if missing:
        raise ValueError("missing required case fields: " + ", ".join(sorted(missing)))

    hard_findings = set()
    handoff = case.get("handoff", {}) if isinstance(case.get("handoff", {}), dict) else {}

    if _reducible_handoff(case):
        hard_findings.add("REDUCIBLE_HANDOFF")
    if handoff.get("requested") and not handoff.get("supported_by_evidence", False):
        hard_findings.add("UNSUPPORTED_HANDOFF")
    if _duplicate_committed_effect(case):
        hard_findings.add("DUPLICATE_COMMITTED_EFFECT")
    if _truthy(case, "cas_conflict", "documented_cas_conflict") or case.get("cas_conflicts"):
        hard_findings.add("CAS_CONFLICT")
    if _truthy(case, "protected_authority_violation"):
        hard_findings.add("PROTECTED_AUTHORITY_VIOLATION")

    # ECV2-4 is evaluated only after the other hard gates have been aggregated.
    if not hard_findings and _usefulness_low(case, schema):
        hard_findings.add("LOW_USEFULNESS")

    if hard_findings:
        return {
            "checker_id": CHECKER_ID,
            "decision": "reject_hard",
            "partial": False,
            "hard_findings": sorted(hard_findings),
            "root_acceptance_claimed": False,
        }

    generic_remaining = bool(case.get("generic_remaining_effect_exists"))
    capabilities = case.get("capability_status", {})
    if generic_remaining:
        decision = "supported_generic_boundary"
        partial = True
    elif isinstance(capabilities, dict) and capabilities and all(bool(v) for v in capabilities.values()):
        decision = "clean_cell_pass"
        partial = False
    else:
        decision = "partial_supported"
        partial = True

    return {
        "checker_id": CHECKER_ID,
        "decision": decision,
        "partial": partial,
        "hard_findings": [],
        "root_acceptance_claimed": False,
    }
