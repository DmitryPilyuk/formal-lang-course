from typing import Dict, Set, Tuple
import networkx as nx
from pyformlang.cfg import CFG, Epsilon, Terminal, Production, Variable


def cfg_to_weak_normal_form(cfg: CFG) -> CFG:
    epsil_prod = cfg.get_nullable_symbols()
    cfg = cfg.to_normal_form()
    cfg_prod = list(cfg.productions)

    for symb in epsil_prod:
        cfg_prod.append(Production(head=symb, body=[Epsilon()], filtering=False))

    return CFG(start_symbol=cfg.start_symbol, productions=cfg_prod)


def hellings_based_cfpq(
    cfg: CFG,
    graph: nx.DiGraph,
    start_nodes: Set[int] | None = None,
    final_nodes: Set[int] | None = None,
) -> Set[Tuple[int, int]]:
    if (start_nodes is None) or (start_nodes == set()):
        start_nodes = set(graph.nodes())

    if (final_nodes is None) or (final_nodes == set()):
        final_nodes = set(graph.nodes())
    wcnf = cfg_to_weak_normal_form(cfg)

    nullable: Set[Variable] = set()
    terminal_to_vars: Dict[Terminal, Set[Variable]] = {}
    vars_to_vars: Dict[Tuple[Variable, Variable], Set[Variable]] = {}

    for prod in wcnf.productions:
        head = prod.head
        b = prod.body
        if len(b) == 1:
            if b[0] == Epsilon():
                nullable.add(head)
            else:
                t = terminal_to_vars.get(b[0], set())
                t.add(head)
                terminal_to_vars[b[0]] = t
        elif len(b) == 2:
            t = vars_to_vars.get((b[0], b[1]), set())
            t.add(head)
            vars_to_vars[(b[0], b[1])] = t

    unprocessed = set()

    nodes = graph.nodes()
    edges = graph.edges(data=True)

    for edg in edges:
        d: Dict = edg[2]
        label_val = Terminal(d.get("label"))

        var_set = terminal_to_vars.get(label_val, set())
        for var in var_set:
            unprocessed.add((edg[0], edg[1], var))

    for var in nullable:
        for node in nodes:
            unprocessed.add((node, node, var))

    res = set()
    while unprocessed != set():
        tr1 = unprocessed.pop()
        if tr1 not in res:
            res.add(tr1)

            for tr2 in res:
                if tr1[1] == tr2[0]:
                    vars = vars_to_vars.get((tr1[2], tr2[2]), set())
                    for v in vars:
                        unprocessed.add((tr1[0], tr2[1], v))

                if tr2[1] == tr1[0]:
                    vars = vars_to_vars.get((tr2[2], tr1[2]), set())
                    for v in vars:
                        unprocessed.add((tr2[0], tr1[1], v))

    return {
        (tr[0], tr[1])
        for tr in res
        if tr[2] == wcnf.start_symbol and tr[0] in start_nodes and tr[1] in final_nodes
    }
