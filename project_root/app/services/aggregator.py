from collections import defaultdict
from typing import Dict, Optional

from app.core.models import Transaction
from app.core.exceptions import ValidationError


class Aggregator:

    def __init__(self, check_duplicates: bool = True):
        self._check_duplicates = check_duplicates
        self._seen_ids: Dict[str, bool] = {}
        self._sums: Dict[str, float] = defaultdict(float)

    @property
    def transactions(self) -> Dict:
        return self._seen_ids

    def add(self, tx: Transaction):
        if self._check_duplicates:
            if tx.id in self._seen_ids:
                raise ValidationError(f"Duplicate transaction id: {tx.id}")
            self._seen_ids[tx.id] = True

        self._sums[tx.category] += tx.amount

    def summarize(self) -> Dict[str, float]:
        return dict(self._sums)