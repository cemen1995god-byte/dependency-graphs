"""Точка входа в визуализатор графа зависимостей."""

import sys
from typing import List

from src.config import load_config, validate_config, print_config
from src.errors import ConfigError, RepositoryError
from src.collector import collect_direct_dependencies


def get_config_path(args: List[str]) -> str:
    """Определяет путь к файлу конфигурации.

    Args:
        args: Аргументы командной строки.

    Returns:
        Путь к JSON-файлу конфигурации.

    Raises:
        ConfigError: Если путь не указан.
    """
    if len(args) < 2:
        raise ConfigError(
            "Использование: python -m src.main <путь к config.json>"
        )
    return args[1]


def main() -> None:
    """Запускает визуализатор графа зависимостей."""
    try:
        config_path = get_config_path(sys.argv)
        raw_config = load_config(config_path)
        config = validate_config(raw_config)
        print_config(config)

        if not config["test_mode"]:
            print("\n=== Прямые зависимости ===")
            dependencies = collect_direct_dependencies(
                config["repository_url"], config["package_name"]
            )
            if dependencies:
                for dep in dependencies:
                    print(
                        f"{dep['groupId']}:{dep['artifactId']}"
                        f":{dep['version']}"
                    )
            else:
                print("Зависимости не найдены")
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