from dataclasses import dataclass
from typing import Any
import cfpq_data


@dataclass
class GraphInfo:
    nodes: int
    edges: int
    labels: list[Any]

def get_graph_info(name):
    path = cfpq_data.download(name)
    graph = cfpq_data.graph_from_csv(path)
    return GraphInfo(graph.number_of_nodes(), graph.number_of_edges(), cfpq_data.get_sorted_labels(graph))
