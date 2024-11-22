from typing import Set
import networkx as nx
from pyformlang.cfg import CFG, Variable, Epsilon
from scipy.sparse import lil_matrix

from project.task6 import cfg_to_weak_normal_form


def matrix_based_cfpq(
    cfg: CFG,
    graph: nx.DiGraph,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
) -> set[tuple[int, int]]:
    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes

    wcnf = cfg_to_weak_normal_form(cfg)

    eps_prods = [
        production.head.value
        for production in wcnf.productions
        if production.body[0] == Epsilon()
    ]
    term_prods = {
        production for production in wcnf.productions if len(production.body) == 1
    }
    var_prods = {
        production for production in wcnf.productions if len(production.body) == 2
    }
    node_to_idx = {n: i for i, n in enumerate(graph.nodes)}
    idx_to_node = {i: n for n, i in node_to_idx.items()}
    num_nodes = graph.number_of_nodes()
    adjacency_matrix: dict[Variable, lil_matrix] = {
        noterm: lil_matrix((num_nodes, num_nodes), dtype=bool)
        for noterm in wcnf.variables
    }

    for eps in eps_prods:
        for n in range(num_nodes):
            adjacency_matrix[eps][n, n] = True

    for i, j, data in graph.edges(data=True):
        label = data["label"]
        for v in {prod.head for prod in term_prods if prod.body[0].value == label}:
            adjacency_matrix[v][node_to_idx[i], node_to_idx[j]] = True

    was_changed = True
    while was_changed:
        was_changed = False
        for prod in var_prods:
            old = adjacency_matrix[prod.head.value].nnz
            adjacency_matrix[prod.head.value] += (
                adjacency_matrix[prod.body[0].value]
                @ adjacency_matrix[prod.body[1].value]
            )
            new = adjacency_matrix[prod.head.value].nnz
            was_changed = was_changed or (old != new)

    result = set()
    for nonterm in adjacency_matrix:
        if nonterm.value == cfg.start_symbol.value:
            for u_idx, v_idx in zip(*adjacency_matrix[nonterm].nonzero()):
                u = idx_to_node[u_idx]
                v = idx_to_node[v_idx]
                if u in start_nodes and v in final_nodes:
                    result.add((u, v))
    return result
