import networkx as nx
from pyformlang.cfg import CFG
from pyformlang.rsa import RecursiveAutomaton
from pyformlang.finite_automaton import State, NondeterministicFiniteAutomaton
from scipy.sparse import dok_matrix

from project.task2 import graph_to_nfa
from project.task3 import AdjacencyMatrixFA, intersect_automata


def ebnf_to_rsm(ebnf: str) -> RecursiveAutomaton:
    return RecursiveAutomaton.from_text(ebnf)


def cfg_to_rsm(cfg: CFG) -> RecursiveAutomaton:
    return ebnf_to_rsm(cfg.to_text())


def rsm_to_nfa(rsm: RecursiveAutomaton) -> NondeterministicFiniteAutomaton:
    nfa = NondeterministicFiniteAutomaton()

    for rule, box in rsm.boxes.items():
        dfa = box.dfa
        starts_and_finals = dfa.start_states.union(dfa.final_states)

        for state in starts_and_finals:
            new_state = State((rule, state))
            if state in dfa.start_states:
                nfa.add_start_state(new_state)
            if state in dfa.final_states:
                nfa.add_final_state(new_state)

        graph = dfa.to_networkx()
        for src, dest, label in graph.edges(data="label"):
            src_state = State((rule, src))
            dest_state = State((rule, dest))
            nfa.add_transition(src_state, label, dest_state)
    return nfa


def tensor_based_cfpq(
    rsm: RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    graph_m = AdjacencyMatrixFA(
        graph_to_nfa(nx.MultiDiGraph(graph), start_nodes, final_nodes)
    )
    graph_idx_to_state = {idx: state for state, idx in graph_m.nodes_indexes.items()}
    rsm_m = AdjacencyMatrixFA(rsm_to_nfa(rsm))

    for nonterminal in rsm.boxes:
        for adj_m in graph_m, rsm_m:
            if adj_m.boolean_decomposition.get(nonterminal) is None:
                adj_m.boolean_decomposition[nonterminal] = dok_matrix(
                    (adj_m.nodes_num, adj_m.nodes_num), dtype=bool
                )

    nnz = -1
    new_nnz = 0
    while nnz != new_nnz:
        nnz = new_nnz
        intersection = intersect_automata(rsm_m, graph_m)
        idx_to_state = {idx: state for state, idx in intersection.nodes_indexes.items()}

        srcs, dests = intersection.transitive_closure().nonzero()
        for s_idx, d_idx in zip(srcs, dests):
            src_rsm_state, src_graph_node = idx_to_state[s_idx].value
            src_symbol, src_rsm_node = src_rsm_state.value
            dest_rsm_state, dest_graph_node = idx_to_state[d_idx].value
            dest_symbol, dest_rsm_node = dest_rsm_state.value

            if src_symbol != dest_symbol:
                continue

            src_rsm_states = rsm.boxes[src_symbol].dfa.start_states
            dest_rsm_states = rsm.boxes[src_symbol].dfa.final_states

            if src_rsm_node in src_rsm_states and dest_rsm_node in dest_rsm_states:
                graph_m.boolean_decomposition[src_symbol][
                    graph_m.nodes_indexes[src_graph_node],
                    graph_m.nodes_indexes[dest_graph_node],
                ] = True

        new_nnz = 0
        for _, matrix in graph_m.boolean_decomposition.items():
            new_nnz += matrix.count_nonzero()

    res = set()

    for start_state in graph_m.start_nodes:
        for final_state in graph_m.final_nodes:
            if graph_m.boolean_decomposition[rsm.initial_label][
                start_state, final_state
            ]:
                res.add(
                    (
                        graph_idx_to_state[start_state].value,
                        graph_idx_to_state[final_state].value,
                    )
                )

    return res
