from datetime import datetime
from typing import Dict

from app.core.models import Transaction
from app.core.exceptions import ValidationError

REQUIRED_FIELDS = {"id", "amount", "category", "date"}


def validate_record(record: Dict) -> Transaction:
    if not REQUIRED_FIELDS.issubset(record):
        missing = REQUIRED_FIELDS - record.keys()
        raise ValidationError(f"Missing fields: {missing}")

    try:
        amount = float(record["amount"])
    except Exception as err:
        raise ValidationError("Amount must be a number") from err

    if amount <= 0:
        raise ValidationError("Amount must be > 0")

    try:
        date = datetime.fromisoformat(record["date"])
    except Exception as err:
        raise ValidationError("Invalid date format") from err

    return Transaction(
        id=str(record["id"]),
        amount=amount,
        category=str(record["category"]),
        date=date,
    )
