"""Тесты модуля топологической сортировки."""

from src.graph import DependencyGraph
from src.sorter import topological_sort


def _make_graph(edges, nodes):
    """Создаёт тестовый граф из списков."""
    graph = DependencyGraph()
    graph.edges = edges
    graph.nodes = set(nodes)
    return graph


def test_topological_sort_simple():
    """Тест сортировки простого графа."""
    # A зависит от B, B зависит от C. Порядок: C, B, A
    edges = [("A", "B"), ("B", "C")]
    nodes = ["A", "B", "C"]
    graph = _make_graph(edges, nodes)

    order, cycles = topological_sort(graph)

    assert cycles == []
    assert order.index("C") < order.index("B")
    assert order.index("B") < order.index("A")


def test_topological_sort_with_cycle():
    """Тест сортировки графа с циклом."""
    # A -> B -> C -> A
    edges = [("A", "B"), ("B", "C"), ("C", "A")]
    nodes = ["A", "B", "C"]
    graph = _make_graph(edges, nodes)

    order, cycles = topological_sort(graph)

    assert len(order) == 0
    assert set(cycles) == {"A", "B", "C"}


def test_topological_sort_partial_cycle():
    """Тест сортировки, где цикл затрагивает не все узлы."""
    # A и D независимы, B -> C -> B (цикл между B и C)
    edges = [("B", "C"), ("C", "B")]
    nodes = ["A", "B", "C", "D"]
    graph = _make_graph(edges, nodes)

    order, cycles = topological_sort(graph)

    assert "A" in order
    assert "D" in order
    assert set(cycles) == {"B", "C"}


def test_topological_sort_no_edges():
    """Тест графа без рёбер."""
    graph = _make_graph([], ["A", "B"])
    order, cycles = topological_sort(graph)

    assert cycles == []
    assert set(order) == {"A", "B"}