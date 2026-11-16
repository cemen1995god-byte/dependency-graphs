"""Модуль топологической сортировки графа зависимостей."""

from typing import Dict, List, Tuple

from src.graph import DependencyGraph


def topological_sort(
    graph: DependencyGraph,
) -> Tuple[List[str], List[str]]:
    """Выполняет топологическую сортировку графа алгоритмом Кана.

    Определяет порядок загрузки: зависимости загружаются раньше.
    Корректно обрабатывает циклические зависимости.

    Args:
        graph: Построенный граф зависимостей.

    Returns:
        Кортеж (порядок_загрузки, пакеты_в_цикле).
    """
    in_degree: Dict[str, int] = {node: 0 for node in graph.nodes}
    adj_list: Dict[str, List[str]] = {node: [] for node in graph.nodes}

    for parent, child in graph.edges:
        if parent in in_degree and child in in_degree:
            in_degree[parent] += 1
            adj_list[child].append(parent)

    queue: List[str] = [
        node for node, degree in in_degree.items() if degree == 0
    ]
    sorted_order: List[str] = []

    while queue:
        current = queue.pop(0)
        sorted_order.append(current)

        for neighbor in adj_list[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    cyclic_nodes = [
        node for node in graph.nodes if node not in sorted_order
    ]

    return sorted_order, cyclic_nodes