"""Модуль загрузки и валидации конфигурации."""

import json
import os
from typing import Dict, Any

from src.errors import (
    ConfigError,
    PackageNotFoundError,
    RepositoryError,
    DepthError,
)

DEFAULT_REPOSITORY_URL = "https://repo1.maven.org/maven2"
DEFAULT_OUTPUT_FILE = "graph.png"
DEFAULT_MAX_DEPTH = 5


def load_config(path: str) -> Dict[str, Any]:
    """Загружает конфигурацию из JSON-файла.

    Args:
        path: Путь к JSON-файлу.

    Returns:
        Словарь с параметрами конфигурации.

    Raises:
        FileNotFoundError: Если файл не найден.
        ConfigError: Если файл не является валидным JSON.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл конфигурации не найден: {path}")

    try:
        with open(path, "r", encoding="utf-8") as file:
            config = json.load(file)
    except json.JSONDecodeError as error:
        raise ConfigError(f"Некорректный JSON: {error}") from error

    return config


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Проверяет корректность параметров конфигурации.

    Args:
        config: Словарь с параметрами.

    Returns:
        Словарь с параметрами и значениями по умолчанию.

    Raises:
        PackageNotFoundError: Если имя пакета отсутствует.
        RepositoryError: Если URL или путь к файлу некорректны.
        DepthError: Если глубина анализа некорректна.
    """
    validated: Dict[str, Any] = {}

    package_name = config.get("package_name")
    if not package_name or not isinstance(package_name, str):
        raise PackageNotFoundError(
            "Параметр 'package_name' должен быть непустой строкой"
        )
    validated["package_name"] = package_name

    repository_url = config.get(
        "repository_url", DEFAULT_REPOSITORY_URL
    )
    if not isinstance(repository_url, str):
        raise RepositoryError(
            "Параметр 'repository_url' должен быть строкой"
        )
    validated["repository_url"] = repository_url

    test_mode = config.get("test_mode", False)
    if not isinstance(test_mode, bool):
        raise ConfigError(
            "Параметр 'test_mode' должен быть булевым значением"
        )
    validated["test_mode"] = test_mode

    if test_mode:
        test_file_path = config.get("test_file_path")
        if not test_file_path or not isinstance(test_file_path, str):
            raise RepositoryError(
                "В режиме тестирования 'test_file_path' обязателен"
            )
        validated["test_file_path"] = test_file_path
    else:
        validated["test_file_path"] = None

    output_file = config.get("output_file", DEFAULT_OUTPUT_FILE)
    if not isinstance(output_file, str):
        raise ConfigError(
            "Параметр 'output_file' должен быть строкой"
        )
    validated["output_file"] = output_file

    max_depth = config.get("max_depth", DEFAULT_MAX_DEPTH)
    if not isinstance(max_depth, int) or max_depth < 1:
        raise DepthError(
            "Параметр 'max_depth' должен быть целым числом >= 1"
        )
    validated["max_depth"] = max_depth

    return validated


def print_config(config: Dict[str, Any]) -> None:
    """Выводит параметры конфигурации в формате ключ-значение.

    Args:
        config: Словарь с проверенными параметрами.
    """
    print("=== Конфигурация визуализатора ===")
    for key, value in config.items():
        print(f"{key}: {value}")
    print("==================================")