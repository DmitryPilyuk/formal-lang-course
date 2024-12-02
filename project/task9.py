from dataclasses import dataclass
from typing import Any, Iterable
import networkx as nx
from pyformlang.rsa import RecursiveAutomaton
from pyformlang.finite_automaton import Symbol
from pyformlang.finite_automaton import State


@dataclass(frozen=True)
class RsmState:
    nonterm: Symbol
    state: State


def get_rsm_edges(
    rsm: RecursiveAutomaton, from_st: RsmState
) -> dict[Symbol, set[RsmState]]:
    nonterm = from_st.nonterm
    edges = {}
    if rsm.get_box(nonterm) is None:
        return {}

    nonterm_edges = rsm.get_box(nonterm).dfa.to_dict()
    if from_st.state in nonterm_edges.keys():
        for lbl, to_st in nonterm_edges[from_st.state].items():
            if not isinstance(to_st, Iterable):
                edges.setdefault(lbl, set()).add(RsmState(nonterm, to_st))
                continue

            for to_state in to_st:
                edges.setdefault(lbl, set()).add(RsmState(nonterm, to_state))

    return edges


def get_graph_edges(g: nx.MultiDiGraph, from_nd: Any) -> dict[Any, set[Any]]:
    edges = {}
    for _, to_nd, label in g.edges(from_nd, data="label"):
        edges.setdefault(label, set()).add(to_nd)
    return edges


@dataclass(frozen=True)
class GssNode:
    rsm_st: RsmState
    graph_node: int


@dataclass(frozen=True)
class Config:
    rsm_st: RsmState
    graph_node: int
    gss_node: GssNode


def process(
    cfg: Config,
    gss: nx.MultiDiGraph,
    graph: nx.DiGraph,
    rsm: RecursiveAutomaton,
    res: set[tuple[int, int]],
    init_gss_node: GssNode,
) -> set[Config]:
    new_configs = set()
    graph_edges: dict[any, set[any]] = get_graph_edges(
        nx.MultiDiGraph(graph), cfg.graph_node
    )
    rsm_edges: dict[Symbol, set[RsmState]] = get_rsm_edges(rsm, cfg.rsm_st)

    labels = set(graph_edges.keys()) & set(rsm_edges.keys())
    for lbl in labels:
        for rsm_st in rsm_edges[lbl]:
            for graph_node in graph_edges[lbl]:
                new_configs.add(Config(rsm_st, graph_node, cfg.gss_node))

    for rsm_lbl in rsm_edges.keys():
        if rsm_lbl in rsm.labels:
            for rsm_start_st in rsm.get_box(rsm_lbl).start_state:
                new_rsm_st = RsmState(rsm_lbl, rsm_start_st)
                new_gss_node = GssNode(new_rsm_st, cfg.graph_node)

                if new_gss_node in gss.nodes and gss.nodes[new_gss_node]["pop_set"]:
                    for graph_node in gss.nodes[new_gss_node]["pop_set"]:
                        for rsm_st in rsm_edges[rsm_lbl]:
                            gss.add_edge(new_gss_node, cfg.gss_node, label=rsm_st)
                            new_configs.add(Config(rsm_st, graph_node, cfg.gss_node))
                    continue

                for rsm_st in rsm_edges[rsm_lbl]:
                    gss.add_node(new_gss_node, pop_set=None)
                    gss.add_edge(new_gss_node, cfg.gss_node, label=rsm_st)

                new_configs.add(Config(new_rsm_st, cfg.graph_node, new_gss_node))

    if cfg.rsm_st.state in rsm.get_box(cfg.rsm_st.nonterm).final_states:
        if gss.nodes[cfg.gss_node]["pop_set"] is None:
            gss.nodes[cfg.gss_node]["pop_set"] = set()
        gss.nodes[cfg.gss_node]["pop_set"].add(cfg.graph_node)

        gss_edges: dict[RsmState, set[GssNode]] = get_graph_edges(gss, cfg.gss_node)
        for lbl in gss_edges.keys():
            for gss_node in gss_edges[lbl]:
                if gss_node == init_gss_node:
                    res.add((cfg.gss_node.graph_node, cfg.graph_node))
                    continue
                new_configs.add(Config(lbl, cfg.graph_node, gss_node))

    return new_configs


def gll_based_cfpq(
    rsm: RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    states = set(n for n in graph.nodes)
    start_nodes = set(n for n in start_nodes) if start_nodes else states
    final_nodes = set(n for n in final_nodes) if final_nodes else states

    waiting_configs: set[Config] = set()
    processed_configs: set[Config] = set()
    gss = nx.MultiDiGraph()
    init_gss_node = GssNode(RsmState(Symbol("$"), State(0)), -1)
    res = set()

    for rsm_start in rsm.get_box(rsm.initial_label).start_state:
        for graph_st in start_nodes:
            rsm_st = RsmState(rsm.initial_label, rsm_start)
            gss_v = GssNode(rsm_st, graph_st)

            gss.add_node(gss_v, pop_set=None)
            gss.add_edge(gss_v, init_gss_node, label=rsm_st)
            config = Config(rsm_st, graph_st, gss_v)
            waiting_configs.add(config)

    while waiting_configs:
        config = waiting_configs.pop()
        if config in processed_configs:
            continue

        processed_configs.add(config)
        waiting_configs |= process(config, gss, graph, rsm, res, init_gss_node)

    return {
        (start_st, final_st)
        for start_st, final_st in res
        if start_st in start_nodes and final_st in final_nodes
    }
