from typing import Set
from networkx import MultiDiGraph
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import Symbol
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.regular_expression import Regex


def regex_to_dfa(regex: str) -> DeterministicFiniteAutomaton:
    dfa = Regex(regex).to_epsilon_nfa().to_deterministic()
    return dfa.minimize()


def graph_to_nfa(
    graph: MultiDiGraph, start_states: Set[int], final_states: Set[int]
) -> NondeterministicFiniteAutomaton:
    all_nodes = {State(n) for n in graph.nodes}
    nfa = NondeterministicFiniteAutomaton(
        states=all_nodes,
        start_state={State(s) for s in start_states} if start_states else all_nodes,
        final_states={State(s) for s in final_states} if final_states else all_nodes,
    )
    for u, v, data in graph.edges(data=True):
        nfa.add_transition(State(u), Symbol(data["label"]), State(v))

    return nfa
