"""Модуль построения графа зависимостей через DFS."""

from typing import Callable, Dict, List, Set, Tuple

DependencyFetcher = Callable[[str], List[str]]
Edge = Tuple[str, str]
NodeDepth = Tuple[str, int]

ROOT_DEPTH = 0
MIN_DEPTH = 1


class DependencyGraph:
    """Граф зависимостей пакетов.

    Атрибуты:
        edges: Список рёбер (родитель, потомок).
        nodes: Множество всех посещённых узлов.
    """

    def __init__(self) -> None:
        """Инициализирует пустой граф."""
        self.edges: List[Edge] = []
        self.nodes: Set[str] = set()

    def _process_node(
        self, node: str, depth: int, fetcher: DependencyFetcher
    ) -> List[NodeDepth]:
        """Обрабатывает один узел и возвращает детей.

        Args:
            node: Имя пакета.
            depth: Текущая глубина.
            fetcher: Функция получения зависимостей.

        Returns:
            Список пар (потомок, новая глубина).
        """
        if depth < MIN_DEPTH:
            return []

        dependencies = fetcher(node)
        next_nodes: List[NodeDepth] = []
        for dep in dependencies:
            self.edges.append((node, dep))
            if dep not in self.nodes:
                next_nodes.append((dep, depth - 1))

        return next_nodes

    def build(
        self,
        root: str,
        max_depth: int,
        fetcher: DependencyFetcher,
    ) -> None:
        """Строит граф от корня алгоритмом DFS.

        Использует явный стек вместо рекурсии.
        Циклические зависимости обрабатываются через
        множество посещённых узлов.

        Args:
            root: Стартовый пакет.
            max_depth: Максимальная глубина анализа.
            fetcher: Функция получения зависимостей.
        """
        stack: List[NodeDepth] = [(root, max_depth)]

        while stack:
            node, depth = stack.pop()
            if node in self.nodes:
                continue
            self.nodes.add(node)

            children = self._process_node(node, depth, fetcher)
            stack.extend(children)

    def to_dict(self) -> Dict[str, List[str]]:
        """Возвращает граф в виде словаря смежности.

        Returns:
            Словарь: пакет -> список его зависимостей.
        """
        result: Dict[str, List[str]] = {}
        for parent, child in self.edges:
            result.setdefault(parent, []).append(child)
        return result