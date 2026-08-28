from collections import defaultdict


NODES = {
    "FROZEN_CONFIG",
    "IMMUTABLE_READ",
    "OWNER_SNAPSHOT",
    "PROVENANCE",
    "RECONSTRUCT",
    "FAIRNESS_META",
    "CANONICAL_ACTIONS",
    "CONFLICT_GRAPH",
    "FAIR_SELECT",
    "DIRECT_FIRST",
    "TRANSVERSAL",
    "CHECKPOINT_BUILD",
    "CHECKPOINT_VERIFY",
    "POINTER_CAS",
    "POINTER_POSTREAD",
    "RECEIPT",
    "HANDOFF_OFFER",
    "HANDOFF_CAS",
    "FENCED_EFFECT",
}

BASE_DEPS = {
    "FROZEN_CONFIG": set(),
    "IMMUTABLE_READ": set(),
    # OWNER_SNAPSHOT is an independently authoritative external primitive.
    "OWNER_SNAPSHOT": set(),
    "PROVENANCE": {"FROZEN_CONFIG", "IMMUTABLE_READ"},
    "RECONSTRUCT": {"PROVENANCE"},
    "FAIRNESS_META": {"RECONSTRUCT"},
    "CANONICAL_ACTIONS": {"RECONSTRUCT", "OWNER_SNAPSHOT"},
    "CONFLICT_GRAPH": {"CANONICAL_ACTIONS"},
    "FAIR_SELECT": {"CONFLICT_GRAPH", "FAIRNESS_META"},
    "DIRECT_FIRST": {"FAIR_SELECT"},
    "TRANSVERSAL": {"DIRECT_FIRST"},
    "CHECKPOINT_BUILD": {"DIRECT_FIRST", "TRANSVERSAL", "RECONSTRUCT"},
    "CHECKPOINT_VERIFY": {"CHECKPOINT_BUILD", "IMMUTABLE_READ"},
    "POINTER_CAS": {"CHECKPOINT_VERIFY"},
    "POINTER_POSTREAD": {"POINTER_CAS"},
    "RECEIPT": {"CHECKPOINT_VERIFY", "POINTER_POSTREAD"},
    "HANDOFF_OFFER": {"CHECKPOINT_VERIFY", "FAIR_SELECT"},
    "HANDOFF_CAS": {"HANDOFF_OFFER", "OWNER_SNAPSHOT"},
    "FENCED_EFFECT": {"HANDOFF_CAS"},
}


def topo(deps):
    outgoing = defaultdict(set)
    indegree = {n: 0 for n in NODES}
    for node in NODES:
        for dependency in deps.get(node, set()):
            outgoing[dependency].add(node)
            indegree[node] += 1

    ready = sorted(n for n, d in indegree.items() if d == 0)
    order = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for target in sorted(outgoing[node]):
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
                ready.sort()
    return order


def with_extra_dependency(target, dependency):
    deps = {k: set(v) for k, v in BASE_DEPS.items()}
    deps[target].add(dependency)
    return deps


def main():
    order = topo(BASE_DEPS)
    assert len(order) == len(NODES)

    # These tempting authority shortcuts are intentionally cyclic:
    # 1. semantic reconstruction may not depend on its own terminal receipt;
    # 2. semantic reconstruction may not depend on the pointer postread produced
    #    after publishing the checkpoint derived from that reconstruction;
    # 3. action eligibility may not infer current ownership from a handoff CAS
    #    that itself occurs only after selection/publication.
    forbidden = {
        "receipt_as_reconstruction_authority": ("RECONSTRUCT", "RECEIPT"),
        "post_publish_pointer_as_reconstruction_authority": (
            "RECONSTRUCT",
            "POINTER_POSTREAD",
        ),
        "handoff_result_as_preselection_owner_authority": (
            "CANONICAL_ACTIONS",
            "HANDOFF_CAS",
        ),
    }

    rejected = {}
    for name, (target, dependency) in forbidden.items():
        bad_order = topo(with_extra_dependency(target, dependency))
        rejected[name] = len(bad_order) < len(NODES)
        assert rejected[name]

    print({
        "base_node_count": len(NODES),
        "base_topological_order": order,
        "base_acyclic": True,
        "forbidden_authority_cycles_rejected": rejected,
    })


if __name__ == "__main__":
    main()
