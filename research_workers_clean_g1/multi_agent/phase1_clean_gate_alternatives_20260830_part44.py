from itertools import combinations
import json

ROLES = tuple(range(6))
EFFECTS = tuple(range(12))
OWNER = {effect: effect // 2 for effect in EFFECTS}
PAIR_TASKS = [frozenset(pair) for pair in combinations(EFFECTS, 2)]
SAME_OWNER_PAIR_TASKS = [task for task in PAIR_TASKS if len({OWNER[e] for e in task}) == 1]

def overlap_components(tasks):
    adjacency = {task: set() for task in tasks}
    for i, a in enumerate(tasks):
        for b in tasks[i+1:]:
            if a & b:
                adjacency[a].add(b)
                adjacency[b].add(a)
    seen = set(); sizes = []
    for task in tasks:
        if task in seen:
            continue
        stack = [task]; component = set()
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current); component.add(current)
            stack.extend(adjacency[current] - seen)
        sizes.append(len(component))
    return sorted(sizes, reverse=True)

def run():
    single_attempts = len(ROLES) * len(EFFECTS)
    exclusive_admitted = len(EFFECTS)
    exclusive_blocked = single_attempts - exclusive_admitted
    return {
        "single_effect_capability_model": {
            "roles": len(ROLES),
            "effects": len(EFFECTS),
            "role_effect_attempts": single_attempts,
            "strategies": {
                "static_exclusive_owner": {
                    "admitted": exclusive_admitted,
                    "blocked_unauthorized": exclusive_blocked,
                    "duplicate_authoritative_effects": 0,
                    "dynamic_shared_read_required": False,
                },
                "two_owners_per_effect": {
                    "duplicate_authoritative_effect_opportunities": len(EFFECTS),
                    "dynamic_shared_read_required": False,
                },
                "branch_serial_no_semantic_claim": {
                    "serialized_attempts": single_attempts,
                    "duplicate_logical_effect_attempts_after_first_per_effect": exclusive_blocked,
                    "note": "Version serialization alone does not communicate that an equivalent semantic effect already happened."
                },
                "shared_create_once_claim": {
                    "duplicate_authoritative_effects": 0,
                    "mechanically_sufficient": True,
                    "current_clean_write_surface_available": False,
                },
                "durable_sink_idempotency": {
                    "duplicate_authoritative_effects_if_supported": 0,
                    "requires_shared_sink_capability": True,
                    "current_generic_sink_capability_proven": False,
                },
                "time_epoch_owner": {
                    "stale_late_owner_cases": len(EFFECTS),
                    "note": "Clock/turn selection without a current authority fence does not revoke an older invocation."
                },
            },
        },
        "multi_effect_static_partition": {
            "two_effect_tasks": len(PAIR_TASKS),
            "same_owner_tasks": len(SAME_OWNER_PAIR_TASKS),
            "cross_owner_tasks": len(PAIR_TASKS) - len(SAME_OWNER_PAIR_TASKS),
            "all_pair_task_overlap_components": overlap_components(PAIR_TASKS),
            "same_owner_pair_overlap_components": overlap_components(SAME_OWNER_PAIR_TASKS),
            "conclusion": "Static exclusive ownership gives local parallelism only when the allowed task/effect family is already split into disconnected conflict components. For all two-effect pairs over 12 effects, the overlap graph is connected, so an exact one-owner-per-conflict-component policy collapses all 66 pair tasks to one owner."
        },
        "current_clean_surface_audit": {
            "other_role_state_semantic_read": False,
            "shared_dynamic_claim_file_write": False,
            "shared_aggregate_ledger": False,
            "branch_or_ref_claim_namespace_write": False,
            "sanitized_root_static_assignment_read": True,
            "own_role_state_write": True,
            "public_source_read": True,
            "result": "Under current control, static capability partitioning can be represented in sanitized root/config without cross-worker semantic reads, but dynamic create-once/shared-ticket claims are not an admissible deployed surface for this role."
        }
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
