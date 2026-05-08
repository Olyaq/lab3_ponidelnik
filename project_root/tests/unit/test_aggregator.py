import pytest
from datetime import datetime
from app.services.aggregator import Aggregator
from app.core.models import Transaction
from app.core.exceptions import ValidationError


def make_tx(id="1", amount=100.0, category="food"):
    """Вспомогательная фабрика транзакций для тестов."""
    return Transaction(id=id, amount=amount, category=category, date=datetime(2024, 1, 1))



# Базовое добавление


def test_add_single_transaction(aggregator):
    """Добавление одной транзакции — summarize возвращает её сумму."""
    aggregator.add(make_tx(id="1", amount=100.0, category="food"))
    result = aggregator.summarize()
    assert result == {"food": 100.0}


def test_add_multiple_categories(aggregator):
    """Разные категории суммируются отдельно."""
    aggregator.add(make_tx(id="1", amount=100.0, category="food"))
    aggregator.add(make_tx(id="2", amount=50.0, category="transport"))
    result = aggregator.summarize()
    assert result["food"] == 100.0
    assert result["transport"] == 50.0


def test_same_category_sums_up(aggregator):
    """Одна категория, несколько транзакций — суммы складываются."""
    aggregator.add(make_tx(id="1", amount=100.0, category="food"))
    aggregator.add(make_tx(id="2", amount=200.0, category="food"))
    result = aggregator.summarize()
    assert result["food"] == 300.0



# Дубликаты


def test_duplicate_id_raises(aggregator):
    """Два раза один id — ValidationError."""
    aggregator.add(make_tx(id="1"))
    with pytest.raises(ValidationError):
        aggregator.add(make_tx(id="1"))


def test_different_ids_no_error(aggregator):
    """Разные id — ошибок нет."""
    aggregator.add(make_tx(id="1"))
    aggregator.add(make_tx(id="2"))
    assert len(aggregator.transactions) == 2



# Пустой агрегатор


def test_summarize_empty(aggregator):
    """Без транзакций summarize возвращает пустой словарь."""
    assert aggregator.summarize() == {}