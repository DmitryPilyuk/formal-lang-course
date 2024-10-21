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
    pass
