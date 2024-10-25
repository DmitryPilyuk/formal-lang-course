import networkx as nx
from pyformlang.cfg import CFG


def cfg_to_weak_normal_form(cfg: CFG) -> CFG:
    _cfg = cfg.eliminate_unit_productions().remove_useless_symbols()
    new_productions = set(
        _cfg._decompose_productions(_cfg._get_productions_with_only_single_terminals())
    )
    return CFG(start_symbol=_cfg.start_symbol, productions=new_productions)


def hellings_based_cfpq(
    cfg: CFG,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    wcnf = cfg_to_weak_normal_form(cfg)

    nullable = wcnf.get_nullable_symbols()
    p_terms = {prod for prod in wcnf.productions if len(prod.body) == 1}
    p_vars = {prod for prod in wcnf.productions if len(prod.body) == 2}

    r = {(node, var, node) for node in graph.nodes for var in nullable} | {
        (u, prod.head, v)
        for (u, v, data) in graph.edges(data=True)
        for prod in p_terms
        if prod.body[0].value == data.get("label")
    }

    new = r.copy()

    while new:
        (n, N, m) = new.pop()
        good = {
            (u, prod.head, m)
            for (u, M, v) in r
            for prod in p_vars
            if v == n
            and prod.body[0].value == M
            and prod.body[1].value == N
            and (u, prod.head, m) not in r
        }
        new |= good
        r |= good

        good = {
            (n, prod.head, v)
            for (u, M, v) in r
            for prod in p_vars
            if m == u
            and prod.body[0].value == N
            and prod.body[1].value == M
            and (n, prod.head, v) not in r
        }
        new |= good
        r |= good

    return {
        (u, v)
        for (u, var, v) in r
        if (not start_nodes or u in start_nodes)
        and (not final_nodes or v in final_nodes)
        and var == wcnf.start_symbol.value
    }
