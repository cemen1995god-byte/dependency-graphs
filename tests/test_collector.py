"""Тесты модуля сбора зависимостей."""

import pytest
from src.collector import parse_package_name
from src.errors import RepositoryError


def test_parse_valid_package():
    """Тест разбора корректного имени пакета."""
    group, artifact = parse_package_name("org.springframework:spring-core")
    assert group == "org.springframework"
    assert artifact == "spring-core"


def test_parse_invalid_format():
    """Тест разбора некорректного формата."""
    with pytest.raises(RepositoryError):
        parse_package_name("invalid-package")


def test_parse_empty_group():
    """Тест разбора с пустым group ID."""
    with pytest.raises(RepositoryError):
        parse_package_name(":artifact")


def test_parse_empty_artifact():
    """Тест разбора с пустым artifact ID."""
    with pytest.raises(RepositoryError):
        parse_package_name("group:")