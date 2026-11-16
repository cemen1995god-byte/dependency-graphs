"""Тесты модуля тестового репозитория."""

import os
import tempfile
import pytest

from src.test_repository import (
    load_test_graph,
    create_test_fetcher,
    parse_line,
)


def _write_temp_graph(content: str) -> str:
    """Создаёт временный файл с описанием графа."""
    file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    file.write(content)
    file.close()
    return file.name


def test_parse_line_valid():
    """Тест разбора корректной строки."""
    package, deps = parse_line("A B C")
    assert package == "A"
    assert deps == ["B", "C"]


def test_parse_line_no_deps():
    """Тест разбора пакета без зависимостей."""
    package, deps = parse_line("A")
    assert package == "A"
    assert deps == []


def test_parse_line_comment():
    """Тест разбора комментария."""
    package, deps = parse_line("# comment")
    assert package is None
    assert deps is None


def test_parse_line_empty():
    """Тест разбора пустой строки."""
    package, deps = parse_line("   ")
    assert package is None


def test_load_test_graph():
    """Тест загрузки графа из файла."""
    path = _write_temp_graph("A B C\nB D\n")
    try:
        graph = load_test_graph(path)
        assert graph["A"] == ["B", "C"]
        assert graph["B"] == ["D"]
    finally:
        os.unlink(path)


def test_load_missing_file():
    """Тест загрузки несуществующего файла."""
    with pytest.raises(FileNotFoundError):
        load_test_graph("/nonexistent/path.txt")


def test_create_fetcher_returns_deps():
    """Тест создания fetcher с зависимостями."""
    graph = {"A": ["B", "C"]}
    fetcher = create_test_fetcher(graph)
    assert fetcher("A") == ["B", "C"]


def test_create_fetcher_missing_package():
    """Тест fetcher для несуществующего пакета."""
    graph = {"A": ["B"]}
    fetcher = create_test_fetcher(graph)
    assert fetcher("ZZZ") == []