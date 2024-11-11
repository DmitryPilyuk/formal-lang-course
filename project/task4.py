from functools import reduce
from itertools import product
from networkx import MultiDiGraph
from scipy.sparse import dok_matrix, vstack

from project.task2 import graph_to_nfa, regex_to_dfa
from project.task3 import AdjacencyMatrixFA


def init_front(mdfa: AdjacencyMatrixFA, mnfa: AdjacencyMatrixFA):
    start_states = list(product(mdfa.start_nodes, mnfa.start_nodes))
    m = mdfa.nodes_num
    n = mnfa.nodes_num
    matices = []
    for dfa_idx, nfa_idx in start_states:
        matrix = dok_matrix((m, n), dtype=bool)
        matrix[dfa_idx, nfa_idx] = True
        matices.append(matrix)
    return vstack(matices, "dok", dtype=bool)


def ms_bfs_based_rpq(
    regex: str, graph: MultiDiGraph, start_nodes: set[int], final_nodes: set[int]
) -> set[tuple[int, int]]:
    regex_dfa = regex_to_dfa(regex)
    grapth_nfa = graph_to_nfa(graph, start_nodes, final_nodes)

    mdfa = AdjacencyMatrixFA(regex_dfa)
    mnfa = AdjacencyMatrixFA(grapth_nfa)

    index_to_state_nfa = {index: state for state, index in mnfa.nodes_indexes.items()}
    alphabet = mdfa.boolean_decomposition.keys() & mnfa.boolean_decomposition.keys()

    permutation_m = {
        sym: mdfa.boolean_decomposition[sym].transpose() for sym in alphabet
    }

    front = init_front(mdfa, mnfa)
    visited = front

    m = mdfa.nodes_num
    start_states = list(product(mdfa.start_nodes, mnfa.start_nodes))
    while front.count_nonzero() > 0:
        new_front = []
        for sym in alphabet:
            sym_front = front @ mnfa.boolean_decomposition[sym]
            new_front.append(
                vstack(
                    [
                        permutation_m[sym] @ sym_front[m * i : m * (i + 1)]
                        for i in range(len(start_states))
                    ]
                )
            )

        front = reduce(lambda x, y: x + y, new_front, front) > visited
        visited += front

    answer = set()
    for i, (_, nfa_start_state) in enumerate(start_states):
        fix_start = visited[m * i : m * (i + 1)]
        row, col = fix_start.nonzero()
        for dfa_state, nfa_state in zip(row, col):
            if dfa_state in mdfa.final_nodes and nfa_state in mnfa.final_nodes:
                answer.add(
                    (
                        index_to_state_nfa[nfa_start_state].value,
                        index_to_state_nfa[nfa_state].value,
                    )
                )
    return answer
