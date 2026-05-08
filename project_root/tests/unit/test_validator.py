import pytest
from app.services.validator import validate_record
from app.core.exceptions import ValidationError
from app.core.models import Transaction



# Позитивный сценарий


def test_validate_returns_transaction(valid_record):
    """Корректная запись возвращает объект Transaction."""
    tx = validate_record(valid_record)
    assert isinstance(tx, Transaction)


def test_validate_correct_values(valid_record):
    """Все поля Transaction соответствуют входным данным."""
    tx = validate_record(valid_record)
    assert tx.id == "1"
    assert tx.amount == 100.0
    assert tx.category == "food"
    assert tx.date.year == 2024



# Граничные значения amount


@pytest.mark.parametrize("amount, should_pass", [
    ("0.01",      True),   # минимально допустимое
    ("100",       True),   # целое число строкой
    ("100.0",     True),   # float строкой
    ("999999999", True),   # очень большое
    ("0",         False),  # ноль — невалидно
    ("-1",        False),  # отрицательное
    ("-0.01",     False),  # минимально отрицательное
    ("abc",       False),  # строка вместо числа
    ("",          False),  # пустая строка
    (None,        False),  # None
    ("1e2",       True),   # научная нотация — Python парсит как 100.0
])
def test_amount_boundaries(valid_record, amount, should_pass):
    """Проверка граничных значений поля amount."""
    valid_record["amount"] = amount
    if should_pass:
        tx = validate_record(valid_record)
        assert tx.amount > 0
    else:
        with pytest.raises(ValidationError):
            validate_record(valid_record)



# Отсутствующие обязательные поля


@pytest.mark.parametrize("missing_field", ["id", "amount", "category", "date"])
def test_missing_required_field(valid_record, missing_field):
    """Каждое обязательное поле по отдельности — если убрать, должна быть ошибка."""
    del valid_record[missing_field]
    with pytest.raises(ValidationError):
        validate_record(valid_record)



# Некорректная дата


@pytest.mark.parametrize("bad_date", [
    "not-a-date",
    "32-01-2024",
    "2024/01/01",   # слэши вместо дефисов — не ISO формат
    "",
    "yesterday",
])
def test_invalid_date_format(valid_record, bad_date):
    """Некорректный формат даты вызывает ValidationError."""
    valid_record["date"] = bad_date
    with pytest.raises(ValidationError):
        validate_record(valid_record)


def test_valid_iso_date_formats(valid_record):
    """ISO 8601 с временем тоже принимается."""
    valid_record["date"] = "2024-01-01T12:00:00"
    tx = validate_record(valid_record)
    assert tx.date.hour == 12



# Мусор на входе


def test_validate_raises_on_none():
    """None вместо словаря — должна быть ошибка, не AttributeError."""
    with pytest.raises(Exception):
        validate_record(None)


def test_validate_raises_on_empty_dict():
    """Пустой словарь — нет обязательных полей."""
    with pytest.raises(ValidationError):
        validate_record({})