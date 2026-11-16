"""Тесты модуля построения графа."""

from src.graph import DependencyGraph


def _make_fetcher(mapping):
    """Создаёт тестовый fetcher из словаря."""
    def fetcher(node):
        return mapping.get(node, [])
    return fetcher


def test_build_simple_graph():
    """Тест построения простого графа."""
    mapping = {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}
    graph = DependencyGraph()
    graph.build("A", 3, _make_fetcher(mapping))

    assert "A" in graph.nodes
    assert "B" in graph.nodes
    assert "C" in graph.nodes
    assert "D" in graph.nodes


def test_build_respects_depth():
    """Тест ограничения глубины."""
    mapping = {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}
    graph = DependencyGraph()
    graph.build("A", 2, _make_fetcher(mapping))

    assert "A" in graph.nodes
    assert "B" in graph.nodes
    assert "C" in graph.nodes
    assert "D" not in graph.nodes


def test_build_handles_cycle():
    """Тест обработки циклической зависимости."""
    mapping = {"A": ["B"], "B": ["C"], "C": ["A"]}
    graph = DependencyGraph()
    graph.build("A", 5, _make_fetcher(mapping))

    assert graph.nodes == {"A", "B", "C"}
    assert len(graph.edges) == 3


def test_build_no_dependencies():
    """Тест пакета без зависимостей."""
    graph = DependencyGraph()
    graph.build("A", 3, _make_fetcher({}))

    assert graph.nodes == {"A"}
    assert graph.edges == []


def test_to_dict():
    """Тест преобразования в словарь смежности."""
    mapping = {"A": ["B", "C"], "B": [], "C": []}
    graph = DependencyGraph()
    graph.build("A", 3, _make_fetcher(mapping))

    result = graph.to_dict()
    assert "A" in result
    assert set(result["A"]) == {"B", "C"}


def test_depth_one_only_root():
    """Тест глубины 1 — только корень."""
    mapping = {"A": ["B"], "B": []}
    graph = DependencyGraph()
    graph.build("A", 1, _make_fetcher(mapping))

    assert "A" in graph.nodes
    assert ("A", "B") in graph.edges