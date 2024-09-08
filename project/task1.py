from dataclasses import dataclass
from typing import Any
import cfpq_data
import networkx


@dataclass
class GraphInfo:
    nodes: int
    edges: int
    labels: list[Any]


def get_graph_info(name):
    path = cfpq_data.download(name)
    graph = cfpq_data.graph_from_csv(path)
    return GraphInfo(graph.number_of_nodes(), graph.number_of_edges(), cfpq_data.get_sorted_labels(graph))


def save_to_pydot_labeled_two_cycles_graph(n, m, labels, path):
    graph = cfpq_data.labeled_two_cycles_graph(n, m, labels)
    pydot_graph = networkx.drawing.nx_pydot.to_pydot(graph)
    f = open(path, "w")
    f.write(pydot_graph.to_string().replace("\n", ""))
    f.close()
