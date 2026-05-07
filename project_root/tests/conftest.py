import pytest
from app.services.aggregator import Aggregator
from app.services.validator import validate_record
from app.core.models import Transaction
from datetime import datetime


@pytest.fixture
def aggregator():
    """Чистый агрегатор для каждого теста."""
    return Aggregator()


@pytest.fixture
def valid_record():
    """Эталонная корректная запись."""
    return {
        "id": "1",
        "amount": "100.0",
        "category": "food",
        "date": "2024-01-01",
    }


@pytest.fixture
def valid_transaction():
    """Готовый объект Transaction."""
    return Transaction(
        id="1",
        amount=100.0,
        category="food",
        date=datetime(2024, 1, 1),
    )


@pytest.fixture
def sample_csv(tmp_path):
    """Временный CSV: 1 хорошая строка, 2 плохих."""
    p = tmp_path / "data.csv"
    p.write_text(
        "id,amount,category,date\n"
        "1,100,food,2024-01-01\n"       # хорошая
        "2,-50,transport,2024-01-02\n"  # плохая: amount <= 0
        "3,abc,food,2024-01-03\n"       # плохая: amount не число
    )
    return p


@pytest.fixture
def sample_json(tmp_path):
    """Временный JSON с одной корректной транзакцией."""
    p = tmp_path / "data.json"
    p.write_text(
        '[{"id": "10", "amount": "150", "category": "food", "date": "2024-01-03"}]'
    )
    return p