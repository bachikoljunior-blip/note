from itertools import combinations


def select_round(n, edges, credit):
    edge_set = {tuple(sorted(e)) for e in edges}
    order = sorted(range(n), key=lambda v: (-credit[v], v))
    selected = []
    for v in order:
        if all(tuple(sorted((v, u))) not in edge_set for u in selected):
            selected.append(v)
    next_credit = [0 if v in selected else credit[v] + 1 for v in range(n)]
    return selected, next_credit


def main():
    graph_cases = 0
    rounds_checked = 0
    worst_first_service = 0
    worst_repeat_gap = 0

    for n in range(1, 7):
        all_edges = list(combinations(range(n), 2))
        for mask in range(1 << len(all_edges)):
            edges = [
                all_edges[i]
                for i in range(len(all_edges))
                if (mask >> i) & 1
            ]
            edge_set = {tuple(sorted(e)) for e in edges}
            degree = [0] * n
            for a, b in edges:
                degree[a] += 1
                degree[b] += 1

            credit = [0] * n
            first_service = [None] * n
            last_service = [None] * n

            # Four n rounds cover multiple recurrence cycles for the finite check.
            for epoch in range(1, 4 * n + 1):
                selected, credit = select_round(n, edges, credit)

                # Per-round safety: selected actions remain an independent set.
                assert all(
                    tuple(sorted((a, b))) not in edge_set
                    for a, b in combinations(selected, 2)
                )

                # Per-round maximality: every unselected vertex conflicts with
                # a selected vertex.
                for v in range(n):
                    if v not in selected:
                        assert any(
                            tuple(sorted((v, u))) in edge_set
                            for u in selected
                        )

                for v in selected:
                    if first_service[v] is None:
                        first_service[v] = epoch
                    else:
                        gap = epoch - last_service[v]
                        worst_repeat_gap = max(worst_repeat_gap, gap)
                        # For a fixed, continuously eligible graph under this
                        # oldest-wait-first rule, a neighbor selected after v's
                        # last service resets below v and cannot block v again
                        # before v is served. The finite model checks the tighter
                        # degree(v)+1 recurrence bound for all n<=6 graphs.
                        assert gap <= degree[v] + 1
                    last_service[v] = epoch

                rounds_checked += 1

            # Starting a fairness epoch with all credits at zero guarantees
            # first service within at most n rounds for a fixed finite cohort.
            assert all(x is not None for x in first_service)
            assert max(first_service) <= n
            worst_first_service = max(worst_first_service, max(first_service))
            graph_cases += 1

    print({
        "fixed_conflict_graphs_n_le_6": graph_cases,
        "selection_rounds_checked": rounds_checked,
        "worst_first_service_round": worst_first_service,
        "worst_repeat_service_gap": worst_repeat_gap,
    })


if __name__ == "__main__":
    main()
