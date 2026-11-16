"""Модуль пользовательских исключений."""


class ConfigError(Exception):
    """Ошибка конфигурации.

    Вызывается при некорректных параметрах в JSON-файле.
    """

    def __init__(self, message: str) -> None:
        """Инициализирует ошибку конфигурации.

        Args:
            message: Текст ошибки.
        """
        super().__init__(message)
        self.message = message


class PackageNotFoundError(ConfigError):
    """Пакет не найден.

    Вызывается, если имя пакета пустое или некорректное.
    """


class RepositoryError(ConfigError):
    """Ошибка репозитория.

    Вызывается при некорректном URL или пути к файлу.
    """


class DepthError(ConfigError):
    """Ошибка глубины анализа.

    Вызывается, если глубина не является положительным числом.
    """