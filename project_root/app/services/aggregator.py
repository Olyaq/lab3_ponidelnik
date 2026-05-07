from collections import defaultdict
from typing import Dict

from app.core.models import Transaction
from app.core.exceptions import ValidationError


class Aggregator:

    def __init__(self):
        self.transactions: Dict[str, Transaction] = {}

    def add(self, tx: Transaction):
        if tx.id in self.transactions:
            raise ValidationError(f"Duplicate transaction id: {tx.id}")

        self.transactions[tx.id] = tx

    def summarize(self) -> Dict[str, float]:
        result = defaultdict(float)

        for tx in self.transactions.values():
            result[tx.category] += tx.amount

        return dict(result)
