from dataclasses import dataclass
from itertools import product, permutations

@dataclass(frozen=True)
class Node:
    nid: str
    parent: str
    policy: int
    write: tuple | None

def valid_nodes(nodes):
    valid = {"r"}
    changed = True
    while changed:
        changed = False
        for node in nodes:
            if node.nid not in valid and node.parent in valid:
                valid.add(node.nid)
                changed = True
    return valid

def ancestors(nid, by):
    out = []
    cur = nid
    seen = set()
    while cur != "r":
        if cur in seen or cur not in by:
            break
        seen.add(cur)
        out.append(cur)
        cur = by[cur].parent
    out.append("r")
    return out

def path_to_root(nid, by):
    path = []
    cur = nid
    while cur != "r":
        node = by[cur]
        path.append(node)
        cur = node.parent
    return list(reversed(path))

def materialize(nid, by):
    state = {}
    for node in path_to_root(nid, by):
        if node.write is not None:
            state[node.write[0]] = node.write[1]
    return state

def reconstruct(nodes, pointer, migration=False, timestamp_order=None):
    by = {node.nid: node for node in nodes}
    valid = valid_nodes(nodes)

    if pointer not in (None, "r") and pointer not in valid:
        return ("INVALID_POINTER_PROVENANCE", pointer)

    valid_ids = sorted(v for v in valid if v != "r")
    heads = []
    for candidate in valid_ids:
        if not any(
            candidate != other and candidate in ancestors(other, by)[1:]
            for other in valid_ids
        ):
            heads.append(candidate)

    if not heads:
        return ("RESOLVED", (), (), "empty")

    policies = {by[h].policy for h in heads}
    if len(policies) > 1 and not migration:
        return ("AMBIGUOUS_POLICY", tuple(heads))

    merged = {}
    for head in sorted(heads):
        state = materialize(head, by)
        for key, value in state.items():
            if key in merged and merged[key] != value:
                return (
                    "AMBIGUOUS_OVERLAP",
                    key,
                    merged[key],
                    value,
                    tuple(heads),
                )
            merged[key] = value

    return (
        "RESOLVED",
        tuple(sorted(merged.items())),
        tuple(heads),
        "migrated" if len(policies) > 1 else "same_policy",
    )

def main():
    parents1 = ["r", "missing"]
    parents2 = ["r", "n1", "missing"]
    parents3 = ["r", "n1", "n2", "missing"]
    writes = [None, ("a", 0), ("a", 1), ("b", 0), ("b", 1)]

    dag_cases = 0
    valid_pointer_comparisons = 0

    for p1, p2, p3 in product(parents1, parents2, parents3):
        for w1, w2, w3 in product(writes, repeat=3):
            for policy1, policy2, policy3 in product([1, 2], repeat=3):
                nodes = [
                    Node("n1", p1, policy1, w1),
                    Node("n2", p2, policy2, w2),
                    Node("n3", p3, policy3, w3),
                ]
                valid = valid_nodes(nodes)
                baseline = reconstruct(nodes, None, False)
                baseline_migrated = reconstruct(nodes, None, True)

                for order in permutations(["n1", "n2", "n3"]):
                    assert reconstruct(nodes, None, False, order) == baseline
                    assert reconstruct(nodes, None, True, order) == baseline_migrated

                for pointer in ["r", "n1", "n2", "n3"]:
                    if pointer == "r" or pointer in valid:
                        assert reconstruct(nodes, pointer, False) == baseline
                        assert reconstruct(nodes, pointer, True) == baseline_migrated
                        valid_pointer_comparisons += 2

                assert reconstruct(nodes, "missing", False)[0] == "INVALID_POINTER_PROVENANCE"
                dag_cases += 1

    print({
        "causal_dag_cases": dag_cases,
        "valid_pointer_semantic_equivalence_checks": valid_pointer_comparisons,
    })

if __name__ == "__main__":
    main()
