from itertools import combinations


def select_round(n, edge_mask, credit):
    all_edges = list(combinations(range(n), 2))
    edge_set = {
        all_edges[i]
        for i in range(len(all_edges))
        if (edge_mask >> i) & 1
    }
    order = sorted(range(n), key=lambda v: (-credit[v], v))
    selected = []
    for v in order:
        if all(tuple(sorted((v, u))) not in edge_set for u in selected):
            selected.append(v)
    next_credit = tuple(0 if v in selected else credit[v] + 1 for v in range(n))
    return tuple(selected), next_credit


def main():
    summary = {}
    total_transitions = 0

    # Exhaustively explore every possible conflict graph at every selection epoch.
    # State merging keeps the search finite: states are (credits, ever_served).
    for n in range(1, 6):
        edge_count = n * (n - 1) // 2
        states = {(tuple([0] * n), tuple([False] * n))}
        epoch_sizes = []
        transitions = 0

        for epoch in range(1, n + 1):
            next_states = set()
            for credit, served in states:
                for edge_mask in range(1 << edge_count):
                    selected, next_credit = select_round(n, edge_mask, credit)
                    next_served = list(served)
                    for v in selected:
                        next_served[v] = True
                    next_states.add((next_credit, tuple(next_served)))
                    transitions += 1
            states = next_states
            epoch_sizes.append(len(states))

        assert all(all(served) for _, served in states)
        summary[n] = {
            "reachable_states_by_epoch": epoch_sizes,
            "transition_evaluations": transitions,
        }
        total_transitions += transitions

    print({
        "n_1_through_5": summary,
        "total_transition_evaluations": total_transitions,
        "property": "all continuously eligible fixed-cohort actions first-served by epoch n under arbitrary per-epoch conflict edges",
    })


if __name__ == "__main__":
    main()
