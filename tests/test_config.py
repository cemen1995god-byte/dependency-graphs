"""Тесты модуля конфигурации."""

import json
import os
import tempfile
import pytest

from src.config import load_config, validate_config
from src.errors import (
    PackageNotFoundError,
    RepositoryError,
    DepthError,
    ConfigError,
)


def _write_temp_config(data: dict) -> str:
    """Создаёт временный JSON-файл с конфигурацией.

    Args:
        data: Словарь с данными.

    Returns:
        Путь к созданному файлу.
    """
    file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(data, file)
    file.close()
    return file.name


def test_load_valid_config():
    """Тест загрузки валидной конфигурации."""
    path = _write_temp_config({
        "package_name": "test:pkg",
        "max_depth": 2,
    })
    try:
        config = load_config(path)
        assert config["package_name"] == "test:pkg"
        assert config["max_depth"] == 2
    finally:
        os.unlink(path)


def test_load_missing_file():
    """Тест загрузки несуществующего файла."""
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/config.json")


def test_load_invalid_json():
    """Тест загрузки невалидного JSON."""
    file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    file.write("{невалидный json")
    file.close()
    try:
        with pytest.raises(ConfigError):
            load_config(file.name)
    finally:
        os.unlink(file.name)


def test_validate_missing_package():
    """Тест валидации без имени пакета."""
    with pytest.raises(PackageNotFoundError):
        validate_config({"max_depth": 3})


def test_validate_empty_package():
    """Тест валидации с пустым именем пакета."""
    with pytest.raises(PackageNotFoundError):
        validate_config({"package_name": ""})


def test_validate_invalid_depth():
    """Тест валидации некорректной глубины."""
    with pytest.raises(DepthError):
        validate_config({"package_name": "a:b", "max_depth": 0})


def test_validate_negative_depth():
    """Тест валидации отрицательной глубины."""
    with pytest.raises(DepthError):
        validate_config({"package_name": "a:b", "max_depth": -1})


def test_validate_test_mode_without_path():
    """Тест тестового режима без пути к файлу."""
    with pytest.raises(RepositoryError):
        validate_config({
            "package_name": "a:b",
            "test_mode": True,
        })


def test_validate_defaults():
    """Тест значений по умолчанию."""
    config = validate_config({"package_name": "a:b"})
    assert config["repository_url"] == "https://repo1.maven.org/maven2"
    assert config["output_file"] == "graph.png"
    assert config["max_depth"] == 5
    assert config["test_mode"] is False
    assert config["test_file_path"] is None