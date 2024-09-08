import pytest
from project.task1 import get_graph_info, GraphInfo


def test_graph_info():
    actual_graph = get_graph_info("generations")
    expected = GraphInfo(129, 273, ['type', 'first', 'rest', 'onProperty', 'intersectionOf', 'equivalentClass', 'someValuesFrom',
                         'hasValue', 'hasSex', 'hasChild', 'hasParent', 'inverseOf', 'sameAs', 'hasSibling', 'oneOf', 'range', 'versionInfo'])
    assert actual_graph == expected


def test_graph_info_fail():
    with pytest.raises(Exception):
        get_graph_info("None")
