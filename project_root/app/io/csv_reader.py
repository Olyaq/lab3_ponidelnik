import csv
from pathlib import Path
from typing import List, Dict, Any

from app.io.base_reader import BaseReader
from app.core.exceptions import DataFormatError


class CSVReader(BaseReader):

    def read(self, path: Path) -> List[Dict[str, Any]]:
        try:
            with path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as err:
            raise DataFormatError(f"CSV error in {path}: {err}") from err
