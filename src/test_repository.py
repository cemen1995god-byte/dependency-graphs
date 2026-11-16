"""Модуль тестового репозитория с графом из файла."""

import os
from typing import Callable, Dict, List

COMMENT_PREFIX = "#"
FIELD_SEPARATOR = " "
ROOT_PACKAGE_INDEX = 0

TestGraph = Dict[str, List[str]]
DependencyFetcher = Callable[[str], List[str]]


def parse_line(line: str) -> tuple:
    """Разбирает одну строку описания графа.

    Формат: 'A B C' означает, что пакет A зависит от B и C.
    Одиночный токен означает пакет без зависимостей.

    Args:
        line: Строка из файла.

    Returns:
        Кортеж (пакет, список зависимостей) или None.
    """
    stripped = line.strip()
    if not stripped or stripped.startswith(COMMENT_PREFIX):
        return None, None

    parts = stripped.split(FIELD_SEPARATOR)
    package = parts[ROOT_PACKAGE_INDEX]
    dependencies = parts[1:]
    return package, dependencies


def load_test_graph(path: str) -> TestGraph:
    """Загружает граф тестового репозитория из файла.

    Args:
        path: Путь к файлу описания графа.

    Returns:
        Словарь: пакет -> список его зависимостей.

    Raises:
        FileNotFoundError: Если файл не найден.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Файл тестового графа не найден: {path}"
        )

    graph: TestGraph = {}
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            package, dependencies = parse_line(line)
            if package is not None:
                graph[package] = dependencies

    return graph


def create_test_fetcher(graph: TestGraph) -> DependencyFetcher:
    """Создаёт функцию-получатель зависимостей из графа.

    Args:
        graph: Словарь с описанием графа.

    Returns:
        Функция, возвращающая список зависимостей пакета.
    """
    def fetcher(package: str) -> List[str]:
        """Возвращает зависимости пакета из тестового графа.

        Args:
            package: Имя пакета.

        Returns:
            Список зависимостей (пустой, если пакета нет).
        """
        return graph.get(package, [])

    return fetcher