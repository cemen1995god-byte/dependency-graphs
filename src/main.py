"""Точка входа в визуализатор графа зависимостей."""

import sys
from typing import List

from src.collector import collect_direct_dependencies
from src.config import load_config, print_config, validate_config
from src.errors import ConfigError, RepositoryError
from src.graph import DependencyGraph
from src.sorter import topological_sort
from src.test_repository import create_test_fetcher, load_test_graph


def get_config_path(args: List[str]) -> str:
    """Определяет путь к файлу конфигурации."""
    if len(args) < 2:
        raise ConfigError(
            "Использование: python -m src.main <путь к config.json>"
        )
    return args[1]


def build_real_graph(config: dict) -> DependencyGraph:
    """Строит граф зависимостей из реального Maven."""
    def fetcher(package: str) -> List[str]:
        deps = collect_direct_dependencies(
            config["repository_url"], package
        )
        return [f"{d['groupId']}:{d['artifactId']}" for d in deps]

    graph = DependencyGraph()
    graph.build(config["package_name"], config["max_depth"], fetcher)
    return graph


def build_test_graph(config: dict) -> DependencyGraph:
    """Строит граф из тестового описания."""
    test_graph = load_test_graph(config["test_file_path"])
    fetcher = create_test_fetcher(test_graph)

    graph = DependencyGraph()
    graph.build(config["package_name"], config["max_depth"], fetcher)
    return graph


def print_graph(graph: DependencyGraph) -> None:
    """Выводит граф зависимостей на экран."""
    print("\n=== Граф зависимостей ===")
    if not graph.edges:
        print("Зависимости не найдены")
        return

    adjacency: dict = {}
    for parent, child in graph.edges:
        adjacency.setdefault(parent, []).append(child)

    for parent in sorted(adjacency.keys()):
        children = ", ".join(adjacency[parent])
        print(f"{parent} -> {children}")

    print(f"\nВсего узлов: {len(graph.nodes)}")
    print(f"Всего рёбер: {len(graph.edges)}")


def print_load_order(graph: DependencyGraph) -> None:
    """Выводит порядок загрузки пакетов."""
    print("\n=== Порядок загрузки ===")
    sorted_order, cyclic_nodes = topological_sort(graph)

    if sorted_order:
        print("Корректный порядок:")
        for i, pkg in enumerate(sorted_order, 1):
            print(f"{i}. {pkg}")

    if cyclic_nodes:
        print("\n⚠️ Обнаружены циклические зависимости:")
        for pkg in sorted(cyclic_nodes):
            print(f"  - {pkg}")
        print("Эти пакеты не могут быть корректно упорядочены.")


def main() -> None:
    """Запускает визуализатор графа зависимостей."""
    try:
        config_path = get_config_path(sys.argv)
        raw_config = load_config(config_path)
        config = validate_config(raw_config)
        print_config(config)

        if config["test_mode"]:
            graph = build_test_graph(config)
        else:
            graph = build_real_graph(config)

        print_graph(graph)
        print_load_order(graph)

    except FileNotFoundError as error:
        print(f"Ошибка: {error}")
        sys.exit(1)
    except ConfigError as error:
        print(f"Ошибка конфигурации: {error.message}")
        sys.exit(1)
    except RepositoryError as error:
        print(f"Ошибка репозитория: {error.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()