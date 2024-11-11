from itertools import product
from typing import Iterable
from networkx import MultiDiGraph
import numpy as np
import scipy.sparse as sp
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import Symbol
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton

from project.task2 import graph_to_nfa, regex_to_dfa


class AdjacencyMatrixFA:
    def __init__(self, automaton: NondeterministicFiniteAutomaton = None) -> None:
        if automaton is None:
            self.start_nodes = set()
            self.final_nodes = set()
            self.nodes = set()
            self.nodes_indexes = dict()
            self.nodes_num = 0
            self.boolean_decomposition = dict()
            return

        self.nodes = automaton.states
        self.nodes_indexes = {state: idx for idx, state in enumerate(self.nodes)}
        self.start_nodes = {
            self.nodes_indexes[state] for state in automaton.start_states
        }
        self.final_nodes = {
            self.nodes_indexes[state] for state in automaton.final_states
        }

        self.nodes_num = len(self.nodes)
        matrixes = {
            s: np.zeros((self.nodes_num, self.nodes_num), dtype=bool)
            for s in automaton.symbols
        }

        graph = automaton.to_networkx()
        for u, v, label in graph.edges(data="label"):
            if label:
                s = Symbol(label)
                matrixes[s][self.nodes_indexes[u], self.nodes_indexes[v]] = True

        self.boolean_decomposition = {
            s: sp.dok_matrix(m) for (s, m) in matrixes.items()
        }

    def accepts(self, word: Iterable[Symbol]) -> bool:
        curr_states = self.start_nodes.copy()

        for sym in word:
            if sym not in self.boolean_decomposition.keys():
                return False
            curr_states = {
                next_state
                for (curr_state, next_state) in product(
                    curr_states, self.nodes_indexes.values()
                )
                if self.boolean_decomposition[sym][curr_state, next_state]
            }

        if any(state in self.final_nodes for state in curr_states):
            return True

        return False

    def transitive_closure(self):
        if not self.boolean_decomposition:
            return np.eye(self.nodes_num, dtype=np.bool_)
        s = sum(self.boolean_decomposition.values())
        s.setdiag(True)
        return np.linalg.matrix_power(s.toarray(), self.nodes_num)

    def is_empty(self) -> bool:
        t = self.transitive_closure()
        return not any(t[s, f] for s in self.start_nodes for f in self.final_nodes)


def intersect_automata(
    automaton1: AdjacencyMatrixFA, automaton2: AdjacencyMatrixFA
) -> AdjacencyMatrixFA:
    intersection = AdjacencyMatrixFA()
    for n1, n2 in product(automaton1.nodes, automaton2.nodes):
        node = State((n1, n2))
        node_idx = (
            automaton2.nodes_num * automaton1.nodes_indexes[n1]
            + automaton2.nodes_indexes[n2]
        )
        intersection.nodes.add(node)
        intersection.nodes_indexes[node] = node_idx
        if (
            automaton1.nodes_indexes[n1] in automaton1.start_nodes
            and automaton2.nodes_indexes[n2] in automaton2.start_nodes
        ):
            intersection.start_nodes.add(node_idx)
        if (
            automaton1.nodes_indexes[n1] in automaton1.final_nodes
            and automaton2.nodes_indexes[n2] in automaton2.final_nodes
        ):
            intersection.final_nodes.add(node_idx)
    intersection.nodes_num = len(intersection.nodes)
    intersection.boolean_decomposition = {
        label: sp.kron(
            automaton1.boolean_decomposition[label],
            automaton2.boolean_decomposition[label],
            format="dok",
        )
        for label in automaton1.boolean_decomposition.keys()
        if label in automaton2.boolean_decomposition.keys()
    }

    return intersection


def tensor_based_rpq(
    regex: str, graph: MultiDiGraph, start_nodes: set[int], final_nodes: set[int]
) -> set[tuple[int, int]]:
    regex_dfa = regex_to_dfa(regex)
    regex_mfa = AdjacencyMatrixFA(regex_dfa)
    graph_nfa = AdjacencyMatrixFA(graph_to_nfa(graph, start_nodes, final_nodes))
    intersect_fa = intersect_automata(graph_nfa, regex_mfa)
    tc = intersect_fa.transitive_closure()
    pairs = set()
    for start_n in start_nodes:
        for final_n in final_nodes:
            for start_st in regex_dfa.start_states:
                for final_st in regex_dfa.final_states:
                    if tc[
                        intersect_fa.nodes_indexes[(start_n, start_st)],
                        intersect_fa.nodes_indexes[(final_n, final_st)],
                    ]:
                        pairs.add((start_n, final_n))
    return pairs
