class BaseAppError(Exception):
    """Базовое исключение проекта."""
    pass


class DataFormatError(BaseAppError):
    """Ошибка структуры файла."""
    pass


class ValidationError(BaseAppError):
    """Ошибка бизнес-логики."""
    pass


class CurrencyMismatchError(BaseAppError):
    """Несоответствие валют (опционально)."""
    pass
