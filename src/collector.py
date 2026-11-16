"""Модуль сбора зависимостей из Maven-репозитория."""

import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

from src.errors import RepositoryError


MAVEN_METADATA_FILE = "maven-metadata.xml"
POM_FILE = "pom.xml"
NAMESPACE = "{http://maven.apache.org/POM/4.0.0}"


def get_latest_version(
    repository_url: str, group_id: str, artifact_id: str
) -> str:
    """Получает последнюю версию пакета из maven-metadata.xml.

    Args:
        repository_url: URL Maven-репозитория.
        group_id: Group ID пакета.
        artifact_id: Artifact ID пакета.

    Returns:
        Строка с номером последней версии.

    Raises:
        RepositoryError: Если не удалось получить метаданные.
    """
    group_path = group_id.replace(".", "/")
    metadata_url = (
        f"{repository_url.rstrip('/')}/{group_path}/{artifact_id}"
        f"/{MAVEN_METADATA_FILE}"
    )

    try:
        with urllib.request.urlopen(metadata_url) as response:
            xml_data = response.read()
    except urllib.error.URLError as error:
        raise RepositoryError(
            f"Не удалось получить метаданные: {error}"
        ) from error

    root = ET.fromstring(xml_data)
    versioning = root.find(f"{NAMESPACE}versioning")
    if versioning is None:
        raise RepositoryError("Не найдена секция versioning")

    latest = versioning.find(f"{NAMESPACE}latest")
    if latest is None or not latest.text:
        raise RepositoryError("Не найдена последняя версия")

    return latest.text


def get_dependencies(
    repository_url: str,
    group_id: str,
    artifact_id: str,
    version: str,
) -> List[Dict[str, str]]:
    """Получает прямые зависимости пакета из pom.xml.

    Args:
        repository_url: URL Maven-репозитория.
        group_id: Group ID пакета.
        artifact_id: Artifact ID пакета.
        version: Версия пакета.

    Returns:
        Список словарей с зависимостями.

    Raises:
        RepositoryError: Если не удалось получить pom.xml.
    """
    group_path = group_id.replace(".", "/")
    pom_url = (
        f"{repository_url.rstrip('/')}/{group_path}/{artifact_id}"
        f"/{version}/{POM_FILE}"
    )

    try:
        with urllib.request.urlopen(pom_url) as response:
            xml_data = response.read()
    except urllib.error.URLError as error:
        raise RepositoryError(
            f"Не удалось получить pom.xml: {error}"
        ) from error

    root = ET.fromstring(xml_data)
    dependencies_elem = root.find(f"{NAMESPACE}dependencies")

    if dependencies_elem is None:
        return []

    dependencies: List[Dict[str, str]] = []
    for dep in dependencies_elem.findall(f"{NAMESPACE}dependency"):
        dep_group = dep.find(f"{NAMESPACE}groupId")
        dep_artifact = dep.find(f"{NAMESPACE}artifactId")
        dep_version = dep.find(f"{NAMESPACE}version")

        if (
            dep_group is not None
            and dep_artifact is not None
            and dep_group.text
            and dep_artifact.text
        ):
            dependency = {
                "groupId": dep_group.text,
                "artifactId": dep_artifact.text,
                "version": dep_version.text if dep_version is not None else "unknown",
            }
            dependencies.append(dependency)

    return dependencies


def parse_package_name(package_name: str) -> tuple:
    """Разбирает имя пакета в формате groupId:artifactId.

    Args:
        package_name: Строка вида 'groupId:artifactId'.

    Returns:
        Кортеж (group_id, artifact_id).

    Raises:
        RepositoryError: Если формат некорректен.
    """
    parts = package_name.split(":")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise RepositoryError(
            f"Некорректный формат пакета: {package_name}. "
            "Ожидается groupId:artifactId"
        )
    return parts[0], parts[1]


def collect_direct_dependencies(
    repository_url: str, package_name: str
) -> List[Dict[str, str]]:
    """Собирает прямые зависимости пакета.

    Args:
        repository_url: URL Maven-репозитория.
        package_name: Имя пакета в формате groupId:artifactId.

    Returns:
        Список словарей с зависимостями.
    """
    group_id, artifact_id = parse_package_name(package_name)
    version = get_latest_version(repository_url, group_id, artifact_id)
    return get_dependencies(repository_url, group_id, artifact_id, version)